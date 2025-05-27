import json
from .column_accuracy import ColumnAccuracyMetric
from .query_structure import QueryStructureMetric
from .join_quality import JoinQualityMetric
import os
from dotenv import load_dotenv

load_dotenv()

CRITERIA = [
    ('column_accuracy', ColumnAccuracyMetric()),
    ('query_structure', QueryStructureMetric()),
    ('join_quality', JoinQualityMetric())
]

def is_error(generated_sql):
    """Check if generated_sql contains error indicators"""
    if not isinstance(generated_sql, str) or not generated_sql.strip():
        return True
    error_keywords = ['error', 'Error', 'BadRequest', 'Exception', 'invalid']
    return any(keyword in generated_sql for keyword in error_keywords)

def process_response(response):
    """Process a single response to add dynamic metrics"""
    question = response.get('question', '')
    generated_sql = response.get('generated_sql', '')
    gold_sql = response.get('gold_sql', '')
    
    # Initialize default values for all metrics
    for metric_name, _ in CRITERIA:
        response[metric_name] = 0.0
        response[f"{metric_name}_rationale"] = 'Error in generated SQL'
    
    # Skip processing if generated SQL is an error
    if is_error(generated_sql):
        return response
    
    # Calculate each metric separately with individual error handling
    for metric_name, metric_obj in CRITERIA:
        try:
            result = metric_obj.calculate(
                question=question,
                generated_sql=generated_sql,
                gold_sql=gold_sql
            )
            response[metric_name] = result.get('score', 0.0)
            rationale = result.get('evaluation_rationale', 'No rationale provided')
            response[f"{metric_name}_rationale"] = rationale
        except Exception as e:
            print(f"Error calculating {metric_name}: {str(e)}")
            response[metric_name] = 0.0
            response[f"{metric_name}_rationale"] = f"Evaluation error: {str(e)}"
    
    return response

def main(input_file, output_file):
    """Main processing function"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    model_evaluations = data.get('model_evaluations', {})
    
    for model_name, model_data in model_evaluations.items():
        responses = model_data.get('responses', [])
        for i in range(len(responses)):
            responses[i] = process_response(responses[i])
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python evaluate_metrics.py <input_file.json> <output_file.json>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])