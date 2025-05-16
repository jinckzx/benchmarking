from .base_metrics import BaseMetric
from typing import Dict, Any
import asyncio
from ..utils.logging import logger

class LLMJudgeMetric(BaseMetric):
    """Generic base class for LLM-as-judge metrics"""
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 prompt_template: str,
                 response_map: Dict[str, float]):
        super().__init__(
            name=name,
            description=description,
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = prompt_template
        self.response_map = response_map
        self.client = None
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
    
    def _initialize_client(self):
        """Lazy initialization of client to avoid circular imports"""
        if self.client is None:
            try:
                from ..core.client_init import llm
                self.client = llm
                return True
            except ImportError as e:
                logger.error(f"Failed to import LLM client: {str(e)}")
                return False
        return True
            
    async def check_sql_query_async(self, generated_sql: str, gold_sql: str) -> str:
        """Async LLM check of SQL queries"""
        try:
            if not self._initialize_client():
                return "error: failed to initialize client"
                
            from langchain.schema import HumanMessage
            
            formatted_prompt = self.prompt.format(
                generated_sql=generated_sql,
                gold_sql=gold_sql
            )
            
            messages = [{"role": "user", "content": formatted_prompt}]
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            return response["content"].strip().lower()
                
        except Exception as e:
            logger.error(f"Error in async check_sql_query: {str(e)}")
            return f"error: {str(e)}"

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """
        Synchronous calculation method - uses a simple rule-based approach.
        This allows compatibility with the existing synchronous model runner.
        
        Override this in subclasses with metric-specific synchronous logic.
        """
        # Implement simple string-based heuristics specific to the metric
        # This is a fallback that doesn't require async LLM calls
        try:
            # Default implementation - should be overridden by subclasses
            result = self._simple_check(generated_sql, gold_sql)
            score = self.response_map.get(result, 0.0)
            
            return {
                self.name: score,
                f"{self.name}_result": result
            }
        except Exception as e:
            logger.error(f"Error in {self.name} calculation: {str(e)}")
            return {
                self.name: 0.0,
                f"{self.name}_result": f"error: {str(e)}"
            }
    
    def _simple_check(self, generated_sql: str, gold_sql: str) -> str:
        """Simple string-based check - override in subclasses"""
        # This should be implemented by subclasses with metric-specific logic
        return "error: not implemented"

    # This method can be used when you modify the model runner for async support
    async def calculate_async(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """
        Async version of calculate that can be used when the caller supports async.
        Uses the LLM for more accurate judgments.
        """
        result = await self.check_sql_query_async(generated_sql, gold_sql)
        score = self.response_map.get(result, 0.0)
        
        return {
            self.name: score,
            f"{self.name}_result": result
        }