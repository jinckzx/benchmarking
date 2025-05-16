# """
# Code generator utilities for SQL metric creation.
# This module contains functions to dynamically generate metric classes.
# """

# def generate_metric_code(metric_name, prompt, keys):
#     keys_dict = "{\n"
#     for kv in keys:
#         if kv.get("key") and kv.get("score"):
#             # Handle both string and numeric scores
#             score = kv["score"]
#             if isinstance(score, str) and not score.replace('.', '').isdigit():
#                 score = f'"{score}"'
#             keys_dict += f'    "{kv["key"]}": {score},\n'
#     keys_dict += "}"

#     class_template = '''
# from .base_metrics import BaseMetric
# from typing import Dict, Any, Optional
# from ..utils.logging import logger
# from ..core.client_init import llm

# class {class_name}Metric(BaseMetric):
#     """LLM Judge metric for {metric_name}"""
    
#     def __init__(self):
#         super().__init__(
#             name="{metric_name_lower}",
#             description="Evaluates if SQL query has proper {metric_name} in both generated and gold SQL.",
#             csv_requires=["gold_sql"],
#             runtime_requires=["generated_sql", "gold_sql"]
#         )
#         self.prompt = """{prompt}"""
#         self.model = "gpt-4o-mini"
#         self.temperature = 0.0
#         self.client = llm
#         self.response_map = {response_map}
#         self.requires_llm = True
        
#     def calculate(self, **kwargs) -> Dict[str, Any]:
#         if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
#             return self._cached_result.get('result', {{}})
        
#         try:
#             generated_sql = kwargs.get('generated_sql', '')
#             gold_sql = kwargs.get('gold_sql', '')
            
#             if hasattr(self, '_pending_llm_result'):
#                 result = self._pending_llm_result
#                 delattr(self, '_pending_llm_result')
#             else:
#                 logger.info("Used string-based check for {metric_name_lower} metric (not in async context)")
#                 result = self._simple_check_sql_query(generated_sql, gold_sql)
                
#             score = self.response_map.get(result, 0.0)
                
#             metrics_result = {{
#                 "{metric_name_lower}": score,
#                 "result": result
#             }}
            
#             self._cached_result = {{
#                 'inputs': kwargs,
#                 'result': metrics_result
#             }}
            
#             return metrics_result
            
#         except Exception as e:
#             logger.error(f"Error in calculate: {{str(e)}}")  # Escaped braces
#             return {{
#                 "{metric_name_lower}": 0.0,
#                 "result": f"error: {{str(e)}}"  # Escaped
#             }}
    
#     def _simple_check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
#         query_term = "{metric_name_lower}"
#         has_feature_generated = query_term in generated_sql.lower()
#         has_feature_gold = query_term in gold_sql.lower()
        
#         return "yes" if has_feature_generated and has_feature_gold else "no"
    
#     async def calculate_async(self, **kwargs) -> Dict[str, Any]:
#         try:
#             generated_sql = kwargs.get('generated_sql', '')
#             gold_sql = kwargs.get('gold_sql', '')
            
#             result = await self._check_sql_query(generated_sql, gold_sql)
#             self._pending_llm_result = result
            
#             return self.calculate(**kwargs)
            
#         except Exception as e:
#             logger.error(f"Error in calculate_async: {{str(e)}}")  # Escaped
#             return {{
#                 "{metric_name_lower}": 0.0,
#                 "result": f"error: {{str(e)}}"  # Escaped
#             }}
    
#     async def _check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
#         try:
#             formatted_prompt = self.prompt.format(
#                 generated_sql=generated_sql,
#                 gold_sql=gold_sql
#             )
            
#             messages = [
#                 {{"role": "user", "content": formatted_prompt}}
#             ]
            
#             logger.info(f"Sending prompt to LLM: {{formatted_prompt}}")  # Escaped
            
#             response = await self.client.chat(
#                 model=self.model,
#                 messages=messages,
#                 temperature=self.temperature
#             )
            
#             result = response["content"].strip().lower()
#             # Fixed line below
#             logger.info(f"LLM response for {metric_name_lower}: {{result}}")  # Escaped
#             return result
#         except Exception as e:
#             logger.error(f"Error in _check_sql_query: {{str(e)}}")  # Escaped
#             return f"error: {{str(e)}}"  # Escaped
#     '''

#     # Prepare the template values
#     template_values = {
#         'class_name': metric_name.capitalize(),
#         'metric_name': metric_name,
#         'metric_name_lower': metric_name.lower(),
#         'prompt': prompt,
#         'response_map': keys_dict
#     }
    
#     # Replace all placeholders
#     raw_code = class_template.format(**template_values)
    
#     # Fix the braces issue by replacing double braces with single braces
#     raw_code = raw_code.replace("{{", "{").replace("}}", "}")
    
