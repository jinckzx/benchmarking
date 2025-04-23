
    


# import asyncio
# import os
# import pandas as pd
# from datetime import datetime
# from typing import List, Dict
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from openai import AsyncOpenAI
# from ..config.models import ConsortiumConfig, LogEntry
# from ..database.database_sql import DatabaseHandlerSQL
# from .synthesis_sql import SynthesisHandlerSQL
# from ..utils.extractors import ResponseExtractor
# from ..utils.prompt_utils import read_iteration_prompt_sql, read_system_prompt
# from dotenv import load_dotenv
# from ..utils.logging import logger
# from ..database.spiderlog_db import SpiderDatasetLogger
# from .rag_processor import RAGConfig
# from .client_init import llm
# load_dotenv()

# SCHEMA_PATH = "D:\\inforigin_projects\\personal-llm\\dataset\\spider_data\\database\\{db_id}\\schema.sql"

# class ConsortiumRunnerSQL:
#     def __init__(self):
        
    
        
#         self.client = llm
#         self.db_handler = DatabaseHandlerSQL()
#         self.extractor = ResponseExtractor()
#         self.synthesis_db_handler = SpiderDatasetLogger()
#         self.synthesis_handler = SynthesisHandlerSQL(self.extractor)
#         self.system_prompt = read_system_prompt()
#         self.iteration_prompt_template = read_iteration_prompt_sql()
#     def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
#         """Load and validate CSV input"""
#         df = pd.read_csv(csv_path)
#         required_columns = {"db_id", "question"}
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
#                         iteration: int, db_id: str) -> LogEntry:
#         """Execute model query with comprehensive logging"""
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
#                 temperature=0.2
#             )
            
#             content = response["content"]
#             logger.debug("Raw model output", 
#                         extra={'question': prompt, 'generated_sql': content})
            
#             extracted_sql = self.extractor.extract_sql(content)
            
#             return LogEntry(
#                 prompt=prompt,
#                 model=f"{model}-{instance}",
#                 response=extracted_sql,  # SQL query goes here
#                 confidence=self.extractor.extract_confidence(content),
#                 latency=(datetime.now() - start_time).total_seconds(),
#                 iteration=iteration,
#                 intent=self.extractor.extract_intent(content),
#                 db_id=db_id,
#                 raw_response=content  # Store full response
#             )
#         except Exception as e:
#             error_msg = f"{type(e).__name__}: {str(e)}"
#             logger.error("Query failed", 
#                     extra={'question': prompt, 'generated_sql': error_msg})
#             return LogEntry(
#                 prompt=prompt,
#                 model=f"{model}-{instance}",
#                 response=error_msg,
#                 confidence=0.0,
#                 latency=(datetime.now() - start_time).total_seconds(),
#                 iteration=iteration,
#                 intent="",
#                 db_id=db_id,
#                 error=error_msg
#             )

#     async def run_consortium(self, config: ConsortiumConfig, csv_path: str) -> List[Dict]:
#         """Main execution flow with end-to-end logging"""
#         final_results = []
#         queries = self.ingest_csv(csv_path)

#         try:
#             for query in queries:
#                 db_id = query["db_id"]
#                 prompt = query["question"]
#                 responses = []
                
#                 for iteration in range(config.max_iterations):
#                     # Log iteration start with context
#                     logger.info(
#                         f"Iteration {iteration+1}/{config.max_iterations} for {db_id}",
#                         extra={'question': prompt, 'generated_sql': 'Iteration started'}
#                     )
                    
#                     # Execute parallel queries
#                     tasks = [
#                         self._query_model(model, prompt, instance, iteration, db_id)
#                         for model, count in config.models.items()
#                         for instance in range(count)
#                     ]
#                     results = await asyncio.gather(*tasks, return_exceptions=True)
                    
#                     # Process results with error handling
#                     valid_results = []
#                     for result in results:
#                         if isinstance(result, Exception):
#                             logger.error("Processing error", 
#                                        extra={'question': prompt, 'generated_sql': str(result)})
#                             continue
                            
#                         self.db_handler.log_interaction(result)
#                         result_dict = result.to_dict()
#                         responses.append(result_dict)
                        
