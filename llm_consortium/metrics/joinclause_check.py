from .base_metrics import BaseMetric
from typing import Dict, Any, Optional
from ..utils.logging import logger
from ..core.client_init import llm

class Joinclause_checkMetric(BaseMetric):
    """LLM Judge metric for joinclause_check"""
    
    def __init__(self):
        super().__init__(
            name="joinclause_check",
            description="Evaluates if SQL query has JOIN clauses in generated SQL.",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """Check whether the following SQL query contains a JOIN clause:
Generated SQL: {generated_sql}
Answer only with 'yes' or 'no'. Strictly."""
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
        self.client = llm
        # Define the response map here
        self.response_map = {
            "yes": 0.8,
            "no": 0.0,
        }
        # Set default score for unexpected responses
        self.default_score = 0.0
        self.requires_llm = True
        
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate whether the generated SQL has JOIN clauses.
        Uses LLM results if available, otherwise uses simple text matching.
        """
        # Check cache first
        if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
            return self._cached_result.get('result', {})
        
        try:
            generated_sql = kwargs.get('generated_sql', '')
            
            # If we have a pending LLM result from async context, use it
            if hasattr(self, '_pending_llm_result'):
                # Get the result from pending and clean up
                result = self._pending_llm_result
                delattr(self, '_pending_llm_result')
                logger.info(f"Using LLM result for joinclause_check: {result}")
            else:
                # If not in async context, use simple detection
                logger.info("No LLM result available for joinclause_check metric (using simple detection)")
                
            
            # Get score from response map, with fallback to default
            score = self.response_map.get(result, self.default_score)
            logger.info(f"Mapped score for '{result}': {score}")
            
            # Build result dictionary
            metrics_result = {
                "joinclause_check": score,
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
                "joinclause_check": 0.0,
                "result": f"error: {str(e)}"
            }
    
    async def calculate_async(self, **kwargs) -> Dict[str, Any]:
        """
        Asynchronous version that uses LLM to check SQL queries.
        This should be called from async contexts.
        """
        try:
            generated_sql = kwargs.get('generated_sql', '')
            
            # Call LLM to check query
            result = await self._check_sql_query(generated_sql)
            
            # Store the result for calculate method to use
            self._pending_llm_result = result
            
            # Call calculate to handle mapping and caching
            return self.calculate(**kwargs)
            
        except Exception as e:
            logger.error(f"Error in calculate_async: {str(e)}")
            return {
                "joinclause_check": 0.0,
                "result": f"error: {str(e)}"
            }
    
    async def _check_sql_query(self, generated_sql: str) -> str:
        """Private async method to query the LLM for SQL JOIN clause checking"""
        try:
            # Format prompt with just the generated SQL
            formatted_prompt = self.prompt.format(
                generated_sql=generated_sql
            )
            
            messages = [
                {"role": "user", "content": formatted_prompt}
            ]
            
            logger.info(f"Sending prompt to LLM: {formatted_prompt}")
            
            # Call LLM API
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            # Process response
            result = response["content"].strip().lower()
            logger.info(f"LLM response for joinclause_check: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in _check_sql_query: {str(e)}")
            return f"error: {str(e)}"