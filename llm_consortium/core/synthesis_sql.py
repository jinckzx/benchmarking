
from typing import List, Dict
from openai import AsyncOpenAI
from ..config.models import LogEntry
from ..utils.prompt_utils import read_arbiter_prompt, read_arbiter_system_prompt
from ..utils.extractors import ResponseExtractor
from ..database.spiderlog_db import SpiderDatasetLogger
from ..utils.logging import logger
import json

class SynthesisHandlerSQL:
    def __init__(self, client: AsyncOpenAI, extractor: ResponseExtractor):
        self.client = client
        self.extractor = extractor
        self.db_handler = SpiderDatasetLogger()
        self.arbiter_system_prompt = read_arbiter_system_prompt()

    async def synthesize(self, prompt: str, responses: List[LogEntry], 
                        arbiter: str, iteration: int) -> Dict:
        """Perform final synthesis with enhanced SQL logging"""
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
        
        try:
            response = await self.client.chat.completions.create(
                model=arbiter,
                messages=messages,
                temperature=0.2
            )
            content = response.choices[0].message.content
            
            # Extract final SQL using the response extractor
            final_sql = self.extractor.extract_sql(content)
            
            result = {
                "text": content,
                "final_query": final_sql,
                "confidence": self.extractor.extract_confidence(content),
                "analysis": self._extract_analysis(content),
                "dissenting_views": self._extract_dissent(content),
                "arbiter_model": arbiter,
                "intent": self.extractor.extract_intent(content)
            }

            # Enhanced logging with context
            self._log_to_spider_db(
                prompt=prompt,
                synthesized_text=result['final_query'],  # Use extracted SQL
                confidence=result['confidence'],
                analysis=result['analysis'],
                dissent=result['dissenting_views'],
                intent=result['intent'],
                model_responses=responses,
                iteration=iteration
            )

            logger.info(
                f"Iteration {iteration} Synthesis Complete - Confidence: {result['confidence']:.2f}",
                extra={
                    'question': prompt,
                    'generated_sql': result['final_query']
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Arbiter synthesis error: {str(e)}"
            logger.error(error_msg, extra={'question': prompt, 'generated_sql': 'N/A'})
            return {
                "text": error_msg,
                "final_query": "N/A",
                "confidence": 0.0,
                "analysis": "",
                "dissenting_views": "",
                "arbiter_model": arbiter,
                "intent": ""
            }

    def _log_to_spider_db(self, prompt: str, synthesized_text: str, confidence: float,
                         analysis: str, dissent: str, intent: str, 
                         model_responses: List[LogEntry], iteration: int):
        """Enhanced database logging with SQL validation"""
        try:
            responses_dict = [
                {
                    "model": r.model,
                    "response": r.response,
                    "confidence": r.confidence,
                    "sql": r.response  # Direct SQL from LogEntry
                } for r in model_responses
            ]
            
            self.db_handler.log_query(
                db_schema=f"Synthesis_Iteration_{iteration}",
                natural_language_query=prompt,
                intent_category=intent,
                generated_sql=synthesized_text,
                confidence=confidence,
                model_responses=responses_dict
            )
        except Exception as e:
            logger.error(f"DB logging failed: {str(e)}", 
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