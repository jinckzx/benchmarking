# import numpy as np
# from typing import List, Dict, Tuple
# from ..config.models import LogEntry
# from ..database.synthesis_db import SynthesisDatabaseHandler

# class RandomSearchTuner:
#     def __init__(self, synthesis_db: SynthesisDatabaseHandler):
#         self.synthesis_db = synthesis_db
        
#     async def run_temperature_search(
#         self,
#         synthesis_handler,
#         prompt: str,
#         responses: List[LogEntry],
#         arbiter: str,
#         iteration: int,
#         min_temp: float,
#         max_temp: float,
#         num_trials: int
#     ) -> Tuple[Dict, List[Dict]]:
#         """Perform random temperature search"""
#         temperatures = np.random.uniform(min_temp, max_temp, num_trials).round(2)
#         unique_temps = np.unique(temperatures).tolist()
        
#         best_result = None
#         all_results = []

#         for temp in unique_temps:
#             synthesis = await synthesis_handler.synthesize(
#                 prompt=prompt,
#                 responses=responses,
#                 arbiter=arbiter,
#                 iteration=iteration,
#                 temperature=temp
#             )
            
#             result_entry = {
#                 "temperature": temp,
#                 "confidence": synthesis["confidence"],
#                 "text": synthesis["text"],
#                 "analysis": synthesis["analysis"],
#                 "dissent": synthesis["dissenting_views"]
#             }
            
#             all_results.append(result_entry)

#             # Update best result
#             if not best_result or synthesis["confidence"] > best_result["confidence"]:
#                 best_result = {
#                     "temperature": temp,
#                     "confidence": synthesis["confidence"],
#                     "text": synthesis["text"],
#                     "analysis": synthesis["analysis"],
#                     "dissent": synthesis["dissenting_views"]
#                 }

#             # Log to database
#             self.synthesis_db.log_tuning_trial(
#                 iteration=iteration,
#                 temperature=temp,
#                 result=result_entry
#             )

#         return best_result, all_results
import numpy as np
from typing import List, Dict

class ArbiterTemperatureTuner:
    @staticmethod
    def generate_temperatures(min_temp: float, max_temp: float, num_trials: int) -> List[float]:
        """Generate unique temperatures for arbiter tuning"""
        temps = np.random.uniform(min_temp, max_temp, num_trials)
        return np.unique(np.round(temps, 2)).tolist()