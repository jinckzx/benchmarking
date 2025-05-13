import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
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

load_dotenv()
SCHEMA_PATH = "D:\\data_sci\\benchmarking_tool\\dataset\\spider_data\\spider_data\\database\\{db_id}\\schema.sql"

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
            
            self.db_handler.log_interaction(entry, temperature)
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
                temperature=temperature
            )

    async def _process_single_query(self, model_name: str, query: Dict, temperature: float) -> Optional[Dict]:
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
                temperature
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
                
                metric_results = {"execution_match": False, "exact_match": False}  # Default values
                for metric in self.selected_metrics:
                    try:
                        required_fields = metric.runtime_requires
                        if all(field in metric_inputs for field in required_fields):
                            metric_result = metric.calculate(
                                **{k: metric_inputs[k] for k in required_fields}
                            )
                            metric_results.update(metric_result)
                    except Exception as e:
                        logger.error(f"Metric error: {str(e)}")

                
                result.update(metric_results)

            return result

        except KeyError as ke:
            logger.error(f"Missing required field in query: {str(ke)}")
            return {**result_template, "generated_sql": f"KeyError: {str(ke)}"}
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {**result_template, "generated_sql": f"Error: {str(e)}"}

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

    # Add this method to fix compatibility with hyperparameter_tuner
    def evaluate_query(self, generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
        """Evaluate a single query against the selected metrics"""
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
                
                # Create all query tasks for this model
                query_tasks = [
                    self._process_single_query(model_name, query, config.base_temperature)
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

    async def tune_best_model(self, model: str, csv_path: str, config: ModelConfig) -> Dict[str, Any]:
        """Tune hyperparameters using selected metrics"""
        try:
            logger.info(f"Tuning hyperparameters for {model}")
            queries = self.ingest_csv(csv_path)
            
            # Configure tuning based on selected metrics
            primary_metric = self.selected_metrics[0].name
            tuning_config = {
                "temp_range": (config.min_temp, config.max_temp),
                "num_trials": config.num_trials,
                "primary_metric": f"{primary_metric}_rate"
            }
            
            best_params = await self.hyperparameter_tuner.tune_model(
                model,
                queries,
                self._query_model,
                self,  # Pass self as metrics_func to access evaluate_query
                tuning_config
            )
            
            logger.info(f"Tuning complete. Best params: {best_params}")
            return best_params
            
        except Exception as e:
            logger.error(f"Tuning failed: {str(e)}")
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