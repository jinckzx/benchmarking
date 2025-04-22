from typing import List, Dict
import numpy as np
from ..config.models import LogEntry
from ..utils.prompt_utils import read_arbiter_prompt_class, read_arbiter_system_prompt
from ..utils.extractors import ResponseExtractor
from ..database.synthesis_class_db import ClassificationSynthesisLogger
from ..utils.logging import logger
from .client_init import llm
from typing import Optional
from .random_search import ArbiterTemperatureTuner

class SynthesisHandlerClass:
    def __init__(self, extractor: ResponseExtractor):
        self.client = llm
        self.extractor = extractor
        self.db_handler = ClassificationSynthesisLogger()
        self.arbiter_system_prompt = read_arbiter_system_prompt()
        self.tuner = ArbiterTemperatureTuner()

    async def synthesize(self, question: str, responses: List[LogEntry], 
                        arbiter: str, iteration: int,
                        min_temp: float, max_temp: float, 
                        num_trials: int, 
                        true_class: Optional[str] = None) -> Dict:
        """Perform classification synthesis with temperature tuning"""
        temperatures = self.tuner.generate_temperatures(min_temp, max_temp, num_trials)
        best_result = None
        all_trials = []

        for temp in temperatures:
            try:
                trial_result = await self._run_arbiter(
                    question=question,
                    responses=responses,
                    arbiter=arbiter,
                    temperature=temp
                )
                
                # Log individual trial
                self._log_trial(
                    question=question,
                    true_class=true_class,
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
                    'predicted_class': trial_result['final_class']
                })

            except Exception as e:
                logger.error(f"Temperature trial {temp} failed: {str(e)}")
                continue

        # Log best result
        if best_result:
            self._log_best_result(
                question=question,
                true_class=true_class,
                final_class=best_result['final_class'],
                confidence=best_result['confidence'],
                analysis=best_result['analysis'],
                reasoning=best_result['reasoning'],
                model_responses=responses,
                iteration=iteration,
                temperature=best_result['temperature']
            )

        return {
            'best': best_result or {
                'text': "No valid classification generated",
                'final_class': "UNKNOWN",
                'confidence': 0.0,
                'analysis': '',
                'reasoning': '',
                'temperature': 0.0
            },
            'trials': all_trials
        }

    async def _run_arbiter(self, question: str, responses: List[LogEntry], 
                          arbiter: str, temperature: float) -> Dict:
        """Execute single arbiter query with specific temperature"""
        comparisons = "\n\n".join(
            f"Model: {entry.model}\nConfidence: {entry.confidence:.2f}\nClass: {entry.predicted_class}\nReasoning: {entry.reasoning}"
            for entry in responses
        )
        
        synthesis_prompt = read_arbiter_prompt_class().format(
            prompt=question,
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
        final_class = self.extractor.extract_class(content)
        
        return {
            "text": content,
            "final_class": final_class,
            "confidence": self.extractor.extract_confidence(content),
            "analysis": self._extract_analysis(content),
            "reasoning": self._extract_reasoning(content),
            "arbiter_model": arbiter,
            "temperature": temperature
        }
        
    def _log_trial(self, question: str, true_class: Optional[str], result: Dict, 
                  iteration: int, temperature: float, model_responses: List[LogEntry]):
        """Log individual temperature trial"""
        try:
            responses_dict = [
                {
                    "model": r.model,
                    "response": r.predicted_class,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning
                } for r in model_responses
            ]
            
            # Use correct temperature trial logging method
            self.db_handler.log_temperature_trial(
                question=question,
                true_class=true_class,
                predicted_class=result['final_class'],
                confidence=result['confidence'],
                temperature=temperature,
                model_responses=responses_dict,
                reasoning=result['reasoning'],
                iteration=iteration
            )
        except Exception as e:
            logger.error(f"Trial logging failed: {str(e)}", 
                        extra={'question': question, 'predicted_class': result.get('final_class', 'UNKNOWN')})

    def _log_best_result(self, question: str, true_class: Optional[str], 
                        final_class: str, confidence: float,
                        analysis: str, reasoning: str, 
                        model_responses: List[LogEntry], 
                        iteration: int, temperature: float):
        """Log final best synthesis"""
        try:
            responses_dict = [
                {
                    "model": r.model,
                    "response": r.predicted_class,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning
                } for r in model_responses
            ]
            
            self.db_handler.log_classification(
                question=question,
                true_class=true_class,
                predicted_class=final_class,
                confidence=confidence,
                model_responses=responses_dict,
                reasoning=reasoning,
                iteration=iteration,
                temperature=temperature,
                is_best_result=True
            )
        except Exception as e:
            logger.error(f"Best result logging failed: {str(e)}", 
                        extra={'question': question, 'predicted_class': final_class})

    def _extract_analysis(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Analysis of Classifications:", 
            "### Final Reasoning:"
        )

    def _extract_reasoning(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Final Reasoning:"
        )