# import asyncio
# import os
# import pandas as pd
# from datetime import datetime
# from typing import List, Dict, Any, Optional
# from ...config.models_sql import ModelConfig, LogEntry
# from ...database.database_sql import DatabaseHandlerSQL
# from ...metrics.base_metrics import BaseMetric
# from ...metrics.registry import MetricRegistry
# from ...utils.extractors import ResponseExtractor
# from ...utils.prompt_utils import read_system_prompt, read_iteration_prompt_sql
# from dotenv import load_dotenv
# from ...utils.logging import logger
# from .hyperparameter_tuner import HyperparameterTuner
# from ..client_init import llm

# load_dotenv()
# SCHEMA_PATH = "D:\\data_sci\\benchmarking_tool\\dataset\\spider_data\\spider_data\\database\\{db_id}\\schema.sql"

# class SQLModelRunner:
#     def __init__(self, selected_metrics: List[str]):
#         self.client = llm
#         self.db_handler = DatabaseHandlerSQL()
#         self.extractor = ResponseExtractor()
#         self.system_prompt = read_system_prompt()
#         self.iteration_prompt_template = read_iteration_prompt_sql()
#         self.hyperparameter_tuner = HyperparameterTuner()
        
#         # Metrics configuration
#         self.metric_registry = MetricRegistry()
#         self.selected_metrics = self._validate_metrics(selected_metrics)
#         logger.info(f"Initialized with metrics: {[m.name for m in self.selected_metrics]}")

#     def _validate_metrics(self, metric_names: List[str]) -> List[BaseMetric]:
#         """Validate and load requested metrics"""
#         sql_metrics = self.metric_registry.get_metrics_for_task("sql")
#         valid_metrics = []
        
#         for name in metric_names:
#             if name in sql_metrics:
#                 valid_metrics.append(sql_metrics[name])
#             else:
#                 logger.warning(f"Ignoring invalid metric: {name}")
        
#         if not valid_metrics:
#             raise ValueError("No valid metrics selected")
            
#         return valid_metrics

#     def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
#         """Load and validate CSV input"""
#         df = pd.read_csv(csv_path)
#         required_columns = {"db_id", "question"}
        
#         # Add metric-specific CSV requirements
#         for metric in self.selected_metrics:
#             required_columns.update(metric.csv_requires)
            
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
            
#             self.db_handler.log_interaction(entry, temperature)
#             return entry
            
#         except Exception as e:
#             error_msg = f"{type(e).__name__}: {str(e)}"
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

#     async def _process_single_query(self, model_name: str, query: Dict, temperature: float) -> Optional[Dict]:
#         """Process individual query with error handling"""
#         result_template = {
#             "question": query["question"],
#             "db_id": query["db_id"],
#             "generated_sql": "",
#             "gold_sql": query.get("gold_sql", ""),
#             "confidence": 0.0,
#             "latency": 0.0
#         }
        
#         try:
#             # Generate SQL response
#             entry = await self._query_model(
#                 model_name, 
#                 query["question"], 
#                 0,  # instance
#                 0,  # iteration
#                 query["db_id"], 
#                 temperature
#             )
            
#             # Prepare base result
#             result = {
#                 **result_template,
#                 "generated_sql": entry.response,
#                 "confidence": entry.confidence,
#                 "latency": entry.latency
#             }

#             # Calculate metrics only if we have a valid response
#             if not entry.error:
#                 metric_inputs = {
#                     "gold_sql": query.get("gold_sql", ""),
#                     "db_id": query["db_id"],
#                     "generated_sql": entry.response
#                 }
                
#                 metric_results = {"execution_match": False, "exact_match": False}  # Default values
#                 for metric in self.selected_metrics:
#                     try:
#                         required_fields = metric.runtime_requires
#                         if all(field in metric_inputs for field in required_fields):
#                             metric_result = metric.calculate(
#                                 **{k: metric_inputs[k] for k in required_fields}
#                             )
#                             metric_results.update(metric_result)
#                     except Exception as e:
#                         logger.error(f"Metric error: {str(e)}")

                
#                 result.update(metric_results)

#             return result

#         except KeyError as ke:
#             logger.error(f"Missing required field in query: {str(ke)}")
#             return {**result_template, "generated_sql": f"KeyError: {str(ke)}"}
            
#         except Exception as e:
#             logger.error(f"Query processing failed: {str(e)}")
#             return {**result_template, "generated_sql": f"Error: {str(e)}"}

#     def compute_metrics(self, results_df: pd.DataFrame) -> Dict[str, Any]:
#         """Compute aggregate metrics from results"""
#         metrics = {"total": len(results_df)}
        
