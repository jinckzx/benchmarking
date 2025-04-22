import asyncio
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from ..config.models import ConsortiumConfig, LogEntry
from ..database.database_class import DatabaseHandlerClass
from .synthesis_class import SynthesisHandlerClass
from ..utils.extractors import ResponseExtractor
from ..utils.prompt_utils import read_iteration_prompt_class, read_system_prompt
from ..utils.logging import logger
from ..database.synthesis_class_db import ClassificationSynthesisLogger
from .client_init import llm
from .metrics_class import ClassificationMetricsHandler

class ConsortiumRunnerClass:
    def __init__(self):
        self.client = llm
        self.metrics_handler = ClassificationMetricsHandler()
        self.db_handler = DatabaseHandlerClass()
        self.extractor = ResponseExtractor()
        self.synthesis_db_handler = ClassificationSynthesisLogger()
        self.synthesis_handler = SynthesisHandlerClass(self.extractor)
        self.system_prompt = read_system_prompt()
        self.iteration_prompt_template = read_iteration_prompt_class()
        
    def ingest_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """Load and validate CSV input for classification"""
        df = pd.read_csv(csv_path)
        required_columns = {"question"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
        return df.to_dict(orient="records")

    async def _query_model(self, model: str, question: str, available_classes: List[str], 
                        instance: int, iteration: int, true_class: Optional[str] = None) -> LogEntry:
        """Execute model query with comprehensive logging"""
        start_time = datetime.now()
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.iteration_prompt_template.format(
                    classes=", ".join(available_classes),
                    question=question,
                    model=model
                )}
            ]
            
            response = await self.client.chat(
                model=model,
                messages=messages,
                temperature=0.2
            )
            
            content = response["content"]
            logger.debug("Raw model output", 
                        extra={'question': question, 'predicted_class': self.extractor.extract_class(content)})
            
            return LogEntry(
                question=question,
                model=f"{model}-{instance}",
                response=self.extractor.extract_class(content),  
                predicted_class=self.extractor.extract_class(content),
                confidence=self.extractor.extract_confidence(content),
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                reasoning=self.extractor.extract_reasoning(content),
                raw_response=content  # Store the full raw response
            )
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error("Query failed", 
                        extra={'question': question, 'predicted_class': error_msg})
            return LogEntry(
                question=question,
                model=f"{model}-{instance}",
                predicted_class="ERROR",
                confidence=0.0,
                latency=(datetime.now() - start_time).total_seconds(),
                iteration=iteration,
                reasoning=error_msg,
                raw_response=error_msg
            )
    async def run_consortium(self, config: ConsortiumConfig, csv_path: str, output_path: str) -> Dict:
        """Main execution flow with end-to-end logging"""
        final_results = []
        data = self.ingest_csv(csv_path)
        
        # Extract available classes
        available_classes = []
        has_true_classes = False
        
        # Check if dataset has class labels
        if "class" in data[0] or "label" in data[0] or "category" in data[0]:
            has_true_classes = True
            class_key = "class" if "class" in data[0] else "label" if "label" in data[0] else "category"
            # Extract unique classes
            available_classes = list(set(item[class_key] for item in data if class_key in item))
        else:
            # Ask user to provide classes
            classes_input = input("No class labels found in CSV. Please enter comma-separated class names: ")
            available_classes = [cls.strip() for cls in classes_input.split(",")]

        try:
            for item in data:
                question = item["question"]
                true_class = item.get("class") or item.get("label") or item.get("category") if has_true_classes else None
                responses = []
                
                for iteration in range(config.max_iterations):
                    # Log iteration start with context
                    logger.info(
                        f"Iteration {iteration+1}/{config.max_iterations} for question",
                        extra={'question': question, 'class': 'Iteration started'}
                    )
                    
                    # Execute parallel queries
                    tasks = [
                        self._query_model(model, question, available_classes, instance, iteration, true_class)
                        for model, count in config.models.items()
                        for instance in range(count)
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results with error handling
                    valid_results = []
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error("Processing error", 
                                       extra={'question': question, 'predicted_class': str(result)})
                            continue
                            
                        self.db_handler.log_interaction(result)
                        result_dict = result.to_dict()
                        responses.append(result_dict)
                        
                        # Log individual classification response
                        logger.debug(
                            "Model response",
                            extra={
                                'question': question,
                                'predicted_class': result_dict.get('predicted_class', 'UNKNOWN')
                            }
                        )
                        valid_results.append(result)
                
                    # Perform synthesis with temperature tuning
                    synthesis = await self.synthesis_handler.synthesize(
                        question,
                        valid_results,
                        config.arbiter,
                        iteration + 1,
                        min_temp=config.min_temp,
                        max_temp=config.max_temp,
                        num_trials=config.num_trials,
                        true_class=true_class
                    )
                    
                    # Log synthesis results
                    logger.info(
                        f"Iteration {iteration+1} Best Synthesis - "
                        f"Temp: {synthesis['best']['temperature']:.2f}, "
                        f"Confidence: {synthesis['best']['confidence']:.2f}",
                        extra={
                            'question': question,
                            'predicted_class': synthesis['best']['final_class']
                        }
                    )
                    
                    # Build final result package
                    final_result = {
                        **synthesis,
                        "raw_responses": responses,
                        "iterations": iteration + 1,
                        "true_class": true_class,
                        "question": question  
                    }
                    final_results.append(final_result)
                    
                    # Check early exit conditions
                    if (synthesis['best']['confidence'] >= config.confidence_threshold 
                        and iteration >= config.min_iterations - 1):
                        break

            # Export final results to CSV
            self._export_results(final_results, output_path, has_true_classes)
            
            # Calculate metrics if we have true classes
            metrics = {}
            if has_true_classes:
                
                metrics = self.metrics_handler.calculate_metrics(final_results)
                self._export_metrics(metrics, output_path.replace('.csv', '_metrics.csv'))
                
        finally:
            self.db_handler.close()
            self.synthesis_db_handler.close()
            
        return {
            "results": final_results,
            "metrics": metrics if has_true_classes else {},
            "has_true_classes": has_true_classes
        }

    def _export_results(self, results: List[Dict], output_path: str, has_true_classes: bool) -> None:
        """Export classification results to CSV"""
        export_data = []
        for result in results:
            best = result.get('best', {})
            export_item = {
                "question": result.get('question', ''),
                "predicted_class": best.get('final_class', 'UNKNOWN'),
                "confidence": best.get('confidence', 0.0),
                "iterations": result.get('iterations', 0),
                "temperature": best.get('temperature', 0.0),
                "reasoning": best.get('reasoning', '')
            }
            
            if has_true_classes:
                export_item["true_class"] = result.get('true_class', '')
                export_item["is_correct"] = export_item["predicted_class"] == export_item["true_class"]
            
            export_data.append(export_item)
        
        df = pd.DataFrame(export_data)
        df.to_csv(output_path, index=False)
        logger.info(f"Results exported to {output_path}")
        
    def _export_metrics(self, metrics: Dict, output_path: str) -> None:
        """Export classification metrics to CSV"""
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(output_path, index=False)
        logger.info(f"Metrics exported to {output_path}")