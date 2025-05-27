import json
from typing import Dict, Any
from .criteria_registry import CRITERIA_REGISTRY

def is_error(generated_sql: str) -> bool:
    """Check if generated_sql contains error indicators"""
    if not isinstance(generated_sql, str) or not generated_sql.strip():
        return True
    error_keywords = ['error', 'Error', 'BadRequest', 'Exception', 'invalid']
    return any(keyword in generated_sql for keyword in error_keywords)

def process_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single response using registered criterias"""
    question = response.get('question', '')
    generated_sql = response.get('generated_sql', '')
    gold_sql = response.get('gold_sql', '')
    

    for criteria_name in CRITERIA_REGISTRY:
        response[criteria_name] = 0.0
        response[f"{criteria_name}_rationale"] = 'Error in generated SQL'
    
    if is_error(generated_sql):
        return response

    for criteria_name, criteria_obj in CRITERIA_REGISTRY.items():
        try:
            result = criteria_obj.calculate(
                question=question,
                generated_sql=generated_sql,
                gold_sql=gold_sql
            )
            response[criteria_name] = result.get('score', 0.0)
            response[f"{criteria_name}_rationale"] = result.get('evaluation_rationale', 'No rationale provided')
        except Exception as e:
            print(f"Error calculating {criteria_name}: {str(e)}")
            response[criteria_name] = 0.0
            response[f"{criteria_name}_rationale"] = f"Evaluation error: {str(e)}"
    
    return response

def run_evaluation_pipeline(input_file: str, output_file: str) -> None:
    """Main evaluation pipeline execution"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    model_evaluations = data.get('model_evaluations', {})
    
    for model_name, model_data in model_evaluations.items():
        responses = model_data.get('responses', [])
        for i in range(len(responses)):
            responses[i] = process_response(responses[i])
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)