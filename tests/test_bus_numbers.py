#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des numéros de bus
"""

import requests
import json

API_URL = "http://127.0.0.1:5000/api/itineraire"

def test_route(depart, destination, mode, city_name):
    """Teste un itinéraire et affiche les infos de transport"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {city_name}")
    print(f"{'='*60}")
    print(f"📍 {depart} → {destination}")
    print(f"🚀 Mode: {mode}")
    
    try:
        response = requests.post(
            API_URL,
            json={"depart": depart, "destination": destination, "mode": mode},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}")
            return
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
            return
        
        print(f"\n✅ Succès - {len(result.get('options', []))} options trouvées")
        
        # Afficher les détails de chaque option
        for i, option in enumerate(result.get('options', []), 1):
            print(f"\n--- Option {i}: {option.get('label', 'N/A')} ---")
            print(f"⏱️  Temps: {option.get('total_time', 0)} min")
            print(f"📏 Distance: {option.get('total_distance', 0)} km")
            print(f"💰 Coût: {option.get('cost_estimate', 0)} €")
            
            # Vérifier les segments
            segments = option.get('segments', [])
            print(f"\n📍 {len(segments)} segments:")
            
            for j, seg in enumerate(segments, 1):
                seg_type = seg.get('type', 'N/A')
                print(f"\n  Segment {j}: {seg_type}")
                print(f"    De: {seg.get('from', 'N/A')}")
                print(f"    À: {seg.get('to', 'N/A')}")
                print(f"    Distance: {seg.get('distance', 0)} km")
                print(f"    Durée: {seg.get('duration', 0)} min")
                
                # Si c'est un segment de transport
                if seg_type == 'transit':
                    routes = seg.get('routes', [])
                    departures = seg.get('departures', [])
                    
                    print(f"\n    🚌 LIGNES TROUVÉES: {len(routes)}")
                    if routes:
                        for route in routes:
                            print(f"      ✓ {route.get('short_name', 'N/A')} - {route.get('long_name', '')}")
                            print(f"        Type: {route.get('type', 'N/A')}")
                            print(f"        Couleur: {route.get('color', 'N/A')}")
                    else:
                        print(f"      ⚠️  Aucune ligne trouvée!")
                    
                    print(f"\n    ⏰ DÉPARTS: {len(departures)}")
                    if departures:
                        for dep in departures[:5]:
                            print(f"      ✓ {dep.get('route', 'N/A')} à {dep.get('time', 'N/A')}")
                            print(f"        Direction: {dep.get('headsign', 'N/A')}")
                    else:
                        print(f"      ⚠️  Aucun départ trouvé!")
        
        print(f"\n{'='*60}\n")
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout - L'API ne répond pas")
    except requests.exceptions.ConnectionError:
        print(f"❌ Erreur de connexion - L'API n'est pas démarrée")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Tests principaux"""
    print("🌍 TEST DE L'API TRANSPORT OPTIMIZATION")
    print("Assurez-vous que l'API tourne sur le port 5000\n")
    
    tests = [
        {
            "depart": "Place de la Victoire, Bordeaux",
            "destination": "Gare Saint-Jean, Bordeaux",
            "mode": "transport",
            "city": "Bordeaux, France"
        },
        {
            "depart": "Châtelet, Paris",
            "destination": "Tour Eiffel, Paris",
            "mode": "transport",
            "city": "Paris, France"
        },
        {
            "depart": "Times Square, New York",
            "destination": "Brooklyn Bridge, New York",
            "mode": "transport",
            "city": "New York, USA"
        }
    ]
    
    for test in tests:
        test_route(
            test["depart"],
            test["destination"],
            test["mode"],
            test["city"]
        )
    
    print("\n✨ Tests terminés!")


if __name__ == "__main__":
    main()
