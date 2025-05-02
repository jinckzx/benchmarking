import asyncio
import numpy as np
from typing import List, Dict, Callable, Tuple, Any
import pandas as pd
from ...utils.logging import logger
import re
class ClassificationHyperparameterTuner:
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
        valid_classes: List[str]  # Add valid_classes parameter
    ) -> Dict:
        """Evaluate model performance at a specific temperature for classification"""
        results = []
        
        for i, query in enumerate(queries):
            try:
                entry = await query_func(
                    model,
                    query["question"],
                    0,  # instance
                    0,  # iteration 
                    valid_classes,  # Pass valid_classes
                    temperature
                )
                
                # Handle invalid predictions without copy()
                predicted_class = entry.predicted_class
                if predicted_class not in valid_classes:
                    predicted_class = "invalid_prediction"
                
                results.append({
                    "question": query["question"],
                    "ground_truth": query["ground_truth"],
                    "predicted_class": entry.predicted_class,
                    "confidence": entry.confidence,
                    "correct": entry.predicted_class == query["ground_truth"]
                })
                
            except KeyError as e:
                logger.error(f"Skipping invalid query: {str(e)}")
                continue

        # Calculate metrics using the metrics handler with valid_classes
        df = pd.DataFrame(results)
        metrics = metrics_func.calculate_metrics_single_model(df, model)
        
        # Calculate combined score (average of accuracy and F1)
        combined_score = (metrics["accuracy"] + metrics["f1"]) / 2
        
        return {
            "temperature": temperature,
            "accuracy": metrics["accuracy"],
            "f1": metrics["f1"],
            "combined_score": combined_score,
            "results": results
        }    
    # async def evaluate_temperature(
    #     self, 
    #     model: str,
    #     temperature: float,
    #     queries: List[Dict],
    #     query_func: Callable,
    #     metrics_func: Any,
    #     valid_classes: List[str]
    # ) -> Dict:
    #     """Evaluate model performance at a specific temperature for classification"""
    #     results = []
        
    #     for i, query in enumerate(queries):
    #         if 'question' not in query or 'ground_truth' not in query:
    #             logger.error(f"Skipping invalid query in tuning: {query}")
    #             continue

    #         # Run model with this temperature
    #         entry = await query_func(
    #             model,
    #             query["question"],
    #             0,  # instance
    #             0,  # iteration 
    #             valid_classes,
    #             temperature
    #         )
            
    #         # Store result for metrics calculation
    #         results.append({
    #             "question": query["question"],
    #             "ground_truth": query["ground_truth"],
    #             "predicted_class": entry.predicted_class,
    #             "confidence": entry.confidence,
    #             "correct": entry.predicted_class == query["ground_truth"]
    #         })
        
    #     # Calculate metrics using the metrics handler
    #     df = pd.DataFrame(results)
    #     metrics = metrics_func.calculate_metrics_single_model(df, model)
        
    #     # Calculate combined score (average of accuracy and F1)
    #     combined_score = (metrics["accuracy"] + metrics["f1"]) / 2
        
    #     return {
    #         "temperature": temperature,
    #         "accuracy": metrics["accuracy"],
    #         "f1": metrics["f1"],
    #         "combined_score": combined_score,
    #         "results": results
    #     }
    
    async def tune_model(
        self,
        model: str,
        queries: List[Dict],
        query_func: Callable,
        metrics_func: Any,
        tuning_config: Dict
    ) -> Dict:
        """Find optimal hyperparameters for the classification model"""
        # Get temperature range and number of trials
        min_temp, max_temp = tuning_config.get("temp_range", (0.0, 1.0))
        num_trials = tuning_config.get("num_trials", 5)
        valid_classes = tuning_config.get("valid_classes", [])
        
        # Clear previous trial results
        self.trial_results = []
        
        # Generate temperature values to test
        temperatures = self.generate_temperature_values(min_temp, max_temp, num_trials)
        logger.info(f"Testing temperatures for classification: {temperatures}")
        
        # Evaluate each temperature
        tasks = []
        for temp in temperatures:
            task = self.evaluate_temperature(
                model,
                temp,
                queries,
                query_func,
                metrics_func,
                valid_classes
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Store all trial results
        for result in results:
            # Store key metrics for visualization
            self.trial_results.append({
                "temperature": result["temperature"],
                "accuracy": result["accuracy"],
                "f1": result["f1"],
                "combined_score": result["combined_score"]
            })
        
        # Find best temperature based on combined score
        best_result = max(results, key=lambda x: x["combined_score"])
        best_temp = best_result["temperature"]
        
        logger.info(f"Temperature tuning results for classification:")
        for result in results:
            logger.info(f"  Temperature {result['temperature']}: "
                     f"Accuracy {result['accuracy']:.2f}, "
                     f"F1 {result['f1']:.2f}, "
                     f"Combined {result['combined_score']:.2f}")
        
        return {
            "temperature": best_temp,
            "accuracy": best_result["accuracy"],
            "f1": best_result["f1"],
            "combined_score": best_result["combined_score"]
        }
        
    def visualize_results(self) -> Dict:
        """Prepare trial results for visualization"""
        if not self.trial_results:
            return {"status": "No tuning data available"}
            
        df = pd.DataFrame(self.trial_results)
        
        return {
            "temperatures": df["temperature"].tolist(),
            "accuracy_values": df["accuracy"].tolist(),
            "f1_values": df["f1"].tolist(),
            "combined_scores": df["combined_score"].tolist()
        }