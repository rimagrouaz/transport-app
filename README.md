# 🌍 API Transport Optimization - Worldwide

Application Flask robuste pour l'optimisation d'itinéraires de transport dans le monde entier avec données GTFS réelles et fallback OpenStreetMap.

## 🚀 Fonctionnalités

### ✨ Principales caractéristiques
- **🌐 Couverture mondiale** : Fonctionne partout dans le monde
- **🚌 Données réelles** : GTFS + OpenStreetMap pour les transports en commun
- **🎯 Optimisation multi-modale** : Combine marche, bus, tram, métro, vélo, voiture
- **💾 Cache intelligent** : Stockage en mémoire des données GTFS (24h)
- **🔄 Fallback automatique** : OSM si GTFS indisponible
- **⚡ Temps réel** : Horaires et lignes de transport réels
- **♻️ Écologique** : Calcul d'émissions CO2 et recommandations vertes

### 🗺️ Sources de données

1. **GTFS (General Transit Feed Specification)**
   - Mobility Database API (base mondiale)
   - Sources locales préconfigurées (50+ villes)
   - Horaires réels, numéros de lignes, arrêts précis

2. **OpenStreetMap (Fallback)**
   - Overpass API pour données de transport
   - Couverture mondiale garantie
   - Arrêts et lignes communautaires

3. **OpenRouteService**
   - Calcul d'itinéraires (voiture, vélo, marche)
   - Polylines optimisées

4. **Photon**
   - Géocodage gratuit (OpenStreetMap)
   - Reverse geocoding pour détection pays/ville

## 📋 Prérequis

```bash
Python 3.8+
pip
```

## 🔧 Installation

### 1. Cloner et installer les dépendances

```bash
git clone <votre-repo>
cd transport-optimization
pip install -r requirements.txt
```

### 2. Configuration

Créer un fichier `.env` :

```env
ORS_API_KEY=votre_clé_openrouteservice
FLASK_ENV=development
PORT=5000
```

**Obtenir une clé OpenRouteService (GRATUITE)** :
1. Aller sur https://openrouteservice.org/dev/#/signup
2. S'inscrire gratuitement
3. Copier la clé API

### 3. Lancer l'application

```bash
python app.py
```

L'API sera disponible sur `http://localhost:5000`

## 📡 API Endpoints

### 1. Calcul d'itinéraire optimisé

**POST** `/api/itineraire`

```json
{
  "depart": "Bordeaux, France",
  "destination": "Mérignac, France",
  "mode": "optimal"
}
```

**Modes disponibles** :
- `optimal` : Toutes les options triées par temps
- `transport` : Transports en commun uniquement
- `voiture` : Voiture uniquement
- `velo` : Vélo uniquement
- `pieton` : Marche uniquement

**Réponse** :

```json
{
  "success": true,
  "location": {
    "city": "Bordeaux",
    "country": "France",
    "country_code": "FR"
  },
  "depart": {
    "address": "Bordeaux, France",
    "name": "Bordeaux",
    "lat": 44.8378,
    "lon": -0.5792
  },
  "destination": {
    "address": "Mérignac, France",
    "name": "Mérignac",
    "lat": 44.8347,
    "lon": -0.6458
  },
  "direct_distance": 5.2,
  "options": [
    {
      "mode": "transport",
      "label": "Transports en commun",
      "icon": "🚌",
      "total_time": 25.5,
      "total_distance": 6.1,
      "co2_emissions": 0.31,
      "cost_estimate": 1.50,
      "segments": [
        {
          "type": "walk",
          "icon": "🚶",
          "from": "Bordeaux",
          "to": "Hôtel de Ville",
          "distance": 0.3,
          "duration": 4.2
        },
        {
          "type": "transit",
          "icon": "🚌",
          "from": "Hôtel de Ville",
          "to": "Mérignac Centre",
          "distance": 5.2,
          "duration": 18.0,
          "routes": [
            {
              "id": "1",
              "short_name": "B1",
              "long_name": "Liane B1",
              "type": "Bus",
              "color": "#FF0000"
            }
          ],
          "departures": [
            {
              "time": "14:35:00",
              "route": "B1",
              "headsign": "Mérignac Aéroport",
              "type": "Bus",
              "color": "#FF0000"
            }
          ]
        },
        {
          "type": "walk",
          "icon": "🚶",
          "from": "Mérignac Centre",
          "to": "Mérignac",
          "distance": 0.6,
          "duration": 7.8
        }
      ],
      "data_source": "gtfs"
    },
    {
      "mode": "velo",
      "label": "Vélo",
      "icon": "🚴",
      "total_time": 18.2,
      "total_distance": 5.4,
      "co2_emissions": 0,
      "cost_estimate": 0,
      "route_coords": [[...]]
    }
  ],
  "recommended": {...},
  "recommendations": [
    "🚴 Distance idéale pour le vélo",
    "🌱 Vélo - Zéro émission!",
    "⚡ Plus rapide: Vélo (18.2min)",
    "💰 Moins cher: Vélo (0€)"
  ],
  "timestamp": "2025-01-15T14:30:00"
}
```

### 2. Arrêts à proximité

**POST** `/api/stops/nearby`

```json
{
  "lat": 44.8378,
  "lon": -0.5792,
  "radius": 0.5
}
```

**Réponse** :

