import httpx
import unicodedata

# Mapeo de prueba para comunas MVP apuntando al FeatureServer.
# Nota: "isidro.puigOCUC" u otro publicador debe poner la capa pública.
# Usualmente el URL base será algo como services.arcgis.com/{ID_ORG}/arcgis/rest/...
# Acá se provee un MOCK STRUCTURAL o URL PÚBLICO MINVU si corresponde.
PRC_LAYERS = {
    "providencia": "https://geoide.minvu.cl/server/rest/services/IPT/PRC_Metropolitana/FeatureServer/2", # Capas base MINVU temporal
    "las_condes": "https://geoide.minvu.cl/server/rest/services/IPT/PRC_Metropolitana/FeatureServer/2",
    "nunoa": "https://geoide.minvu.cl/server/rest/services/IPT/PRC_Metropolitana/FeatureServer/2"
}

def normalizar_nombre(comuna: str) -> str:
    nfkd = unicodedata.normalize("NFKD", comuna.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c)).replace("ñ", "n").replace(" ", "_").strip()

async def get_zona_prc(comuna: str, lat: float, lng: float) -> dict:
    """
    Hace una consulta espacial enviando la coordenada al FeatureServer de ArcGIS.
    Retorna directamente la zona oficial sin raspar el HTML.
    """
    comuna_key = normalizar_nombre(comuna)
    layer_url = PRC_LAYERS.get(comuna_key)
    
    if not layer_url:
        return {'error': f'PRC no disponible para comuna: {comuna}'}

    params = {
        'geometry': f'{lng},{lat}',
        'geometryType': 'esriGeometryPoint',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',  # Tráeme uso de suelo, ID de zona, alturas, constructibilidad...
        'returnGeometry': 'false',
        'f': 'json'
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{layer_url}/query', params=params, timeout=15)
            if resp.status_code != 200:
                return {'error': 'ArcGIS no respondió'}
            
            data = resp.json()

        if not data.get('features'):
            return {'error': 'Punto no encontrado en ninguna zona normativa del PRC'}

        attrs = data['features'][0]['attributes']

        return {
            'id_zona': attrs.get('ZONA', attrs.get('COD_ZONA', attrs.get('ID_ZONA', ''))),
            'nombre_zona': attrs.get('NOMBRE_ZONA', attrs.get('ZONA_NOMBRE', '')),
            'uso_suelo': attrs.get('USO', attrs.get('USO_SUELO', '')),
            'cc': attrs.get('CC', attrs.get('COEF_CONSTR', None)),
            'cos': attrs.get('COS', attrs.get('OC_SUELO', None)),
            'altura_max': attrs.get('ALT_MAX', attrs.get('ALTURA', None)),
            'instrumento': attrs.get('INSTRUMENTO', f'PRC_{comuna_key}')
        }

    except Exception as e:
        print(f"[ArcGIS Client] Error: {e}")
        return {'error': 'Excepción consultando ArcGIS'}
