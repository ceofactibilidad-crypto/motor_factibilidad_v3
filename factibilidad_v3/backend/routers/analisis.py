from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import unicodedata
import schemas
import logica_radar
import models
from database import get_db
from modulo_e import CalculadorRestricciones
from services import geocode_address
from arcgis_client import get_zona_prc
from osm_client import get_osm_footprint

router = APIRouter()

PRECIO_M2_MERCADO = {
    "providencia":   85_000,
    "las condes":   100_000,
    "vitacura":     120_000,
    "santiago":      60_000,
    "nunoa":         70_000,
}

def _norm(text: str) -> str:
    if not text: return ""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_text.replace("ñ", "n").replace("ü", "u").strip()

def _tokens(text: str) -> list[str]:
    STOP = {"de", "del", "la", "el", "los", "las", "y", "e", "av", "calle"}
    return [t for t in _norm(text).split() if len(t) > 2 and t not in STOP]

def _precio_m2(comuna: str) -> float:
    return PRECIO_M2_MERCADO.get(_norm(comuna), 55_000)

def _buscar_normativa(db: Session, comuna: str):
    cn = _norm(comuna)
    tokens = _tokens(cn)
    if not tokens: return None
    anchor = tokens[0]
    return db.query(models.FichaPoliZona).filter(models.FichaPoliZona.comuna.ilike(f"%{anchor}%")).first()

def _buscar_sii(db: Session, comuna: str, calle: str):
    cn = _norm(comuna)
    cl = _norm(calle)
    return db.query(models.PropiedadSII).filter(
        models.PropiedadSII.direccion.ilike(f"%{cl}%"),
        models.PropiedadSII.comuna.ilike(f"%{cn}%")
    ).first()

def _buscar_restricciones(db: Session, comuna: str):
    # Mocking restrictions for now. In production, query the RestriccionEspecial table
    # using postgis location logic.
    return [{"tipo": "Afectación LUP (10-30%)", "categoria": "Afectación Vial"}]

@router.post("/api/analizar", response_model=schemas.AnalisisResponse)
async def analizar_propiedad(request: schemas.AnalisisRequest, db: Session = Depends(get_db)):
    tier = request.tier.upper()

    # 1. Geocodificación del punto (vital para ArcGIS y OSM)
    geo = await geocode_address(f"{request.calle} {request.numero}")
    lat_val, lon_val = geo["lat"], geo["lon"]

    # 2. Consultar fuente de verdad GIS: ArcGIS REST API
    zona_arcgis = await get_zona_prc(request.comuna, lat_val, lon_val)
    if "error" not in zona_arcgis:
        zona_codigo = zona_arcgis.get("id_zona") or zona_arcgis.get("nombre_zona", "Z-Default")
        altura_maxima = zona_arcgis.get("altura_max", "Según PRC")
        
        cc_raw = zona_arcgis.get("cc")
        constructibilidad = float(str(cc_raw).replace(",", ".")) if cc_raw else 1.2
        
        cos_raw = zona_arcgis.get("cos")
        ocupacion_suelo = float(str(cos_raw).replace(",", ".")) if cos_raw else 40.0
        
        fuente = zona_arcgis.get("instrumento", "ArcGIS PRC Comunal")
    else:
        # Fallback a BD Interna si ArcGIS falla
        zona_db = _buscar_normativa(db, request.comuna)
        if zona_db:
            zona_codigo = zona_db.nombre_zona
            altura_maxima = zona_db.altura_maxima
            constructibilidad = float(zona_db.constructibilidad.replace(",", ".")) if zona_db.constructibilidad else 1.2
            ocupacion_suelo = float(zona_db.ocupacion_suelo.replace(",", ".")) if zona_db.ocupacion_suelo else 40.0
            fuente = f"{zona_db.documento.tipo_documento} {zona_db.documento.numero_documento}" if zona_db.documento else "PRC Interno"
        else:
            zona_codigo = "Z-Default"; altura_maxima = "3 pisos"; constructibilidad = 1.2; ocupacion_suelo = 40.0; fuente = "Estimación"

    # 3. SII y Footprint OSM Live
    osm_data = await get_osm_footprint(lat_val, lon_val)
    osm_const = osm_data.get('metros_construidos_est', 0)
    
    sii_db = _buscar_sii(db, request.comuna, request.calle)
    if sii_db:
        rol = sii_db.rol; terreno_m2 = sii_db.terreno_m2; destino = sii_db.destino_sii; avaluo = sii_db.avaluo_fiscal_clp;
        construccion_m2 = sii_db.construccion_m2
    else:
        rol = "Consultar SII"; terreno_m2 = osm_data.get("footprint_m2", 400.0) * 3 if osm_data.get("disponible") else 400.0
        construccion_m2 = osm_const if osm_const and osm_const > 0 else 120.0
        avaluo = (terreno_m2 * float(_precio_m2(request.comuna)) * 0.4); destino = "Habitacional"

    # 4. Restricciones (Módulo E)
    restricciones = _buscar_restricciones(db, request.comuna)
    eval_restricciones = CalculadorRestricciones.evaluar_restricciones(restricciones)

    # 4. Radar y FPI (Penalizado)
    calculos = logica_radar.calcular_oportunidad(terreno_m2, construccion_m2, constructibilidad, ocupacion_suelo)
    
    factor_base = calculos["factor_potencial"] or 5.0
    factor_penalizado = CalculadorRestricciones.aplicar_fpi_penalizado(factor_base, eval_restricciones["factor_penalizacion_fpi"])
    semaforo = eval_restricciones["semaforo_restriccion"]

    alerta_restriccion = ""
    if eval_restricciones["alertas_detalladas"]:
        alerta_restriccion = " ATENCIÓN: " + " | ".join([f"[{r['categoria']}] {r['tipo']}" for r in eval_restricciones["alertas_detalladas"]])

    return schemas.AnalisisResponse(
        tier = tier,
        direccion = f"{request.calle} {request.numero}, {request.comuna}",
        terreno_m2 = terreno_m2,
        construido_m2 = construccion_m2,
        zona = zona_codigo,
        altura_maxima = altura_maxima,
        constructibilidad = constructibilidad,
        ocupacion_suelo = ocupacion_suelo,
        potencial_edificable = calculos["potencial_edificable"],
        indice_subutilizacion = calculos["indice_subutilizacion"],
        factor_potencial = factor_penalizado,
        tipo_oportunidad = calculos["tipo_oportunidad"],
        analisis_ia = calculos["analisis_ia"] + alerta_restriccion,
        fuente_normativa = fuente,
        rol_sii = rol,
        avaluo_fiscal_clp = avaluo,
        anio_construccion = 1990,
        destino_sii = destino,
        precio_m2_mercado = float(_precio_m2(request.comuna)),
        valor_proyecto_estimado = float((calculos["potencial_edificable"] or 0) * _precio_m2(request.comuna)),
        recomendacion = "EVALUAR" if semaforo != "🔴" else "RIESGO ALTO",
        nivel_potencial = "MEDIO",
        mensaje_potencial = "Potencial moderado de desarrollo." + alerta_restriccion,
        color_mapa = "amarillo" if semaforo != "🔴" else "rojo",
        coordenadas = f"{lat_val},{lon_val}",
        tooltip_resumen = "Propiedad Evaluada " + semaforo
    )
