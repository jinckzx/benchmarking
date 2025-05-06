import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from ...config.models_classification import ModelConfig, LogEntry
from ...database.database_classification import DatabaseHandlerClassification
from ...utils.extractors import ResponseExtractor
from ...utils.prompt_utils import read_system_prompt, read_iteration_prompt_class
from dotenv import load_dotenv
from ...utils.logging import logger
from ...metrics.metrics_classification import ClassificationMetricsHandler
from .hyperparameter_tuner_classification import ClassificationHyperparameterTuner
from ..client_init import llm

load_dotenv()

class ClassificationModelRunner:
    def __init__(self):
        self.client = llm
        self.db_handler = DatabaseHandlerClassification()
        self.extractor = ResponseExtractor()
        self.system_prompt = read_system_prompt()
        self.iteration_prompt_template = read_iteration_prompt_class()
        self.metrics = ClassificationMetricsHandler()
        self.hyperparameter_tuner = ClassificationHyperparameterTuner()
        
    def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load and validate CSV input for classification tasks"""
        try:
            df = pd.read_csv(csv_path)

            # Validate required columns
            required_columns = {"question", "ground_truth"}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
            
            # Clean data
            df = df.dropna(subset=['question', 'ground_truth'])
            df = df[df['question'].astype(bool) & df['ground_truth'].astype(bool)]
            
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"CSV ingestion failed: {str(e)}")
            return []

    async def _query_model(self, model: str, prompt: str, instance: int,
                     iteration: int, valid_classes: List[str], temperature: float = 0.2) -> LogEntry:
        """Execute model query with enhanced error handling"""
        start_time = datetime.now()
        try:
            # Validate inputs
            if not prompt or not isinstance(prompt, str):
                raise ValueError("Invalid question prompt")
            if not valid_classes:
                raise ValueError("No valid classes provided")
            
            classes_context = ", ".join(valid_classes)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.iteration_prompt_template.format(
                    prompt=prompt,
                    classes=classes_context,
                    model=model
                )}
            ]
            
            response = await self.client.chat(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            content = response.get("content", "")
            predicted_class = self.extractor.extract_class(content)
            confidence = self.extractor.extract_confidence(content)
            
            return LogEntry(
                prompt=prompt,
                model=f"{model}-{instance}",
                predicted_class=predicted_class,
                confidence=confidence,
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                raw_response=content,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Query failed for model {model}: {str(e)}")
            return LogEntry(
                prompt=prompt,
                model=f"{model}-{instance}",
                predicted_class="",
                confidence=0.0,
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                error=str(e),
                temperature=temperature
            )
    async def evaluate_models(self, config: ModelConfig, csv_path: str, 
                        valid_classes: List[str]) -> Dict[str, Any]:
        """Run evaluation with models and queries in parallel"""
        models_results = {}
        queries = self.ingest_csv(csv_path)
        
        if not queries:
            logger.error("No valid queries to process")
            return models_results
            
        if not valid_classes:
            raise ValueError("Valid classes list cannot be empty")

        async def evaluate_single_model(model_name: str):
            """Process one model with parallel queries"""
            try:
                logger.info(f"Starting parallel evaluation for {model_name}")
                
                # Create all query tasks
                query_tasks = [
                    self._query_model(
                        model_name,
                        query["question"],
                        0,  # instance
                        0,  # iteration
                        valid_classes,
                        config.base_temperature
                    )
                    for query in queries
                ]
                
                # Run all queries concurrently
                entries = await asyncio.gather(*query_tasks)
                
                model_responses = []
                for entry, query in zip(entries, queries):
                    response_with_metrics = {
                        "question": query["question"],
                        "ground_truth": query["ground_truth"],
                        "predicted_class": entry.predicted_class,
                        "confidence": float(entry.confidence),
                        "latency": float(entry.latency),
                        "correct": entry.predicted_class == query["ground_truth"],
                        "error": entry.error
                    }
                    model_responses.append(response_with_metrics)

                # Calculate metrics
                df = pd.DataFrame(model_responses)
                if df.empty:
                    raise ValueError("No valid responses collected")
                    
                df = df.convert_dtypes()
                df['correct'] = df['correct'].astype(bool)
                df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.0)
                
                metrics = self.metrics.calculate_metrics_single_model(df, model_name)
                return (model_name, metrics, model_responses)

            except Exception as e:
                logger.error(f"Model {model_name} evaluation failed: {str(e)}")
                return (model_name, {
                    "model": model_name,
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0,
                    "error": str(e)
                }, [])

        # Create and run all model tasks concurrently
        model_tasks = [evaluate_single_model(model) for model in config.models]
        results = await asyncio.gather(*model_tasks)

        # Process results
        for model_name, metrics, responses in results:
            models_results[model_name] = {
                "metrics": metrics,
                "responses": responses
            }

        return models_results
    # async def evaluate_models(self, config: ModelConfig, csv_path: str, 
    #                      valid_classes: List[str]) -> Dict[str, Any]:
    #     """Run evaluation with comprehensive validation"""
    #     models_results = {}
    #     queries = self.ingest_csv(csv_path)
        
    #     if not queries:
    #         logger.error("No valid queries to process")
    #         return models_results
            
    #     if not valid_classes:
    #         raise ValueError("Valid classes list cannot be empty")
            
    #     for model_name in config.models:
    #         try:
    #             model_responses = []
    #             logger.info(f"Starting evaluation for {model_name} with {len(queries)} queries")
                
    #             for query in queries:
    #                 try:
    #                     entry = await self._query_model(
    #                         model_name,
    #                         query["question"],
    #                         0,  # instance
    #                         0,  # iteration
    #                         valid_classes,
    #                         config.base_temperature
    #                     )
                        
    #                     response_with_metrics = {
    #                         "question": query["question"],
    #                         "ground_truth": query["ground_truth"],
    #                         "predicted_class": entry.predicted_class,
    #                         "confidence": float(entry.confidence),
    #                         "latency": float(entry.latency),
    #                         "correct": entry.predicted_class == query["ground_truth"],
    #                         "error": entry.error
    #                     }
    #                     model_responses.append(response_with_metrics)
    #                 except KeyError as e:
    #                     logger.error(f"Skipping invalid query: {str(e)}")
    #                     continue
                
    #             # Calculate metrics with enhanced validation
    #             try:
    #                 df = pd.DataFrame(model_responses)
    #                 if df.empty:
    #                     raise ValueError("No valid responses collected")
                        
    #                 # Convert types explicitly
    #                 df = df.convert_dtypes()
    #                 df['correct'] = df['correct'].astype(bool)
    #                 df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.0)
                    
    #                 metrics = self.metrics.calculate_metrics_single_model(df, model_name)
    #             except Exception as e:
    #                 logger.error(f"Metrics calculation failed for {model_name}: {str(e)}")
    #                 metrics = {
    #                     "model": model_name,
    #                     "accuracy": 0.0,
    #                     "precision": 0.0,
    #                     "recall": 0.0,
    #                     "f1": 0.0,
    #                     "error": str(e)
    #                 }
                
    #             models_results[model_name] = {
    #                 "metrics": metrics,
    #                 "responses": model_responses
    #             }
                
    #         except Exception as e:
    #             logger.error(f"Model {model_name} evaluation failed: {str(e)}")
    #             models_results[model_name] = {
    #                 "metrics": {
    #                     "model": model_name,
    #                     "accuracy": 0.0,
    #                     "precision": 0.0,
    #                     "recall": 0.0,
    #                     "f1": 0.0,
    #                     "error": str(e)
    #                 },
    #                 "responses": []
    #             }
        
    #     return models_results

    def find_best_model(self, evaluation_results: Dict) -> str:
        """Find the best model with validation"""
        if not evaluation_results:
            raise ValueError("No evaluation results to analyze")
            
        best_model = None
        best_score = -1
        
        for model_name, results in evaluation_results.items():
            try:
                metrics = results["metrics"]
                accuracy = metrics.get("accuracy", 0.0)
                f1 = metrics.get("f1", 0.0)
                combined_score = (accuracy + f1) / 2
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_model = model_name
            except KeyError as e:
                logger.error(f"Invalid metrics format for {model_name}: {str(e)}")
                continue
        
        if not best_model:
            raise ValueError("No valid models found in evaluation results")
            
        logger.info(f"Best model identified: {best_model} (Score: {best_score:.2f})")
        return best_model

    async def tune_best_model(self, model: str, csv_path: str, config: ModelConfig, 
                         valid_classes: List[str]) -> Dict[str, Any]:
        """Tune hyperparameters with validation"""
        if config.min_temp >= config.max_temp:
            raise ValueError(f"Invalid temperature range: {config.min_temp}-{config.max_temp}")
            
        if config.num_trials < 3:
            logger.warning("Increasing number of trials to minimum 3")
            config.num_trials = 3
            
        try:
            logger.info(f"Starting hyperparameter tuning for {model}")
            queries = self.ingest_csv(csv_path)
            
            if not queries:
                raise ValueError("No valid queries available for tuning")
                
            tuning_config = {
                "temp_range": (config.min_temp, config.max_temp),
                "num_trials": config.num_trials,
                "valid_classes": valid_classes
            }
            
            best_params = await self.hyperparameter_tuner.tune_model(
                model,
                queries,
                self._query_model,
                self.metrics,
                tuning_config
            )
            # Check if we have meaningful results
            if best_params["combined_score"] < 0.5:  # Adjust threshold as needed
                raise ValueError(f"Tuning failed to find parameters above threshold. Best score: {best_params['combined_score']}")
                
            logger.info(f"Tuning complete. Best params: {best_params}")
            return best_params
            
        except Exception as e:
            logger.error(f"Hyperparameter tuning failed: {str(e)}")
            raise


    async def evaluate_with_params(self, model: str, params: Dict[str, Any], 
                              csv_path: str, valid_classes: List[str]) -> Dict[str, Any]:
        """Final evaluation with type enforcement"""
        try:
            if 'temperature' not in params:
                raise ValueError("Missing temperature parameter")
                
            temperature = params["temperature"]
            queries = self.ingest_csv(csv_path)
            
            if not queries:
                raise ValueError("No valid queries for final evaluation")
                
            model_responses = []
            
            for query in queries:
                entry = await self._query_model(
                    model,
                    query["question"],
                    0,  # instance
                    1,  # iteration
                    valid_classes,
                    temperature
                )
                
                response_with_metrics = {
                    "question": query["question"],
                    "ground_truth": query["ground_truth"],
                    "predicted_class": entry.predicted_class,
                    "confidence": float(entry.confidence),
                    "latency": float(entry.latency),
                    "correct": entry.predicted_class == query["ground_truth"]
                }
                model_responses.append(response_with_metrics)
            
            df = pd.DataFrame(model_responses)
            if df.empty:
                raise ValueError("No valid responses in final evaluation")
                
            # Enforce data types
            df['correct'] = df['correct'].astype(bool)
            df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.0)
            
            metrics = self.metrics.calculate_metrics_single_model(df, model)
            
            return {
                "metrics": metrics,
                "responses": model_responses,
                "temperature": temperature
            }
            
        except Exception as e:
            logger.error(f"Final evaluation failed: {str(e)}")
            raise

    async def run_pipeline(self, config: ModelConfig, csv_path: str, 
                      valid_classes: List[str]) -> Dict[str, Any]:
        """Main pipeline with enhanced validation"""
        if not valid_classes:
            raise ValueError("Valid classes list cannot be empty")
            
        # Step 1: Base evaluation
        evaluation_results = await self.evaluate_models(config, csv_path, valid_classes)
        
        # Step 2: Best model selection
        best_model = self.find_best_model(evaluation_results)
        
        # Step 3: Tuning
        best_params = None
        if config.enable_tuning:
            try:
                best_params = await self.tune_best_model(
                    best_model,
                    csv_path,
                    config,
                    valid_classes
                )
                
                # Step 4: Final evaluation
                if config.run_final_evaluation:
                    final_results = await self.evaluate_with_params(
                        best_model,
                        best_params,
                        csv_path,
                        valid_classes
                    )
                    evaluation_results["tuned_best_model"] = final_results
                    
            except Exception as e:
                logger.error(f"Tuning pipeline failed: {str(e)}")
                if config.continue_on_tuning_error:
                    logger.info("Continuing with base model results")
                else:
                    raise
        
        return {
            "model_evaluations": evaluation_results,
            "best_model": best_model,
            "best_params": best_params if config.enable_tuning else None
        }