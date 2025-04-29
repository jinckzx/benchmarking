
# import asyncio
# import os
# import pandas as pd
# from datetime import datetime
# from typing import List, Dict
# from ...config.models_sql import ModelConfig, LogEntry
# from ...database.database_sql import DatabaseHandlerSQL
# from ...utils.extractors import ResponseExtractor
# from ...utils.prompt_utils import read_system_prompt, read_iteration_prompt_sql
# from dotenv import load_dotenv
# from ...utils.logging import logger
# from ...metrics.metrics_sql import SQLMetrics
# from .hyperparameter_tuner import HyperparameterTuner
# from ..client_init import llm

# load_dotenv()
# SCHEMA_PATH = "D:\\data_sci\\benchmarking_tool\\dataset\\spider_data\\spider_data\\database\\{db_id}\\schema.sql"

# class SQLModelRunner:
#     def __init__(self):
#         self.client = llm
#         self.db_handler = DatabaseHandlerSQL()
#         self.extractor = ResponseExtractor()
#         self.system_prompt = read_system_prompt()
#         self.iteration_prompt_template = read_iteration_prompt_sql()
#         self.metrics = SQLMetrics()
#         self.hyperparameter_tuner = HyperparameterTuner()
        
#     def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
#         """Load and validate CSV input"""
#         df = pd.read_csv(csv_path)
#         required_columns = {"db_id", "question", "gold_sql"}  # Added gold_sql for evaluation
#         if not required_columns.issubset(df.columns):
#             missing = required_columns - set(df.columns)
#             raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
#         return df.to_dict(orient="records")

#     def get_schema(self, db_id: str) -> str:
#         """Fetch validated database schema"""
#         schema_file = SCHEMA_PATH.format(db_id=db_id)
#         if not os.path.exists(schema_file):
#             raise FileNotFoundError(f"Schema file not found: {schema_file}")
#         with open(schema_file, "r") as f:
#             return f.read()
            
#     async def _query_model(self, model: str, prompt: str, instance: int, 
#                       iteration: int, db_id: str, temperature: float = 0.2) -> LogEntry:
#         """Execute model query with specific temperature"""
#         start_time = datetime.now()
#         try:
#             context = self.get_schema(db_id)
#             messages = [
#                 {"role": "system", "content": self.system_prompt},
#                 {"role": "user", "content": self.iteration_prompt_template.format(
#                     context=context,
#                     prompt=prompt,
#                     model=model
#                 )}
#             ]
            
#             response = await self.client.chat(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature
#             )
            
#             content = response["content"]
#             logger.debug("Model output", 
#                       extra={'question': prompt, 'generated_sql': content, 'temperature': temperature})
            
#             extracted_sql = self.extractor.extract_sql(content)
            
#             entry = LogEntry(
#                 prompt=prompt,
#                 model=f"{model}-{instance}",
#                 response=extracted_sql,
#                 confidence=self.extractor.extract_confidence(content),
#                 latency=(datetime.now() - start_time).total_seconds(),
#                 iteration=iteration,
#                 intent=self.extractor.extract_intent(content),
#                 db_id=db_id,
#                 raw_response=content,
#                 temperature=temperature
#             )
            
#             # Log the response
#             self.db_handler.log_interaction(entry, temperature)
            
#             return entry
#         except Exception as e:
#             error_msg = f"{type(e).__name__}: {str(e)}"
#             logger.error("Query failed", 
#                     extra={'question': prompt, 'generated_sql': error_msg, 'temperature': temperature})
#             return LogEntry(
#                 prompt=prompt,
#                 model=f"{model}-{instance}",
#                 response=error_msg,
#                 confidence=0.0,
#                 latency=(datetime.now() - start_time).total_seconds(),
#                 iteration=iteration,
#                 intent="",
#                 db_id=db_id,
#                 error=error_msg,
#                 temperature=temperature
#             )
            
#     async def evaluate_models(self, config: ModelConfig, csv_path: str) -> Dict:
#         """Run and evaluate each model against gold standard"""
#         models_results = {}
#         queries = self.ingest_csv(csv_path)
        
#         try:
#             # Fix: Change from config.sql.models to config.models
#             for model_name in config.models:
#                 model_responses = []
                
#                 logger.info(f"Evaluating model: {model_name}")
                
#                 for query in queries:
#                     db_id = query["db_id"]
#                     prompt = query["question"]
#                     gold_sql = query["gold_sql"]
                    
