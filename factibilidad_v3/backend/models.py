from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class DocumentoNormativo(Base):
    """
    Tabla Central de Trazabilidad: Almacena la ley, resolución o decreto que origina el dato.
    Ej: "PRC Ñuñoa", "PRMS Metropolitana", "OGUC Nacional", "Memoria Explicativa DOM Vitacura".
    """
    __tablename__ = "documento_normativo"

    id = Column(Integer, primary_key=True, index=True)
    jerarquia = Column(String, index=True) # "NACIONAL" (OGUC/LGUC), "METROPOLITANO" (PRMS), "COMUNAL" (PRC)
    comuna = Column(String, index=True) # "Ñuñoa", "Metropolitana", "Nacional"
    tipo_documento = Column(String) # Ej: "Ley", "Ordenanza General", "Decreto", "Resolución"
    entidad_emisora = Column(String) # Ej: "MINVU", "BCN Ley Chile", "DOM Providencia"
    
    numero_documento = Column(String) # "N° 145", "Ley 21.450"
    fecha_promulgacion = Column(String) # Idealmente formato YYYY-MM-DD
    
    url_fuente = Column(String) # URL hacia IDE Minvu o BCN Ley Chile
    texto_vigente_pdf_crudo = Column(Text) # Almacenaje masivo del XML/PDF extraído para búsquedas
    es_vigente = Column(Boolean, default=True)

    # Relaciones
    zonas = relationship("FichaPoliZona", back_populates="documento")
    articulos = relationship("ArticuloReglamentario", back_populates="documento")


class ArticuloReglamentario(Base):
    """
    Almacena artículos literales y exactos de leyes superiores (como OGUC o LGUC).
    Se usa para citar la ley directamente sin promediarla ni parafrasearla.
    """
    __tablename__ = "articulo_reglamentario"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documento_normativo.id"))
    
    numero_articulo = Column(String, index=True) # Ej: "Art. 2.1.20"
    titulo = Column(String)
    cuerpo_legal = Column(Text) # El texto literal de la ley extraído del BCN
    palabras_clave = Column(String) # Ej: "Antejardín, Cierre perimetral"

    documento = relationship("DocumentoNormativo", back_populates="articulos")


class FichaPoliZona(Base):
    """
    Ficha de Polígono. Almacena rigurosamente los listados normativos exigidos para el cálculo volumétrico.
    """
    __tablename__ = "ficha_poli_zona"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documento_normativo.id"))
    
    comuna = Column(String, index=True)
    nombre_zona = Column(String, index=True) # Ej: "Z-4", "Upr-1", "Área Verde PRMS"
    
    # Verificación estricta cruzada
    fuente_minvu_geoide = Column(Boolean, default=False) # ¿Coincide 100% gráfica de ide.minvu.cl con BCN?
    
    # Listado Exigido de Parámetros Normados Oficiales
    altura_maxima = Column(String)          # Ej: "21 metros (7 pisos)"
    constructibilidad = Column(String)      # Ej: "2.5" o "1.2". String para soportar "Libre" o cuotas.
    porcentaje_edificacion = Column(String) # Coeficiente o porcentaje total
    ocupacion_suelo = Column(String)        # Permiso en primer piso (Ej: "40%")
    
    agrupamiento_sistema = Column(String)   # "Aislado", "Pareado", "Continuo"
    antejardin = Column(String)             # Ej: "5 metros" o "Según plano de loteo"
    uso_suelo = Column(String)              # "Residencial Mixto", "Equipamiento"
    restricciones = Column(Text)            # Franjas de utilidad, protección, áreas de riesgo.
    
    # Relación
    documento = relationship("DocumentoNormativo", back_populates="zonas")


# =====================================================================
# Modulos Heredados Compatibles con Analisis Actual
# =====================================================================

class PropiedadSII(Base):
    """
    Tabla de datos del Servicio de Impuestos Internos (SII).
    En producción se alimenta vía Playwright asincrónico evaluando rolt/comuna.
    """
    __tablename__ = "propiedad_sii"

    id = Column(Integer, primary_key=True, index=True)
    rol = Column(String, index=True)
    direccion = Column(String, index=True)
    comuna = Column(String, index=True)

    terreno_m2 = Column(Float)
    construccion_m2 = Column(Float)
    anio_construccion = Column(Integer)
    
    uso_suelo_sii = Column(String)
    destino_sii = Column(String)
    tipo_propiedad = Column(String)

    avaluo_fiscal_clp = Column(Float)
    avaluo_terreno_clp = Column(Float)
    avaluo_const_clp = Column(Float)

    zona_homogenea = Column(String)
    serie = Column(String)


class PropiedadMercado(Base):
    __tablename__ = "propiedad_mercado"

    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String, index=True)
    comuna = Column(String, index=True)

    terreno_m2 = Column(Float)
    construido_m2 = Column(Float)
    precio_clp = Column(Float)
    precio_m2_clp = Column(Float)
    tipo_propiedad = Column(String)

    url_origen = Column(String)

class RestriccionEspecial(Base):
    """
    Módulo E: Almacena restricciones de LUP, DUP, Patrimoniales, Riesgos y Servidumbres.
    """
    __tablename__ = "restriccion_especial"

    id = Column(Integer, primary_key=True, index=True)
    comuna = Column(String, index=True)
    categoria = Column(String) # Ej: "Riesgo Natural", "Protección Patrimonial", "Afectación Vial"
    tipo_restriccion = Column(String) # "Remoción en masa", "Zona Típica", "Línea Oficial de Edificación"
    
    fuente = Column(String) # "SERNAGEOMIN", "CMN", "PRC Comunal"
    afectacion_fpi_factor = Column(Float) # Penalización al FPI, ej: 0.4 (Reducción al 40%)
    
    descripcion_impacto = Column(Text) # "Reducción severa. El riesgo puede hacer inviable el proyecto."
    poligono_geom = Column(Text) # WKT o ref string si no hay postgis directo aquí, o se usaría Geometry.
