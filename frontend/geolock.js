const map = L.map('map').setView([51.505, -0.09], 13);

// Define different tile layers
const standardLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap, © CartoDB'
});

const satelliteLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

// Add the standard layer to the map initially
standardLayer.addTo(map);

// Define base maps for layer control
const baseMaps = {
    "Standard": standardLayer,
    "Dark Mode": darkLayer,
    "Satellite": satelliteLayer
};

// Add layer control to the map
L.control.layers(baseMaps).addTo(map);

let marker;
let circle;
let trail = [];
let userMarker;
let userCircle;

async function connectWebSocket() {
    const websocket = new WebSocket('ws://localhost:8765');

    websocket.onmessage = function(event) {
        const message = event.data;
        const [latitude, longitude] = message.split(', ').map(coord => parseFloat(coord.split('=')[1]));
        updateMap(latitude, longitude);
    };

    websocket.onerror = function(error) {
        console.error('WebSocket Error: ', error);
    };
}

function updateMap(lat, lon) {
    if (marker) {
        map.removeLayer(marker);
    }
    if (circle) {
        map.removeLayer(circle);
    }

    marker = L.marker([lat, lon], { icon: redIcon }).addTo(map);
    circle = L.circle([lat, lon], { radius: 50, color: 'red' }).addTo(map);

    // Add new coordinates to trail
    trail.push([lat, lon]);

    // Remove old polyline and create a new one with the updated trail
    if (trail.length > 1) {
        if (window.polyline) {
            map.removeLayer(window.polyline);
        }
        window.polyline = L.polyline(trail, { color: 'blue' }).addTo(map);
    }

    // Get the current zoom level
    const currentZoom = map.getZoom();

    // Update map view without changing the zoom level
    map.setView([lat, lon], currentZoom);

    document.getElementById('coordinates').textContent = `Coordinates: ${lat}, ${lon}`;
    document.getElementById('address').textContent = `Address: Fetching...`;

    // Fetch address using reverse geocoding
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            const address = data.display_name;
            document.getElementById('address').textContent = `Address: ${address}`;
        })
        .catch(error => {
            console.error('Error fetching address:', error);
            document.getElementById('address').textContent = 'Address: Error fetching address';
        });
}

function geolocateUser() {
    if ('geolocation' in navigator) {
        alert("Geolocation feature might be inaccurate on non-GPS enabled devices.");

        navigator.geolocation.getCurrentPosition(position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            if (userMarker) {
                map.removeLayer(userMarker);
            }
            if (userCircle) {
                map.removeLayer(userCircle);
            }

            userMarker = L.marker([lat, lon], { icon: blueIcon }).addTo(map);
            userCircle = L.circle([lat, lon], { radius: accuracy, color: 'blue' }).addTo(map);

            map.setView([lat, lon]);
        }, error => {
            console.error('Geolocation Error: ', error);
            alert("Unable to retrieve your location.");
        });
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

const redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const blueIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

document.getElementById('geolocate-btn').addEventListener('click', geolocateUser);

connectWebSocket();
