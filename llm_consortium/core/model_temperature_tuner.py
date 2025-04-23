import numpy as np
from typing import List, Dict, Tuple

class ModelTemperatureTuner:
    @staticmethod
    def generate_temperatures(min_temp: float, max_temp: float, num_trials: int) -> List[float]:
        """Generate unique temperatures for model tuning"""
        temps = np.random.uniform(min_temp, max_temp, num_trials)
        return np.unique(np.round(temps, 2)).tolist()
    
    @staticmethod
    def assign_temperatures_to_models(models: Dict[str, int], 
                                    temperatures: List[float]) -> Dict[str, List[float]]:
        """Assign temperatures to each model instance"""
        model_temps = {}
        for model_name, count in models.items():
            # For each model, randomly select a subset of temperatures
            # limited by the number of instances
            selected_temps = np.random.choice(
                temperatures, 
                min(count, len(temperatures)), 
                replace=False
            ).tolist()
            
            # If more instances than temperatures, we'll need to reuse temperatures
            if count > len(selected_temps):
                additional_temps = np.random.choice(
                    temperatures,
                    count - len(selected_temps),
                    replace=True
                ).tolist()
                selected_temps.extend(additional_temps)
            
            model_temps[model_name] = selected_temps
        
        return model_temps