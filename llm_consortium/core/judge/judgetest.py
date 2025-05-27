# import os
# os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"
# from deepeval.metrics import GEval
# from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# from typing import Dict, Any, List, Union
# import json
# import asyncio
# from tqdm import tqdm
# from dotenv import load_dotenv
# load_dotenv()

# class SQLJudge:
#     """Main class to evaluate SQL generation performance across multiple models"""
    
#     def __init__(self, criteria_files: List[str] = None, model: str = "gpt-4o-mini"):
#         """
#         Initialize the SQL judge with evaluation criteria
        
#         Args:
#             criteria_files: List of criteria file paths to load
#             model: Model to use for evaluation
#         """
#         self.model = model
#         self.metrics = self._load_metrics(criteria_files)
        
#     def _load_metrics(self, criteria_files: List[str]) -> Dict[str, Any]:
#         """Load evaluation metrics from criteria files"""
#         metrics = {
#             "query_metrics": QueryMetricsAnalyzer(model=self.model),
#             "intent_understanding": IntentUnderstandingMetric(model=self.model),
#             "syntax_accuracy": SyntaxAccuracyMetric(model=self.model),
#             "logical_correctness": LogicalCorrectnessMetric(model=self.model)
#         }
#         return metrics
    
#     async def evaluate_model(self, model_name: str, responses: List[Dict]) -> Dict[str, Any]:
#         """Evaluate a single model's performance"""
#         results = {
#             "model": model_name,
#             "metrics": {},
#             "detailed_results": []
#         }
        
#         # Evaluate each metric
#         for metric_name, metric in self.metrics.items():
#             # Evaluate all responses for this metric
#             metric_results = []
#             scores = []
            
#             for response in tqdm(responses, desc=f"Evaluating {metric_name} for {model_name}"):
#                 if 'generated_sql' not in response or 'gold_sql' not in response:
#                     continue
                    
#                 try:
#                     result = await metric.evaluate_async(
#                         question=response.get('question', ''),
#                         generated_sql=response.get('generated_sql', ''),
#                         gold_sql=response.get('gold_sql', '')
#                     )
#                     metric_results.append(result)
#                     scores.append(result['score'])
                    
#                     # Print detailed rationale for debugging
#                     print(f"\n--- {metric_name.upper()} EVALUATION ---")
#                     print(f"Question: {response.get('question', '')[:100]}...")
#                     print(f"Score: {result['score']}")
#                     print(f"Rationale: {result['rationale']}")
#                     print("-" * 50)
                    
#                 except Exception as e:
#                     print(f"Error evaluating {metric_name}: {str(e)}")
#                     continue
            
#             # Calculate aggregate metrics
#             if scores:
#                 avg_score = sum(scores) / len(scores)
#                 results['metrics'][metric_name] = {
#                     "average_score": avg_score,
#                     "num_evaluated": len(scores),
#                     "pass_rate": sum(1 for s in scores if s >= metric.threshold) / len(scores),
#                     "detailed_results": metric_results
#                 }
#             else:
#                 results['metrics'][metric_name] = {
#                     "average_score": 0,
#                     "num_evaluated": 0,
#                     "pass_rate": 0,
#                     "detailed_results": []
#                 }
        
#         return results
    
#     async def evaluate_all_models(self, input_data: Dict) -> Dict[str, Any]:
#         """Evaluate all models in the input data"""
#         results = {}
        
#         if "model_evaluations" not in input_data:
#             raise ValueError("Input data must contain 'model_evaluations' key")
        
#         # Create tasks for concurrent evaluation
#         tasks = []
#         model_names = []
        
#         for model_name, model_data in input_data['model_evaluations'].items():
#             if 'responses' in model_data:
#                 task = self.evaluate_model(model_name, model_data['responses'])
#                 tasks.append(task)
#                 model_names.append(model_name)
        
#         # Execute all tasks concurrently with progress tracking
#         print(f"Evaluating {len(tasks)} models...")
        
#         # Use asyncio.gather with return_exceptions=True to handle individual failures
#         completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
#         # Process results
#         for i, result in enumerate(completed_results):
#             if isinstance(result, Exception):
#                 print(f"Error evaluating model {model_names[i]}: {str(result)}")
#                 # Create a default result for failed models
#                 results[model_names[i]] = {
#                     "model": model_names[i],
#                     "metrics": {},
#                     "detailed_results": [],
#                     "error": str(result)
#                 }
#             else:
#                 results[result['model']] = result
        
