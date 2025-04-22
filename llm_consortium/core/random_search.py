import numpy as np
from typing import List, Dict

class ArbiterTemperatureTuner:
    @staticmethod
    def generate_temperatures(min_temp: float, max_temp: float, num_trials: int) -> List[float]:
        """Generate unique temperatures for arbiter tuning"""
        temps = np.random.uniform(min_temp, max_temp, num_trials)
        return np.unique(np.round(temps, 2)).tolist()