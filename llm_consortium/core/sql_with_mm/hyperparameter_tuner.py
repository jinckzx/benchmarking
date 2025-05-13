import asyncio
import numpy as np
from typing import List, Dict, Callable, Any
import pandas as pd
from ...utils.logging import logger

class HyperparameterTuner:
    def __init__(self):
        self.trial_results = []  # To store all trial results
        
    def generate_temperature_values(self, min_temp: float, max_temp: float, num_trials: int) -> List[float]:
        """Generate a range of temperature values to test"""
        # Linear spacing between min and max
        temps = np.linspace(min_temp, max_temp, num_trials)
        return np.round(temps, 2).tolist()
    
    async def evaluate_temperature(
        self, 
        model: str,
        temperature: float,
        queries: List[Dict],
        query_func: Callable,
        metrics_func: Any,
        primary_metric: str
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
            
            # Evaluate against gold standard using the metrics object
            eval_result = metrics_func.evaluate_query(
                entry.response,
                query.get("gold_sql", ""),
                query["db_id"]
            )
            
            # Add results
            results.append({
                "question": query["question"],
                "generated_sql": entry.response,
                "gold_sql": query.get("gold_sql", ""),
                "confidence": entry.confidence,
                **eval_result  # Unpack all metric results
            })
        
        # Calculate metrics
        df = pd.DataFrame(results)
        metrics = metrics_func.compute_metrics(df)

        # Return primary metric and all results
        primary_metric_value = metrics.get(primary_metric, 0.0)
        if isinstance(primary_metric_value, (int, float)):
            # For numerical metrics
            return {
                "temperature": temperature,
                primary_metric: primary_metric_value,
                "results": results
            }
        else:
            # For non-numerical metrics, default to first available numerical metric
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and "_rate" in key:
                    return {
                        "temperature": temperature,
                        key: value,
                        "results": results
                    }
            # Fallback
            return {
                "temperature": temperature,
                "performance": 0.0,
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
        primary_metric = tuning_config.get("primary_metric", "execution_match_rate")
        
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
                queries,
                query_func,
                metrics_func,
                primary_metric
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Store all trial results for visualization
        for result in results:
            self.trial_results.append({
                "temperature": result["temperature"],
                primary_metric: result.get(primary_metric, 0.0)
            })
        
        # Find best temperature based on primary metric
        best_result = max(results, key=lambda x: x.get(primary_metric, 0.0))
        best_temp = best_result["temperature"]
        
        logger.info(f"Temperature tuning results:")
        for result in results:
            metric_value = result.get(primary_metric, 0.0)
            if isinstance(metric_value, (int, float)):
                logger.info(f"  Temperature {result['temperature']}: {metric_value:.2f}%")
            else:
                logger.info(f"  Temperature {result['temperature']}: {metric_value}")
        
        return {
            "temperature": best_temp,
            primary_metric: best_result.get(primary_metric, 0.0)
        }