#                     # Fix: Change from config.sql.base_temperature to config.base_temperature
#                     entry = await self._query_model(
#                         model_name, 
#                         prompt, 
#                         0,  # Single instance 
#                         0,  # Single iteration
#                         db_id, 
#                         config.base_temperature
#                     )
                    
#                     # Evaluate against gold standard
#                     eval_result = self.metrics.evaluate_query(
#                         entry.response, 
#                         gold_sql, 
#                         db_id
#                     )
                    
#                     response_with_metrics = {
#                         "question": prompt,
#                         "db_id": db_id,
#                         "generated_sql": entry.response,
#                         "gold_sql": gold_sql,
#                         "exact_match": eval_result["exact_match"],
#                         "execution_match": eval_result["execution_match"],
#                         "confidence": entry.confidence,
#                         "latency": entry.latency
#                     }
                    
#                     model_responses.append(response_with_metrics)
                    
#                 # Calculate overall metrics for this model
#                 df = pd.DataFrame(model_responses)
#                 metrics = self.metrics.compute_metrics(df)
                
#                 models_results[model_name] = {
#                     "metrics": metrics,
#                     "responses": model_responses
#                 }
                
#                 logger.info(f"Model {model_name} - Execution Match: {metrics['execution_match_rate']:.2f}%")
        
#         finally:
#             self.db_handler.close()
            
#         return models_results
    
#     def find_best_model(self, evaluation_results: Dict) -> str:
#         """Find the model with the best performance metrics"""
#         best_model = None
#         best_score = -1
        
#         for model_name, results in evaluation_results.items():
#             # Use execution match rate as the primary metric
#             score = results["metrics"]["execution_match_rate"]
            
#             if score > best_score:
#                 best_score = score
#                 best_model = model_name
        
#         logger.info(f"Best model identified: {best_model} with execution match rate: {best_score:.2f}%")
#         return best_model
    
#     async def evaluate_with_params(self, model_name: str, params: Dict, csv_path: str) -> Dict:
#         """Evaluate a model with specific parameters"""
#         logger.info(f"Running final evaluation for {model_name} with tuned parameters: {params}")
        
#         queries = self.ingest_csv(csv_path)
#         model_responses = []
        
#         for query in queries:
#             db_id = query["db_id"]
#             prompt = query["question"]
#             gold_sql = query["gold_sql"]
            
#             # Use the tuned temperature parameter from the best params
#             temperature = params.get("temperature", 0.2)
            
#             entry = await self._query_model(
#                 model_name, 
#                 prompt, 
#                 0,  # Single instance 
#                 0,  # Single iteration
#                 db_id, 
#                 temperature
#             )
            
#             # Evaluate against gold standard
#             eval_result = self.metrics.evaluate_query(
#                 entry.response, 
#                 gold_sql, 
#                 db_id
#             )
            
#             response_with_metrics = {
#                 "question": prompt,
#                 "db_id": db_id,
#                 "generated_sql": entry.response,
#                 "gold_sql": gold_sql,
#                 "exact_match": eval_result["exact_match"],
#                 "execution_match": eval_result["execution_match"],
#                 "confidence": entry.confidence,
#                 "latency": entry.latency
#             }
            
#             model_responses.append(response_with_metrics)
        
#         # Calculate overall metrics for this model with tuned parameters
#         df = pd.DataFrame(model_responses)
#         metrics = self.metrics.compute_metrics(df)
        
#         return {
#             "metrics": metrics,
#             "responses": model_responses
#         }

#     async def tune_best_model(self, model_name: str, csv_path: str, config: ModelConfig) -> Dict:
#         """Tune hyperparameters for the best model"""
#         logger.info(f"Starting hyperparameter tuning for model: {model_name}")
        
#         # Get a subset of queries for tuning
#         queries = self.ingest_csv(csv_path)
#         tuning_queries = queries[:config.tuning_sample_size]  # Fix: removed config.sql prefix
        
#         # Perform hyperparameter tuning
#         best_params = await self.hyperparameter_tuner.tune_model(
#             model_name,
#             tuning_queries,
#             self._query_model,
#             self.metrics,
#             {
#                 "temp_range": (config.min_temp, config.max_temp),  # Fix: removed config.base prefix
#                 "num_trials": config.num_trials  # Fix: removed config.base prefix
#             }
#         )
        
