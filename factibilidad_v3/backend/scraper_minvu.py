import random
import time
from sqlalchemy.orm import Session
import models

def procesar_texto_con_ia(texto_pdf: str):
    """
    Aqu\u00ed ir\u00e1 la l\u00f3gica real de extracci\u00f3n con LLMs/OpenAI en el futuro.
    Por ahora simulamos un % de acierto y fallo basado en la calidad del PDF.
    """
    if random.random() > 0.8: # 20% de probabilidad de fallo por PDF viejo
        raise ValueError("PDF ininteligible (M\u00e1quina de Escribir Antig\u00fca)")
    
    # Valores aleatorios l\u00f3gicos simulando la IA
    return {
        "altura_maxima": f"{random.choice([7, 9, 12, 18, 24])}m",
        "constructibilidad": round(random.uniform(0.8, 3.5), 2),
        "ocupacion_suelo": round(random.uniform(0.3, 0.8), 2),
        "antejardin": f"{random.choice([2, 3, 5])}m"
    }

def sincronizar_ordenanzas_minvu(db: Session):
    """
    Simula la conexi\u00f3n a portalipt.minvu.cl, descarga de PDFs de las ordenanzas 
    y parseo autom\u00e1tico usando la funci\u00f3n de IA.
    """
    # Buscar solo zonas maestras que a\u00fan no tienen datos normativos
    zonas_pendientes = db.query(models.NormativaPRC).filter(
        models.NormativaPRC.constructibilidad == None,
        models.NormativaPRC.comuna.in_(["Providencia", "Nunoa", "Colina"]) # Filtramos solo unas pocas para la demo
    ).limit(10).all()
    
    actualizadas = 0
    errores = 0
    lista_errores = []

    for zona in zonas_pendientes:
        # 1. Simular descarga del PDF de minvu.cl
        time.sleep(0.5) 
        try:
            # 2. Intentar parsear con IA
            datos_matematicos = procesar_texto_con_ia("CONTENIDO DEL PDF...")
            
            # 3. Guardar \u00e9xito
            zona.altura_maxima = datos_matematicos["altura_maxima"]
            zona.constructibilidad = datos_matematicos["constructibilidad"]
            zona.ocupacion_suelo = datos_matematicos["ocupacion_suelo"]
            zona.antejardin = datos_matematicos["antejardin"]
            
            # Opcionalmente, agregar una etiqueta de que fue procesado por IA
            zona.beneficios = f"{zona.beneficios} | [Extra\u00eddo por IA]" 
            actualizadas += 1
            
        except ValueError as e:
            # Documento ilegible: Marcar para revisi\u00f3n manual
            errores += 1
            zona.restricciones = f"[ETIQUETA: REVISION MANUAL] Error: {e}"
            lista_errores.append(f"{zona.comuna} - {zona.zona}")
            
    db.commit()
    return {"status": "ok", "actualizadas": actualizadas, "errores": errores, "detalle_errores": lista_errores}
