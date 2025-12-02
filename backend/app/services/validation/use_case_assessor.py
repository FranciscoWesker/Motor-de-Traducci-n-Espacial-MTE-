"""
Evaluador de idoneidad de datos espaciales para diferentes casos de uso
"""
from typing import Dict, Any, Optional, List
from app.models.validation_result import ValidationResult


class UseCaseAssessor:
    """Evalúa si los datos son adecuados para diferentes casos de uso"""
    
    # Criterios por caso de uso
    USE_CASE_CRITERIA = {
        'catastro': {
            'error_planimetrico_max': 0.5,  # metros
            'error_altimetrico_max': 0.3,   # metros
            'escala_min': 1000,              # 1:1000 o mayor
            'crs_requerido': 'oficial',      # MAGNA-SIRGAS
            'geometrias_validas': True,
            'outliers_max': 0.01,            # 1% máximo
        },
        'topografia_obra': {
            'error_planimetrico_max': 2.0,   # metros
            'error_altimetrico_max': 1.0,    # metros
            'escala_min': 500,                # 1:500 o mayor
            'crs_requerido': 'cualquiera',   # Puede ser local
            'geometrias_validas': True,
            'outliers_max': 0.05,            # 5% máximo
        },
        'analisis_territorial': {
            'error_planimetrico_max': 10.0,  # metros
            'error_altimetrico_max': None,   # No crítico
            'escala_min': 10000,             # 1:10000 o mayor
            'crs_requerido': 'consistente',  # Debe ser consistente
            'geometrias_validas': True,
            'outliers_max': 0.10,            # 10% máximo
        },
        'modelado_ambiental': {
            'error_planimetrico_max': 50.0,  # metros
            'error_altimetrico_max': None,   # No crítico
            'escala_min': 25000,             # 1:25000 o mayor
            'crs_requerido': 'geografico',   # Geográfico o proyectado adecuado
            'geometrias_validas': False,     # Puede tolerar algunas inválidas
            'outliers_max': 0.20,            # 20% máximo
        }
    }
    
    def assess_use_cases(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa idoneidad para todos los casos de uso"""
        results = {
            'catastro': self._assess_catastro(analysis_data),
            'topografia_obra': self._assess_topografia_obra(analysis_data),
            'analisis_territorial': self._assess_analisis_territorial(analysis_data),
            'modelado_ambiental': self._assess_modelado_ambiental(analysis_data)
        }
        
        return results
    
    def _assess_catastro(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa idoneidad para catastro"""
        criteria = self.USE_CASE_CRITERIA['catastro']
        score = 0.0
        max_score = 6.0
        reasons = []
        recomendaciones = []
        
        # Criterio 1: Error planimétrico
        error_plan = analysis_data.get('error_planimetrico')
        if error_plan is not None:
            if error_plan <= criteria['error_planimetrico_max']:
                score += 1.5
                reasons.append(f"Error planimétrico adecuado ({error_plan:.2f}m ≤ {criteria['error_planimetrico_max']}m)")
            else:
                reasons.append(f"Error planimétrico alto ({error_plan:.2f}m > {criteria['error_planimetrico_max']}m)")
                recomendaciones.append("Reducir error planimétrico mediante mejor calibración o datos de referencia")
        else:
            reasons.append("Error planimétrico no calculado")
        
        # Criterio 2: Error altimétrico
        error_alt = analysis_data.get('error_altimetrico')
        if error_alt is not None:
            if error_alt <= criteria['error_altimetrico_max']:
                score += 1.0
                reasons.append(f"Error altimétrico adecuado ({error_alt:.2f}m ≤ {criteria['error_altimetrico_max']}m)")
            else:
                reasons.append(f"Error altimétrico alto ({error_alt:.2f}m > {criteria['error_altimetrico_max']}m)")
                recomendaciones.append("Mejorar precisión altimétrica para catastro")
        else:
            reasons.append("Error altimétrico no disponible (puede ser aceptable si no hay datos Z)")
        
        # Criterio 3: Escala
        escala = analysis_data.get('escala_estimada')
        if escala is not None:
            if escala >= criteria['escala_min']:
                score += 1.5
                reasons.append(f"Escala adecuada (1:{escala} ≥ 1:{criteria['escala_min']})")
            else:
                reasons.append(f"Escala insuficiente (1:{escala} < 1:{criteria['escala_min']})")
                recomendaciones.append(f"Se requiere escala mayor o igual a 1:{criteria['escala_min']} para catastro")
        else:
            reasons.append("Escala no estimada")
        
        # Criterio 4: CRS oficial
        crs = analysis_data.get('crs_detectado', '')
        origen = analysis_data.get('origen_detectado', '')
        if 'MAGNA-SIRGAS' in str(crs) or 'MAGNA-SIRGAS' in str(origen):
            score += 1.5
            reasons.append("CRS oficial (MAGNA-SIRGAS) detectado")
        else:
            reasons.append("CRS no oficial detectado")
            recomendaciones.append("Usar sistema de coordenadas oficial MAGNA-SIRGAS para catastro")
        
        # Criterio 5: Geometrías válidas
        validation = analysis_data.get('validation', {})
        errors = validation.get('errors', [])
        if len(errors) == 0:
            score += 0.5
            reasons.append("Todas las geometrías son válidas")
        else:
            reasons.append(f"Se encontraron {len(errors)} geometrías inválidas")
            recomendaciones.append("Corregir geometrías inválidas antes de usar en catastro")
        
        # Criterio 6: Outliers
        outliers = validation.get('outliers', [])
        num_features = validation.get('statistics', {}).get('num_features', 1)
        outlier_ratio = len(outliers) / num_features if num_features > 0 else 0
        if outlier_ratio <= criteria['outliers_max']:
            score += 0.5
            reasons.append(f"Ratio de outliers aceptable ({outlier_ratio:.2%} ≤ {criteria['outliers_max']:.2%})")
        else:
            reasons.append(f"Ratio de outliers alto ({outlier_ratio:.2%} > {criteria['outliers_max']:.2%})")
            recomendaciones.append("Revisar y validar outliers antes de usar en catastro")
        
        # Determinar idoneidad
        idoneidad = score >= max_score * 0.7  # 70% del score máximo
        
        return {
            'idoneidad': idoneidad,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'reasons': reasons,
            'recomendaciones': recomendaciones
        }
    
    def _assess_topografia_obra(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa idoneidad para topografía de obra"""
        criteria = self.USE_CASE_CRITERIA['topografia_obra']
        score = 0.0
        max_score = 5.0
        reasons = []
        recomendaciones = []
        
        # Criterio 1: Error planimétrico
        error_plan = analysis_data.get('error_planimetrico')
        if error_plan is not None:
            if error_plan <= criteria['error_planimetrico_max']:
                score += 1.5
                reasons.append(f"Error planimétrico adecuado ({error_plan:.2f}m ≤ {criteria['error_planimetrico_max']}m)")
            else:
                reasons.append(f"Error planimétrico alto ({error_plan:.2f}m > {criteria['error_planimetrico_max']}m)")
                recomendaciones.append("Verificar calibración de instrumentos de medición")
        else:
            reasons.append("Error planimétrico no calculado")
        
        # Criterio 2: Escala
        escala = analysis_data.get('escala_estimada')
        if escala is not None:
            if escala >= criteria['escala_min']:
                score += 1.5
                reasons.append(f"Escala adecuada (1:{escala} ≥ 1:{criteria['escala_min']})")
            else:
                reasons.append(f"Escala puede ser insuficiente (1:{escala} < 1:{criteria['escala_min']})")
        else:
            reasons.append("Escala no estimada")
        
        # Criterio 3: CRS (puede ser local)
        crs = analysis_data.get('crs_detectado', '')
        origen = analysis_data.get('origen_detectado', '')
        if crs or origen:
            score += 1.0
            reasons.append(f"CRS detectado: {crs or origen}")
        else:
            reasons.append("CRS no detectado")
            recomendaciones.append("Definir sistema de coordenadas para topografía de obra")
        
        # Criterio 4: Geometrías válidas
        validation = analysis_data.get('validation', {})
        errors = validation.get('errors', [])
        if len(errors) == 0:
            score += 1.0
            reasons.append("Todas las geometrías son válidas")
        else:
            reasons.append(f"Se encontraron {len(errors)} geometrías inválidas")
            recomendaciones.append("Corregir geometrías inválidas")
        
        idoneidad = score >= max_score * 0.6  # 60% del score máximo
        
        return {
            'idoneidad': idoneidad,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'reasons': reasons,
            'recomendaciones': recomendaciones
        }
    
    def _assess_analisis_territorial(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa idoneidad para análisis territorial"""
        criteria = self.USE_CASE_CRITERIA['analisis_territorial']
        score = 0.0
        max_score = 4.0
        reasons = []
        recomendaciones = []
        
        # Criterio 1: Error planimétrico (más tolerante)
        error_plan = analysis_data.get('error_planimetrico')
        if error_plan is not None:
            if error_plan <= criteria['error_planimetrico_max']:
                score += 1.5
                reasons.append(f"Error planimétrico aceptable ({error_plan:.2f}m ≤ {criteria['error_planimetrico_max']}m)")
            else:
                reasons.append(f"Error planimétrico alto ({error_plan:.2f}m > {criteria['error_planimetrico_max']}m)")
                recomendaciones.append("Considerar usar datos con mayor precisión para análisis territorial detallado")
        else:
            reasons.append("Error planimétrico no calculado")
        
        # Criterio 2: Escala
        escala = analysis_data.get('escala_estimada')
        if escala is not None:
            if escala >= criteria['escala_min']:
                score += 1.5
                reasons.append(f"Escala adecuada (1:{escala} ≥ 1:{criteria['escala_min']})")
            else:
                reasons.append(f"Escala puede ser insuficiente para análisis detallado")
        else:
            reasons.append("Escala no estimada")
        
        # Criterio 3: CRS consistente
        crs = analysis_data.get('crs_detectado', '')
        if crs:
            score += 1.0
            reasons.append(f"CRS consistente detectado: {crs}")
        else:
            reasons.append("CRS no detectado")
            recomendaciones.append("Definir CRS consistente para análisis territorial")
        
        idoneidad = score >= max_score * 0.5  # 50% del score máximo
        
        return {
            'idoneidad': idoneidad,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'reasons': reasons,
            'recomendaciones': recomendaciones
        }
    
    def _assess_modelado_ambiental(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa idoneidad para modelado ambiental"""
        criteria = self.USE_CASE_CRITERIA['modelado_ambiental']
        score = 0.0
        max_score = 3.0
        reasons = []
        recomendaciones = []
        
        # Criterio 1: Error planimétrico (muy tolerante)
        error_plan = analysis_data.get('error_planimetrico')
        if error_plan is not None:
            if error_plan <= criteria['error_planimetrico_max']:
                score += 1.5
                reasons.append(f"Error planimétrico aceptable ({error_plan:.2f}m ≤ {criteria['error_planimetrico_max']}m)")
            else:
                reasons.append(f"Error planimétrico muy alto ({error_plan:.2f}m > {criteria['error_planimetrico_max']}m)")
                recomendaciones.append("Considerar usar datos con mayor precisión para modelado ambiental detallado")
        else:
            reasons.append("Error planimétrico no calculado")
        
        # Criterio 2: Escala
        escala = analysis_data.get('escala_estimada')
        if escala is not None:
            if escala >= criteria['escala_min']:
                score += 1.5
                reasons.append(f"Escala adecuada (1:{escala} ≥ 1:{criteria['escala_min']})")
            else:
                reasons.append("Escala puede ser insuficiente para modelado detallado")
        else:
            reasons.append("Escala no estimada")
        
        # Criterio 3: CRS geográfico o proyectado adecuado
        crs = analysis_data.get('crs_detectado', '')
        if crs:
            score += 1.0
            reasons.append(f"CRS detectado: {crs}")
        else:
            reasons.append("CRS no detectado")
            recomendaciones.append("Definir CRS apropiado para modelado ambiental")
        
        idoneidad = score >= max_score * 0.5  # 50% del score máximo
        
        return {
            'idoneidad': idoneidad,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'reasons': reasons,
            'recomendaciones': recomendaciones
        }
    
    def create_validation_results(self, analysis_id: int, use_case_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Crea objetos ValidationResult para cada caso de uso"""
        validation_results = []
        
        use_case_names = {
            'catastro': 'Catastro',
            'topografia_obra': 'Topografía de Obra',
            'analisis_territorial': 'Análisis Territorial',
            'modelado_ambiental': 'Modelado Ambiental'
        }
        
        for use_case_key, use_case_name in use_case_names.items():
            result = use_case_results.get(use_case_key, {})
            
            validation_result = {
                'analisis_id': analysis_id,
                'tipo_validacion': f'idoneidad_{use_case_key}',
                'resultado': 'adecuado' if result.get('idoneidad', False) else 'no_adecuado',
                'mensajes': ' | '.join(result.get('reasons', [])),
                'advertencias': ' | '.join(result.get('recomendaciones', [])),
                'idoneidad_catastro': use_case_key == 'catastro' and result.get('idoneidad', False),
                'idoneidad_topografia': use_case_key == 'topografia_obra' and result.get('idoneidad', False),
                'idoneidad_analisis_territorial': use_case_key == 'analisis_territorial' and result.get('idoneidad', False),
                'idoneidad_modelado_ambiental': use_case_key == 'modelado_ambiental' and result.get('idoneidad', False),
            }
            
            validation_results.append(validation_result)
        
        return validation_results

