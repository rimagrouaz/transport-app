// Initialize map centered on Bordeaux
let map;
let routeLayer;
let markersLayer;

// Initialize the map
function initMap() {
    map = L.map('map').setView([44.8378, -0.5792], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Create layer groups
    routeLayer = L.layerGroup().addTo(map);
    markersLayer = L.layerGroup().addTo(map);
    
    console.log('Map initialized');
}

// Check API health status
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('status').className = 'status-indicator online';
            document.getElementById('statusText').textContent = 'Service en ligne';
        } else {
            document.getElementById('status').className = 'status-indicator offline';
            document.getElementById('statusText').textContent = 'Service hors ligne';
        }
    } catch (error) {
        document.getElementById('status').className = 'status-indicator offline';
        document.getElementById('statusText').textContent = 'Service hors ligne';
    }
}

// Create custom marker icon
function createMarkerIcon(color, icon) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3); font-size: 16px;">${icon}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

// Display route on map
function displayRoute(routeCoords, depart, destination, buses) {
    // Clear previous route and markers
    routeLayer.clearLayers();
    markersLayer.clearLayers();
    
    if (!routeCoords || routeCoords.length === 0) {
        console.error('No route coordinates');
        return;
    }
    
    // Convert coordinates for Leaflet (swap lon/lat to lat/lon)
    const latLngs = routeCoords.map(coord => [coord[1], coord[0]]);
    
    // Draw route
    const polyline = L.polyline(latLngs, {
        color: '#2563eb',
        weight: 5,
        opacity: 0.7,
        smoothFactor: 1
    }).addTo(routeLayer);
    
    // Fit map to route bounds
    map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
    
    // Add start marker
    const startMarker = L.marker(latLngs[0], {
        icon: createMarkerIcon('#10b981', '🚩')
    }).addTo(markersLayer);
    startMarker.bindPopup(`<b>Départ</b><br>${depart}`);
    
    // Add end marker
    const endMarker = L.marker(latLngs[latLngs.length - 1], {
        icon: createMarkerIcon('#ef4444', '🎯')
    }).addTo(markersLayer);
    endMarker.bindPopup(`<b>Destination</b><br>${destination}`);
    
    // Add bus markers if available
    if (buses && buses.length > 0) {
        buses.forEach(bus => {
            const busMarker = L.marker([bus.lat, bus.lon], {
                icon: createMarkerIcon(bus.color, '🚌')
            }).addTo(markersLayer);
            
            const popupContent = `
                <div style="min-width: 150px;">
                    <b>${bus.route_name}</b><br>
                    <small>ID: ${bus.id}</small><br>
                    Vitesse: ${bus.speed} km/h<br>
                    Passagers: ${bus.passengers}/50<br>
                    ${bus.delay > 0 ? `⚠️ Retard: ${bus.delay} min` : '✅ À l\'heure'}
                </div>
            `;
            busMarker.bindPopup(popupContent);
        });
    }
}

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';
    
    // Update stats
    document.getElementById('distance').textContent = data.distance.toFixed(2);
    document.getElementById('duration').textContent = Math.round(data.duration);
    document.getElementById('urbanScore').textContent = data.urban_score;
    document.getElementById('co2').textContent = data.co2_emissions.toFixed(2);
    
    // Display recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        const recommendationsDiv = document.getElementById('recommendations');
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsDiv.style.display = 'block';
        recommendationsList.innerHTML = '';
        
        data.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsList.appendChild(li);
        });
    } else {
        document.getElementById('recommendations').style.display = 'none';
    }
    
    // Display bus list
    if (data.buses && data.buses.length > 0) {
        const busListDiv = document.getElementById('busList');
        const busContainer = document.getElementById('busContainer');
        busListDiv.style.display = 'block';
        busContainer.innerHTML = '';
        
        data.buses.forEach(bus => {
            const busItem = document.createElement('div');
            busItem.className = 'bus-item';
            
            const delayClass = bus.delay <= 0 ? 'on-time' : 'delayed';
            const delayText = bus.delay <= 0 ? '✅ À l\'heure' : `⚠️ +${bus.delay} min`;
            
            busItem.innerHTML = `
                <div class="bus-info">
                    <div class="bus-route">${bus.route_name}</div>
                    <div class="bus-status">
                        ID: ${bus.id} | 
                        ${bus.passengers} passagers | 
                        ${bus.speed} km/h
                    </div>
                </div>
                <div class="bus-delay ${delayClass}">${delayText}</div>
            `;
            
            busContainer.appendChild(busItem);
        });
    } else {
        document.getElementById('busList').style.display = 'none';
    }
    
    // Display route on map
    displayRoute(data.route_coords, data.depart, data.destination, data.buses);
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = `❌ Erreur: ${message}`;
    errorDiv.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Handle form submission
document.getElementById('routeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const depart = document.getElementById('depart').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const mode = document.getElementById('mode').value;
    
    // Validate
    if (!depart || !destination) {
        showError('Veuillez remplir tous les champs');
        return;
    }
    
    // Update button state
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    // Hide previous results and errors
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    
    try {
        // Call API
        const response = await fetch('/api/itineraire', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ depart, destination, mode })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Erreur lors du calcul de l\'itinéraire');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Erreur de connexion au serveur');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Example locations for quick testing
const examples = [
    {
        depart: 'Gare Saint-Jean, Bordeaux',
        destination: 'Place de la Victoire, Bordeaux'
    },
    {
        depart: 'Place de la Bourse, Bordeaux',
        destination: 'Cité du Vin, Bordeaux'
    },
    {
        depart: 'Université de Bordeaux',
        destination: 'Grand Théâtre, Bordeaux'
    }
];

// Add double-click event for quick example
let clickCount = 0;
document.getElementById('depart').addEventListener('click', () => {
    clickCount++;
    if (clickCount === 2) {
        const example = examples[Math.floor(Math.random() * examples.length)];
        document.getElementById('depart').value = example.depart;
        document.getElementById('destination').value = example.destination;
        clickCount = 0;
    }
    setTimeout(() => clickCount = 0, 500);
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    checkHealth();
    
    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
    
    console.log('Application initialized');
});
