from .base_metrics import BaseMetric
from typing import Dict, Any, Optional
from langchain.schema import HumanMessage
from ..core.client_init import llm
from ..utils.logging import logger
import inspect

class Select_checkMetric(BaseMetric):
    """LLM Judge metric for select_check"""

    def __init__(self):
        super().__init__(
            name="select_check",
            description="Evaluates if SQL query has proper SELECT clause in both generated and gold SQL.",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = (
            "Check whether the following two SQL queries both contain a SELECT clause:\n"
            "Generated SQL: {generated_sql}\n"
            "Gold SQL: {gold_sql}\n"
            "Answer only with 'yes' or 'no'. Strictly."
        )
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
        self.client = llm
        # Flag to indicate if this metric requires LLM
        self.requires_llm = True
        
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate whether both SQL queries have SELECT clauses.
        Uses LLM to check if we're in an async context, otherwise falls back to string matching.
        """
        # We'll store the cached result to avoid duplicate LLM calls
        if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
            return self._cached_result.get('result', {})
        
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            # If we have a coroutine object attached from an async context, use that result
            if hasattr(self, '_pending_llm_result'):
                result = self._pending_llm_result
                delattr(self, '_pending_llm_result')  # Clean up
            else:
                # Fallback to string-based check when not in async context
                has_select_generated = "select" in generated_sql.lower()
                has_select_gold = "select" in gold_sql.lower()
                result = "yes" if (has_select_generated and has_select_gold) else "no"
                logger.info("Used string-based check for select_check metric (not in async context)")
                
            # Map result to score
            if result == "yes":
                score = 0.9
            elif result == "no":
                score = 0.2
            else:
                score = 0.0
                
            metrics_result = {
                "select_check": score,
                "result": result
            }
            
            # Cache the result
            self._cached_result = {
                'inputs': kwargs,
                'result': metrics_result
            }
            
            return metrics_result
            
        except Exception as e:
            logger.error(f"Error in calculate: {str(e)}")
            return {
                "select_check": 0.0,
                "result": f"error: {str(e)}"
            }
    
    async def calculate_async(self, **kwargs) -> Dict[str, Any]:
        """
        Asynchronous version that uses LLM to check SQL queries.
        This should be called from async contexts.
        """
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            # Call LLM to check queries
            result = await self._check_sql_query(generated_sql, gold_sql)
            
            # Store the result for the calculate method to use
            self._pending_llm_result = result
            
            # Now call calculate to handle the mapping and caching
            return self.calculate(**kwargs)
            
        except Exception as e:
            logger.error(f"Error in calculate_async: {str(e)}")
            return {
                "select_check": 0.0,
                "result": f"error: {str(e)}"
            }
    
    async def _check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Private async method to query the LLM for SQL clause checking"""
        try:
            formatted_prompt = self.prompt.format(
                generated_sql=generated_sql,
                gold_sql=gold_sql
            )
            messages = [HumanMessage(content=formatted_prompt)]
            logger.info(f"Sending prompt to LLM: {formatted_prompt}")
            
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            result = response["content"].strip().lower()
            logger.info(f"LLM response for select_check: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in _check_sql_query: {str(e)}")
            return f"error: {str(e)}"