// --- ACCESO DIRECTO (Login desactivado temporalmente) ---
function initAuth() {
    document.getElementById('login-overlay').style.display = 'none';
    document.getElementById('admin-app').style.display = 'flex';
    cargarEstadisticas();
}

async function checkLogin() {
    const user = document.getElementById('admin-user').value;
    const pass = document.getElementById('admin-pass').value;
    
    // Conectar al backend usando JSON puro para evitar conflictos Multipart en Windows
    try {
        const res = await fetch('/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        if(res.ok) {
            const data = await res.json();
            sessionStorage.setItem('adminAuth', data.access_token);
            initAuth();
        } else {
            throw new Error("Invalid");
        }
    } catch (e) {
        document.getElementById('login-error').style.display = 'block';
        setTimeout(() => document.getElementById('login-error').style.display = 'none', 3000);
    }
}

// --- LÓGICA DE PESTAÑAS ---
function cambiarPestana(tabId) {
    document.querySelectorAll('.tab-section').forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden');
    });
    document.querySelectorAll('#admin-nav a').forEach(a => a.classList.remove('active'));

    const targetSection = document.getElementById(`tab-${tabId}`);
    if (targetSection) {
        targetSection.classList.remove('hidden');
        targetSection.classList.add('active');
    }

    const targetNav = document.getElementById(`nav-${tabId}`);
    if (targetNav) targetNav.classList.add('active');

    const headerTitle = document.getElementById('header-title');
    const headerBtn = document.getElementById('btn-header-sync');
    
    if (tabId === 'dashboard') {
        headerTitle.textContent = "Centro de Control Maestro";
        headerBtn.style.display = "none";
    } else if (tabId === 'motor') {
        headerTitle.textContent = "Motor de Sincronización MINVU";
        headerBtn.style.display = "block";
    } else if (tabId === 'manuales') {
        headerTitle.textContent = "Revisión Manual de Zonas";
        headerBtn.style.display = "none";
    } else if (tabId === 'ventas') {
        headerTitle.textContent = "Métricas de Ventas";
        headerBtn.style.display = "none";
    }
}

// --- LÓGICA DE DATOS ---
async function cargarEstadisticas() {
    try {
        const token = sessionStorage.getItem('adminAuth');
        const res = await fetch('/api/admin/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if(document.getElementById('stat-informes')) document.getElementById('stat-informes').textContent = data.informes_vendidos;
            if(document.getElementById('stat-activas')) document.getElementById('stat-activas').textContent = data.zonas_activas.toLocaleString('es-CL');
            if(document.getElementById('stat-errores')) document.getElementById('stat-errores').textContent = data.errores_manuales;
        }
    } catch (e) {
        console.error("No se pudo cargar estadisticas", e);
    }
}

async function sincronizar() {
    const originalText = `<span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1.2rem;">cloud_sync</span> Ejecutar Scraper MINVU`;
    const btns = document.querySelectorAll('button[onclick="sincronizar()"]'); 
    
    btns.forEach(btn => {
        btn.innerHTML = `<span class="material-symbols-outlined" style="animation: spin 1s linear infinite; vertical-align: middle; font-size: 1.2rem;">sync</span> Procesando...`;
        btn.style.opacity = '0.7';
        btn.style.pointerEvents = 'none';
    });

    const logs = document.getElementById('scraper-logs');
    if(logs) {
        logs.innerHTML += `> [${new Date().toLocaleTimeString()}] Conectando con servidor AI (8080)...<br>`;
        logs.scrollTop = logs.scrollHeight;
    }
    
    try {
        const token = sessionStorage.getItem('adminAuth');
        const res = await fetch('/api/admin/sync-minvu', { 
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if(logs) logs.innerHTML += `> [${new Date().toLocaleTimeString()}] Zonas Actualizadas: ${data.actualizadas}. Tareas manuales creadas: ${data.errores}.<br>`;
            cargarEstadisticas();
            
            if (data.detalle_errores.length > 0) {
                const tbody = document.getElementById('tabla-errores');
                if(tbody) tbody.innerHTML = ''; 
                data.detalle_errores.forEach(err => {
                    const [comuna, zona] = err.split(' - ');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${comuna}</strong></td>
                        <td>${zona}</td>
                        <td><span class="badge warning">PDF Ilegible Escaneado</span></td>
                        <td><button class="btn-small">Ingresar Manual</button></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (e) {
        if(logs) logs.innerHTML += `<span style="color: #ef4444;">> [${new Date().toLocaleTimeString()}] Error de API.</span><br>`;
    } finally {
        btns.forEach(btn => {
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        });
    }
}

initAuth();

const style = document.createElement('style');
style.innerHTML = `
@keyframes spin { 100% { transform: rotate(360deg); } }
.hidden { display: none !important; margin-top: -9999px; opacity: 0; }
`;
document.head.appendChild(style);
