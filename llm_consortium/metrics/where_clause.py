from .base_metrics import BaseMetric
from typing import Dict, Any, Optional
from ..utils.logging import logger
from ..core.client_init import llm

class Where_clauseMetric(BaseMetric):
    """LLM Judge metric for where_clause"""
    
    def __init__(self):
        super().__init__(
            name="where_clause",
            description="check if there exist a WHERE clause in the {generated_sql} return in yes or no only. strictly.",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """[{'key': 'yes', 'score': '0.9'}, {'key': 'no', 'score': '0.5'}]"""
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
        self.client = llm
        # Define the response map
        self.response_map = {
            'yes': 1.0,
            'no': 0.0,
        }
        # Set default score for unexpected responses
        self.default_score = 0.0
        self.requires_llm = True
        self.fallback_check = True
        
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate whether both SQL queries have the relevant feature.
        Uses LLM results if available, otherwise uses simple text matching.
        """
        # Check cache first
        if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
            return self._cached_result.get('result', {})
        
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            # If we have a pending LLM result from async context, use it
            if hasattr(self, '_pending_llm_result'):
                # Get the result from pending and clean up
                result = self._pending_llm_result
                delattr(self, '_pending_llm_result')
                logger.info(f"Using LLM result for {metric_name_lower}: {result}")
            elif self.fallback_check:
                # If not in async context, use simple detection
                logger.info(f"No LLM result available for {metric_name_lower} metric (using simple detection)")
                result = self._simple_check_sql_query(generated_sql, gold_sql)
            else:
                # Default result if no LLM and no fallback
                result = "error: no_llm_result_available"
            
            # Get score from response map, with fallback to default
            score = self.response_map.get(result, self.default_score)
            logger.info(f"Mapped score for '{result}': {score}")
            
            # Build result dictionary
            metrics_result = {{
                "{metric_name_lower}": score,
                "result": result
            }}
            
            # Cache the result
            self._cached_result = {{
                'inputs': kwargs,
                'result': metrics_result
            }}
            
            return metrics_result
            
        except Exception as e:
            logger.error(f"Error in calculate: {{str(e)}}")
            return {{
                "{metric_name_lower}": 0.0,
                "result": f"error: {{str(e)}}"
            }}
    
    def _simple_check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Simple string-based check when LLM is not available"""
        query_term = "{metric_name_lower}"
        has_feature_generated = query_term in generated_sql.lower()
        has_feature_gold = query_term in gold_sql.lower()
        
        return "yes" if has_feature_generated and has_feature_gold else "no"
    
    async def calculate_async(self, **kwargs) -> Dict[str, Any]:
        """
        Asynchronous version that uses LLM to check SQL queries.
        This should be called from async contexts.
        """
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            # Call LLM to check query
            result = await self._check_sql_query(generated_sql, gold_sql)
            
            # Store the result for calculate method to use
            self._pending_llm_result = result
            
            # Call calculate to handle mapping and caching
            return self.calculate(**kwargs)
            
        except Exception as e:
            logger.error(f"Error in calculate_async: {{str(e)}}")
            return {{
                "{metric_name_lower}": 0.0,
                "result": f"error: {{str(e)}}"
            }}
    
    async def _check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Private async method to query the LLM for SQL feature checking"""
        try:
            formatted_prompt = self.prompt.format(
                generated_sql=generated_sql,
                gold_sql=gold_sql
            )
            
            messages = [
                {'role': 'user', 'content': formatted_prompt}
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
            logger.info(f"LLM response for where_clause: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in _check_sql_query: {str(e)}")
            return f"error: {str(e)}"