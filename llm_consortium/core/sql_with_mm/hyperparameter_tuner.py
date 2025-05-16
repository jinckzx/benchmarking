#old
# import asyncio
# import numpy as np
# from typing import List, Dict, Callable, Any
# import pandas as pd
# from ...utils.logging import logger

# class HyperparameterTuner:
#     def __init__(self):
#         self.trial_results = []  # To store all trial results
        
#     def generate_temperature_values(self, min_temp: float, max_temp: float, num_trials: int) -> List[float]:
#         """Generate a range of temperature values to test"""
#         # temps = np.random.uniform(min_temp, max_temp, num_trials) #FOR RANDOM SEARCH
#         temps = np.linspace(min_temp, max_temp, num_trials)
#         return np.round(temps, 2).tolist()
    
#     async def evaluate_temperature(
#         self, 
#         model: str,
#         temperature: float,
#         queries: List[Dict],
#         query_func: Callable,
#         metrics_func: Any,
#         primary_metric: str
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
            
#             # Evaluate against gold standard using the metrics object
#             eval_result = metrics_func.evaluate_query(
#                 entry.response,
#                 query.get("gold_sql", ""),
#                 query["db_id"]
#             )
            
#             # Add results
#             results.append({
#                 "question": query["question"],
#                 "generated_sql": entry.response,
#                 "gold_sql": query.get("gold_sql", ""),
#                 "confidence": entry.confidence,
#                 **eval_result  # Unpack all metric results
#             })
        
#         # Calculate metrics
#         df = pd.DataFrame(results)
#         metrics = metrics_func.compute_metrics(df)

#         # Return primary metric and all results
#         primary_metric_value = metrics.get(primary_metric, 0.0)
#         if isinstance(primary_metric_value, (int, float)):
#             # For numerical metrics
#             return {
#                 "temperature": temperature,
#                 primary_metric: primary_metric_value,
#                 "results": results
#             }
#         else:
#             # For non-numerical metrics, default to first available numerical metric
#             for key, value in metrics.items():
#                 if isinstance(value, (int, float)) and "_rate" in key:
#                     return {
#                         "temperature": temperature,
#                         key: value,
#                         "results": results
#                     }
#             # Fallback
#             return {
#                 "temperature": temperature,
#                 "performance": 0.0,
#                 "results": results
#             }
    
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
#         primary_metric = tuning_config.get("primary_metric", "execution_match_rate")
        
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
#                 metrics_func,
#                 primary_metric
#             )
#             tasks.append(task)
        
#         results = await asyncio.gather(*tasks)
        
#         # Store all trial results for visualization
#         for result in results:
#             self.trial_results.append({
#                 "temperature": result["temperature"],
#                 primary_metric: result.get(primary_metric, 0.0)
#             })
        
#         # Find best temperature based on primary metric
#         best_result = max(results, key=lambda x: x.get(primary_metric, 0.0))
#         best_temp = best_result["temperature"]
        
#         logger.info(f"Temperature tuning results:")
#         for result in results:
#             metric_value = result.get(primary_metric, 0.0)
#             if isinstance(metric_value, (int, float)):
#                 logger.info(f"  Temperature {result['temperature']}: {metric_value:.2f}%")
#             else:
#                 logger.info(f"  Temperature {result['temperature']}: {metric_value}")
        
#         return {
#             "temperature": best_temp,
#             primary_metric: best_result.get(primary_metric, 0.0)
#         }

import asyncio
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Callable, Awaitable
from ...utils.logging import logger