#         logger.info(f"Best parameters for {model_name}: {best_params}")
#         return best_params

#     async def run_pipeline(self, config: ModelConfig, csv_path: str) -> Dict:
#         """Main execution pipeline: evaluate, find best, tune"""
#         # Step 1: Evaluate all models with base settings
#         evaluation_results = await self.evaluate_models(config, csv_path)
        
#         # Step 2: Find the best model
#         best_model = self.find_best_model(evaluation_results)
        
#         # Step 3: Tune the best model
#         best_params = None
#         if config.enable_tuning:  # Fix: removed config.base prefix
#             best_params = await self.tune_best_model(
#                 best_model,
#                 csv_path,
#                 config
#             )
            
#             # Step 4: Evaluate best model with tuned parameters (optional)
#             if config.run_final_evaluation:  # Fix: removed config.sql prefix
#                 final_results = await self.evaluate_with_params(
#                     best_model, 
#                     best_params, 
#                     csv_path
#                 )
#                 evaluation_results["tuned_best_model"] = final_results
        
#         return {
#             "model_evaluations": evaluation_results,
#             "best_model": best_model,
#             "best_params": best_params if config.enable_tuning else None  # Fix: removed config.base prefix
#         }
import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from ...config.models_sql import ModelConfig, LogEntry
from ...database.database_sql import DatabaseHandlerSQL
from ...utils.extractors import ResponseExtractor
from ...utils.prompt_utils import read_system_prompt, read_iteration_prompt_sql
from dotenv import load_dotenv
from ...utils.logging import logger
from ...metrics.metrics_sql import SQLMetrics
from .hyperparameter_tuner import HyperparameterTuner
from ..client_init import llm

load_dotenv()
SCHEMA_PATH = "D:\\data_sci\\benchmarking_tool\\dataset\\spider_data\\spider_data\\database\\{db_id}\\schema.sql"

