#!/usr/bin/env python3
"""
Script de test pour l'API Transport Optimization
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_itineraire_bordeaux():
    """Test itinéraire Bordeaux"""
    print("\n=== TEST 1: Itinéraire Bordeaux → Mérignac ===")
    
    response = requests.post(
        f"{BASE_URL}/api/itineraire",
        json={
            "depart": "Bordeaux, France",
            "destination": "Mérignac, France",
            "mode": "optimal"
        }
    )
    
    data = response.json()
    
    if data['success']:
        print(f"✓ Succès!")
        print(f"📍 {data['location']['city']}, {data['location']['country']}")
        print(f"📏 Distance directe: {data['direct_distance']} km")
        print(f"\n🚦 {len(data['options'])} options disponibles:")
        
        for opt in data['options']:
            print(f"\n  {opt['icon']} {opt['label']}")
            print(f"    Temps: {opt['total_time']} min")
            print(f"    Distance: {opt['total_distance']} km")
            print(f"    CO2: {opt['co2_emissions']} kg")
            print(f"    Coût: {opt['cost_estimate']}€")
            
            if opt['mode'] == 'transport' and 'segments' in opt:
                print(f"    Segments:")
                for seg in opt['segments']:
                    print(f"      - {seg['icon']} {seg['from']} → {seg['to']}")
                    if seg['type'] == 'transit' and seg.get('routes'):
                        for route in seg['routes'][:2]:
                            print(f"        Ligne: {route['short_name']} - {route['long_name']}")
        
        print(f"\n💡 Recommandations:")
        for rec in data['recommendations']:
            print(f"  {rec}")
    else:
        print(f"❌ Erreur: {data['error']}")


def test_itineraire_paris():
    """Test itinéraire Paris"""
    print("\n=== TEST 2: Itinéraire Paris → Versailles ===")
    
    response = requests.post(
        f"{BASE_URL}/api/itineraire",
        json={
            "depart": "Paris Gare du Nord",
            "destination": "Versailles Château",
            "mode": "optimal"
        }
    )
    
    data = response.json()
    
    if data['success']:
        print(f"✓ Succès!")
        print(f"📏 Distance: {data['direct_distance']} km")
        print(f"🏆 Meilleure option: {data['recommended']['label']} ({data['recommended']['total_time']} min)")
    else:
        print(f"❌ Erreur: {data['error']}")


def test_itineraire_international():
    """Test itinéraire international"""
    print("\n=== TEST 3: Itinéraire New York ===")
    
    response = requests.post(
        f"{BASE_URL}/api/itineraire",
        json={
            "depart": "Times Square, New York",
            "destination": "Brooklyn Bridge, New York",
            "mode": "optimal"
        }
    )
    
    data = response.json()
    
    if data['success']:
        print(f"✓ Succès!")
        print(f"📍 {data['location']['city']}, {data['location']['country']}")
        print(f"🚦 {len(data['options'])} options")
    else:
        print(f"❌ Erreur: {data['error']}")


def test_stops_nearby():
    """Test arrêts à proximité"""
    print("\n=== TEST 4: Arrêts proches (Place de la Victoire, Bordeaux) ===")
    
    response = requests.post(
        f"{BASE_URL}/api/stops/nearby",
        json={
            "lat": 44.8264,
            "lon": -0.5731,
            "radius": 0.3
        }
    )
    
    data = response.json()
    
    if data['success']:
        print(f"✓ {data['count']} arrêts trouvés (source: {data['source']})")
        
        for stop in data['stops'][:3]:
            print(f"\n  🚏 {stop['name']}")
            print(f"     Distance: {stop['distance']}m")
            
            if stop.get('routes'):
                print(f"     Lignes:")
                for route in stop['routes'][:3]:
                    print(f"       - {route['short_name']}: {route['long_name']}")
            
            if stop.get('next_departures'):
                print(f"     Prochains départs:")
                for dep in stop['next_departures'][:2]:
                    print(f"       - {dep['time']} | {dep['route']} → {dep['headsign']}")
    else:
        print(f"❌ Erreur: {data['error']}")


def test_location_detect():
    """Test détection de localisation"""
    print("\n=== TEST 5: Détection localisation ===")
    
    response = requests.post(
        f"{BASE_URL}/api/location/detect",
        json={
            "lat": 51.5074,
            "lon": -0.1278
        }
    )
    
    data = response.json()
    
    if data['success']:
        loc = data['location']
        print(f"✓ {loc['city']}, {loc['country']} ({loc['country_code']})")
    else:
        print(f"❌ Erreur: {data['error']}")


def test_health():
    """Test health check"""
    print("\n=== TEST 6: Health Check ===")
    
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Service: {data['service']}")
    print(f"Régions en cache: {data['cache_regions']}")
    print(f"Timestamp: {data['timestamp']}")


if __name__ == "__main__":
    print("🚀 Tests de l'API Transport Optimization")
    print("=" * 60)
    
    try:
        # Vérifier si l'API est accessible
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible. Lancez d'abord: python app.py")
            exit(1)
        
        # Lancer les tests
        test_health()
        test_itineraire_bordeaux()
        test_itineraire_paris()
        test_itineraire_international()
        test_stops_nearby()
        test_location_detect()
        
        print("\n" + "=" * 60)
        print("✅ Tous les tests sont terminés!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API.")
        print("   Assurez-vous que l'application tourne sur http://localhost:5000")
        print("   Lancez: python app.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")
