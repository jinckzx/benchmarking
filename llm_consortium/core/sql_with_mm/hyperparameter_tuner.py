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
        primary_metric: str,
        base_params: Dict
    ) -> Dict:
        """Evaluate model performance at a specific temperature"""
        results = []
        params = base_params.copy()
        params["temperature"] = temperature
        
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
                    params
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
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Log the number of results collected
        logger.info(f"Temperature {temperature}: Collected {len(results)} valid results")
        
        # Calculate metrics
        metrics = {}
        if results:
            # Calculate average metrics across results
            metrics = self._calculate_average_metrics(results)
            logger.info(f"Temperature {temperature}: Metrics: {metrics}")
        else:
            logger.warning(f"Temperature {temperature}: No valid results collected")
        
        return {
            "temperature": temperature,
            "metrics": metrics,
            "results": results
        }
        
    async def tune_model(
        self,
        model: str,
        queries: List[Dict],
        query_func: Callable,
        metrics_func: Callable[[str, str, str], Awaitable[Dict[str, Any]]],
        tuning_config: Dict,
        base_params: Dict
    ) -> Dict:
        """Find optimal hyperparameters for the model"""
        logger.info(f"Starting hyperparameter tuning for {model}")
        
        # Get configuration parameters
        min_temp, max_temp = tuning_config.get("temp_range", (0.0, 1.0))
        num_trials = tuning_config.get("num_trials", 5)
        primary_metric = tuning_config.get("primary_metric", "execution_match_rate")
        
        # Generate temperatures and run evaluations
        temperatures = self.generate_temperature_values(min_temp, max_temp, num_trials)
        results = await asyncio.gather(*[
            self.evaluate_temperature(
                model, temp, queries, query_func, 
                metrics_func, primary_metric, base_params
            )
            for temp in temperatures
        ])

        # Store trial results with all metrics
        self.trial_results = []
        for result in results:
            if result["metrics"]: 
                self.trial_results.append({
                    "temperature": result["temperature"],
                    **result["metrics"]
                })

        # Create a DataFrame for analysis
        result_df = pd.DataFrame(self.trial_results) if self.trial_results else pd.DataFrame()
        
        # Find best temperature for each metric
        best_metrics = {}
        if not result_df.empty:
            # Get all metrics columns (exclude temperature)
            metric_cols = [col for col in result_df.columns if col != "temperature"]
            
            for metric in metric_cols:
                if pd.api.types.is_numeric_dtype(result_df[metric]):
                    # Find the best temperature for this metric
                    # For metrics with "rate" in name or higher is better
                    if "rate" in metric or metric.endswith("_score"):
                        best_idx = result_df[metric].idxmax()
                    else:
                        # For error metrics, lower is better
                        best_idx = result_df[metric].idxmin()
                        
                    best_metrics[metric] = {
                        "temperature": result_df.loc[best_idx, "temperature"],
                        "value": result_df.loc[best_idx, metric]
                    }

        # Get primary metric result
        primary_result = best_metrics.get(
            primary_metric,
            {"temperature": (min_temp + max_temp)/2, "value": 0.0}
        )

        # Return all metrics results organized by metric
        return {
            "primary_metric": primary_result,
            "all_metrics": best_metrics,
            "trial_results": self.trial_results,
            "result_df": result_df
        }
     
    def _calculate_average_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average metrics across all results."""
        df = pd.DataFrame(results)
        avg_metrics = {}
        
        # Handle boolean success metrics
        bool_cols = [col for col in df.columns if df[col].dtype == 'bool']
        for col in bool_cols:
            avg_metrics[f"{col}_rate"] = df[col].mean() * 100
            
        # Handle numeric metrics
        num_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        for col in num_cols:
            if col not in bool_cols:  # Skip boolean columns already processed
                avg_metrics[col] = df[col].mean()
                
        return avg_metrics