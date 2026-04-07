abreimport os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import models
from models import NormativaPRC

load_dotenv()

# Origen
sqlite_engine = create_engine("sqlite:///./proptech.db")
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_db = SqliteSession()

# Destino
postgres_url = os.getenv("DATABASE_URL")

print(f"Conectando a Cloud PostgreSQL...")
try:
    postgres_engine = create_engine(postgres_url)
    
    print("Creando tablas en la nube (Supabase)...")
    models.Base.metadata.create_all(bind=postgres_engine)
    
    PgSession = sessionmaker(bind=postgres_engine)
    pg_db = PgSession()
    
    print("Leyendo zonas normativas desde Disco Local (SQLite)...")
    zonas_locales = sqlite_db.query(NormativaPRC).all()
    print(f"Total encontrado: {len(zonas_locales)} zonas.")
    
    # Check if we already migrated
    enbd = pg_db.query(NormativaPRC).count()
    if enbd >= len(zonas_locales):
        print("La base de datos Cloud ya contiene las zonas. Omientiendo inyecci\u00f3n.")
    else:
        print("Inyectando masivamente zonas a Supabase (Puede tomar 15-30 seg)...")
        for zona in zonas_locales:
            nueva_zona = NormativaPRC(
                comuna=zona.comuna,
                zona=zona.zona,
                fuente_datos=zona.fuente_datos,
                fuente_fecha=zona.fuente_fecha,
                altura_maxima=zona.altura_maxima,
                constructibilidad=zona.constructibilidad,
                ocupacion_suelo=zona.ocupacion_suelo,
                antejardin=zona.antejardin,
                restricciones=zona.restricciones,
                beneficios=zona.beneficios
            )
            pg_db.add(nueva_zona)
        
        pg_db.commit()
        print("\u00a1Migraci\u00f3n de Zonas Normativas 100% Exitosa!")
    
    pg_db.close()
except Exception as e:
    print(f"Error Cr\u00edtico de Conexion o Escritura a Supabase: {e}")

sqlite_db.close()
