// ==========================================
// SCROLLYTELLING MAP & INTERACTIVITY
// ==========================================

const map = L.map('map', {
    zoomControl: false,
    scrollWheelZoom: false, // Map is purely for cinematic background
    dragging: false,
    doubleClickZoom: false
}).setView([-33.4372, -70.6506], 12);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

let currentPolygon = null;

// DOM Elements
const form = document.getElementById('search-form');
const comunaSelect = document.getElementById('comuna');
const resultsArea = document.getElementById('results-area');
const scrollPrompt = document.getElementById('scroll-prompt');
const mapOverlay = document.querySelector('.map-overlay-layer');

// Pre-defined Comuna Centers for Cinematic Flyovers
const comunaCoords = {
    'Providencia': [-33.432, -70.615],
    'Las Condes': [-33.400, -70.550],
    'Vitacura': [-33.380, -70.580],
    'Santiago Centro': [-33.437, -70.650],
    'Ñuñoa': [-33.455, -70.600] // Added default
};

// 1. Hover/Change Location - Fly the map smoothly!
comunaSelect.addEventListener('change', (e) => {
    const val = e.target.options[e.target.selectedIndex].text;
    if (comunaCoords[val]) {
        map.flyTo(comunaCoords[val], 13, {
            animate: true,
            duration: 1.5
        });
    }
});

// 2. Submit - Zoom to actual property, Draw Polygon, Reveal content
form.addEventListener('submit', (e) => {
    e.preventDefault();

    // Dim the overlay completely so the polygon really shines
    mapOverlay.style.backdropFilter = 'blur(0px)';
    mapOverlay.style.background = 'radial-gradient(circle at center, rgba(15, 23, 42, 0.1) 0%, rgba(2, 6, 23, 0.8) 100%)';

    const selectedComunaText = comunaSelect.options[comunaSelect.selectedIndex].text;
    const baseCoords = comunaCoords[selectedComunaText] || [-33.432, -70.615];

    // Simulate Address specific coords (Slight offset from comuna center)
    const propertyExtents = [
        [baseCoords[0] - 0.001, baseCoords[1] - 0.001],
        [baseCoords[0] + 0.001, baseCoords[1] - 0.001],
        [baseCoords[0] + 0.001, baseCoords[1] + 0.001],
        [baseCoords[0] - 0.001, baseCoords[1] + 0.001]
    ];

    // 1. Zoom To Bounds and Center using 3.0s Cinematic Fly
    map.flyTo(baseCoords, 17, { animate: true, duration: 3.0 });

    // 2. Cross-fade the UI simultaneously
    const heroSection = document.querySelector('.hero-map-section');
    heroSection.classList.add('fade-out');

    // Unhide Results logically and spawn the cinematic fade-in
    resultsArea.style.display = 'block';
    resultsArea.classList.add('fade-in');

    // Normalize Address Title Case and Add ROL
    const inputCalle = document.getElementById('calle').value;
    const inputNum = document.getElementById('numero').value;
    const addressCombined = `${inputCalle} ${inputNum}, ${selectedComunaText}`.toLowerCase().replace(/(^\w{1})|(\s+\w{1})/g, letter => letter.toUpperCase());

    document.getElementById('address-display').textContent = `${addressCombined} | ROL: 3145-12`;

    // 3. Wait exactly 3 seconds for the map to arrive, then inject polygon
    setTimeout(() => {
        if (currentPolygon) map.removeLayer(currentPolygon);
        // "resaltada tenuamente en el mapa" -> A glowing golden polygon!
        currentPolygon = L.polygon(propertyExtents, {
            color: "#fbbf24", // Dorado (Golden border)
            weight: 3,
            fillColor: "#f59e0b", // Dorado (Golden fill)
            fillOpacity: 0.35,
            className: 'glowing-property'
        }).addTo(map);

    }, 3000); // 3 seconds timeout exactly matches the flyTo and CSS animation durations!
});


// ==========================================
// UPSELLS
// ==========================================
window.compra = function (tipoInforme) {
    if (tipoInforme === 'basico') {
        alert("Integración MercadoPago: Redirigiendo al pago de $15.000 CLP para informe Básico.");
    } else if (tipoInforme === 'profesional') {
        alert("Integración MercadoPago: Redirigiendo al flujo Profesional.");
    } else {
        alert("Integración MercadoPago: Flujo de venta Premium Máximo Potencial.");
    }
};
