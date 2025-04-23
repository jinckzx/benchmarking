from typing import List, Dict
import numpy as np
from openai import AsyncOpenAI
from ..config.models import LogEntry
from ..utils.prompt_utils import read_arbiter_prompt, read_arbiter_system_prompt
from ..utils.extractors import ResponseExtractor
from ..database.spiderlog_db import SpiderDatasetLogger
from ..utils.logging import logger
from .client_init import llm
from .random_search import ArbiterTemperatureTuner

class SynthesisHandlerSQL:
    def __init__(self, extractor: ResponseExtractor):
        self.client = llm
        self.extractor = extractor
        self.db_handler = SpiderDatasetLogger()
        self.arbiter_system_prompt = read_arbiter_system_prompt()
        self.tuner = ArbiterTemperatureTuner()

    async def synthesize(self, prompt: str, responses: List[LogEntry], 
                        arbiter: str, iteration: int,
                        min_temp: float, max_temp: float, 
                        num_trials: int) -> Dict:
        """Perform SQL synthesis with temperature tuning"""
        temperatures = self.tuner.generate_temperatures(min_temp, max_temp, num_trials)
        best_result = None
        all_trials = []

        for temp in temperatures:
            try:
                trial_result = await self._run_arbiter(
                    prompt=prompt,
                    responses=responses,
                    arbiter=arbiter,
                    temperature=temp
                )
                
                # Log individual trial
                self._log_trial(
                    prompt=prompt,
                    result=trial_result,
                    iteration=iteration,
                    temperature=temp,
                    model_responses=responses
                )

                # Track best result
                if not best_result or trial_result['confidence'] > best_result['confidence']:
                    best_result = trial_result

                all_trials.append({
                    'temperature': temp,
                    'confidence': trial_result['confidence'],
                    'sql': trial_result['final_query']
                })

            except Exception as e:
                logger.error(f"Temperature trial {temp} failed: {str(e)}")
                continue

        # Log best result
        if best_result:
            self._log_to_spider_db(
                prompt=prompt,
                synthesized_text=best_result['final_query'],
                confidence=best_result['confidence'],
                analysis=best_result['analysis'],
                dissent=best_result['dissenting_views'],
                intent=best_result['intent'],
                model_responses=responses,
                iteration=iteration,
                temperature=best_result['temperature']
            )

        return {
            'best': best_result or {
                'text': "No valid synthesis generated",
                'final_query': "N/A",
                'confidence': 0.0,
                'analysis': '',
                'dissenting_views': '',
                'temperature': 0.0,
                'intent': ''
            },
            'trials': all_trials
        }

    async def _run_arbiter(self, prompt: str, responses: List[LogEntry], 
                         arbiter: str, temperature: float) -> Dict:
        """Execute single arbiter query with specific temperature"""
        comparisons = "\n\n".join(
            f"Model: {entry.model}\nConfidence: {entry.confidence:.2f}\nSQL:\n{entry.response}"
            for entry in responses
        )
        
        synthesis_prompt = read_arbiter_prompt().format(
            prompt=prompt,
            comparisons=comparisons,
            arbiter=arbiter
        )

        messages = [
            {"role": "system", "content": self.arbiter_system_prompt},
            {"role": "user", "content": synthesis_prompt}
        ]

        response = await self.client.chat(
            model=arbiter,
            messages=messages,
            temperature=temperature
        )

        content = response["content"]
        final_sql = self.extractor.extract_sql(content)
        
        return {
            "text": content,
            "final_query": final_sql,
            "confidence": self.extractor.extract_confidence(content),
            "analysis": self._extract_analysis(content),
            "dissenting_views": self._extract_dissent(content),
            "arbiter_model": arbiter,
            "intent": self.extractor.extract_intent(content),
            "temperature": temperature
        }
    def _log_trial(self, prompt: str, result: Dict, iteration: int,
              temperature: float, model_responses: List[LogEntry]):
        """Log individual temperature trial"""
        try:
            responses_dict = [
                {
                    "model": r.model,
                    "response": r.response,
                    "confidence": r.confidence,
                    "sql": r.response
                } for r in model_responses
            ]
            
            # Use correct temperature trial logging method
            self.db_handler.log_temperature_trial(
                db_schema=f"Trial_{temperature}_Iteration_{iteration}",
                natural_language_query=prompt,
                intent_category=result['intent'],
                generated_sql=result['final_query'],
                confidence=result['confidence'],
                temperature=temperature,
                model_responses=responses_dict,
                iteration=iteration
            )
        except Exception as e:
            logger.error(f"Trial logging failed: {str(e)}", 
                        extra={'question': prompt, 'generated_sql': result.get('final_query', 'N/A')})


    def _log_to_spider_db(self, prompt: str, synthesized_text: str, confidence: float,
                         analysis: str, dissent: str, intent: str, 
                         model_responses: List[LogEntry], iteration: int,
                         temperature: float):
        """Log final best synthesis"""
        try:
            responses_dict = [
                {
                    "model": r.model,
                    "response": r.response,
                    "confidence": r.confidence,
                    "sql": r.response
                } for r in model_responses
            ]
            
            self.db_handler.log_query(
                db_schema=f"Best_Iteration_{iteration}",
                natural_language_query=prompt,
                intent_category=intent,
                generated_sql=synthesized_text,
                confidence=confidence,
                model_responses=responses_dict,
                temperature=temperature,
                is_best_result=True
            )
        except Exception as e:
            logger.error(f"Best result logging failed: {str(e)}", 
                        extra={'question': prompt, 'generated_sql': synthesized_text})

    def _extract_analysis(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Analysis of Differences:", 
            "### Dissenting Views:"
        )

    def _extract_dissent(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Dissenting Views:"
        )