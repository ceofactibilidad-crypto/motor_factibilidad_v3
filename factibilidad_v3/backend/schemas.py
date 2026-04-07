from pydantic import BaseModel
from typing import Optional

class AnalisisRequest(BaseModel):
    region: str
    comuna: str
    calle: str
    numero: int
    tier: str = "GRATIS"  # GRATIS|BASICO|PROFESIONAL|PREMIUM|MEMBRESIA_PRO


# =====================================================
# GRATIS: Texto gancho, sin valores exactos
# =====================================================
class GratisResponse(BaseModel):
    tier: str = "GRATIS"
    # Identificación básica
    rol_sii: str
    comuna: str
    uso_suelo_general: str   # "Residencial", "Mixto", etc.
    mensaje_potencial: str   # Texto gancho "ALTO / MEDIO / BAJO"
    nivel_potencial: str     # "ALTO" / "MEDIO" / "BAJO"

    # Datos visibles parciales (sin valores exactos)
    zona_prc: str            # Ej: "UP-R"
    tipo_oportunidad: str    # A, B, C
    analisis_ia_breve: str   # 2-3 líneas de análisis IA básico
    fuente_normativa: str


# =====================================================
# BASICO: Técnico básico, sin cálculos financieros
# =====================================================
class BasicoResponse(BaseModel):
    tier: str = "BASICO"
    # Todo lo de GRATIS +
    rol_sii: str
    direccion: str
    comuna: str

    # Datos SII
    terreno_m2: float
    construccion_m2: float
    anio_construccion: Optional[int] = None

    # Normativa
    zona_prc: str
    uso_suelo: str
    altura_maxima: str        # Rango: "7 pisos (21m)"
    constructibilidad_rango: str  # "Entre 2.0 y 3.0"
    ocupacion_suelo: float
    antejardin: str
    beneficios: str
    restricciones: str

    tipo_oportunidad: str
    analisis_ia_breve: str
    fuente_normativa: str


# =====================================================
# PROFESIONAL: Técnico + análisis negocio
# =====================================================
class ProfesionalResponse(BaseModel):
    tier: str = "PROFESIONAL"
    # Todo lo de BASICO +
    rol_sii: str
    direccion: str
    comuna: str

    # SII
    terreno_m2: float
    construccion_m2: float
    anio_construccion: Optional[int] = None
    avaluo_fiscal_clp: Optional[float] = None
    destino_sii: Optional[str] = None

    # Normativa exacta
    zona_prc: str
    uso_suelo: str
    altura_maxima: str
    constructibilidad: float       # Valor exacto
    ocupacion_suelo: float
    antejardin: str
    beneficios: str
    restricciones: str

    # Cálculos
    potencial_edificable: float
    indice_subutilizacion: float
    indice_ocupacion: float

    # Económico
    precio_m2_mercado: float       # CLP/m²
    valor_proyecto_estimado: float # CLP

    tipo_oportunidad: str
    recomendacion: str             # "COMPRAR" / "EVALUAR" / "DESCARTAR"
    analisis_ia: str
    fuente_normativa: str


# =====================================================
# PREMIUM: Estudio inmobiliario completo
# =====================================================
class EscenarioFinanciero(BaseModel):
    nombre: str               # "Conservador" / "Medio" / "Agresivo"
    supuesto: str
    unidades: int
    valor_venta_clp: float
    costo_construccion_clp: float
    margen_estimado_pct: float

class PremiumResponse(BaseModel):
    tier: str = "PREMIUM"
    # Todo lo del PROFESIONAL +
    rol_sii: str
    direccion: str
    comuna: str

    terreno_m2: float
    construccion_m2: float
    anio_construccion: Optional[int] = None
    avaluo_fiscal_clp: Optional[float] = None
    destino_sii: Optional[str] = None

    zona_prc: str
    uso_suelo: str
    altura_maxima: str
    constructibilidad: float
    ocupacion_suelo: float
    antejardin: str
    beneficios: str
    restricciones: str

    potencial_edificable: float
    indice_subutilizacion: float
    indice_ocupacion: float
    precio_m2_mercado: float
    valor_proyecto_estimado: float

    # Escenarios financieros
    escenarios: list[EscenarioFinanciero]

    # Análisis de riesgo
    riesgo_normativo: str
    riesgo_mercado: str
    riesgo_entorno: str

    # Estrategia
    tipo_desarrollo_recomendado: str

    tipo_oportunidad: str
    recomendacion: str
    analisis_ia: str
    fuente_normativa: str


# =====================================================
# MEMBRESIA_PRO: JSON para mapa interactivo
# =====================================================
class MembresiaPROResponse(BaseModel):
    tier: str = "MEMBRESIA_PRO"
    direccion: str
    coordenadas: str           # "lat,lng"
    comuna: str
    terreno: float
    potencial: float
    indice_subutilizacion: float
    nivel_oportunidad: str     # "ALTO" / "MEDIO" / "BAJO"
    color_mapa: str            # "verde" / "amarillo" / "rojo"
    tipo_oportunidad: str      # A, B, C
    tooltip_resumen: str       # Texto corto para marker del mapa


# Alias genérico que devuelve el endpoint
class AnalisisResponse(BaseModel):
    tier: str
    direccion: str
    terreno_m2: float
    construido_m2: float
    zona: str
    altura_maxima: str
    constructibilidad: float
    ocupacion_suelo: float
    potencial_edificable: float
    indice_subutilizacion: float
    factor_potencial: float
    tipo_oportunidad: str
    analisis_ia: str
    fuente_normativa: str
    # Campos opcionales de tiers superiores
    rol_sii: Optional[str] = None
    avaluo_fiscal_clp: Optional[float] = None
    anio_construccion: Optional[int] = None
    destino_sii: Optional[str] = None
    precio_m2_mercado: Optional[float] = None
    valor_proyecto_estimado: Optional[float] = None
    recomendacion: Optional[str] = None
    riesgo_normativo: Optional[str] = None
    riesgo_mercado: Optional[str] = None
    riesgo_entorno: Optional[str] = None
    tipo_desarrollo_recomendado: Optional[str] = None
    escenarios: Optional[list] = None
    nivel_potencial: Optional[str] = None
    mensaje_potencial: Optional[str] = None
    color_mapa: Optional[str] = None
    coordenadas: Optional[str] = None
    tooltip_resumen: Optional[str] = None
