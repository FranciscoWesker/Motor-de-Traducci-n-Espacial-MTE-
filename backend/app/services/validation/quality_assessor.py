from typing import Dict, Any
from app.models.spatial_analysis import ConfiabilidadEnum

class QualityAssessor:
    """Evalúa la calidad general y asigna nivel de confiabilidad"""
    
    def assess(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa la calidad y determina el nivel de confiabilidad"""
        confidence_score = 0.0
        reasons = []
        
        # Factor 1: CRS detectado con confianza
        crs_confidence = analysis_results.get('crs_confidence', 0.0)
        if crs_confidence >= 0.8:
            confidence_score += 0.4
            reasons.append("CRS detectado con alta confianza")
        elif crs_confidence >= 0.6:
            confidence_score += 0.25
            reasons.append("CRS detectado con confianza media")
        else:
            reasons.append("CRS detectado con baja confianza o no detectado")
        
        # Factor 2: Validación geométrica
        validation_results = analysis_results.get('validation', {})
        if validation_results.get('is_valid', False) and len(validation_results.get('errors', [])) == 0:
            confidence_score += 0.3
            reasons.append("Geometrías válidas")
        else:
            error_count = len(validation_results.get('errors', []))
            if error_count > 0:
                confidence_score -= 0.2 * min(error_count / 10, 1.0)
                reasons.append(f"Se encontraron {error_count} errores geométricos")
        
        # Factor 3: Outliers
        outliers = validation_results.get('outliers', [])
        if len(outliers) == 0:
            confidence_score += 0.2
            reasons.append("No se detectaron outliers")
        else:
            outlier_penalty = min(len(outliers) / 20, 0.2)
            confidence_score -= outlier_penalty
            reasons.append(f"Se detectaron {len(outliers)} outliers")
        
        # Factor 4: Unidades detectadas
        if analysis_results.get('unidades_detectadas') and analysis_results.get('unidades_detectadas') != 'desconocidas':
            confidence_score += 0.1
            reasons.append("Unidades detectadas correctamente")
        
        # Normalizar score
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Determinar nivel de confiabilidad
        if confidence_score >= 0.7:
            confiabilidad = ConfiabilidadEnum.VERDE
            nivel = "verde"
        elif confidence_score >= 0.4:
            confiabilidad = ConfiabilidadEnum.AMARILLO
            nivel = "amarillo"
        else:
            confiabilidad = ConfiabilidadEnum.ROJO
            nivel = "rojo"
        
        # Generar recomendaciones
        recomendaciones = self._generate_recommendations(confidence_score, analysis_results)
        
        return {
            'confiabilidad': nivel,
            'confidence_score': confidence_score,
            'reasons': reasons,
            'recomendaciones': recomendaciones,
            'explicacion_tecnica': self._generate_technical_explanation(analysis_results, nivel)
        }
    
    def _generate_recommendations(self, score: float, results: Dict[str, Any]) -> list:
        """Genera recomendaciones basadas en los resultados"""
        recomendaciones = []
        
        if score < 0.4:
            recomendaciones.append("Se recomienda revisar manualmente el CRS y las coordenadas")
            recomendaciones.append("Verificar la fuente de los datos y sus metadatos originales")
        
        if results.get('validation', {}).get('errors'):
            recomendaciones.append("Corregir las geometrías inválidas antes de usar los datos")
        
        if len(results.get('validation', {}).get('outliers', [])) > 0:
            recomendaciones.append("Revisar y validar los outliers detectados")
        
        if results.get('crs_detectado') and '4686' in str(results.get('crs_detectado')):
            recomendaciones.append("Los datos están en MAGNA-SIRGAS, adecuado para uso en Colombia")
        
        if score >= 0.7:
            recomendaciones.append("Los datos son confiables para uso en análisis espaciales")
        
        return recomendaciones
    
    def _generate_technical_explanation(self, results: Dict[str, Any], nivel: str) -> str:
        """Genera explicación técnica comprensible"""
        crs = results.get('crs_detectado', 'No detectado')
        origen = results.get('origen_detectado', 'No determinado')
        unidades = results.get('unidades_detectadas', 'No detectadas')
        
        explanation = f"""
        Análisis de Datos Espaciales:
        
        Sistema de Referencia (CRS): {crs}
        Origen: {origen}
        Unidades: {unidades}
        
        Nivel de Confiabilidad: {nivel.upper()}
        
        """
        
        if nivel == "verde":
            explanation += "Los datos son confiables y están listos para uso en análisis espaciales."
        elif nivel == "amarillo":
            explanation += "Los datos tienen algunas advertencias. Se recomienda revisar antes de usar en análisis críticos."
        else:
            explanation += "Los datos requieren intervención manual. Se recomienda verificar el CRS y la calidad geométrica."
        
        return explanation.strip()
