def calcular_oportunidad(terreno_m2: float | None, construido_m2: float | None, constructibilidad: float | None, ocupacion_suelo: float | None):
    # Si faltan datos vitales, no se puede calcular nada real.
    if terreno_m2 is None or constructibilidad is None:
        return {
            "potencial_edificable": None,
            "indice_subutilizacion": None,
            "factor_potencial": None,
            "tipo_oportunidad": "Sin Info",
            "analisis_ia": "Falta información (terreno o constructibilidad) para generar el análisis de inteligencia."
        }

    potencial_edificable = terreno_m2 * constructibilidad
    
    # Evitar division por cero
    if not construido_m2 or construido_m2 == 0:
        construido_m2 = 1.0
        
    oc_suelo = ocupacion_suelo if ocupacion_suelo is not None else 1.0

    indice_subutilizacion = potencial_edificable / construido_m2
    indice_ocupacion = construido_m2 / terreno_m2
    
    tipo_oportunidad = "C"
    factor = 5.0
    analisis = "Propiedad estándar sin mayor flexibilidad normativa."

    if indice_subutilizacion > 5:
        tipo_oportunidad = "A"
        factor = min(10.0, 5.0 + (indice_subutilizacion / 2))
        analisis = f"EXCELENTE OPORTUNIDAD: La propiedad actual ({construido_m2}m²) subutiliza enormemente el terreno. Se permite construir hasta {round(potencial_edificable,1)}m² según la normativa vigente. Ideal para desarrollo habitacional o mixto."
    elif indice_subutilizacion > 2:
        tipo_oportunidad = "B"
        factor = 7.0
        analisis = f"OPORTUNIDAD MODERADA: Existe un margen de densificación interesante, permitiendo construir hasta {round(potencial_edificable,1)}m². Apto para proyecto de mediana escala."
    elif indice_ocupacion < oc_suelo:
        tipo_oportunidad = "C"
        factor = 6.0
        analisis = f"ALTA FLEXIBILIDAD: El terreno no ha alcanzado su máxima ocupación de suelo permitida ({round(oc_suelo*100,1)}%), ideal para ampliaciones horizontales."

    return {
        "potencial_edificable": round(potencial_edificable, 2),
        "indice_subutilizacion": round(indice_subutilizacion, 2),
        "factor_potencial": round(factor, 1),
        "tipo_oportunidad": tipo_oportunidad,
        "analisis_ia": analisis
    }