#         # Calculate overall rankings
#         ranked_models = self._rank_models(results)
#         results['rankings'] = ranked_models
        
#         return results
    
#     def _rank_models(self, results: Dict) -> List[Dict]:
#         """Rank models based on their performance across all metrics"""
#         model_scores = []
        
#         for model_name, model_data in results.items():
#             if not isinstance(model_data, dict) or 'metrics' not in model_data:
#                 continue
                
#             # Calculate weighted average across all metrics
#             total_score = 0
#             total_weight = 0
#             for metric_name, metric_data in model_data['metrics'].items():
#                 if metric_name in self.metrics:
#                     weight = getattr(self.metrics[metric_name], 'weight', 1.0)
#                     total_score += metric_data['average_score'] * weight
#                     total_weight += weight
                
#             weighted_avg = total_score / total_weight if total_weight > 0 else 0
#             model_scores.append({
#                 'model': model_name,
#                 'overall_score': weighted_avg,
#                 'metrics': model_data['metrics']
#             })
        
#         # Sort by overall score
#         return sorted(model_scores, key=lambda x: x['overall_score'], reverse=True)
    
#     def save_results(self, results: Dict, output_path: str) -> None:
#         """Save evaluation results to a JSON file"""
#         with open(output_path, 'w') as f:
#             json.dump(results, f, indent=2)
            
#         print(f"Results saved to {output_path}")

# # Enhanced metric classes with detailed rationales
# class QueryMetricsAnalyzer:
#     """Analyzes basic SQL query metrics"""
    
#     def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
#         self.name = "query_metrics"
#         self.threshold = threshold
#         self.model = model
#         self.weight = 1.0  # Relative importance for ranking
        
#         self.geval = GEval(
#             name=self.name,
#             criteria="""Evaluate the SQL query across these specific dimensions, providing 3-4 lines for each:

# 1. COLUMN ACCURACY: Are the correct columns selected? Missing or extra columns? Column aliases appropriate?
# 2. QUERY STRUCTURE: Is the SQL structure proper? Correct syntax and organization? Readable formatting?
# 3. JOIN QUALITY: Are join conditions appropriate and efficient? Missing joins or incorrect join types?
# 4. CLAUSE ACCURACY: Are WHERE, GROUP BY, HAVING, ORDER BY clauses correctly implemented?

# For each dimension, explain what's correct, what's missing, and why it matters for the query's correctness.""",
#             evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
#             model=model
#         )
    
#     async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
#         """Async evaluation of a single query"""
#         test_case = LLMTestCase(
#             input=f"Question: {question}\nGold SQL: {gold_sql}",
#             actual_output=generated_sql,
#             expected_output=gold_sql
#         )
        
#         await self.geval.a_measure(test_case)
        
#         # Try different ways to get the rationale
#         rationale = None
#         for attr in ['reason', 'rationale', 'explanation', 'verbose_logs']:
#             if hasattr(self.geval, attr):
#                 rationale = getattr(self.geval, attr)
#                 break
        
#         if rationale is None:
#             rationale = "Rationale not available - check GEval response format"
        
#         return {
#             "score": self.geval.score,
#             "rationale": rationale,
#             "question": question,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql
#         }

# class IntentUnderstandingMetric:
#     """Evaluates how well SQL captures question intent"""
    
#     def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
#         self.name = "intent_understanding"
#         self.threshold = threshold
#         self.model = model
#         self.weight = 1.2  # More important than basic metrics
        
#         self.geval = GEval(
#             name=self.name,
#             criteria="""Evaluate how well the SQL captures the question's intent across these dimensions (3-4 lines each):

# 1. QUESTION COMPREHENSION: Does the SQL address what's actually being asked? Missing key aspects of the question?
# 2. BUSINESS LOGIC ACCURACY: Are business rules correctly implemented? Any logical gaps or misinterpretations?
# 3. DATA REQUIREMENTS: Does the query retrieve all necessary data? Missing tables, columns, or relationships?
# 4. SCOPE APPROPRIATENESS: Is the query scope too broad or narrow? Filtering appropriately?
# 5. IMPLICIT REQUIREMENTS: Does it handle unstated but necessary requirements (like data validation, edge cases)?
# 6. RESULT FORMAT ALIGNMENT: Will the results be in the format expected by the question?