#                         # Log individual SQL response
#                         logger.debug(
#                             "Model response",
#                             extra={
#                                 'question': prompt,
#                                 'generated_sql': result_dict.get('response', 'No SQL found')
#                             }
#                         )
#                         valid_results.append(result)
#                     # Perform synthesis with temperature tuning
#                     synthesis = await self.synthesis_handler.synthesize(
#                         prompt,
#                         valid_results,
#                         config.arbiter,
#                         iteration + 1,
#                         min_temp=config.min_temp,
#                         max_temp=config.max_temp,
#                         num_trials=config.num_trials
#                     )
#                     #####################################################################
#                     # # Perform synthesis with context
#                     # synthesis = await self.synthesis_handler.synthesize(
#                     #     prompt,
#                     #     valid_results,
#                     #     config.arbiter,
#                     #     iteration + 1
#                     # )
#                     ###################################################################
#                     # # Log synthesis results with full context
#                     # logger.info(
#                     #     f"Iteration {iteration+1} Synthesis Complete - Confidence: {synthesis['confidence']:.2f}",
#                     #     extra={
#                     #         'question': prompt,
#                     #         'generated_sql': synthesis.get('final_query', synthesis.get('response', 'N/A'))
#                     #     }
#                     # )                    
#                     # # Update logging with temperature info
#                     logger.info(
#                         f"Iteration {iteration+1} Best Synthesis - "
#                         f"Temp: {synthesis['best']['temperature']:.2f}, "
#                         f"Confidence: {synthesis['best']['confidence']:.2f}",
#                         extra={
#                             'question': prompt,
#                             'generated_sql': synthesis['best']['final_query']
#                         }
#                     )
#                     final_result = {
#                         **synthesis,
#                         "raw_responses": responses,
#                         "iterations": iteration + 1,
#                         "intent": synthesis['best']['intent'],
#                         "db_id": db_id,
#                         "question": prompt  
#                     }
#                     final_results.append(final_result)
#                     # Build final result package
#                     # final_result = {
#                     #     "synthesis": synthesis,
#                     #     "raw_responses": responses,
#                     #     "iterations": iteration + 1,
#                     #     "intent": max(
#                     #         (r.intent for r in valid_results),
#                     #         key=lambda x: list(r.intent for r in valid_results).count(x)
#                     #     ) if valid_results else "unknown",
#                     #     "db_id": db_id,
#                     #     "question": prompt  
#                     # }
#                     # final_results.append(final_result)
#                     # Check early exit conditions
#                     if (synthesis['best']['confidence'] >= config.confidence_threshold 
#                         and iteration >= config.min_iterations - 1):
#                         break
#                     # # Check early exit conditions
#                     # if (synthesis['confidence'] >= config.confidence_threshold 
#                     #     and iteration >= config.min_iterations - 1):
#                     #     break

#         finally:
#             self.db_handler.close()
#             self.synthesis_db_handler.close()
            
#         return final_results
import asyncio
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from ..config.models import ConsortiumConfig, LogEntry
from ..database.database_sql import DatabaseHandlerSQL
from .synthesis_sql import SynthesisHandlerSQL
from ..utils.extractors import ResponseExtractor
from ..utils.prompt_utils import read_iteration_prompt_sql, read_system_prompt
from dotenv import load_dotenv
from ..utils.logging import logger
from ..database.spiderlog_db import SpiderDatasetLogger
from .model_temperature_tuner import ModelTemperatureTuner
from .client_init import llm

load_dotenv()

SCHEMA_PATH = "D:\\inforigin_projects\\personal-llm\\dataset\\spider_data\\database\\{db_id}\\schema.sql"