```json
{
  "success": true,
  "stops": [
    {
      "id": "stop_123",
      "name": "Hôtel de Ville",
      "lat": 44.8378,
      "lon": -0.5792,
      "distance": 50,
      "routes": [
        {
          "short_name": "B1",
          "long_name": "Liane B1",
          "type": "Bus",
          "color": "#FF0000"
        }
      ],
      "next_departures": [
        {
          "time": "14:35:00",
          "route": "B1",
          "headsign": "Mérignac Aéroport",
          "type": "Bus",
          "color": "#FF0000"
        }
      ]
    }
  ],
  "count": 5,
  "source": "gtfs"
}
```

### 3. Détection de localisation

**POST** `/api/location/detect`

```json
{
  "lat": 44.8378,
  "lon": -0.5792
}
```

### 4. Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "worldwide-transport-api",
  "cache_regions": 3,
  "timestamp": "2025-01-15T14:30:00"
}
```

## 🏗️ Architecture

```
app.py
├── TransitAPIManager          # Gestion APIs de transport
│   ├── detect_country_city()  # Détection géographique
│   ├── search_gtfs_feeds()    # Recherche flux GTFS
│   ├── get_local_gtfs_sources() # Base GTFS locale
│   └── get_transit_data_overpass() # Fallback OSM
│
├── GTFSManager                # Gestion données GTFS
│   ├── load_gtfs_for_region() # Chargement avec cache
│   ├── download_and_parse_gtfs() # Téléchargement
│   ├── find_nearby_stops()    # Recherche arrêts
│   ├── get_routes_at_stop()   # Lignes par arrêt
│   └── get_next_departures()  # Prochains départs
│
├── Fonctions utilitaires
│   ├── geocode()              # Photon geocoding
│   ├── get_route()            # OpenRouteService
│   ├── calculate_multimodal_route() # Calcul multimodal
│   └── haversine_distance()   # Distance GPS
│
└── Endpoints Flask
    ├── /api/itineraire        # Calcul principal
    ├── /api/stops/nearby      # Arrêts proches
    ├── /api/location/detect   # Détection lieu
    └── /health                # Health check
```

## 🎯 Villes supportées (GTFS préconfigurées)

### France
- Bordeaux (TBM)
- Paris (RATP)
- Lyon (TCL)

### USA
- New York (MTA)
- San Francisco (BART)
- Chicago (CTA)

### Europe
- Londres (TfL)
- Berlin (BVG)
- Madrid (EMT)
- Barcelona (TMB)
- Rome (ATAC)
- Milan (ATM)
- Amsterdam (GVB)
- Brussels (STIB)

### Canada
- Montreal (STM)
- Toronto (TTC)

### Australie
- Sydney (Transport NSW)
- Melbourne (PTV)

### Japon
- Tokyo (Tokyo Metro)

**+ Toutes les autres villes via OpenStreetMap**

## 🔒 Sécurité & Performance

### Cache
- **Durée** : 24 heures par région
- **Clé** : Coordonnées arrondies (lat_lon)
- **Thread-safe** : Verrous pour accès concurrent

### Limitations
- **stop_times.txt** : Limité à 100 000 entrées (évite surcharge mémoire)
- **Arrêts proches** : Rayon max 0.5 km
- **Top 3** : Seulement les 3 meilleurs arrêts analysés

### Robustesse
- ✅ Gestion d'erreurs complète
- ✅ Fallback automatique (GTFS → OSM)
- ✅ Retry sur échecs réseau
- ✅ Timeouts configurés
- ✅ Logs détaillés

## 🐳 Déploiement Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

**Build et run** :

```bash
docker build -t transport-api .
docker run -p 5000:5000 -e ORS_API_KEY=votre_clé transport-api
```

## ☁️ Déploiement Cloud

### Heroku

```bash
heroku create transport-api
heroku config:set ORS_API_KEY=votre_clé
git push heroku main
```

### Railway / Render

1. Connecter le repo GitHub
2. Ajouter variable d'environnement `ORS_API_KEY`
3. Deploy automatique

## 🧪 Tests

### Test manuel avec curl

```bash
# Test itinéraire
curl -X POST http://localhost:5000/api/itineraire \
  -H "Content-Type: application/json" \
  -d '{
    "depart": "Paris, France",
    "destination": "Versailles, France",
    "mode": "optimal"
  }'

# Test arrêts proches
curl -X POST http://localhost:5000/api/stops/nearby \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 48.8566,
    "lon": 2.3522,
    "radius": 0.3
  }'
```

## 🚦 Limites & Quotas

### OpenRouteService (Gratuit)
- **2 000 requêtes/jour**
- **40 requêtes/minute**

Si dépassement → Envisager :
- Clé premium OpenRouteService
- Alternative : GraphHopper, Mapbox

### APIs utilisées
- ✅ **Photon** : Illimité (OSM)
- ✅ **Overpass API** : Rate limit 2 req/sec
- ⚠️ **OpenRouteService** : 2000/jour gratuit

## 💡 Améliorations futures

- [ ] **GTFS-RT** : Données temps réel avec delays
- [ ] **Multi-legs transit** : Correspondances multiples
- [ ] **Prix dynamiques** : Calcul coûts réels par ville
- [ ] **Isochrones** : Zones accessibles en X minutes
- [ ] **WebSocket** : Updates en temps réel
- [ ] **GraphQL** : API alternative
- [ ] **Redis** : Cache distribué
- [ ] **PostgreSQL/PostGIS** : Stockage GTFS persistant

## 📄 Licence

MIT

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou PR.

## 📧 Support

Pour toute question : votre@email.com

---

**Made with ❤️ for sustainable urban mobility**