#         for metric in self.selected_metrics:
#             col_name = metric.name
#             if col_name in results_df.columns:
#                 # Handle boolean success metrics
#                 if results_df[col_name].dtype == bool:
#                     success_count = results_df[col_name].sum()
#                     metrics[f"{col_name}_count"] = success_count
#                     metrics[f"{col_name}_rate"] = (success_count / len(results_df)) * 100
#                 # Handle complex metric objects
#                 elif isinstance(results_df[col_name].iloc[0], dict):
#                     metrics[col_name] = results_df[col_name].tolist()
#                 # Handle numerical metrics
#                 else:
#                     metrics[col_name] = results_df[col_name].mean()
                    
#         return metrics

#     # Add this method to fix compatibility with hyperparameter_tuner
#     def evaluate_query(self, generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
#         """Evaluate a single query against the selected metrics"""
#         metric_inputs = {
#             "gold_sql": gold_sql,
#             "db_id": db_id,
#             "generated_sql": generated_sql
#         }
        
#         metric_results = {}
#         for metric in self.selected_metrics:
#             try:
#                 # Get required fields for this metric
#                 required_fields = metric.runtime_requires
#                 if all(field in metric_inputs for field in required_fields):
#                     metric_result = metric.calculate(
#                         **{k: metric_inputs[k] for k in required_fields}
#                     )
#                     metric_results.update(metric_result)
#             except Exception as metric_error:
#                 logger.error(f"Metric {metric.name} failed: {str(metric_error)}")
                
#         return metric_results

#     async def evaluate_models(self, config: ModelConfig, csv_path: str) -> Dict[str, Any]:
#         """Run and evaluate models in parallel with selected metrics"""
#         models_results = {}
#         queries = self.ingest_csv(csv_path)
        
#         async def evaluate_single_model(model_name: str):
#             """Process one model with parallel query execution"""
#             try:
#                 logger.info(f"Starting evaluation for {model_name}")
                
#                 # Create all query tasks for this model
#                 query_tasks = [
#                     self._process_single_query(model_name, query, config.base_temperature)
#                     for query in queries
#                 ]
                
#                 # Run all queries concurrently
#                 query_results = await asyncio.gather(*query_tasks)
#                 valid_results = [r for r in query_results if r is not None]
                
#                 # Calculate metrics
#                 df = pd.DataFrame(valid_results)
#                 metrics = self.compute_metrics(df) if not df.empty else {"total": 0}
                
#                 logger.info(f"Model {model_name} evaluation complete")
#                 return (model_name, metrics, valid_results)
            
#             except Exception as e:
#                 logger.error(f"Model {model_name} evaluation failed: {str(e)}")
#                 return (model_name, {"error": str(e), "total": 0}, [])

#         # Run all model evaluations concurrently
#         model_tasks = [evaluate_single_model(model) for model in config.models]
#         results = await asyncio.gather(*model_tasks)
        
#         # Organize results
#         for model_name, metrics, responses in results:
#             models_results[model_name] = {
#                 "metrics": metrics,
#                 "responses": responses
#             }
            
#         return models_results

#     async def tune_best_model(self, model: str, csv_path: str, config: ModelConfig) -> Dict[str, Any]:
#         """Tune hyperparameters using selected metrics"""
#         try:
#             logger.info(f"Tuning hyperparameters for {model}")
#             queries = self.ingest_csv(csv_path)
            
#             # Configure tuning based on selected metrics
#             primary_metric = self.selected_metrics[0].name
#             tuning_config = {
#                 "temp_range": (config.min_temp, config.max_temp),
#                 "num_trials": config.num_trials,
#                 "primary_metric": f"{primary_metric}_rate"
#             }
            
#             best_params = await self.hyperparameter_tuner.tune_model(
#                 model,
#                 queries,
#                 self._query_model,
#                 self,  # Pass self as metrics_func to access evaluate_query
#                 tuning_config
#             )
            
#             logger.info(f"Tuning complete. Best params: {best_params}")
#             return best_params
            
#         except Exception as e:
#             logger.error(f"Tuning failed: {str(e)}")
#             raise

#     async def evaluate_with_params(self, model: str, params: Dict[str, Any], csv_path: str) -> Dict[str, Any]:
#         """Final evaluation with tuned parameters"""
#         try:
#             queries = self.ingest_csv(csv_path)
#             model_responses = []
            
#             for query in queries:
#                 result = await self._process_single_query(
#                     model,
#                     query,
#                     params["temperature"]
#                 )
#                 if result:
#                     model_responses.append(result)
            
