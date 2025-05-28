from .base_metrics import BaseMetric
from typing import Dict, Any, Optional
from ..utils.logging import logger
from ..core.client_init import llm

class New_2805Metric(BaseMetric):
    """LLM Judge metric for new_2805"""
    
    def __init__(self):
        super().__init__(
            name="new_2805",
            description="Evaluates if SQL query meets new_2805 criteria.",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """check whether {gold_sql} and {generated_sql} have same column name produced or not"""
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
        self.client = llm
        self.response_map = {
    "yes": 1,
    "no": 0.5,
}
        self.requires_llm = True
        
    def calculate(self, **kwargs) -> Dict[str, Any]:
        if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
            return self._cached_result.get('result', {})
        
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            if hasattr(self, '_pending_llm_result'):
                result = self._pending_llm_result
                delattr(self, '_pending_llm_result')
            else:
                logger.info("Using simple check for new_2805")
                result = self._simple_check_sql_query(gold_sql=gold_sql, generated_sql=generated_sql)
                
            score = self.response_map.get(result, 0.0)
            
            metrics_result = {
                "new_2805": score,
                "result": result
            }
            
            self._cached_result = {
                'inputs': kwargs,
                'result': metrics_result
            }
            return metrics_result
            
        except Exception as e:
            logger.error(f"Error in calculate: {str(e)}")
            return {
                "new_2805": 0.0,
                "result": f"error: {str(e)}"
            }
    
    def _simple_check_sql_query(self, gold_sql: str, generated_sql: str) -> str:
        return "no"
    
    async def calculate_async(self, **kwargs) -> Dict[str, Any]:
        try:
            gold_sql = kwargs.get('gold_sql', '')
            generated_sql = kwargs.get('generated_sql', '')
            
            result = await self._check_sql_query(gold_sql, generated_sql)
            self._pending_llm_result = result
            
            return self.calculate(**kwargs)
            
        except Exception as e:
            logger.error(f"Error in calculate_async: {str(e)}")
            return {
                "new_2805": 0.0,
                "result": f"error: {str(e)}"
            }
    
    async def _check_sql_query(self, gold_sql: str, generated_sql: str) -> str:
        try:
            formatted_prompt = self.prompt.format(gold_sql=gold_sql, generated_sql=generated_sql)
            
            messages = [
                {"role": "user", "content": formatted_prompt}
            ]
            
            logger.info(f"Sending prompt: {formatted_prompt}")
            
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            result = response["content"].strip().lower()
            logger.info(f"LLM response: {result}")
            if "yes" in result:
                return "yes"
            elif "no" in result:
                return "no"
        except Exception as e:
            logger.error(f"Query check error: {str(e)}")
            return f"error: {str(e)}"