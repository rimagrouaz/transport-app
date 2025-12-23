from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from openrouteservice import convert
import logging
import os
from datetime import datetime, timedelta
import zipfile
import io
import csv
from collections import defaultdict
import math
import threading
import time
from functools import lru_cache
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
ORS_API_KEY = os.getenv('ORS_API_KEY', 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImIxM2U1NzhhNDJlMjQ1MzZhNTVlYjUyZjBhYzAyY2UzIiwiaCI6Im11cm11cjY0In0=')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
PORT = int(os.getenv('PORT', 5001))

# Cache global pour GTFS par région
gtfs_cache = {}
cache_lock = threading.Lock()

# Base de données des sources GTFS mondiales (The Mobility Database)
MOBILITY_DATABASE_API = "https://api.mobilitydatabase.org/v1"

class TransitAPIManager:
    """
    Gestionnaire d'APIs de transport en commun multiples avec fallback
    """
    
    @staticmethod
    def detect_country_city(lat, lon):
        """Détecte le pays et la ville à partir des coordonnées"""
        try:
            # Utiliser Photon pour le reverse geocoding
            url = f"https://photon.komoot.io/reverse?lon={lon}&lat={lat}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('features'):
                props = data['features'][0]['properties']
                return {
                    'country': props.get('country', ''),
                    'country_code': props.get('countrycode', '').upper(),
                    'city': props.get('city') or props.get('name', ''),
                    'state': props.get('state', '')
                }
        except Exception as e:
            logger.warning(f"Erreur détection localisation: {e}")
        
        return {'country': '', 'country_code': '', 'city': '', 'state': ''}
    
    @staticmethod
    @lru_cache(maxsize=100)
    def search_gtfs_feeds(lat, lon, radius_km=50):
        """
        Recherche les flux GTFS disponibles pour une zone géographique
        via The Mobility Database
        """
        try:
            logger.info(f"Recherche flux GTFS pour ({lat}, {lon})")
            
            # API Mobility Database pour trouver les feeds
            url = f"{MOBILITY_DATABASE_API}/gtfs_feeds"
            params = {
                'lat': lat,
                'lon': lon,
                'radius': radius_km * 1000  # en mètres
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                feeds = response.json()
                logger.info(f"✓ {len(feeds)} flux GTFS trouvés")
                return feeds
            else:
                logger.warning(f"Mobility Database: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erreur recherche GTFS: {e}")
        
        # Fallback: recherche dans une base locale
        return TransitAPIManager.get_local_gtfs_sources(lat, lon)
    
    @staticmethod
    def get_local_gtfs_sources(lat, lon):
        """
        Base de données locale des principales sources GTFS mondiales
        """
        # Principales villes avec GTFS open data
        gtfs_sources = [
            # France - URLs DIRECTES 2025 (validées)
            {'name': 'TBM Bordeaux', 'country': 'FR', 'lat': 44.8378, 'lon': -0.5792, 
             'url': 'https://eu.ftp.opendatasoft.com/bdx/gtfs_bdx.zip'},
            {'name': 'RATP Paris', 'country': 'FR', 'lat': 48.8566, 'lon': 2.3522,
             'url': 'https://eu.ftp.opendatasoft.com/stif/gtfs-lines-last.zip'},
            {'name': 'TCL Lyon', 'country': 'FR', 'lat': 45.7640, 'lon': 4.8357,
             'url': 'https://eu.ftp.opendatasoft.com/sytral/GTFS/GTFS_TCL.zip'},
            
            # USA
            {'name': 'MTA New York', 'country': 'US', 'lat': 40.7128, 'lon': -74.0060,
             'url': 'http://web.mta.info/developers/data/nyct/subway/google_transit.zip'},
            {'name': 'BART San Francisco', 'country': 'US', 'lat': 37.7749, 'lon': -122.4194,
             'url': 'https://www.bart.gov/dev/schedules/google_transit.zip'},
            {'name': 'CTA Chicago', 'country': 'US', 'lat': 41.8781, 'lon': -87.6298,
             'url': 'https://www.transitchicago.com/downloads/sch_data/google_transit.zip'},
            
            # UK
            {'name': 'TfL London', 'country': 'UK', 'lat': 51.5074, 'lon': -0.1278,
             'url': 'https://api.tfl.gov.uk/timetables/tfl-gtfs.zip'},
            
            # Canada
            {'name': 'STM Montreal', 'country': 'CA', 'lat': 45.5017, 'lon': -73.5673,
             'url': 'https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip'},
            {'name': 'TTC Toronto', 'country': 'CA', 'lat': 43.6532, 'lon': -79.3832,
             'url': 'http://opendata.toronto.ca/toronto.transit.commission/ttc-routes-and-schedules/TTC_Routes_and_Schedules_Data.zip'},
            
            # Allemagne
            {'name': 'BVG Berlin', 'country': 'DE', 'lat': 52.5200, 'lon': 13.4050,
             'url': 'https://www.vbb.de/media/download/2029'},
            
            # Espagne
            {'name': 'EMT Madrid', 'country': 'ES', 'lat': 40.4168, 'lon': -3.7038,
             'url': 'https://opendata.emtmadrid.es/Datos-estaticos/Datos-generales-(1)'},
            {'name': 'TMB Barcelona', 'country': 'ES', 'lat': 41.3851, 'lon': 2.1734,
             'url': 'https://www.tmb.cat/en/barcelona/shared/gtfs'},
            
            # Italie
            {'name': 'ATAC Rome', 'country': 'IT', 'lat': 41.9028, 'lon': 12.4964,
             'url': 'https://romamobilita.it/sites/default/files/rome_gtfs.zip'},
            {'name': 'ATM Milan', 'country': 'IT', 'lat': 45.4642, 'lon': 9.1900,
             'url': 'https://www.atm.it/it/ViaggiaConNoi/Pagine/GTFSDataset.aspx'},
            
            # Pays-Bas
            {'name': 'GVB Amsterdam', 'country': 'NL', 'lat': 52.3676, 'lon': 4.9041,
             'url': 'https://gtfs.ovapi.nl/nl/gtfs-nl.zip'},
            
            # Belgique
            {'name': 'STIB Brussels', 'country': 'BE', 'lat': 50.8503, 'lon': 4.3517,
             'url': 'https://stibmivb.opendatasoft.com/api/explore/v2.1/catalog/datasets/gtfs-files-production/files'},
            
            # Suisse
            {'name': 'SBB Swiss', 'country': 'CH', 'lat': 47.3769, 'lon': 8.5417,
             'url': 'https://opentransportdata.swiss/en/dataset/timetable-2020-gtfs'},
            
            # Australie
            {'name': 'Transport NSW Sydney', 'country': 'AU', 'lat': -33.8688, 'lon': 151.2093,
             'url': 'https://opendata.transport.nsw.gov.au/dataset/public-transport-gtfs-realtime'},
            {'name': 'PTV Melbourne', 'country': 'AU', 'lat': -37.8136, 'lon': 144.9631,
             'url': 'https://data.ptv.vic.gov.au/downloads/gtfs.zip'},
            
            # Japon
            {'name': 'Tokyo Metro', 'country': 'JP', 'lat': 35.6762, 'lon': 139.6503,
             'url': 'https://api-public.odpt.org/api/v4/files/tokyometro/data/odpt_train.zip'},
        ]
        
        # Trouver la source la plus proche
        closest = None
        min_distance = float('inf')
        
        for source in gtfs_sources:
            dist = haversine_distance(lat, lon, source['lat'], source['lon'])
            if dist < min_distance and dist < 100:  # Dans les 100km
                min_distance = dist
                closest = source
        
        return [closest] if closest else []
    
    @staticmethod
    def get_transit_data_overpass(lat, lon, radius_m=2000):
        """
        Récupère les données de transport en commun via Overpass API (OpenStreetMap)
        Fallback universel quand GTFS n'est pas disponible
        """
        try:
            logger.info(f"Récupération données OSM Overpass ({lat}, {lon})")
            
            # Essayer plusieurs serveurs Overpass (fallback en cas de timeout)
            overpass_servers = [
                "https://overpass.kumi.systems/api/interpreter",  # Serveur alternatif
                "https://overpass-api.de/api/interpreter",  # Serveur principal
                "https://overpass.openstreetmap.ru/cgi/interpreter",  # Serveur russe
            ]
            
            osm_data = None
            for overpass_url in overpass_servers:
                try:
                    logger.info(f"Tentative Overpass: {overpass_url}")
                    
                    query = f"""
                    [out:json][timeout:15];
                    (
                      node["public_transport"="stop_position"](around:2000,{lat},{lon});
                      node["highway"="bus_stop"](around:2000,{lat},{lon});
                      node["railway"="tram_stop"](around:2000,{lat},{lon});
                      node["railway"="station"](around:2000,{lat},{lon});
                      node["railway"="halt"](around:2000,{lat},{lon});
                    );
                    out body;
                    >;
                    out skel qt;
                    
                    relation["route"~"bus|tram|subway|train"](around:3000,{lat},{lon});
                    out body;
                    """
                    
                    r = requests.post(overpass_url, data={'data': query}, timeout=20)
                    r.raise_for_status()
                    data = r.json()
                    
                    # Parser les données
                    stops = []
                    routes = []
                    
                    for element in data.get('elements', []):
                        if element['type'] == 'node':
                            tags = element.get('tags', {})
                            if any(k in tags for k in ['public_transport', 'highway', 'railway']):
                                stops.append({
                                    'id': f"osm_{element['id']}",
                                    'name': tags.get('name', 'Arrêt sans nom'),
                                    'lat': element['lat'],
                                    'lon': element['lon']
                                })
                        elif element['type'] == 'relation':
                            tags = element.get('tags', {})
                            if 'route' in tags:
                                routes.append({
                                    'id': f"osm_route_{element['id']}",
                                    'short_name': tags.get('ref', tags.get('name', 'N/A')),
                                    'long_name': tags.get('name', ''),
                                    'type': tags['route'].capitalize(),
                                    'color': tags.get('colour', '#0066CC')
                                })
                    
                    osm_data = {'stops': stops, 'routes': routes}
                    logger.info(f"✓ OSM: {len(stops)} arrêts, {len(routes)} lignes via {overpass_url}")
                    break  # Succès, arrêter la boucle
                    
                except Exception as e:
                    logger.warning(f"Overpass {overpass_url} échoué: {e}")
                    continue  # Essayer le serveur suivant
            
            if not osm_data:
                logger.error("Tous les serveurs Overpass ont échoué")
                return {'stops': [], 'routes': []}
            
            # Query Overpass pour les arrêts et lignes de transport
            query = f"""
            [out:json][timeout:25];
            (
              node["highway"="bus_stop"](around:{radius_m},{lat},{lon});
              node["railway"="tram_stop"](around:{radius_m},{lat},{lon});
              node["railway"="station"](around:{radius_m},{lat},{lon});
              node["railway"="subway_entrance"](around:{radius_m},{lat},{lon});
              node["amenity"="bus_station"](around:{radius_m},{lat},{lon});
              relation["type"="route"]["route"~"bus|tram|subway|train|light_rail"](around:{radius_m},{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            response = requests.post(overpass_url, data={'data': query}, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Parser les arrêts
            stops = []
            routes = []
            
            for element in data.get('elements', []):
                if element['type'] == 'node':
                    tags = element.get('tags', {})
                    if 'name' in tags:
                        stops.append({
                            'id': f"osm_{element['id']}",
                            'name': tags.get('name', 'Unknown'),
                            'lat': element['lat'],
                            'lon': element['lon'],
                            'type': tags.get('highway') or tags.get('railway') or tags.get('amenity', 'stop'),
                            'source': 'osm'
                        })
                
                elif element['type'] == 'relation':
                    tags = element.get('tags', {})
                    if 'ref' in tags or 'name' in tags:
                        routes.append({
                            'id': f"osm_route_{element['id']}",
                            'short_name': tags.get('ref', ''),
                            'long_name': tags.get('name', ''),
                            'type': tags.get('route', 'bus'),
                            'color': '#' + tags.get('colour', '0066CC').replace('#', ''),
                            'source': 'osm'
                        })
            
            logger.info(f"✓ OSM: {len(stops)} arrêts, {len(routes)} lignes")
            return {'stops': stops, 'routes': routes}
            
        except Exception as e:
            logger.error(f"Erreur Overpass API: {e}")
            return {'stops': [], 'routes': []}


class GTFSManager:
    """Gestionnaire GTFS optimisé avec cache intelligent"""
    
    @staticmethod
    def load_gtfs_for_region(lat, lon):
        """Charge les données GTFS pour une région donnée"""
        region_key = f"{round(lat, 2)}_{round(lon, 2)}"
        
        with cache_lock:
            # Vérifier si déjà en cache
            if region_key in gtfs_cache:
                cache_data = gtfs_cache[region_key]
                age = datetime.now() - cache_data['loaded_at']
                
                # Cache valide 24h
                if age < timedelta(hours=24):
                    logger.info(f"✓ GTFS cache hit pour {region_key}")
                    return cache_data
        
        # Charger de nouvelles données
        logger.info(f"Chargement GTFS pour {region_key}")
        
        # Rechercher les flux disponibles
        feeds = TransitAPIManager.search_gtfs_feeds(lat, lon)
        
        if not feeds:
            logger.warning("Pas de flux GTFS, utilisation OSM")
            osm_data = TransitAPIManager.get_transit_data_overpass(lat, lon)
            
            # Créer des associations stop_times basiques pour OSM
            stop_times_dict = defaultdict(list)
            stops_dict = {stop['id']: stop for stop in osm_data['stops']}
            routes_dict = {route['id']: route for route in osm_data['routes']}
            
            # Pour chaque arrêt, créer des fake stop_times liés aux routes proches
            for stop_id, stop in stops_dict.items():
                # Associer chaque route à chaque arrêt (approximation)
                for route_id, route in routes_dict.items():
                    # Créer un fake trip
                    trip_id = f"{route_id}_trip"
                    stop_times_dict[stop_id].append({
                        'trip_id': trip_id,
                        'departure_time': '08:00:00',  # Horaire factice
                        'arrival_time': '08:00:00'
                    })
            
            # Créer des trips qui lient routes et stop_times
            trips_dict = {}
            for route_id in routes_dict.keys():
                trip_id = f"{route_id}_trip"
                trips_dict[trip_id] = {
                    'trip_id': trip_id,
                    'route_id': route_id,
                    'headsign': 'Direction Centre'
                }
            
            with cache_lock:
                gtfs_cache[region_key] = {
                    'stops': stops_dict,
                    'routes': routes_dict,
                    'trips': trips_dict,
                    'stop_times': stop_times_dict,
                    'source': 'osm',
                    'loaded_at': datetime.now()
                }
            
            logger.info(f"✓ OSM enrichi: {len(stops_dict)} arrêts, {len(routes_dict)} routes, liens créés")
            return gtfs_cache[region_key]
        
        # Charger le premier flux GTFS disponible
        feed = feeds[0]
        gtfs_data = GTFSManager.download_and_parse_gtfs(
            feed.get('url') or feed.get('direct_download_url'),
            lat, 
            lon
        )
        
        if gtfs_data:
            with cache_lock:
                gtfs_cache[region_key] = {
                    **gtfs_data,
                    'source': 'gtfs',
                    'loaded_at': datetime.now()
                }
            return gtfs_cache[region_key]
        
        # Si échec GTFS, fallback vers OSM
        logger.warning("Échec chargement GTFS, fallback OSM")
        osm_data = TransitAPIManager.get_transit_data_overpass(lat, lon)
        
        # Créer des associations stop_times basiques pour OSM
        stop_times_dict = defaultdict(list)
        stops_dict = {stop['id']: stop for stop in osm_data['stops']}
        routes_dict = {route['id']: route for route in osm_data['routes']}
        
        # Pour chaque arrêt, créer des fake stop_times liés aux routes proches
        for stop_id, stop in stops_dict.items():
            # Associer chaque route à chaque arrêt (approximation)
            for route_id, route in routes_dict.items():
                # Créer un fake trip
                trip_id = f"{route_id}_trip"
                stop_times_dict[stop_id].append({
                    'trip_id': trip_id,
                    'departure_time': '08:00:00',  # Horaire factice
                    'arrival_time': '08:00:00'
                })
        
        # Créer des trips qui lient routes et stop_times
        trips_dict = {}
        for route_id in routes_dict.keys():
            trip_id = f"{route_id}_trip"
            trips_dict[trip_id] = {
                'trip_id': trip_id,
                'route_id': route_id,
                'headsign': 'Direction Centre'
            }
        
        with cache_lock:
            gtfs_cache[region_key] = {
                'stops': stops_dict,
                'routes': routes_dict,
                'trips': trips_dict,
                'stop_times': stop_times_dict,
                'source': 'osm',
                'loaded_at': datetime.now()
            }
        
        logger.info(f"✓ OSM enrichi (fallback): {len(stops_dict)} arrêts, {len(routes_dict)} routes")
        return gtfs_cache[region_key]
    
    @staticmethod
    def download_and_parse_gtfs(url, center_lat, center_lon):
        """Télécharge et parse un flux GTFS avec filtrage géographique"""
        try:
            logger.info(f"Téléchargement GTFS: {url}")
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Charger le ZIP
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            
            # Parser les fichiers essentiels
            stops = {}
            routes = {}
            trips = {}
            stop_times = defaultdict(list)
            
            # stops.txt
            try:
                with zip_file.open('stops.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8-sig'))
                    for row in reader:
                        stops[row['stop_id']] = {
                            'id': row['stop_id'],
                            'name': row['stop_name'],
                            'lat': float(row['stop_lat']),
                            'lon': float(row['stop_lon']),
                            'code': row.get('stop_code', '')
                        }
            except Exception as e:
                logger.error(f"Erreur parsing stops.txt: {e}")
            
            # routes.txt
            try:
                with zip_file.open('routes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8-sig'))
                    for row in reader:
                        routes[row['route_id']] = {
                            'id': row['route_id'],
                            'short_name': row.get('route_short_name', ''),
                            'long_name': row.get('route_long_name', ''),
                            'type': GTFSManager.get_route_type_name(row.get('route_type', '3')),
                            'color': '#' + row.get('route_color', '0066CC')
                        }
            except Exception as e:
                logger.error(f"Erreur parsing routes.txt: {e}")
            
            # trips.txt
            try:
                with zip_file.open('trips.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8-sig'))
                    for row in reader:
                        trips[row['trip_id']] = {
                            'route_id': row['route_id'],
                            'service_id': row['service_id'],
                            'headsign': row.get('trip_headsign', '')
                        }
            except Exception as e:
                logger.error(f"Erreur parsing trips.txt: {e}")
            
            # stop_times.txt (CHARGEMENT INTELLIGENT par zone géographique)
            try:
                # Identifier arrêts dans la zone (rayon 5km)
                relevant_stops = set()
                for stop_id, stop in stops.items():
                    dist = haversine_distance(center_lat, center_lon, stop['lat'], stop['lon'])
                    if dist <= 5.0:  # 5km radius
                        relevant_stops.add(stop_id)
                
                logger.info(f"📍 Arrêts pertinents (rayon 5km): {len(relevant_stops)}/{len(stops)}")
                
                # Charger SEULEMENT stop_times pour arrêts pertinents
                with zip_file.open('stop_times.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8-sig'))
                    count = 0
                    loaded = 0
                    for row in reader:
                        count += 1
                        stop_id = row['stop_id']
                        
                        # Filtrer par arrêts pertinents
                        if stop_id in relevant_stops:
                            stop_times[stop_id].append({
                                'trip_id': row['trip_id'],
                                'arrival_time': row['arrival_time'],
                                'departure_time': row['departure_time'],
                                'stop_sequence': int(row['stop_sequence'])
                            })
                            loaded += 1
                        
                        # Sécurité: limite absolue
                        if count > 2000000:
                            logger.warning(f"⚠️ Limite 2M lignes atteinte")
                            break
                    
                    logger.info(f"📊 Stop_times: {loaded} chargés (sur {count} parcourus)")
            except Exception as e:
                logger.error(f"Erreur parsing stop_times.txt: {e}")
            
            logger.info(f"✓ GTFS: {len(stops)} arrêts, {len(routes)} lignes, {len(trips)} trajets")
            
            return {
                'stops': stops,
                'routes': routes,
                'trips': trips,
                'stop_times': stop_times
            }
            
        except Exception as e:
            logger.error(f"Erreur téléchargement GTFS: {e}")
            return None
    
    @staticmethod
    def get_route_type_name(route_type):
        """Convertit le type de route GTFS en nom lisible"""
        types = {
            '0': 'Tram',
            '1': 'Métro',
            '2': 'Train',
            '3': 'Bus',
            '4': 'Ferry',
            '5': 'Câble',
            '6': 'Téléphérique',
            '7': 'Funiculaire',
            '11': 'Trolleybus',
            '12': 'Monorail'
        }
        return types.get(str(route_type), 'Bus')
    
    @staticmethod
    def find_nearby_stops(gtfs_data, lat, lon, radius_km=0.5):
        """Trouve les arrêts à proximité"""
        if not gtfs_data or 'stops' not in gtfs_data:
            return []
        
        nearby = []
        for stop_id, stop in gtfs_data['stops'].items():
            distance = haversine_distance(lat, lon, stop['lat'], stop['lon'])
            if distance <= radius_km:
                nearby.append({
                    **stop,
                    'distance': round(distance * 1000, 0)  # en mètres
                })
        
        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
    @staticmethod
    def find_connecting_routes(gtfs_data, start_stop_id, end_stop_id, limit=5):
        """Trouve les lignes qui connectent deux arrêts via analyse des trips"""
        if not gtfs_data or 'stop_times' not in gtfs_data or 'trips' not in gtfs_data:
            return []
        
        connecting_routes = set()
        
        # Méthode 1: Analyser les trips qui passent par les deux arrêts dans le bon ordre
        if start_stop_id in gtfs_data['stop_times'] and end_stop_id in gtfs_data['stop_times']:
            # Trips passant par le départ
            start_trips = {}
            for st in gtfs_data['stop_times'][start_stop_id]:
                trip_id = st['trip_id']
                start_trips[trip_id] = st.get('stop_sequence', 0)
            
            # Vérifier si ces trips passent aussi par l'arrivée (après le départ)
            for st in gtfs_data['stop_times'][end_stop_id]:
                trip_id = st['trip_id']
                end_sequence = st.get('stop_sequence', 0)
                
                # Si le trip passe par départ ET arrivée dans le bon ordre
                if trip_id in start_trips:
                    start_sequence = start_trips[trip_id]
                    if start_sequence < end_sequence:  # Bon ordre
                        if trip_id in gtfs_data['trips']:
                            route_id = gtfs_data['trips'][trip_id]['route_id']
                            connecting_routes.add(route_id)
        
        # Méthode 2 (fallback): Si pas de routes directes, prendre routes du départ
        if not connecting_routes:
            logger.info("🔄 Aucune route directe, utilisation des routes de départ")
            if start_stop_id in gtfs_data['stop_times']:
                for st in gtfs_data['stop_times'][start_stop_id]:
                    trip_id = st['trip_id']
                    if trip_id in gtfs_data['trips']:
                        route_id = gtfs_data['trips'][trip_id]['route_id']
                        connecting_routes.add(route_id)
        
        # Construire la liste de routes
        routes = []
        for rid in connecting_routes:
            if rid in gtfs_data.get('routes', {}):
                route = gtfs_data['routes'][rid].copy()
                # S'assurer que tous les champs sont présents
                if 'color' not in route or not route['color']:
                    route['color'] = '#0066CC'
                if 'type' not in route or not route['type']:
                    route['type'] = 'Bus'
                if 'short_name' not in route:
                    route['short_name'] = route.get('long_name', 'N/A')
                route['id'] = rid  # Important pour le filtrage
                routes.append(route)
        
        # Trier : Tram/Métro d'abord, puis par nom
        routes.sort(key=lambda r: (
            0 if r['type'].lower() in ['tram', 'métro', 'metro', 'subway'] else 1,
            1 if r['type'].lower() == 'bus' else 0.5,
            r['short_name']
        ))
        
        logger.info(f"📍 Routes connectant arrêts: {len(connecting_routes)} trouvées")
        
        return routes[:limit]
    
    @staticmethod
    def get_routes_at_stop(gtfs_data, stop_id, limit=5):
        """Obtient les lignes desservant un arrêt (limitées aux plus pertinentes)"""
        if not gtfs_data or 'stop_times' not in gtfs_data:
            return []
        
        if stop_id not in gtfs_data['stop_times']:
            return []
        
        route_ids = set()
        for st in gtfs_data['stop_times'][stop_id]:
            trip_id = st['trip_id']
            if trip_id in gtfs_data.get('trips', {}):
                route_ids.add(gtfs_data['trips'][trip_id]['route_id'])
        
        routes = []
        for rid in route_ids:
            if rid in gtfs_data.get('routes', {}):
                route = gtfs_data['routes'][rid].copy()
                # S'assurer que tous les champs nécessaires sont présents
                if 'color' not in route or not route['color']:
                    route['color'] = '#0066CC'  # Couleur par défaut
                if 'type' not in route or not route['type']:
                    route['type'] = 'Bus'
                if 'short_name' not in route:
                    route['short_name'] = route.get('long_name', 'N/A')
                route['id'] = rid  # Important pour le filtrage
                routes.append(route)
        
        # Limiter au nombre de routes demandé (prioriser tram/métro > bus)
        routes.sort(key=lambda r: (
            0 if r['type'] in ['Tram', 'Métro', 'Metro', 'tram', 'metro'] else 1,
            r['short_name']
        ))
        
        return routes[:limit]
    
    @staticmethod
    def get_next_departures(gtfs_data, stop_id, limit=5, route_filter=None):
        """Obtient les prochains départs (filtrés par routes pertinentes)"""
        if not gtfs_data or 'stop_times' not in gtfs_data:
            return []
        
        if stop_id not in gtfs_data['stop_times']:
            return []
        
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        
        departures = []
        for st in gtfs_data['stop_times'][stop_id]:
            dep_time = st['departure_time']
            
            # Gérer heures > 24
            parts = dep_time.split(':')
            hours = int(parts[0])
            if hours >= 24:
                dep_time = f"{hours-24:02d}:{parts[1]}:{parts[2]}"
            
            # Filtrer par heure actuelle ou générer horaires factices
            if dep_time >= current_time or gtfs_data.get('source') == 'osm':
                trip_id = st['trip_id']
                if trip_id in gtfs_data.get('trips', {}):
                    trip = gtfs_data['trips'][trip_id]
                    route_id = trip['route_id']
                    
                    # Filtrer par routes pertinentes si fourni
                    if route_filter and route_id not in route_filter:
                        continue
                    
                    if route_id in gtfs_data.get('routes', {}):
                        route = gtfs_data['routes'][route_id]
                        
                        # Pour OSM, générer horaires réalistes
                        if gtfs_data.get('source') == 'osm':
                            # Générer 3 horaires dans les 30 prochaines minutes
                            base_minutes = (now.hour * 60 + now.minute)
                            for offset in [5, 15, 25]:
                                future_minutes = base_minutes + offset
                                future_hour = future_minutes // 60
                                future_min = future_minutes % 60
                                fake_time = f"{future_hour:02d}:{future_min:02d}:00"
                                
                                departures.append({
                                    'time': fake_time,
                                    'route': route.get('short_name') or route.get('long_name', 'N/A'),
                                    'headsign': trip.get('headsign', 'Direction Centre'),
                                    'type': route.get('type', 'Bus'),
                                    'color': route.get('color', '#0066CC'),
                                    'estimated': True  # Marquer comme estimé
                                })
                            break  # Une seule fois pour OSM
                        else:
                            # GTFS réel
                            departures.append({
                                'time': dep_time,
                                'route': route.get('short_name') or route.get('long_name', 'N/A'),
                                'headsign': trip.get('headsign', ''),
                                'type': route.get('type', 'Bus'),
                                'color': route.get('color', '#0066CC'),
                                'estimated': False  # Horaire réel
                            })
        
        departures.sort(key=lambda x: x['time'])
        return departures[:limit]


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance haversine entre deux points GPS"""
    R = 6371  # Rayon Terre en km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def geocode(address):
    """Géocode une adresse avec Photon (+ fallback Nominatim) OU utilise coordonnées directes"""
    try:
        # Vérifier si c'est déjà des coordonnées (format: "lat,lon")
        if isinstance(address, str) and ',' in address:
            parts = address.split(',')
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    # Vérifier que c'est dans des plages valides
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        logger.info(f"✓ Coordonnées directes: {lat}, {lon}")
                        return lat, lon, f"Point ({lat:.4f}, {lon:.4f})"
                except ValueError:
                    pass  # Pas des coordonnées valides, continuer avec géocodage
        
        # Essayer d'abord Photon (avec User-Agent)
        logger.info(f"Géocodage: {address}")
        try:
            url = f"https://photon.komoot.io/api/?q={address}&limit=1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            if "features" in data and len(data["features"]) > 0:
                lon, lat = data["features"][0]["geometry"]["coordinates"]
                props = data["features"][0]["properties"]
                place_name = props.get("name", address)
                
                logger.info(f"✓ Géocodage Photon: {lat}, {lon}")
                return lat, lon, place_name
        except Exception as e:
            logger.warning(f"Photon échoué ({e}), essai Nominatim...")
            
            # Fallback vers Nominatim (OpenStreetMap)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'TransportOptimization/1.0 (contact@example.com)'
            }
            
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                place_name = result.get('display_name', address)
                
                logger.info(f"✓ Géocodage Nominatim: {lat}, {lon}")
                return lat, lon, place_name
        
        raise Exception(f"Impossible de géocoder: {address}")
    except Exception as e:
        logger.error(f"Erreur géocodage: {e}")
        raise


def decode_polyline(encoded):
    """Décode une polyline"""
    try:
        return convert.decode_polyline(encoded)['coordinates']
    except Exception as e:
        logger.error(f"Erreur décodage polyline: {e}")
        return []


def get_route(lat1, lon1, lat2, lon2, profile='driving-car'):
    """Calcule un itinéraire avec OpenRouteService"""
    try:
        logger.info(f"Route {profile}: ({lat1},{lon1}) → ({lat2},{lon2})")
        url = f"https://api.openrouteservice.org/v2/directions/{profile}"
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "coordinates": [[lon1, lat1], [lon2, lat2]]
        }
        
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        if "routes" not in data or len(data["routes"]) == 0:
            return [], 0, 0
        
        route = data["routes"][0]
        coords = decode_polyline(route["geometry"])
        distance = route["summary"].get("distance", 0) / 1000  # km
        duration = route["summary"].get("duration", 0) / 60    # min
        
        logger.info(f"✓ {distance:.2f}km, {duration:.2f}min")
        return coords, distance, duration
        
    except Exception as e:
        logger.error(f"Erreur calcul route: {e}")
        return [], 0, 0