# Specifically identify WHERE intent is missing and WHY it's problematic for answering the original question.""",
#             evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
#             model=model
#         )
    
#     async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
#         test_case = LLMTestCase(
#             input=f"Question: {question}\nGold SQL: {gold_sql}",
#             actual_output=generated_sql,
#             expected_output=gold_sql
#         )
        
#         await self.geval.a_measure(test_case)
        
#         # Try different ways to get the rationale
#         rationale = None
#         for attr in ['reason', 'rationale', 'explanation', 'verbose_logs']:
#             if hasattr(self.geval, attr):
#                 rationale = getattr(self.geval, attr)
#                 break
        
#         if rationale is None:
#             rationale = "Rationale not available - check GEval response format"
        
#         return {
#             "score": self.geval.score,
#             "rationale": rationale,
#             "question": question,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql
#         }

# class SyntaxAccuracyMetric:
#     """Evaluates SQL syntax correctness"""
    
#     def __init__(self, threshold: float = 0.9, model: str = "gpt-4o-mini"):
#         self.name = "syntax_accuracy"
#         self.threshold = threshold
#         self.model = model
#         self.weight = 0.8  # Less important than intent
        
#         self.geval = GEval(
#             name=self.name,
#             criteria="""Evaluate SQL syntax correctness across these areas (3-4 lines each):

# 1. VALID SQL SYNTAX: Is the SQL syntactically correct? Any parsing errors or malformed statements?
# 2. KEYWORD USAGE: Are SQL keywords used properly? Correct spelling and placement?
# 3. CLAUSE ORDERING: Are clauses in the correct order (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY)?
# 4. TABLE/COLUMN REFERENCES: Are all table and column names valid? Proper aliasing?
# 5. OPERATOR USAGE: Are operators (=, <>, LIKE, IN, etc.) used correctly?

# Identify specific syntax issues and explain why they would cause query execution problems.""",
#             evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
#             model=model
#         )
    
#     async def evaluate_async(self, generated_sql: str, **kwargs) -> Dict[str, Any]:
#         test_case = LLMTestCase(
#             input="Evaluate SQL syntax",
#             actual_output=generated_sql,
#             expected_output="Valid SQL syntax"
#         )
        
#         await self.geval.a_measure(test_case)
        
#         # Try different ways to get the rationale
#         rationale = None
#         for attr in ['reason', 'rationale', 'explanation', 'verbose_logs']:
#             if hasattr(self.geval, attr):
#                 rationale = getattr(self.geval, attr)
#                 break
        
#         if rationale is None:
#             rationale = "Rationale not available - check GEval response format"
        
#         return {
#             "score": self.geval.score,
#             "rationale": rationale,
#             "generated_sql": generated_sql
#         }

# class LogicalCorrectnessMetric:
#     """Evaluates logical correctness of SQL queries"""
    
#     def __init__(self, threshold: float = 0.85, model: str = "gpt-4o-mini"):
#         self.name = "logical_correctness"
#         self.threshold = threshold
#         self.model = model
#         self.weight = 1.1
        
#         self.geval = GEval(
#             name=self.name,
#             criteria="""Evaluate logical correctness across these dimensions (3-4 lines each):

# 1. QUERY LOGIC ALIGNMENT: Does the query logic match question requirements? Logical flow correct?
# 2. JOIN CONDITIONS: Are join conditions logically sound? Appropriate join keys and types?
# 3. FILTER CONDITIONS: Do WHERE clauses properly implement business rules? Logical operators correct?
# 4. AGGREGATION LOGIC: Are GROUP BY, HAVING, and aggregate functions applied correctly? Proper grouping levels?
# 5. SUBQUERY LOGIC: Are subqueries logically sound and necessary? Efficient and correct implementation?

# Identify specific logical flaws and explain how they would produce incorrect results.""",
#             evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
#             model=model
#         )
    
#     async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
#         test_case = LLMTestCase(
#             input=f"Question: {question}\nGold SQL: {gold_sql}",
#             actual_output=generated_sql,
#             expected_output=gold_sql
#         )
        
#         await self.geval.a_measure(test_case)
        
#         # Try different ways to get the rationale
#         rationale = None
#         for attr in ['reason', 'rationale', 'explanation', 'verbose_logs']:
#             if hasattr(self.geval, attr):
#                 rationale = getattr(self.geval, attr)
#                 break
        
