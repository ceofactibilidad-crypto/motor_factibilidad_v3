import httpx
from shapely.geometry import shape

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

async def get_osm_footprint(lat: float, lng: float, radio_m: int = 30) -> dict:
    """Extrae el footprint del edificio o predio más cercano desde OpenStreetMap usando overpass QL"""
    query = f"""
    [out:json][timeout:25];
    (
      way["building"](around:{radio_m},{lat},{lng});
      way["landuse"="residential"](around:{radio_m},{lat},{lng});
    );
    out body geom;
    """

    resultado = {
        'footprint_m2': None,
        'pisos': None,
        'metros_construidos_est': None,
        'tipo_edificio': None,
        'disponible': False,
        'attribution': '© OpenStreetMap contributors'
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(OVERPASS_URL, data={'data': query}, timeout=30.0)
            if resp.status_code != 200:
                print(f"[OSM Client] Error en Overpass: {resp.status_code}")
                return resultado
            
            data = resp.json()

        if not data.get('elements'):
            return resultado  # No hay datos en ese radio

        elemento = data['elements'][0]
        # Calcular superficie aproximada usando Shapely
        if 'geometry' in elemento and len(elemento['geometry']) >= 3:
            geom = shape({'type': 'Polygon', 'coordinates': [
                [[n['lon'], n['lat']] for n in elemento['geometry']]
            ]})
            # Factor de conversión aproximado a m2 usando grados a metros en latitud media
            metro_factor = 111320 * 111320 * abs(lat) / lat if lat != 0 else 1
            footprint = abs(geom.area * metro_factor)
        else:
            footprint = 0

        tags = elemento.get('tags', {})
        pisos = int(tags.get('building:levels', 1))

        resultado.update({
            'footprint_m2': round(footprint, 1),
            'pisos': pisos,
            'metros_construidos_est': round(footprint * pisos, 1),
            'tipo_edificio': tags.get('building', 'desconocido'),
            'disponible': True
        })

    except Exception as e:
        print(f"[OSM Client] Error de conexión: {e}")

    return resultado
