const map = L.map('map', {
    zoomControl: false, // Cleaner background look
    scrollWheelZoom: false // Prevent scroll trap when scrolling past the hero section
}).setView([-33.4372, -70.6506], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

let currentPolygon = null;

const form = document.getElementById('search-form');
const resultsArea = document.getElementById('results-area');
const scrollPrompt = document.getElementById('scroll-prompt');

// Mock Data logic for Free Report Generation
const mockBaseData = {
    // Zona 3 Requirements
    superficie_terreno: 1200,
    superficie_construida: 850,
    uso: "Residencial y Comercial",
    zona_nombre: "UpR-1",
    normativa: {
        coef_const: 1.2,
        ocup_suelo: 0.40,
        altura_max: "12m (4 Pisos)"
    },
    factor_potencial: "8.5 / 10" // Visual score metric
};

form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const calle = document.getElementById('calle').value;
    const numero = document.getElementById('numero').value;
    const comuna = document.getElementById('comuna').options[document.getElementById('comuna').selectedIndex].text;
    
    // 1. Move map to simulated location
    map.setView([-33.432, -70.615], 16);
    if(currentPolygon) map.removeLayer(currentPolygon);
    currentPolygon = L.polygon([
        [-33.433, -70.616], [-33.431, -70.616], [-33.431, -70.614], [-33.433, -70.614]
    ], {color: "#3b82f6", fillColor: "#3b82f6", fillOpacity: 0.5}).addTo(map);

    // 2. Populate Zona 3
    document.getElementById('address-display').textContent = `${calle} ${numero}, ${comuna}`;
    document.getElementById('val-terreno').textContent = mockBaseData.superficie_terreno.toLocaleString('es-CL') + ' m²';
    document.getElementById('val-construido').textContent = mockBaseData.superficie_construida.toLocaleString('es-CL') + ' m²';
    document.getElementById('val-factor').textContent = mockBaseData.factor_potencial;
    
    document.getElementById('val-zona').textContent = mockBaseData.zona_nombre;
    document.getElementById('val-uso').textContent = mockBaseData.uso;
    
    document.getElementById('val-coef').textContent = mockBaseData.normativa.coef_const;
    document.getElementById('val-ocupacion').textContent = (mockBaseData.normativa.ocup_suelo * 100) + '%';
    document.getElementById('val-altura').textContent = mockBaseData.normativa.altura_max;

    // AI summary is pre-written in HTML for MVP, but can be updated here if needed.

    // 3. Reveal and Scroll to Results
    resultsArea.classList.remove('hidden');
    scrollPrompt.classList.remove('hidden');
    
    // Small delay to allow layout, then smooth scroll down
    setTimeout(() => {
        resultsArea.scrollIntoView({ behavior: 'smooth' });
    }, 200);
});

// Upsell pricing logic placeholder
window.compra = function(tipoInforme) {
    if(tipoInforme === 'basico') {
        alert("Redirigiendo a MercadoPago: Pagarás $15.000 CLP para desbloquear el Nivel Básico (Información tabulada completa).");
    } else if(tipoInforme === 'profesional') {
        alert("Redirigiendo a Flujo de Pago: Informe Profesional cuesta desde $50.000 CLP, analizando constructibilidad extendida.");
    } else if(tipoInforme === 'premium') {
        alert("Redirigiendo a Compra Premium: Estudio comercial y arquitectónico completo desde $250.000 CLP.");
    }
};
