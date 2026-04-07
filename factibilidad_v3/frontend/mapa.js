// Init Full Map
const map = L.map('full-map', {
    zoomControl: true,
    minZoom: 10,
}).setView([-33.4485, -70.6695], 11); // Start zoomed out slightly in RM

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

// Mocks de Zonas Doradas para Venta (These simulate the 1.300 ingested zones)
const mockZonas = [
    { coords: [[-33.42, -70.61], [-33.41, -70.60], [-33.41, -70.58], [-33.43, -70.60]], type: 'A' }, // Providencia/Las Condes
    { coords: [[-33.46, -70.66], [-33.45, -70.65], [-33.45, -70.63], [-33.47, -70.65]], type: 'B' }, // Santiago Sur
    { coords: [[-33.40, -70.55], [-33.39, -70.54], [-33.38, -70.52], [-33.41, -70.54]], type: 'A' }  // Vitacura
];

mockZonas.forEach(z => {
    L.polygon(z.coords, {
        color: z.type === 'A' ? "#10b981" : "#fbbf24", // Verde esmeralda para Tipo A, Dorado para B
        weight: 2, 
        fillColor: z.type === 'A' ? "#059669" : "#d97706",
        fillOpacity: 0.4
    }).addTo(map);
});

function simularPago() {
    const btn = document.querySelector('.paywall-box .btn-primary');
    btn.innerHTML = "Procesando pago seguro...";
    btn.style.opacity = '0.7';

    setTimeout(() => {
        // [LINK_DE_PAGO_MERCADOPAGO_AQUI] (En Producción)
        window.location.href = "aprobado.html";
    }, 1500);
}
