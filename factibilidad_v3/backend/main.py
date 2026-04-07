from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine

# Crear las tablas en la base de datos (Ejecución de migración básica)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Motor Factibilidad.cl API")

# Habilitar CORS para que el frontend React/Vanilla en otro puerto pueda consultar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En pro, cambiar a la URL real del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import analisis
from fastapi.staticfiles import StaticFiles

app.include_router(analisis.router)

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

@app.get("/")
def read_root():
    return {"status": "Radar y Reportes API operativa", "version": "1.0"}