def calculate_multimodal_route(start_lat, start_lon, end_lat, end_lon):
    """Calcule un itinéraire multimodal optimal"""
    try:
        # Charger GTFS pour la région de départ
        gtfs_data = GTFSManager.load_gtfs_for_region(start_lat, start_lon)
        
        if not gtfs_data:
            logger.warning("Pas de données transport disponibles")
            return None
        
        # Trouver arrêts proches départ (augmenté à 2km pour grandes villes)
        start_stops = GTFSManager.find_nearby_stops(gtfs_data, start_lat, start_lon, 2.0)
        
        # Trouver arrêts proches arrivée (augmenté à 2km pour grandes villes)
        end_stops = GTFSManager.find_nearby_stops(gtfs_data, end_lat, end_lon, 2.0)
        
        if not start_stops or not end_stops:
            logger.warning("Pas d'arrêts à proximité")
            return None
        
        # Calculer la meilleure option
        best_option = None
        min_time = float('inf')
        
        for start_stop in start_stops[:3]:
            for end_stop in end_stops[:3]:
                # Marche jusqu'à départ
                _, walk_start_dist, walk_start_time = get_route(
                    start_lat, start_lon,
                    start_stop['lat'], start_stop['lon'],
                    'foot-walking'
                )
                
                # Marche depuis arrivée
                _, walk_end_dist, walk_end_time = get_route(
                    end_stop['lat'], end_stop['lon'],
                    end_lat, end_lon,
                    'foot-walking'
                )
                
                # Distance transit
                transit_dist = haversine_distance(
                    start_stop['lat'], start_stop['lon'],
                    end_stop['lat'], end_stop['lon']
                )
                
                # Temps transit (vitesse moyenne 25 km/h)
                transit_time = (transit_dist / 25) * 60
                wait_time = 5  # minutes
                
                total_time = walk_start_time + wait_time + transit_time + walk_end_time
                
                if total_time < min_time:
                    min_time = total_time
                    
                    # Routes et départs - SEULEMENT les routes pertinentes
                    routes = GTFSManager.find_connecting_routes(
                        gtfs_data, 
                        start_stop['id'], 
                        end_stop['id'], 
                        limit=5  # Max 5 lignes pertinentes
                    )
                    
                    # Filtrer départs par routes pertinentes uniquement
                    route_ids = {r['id'] for r in routes}
                    departures = GTFSManager.get_next_departures(
                        gtfs_data, 
                        start_stop['id'], 
                        limit=5,
                        route_filter=route_ids
                    )
                    
                    logger.info(f"🚌 Routes pertinentes: {len(routes)}")
                    for route in routes:
                        logger.info(f"  ✓ {route.get('short_name', 'N/A')} ({route.get('type', 'Bus')}) [{route.get('color', '#0066CC')}]")
                    
                    logger.info(f"⏰ Départs: {len(departures)}")
                    for dep in departures[:3]:
                        estimated_mark = " (estimé)" if dep.get('estimated') else ""
                        logger.info(f"  ⏱️  {dep['route']} à {dep['time']}{estimated_mark}")
                    
                    best_option = {
                        'start_stop': start_stop,
                        'end_stop': end_stop,
                        'routes': routes,
                        'departures': departures,
                        'walk_start': {
                            'distance': walk_start_dist,
                            'duration': walk_start_time
                        },
                        'transit': {
                            'distance': transit_dist,
                            'duration': transit_time
                        },
                        'walk_end': {
                            'distance': walk_end_dist,
                            'duration': walk_end_time
                        },
                        'total_time': total_time,
                        'total_distance': walk_start_dist + transit_dist + walk_end_dist,
                        'source': gtfs_data.get('source', 'unknown')
                    }
        
        return best_option
        
    except Exception as e:
        logger.error(f"Erreur calcul multimodal: {e}")
        return None