#         if rationale is None:
#             rationale = "Rationale not available - check GEval response format"
        
#         return {
#             "score": self.geval.score,
#             "rationale": rationale,
#             "question": question,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql
#         }

# # Enhanced debug function to inspect GEval object
# def debug_geval_attributes(geval_obj):
#     """Debug function to see what attributes are available on GEval object"""
#     print("Available GEval attributes:")
#     for attr in dir(geval_obj):
#         if not attr.startswith('_'):
#             try:
#                 value = getattr(geval_obj, attr)
#                 print(f"  {attr}: {type(value)} = {str(value)[:100]}...")
#             except:
#                 print(f"  {attr}: <unable to access>")

# # Example usage
# async def main():
#     # Load your input data
#     with open('D:/data_sci/v4/benchmarking_tool/llm_consortium/core/judge_data/input.json') as f:
#         input_data = json.load(f)
    
#     # Initialize judge
#     judge = SQLJudge(model="gpt-4o-mini")
    
#     # Evaluate all models
#     results = await judge.evaluate_all_models(input_data)
    
#     # Save results
#     judge.save_results(results, 'evaluation_results.json')
    
#     # Print summary
#     print("\nModel Rankings:")
#     for i, model in enumerate(results['rankings']):
#         print(f"{i+1}. {model['model']}: {model['overall_score']:.2f}")

# if __name__ == "__main__":
#     asyncio.run(main())
import os
os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from typing import Dict, Any, List, Union
import json
import asyncio
from tqdm import tqdm
from dotenv import load_dotenv
from collections import defaultdict
load_dotenv()

