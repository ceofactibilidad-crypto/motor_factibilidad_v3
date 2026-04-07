import httpx
from bs4 import BeautifulSoup
import asyncio

"""
MOTOR DE INGESTA VERDADERA - BCN (Biblioteca del Congreso Nacional - Ley Chile)
=================================================================================
Este módulo extrae textos técnicos, normativas legales, planes reguladores y 
modificaciones directamente desde www.bcn.cl (Ley Chile), garantizando que los
datos mostrados en factibilidad.cl sean públicos, formales y no inventados.

Comunas Prioritarias Actuales: Ñuñoa, Vitacura, Providencia.
"""

UR_BCN_SEARCH = "https://www.bcn.cl/leychile/consulta/codificacion/busqueda"
URL_BCN_BASE = "https://www.bcn.cl"

COMUNAS_PRIORITARIAS = ["Ñuñoa", "Vitacura", "Providencia"]

async def buscar_plan_regulador_bcn(comuna: str):
    """
    Realiza una búsqueda HTTP en el portal web de la Biblioteca del Congreso Nacional
    para encontrar la Resolución o Decreto que aprueba el Plan Regulador Comunal.
    Retorna el ID de la Norma y su enlace a las versiones y modificaciones.
    """
    if comuna not in COMUNAS_PRIORITARIAS:
        return {"error": f"Comuna {comuna} fuera del alcance de la Fase 1", "fuente": "Ley Chile - BCN"}

    query = f"Plan Regulador Comunal de {comuna}"
    # Aquí iría el payload real o querystring que bcn.cl usa en su buscador avanzado
    params = {
        "palabras_claves": query,
        # Filtros adicionales si fuera necesario (ej: tipo_norma=Resolucion)
    }
    
    # Este es el esqueleto que conectará a la web en vivo y parseará con BS4
    print(f"[BCN Ley Chile] Buscando normativas para: {query}")
    
    # r = await httpx.AsyncClient().get("https://www.bcn.cl/leychile/consulta/resultados", params=params)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # extraer idNorma...
    
    # Para efectos del MVP sin levantar protecciones, retornamos el esqueleto de 
    # cómo se estructurará la data histórica (Versiones y Modificaciones).
    return {
        "comuna": comuna,
        "documento_titular": f"Plan Regulador Comunal de {comuna}",
        "fuente": "Ley Chile - BCN (Biblioteca del Congreso Nacional)",
        "id_norma_bcn": "PENDIENTE_DE_EXTRACCION",
        "url_ley_chile": f"https://www.bcn.cl/leychile/buscar?q={comuna}",
        "estado_vigencia": "VIGENTE",
        "versiones_disponibles": [
            {"fecha": "PENDIENTE", "modificacion": "Texto original"},
            {"fecha": "PENDIENTE", "modificacion": "Modificación Nº 1"}
        ],
        "texto_crudo": "Sin Información - Listo para ser procesado y leído en crudo",
        "indicaciones": "Extracción en Construcción - Se requiere procesar XML/PDF de Ley Chile"
    }

async def extraer_texto_ley(id_norma: str, version: str = "actual"):
    """
    Dado el idNorma de BCN, descarga el texto completo (HTML o XML) de la Ley/Decreto 
    para poder alimentar directamente el bloque del panel de administración o IA,
    sin inventar o diluir la fuente formal.
    """
    pass

if __name__ == "__main__":
    import asyncio
    res = asyncio.run(buscar_plan_regulador_bcn("Ñuñoa"))
    print(res)
