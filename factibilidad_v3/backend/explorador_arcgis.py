import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://geoide.minvu.cl/server/rest/services/IPT/PRC_Metropolitana/FeatureServer/2?f=pjson"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        print("Nombre de la Capa:", data.get("name"))
        print("Campos Disponibles:")
        for f in data.get("fields", []):
            print(f"  - {f['name']} ({f['alias']}): {f['type']}")
except Exception as e:
    print(f"Error conectando a MINVU ArcGIS: {e}")
