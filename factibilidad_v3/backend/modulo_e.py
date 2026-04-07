# Módulo E: Restricciones Especiales, Riesgos Naturales y Afectación FPI.
# Implementación según Documento de Proyecto v3.0

class CalculadorRestricciones:
    @staticmethod
    def evaluar_restricciones(restricciones_encontradas: list[dict]) -> dict:
        """
        Recibe una lista de diccionarios con restricciones encontradas para el predio.
        Ejemplo de restricción: 
        {'tipo': 'Zona de riesgo SERNAGEOMIN (Alto)', 'categoria': 'Riesgo Natural'}
        """
        penalizacion_total = 1.0
        alertas = []

        # Tabla de penalizaciones (Factor de Potencial Inmobiliario)
        # 1.0 = No afecta, 0.4 = Reduce a un 40%
        penalizador_fpi = {
            "Zona de riesgo SERNAGEOMIN (Alto)": 0.4,
            "Zona de riesgo SERNAGEOMIN (Medio)": 0.7,
            "Afectación LUP (>30%)": 0.5,
            "Afectación LUP (10-30%)": 0.75,
            "Monumento Nacional / Zona Típica": 0.6,
            "ZCH o ICH del PRC": 0.8,
            "Restricción aeronáutica de altura": 0.8,
            "Servidumbre eléctrica o de ductos": 0.85
        }

        severidad_maxima = "🟢" # Verde
        
        for r in restricciones_encontradas:
            tipo = r.get("tipo", "")
            factor = penalizador_fpi.get(tipo, 1.0)
            
            if factor < penalizacion_total:
                penalizacion_total = factor # Toma la restricción más castigadora

            # Determinar semáforo de gravedad
            if factor <= 0.6:
                severidad_maxima = "🔴" # Restricción Severa
            elif factor < 1.0 and severidad_maxima != "🔴":
                severidad_maxima = "🟡" # Restricción Moderada/Parcial
                
            alertas.append({
                "tipo": tipo,
                "categoria": r.get("categoria", "General"),
                "factor_aplicado": factor
            })

        return {
            "factor_penalizacion_fpi": penalizacion_total,
            "semaforo_restriccion": severidad_maxima,
            "alertas_detalladas": alertas
        }

    @staticmethod
    def aplicar_fpi_penalizado(fpi_base: float, factor_penalizacion: float) -> float:
        """Aplica la reducción de puntaje al FPI bruto resultante de la constructibilidad, etc."""
        return round(fpi_base * factor_penalizacion, 1)