#             df = pd.DataFrame(model_responses)
#             metrics = self.compute_metrics(df)
            
#             return {
#                 "metrics": metrics,
#                 "responses": model_responses,
#                 "temperature": params["temperature"]
#             }
            
#         except Exception as e:
#             logger.error(f"Final evaluation failed: {str(e)}")
#             
import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Awaitable
from ...config.models_sql import ModelConfig, LogEntry
from ...database.database_sql import DatabaseHandlerSQL
from ...metrics.base_metrics import BaseMetric
from ...metrics.registry import MetricRegistry
from ...utils.extractors import ResponseExtractor
from ...utils.prompt_utils import read_system_prompt, read_iteration_prompt_sql
from dotenv import load_dotenv
from ...utils.logging import logger
from .hyperparameter_tuner import HyperparameterTuner
from ..client_init import llm
import inspect

load_dotenv()
# SCHEMA_PATH = "D:\\data_sci\\benchmarking_tool\\dataset\\spider_data\\spider_data\\database\\{db_id}\\schema.sql"

SCHEMA_PATH = "C:/Users/NikhilJain/OneDrive - Info Origin Technologies Pvt Ltd/Desktop/Info Origin/LLM_Benchmarking/04_updated/benchmarking_tool/dataset/spider_data/spider_data/database/{db_id}/schema.sql"

