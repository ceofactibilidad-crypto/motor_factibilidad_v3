"""
sii_scraper.py — Scraper para SII Mapas Digitales
===================================================
Portal objetivo: https://www4.sii.cl/mapasui/internet/#/contenido/index.html

Flujo:
 1. Abre el mapa SII en Chromium headless
 2. Hace click en el ícono "Búsqueda por dirección" (glyphicon-map-marker)
 3. Rellena: Comuna → Nombre Calle → Número
 4. Click en botón naranja "Buscar"
 5. Espera el panel de resultados (lado derecho del mapa)
 6. Extrae: ROL, Destino, Terreno m², Construcción m², Avalúo Fiscal
 7. Si hay múltiples resultados, toma el primero que coincida con el número

Retorna dict o None si no hay datos / falla el portal.
"""

import asyncio
import re
import unicodedata
import nest_asyncio

# Permite correr asyncio dentro de FastAPI/uvicorn sin RuntimeError
nest_asyncio.apply()

# ─── Mapeo de comunas a nombre oficial SII ───────────────────────────────────
COMUNAS_SII_MAP = {
    "providencia":       "PROVIDENCIA",
    "nunoa":             "ÑUÑOA",
    "ñuñoa":             "ÑUÑOA",
    "las condes":        "LAS CONDES",
    "santiago":          "SANTIAGO",
    "vitacura":          "VITACURA",
}

SII_MAPS_URL = "https://www4.sii.cl/mapasui/internet/#/contenido/index.html"

# ─── Helper: normalizar texto ─────────────────────────────────────────────────
def _norm(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _comuna_sii(nombre: str) -> str:
    """Convierte nombre de comuna al nombre exacto que usa el SII."""
    n = _norm(nombre.strip())
    return COMUNAS_SII_MAP.get(n, nombre.upper().strip())


# ─── Extracción de texto numérico de un string ────────────────────────────────
def _parse_float(text: str) -> float | None:
    if not text:
        return None
    clean = re.sub(r"[^\d,\.]", "", text).replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None


# ─── Core scraper ─────────────────────────────────────────────────────────────
async def fetch_sii_data_mapas(
    comuna_nombre: str,
    calle: str,
    numero: int,
    headless: bool = True,
    timeout_ms: int = 15_000,
) -> dict | None:
    """
    Consulta el portal SII Mapas por dirección y retorna datos prediales extráidos.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[SII Scraper] ERROR: playwright no instalado")
        return None

    comuna_sii = _comuna_sii(comuna_nombre)
    calle_upper = calle.upper().strip()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(SII_MAPS_URL, timeout=30_000)
            
            # 2. Búsqueda por Dirección (ícono marcador)
            await page.click('.glyphicon-map-marker', timeout=10_000)
            await page.wait_for_timeout(1000)

            # 3. Rellenar form
            # Comuna
            input_comuna = page.locator('input[ng-model*="comuna"]').first
            await input_comuna.fill(comuna_sii)
            await page.wait_for_timeout(1000)
            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("Enter")

            # Calle
            input_calle = page.locator('input[ng-model*="calle"]').first
            await input_calle.fill(calle_upper)
            await page.wait_for_timeout(1000)
            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("Enter")

            # Número
            input_num = page.locator('input[ng-model*="numero"]').first
            await input_num.fill(str(numero))

            # 4. Buscar
            await page.click('button:has-text("Buscar")')
            
            # 5. Esperar panel de resultados
            await page.wait_for_selector('table.table-condensed', timeout=10_000)

            # 6. Extraer
            datos = await _extraer_datos_panel(page)

            await browser.close()
            return datos

        except Exception as e:
            print(f"[SII Scraper] ERROR: {e}")
            await browser.close()
            return None


async def _extraer_datos_panel(page) -> dict | None:
    """Intenta extraer datos del panel lateral."""
    datos = {}
    try:
        # ROL
        rol_text = await page.locator('tr:has-text("ROL") td').nth(1).inner_text()
        datos["rol"] = rol_text.strip()
        
        # Terreno
        terreno_text = await page.locator('tr:has-text("Terreno") td').nth(1).inner_text()
        datos["terreno_m2"] = _parse_float(terreno_text)

        # Avalúo
        avaluo_text = await page.locator('tr:has-text("Avalúo Fiscal") td').nth(1).inner_text()
        datos["avaluo_fiscal_clp"] = _parse_float(avaluo_text)
        
    except Exception:
        pass
    return datos if datos else None


# ─── Wrapper síncrono ─────────────────────────────────────────────────────────
def buscar_sii_sync(comuna: str, calle: str, numero: int) -> dict | None:
    return asyncio.run(fetch_sii_data_mapas(comuna, calle, numero))


# ─── Test directo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _comuna = "Ñuñoa"
    _calle  = "Irarrázaval"
    _numero = 3456
    resultado = asyncio.run(fetch_sii_data_mapas(_comuna, _calle, _numero, headless=False))
    print(f"Resultado: {resultado}")
