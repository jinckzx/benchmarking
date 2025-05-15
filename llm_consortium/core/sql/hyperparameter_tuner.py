# import asyncio
# import numpy as np
# from typing import List, Dict, Callable, Tuple, Any
# import pandas as pd
# from ...utils.logging import logger

# class HyperparameterTuner:
#     def __init__(self):
#         self.trial_results = []  # To store all trial results
        
#     def generate_temperature_values(self, min_temp: float, max_temp: float, num_trials: int) -> List[float]:
#         """Generate a range of temperature values to test"""
#         # Linear spacing between min and max
#         temps = np.linspace(min_temp, max_temp, num_trials)
#         return np.round(temps, 2).tolist()
    
#     async def evaluate_temperature(
#         self, 
#         model: str,
#         temperature: float,
#         queries: List[Dict],
#         query_func: Callable,
#         metrics_func: Any
#     ) -> Dict:
#         """Evaluate model performance at a specific temperature"""
#         results = []
        
#         for i, query in enumerate(queries):
#             # Run model with this temperature
#             entry = await query_func(
#                 model,
#                 query["question"],
#                 0,  # instance
#                 0,  # iteration
#                 query["db_id"],
#                 temperature
#             )
            
#             # Evaluate against gold standard
#             eval_result = metrics_func.evaluate_query(
#                 entry.response,
#                 query["gold_sql"],
#                 query["db_id"]
#             )
            
#             results.append({
#                 "question": query["question"],
#                 "generated_sql": entry.response,
#                 "gold_sql": query["gold_sql"],
#                 "exact_match": eval_result["exact_match"],
#                 "execution_match": eval_result["execution_match"],
#                 "confidence": entry.confidence
#             })
        
#         # Calculate metrics
#         df = pd.DataFrame(results)
#         metrics = metrics_func.compute_metrics(df)
        
#         return {
#             "temperature": temperature,
#             "execution_match_rate": metrics["execution_match_rate"],
#             "exact_match_rate": metrics["exact_match_rate"],
#             "results": results
#         }
    
#     async def tune_model(
#         self,
#         model: str,
#         queries: List[Dict],
#         query_func: Callable,
#         metrics_func: Any,
#         tuning_config: Dict
#     ) -> Dict:
#         """Find optimal hyperparameters for the model"""
#         # Get temperature range and number of trials
#         min_temp, max_temp = tuning_config.get("temp_range", (0.0, 1.0))
#         num_trials = tuning_config.get("num_trials", 5)
        
#         # Clear previous trial results
#         self.trial_results = []
        
#         # Generate temperature values to test
#         temperatures = self.generate_temperature_values(min_temp, max_temp, num_trials)
#         logger.info(f"Testing temperatures: {temperatures}")
        
#         # Evaluate each temperature
#         tasks = []
#         for temp in temperatures:
#             task = self.evaluate_temperature(
#                 model,
#                 temp,
#                 queries,
#                 query_func,
#                 metrics_func
#             )
#             tasks.append(task)
        
#         results = await asyncio.gather(*tasks)
        
#         # Store all trial results
#         for result in results:
#             # Store just the key metrics we need for visualization
#             self.trial_results.append({
#                 "temperature": result["temperature"],
#                 "execution_match_rate": result["execution_match_rate"],
#                 "exact_match_rate": result.get("exact_match_rate", 0.0)
#             })
        
#         # Find best temperature
#         best_result = max(results, key=lambda x: x["execution_match_rate"])
#         best_temp = best_result["temperature"]
        
#         logger.info(f"Temperature tuning results:")
#         for result in results:
#             logger.info(f"  Temperature {result['temperature']}: {result['execution_match_rate']:.2f}%")
        
#         # Add more hyperparameters like top-k, top-p if needed
        
#         return {
#             "temperature": best_temp,
#             "execution_match_rate": best_result["execution_match_rate"],
#             # Add other hyperparameters as needed
#         }
import asyncio
import numpy as np
from typing import List, Dict, Callable, Tuple, Any
import pandas as pd
from ...utils.logging import logger

class HyperparameterTuner:
    def __init__(self):
        self.trial_results = []  # To store all trial results
        
    def generate_temperature_values(self, min_temp: float, max_temp: float, num_trials: int) -> List[float]:
        """Generate a range of temperature values to test"""
        # temps = np.random.uniform(min_temp, max_temp, num_trials) #FOR RANDOM SEARCH
        temps = np.linspace(min_temp, max_temp, num_trials)
        return np.round(temps, 2).tolist()
    
    async def evaluate_temperature(
        self, 
        model: str,
        temperature: float,
        queries: List[Dict],
        query_func: Callable,
        metrics_func: Any
    ) -> Dict:
        """Evaluate model performance at a specific temperature"""
        results = []
        
        for i, query in enumerate(queries):
            # Run model with this temperature
            entry = await query_func(
                model,
                query["question"],
                0,  # instance
                0,  # iteration
                query["db_id"],
                temperature
            )
            
            # Evaluate against gold standard
            eval_result = metrics_func.evaluate_query(
                entry.response,
                query["gold_sql"],
                query["db_id"]
            )
            
            results.append({
                "question": query["question"],
                "generated_sql": entry.response,
                "gold_sql": query["gold_sql"],
                "exact_match": eval_result["exact_match"],
                "execution_match": eval_result["execution_match"],
                "confidence": entry.confidence
            })
        
        # Calculate metrics
        df = pd.DataFrame(results)
        metrics = metrics_func.compute_metrics(df)
        
        return {
            "temperature": temperature,
            "execution_match_rate": metrics["execution_match_rate"],
            "exact_match_rate": metrics["exact_match_rate"],
            "results": results
        }
    
    async def tune_model(
        self,
        model: str,
        queries: List[Dict],
        query_func: Callable,
        metrics_func: Any,
        tuning_config: Dict
    ) -> Dict:
        """Find optimal hyperparameters for the model"""
        # Get temperature range and number of trials
        min_temp, max_temp = tuning_config.get("temp_range", (0.0, 1.0))
        num_trials = tuning_config.get("num_trials", 5)
        
        # Clear previous trial results
        self.trial_results = []
        
        # Generate temperature values to test
        temperatures = self.generate_temperature_values(min_temp, max_temp, num_trials)
        logger.info(f"Testing temperatures: {temperatures}")
        
        # Evaluate each temperature
        tasks = []
        for temp in temperatures:
            task = self.evaluate_temperature(
                model,
                temp,
                queries,  # Use the entire provided query set (which is already sampled at the UI level)
                query_func,
                metrics_func
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Store all trial results
        for result in results:
            # Store just the key metrics we need for visualization
            self.trial_results.append({
                "temperature": result["temperature"],
                "execution_match_rate": result["execution_match_rate"],
                "exact_match_rate": result.get("exact_match_rate", 0.0)
            })
        
        # Find best temperature
        best_result = max(results, key=lambda x: x["execution_match_rate"])
        best_temp = best_result["temperature"]
        
        logger.info(f"Temperature tuning results:")
        for result in results:
            logger.info(f"  Temperature {result['temperature']}: {result['execution_match_rate']:.2f}%")
        
        # Add more hyperparameters like top-k, top-p if needed
        
        return {
            "temperature": best_temp,
            "execution_match_rate": best_result["execution_match_rate"],
            # Add other hyperparameters as needed
        }