class SQLModelRunner:
    def __init__(self, selected_metrics: List[str]):
        self.client = llm
        self.db_handler = DatabaseHandlerSQL()
        self.extractor = ResponseExtractor()
        self.system_prompt = read_system_prompt()
        self.iteration_prompt_template = read_iteration_prompt_sql()
        self.hyperparameter_tuner = HyperparameterTuner()
        
        # Metrics configuration
        self.metric_registry = MetricRegistry()
        self.selected_metrics = self._validate_metrics(selected_metrics)
        logger.info(f"Initialized with metrics: {[m.name for m in self.selected_metrics]}")

    def _validate_metrics(self, metric_names: List[str]) -> List[BaseMetric]:
        """Validate and load requested metrics"""
        sql_metrics = self.metric_registry.get_metrics_for_task("sql")
        valid_metrics = []
        
        for name in metric_names:
            if name in sql_metrics:
                valid_metrics.append(sql_metrics[name])
            else:
                logger.warning(f"Ignoring invalid metric: {name}")
        
        if not valid_metrics:
            raise ValueError("No valid metrics selected")
            
        return valid_metrics

    def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load and validate CSV input"""
        df = pd.read_csv(csv_path)
        required_columns = {"db_id", "question"}
        
        # Add metric-specific CSV requirements
        for metric in self.selected_metrics:
            required_columns.update(metric.csv_requires)
            
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
                      iteration: int, db_id: str, params: Dict = None) -> LogEntry:
        """Execute model query with specific temperature"""
        if params is None:
            params = {
                "temperature": 0.2,
                "top_p": 1.0,
                "max_tokens": 1024,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": None,
                "tool_choice": None,
                "use_cache": True
            }

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
                temperature=params["temperature"],
                top_p=params["top_p"],
                max_tokens=params["max_tokens"],
                frequency_penalty=params["frequency_penalty"],
                presence_penalty=params["presence_penalty"],
                stop=params["stop"],
                tool_choice=params["tool_choice"],
                use_cache=params["use_cache"]
            )
            
            content = response["content"]
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
                temperature=params["temperature"]
            )
            
            self.db_handler.log_interaction(entry)
            return entry
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
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
                temperature=params["temperature"]
            )

    async def _process_single_query(self, model_name: str, query: Dict, params: Dict) -> Optional[Dict]:
        """Process individual query with error handling"""
        result_template = {
            "question": query["question"],
            "db_id": query["db_id"],
            "generated_sql": "",
            "gold_sql": query.get("gold_sql", ""),
            "confidence": 0.0,
            "latency": 0.0
        }
        
        try:
            # Generate SQL response
            entry = await self._query_model(
                model_name, 
                query["question"], 
                0,  # instance
                0,  # iteration
                query["db_id"], 
                params
            )
            
            # Prepare base result
            result = {
                **result_template,
                "generated_sql": entry.response,
                "confidence": entry.confidence,
                "latency": entry.latency
            }

            # Calculate metrics only if we have a valid response
            if not entry.error:
                metric_inputs = {
                    "gold_sql": query.get("gold_sql", ""),
                    "db_id": query["db_id"],
                    "generated_sql": entry.response
                }
                
                # Create a dict to collect LLM-based metric calls that need to be awaited
                llm_metric_tasks = {}
                
                # Process all metrics - handle both LLM and non-LLM metrics
                for metric in self.selected_metrics:
                    try:
                        required_fields = metric.runtime_requires
                        if all(field in metric_inputs for field in required_fields):
                            # Check if metric requires LLM and has an async calculate method
                            if hasattr(metric, 'requires_llm') and metric.requires_llm and hasattr(metric, 'calculate_async'):
                                # Store the async task to await later
                                filtered_inputs = {k: metric_inputs[k] for k in required_fields}
                                llm_metric_tasks[metric.name] = metric.calculate_async(**filtered_inputs)
                            else:
                                # Process non-LLM metrics synchronously
                                metric_result = metric.calculate(
                                    **{k: metric_inputs[k] for k in required_fields}
                                )
                                result.update(metric_result)
                    except Exception as e:
                        logger.error(f"Metric error: {str(e)}")

                # Now await all LLM metric tasks if any
                if llm_metric_tasks:
                    llm_results = await asyncio.gather(*llm_metric_tasks.values(), return_exceptions=True)
                    
                    # Add LLM results to the result dict
                    for i, metric_name in enumerate(llm_metric_tasks.keys()):
                        if isinstance(llm_results[i], Exception):
                            logger.error(f"LLM metric {metric_name} failed: {str(llm_results[i])}")
                        else:
                            result.update(llm_results[i])

            return result

        except KeyError as ke:
            logger.error(f"Missing required field in query: {str(ke)}")
            return {**result_template, "generated_sql": f"KeyError: {str(ke)}"}
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {**result_template, "generated_sql": f"Error: {str(e)}"}

    # FIXED: Make evaluate_query as an instance method, not a callable function
    
    
    async def evaluate_query_async(self, generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
        """Async version of evaluate_query that handles LLM-based metrics"""
        metric_inputs = {
            "gold_sql": gold_sql,
            "db_id": db_id, 
            "generated_sql": generated_sql
        }
        
        metric_results = {}
        llm_metric_tasks = {}
        
        # Process metrics - separate LLM and non-LLM metrics
        for metric in self.selected_metrics:
            try:
                required_fields = metric.runtime_requires
                if all(field in metric_inputs for field in required_fields):
                    filtered_inputs = {k: metric_inputs[k] for k in required_fields}
                    
                    # Check if metric requires LLM
                    if hasattr(metric, 'requires_llm') and metric.requires_llm and hasattr(metric, 'calculate_async'):
                        llm_metric_tasks[metric.name] = metric.calculate_async(**filtered_inputs)
                    else:
                        # Process non-LLM metrics synchronously
                        # For hyperparameter tuning, always include at least one boolean success metric
                        result = metric.calculate(**filtered_inputs)
                        metric_results.update(result)
            except Exception as e:
                logger.error(f"Metric {metric.name} failed: {str(e)}")
        
        # Ensure we have at least a default execution_match result if none provided
        if "execution_match" not in metric_results:
            metric_results["execution_match"] = False
        
        # Await LLM-based metrics if any
        if llm_metric_tasks:
            llm_results = await asyncio.gather(*llm_metric_tasks.values(), return_exceptions=True)
            
            # Add LLM results to the result dict
            for i, metric_name in enumerate(llm_metric_tasks.keys()):
                if isinstance(llm_results[i], Exception):
                    logger.error(f"LLM metric {metric_name} failed: {str(llm_results[i])}")
                else:
                    metric_results.update(llm_results[i])
        
        return metric_results
    

    # Keep the original evaluate_query for backward compatibility
    def evaluate_query(self, generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
        """Evaluate a single query against the selected metrics (sync version)"""
        metric_inputs = {
            "gold_sql": gold_sql,
            "db_id": db_id,
            "generated_sql": generated_sql
        }
        
        metric_results = {}
        for metric in self.selected_metrics:
            try:
                # Get required fields for this metric
                required_fields = metric.runtime_requires
                if all(field in metric_inputs for field in required_fields):
                    # Use only synchronous calculate method for compatibility
                    metric_result = metric.calculate(
                        **{k: metric_inputs[k] for k in required_fields}
                    )
                    metric_results.update(metric_result)
            except Exception as metric_error:
                logger.error(f"Metric {metric.name} failed: {str(metric_error)}")
                
        return metric_results

    async def evaluate_models(self, config: ModelConfig, csv_path: str) -> Dict[str, Any]:
        """Run and evaluate models in parallel with selected metrics"""
        models_results = {}
        queries = self.ingest_csv(csv_path)
        
        async def evaluate_single_model(model_name: str):
            """Process one model with parallel query execution"""
            try:
                logger.info(f"Starting evaluation for {model_name}")

                # Get model-specific parameters
                model_params = config.get_model_params(model_name)
                
                # Create all query tasks for this model
                query_tasks = [
                    self._process_single_query(model_name, query, model_params)
                    for query in queries
                ]
                
                # Run all queries concurrently
                query_results = await asyncio.gather(*query_tasks)
                valid_results = [r for r in query_results if r is not None]
                
                # Calculate metrics
                df = pd.DataFrame(valid_results)
                metrics = self.compute_metrics(df) if not df.empty else {"total": 0}
                
                logger.info(f"Model {model_name} evaluation complete")
                return (model_name, metrics, valid_results)
            
            except Exception as e:
                logger.error(f"Model {model_name} evaluation failed: {str(e)}")
                return (model_name, {"error": str(e), "total": 0}, [])

        # Run all model evaluations concurrently
        model_tasks = [evaluate_single_model(model) for model in config.models]
        results = await asyncio.gather(*model_tasks)
        
        # Organize results
        for model_name, metrics, responses in results:
            models_results[model_name] = {
                "metrics": metrics,
                "responses": responses
            }
            
        return models_results

    # FIXED: Update hyperparameter tuning to use bound methods instead of functions
    # Updated tune_best_model method in SQLModelRunner
    
    async def tune_best_model(self, model: str, csv_path: str, config: ModelConfig) -> Dict[str, Any]:
        """Tune hyperparameters using selected metrics"""
        try:
            logger.info(f"Tuning hyperparameters for {model}")
            queries = self.ingest_csv(csv_path)
            
            # Configure tuning based on selected metrics
            primary_metric = self.selected_metrics[0].name
            
            # If primary metric is not a boolean or rate, default to execution_match
            if not any(metric.name == primary_metric and hasattr(metric, 'is_boolean_success') 
                    for metric in self.selected_metrics):
                logger.info(f"Primary metric {primary_metric} is not a boolean success metric, defaulting to execution_match")
                primary_metric = "execution_match"
                
            tuning_config = {
                "temp_range": (config.min_temp, config.max_temp),
                "num_trials": config.num_trials,
                "primary_metric": f"{primary_metric}_rate"
            }
            
            # When passing the evaluate_query_async method to tuner, create a simple wrapper
            # that binds it to self and ensures proper parameter passing
            async def evaluate_query_wrapper(generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
                return await self.evaluate_query_async(generated_sql, gold_sql, db_id)
            
            best_params = await self.hyperparameter_tuner.tune_model(
                model,
                queries,
                self._query_model,  # This is a bound method
                evaluate_query_wrapper,  # This wraps the bound method properly
                tuning_config,
                config.get_model_params(model)
            )
            
            logger.info(f"Tuning complete. Best params: {best_params}")
            return best_params
            
        except Exception as e:
            logger.error(f"Tuning failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    

    async def evaluate_with_params(self, model: str, params: Dict[str, Any], csv_path: str) -> Dict[str, Any]:
        """Final evaluation with tuned parameters"""
        try:
            queries = self.ingest_csv(csv_path)
            model_responses = []
            
            for query in queries:
                result = await self._process_single_query(
                    model,
                    query,
                    params["temperature"]
                )
                if result:
                    model_responses.append(result)
            
            df = pd.DataFrame(model_responses)
            metrics = self.compute_metrics(df)
            
            return {
                "metrics": metrics,
                "responses": model_responses,
                "temperature": params["temperature"]
            }
            
        except Exception as e:
            logger.error(f"Final evaluation failed: {str(e)}")
            raise

    def compute_metrics(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Compute aggregate metrics from results"""
        metrics = {"total": len(results_df)}
        
        for metric in self.selected_metrics:
            col_name = metric.name
            if col_name in results_df.columns:
                # Handle boolean success metrics
                if results_df[col_name].dtype == bool:
                    success_count = results_df[col_name].sum()
                    metrics[f"{col_name}_count"] = success_count
                    metrics[f"{col_name}_rate"] = (success_count / len(results_df)) * 100
                # Handle complex metric objects
                elif isinstance(results_df[col_name].iloc[0], dict):
                    metrics[col_name] = results_df[col_name].tolist()
                # Handle numerical metrics
                else:
                    metrics[col_name] = results_df[col_name].mean()
                    
        return metrics