class ConsortiumRunnerSQL:
    def __init__(self):
        self.client = llm
        self.db_handler = DatabaseHandlerSQL()
        self.extractor = ResponseExtractor()
        self.synthesis_db_handler = SpiderDatasetLogger()
        self.synthesis_handler = SynthesisHandlerSQL(self.extractor)
        self.model_tuner = ModelTemperatureTuner()
        self.system_prompt = read_system_prompt()
        self.iteration_prompt_template = read_iteration_prompt_sql()

    def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load and validate CSV input"""
        df = pd.read_csv(csv_path)
        required_columns = {"db_id", "question"}
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
        """Execute model query with temperature tuning"""
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
            logger.debug("Raw model output with temperature", 
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
                temperature=temperature  # Add temperature to LogEntry
            )
            
            # Log with temperature
            self.db_handler.log_interaction(entry, temperature)
            
            # Log as a temperature trial
            self.db_handler.log_model_temperature_trial(entry, temperature)
            
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
                temperature=temperature  # Add temperature to error LogEntry
            )

    # Update the run_consortium method in core/runner_sql.py
    async def run_consortium(self, config: ConsortiumConfig, csv_path: str) -> List[Dict]:
        """Main execution flow with temperature tuning for all models"""
        final_results = []
        queries = self.ingest_csv(csv_path)

        try:
            for query in queries:
                db_id = query["db_id"]
                prompt = query["question"]
                responses = []
                
                for iteration in range(config.max_iterations):
                    # Log iteration start with context
                    logger.info(
                        f"Iteration {iteration+1}/{config.max_iterations} for {db_id}",
                        extra={'question': prompt, 'generated_sql': 'Iteration started'}
                    )
                    
                    # Generate model temperatures if enabled
                    if getattr(config, 'enable_model_temp_tuning', False):
                        # Generate temperature ranges for models
                        model_temperatures = self.model_tuner.generate_temperatures(
                            config.model_min_temp, 
                            config.model_max_temp, 
                            config.model_num_trials
                        )
                        
                        # Assign temperatures to model instances
                        model_temp_mapping = self.model_tuner.assign_temperatures_to_models(
                            config.models,
                            model_temperatures
                        )
                        
                        # Log temperature assignments
                        logger.info(
                            f"Model temperature assignments for iteration {iteration+1}",
                            extra={'temp_mapping': str(model_temp_mapping)}
                        )
                        
                        # Execute parallel queries with assigned temperatures
                        tasks = []
                        for model, temps in model_temp_mapping.items():
                            for instance, temp in enumerate(temps):
                                tasks.append(
                                    self._query_model(model, prompt, instance, iteration, db_id, temp)
                                )
                    else:
                        # Standard execution without model temperature tuning
                        tasks = [
                            self._query_model(model, prompt, instance, iteration, db_id)
                            for model, count in config.models.items()
                            for instance in range(count)
                        ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results with error handling
                    valid_results = []
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error("Processing error", 
                                    extra={'question': prompt, 'generated_sql': str(result)})
                            continue
                            
                        result_dict = result.to_dict()
                            # Make sure temperature is included
                        if not "temperature" in result_dict and hasattr(result, "temperature"):
                            result_dict["temperature"] = result.temperature
                        responses.append(result_dict)
                        
                        # Log individual SQL response
                        logger.debug(
                            "Model response",
                            extra={
                                'question': prompt,
                                'generated_sql': result_dict.get('response', 'No SQL found'),
                                'temperature': result_dict.get('temperature', 'N/A')
                            }
                        )
                        valid_results.append(result)
                    
                    # Perform synthesis with temperature tuning
                    synthesis = await self.synthesis_handler.synthesize(
                        prompt,
                        valid_results,
                        config.arbiter,
                        iteration + 1,
                        min_temp=config.min_temp,
                        max_temp=config.max_temp,
                        num_trials=config.num_trials
                    )
                    
                    # Log synthesis results
                    logger.info(
                        f"Iteration {iteration+1} Best Synthesis - "
                        f"Temp: {synthesis['best']['temperature']:.2f}, "
                        f"Confidence: {synthesis['best']['confidence']:.2f}",
                        extra={
                            'question': prompt,
                            'generated_sql': synthesis['best']['final_query']
                        }
                    )
                    
                    # Build final result package
                    final_result = {
                        **synthesis,
                        "raw_responses": responses,
                        "iterations": iteration + 1,
                        "intent": synthesis['best']['intent'],
                        "db_id": db_id,
                        "question": prompt  
                    }
                    final_results.append(final_result)
                    
                    # Check early exit conditions
                    if (synthesis['best']['confidence'] >= config.confidence_threshold 
                        and iteration >= config.min_iterations - 1):
                        break

        finally:
            self.db_handler.close()
            self.synthesis_db_handler.close()
            
        return final_results