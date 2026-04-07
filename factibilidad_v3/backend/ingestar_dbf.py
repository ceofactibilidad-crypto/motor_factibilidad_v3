import os
import glob
from dbfread import DBF
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

def run_ingestion():
    # Asegurar que las tablas existen
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    base_dir = r"C:\Users\Rocha\.gemini\antigravity\scratch\proptech_mvp\IPT_Metropolitana"
    dbf_files = glob.glob(os.path.join(base_dir, "**", "*.dbf"), recursive=True)
    
    zonas_vistas = set()
    registros_insertados = 0
    
    print(f"Buscando en {len(dbf_files)} archivos .dbf...")
    
    for dbf_path in dbf_files:
        try:
            table = DBF(dbf_path, encoding='latin-1', load=True)
            for record in table:
                com = record.get("COM", "Desconocida")
                zona = record.get("ZONA", "Sin Zona")
                
                # Usar campos legales si existen
                n_doc = record.get("N_DOC", "")
                t_do = record.get("T_DO", "Decreto")
                p_do = record.get("P_DO", "Sin Fecha")
                
                # La clave \u00fanica es la combinaci\u00f3n de comuna y zona para no repetir reglas
                clave_unica = f"{com}-{zona}"
                
                if clave_unica not in zonas_vistas and zona != "Sin Zona":
                    zonas_vistas.add(clave_unica)
                    
                    # Truncate strings that might be excessively long for standard limits if necessary
                    uproh = str(record.get("UPROH", ""))[:500]
                    uperm = str(record.get("UPERM", ""))[:500]
                    
                    nueva_norma = models.NormativaPRC(
                        comuna=com,
                        zona=zona,
                        fuente_datos=f"EGIS .dbf - {t_do} {n_doc}",
                        fuente_fecha=p_do,
                        # Valores nulos por ahora, a rellenar con scraping de portalipt.minvu.cl
                        altura_maxima=None,
                        constructibilidad=None,
                        ocupacion_suelo=None,
                        antejardin=None,
                        restricciones=uproh,
                        beneficios=uperm
                    )
                    db.add(nueva_norma)
                    registros_insertados += 1
        except Exception as e:
            # print(f"Error o formato no estandar en {dbf_path}")
            pass
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error al commitear a la base de datos: {e}")
    finally:
        db.close()
        
    print(f"Ingesti\u00f3n completada: {registros_insertados} zonas \u00fanicas guardadas en proptech.db (SQLite).")

if __name__ == "__main__":
    run_ingestion()