class SQLModelRunner:
    def __init__(self):
        self.client = llm
        self.db_handler = DatabaseHandlerSQL()
        self.extractor = ResponseExtractor()
        self.system_prompt = read_system_prompt()
        self.iteration_prompt_template = read_iteration_prompt_sql()
        self.metrics = SQLMetrics()
        self.hyperparameter_tuner = HyperparameterTuner()
        
    def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load and validate CSV input"""
        df = pd.read_csv(csv_path)
        required_columns = {"db_id", "question", "gold_sql"}  # Added gold_sql for evaluation
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
        return df.to_dict(orient="records")

    def get_schema(self, db_id: str) -> str:
        """Fetch validated database schema"""
        schema_file = SCHEMA_PATH.format(db_id=db_id)
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        with open(schema_file, "r") as f:
            return f.read()
            
    async def _query_model(self, model: str, prompt: str, instance: int, 
                      iteration: int, db_id: str, temperature: float = 0.2) -> LogEntry:
        """Execute model query with specific temperature"""
        start_time = datetime.now()
        try:
            context = self.get_schema(db_id)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.iteration_prompt_template.format(
                    context=context,
                    prompt=prompt,
                    model=model
                )}
            ]
            
            response = await self.client.chat(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            content = response["content"]
            logger.debug("Model output", 
                      extra={'question': prompt, 'generated_sql': content, 'temperature': temperature})
            
            extracted_sql = self.extractor.extract_sql(content)
            
            entry = LogEntry(
                prompt=prompt,
                model=f"{model}-{instance}",
                response=extracted_sql,
                confidence=self.extractor.extract_confidence(content),
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                intent=self.extractor.extract_intent(content),
                db_id=db_id,
                raw_response=content,
                temperature=temperature
            )
            
            # Log the response
            self.db_handler.log_interaction(entry, temperature)
            
            return entry
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error("Query failed", 
                    extra={'question': prompt, 'generated_sql': error_msg, 'temperature': temperature})
            return LogEntry(
                prompt=prompt,
                model=f"{model}-{instance}",
                response=error_msg,
                confidence=0.0,
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                intent="",
                db_id=db_id,
                error=error_msg,
                temperature=temperature
            )
            
    async def evaluate_models(self, config: ModelConfig, csv_path: str) -> Dict[str, Any]:
        """Run and evaluate each model against gold standard"""
        models_results = {}
        queries = self.ingest_csv(csv_path)
        
        try:
            for model_name in config.models:
                model_responses = []
                
                logger.info(f"Evaluating model: {model_name}")
                
                for query in queries:
                    db_id = query["db_id"]
                    prompt = query["question"]
                    gold_sql = query["gold_sql"]
                    
                    entry = await self._query_model(
                        model_name, 
                        prompt, 
                        0,  # Single instance 
                        0,  # Single iteration
                        db_id, 
                        config.base_temperature
                    )
                    
                    # Evaluate against gold standard
                    eval_result = self.metrics.evaluate_query(
                        entry.response, 
                        gold_sql, 
                        db_id
                    )
                    
                    response_with_metrics = {
                        "question": prompt,
                        "db_id": db_id,
                        "generated_sql": entry.response,
                        "gold_sql": gold_sql,
                        "exact_match": eval_result["exact_match"],
                        "execution_match": eval_result["execution_match"],
                        "confidence": entry.confidence,
                        "latency": entry.latency
                    }
                    
                    model_responses.append(response_with_metrics)
                
                # Calculate aggregate metrics
                df = pd.DataFrame(model_responses)
                metrics = self.metrics.compute_metrics(df)
                
                # Store results for this model
                models_results[model_name] = {
                    "metrics": metrics,
                    "responses": model_responses
                }
                
                logger.info(f"Model {model_name} evaluation complete. "
                         f"Execution match rate: {metrics['execution_match_rate']:.2f}%, "
                         f"Exact match rate: {metrics['exact_match_rate']:.2f}%")
            
            return models_results
                
        except Exception as e:
            logger.error(f"Error in model evaluation: {str(e)}")
            raise
            
    async def tune_best_model(self, model: str, csv_path: str, config: ModelConfig) -> Dict[str, Any]:
        """Tune hyperparameters for the best performing model using the already sampled dataset"""
        try:
            logger.info(f"Tuning hyperparameters for model: {model}")
            
            # Load the queries from the already sampled CSV
            queries = self.ingest_csv(csv_path)
            
            # Create tuning config
            tuning_config = {
                "temp_range": (config.min_temp, config.max_temp),
                "num_trials": config.num_trials
            }
            
            # Run hyperparameter tuning
            best_params = await self.hyperparameter_tuner.tune_model(
                model,
                queries,  # Use the already sampled dataset
                self._query_model,
                self.metrics,
                tuning_config
            )
            
            logger.info(f"Tuning complete. Best temperature: {best_params['temperature']}")
            return best_params
            
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {str(e)}")
            raise
    
    async def evaluate_with_params(self, model: str, params: Dict[str, Any], csv_path: str) -> Dict[str, Any]:
        """Run final evaluation with tuned parameters"""
        try:
            logger.info(f"Running final evaluation for {model} with temperature {params['temperature']}")
            
            # Load the queries from the provided CSV (which is already sampled)
            queries = self.ingest_csv(csv_path)
            temperature = params["temperature"]
            
            model_responses = []
            
            for query in queries:
                db_id = query["db_id"]
                prompt = query["question"]
                gold_sql = query["gold_sql"]
                
                entry = await self._query_model(
                    model, 
                    prompt, 
                    0,  # Single instance 
                    1,  # Marked as tuned iteration
                    db_id, 
                    temperature
                )
                
                # Evaluate against gold standard
                eval_result = self.metrics.evaluate_query(
                    entry.response, 
                    gold_sql, 
                    db_id
                )
                
                response_with_metrics = {
                    "question": prompt,
                    "db_id": db_id,
                    "generated_sql": entry.response,
                    "gold_sql": gold_sql,
                    "exact_match": eval_result["exact_match"],
                    "execution_match": eval_result["execution_match"],
                    "confidence": entry.confidence,
                    "latency": entry.latency
                }
                
                model_responses.append(response_with_metrics)
            
            # Calculate aggregate metrics
            df = pd.DataFrame(model_responses)
            metrics = self.metrics.compute_metrics(df)
            
            # Store results for tuned model
            tuned_results = {
                "metrics": metrics,
                "responses": model_responses,
                "temperature": temperature
            }
            
            logger.info(f"Tuned model evaluation complete. "
                     f"Execution match rate: {metrics['execution_match_rate']:.2f}%, "
                     f"Exact match rate: {metrics['exact_match_rate']:.2f}%")
                     
            return tuned_results
            
        except Exception as e:
            logger.error(f"Error in final evaluation: {str(e)}")
            raise