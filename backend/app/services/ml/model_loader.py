"""
Cargador de modelos ML para inferencia
"""
import os
import pickle
from typing import Optional, Dict, Any, List
from pathlib import Path


class ModelLoader:
    """Carga y gestiona modelos ML para inferencia"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._loaded_models = {}
    
    def load_model(self, model_name: str, model_type: str = "sklearn") -> Optional[Any]:
        """Carga un modelo ML"""
        if model_name in self._loaded_models:
            return self._loaded_models[model_name]
        
        model_path = self.models_dir / f"{model_name}.pkl"
        
        if not model_path.exists():
            print(f"Modelo no encontrado: {model_path}")
            return None
        
        try:
            if model_type == "sklearn":
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            elif model_type == "xgboost":
                try:
                    import xgboost as xgb
                    model = xgb.Booster()
                    model.load_model(str(model_path))
                except ImportError:
                    print("xgboost no está instalado")
                    return None
            else:
                print(f"Tipo de modelo no soportado: {model_type}")
                return None
            
            self._loaded_models[model_name] = model
            return model
        except Exception as e:
            print(f"Error cargando modelo {model_name}: {str(e)}")
            return None
    
    def predict(self, model_name: str, features: Any, model_type: str = "sklearn") -> Optional[Any]:
        """Realiza predicción con un modelo"""
        model = self.load_model(model_name, model_type)
        if model is None:
            return None
        
        try:
            if model_type == "sklearn":
                prediction = model.predict(features)
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(features)
                    return {
                        'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
                        'probabilities': probabilities.tolist() if hasattr(probabilities, 'tolist') else probabilities
                    }
                return {
                    'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction
                }
            elif model_type == "xgboost":
                try:
                    import xgboost as xgb
                    import numpy as np
                    dmatrix = xgb.DMatrix(features)
                    prediction = model.predict(dmatrix)
                except ImportError:
                    print("xgboost no está instalado")
                    return None
                return {
                    'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction
                }
        except Exception as e:
            print(f"Error en predicción: {str(e)}")
            return None
    
    def list_available_models(self) -> List[str]:
        """Lista modelos disponibles"""
        models = []
        for file in self.models_dir.glob("*.pkl"):
            models.append(file.stem)
        return models