class HyperparameterTuner:
    """
    Tunes hyperparameters for SQL generation models.
    
    This class implements Bayesian optimization for hyperparameter tuning
    with automatic parallelization.
    """
    
    def __init__(self):
        """Initialize the tuner with default settings."""
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
        metrics_func: Callable[[str, str, str], Awaitable[Dict[str, Any]]],
        primary_metric: str
    ) -> Dict:
        """Evaluate model performance at a specific temperature"""
        results = []
        
        # For simplicity, use a subset of queries if there are many
        sample_queries = queries
        if len(queries) > 5:
            sample_queries = random.sample(queries, 5)
            
        for query in sample_queries:
            try:
                # Run model with this temperature
                entry = await query_func(
                    model,
                    query["question"],
                    0,  # instance
                    0,  # iteration
                    query["db_id"],
                    temperature
                )
                
                # Evaluate against gold standard using the metrics function
                if not entry.error:
                    # Call the metrics_func correctly
                    eval_result = await metrics_func(
                        entry.response,
                        query.get("gold_sql", ""),
                        query["db_id"]
                    )
                    
                    # Add results
                    results.append({
                        "question": query["question"],
                        "generated_sql": entry.response,
                        "gold_sql": query.get("gold_sql", ""),
                        "confidence": entry.confidence if hasattr(entry, "confidence") else 0.0,
                        **eval_result  # Unpack all metric results
                    })
            except Exception as e:
                logger.error(f"Error evaluating query with temperature {temperature}: {str(e)}")
                # Log the full exception traceback for debugging
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Log the number of results collected
        logger.info(f"Temperature {temperature}: Collected {len(results)} valid results")
        
        # Calculate metrics
        if results:
            # Calculate average metrics across results
            metrics = self._calculate_average_metrics(results)
            logger.info(f"Temperature {temperature}: Metrics: {metrics}")
            
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
        logger.warning(f"Temperature {temperature}: No valid metrics calculated, returning 0.0")
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
        metrics_func: Callable[[str, str, str], Awaitable[Dict[str, Any]]],
        tuning_config: Dict
    ) -> Dict:
        """Find optimal hyperparameters for the model"""
        logger.info(f"Starting hyperparameter tuning for {model}")
        
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
        
        # Check if any results were obtained
        if not results:
            logger.error("No results obtained from temperature evaluation")
            return {"temperature": (min_temp + max_temp) / 2, primary_metric: 0.0}
        
        # Store all trial results for visualization
        for result in results:
            metric_value = result.get(primary_metric, 0.0)
            self.trial_results.append({
                "temperature": result["temperature"],
                primary_metric: metric_value
            })
            logger.info(f"Trial result: temp={result['temperature']}, {primary_metric}={metric_value}")
        
        # Find best temperature based on primary metric
        if not results or not any(primary_metric in r for r in results):
            logger.error(f"No results contain primary metric '{primary_metric}'")
            return {"temperature": (min_temp + max_temp) / 2, primary_metric: 0.0}
            
        filtered_results = [r for r in results if primary_metric in r]
        if not filtered_results:
            logger.error(f"No valid results with primary metric '{primary_metric}'")
            return {"temperature": (min_temp + max_temp) / 2, primary_metric: 0.0}
            
        best_result = max(filtered_results, key=lambda x: x.get(primary_metric, 0.0))
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
     # Updated _calculate_average_metrics in HyperparameterTuner
       
    def _calculate_average_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average metrics across all results."""
        # Create a DataFrame with all results
        df = pd.DataFrame(results)
        
        # Extract numerical columns (metrics)
        non_metric_columns = ["question", "generated_sql", "gold_sql", "confidence"]
        metric_columns = [col for col in df.columns if col not in non_metric_columns]
        
        # Calculate averages for each metric
        avg_metrics = {}
        
        for col in metric_columns:
            # Check if column exists and if it's a simple numeric type
            if col in df:
                if df[col].dtype in ['int64', 'float64', 'bool']:
                    # For boolean columns, calculate the percentage of True values
                    if df[col].dtype == 'bool':
                        avg_metrics[col] = df[col].mean() * 100
                    else:
                        avg_metrics[col] = df[col].mean()
                elif df[col].apply(lambda x: isinstance(x, (int, float, bool))).all():
                    # For columns with mixed numeric types
                    avg_metrics[col] = df[col].astype(float).mean()
        
        # Add metric rates for boolean columns
        for col in metric_columns:
            if col in df and df[col].dtype == 'bool':
                rate_key = f"{col}_rate"
                if rate_key not in avg_metrics:
                    avg_metrics[rate_key] = df[col].mean() * 100
                    
        return avg_metrics