class SQLJudge:
    """Main class to evaluate SQL generation performance across multiple models"""
    
    def __init__(self, criteria_files: List[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the SQL judge with evaluation criteria
        
        Args:
            criteria_files: List of criteria file paths to load
            model: Model to use for evaluation
        """
        self.model = model
        self.metrics = self._load_metrics(criteria_files)
        
    def _load_metrics(self, criteria_files: List[str]) -> Dict[str, Any]:
        """Load evaluation metrics from criteria files"""
        metrics = {
            "query_metrics": QueryMetricsAnalyzer(model=self.model),
            "intent_understanding": IntentUnderstandingMetric(model=self.model),
            "syntax_accuracy": SyntaxAccuracyMetric(model=self.model),
            "logical_correctness": LogicalCorrectnessMetric(model=self.model)
        }
        return metrics
    
    def _generate_criteria_summary(self, metric_name: str, metric_results: List[Dict], metric_obj: Any) -> str:
        """Generate a summarized rationale for a specific criteria across all queries"""
        if not metric_results:
            return "No evaluations completed for this metric."
        
        # Extract rationales and scores
        rationales = [result.get('rationale', '') for result in metric_results if result.get('rationale')]
        scores = [result.get('score', 0) for result in metric_results if 'score' in result]
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores) if scores else 0
        pass_rate = sum(1 for s in scores if s >= metric_obj.threshold) / len(scores) if scores else 0
        
        # Create summary prompt for LLM
        summary_prompt = f"""
        Analyze the following {len(rationales)} evaluation rationales for the {metric_name} metric and provide a comprehensive summary:

        METRIC: {metric_name.upper()}
        AVERAGE SCORE: {avg_score:.2f}
        PASS RATE: {pass_rate:.1%}
        THRESHOLD: {metric_obj.threshold}

        INDIVIDUAL RATIONALES:
        {chr(10).join([f"{i+1}. {rationale}" for i, rationale in enumerate(rationales[:10])])}
        {'...(showing first 10 of ' + str(len(rationales)) + ' rationales)' if len(rationales) > 10 else ''}

        Please provide a summary that includes:
        1. Common patterns in the evaluations
        2. Most frequent issues identified
        3. Areas where queries performed well
        4. Key recommendations for improvement
        5. Overall assessment of performance for this metric

        Keep the summary concise but comprehensive (4-6 paragraphs).
        """
        
        # Use the same model to generate summary
        try:
            # Create a simple evaluation to get summary
            summary_geval = GEval(
                name=f"{metric_name}_summary",
                criteria="Provide a comprehensive summary analysis based on the evaluation data provided.",
                evaluation_params=[LLMTestCaseParams.INPUT],
                model=self.model
            )
            
            # Create test case for summary
            test_case = LLMTestCase(
                input=summary_prompt,
                actual_output="Summary requested",
                expected_output="Comprehensive summary"
            )
            
            # This is synchronous - we'll need to handle this differently
            # For now, return a basic summary
            common_issues = self._extract_common_issues(rationales)
            
            summary = f"""
SUMMARY FOR {metric_name.upper()} METRIC:

Performance Overview:
Average score of {avg_score:.2f} with {pass_rate:.1%} pass rate indicates {'strong' if avg_score >= 0.8 else 'moderate' if avg_score >= 0.6 else 'weak'} performance in this area.

Common Issues Identified:
{chr(10).join([f"• {issue}" for issue in common_issues[:5]])}

Recommendations:
Based on the evaluation patterns, focus on addressing the most frequent issues identified above to improve performance in {metric_name}.
            """
            
            return summary.strip()
            
        except Exception as e:
            # Fallback to basic summary
            return f"""
SUMMARY FOR {metric_name.upper()} METRIC:
Average Score: {avg_score:.2f}
Pass Rate: {pass_rate:.1%}
Total Evaluations: {len(metric_results)}

Basic analysis of {len(rationales)} rationales shows mixed performance. 
Detailed analysis requires manual review of individual rationales.
Error generating detailed summary: {str(e)}
            """
    
    def _extract_common_issues(self, rationales: List[str]) -> List[str]:
        """Extract common issues from rationales using simple keyword analysis"""
        common_terms = defaultdict(int)
        issue_keywords = [
            'missing', 'incorrect', 'wrong', 'error', 'problem', 'issue', 
            'incomplete', 'unnecessary', 'invalid', 'improper', 'lacking'
        ]
        
        for rationale in rationales:
            rationale_lower = rationale.lower()
            for keyword in issue_keywords:
                if keyword in rationale_lower:
                    # Extract sentence containing the keyword
                    sentences = rationale.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            common_terms[sentence.strip()] += 1
                            break
        
        # Return most common issues
        sorted_issues = sorted(common_terms.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5] if count > 1]
    
    async def evaluate_model(self, model_name: str, responses: List[Dict]) -> Dict[str, Any]:
        """Evaluate a single model's performance"""
        results = {
            "model": model_name,
            "metrics": {},
            "detailed_results": []
        }
        
        # Evaluate each metric
        for metric_name, metric in self.metrics.items():
            print(f"\nEvaluating {metric_name} for {model_name}...")
            
            # Evaluate all responses for this metric
            metric_results = []
            scores = []
            
            for i, response in enumerate(tqdm(responses, desc=f"Evaluating {metric_name}")):
                if 'generated_sql' not in response or 'gold_sql' not in response:
                    continue
                    
                try:
                    result = await metric.evaluate_async(
                        question=response.get('question', ''),
                        generated_sql=response.get('generated_sql', ''),
                        gold_sql=response.get('gold_sql', '')
                    )
                    metric_results.append(result)
                    scores.append(result['score'])
                    
                    # Print individual rationale for each query
                    print(f"\n--- {metric_name.upper()} - Query {i+1} ---")
                    print(f"Question: {response.get('question', '')[:100]}...")
                    print(f"Score: {result['score']}")
                    print(f"Individual Rationale: {result['rationale']}")
                    print("-" * 50)
                    
                except Exception as e:
                    print(f"Error evaluating {metric_name} for query {i+1}: {str(e)}")
                    continue
            
            # Generate summarized rationale for this metric
            criteria_summary = self._generate_criteria_summary(metric_name, metric_results, metric)
            
            # Calculate aggregate metrics
            if scores:
                avg_score = sum(scores) / len(scores)
                pass_rate = sum(1 for s in scores if s >= metric.threshold) / len(scores)
                
                results['metrics'][metric_name] = {
                    "average_score": avg_score,
                    "num_evaluated": len(scores),
                    "pass_rate": pass_rate,
                    "threshold": metric.threshold,
                    "detailed_results": metric_results,
                    "criteria_summary": criteria_summary  # Added summary
                }
                
                # Print summarized rationale
                print(f"\n{'='*60}")
                print(f"CRITERIA SUMMARY FOR {metric_name.upper()}")
                print(f"{'='*60}")
                print(criteria_summary)
                print(f"{'='*60}\n")
                
            else:
                results['metrics'][metric_name] = {
                    "average_score": 0,
                    "num_evaluated": 0,
                    "pass_rate": 0,
                    "threshold": metric.threshold,
                    "detailed_results": [],
                    "criteria_summary": "No successful evaluations completed for this metric."
                }
        
        return results
    
    async def evaluate_all_models(self, input_data: Dict) -> Dict[str, Any]:
        """Evaluate all models in the input data"""
        results = {}
        
        if "model_evaluations" not in input_data:
            raise ValueError("Input data must contain 'model_evaluations' key")
        
        # Evaluate models sequentially to maintain clear output
        for model_name, model_data in input_data['model_evaluations'].items():
            if 'responses' in model_data:
                print(f"\n{'#'*80}")
                print(f"EVALUATING MODEL: {model_name}")
                print(f"{'#'*80}")
                
                try:
                    model_result = await self.evaluate_model(model_name, model_data['responses'])
                    results[model_name] = model_result
                except Exception as e:
                    print(f"Error evaluating model {model_name}: {str(e)}")
                    results[model_name] = {
                        "model": model_name,
                        "metrics": {},
                        "detailed_results": [],
                        "error": str(e)
                    }
        
        # Calculate overall rankings
        ranked_models = self._rank_models(results)
        results['rankings'] = ranked_models
        
        return results
    
    def _rank_models(self, results: Dict) -> List[Dict]:
        """Rank models based on their performance across all metrics"""
        model_scores = []
        
        for model_name, model_data in results.items():
            if not isinstance(model_data, dict) or 'metrics' not in model_data:
                continue
                
            # Calculate weighted average across all metrics
            total_score = 0
            total_weight = 0
            metric_breakdown = {}
            
            for metric_name, metric_data in model_data['metrics'].items():
                if metric_name in self.metrics:
                    weight = getattr(self.metrics[metric_name], 'weight', 1.0)
                    score = metric_data['average_score']
                    total_score += score * weight
                    total_weight += weight
                    metric_breakdown[metric_name] = {
                        'score': score,
                        'weight': weight,
                        'pass_rate': metric_data.get('pass_rate', 0)
                    }
                
            weighted_avg = total_score / total_weight if total_weight > 0 else 0
            model_scores.append({
                'model': model_name,
                'overall_score': weighted_avg,
                'metric_breakdown': metric_breakdown,
                'metrics': model_data['metrics']
            })
        
        # Sort by overall score
        return sorted(model_scores, key=lambda x: x['overall_score'], reverse=True)
    
    def save_results(self, results: Dict, output_path: str) -> None:
        """Save evaluation results to a JSON file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"Results saved to {output_path}")
        
        # Also save a summary report
        summary_path = output_path.replace('.json', '_summary.txt')
        self._save_summary_report(results, summary_path)
    
    def _save_summary_report(self, results: Dict, summary_path: str) -> None:
        """Save a human-readable summary report"""
        with open(summary_path, 'w') as f:
            f.write("SQL EVALUATION SUMMARY REPORT\n")
            f.write("="*50 + "\n\n")
            
            # Model rankings
            f.write("MODEL RANKINGS:\n")
            f.write("-"*20 + "\n")
            for i, model in enumerate(results.get('rankings', [])):
                f.write(f"{i+1}. {model['model']}: {model['overall_score']:.3f}\n")
            f.write("\n")
            
            # Detailed results for each model
            for model_name, model_data in results.items():
                if model_name == 'rankings' or not isinstance(model_data, dict):
                    continue
                    
                f.write(f"\nMODEL: {model_name}\n")
                f.write("="*40 + "\n")
                
                for metric_name, metric_data in model_data.get('metrics', {}).items():
                    f.write(f"\n{metric_name.upper()} METRIC:\n")
                    f.write(f"Average Score: {metric_data.get('average_score', 0):.3f}\n")
                    f.write(f"Pass Rate: {metric_data.get('pass_rate', 0):.1%}\n")
                    f.write(f"Evaluations: {metric_data.get('num_evaluated', 0)}\n")
                    f.write(f"\nCriteria Summary:\n{metric_data.get('criteria_summary', 'No summary available')}\n")
                    f.write("-"*30 + "\n")
        
        print(f"Summary report saved to {summary_path}")

# Enhanced metric classes remain the same but with better rationale extraction
class QueryMetricsAnalyzer:
    """Analyzes basic SQL query metrics"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        self.name = "query_metrics"
        self.threshold = threshold
        self.model = model
        self.weight = 1.0  # Relative importance for ranking
        
        self.geval = GEval(
            name=self.name,
            criteria="""Evaluate the SQL query across these specific dimensions, providing 3-4 lines for each:

1. COLUMN ACCURACY: Are the correct columns selected? Missing or extra columns? Column aliases appropriate?
2. QUERY STRUCTURE: Is the SQL structure proper? Correct syntax and organization? Readable formatting?
3. JOIN QUALITY: Are join conditions appropriate and efficient? Missing joins or incorrect join types?
4. CLAUSE ACCURACY: Are WHERE, GROUP BY, HAVING, ORDER BY clauses correctly implemented?

For each dimension, explain what's correct, what's missing, and why it matters for the query's correctness.""",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            model=model
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Async evaluation of a single query"""
        test_case = LLMTestCase(
            input=f"Question: {question}\nGold SQL: {gold_sql}",
            actual_output=generated_sql,
            expected_output=gold_sql
        )
        
        await self.geval.a_measure(test_case)
        
        # Enhanced rationale extraction
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql
        }
    
    def _extract_rationale(self, geval_obj) -> str:
        """Enhanced rationale extraction with fallback options"""
        rationale_attrs = ['reason', 'rationale', 'explanation', 'verbose_logs', 'evaluation_cost']
        
        for attr in rationale_attrs:
            if hasattr(geval_obj, attr):
                value = getattr(geval_obj, attr)
                if value and str(value).strip():
                    return str(value)
        
        # If no rationale found, provide basic feedback
        return f"Evaluation completed with score {geval_obj.score}. Detailed rationale not available from GEval object."

class IntentUnderstandingMetric:
    """Evaluates how well SQL captures question intent"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        self.name = "intent_understanding"
        self.threshold = threshold
        self.model = model
        self.weight = 1.2  # More important than basic metrics
        
        self.geval = GEval(
            name=self.name,
            criteria="""Evaluate how well the SQL captures the question's intent across these dimensions (3-4 lines each):

1. QUESTION COMPREHENSION: Does the SQL address what's actually being asked? Missing key aspects of the question?
2. BUSINESS LOGIC ACCURACY: Are business rules correctly implemented? Any logical gaps or misinterpretations?
3. DATA REQUIREMENTS: Does the query retrieve all necessary data? Missing tables, columns, or relationships?
4. SCOPE APPROPRIATENESS: Is the query scope too broad or narrow? Filtering appropriately?
5. IMPLICIT REQUIREMENTS: Does it handle unstated but necessary requirements (like data validation, edge cases)?
6. RESULT FORMAT ALIGNMENT: Will the results be in the format expected by the question?

Specifically identify WHERE intent is missing and WHY it's problematic for answering the original question.""",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            model=model
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        test_case = LLMTestCase(
            input=f"Question: {question}\nGold SQL: {gold_sql}",
            actual_output=generated_sql,
            expected_output=gold_sql
        )
        
        await self.geval.a_measure(test_case)
        
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql
        }
    
    def _extract_rationale(self, geval_obj) -> str:
        """Enhanced rationale extraction with fallback options"""
        rationale_attrs = ['reason', 'rationale', 'explanation', 'verbose_logs', 'evaluation_cost']
        
        for attr in rationale_attrs:
            if hasattr(geval_obj, attr):
                value = getattr(geval_obj, attr)
                if value and str(value).strip():
                    return str(value)
        
        return f"Evaluation completed with score {geval_obj.score}. Detailed rationale not available from GEval object."

class SyntaxAccuracyMetric:
    """Evaluates SQL syntax correctness"""
    
    def __init__(self, threshold: float = 0.9, model: str = "gpt-4o-mini"):
        self.name = "syntax_accuracy"
        self.threshold = threshold
        self.model = model
        self.weight = 0.8  # Less important than intent
        
        self.geval = GEval(
            name=self.name,
            criteria="""Evaluate SQL syntax correctness across these areas (3-4 lines each):

1. VALID SQL SYNTAX: Is the SQL syntactically correct? Any parsing errors or malformed statements?
2. KEYWORD USAGE: Are SQL keywords used properly? Correct spelling and placement?
3. CLAUSE ORDERING: Are clauses in the correct order (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY)?
4. TABLE/COLUMN REFERENCES: Are all table and column names valid? Proper aliasing?
5. OPERATOR USAGE: Are operators (=, <>, LIKE, IN, etc.) used correctly?

Identify specific syntax issues and explain why they would cause query execution problems.""",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            model=model
        )
    
    async def evaluate_async(self, generated_sql: str, **kwargs) -> Dict[str, Any]:
        test_case = LLMTestCase(
            input="Evaluate SQL syntax",
            actual_output=generated_sql,
            expected_output="Valid SQL syntax"
        )
        
        await self.geval.a_measure(test_case)
        
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "generated_sql": generated_sql
        }
    
    def _extract_rationale(self, geval_obj) -> str:
        """Enhanced rationale extraction with fallback options"""
        rationale_attrs = ['reason', 'rationale', 'explanation', 'verbose_logs', 'evaluation_cost']
        
        for attr in rationale_attrs:
            if hasattr(geval_obj, attr):
                value = getattr(geval_obj, attr)
                if value and str(value).strip():
                    return str(value)
        
        return f"Evaluation completed with score {geval_obj.score}. Detailed rationale not available from GEval object."

class LogicalCorrectnessMetric:
    """Evaluates logical correctness of SQL queries"""
    
    def __init__(self, threshold: float = 0.85, model: str = "gpt-4o-mini"):
        self.name = "logical_correctness"
        self.threshold = threshold
        self.model = model
        self.weight = 1.1
        
        self.geval = GEval(
            name=self.name,
            criteria="""Evaluate logical correctness across these dimensions (3-4 lines each):

1. QUERY LOGIC ALIGNMENT: Does the query logic match question requirements? Logical flow correct?
2. JOIN CONDITIONS: Are join conditions logically sound? Appropriate join keys and types?
3. FILTER CONDITIONS: Do WHERE clauses properly implement business rules? Logical operators correct?
4. AGGREGATION LOGIC: Are GROUP BY, HAVING, and aggregate functions applied correctly? Proper grouping levels?
5. SUBQUERY LOGIC: Are subqueries logically sound and necessary? Efficient and correct implementation?

Identify specific logical flaws and explain how they would produce incorrect results.""",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            model=model
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        test_case = LLMTestCase(
            input=f"Question: {question}\nGold SQL: {gold_sql}",
            actual_output=generated_sql,
            expected_output=gold_sql
        )
        
        await self.geval.a_measure(test_case)
        
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql
        }
    
    def _extract_rationale(self, geval_obj) -> str:
        """Enhanced rationale extraction with fallback options"""
        rationale_attrs = ['reason', 'rationale', 'explanation', 'verbose_logs', 'evaluation_cost']
        
        for attr in rationale_attrs:
            if hasattr(geval_obj, attr):
                value = getattr(geval_obj, attr)
                if value and str(value).strip():
                    return str(value)
        
        return f"Evaluation completed with score {geval_obj.score}. Detailed rationale not available from GEval object."

# Enhanced debug function
def debug_geval_attributes(geval_obj):
    """Debug function to see what attributes are available on GEval object"""
    print("Available GEval attributes:")
    for attr in dir(geval_obj):
        if not attr.startswith('_'):
            try:
                value = getattr(geval_obj, attr)
                print(f"  {attr}: {type(value)} = {str(value)[:100]}...")
            except:
                print(f"  {attr}: <unable to access>")

# Example usage
async def main():
    # Load your input data
    with open('D:/data_sci/v4/benchmarking_tool/llm_consortium/core/judge_data/input.json') as f:
        input_data = json.load(f)
    
    # Initialize judge
    judge = SQLJudge(model="gpt-4o-mini")
    
    # Evaluate all models
    results = await judge.evaluate_all_models(input_data)
    
    # Save results
    judge.save_results(results, 'evaluation_results.json')
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL MODEL RANKINGS")
    print("="*60)
    for i, model in enumerate(results['rankings']):
        print(f"{i+1}. {model['model']}: {model['overall_score']:.3f}")
        for metric_name, metric_info in model['metric_breakdown'].items():
            print(f"   - {metric_name}: {metric_info['score']:.3f} (pass rate: {metric_info['pass_rate']:.1%})")
        print()

if __name__ == "__main__":
    asyncio.run(main())