@app.route('/api/itineraire', methods=['POST'])
def itineraire():
    """
    Endpoint principal - Calcul d'itinéraire optimisé mondial
    """
    try:
        data = request.json
        depart = data.get("depart")
        destination = data.get("destination")
        mode = data.get("mode", "optimal")
        
        logger.info(f"=== REQUÊTE: {depart} → {destination} [{mode}] ===")
        
        if not depart or not destination:
            return jsonify({"error": "Départ et destination requis"}), 400
        
        # Géocodage
        start_lat, start_lon, start_name = geocode(depart)
        end_lat, end_lon, end_name = geocode(destination)
        
        # Détection pays/ville
        location_info = TransitAPIManager.detect_country_city(start_lat, start_lon)
        logger.info(f"📍 {location_info['city']}, {location_info['country']}")
        
        # Distance directe
        direct_distance = haversine_distance(start_lat, start_lon, end_lat, end_lon)
        
        options = []
        
        # === TRANSPORT EN COMMUN ===
        if mode in ['optimal', 'transport']:
            multimodal = calculate_multimodal_route(start_lat, start_lon, end_lat, end_lon)
            
            if multimodal:
                options.append({
                    'mode': 'transport',
                    'label': 'Transports en commun',
                    'icon': '🚌',
                    'total_time': round(multimodal['total_time'], 1),
                    'total_distance': round(multimodal['total_distance'], 2),
                    'co2_emissions': round(multimodal['total_distance'] * 0.05, 2),
                    'cost_estimate': 1.50,  # Estimation
                    'segments': [
                        {
                            'type': 'walk',
                            'icon': '🚶',
                            'from': start_name,
                            'to': multimodal['start_stop']['name'],
                            'distance': round(multimodal['walk_start']['distance'], 2),
                            'duration': round(multimodal['walk_start']['duration'], 1)
                        },
                        {
                            'type': 'transit',
                            'icon': '🚌',
                            'from': multimodal['start_stop']['name'],
                            'to': multimodal['end_stop']['name'],
                            'distance': round(multimodal['transit']['distance'], 2),
                            'duration': round(multimodal['transit']['duration'], 1),
                            'routes': multimodal['routes'],
                            'departures': multimodal['departures']
                        },
                        {
                            'type': 'walk',
                            'icon': '🚶',
                            'from': multimodal['end_stop']['name'],
                            'to': end_name,
                            'distance': round(multimodal['walk_end']['distance'], 2),
                            'duration': round(multimodal['walk_end']['duration'], 1)
                        }
                    ],
                    'data_source': multimodal['source']
                })
        
        # === VOITURE ===
        if mode in ['optimal', 'voiture']:
            car_coords, car_dist, car_time = get_route(
                start_lat, start_lon, end_lat, end_lon, 'driving-car'
            )
            if car_coords:
                options.append({
                    'mode': 'voiture',
                    'label': 'Voiture',
                    'icon': '🚗',
                    'total_time': round(car_time, 1),
                    'total_distance': round(car_dist, 2),
                    'co2_emissions': round(car_dist * 0.12, 2),
                    'cost_estimate': round(car_dist * 0.15, 2),
                    'route_coords': car_coords
                })
        
        # === VÉLO ===
        if mode in ['optimal', 'velo']:
            bike_coords, bike_dist, bike_time = get_route(
                start_lat, start_lon, end_lat, end_lon, 'cycling-regular'
            )
            if bike_coords:
                options.append({
                    'mode': 'velo',
                    'label': 'Vélo',
                    'icon': '🚴',
                    'total_time': round(bike_time, 1),
                    'total_distance': round(bike_dist, 2),
                    'co2_emissions': 0,
                    'cost_estimate': 0,
                    'route_coords': bike_coords
                })
        
        # === À PIED ===
        if mode in ['optimal', 'pieton'] or direct_distance < 2:
            walk_coords, walk_dist, walk_time = get_route(
                start_lat, start_lon, end_lat, end_lon, 'foot-walking'
            )
            if walk_coords:
                options.append({
                    'mode': 'pieton',
                    'label': 'À pied',
                    'icon': '🚶',
                    'total_time': round(walk_time, 1),
                    'total_distance': round(walk_dist, 2),
                    'co2_emissions': 0,
                    'cost_estimate': 0,
                    'route_coords': walk_coords
                })
        
        # Tri par temps si optimal
        if mode == 'optimal' and options:
            options.sort(key=lambda x: x['total_time'])
        
        # Recommandations intelligentes
        recommendations = []
        if direct_distance < 1.5:
            recommendations.append("🚶 Courte distance - Marche recommandée!")
        elif direct_distance < 5:
            recommendations.append("🚴 Distance idéale pour le vélo")
        
        if options:
            eco_option = min(options, key=lambda x: x['co2_emissions'])
            if eco_option['co2_emissions'] == 0:
                recommendations.append(f"🌱 {eco_option['label']} - Zéro émission!")
            
            fastest = min(options, key=lambda x: x['total_time'])
            cheapest = min(options, key=lambda x: x['cost_estimate'])
            recommendations.append(f"⚡ Plus rapide: {fastest['label']} ({fastest['total_time']}min)")
            recommendations.append(f"💰 Moins cher: {cheapest['label']} ({cheapest['cost_estimate']}€)")
        
        response = {
            "success": True,
            "location": {
                "city": location_info['city'],
                "country": location_info['country'],
                "country_code": location_info['country_code']
            },
            "depart": {
                "address": depart,
                "name": start_name,
                "lat": start_lat,
                "lon": start_lon
            },
            "destination": {
                "address": destination,
                "name": end_name,
                "lat": end_lat,
                "lon": end_lon
            },
            "direct_distance": round(direct_distance, 2),
            "options": options,
            "recommended": options[0] if options else None,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✓ {len(options)} options calculées")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/stops/nearby', methods=['POST'])
def nearby_stops():
    """Trouve les arrêts à proximité"""
    try:
        data = request.json
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        radius = float(data.get('radius', 0.5))
        
        gtfs_data = GTFSManager.load_gtfs_for_region(lat, lon)
        
        if not gtfs_data:
            return jsonify({"success": False, "error": "Pas de données"}), 404
        
        stops = GTFSManager.find_nearby_stops(gtfs_data, lat, lon, radius)
        
        # Enrichir avec routes et départs
        for stop in stops:
            stop['routes'] = GTFSManager.get_routes_at_stop(gtfs_data, stop['id'])
            stop['next_departures'] = GTFSManager.get_next_departures(gtfs_data, stop['id'], 3)
        
        return jsonify({
            "success": True,
            "stops": stops,
            "count": len(stops),
            "source": gtfs_data.get('source', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Erreur stops: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/location/detect', methods=['POST'])
def detect_location():
    """Détecte la ville et le pays à partir de coordonnées"""
    try:
        data = request.json
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        location = TransitAPIManager.detect_country_city(lat, lon)
        
        return jsonify({
            "success": True,
            "location": location
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "worldwide-transport-api",
        "cache_regions": len(gtfs_cache),
        "timestamp": datetime.now().isoformat()
    }), 200 


@app.route('/ready', methods=['GET'])
def ready():
    """Ready check"""
    try:
        response = requests.get("https://photon.komoot.io/api/", timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "not ready"}), 503
    except:
        return jsonify({"status": "not ready"}), 503


@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route non trouvée"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur serveur: {str(error)}")
    return jsonify({"error": "Erreur interne du serveur"}), 500


if __name__ == "__main__":
    logger.info(f"🚀 Démarrage API Transport Mondial sur le port {PORT}")
    logger.info(f"🌍 Support: GTFS mondial + OpenStreetMap fallback")
    app.run(host='0.0.0.0', port=PORT, debug=(FLASK_ENV == 'development'))