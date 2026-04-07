import os
from database import engine, Base
import models # Esto importa todos los modelos para que Base.metadata los reconozca

print("Inicializando Base de Datos en Supabase...")

try:
    # Cria todas las tablas en la base de datos remota
    Base.metadata.create_all(bind=engine)
    print("¡Éxito! Todas las tablas de Instrumentos de Planificación Territorial (IPT) y Factibilidad han sido creadas en Supabase.")
except Exception as e:
    print(f"Error al conectar o crear tablas: {e}")
