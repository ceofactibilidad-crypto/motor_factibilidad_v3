const map = L.map('map', {
    zoomControl: false,
    scrollWheelZoom: false 
}).setView([-33.4372, -70.6506], 13);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

let currentPolygon = null;

const form = document.getElementById('search-form');
const resultsArea = document.getElementById('results-area');
const scrollPrompt = document.getElementById('scroll-prompt');

let currentChart = null;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const calle = document.getElementById('calle').value;
    const numero = document.getElementById('numero').value;
    const comuna = document.getElementById('comuna').options[document.getElementById('comuna').selectedIndex].text;
    const btn = document.getElementById('btn-gratis');
    
    btn.innerHTML = '<span class="loading-spinner"></span> Analizando...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/analizar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                calle: calle,
                numero: parseInt(numero, 10),
                comuna: comuna,
                region: "Metropolitana",
                tier: "GRATIS"
            })
        });

        if (!response.ok) throw new Error("Error en la petición");
        
        const data = await response.json();

        // 1. Mover Mapa y Pintar Poligono referencial
        const [lat_str, lon_str] = data.coordenadas.split(',');
        const lat = parseFloat(lat_str);
        const lon = parseFloat(lon_str);

        map.setView([lat, lon], 16);
        if(currentPolygon) map.removeLayer(currentPolygon);
        const buffer = 0.001; 
        currentPolygon = L.polygon([
            [lat + buffer, lon - buffer], [lat - buffer, lon - buffer], [lat - buffer, lon + buffer], [lat + buffer, lon + buffer]
        ], {color: "#3b82f6", fillColor: "#3b82f6", fillOpacity: 0.5}).addTo(map);

        // 2. Poblar datos del informe base
        document.getElementById('address-display').innerHTML = `<span class='semaforo-badge ${data.color_mapa}'></span> ` + data.direccion;
        document.getElementById('val-terreno').textContent = data.terreno_m2.toLocaleString('es-CL') + ' m²';
        document.getElementById('val-construido').textContent = data.construido_m2.toLocaleString('es-CL') + ' m²';
        document.getElementById('val-factor').textContent = data.factor_potencial + " / 10";
        
        document.getElementById('val-zona').textContent = data.zona;
        document.getElementById('val-uso').textContent = data.destino_sii;
        
        document.getElementById('val-coef').textContent = data.constructibilidad || "Norma Pendiente";
        document.getElementById('val-ocupacion').textContent = (data.ocupacion_suelo) ? data.ocupacion_suelo + '%' : "Variable";
        document.getElementById('val-altura').textContent = data.altura_maxima;
        document.getElementById('val-ai').textContent = data.analisis_ia;

        // 3. Renderizar Gráfica
        const ctx = document.getElementById('potencialChart').getContext('2d');
        if(currentChart) {
            currentChart.destroy();
        }

        currentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Terreno Base m²', 'Ya Construido m²', 'Potencial Máximo m²'],
                datasets: [{
                    label: 'Metraje (m²)',
                    data: [data.terreno_m2, data.construido_m2, data.potencial_edificable || (data.terreno_m2 * (data.constructibilidad || 1.0))],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.6)', 
                        'rgba(244, 63, 94, 0.6)',
                        'rgba(16, 185, 129, 0.6)'
                    ],
                    borderColor: [
                        'rgba(99, 102, 241, 1)',
                        'rgba(244, 63, 94, 1)',
                        'rgba(16, 185, 129, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#e2e8f0', font: {family: 'Inter', size: 13} }
                    }
                }
            }
        });

        // 4. Reveal con Animación
        resultsArea.classList.remove('hidden');
        resultsArea.style.animation = 'fadeInUp 0.8s ease forwards';
        scrollPrompt.classList.remove('hidden');
        
        setTimeout(() => {
            resultsArea.scrollIntoView({ behavior: 'smooth' });
        }, 300);

    } catch (err) {
        console.error(err);
        alert("Atención: Asegúrate de levantar el backend FastAPI (`uvicorn main:app --reload`) en el puerto 8000 para que este frontend pueda conectarse y calcular el informe real.");
    } finally {
        btn.innerHTML = 'Generar Informe Gratis';
        btn.disabled = false;
    }
});

// =============== PASARELA DE PAGOS (MERCADO PAGO) ===============
const LINKS_PAGO = {
    'basico_1': 'https://mpago.li/1cYJgVj',
    'basico_5': 'https://mpago.li/12hQLp6',
    'profesional_1': 'https://mpago.li/2giyBpz',
    'profesional_5': 'https://mpago.li/13meztP',
    'cabida_1': 'https://mpago.li/198tj5Q',
    'cabida_5': 'https://mpago.li/1744ZB6',
    'suscripcion_pro': 'https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id=0188ef3dbfbc4cc0819f33403c84175e',
    'suscripcion_premium': 'https://www.mercadopago.cl/subscriptions/checkout?preapproval_plan_id=51c4802fce3e4b6c8beb3f031a5e680d'
};

window.abrirMercadoPago = function(tipoInforme) {
    const link = LINKS_PAGO[tipoInforme];
    if (!link) {
        alert("Enlace de pago en construcción.");
        return;
    }

    const loader = document.createElement('div');
    loader.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;font-family:Outfit;font-size:2rem;backdrop-filter:blur(10px);">Generando Ticket Seguro ...<span style="font-size:1rem; margin-top:20px; color:#cbd5e1;">Serás redirigido a Mercado Pago</span></div>';
    document.body.appendChild(loader);

    setTimeout(() => {
        window.location.href = link;
    }, 1200);
};
