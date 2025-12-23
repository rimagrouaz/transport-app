# 🚀 Guide de Démarrage Rapide

## Installation en 3 minutes

### Option 1 : Installation classique

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd transport-optimization

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API
cp .env.example .env
# Éditer .env et ajouter votre clé OpenRouteService

# 4. Lancer l'application
python app.py
```

### Option 2 : Avec Docker

```bash
# 1. Créer le fichier .env avec votre clé
echo "ORS_API_KEY=votre_clé" > .env

# 2. Build et run
docker-compose up -d

# L'API est accessible sur http://localhost:5000
```

## 🔑 Obtenir une clé OpenRouteService (GRATUIT)

1. Aller sur https://openrouteservice.org/dev/#/signup
2. Créer un compte (gratuit)
3. Copier votre clé API
4. La coller dans le fichier `.env`

**Limites gratuites** : 2000 requêtes/jour

## ✅ Vérifier que ça fonctionne

```bash
# Test health check
curl http://localhost:5000/health

# Test itinéraire
curl -X POST http://localhost:5000/api/itineraire \
  -H "Content-Type: application/json" \
  -d '{
    "depart": "Paris, France",
    "destination": "Versailles, France",
    "mode": "optimal"
  }'
```

## 📱 Intégration avec votre Frontend

### JavaScript / React

```javascript
async function getRoute(depart, destination) {
  const response = await fetch('http://localhost:5000/api/itineraire', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      depart: depart,
      destination: destination,
      mode: 'optimal'
    })
  });
  
  const data = await response.json();
  return data;
}

// Utilisation
const result = await getRoute('Bordeaux', 'Mérignac');
console.log(result.options);
```

### Python

```python
import requests

def get_route(depart, destination):
    response = requests.post(
        'http://localhost:5000/api/itineraire',
        json={
            'depart': depart,
            'destination': destination,
            'mode': 'optimal'
        }
    )
    return response.json()

# Utilisation
result = get_route('Bordeaux', 'Mérignac')
print(result['options'])
```

## 🌍 Exemples de villes supportées

```python
# France
"Bordeaux, France" → "Mérignac, France"
"Paris Gare du Nord" → "Versailles Château"
"Lyon Part-Dieu" → "Confluence"

# USA
"Times Square, New York" → "Brooklyn Bridge"
"Union Square, San Francisco" → "Golden Gate"

# UK
"King's Cross, London" → "Tower Bridge"

# Canada
"Downtown Montreal" → "Old Montreal"
"Union Station, Toronto" → "CN Tower"

# Allemagne
"Brandenburg Gate, Berlin" → "Alexanderplatz"

# Espagne
"Puerta del Sol, Madrid" → "Retiro Park"

# Et n'importe où dans le monde grâce à OpenStreetMap!
```

## 🎯 Modes de transport

```json
{
  "mode": "optimal"     // Toutes les options triées par temps
  "mode": "transport"   // Transports en commun uniquement
  "mode": "voiture"     // Voiture
  "mode": "velo"        // Vélo
  "mode": "pieton"      // Marche
}
```

## 📊 Structure de la réponse

```json
{
  "success": true,
  "location": {
    "city": "Bordeaux",
    "country": "France"
  },
  "depart": { "lat": 44.8378, "lon": -0.5792 },
  "destination": { "lat": 44.8347, "lon": -0.6458 },
  "direct_distance": 5.2,
  "options": [
    {
      "mode": "transport",
      "label": "Transports en commun",
      "total_time": 25.5,
      "total_distance": 6.1,
      "co2_emissions": 0.31,
      "cost_estimate": 1.50,
      "segments": [...]
    }
  ],
  "recommended": {...},
  "recommendations": [...]
}
```

## 🔧 Troubleshooting

### Erreur : "Impossible de géocoder"
- Vérifiez l'orthographe de l'adresse
- Ajoutez le pays : "Paris, France" au lieu de "Paris"

### Erreur : API OpenRouteService
- Vérifiez votre clé API dans .env
- Vérifiez que vous n'avez pas dépassé les 2000 req/jour

### Pas de données de transport
- L'API utilise automatiquement OpenStreetMap en fallback
- Certaines petites villes ont moins de données

### Docker ne démarre pas
- Vérifiez que le port 5000 n'est pas déjà utilisé
- `docker-compose logs` pour voir les erreurs

## 📞 Support

- 📧 Email : votre@email.com
- 🐛 Issues : GitHub Issues
- 📖 Documentation complète : README.md

## 🎉 Vous êtes prêt !

L'API est maintenant opérationnelle. Consultez le README.md pour plus de détails.

---

**Happy coding! 🚀**