#     return raw_code.strip()


"""
Code generator utilities for SQL metric creation.
This module contains functions to dynamically generate metric classes.
"""

import re

def generate_metric_code(metric_name, prompt, keys):
    # Extract variables from the prompt using regex
    variables = list(dict.fromkeys(re.findall(r'\{(\w+)\}', prompt)))
    
    # Prepare parameters for _check_sql_query method
    params = ', '.join([f"{var}: str" for var in variables])
    
    # Generate formatted_prompt line in _check_sql_query
    format_args = ', '.join([f"{var}={var}" for var in variables])
    formatted_prompt_line = f"self.prompt.format({format_args})"
    
    # Generate variable extraction and method call in calculate_async
    extract_vars = '\n            '.join([f"{var} = kwargs.get('{var}', '')" for var in variables])
    call_check_sql = f"await self._check_sql_query({', '.join(variables)})"
    
    # Generate _simple_check_sql_query logic based on variables
    checks = []
    for var in variables:
        checks.append(f"{var}_lower = {var}.lower()")
        checks.append(f"has_{var} = query_term in {var}_lower")
    check_conditions = ' and '.join([f"has_{var}" for var in variables])
    simple_check_body = f"""
        query_term = "{metric_name.lower().replace('_check', '')}"
        {"\n        ".join(checks)}
        return "yes" if {check_conditions} else "no"
    """
    
    # Build response_map from keys
    response_map = "{\n"
    for kv in keys:
        if kv.get("key") and kv.get("score"):
            score = kv["score"]
            if isinstance(score, str) and not score.replace('.', '', 1).isdigit():
                score = f'"{score}"'
            response_map += f'    "{kv["key"]}": {score},\n'
    response_map += "}"
    
    class_template = '''
from .base_metrics import BaseMetric
from typing import Dict, Any, Optional
from ..utils.logging import logger
from ..core.client_init import llm

class {class_name}Metric(BaseMetric):
    """LLM Judge metric for {metric_name}"""
    
    def __init__(self):
        super().__init__(
            name="{metric_name_lower}",
            description="Evaluates if SQL query meets {metric_name} criteria.",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """{prompt}"""
        self.model = "gpt-4o-mini"
        self.temperature = 0.0
        self.client = llm
        self.response_map = {response_map}
        self.requires_llm = True
        
    def calculate(self, **kwargs) -> Dict[str, Any]:
        if hasattr(self, '_cached_result') and self._cached_result.get('inputs') == kwargs:
            return self._cached_result.get('result', {{}})
        
        try:
            generated_sql = kwargs.get('generated_sql', '')
            gold_sql = kwargs.get('gold_sql', '')
            
            if hasattr(self, '_pending_llm_result'):
                result = self._pending_llm_result
                delattr(self, '_pending_llm_result')
            else:
                logger.info("Using simple check for {metric_name_lower}")
                result = self._simple_check_sql_query({variables_kwargs})
                
            score = self.response_map.get(result, 0.0)
            
            metrics_result = {{
                "{metric_name_lower}": score,
                "result": result
            }}
            
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
    
    def _simple_check_sql_query(self, {params}) -> str:
        return "no"
    
    async def calculate_async(self, **kwargs) -> Dict[str, Any]:
        try:
            {extract_vars}
            
            result = {call_check_sql}
            self._pending_llm_result = result
            
            return self.calculate(**kwargs)
            
        except Exception as e:
            logger.error(f"Error in calculate_async: {{str(e)}}")
            return {{
                "{metric_name_lower}": 0.0,
                "result": f"error: {{str(e)}}"
            }}
    
    async def _check_sql_query(self, {params}) -> str:
        try:
            formatted_prompt = {formatted_prompt_line}
            
            messages = [
                {{"role": "user", "content": formatted_prompt}}
            ]
            
            logger.info(f"Sending prompt: {{formatted_prompt}}")
            
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            result = response["content"].strip().lower()
            logger.info(f"LLM response: {{result}}")
            if "yes" in result:
                return "yes"
            elif "no" in result:
                return "no"
        except Exception as e:
            logger.error(f"Query check error: {{str(e)}}")
            return f"error: {{str(e)}}"
    '''
    
    template_values = {
        'class_name': metric_name.capitalize(),
        'metric_name': metric_name,
        'metric_name_lower': metric_name.lower(),
        'prompt': prompt,
        'response_map': response_map,
        'params': params,
        'formatted_prompt_line': formatted_prompt_line,
        'extract_vars': extract_vars,
        'call_check_sql': call_check_sql,
        'simple_check_body': simple_check_body,
        'variables_kwargs': ', '.join([f"{var}={var}" for var in variables])
    }
    
    raw_code = class_template.format(**template_values)
    raw_code = raw_code.replace("{{", "{").replace("}}", "}")
    return raw_code.strip()