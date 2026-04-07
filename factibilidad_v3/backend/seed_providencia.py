import requests
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def sembrar_providencia():
    db = SessionLocal()
    
    print("[Seed] Iniciando inyección de datos reales para Providencia...")
    
    # Asegurarnos de que no lo hemos creado antes (evitar duplicados si corremos varias veces)
    doc_existente = db.query(models.DocumentoNormativo).filter_by(numero_documento="Res. Ex. N° 68").first()
    
    if not doc_existente:
        # 1. Crear el Documento Normativo Padre (El texto legal extraído)
        doc_providencia = models.DocumentoNormativo(
            jerarquia="COMUNAL",
            comuna="Providencia",
            tipo_documento="Resolución Aprobatoria PRC",
            entidad_emisora="COREMA RM / MINVU / DOM Providencia",
            numero_documento="Res. Ex. N° 68",
            fecha_promulgacion="2007-01-23", 
            url_fuente="https://www.providencia.cl/provi/site/artic/20200827/asocfile/20200827171427/memoria_explicativa_prc_2007__texto_.pdf",
            texto_vigente_pdf_crudo="TEXTO MOCK PARA BÚSQUEDA FUTURA...",
            es_vigente=True
        )
        db.add(doc_providencia)
        db.commit()
        db.refresh(doc_providencia)
        print(f"[Seed] Documento Normativo creado: ID {doc_providencia.id}")
    else:
        doc_providencia = doc_existente
        print(f"[Seed] Usando Documento Normativo existente: ID {doc_providencia.id}")

    # 2. Crear las Fichas de Polígonos de la zona (Ej: UP-R Edificación Continua)
    zona_existente = db.query(models.FichaPoliZona).filter_by(comuna="Providencia", nombre_zona="Up-R").first()
    
    if not zona_existente:
        ficha = models.FichaPoliZona(
            documento_id=doc_providencia.id,
            comuna="Providencia",
            nombre_zona="Up-R",
            fuente_minvu_geoide=True, # Simulamos cruce verificado 100%
            
            # Parametros rigorosos solicitados:
            altura_maxima="21 metros (7 pisos)", 
            constructibilidad="2.5", # Se admitirá float al convertirlo en logica_radar
            porcentaje_edificacion="100% Volumen Teórico",
            ocupacion_suelo="40", # 40%
            
            agrupamiento_sistema="Aislado, Pareado",
            antejardin="5 metros o según línea de edificación predominante",
            uso_suelo="Residencial, Equipamiento Básico",
            restricciones="Restricción de Cono de Aproximación Aeródromo (PRMS Art 8.2), Conservación Histórica en perímetros definidos."
        )
        db.add(ficha)
        db.commit()
        print("[Seed] Zona 'Up-R' de Providencia inyectada correctamente.")
    else:
        print("[Seed] Zona 'Up-R' ya existía en la base de datos.")

    db.close()
    print("[Seed] Ingesta finalizada. \n")

if __name__ == "__main__":
    # Primero forzamos la creación de tablas si no están hechas en supabase
    models.Base.metadata.create_all(bind=engine)
    sembrar_providencia()
