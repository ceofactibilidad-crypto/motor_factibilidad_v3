"""
enricher.py - Módulo de enriquecimiento automático de datos prediales
Fuentes: 
  1. Nominatim OSM  → dirección → coordenadas (GRATIS, sin API key)
  2. Overpass API   → coordenadas → footprint edificio → m² construcción estimado
  3. SII Maps       → futuro scraper para ROL + avalúo + m² terreno real

Uso:
    from enricher import enricher_predio
    datos = enricher_predio("Irarrazaval 3456", "Ñuñoa")
    # → { lat, lon, footprint_m2, building_levels, terreno_est_m2, ... }
"""
import math
import time
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL  = "https://overpass-api.de/api/interpreter"

HEADERS = {"User-Agent": "factibilidad.cl/1.0 (contacto@factibilidad.cl)"}

# ─── 1. Geocoding ────────────────────────────────────────────────────────────

def geocodificar(direccion: str, comuna: str) -> dict | None:
    """
    Convierte dirección + comuna → {lat, lon, display_name}.
    Fuente: Nominatim (OpenStreetMap) — GRATIS, sin API key.
    Límite: 1 req/seg por política de uso.
    """
    query = f"{direccion}, {comuna}, Chile"
    try:
        r = requests.get(NOMINATIM_URL, params={
            "q": query, "format": "json", "limit": 1,
            "countrycodes": "cl", "addressdetails": 1
        }, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            g = results[0]
            return {
                "lat":          float(g["lat"]),
                "lon":          float(g["lon"]),
                "display_name": g.get("display_name", ""),
                "fuente":       "OpenStreetMap — Nominatim",
            }
    except Exception as e:
        print(f"[geocodificar] ERROR: {e}")
    return None

# ─── 2. Footprint → m² construcción ──────────────────────────────────────────

def _area_poligono(nodos: list[dict]) -> float:
    """
    Calcula el área en m² de un polígono usando la fórmula de Shoelace
    con coordenadas geográficas convertidas a metros.
    """
    if len(nodos) < 3:
        return 0.0
    # Factor de conversión aproximado para Chile (~33° lat):
    # 1° lat ≈ 111_000m  |  1° lon ≈ 91_000m (a lat -33°)
    LAT_M = 111_000
    LON_M = 91_000

    coords = [(n["lon"] * LON_M, n["lat"] * LAT_M) for n in nodos]
    n = len(coords)
    area = 0.0
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        area += (x1 * y2) - (x2 * y1)
    return abs(area) / 2.0

def obtener_footprint(lat: float, lon: float, radio_m: int = 40) -> dict:
    """
    Consulta Overpass API (OSM) para obtener edificios en un radio.
    Devuelve el edificio más cercano con su área de footprint y pisos.
    Fuente: OpenStreetMap — Overpass API (GRATIS, sin API key).
    """
    overpass_query = f"""
    [out:json][timeout:15];
    (
      way["building"](around:{radio_m},{lat},{lon});
      relation["building"](around:{radio_m},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    try:
        r = requests.post(OVERPASS_URL, data={"data": overpass_query},
                          headers=HEADERS, timeout=20)
        data = r.json()
        elements = data.get("elements", [])

        # Separar nodos y ways
        nodo_idx = {e["id"]: e for e in elements if e["type"] == "node"}
        ways = [e for e in elements if e["type"] == "way" and "tags" in e]

        if not ways:
            return {"footprint_m2": None, "pisos": None, "fuente": "OSM — sin edificio encontrado"}

        # Escoger el way con más tags (más completo)
        best = max(ways, key=lambda w: len(w.get("tags", {})))
        tags = best.get("tags", {})

        # Calcular área del polígono
        nodos = [nodo_idx[nid] for nid in best.get("nodes", []) if nid in nodo_idx]
        area = _area_poligono(nodos)

        pisos = None
        for campo in ("building:levels", "levels", "floors"):
            if campo in tags:
                try:
                    pisos = int(tags[campo])
                    break
                except:
                    pass

        return {
            "footprint_m2":    round(area, 1),
            "pisos_osm":       pisos,
            "construccion_est_m2": round(area * (pisos or 1), 1) if area else None,
            "building_type":   tags.get("building", "yes"),
            "osm_name":        tags.get("name", ""),
            "fuente":          "OpenStreetMap — Overpass API (Footprint Satelital)",
        }

    except Exception as e:
        print(f"[footprint] ERROR: {e}")
        return {"footprint_m2": None, "pisos": None, "fuente": "OSM — error de conexión"}

# ─── 3. Pipeline principal ────────────────────────────────────────────────────

def enricher_predio(direccion: str, comuna: str, numero: int | None = None) -> dict:
    """
    Pipeline completo: dirección → coordenadas → footprint → estimaciones.
    Retorna dict con todos los datos disponibles de fuentes gratuitas.
    """
    dir_completa = f"{direccion} {numero}".strip() if numero else direccion
    
    # Paso 1: Geocodificar
    geo = geocodificar(dir_completa, comuna)
    if not geo:
        return {"error": "No se pudo geocodificar la dirección", "fuente": "Nominatim"}

    time.sleep(1)  # Política de uso Nominatim: 1 req/seg

    # Paso 2: Footprint del edificio en OSM
    fp = obtener_footprint(geo["lat"], geo["lon"])

    return {
        "lat":               geo["lat"],
        "lon":               geo["lon"],
        "display_name":      geo["display_name"],
        "footprint_m2":      fp.get("footprint_m2"),
        "pisos_osm":         fp.get("pisos_osm"),
        "construccion_est_m2": fp.get("construccion_est_m2"),
        "building_type":     fp.get("building_type"),
        "fuente_geo":        geo["fuente"],
        "fuente_footprint":  fp["fuente"],
        "datos_estimados":   True,   # Siempre asterisco en dev mode
    }


# ─── Test directo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = enricher_predio("Irarrázaval", "Ñuñoa", 3456)
    print("=== GEOCODIFICACIÓN ===")
    print(f"  Lat/Lon: {data.get('lat')}, {data.get('lon')}")
    print(f"  Display: {data.get('display_name')}")
    print()
    print("=== FOOTPRINT OSM ===")
    print(f"  Footprint:    {data.get('footprint_m2')} m²")
    print(f"  Pisos OSM:    {data.get('pisos_osm')}")
    print(f"  Construcción: {data.get('construccion_est_m2')} m² (estimado)")
    print(f"  Tipo edif.:   {data.get('building_type')}")
    print(f"  Fuente:       {data.get('fuente_footprint')}")
    
    print()
    data2 = enricher_predio("Duble Almeyda", "Ñuñoa", 3028)
    print("=== Duble Almeyda 3028 ===")
    print(f"  Lat/Lon: {data2.get('lat')}, {data2.get('lon')}")
    print(f"  Footprint: {data2.get('footprint_m2')} m²  | Pisos: {data2.get('pisos_osm')}")
    print(f"  Construcción est.: {data2.get('construccion_est_m2')} m²")
