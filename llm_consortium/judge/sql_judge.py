"""
SQL Evaluation Runner - Main execution script for evaluating SQL generation models
"""

import os
import json
import asyncio
from typing import Dict, List
from dotenv import load_dotenv

# Suppress DeepEval signals for clean execution
os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"

# Import your custom metrics
from .judge_base import SQLJudgeBaseMetric
from .query_metrics import QueryMetricsAnalyzer
from .logical_correctness import LogicalCorrectnessMetric


load_dotenv()


class SQLEvaluationRunner:
    """Main runner class for SQL evaluation system"""
    
    def __init__(self, model: str = "gpt-4o-mini", config_path: str = None):
        """
        Initialize the evaluation runner
        
        Args:
            model: Model to use for evaluation (default: gpt-4o-mini)
            config_path: Optional path to configuration file
        """
        self.model = model
        self.config = self._load_config(config_path) if config_path else {}
        self.metrics = self._initialize_metrics()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}
    
    def _initialize_metrics(self) -> Dict[str, SQLJudgeBaseMetric]:
        """Initialize all evaluation metrics"""
        metrics = {}
        
        # Get thresholds from config or use defaults
        thresholds = self.config.get('thresholds', {})
        
        # Initialize each metric
        metrics['query_metrics'] = QueryMetricsAnalyzer(
            threshold=thresholds.get('query_metrics', 0.8),
            model=self.model
        )
        
        metrics['logical_correctness'] = LogicalCorrectnessMetric(
            threshold=thresholds.get('logical_correctness', 0.85),
            model=self.model
        )
        
        # Add other metrics as you implement them
        # metrics['intent_understanding'] = IntentUnderstandingMetric(
        #     threshold=thresholds.get('intent_understanding', 0.8),
        #     model=self.model
        # )
        
        # metrics['syntax_accuracy'] = SyntaxAccuracyMetric(
        #     threshold=thresholds.get('syntax_accuracy', 0.9),
        #     model=self.model
        # )
        
        return metrics
    
    async def evaluate_single_model(self, model_name: str, responses: List[Dict]) -> Dict:
        """
        Evaluate a single model's responses
        
        Args:
            model_name: Name of the model being evaluated
            responses: List of response dictionaries containing question, generated_sql, gold_sql
            
        Returns:
            Dictionary containing evaluation results
        """
        print(f"\n{'='*60}")
        print(f"EVALUATING MODEL: {model_name}")
        print(f"{'='*60}")
        
        results = {
            "model": model_name,
            "metrics": {},
            "summary": {}
        }
        
        # Evaluate each metric
        for metric_name, metric in self.metrics.items():
            print(f"\nEvaluating {metric_name}...")
            
            metric_results = []
            scores = []
            
            for i, response in enumerate(responses):
                if not self._validate_response(response):
                    print(f"Skipping invalid response {i+1}")
                    continue
                
                try:
                    # Evaluate this response
                    result = await metric.evaluate_async(
                        question=response.get('question', ''),
                        generated_sql=response.get('generated_sql', ''),
                        gold_sql=response.get('gold_sql', '')
                    )
                    
                    metric_results.append(result)
                    scores.append(result['score'])
                    
                    # Print progress
                    if (i + 1) % 10 == 0 or i == len(responses) - 1:
                        print(f"  Processed {i+1}/{len(responses)} queries")
                    
                except Exception as e:
                    print(f"  Error evaluating query {i+1}: {str(e)}")
                    continue
            
            # Calculate metric summary
            if scores:
                avg_score = sum(scores) / len(scores)
                pass_rate = sum(1 for s in scores if s >= metric.threshold) / len(scores)
                
                results['metrics'][metric_name] = {
                    "average_score": avg_score,
                    "pass_rate": pass_rate,
                    "num_evaluated": len(scores),
                    "threshold": metric.threshold,
                    "weight": getattr(metric, 'weight', 1.0),
                    "detailed_results": metric_results
                }
                
                print(f"  {metric_name}: Avg={avg_score:.3f}, Pass Rate={pass_rate:.1%}")
            else:
                results['metrics'][metric_name] = {
                    "average_score": 0,
                    "pass_rate": 0,
                    "num_evaluated": 0,
                    "threshold": metric.threshold,
                    "weight": getattr(metric, 'weight', 1.0),
                    "detailed_results": []
                }
                print(f"  {metric_name}: No valid evaluations completed")
        
        # Calculate overall score
        results['summary'] = self._calculate_model_summary(results['metrics'])
        
        return results
    
    def _validate_response(self, response: Dict) -> bool:
        """Validate that response contains required fields"""
        required_fields = ['question', 'generated_sql', 'gold_sql']
        return all(field in response and response[field] for field in required_fields)
    
    def _calculate_model_summary(self, metrics: Dict) -> Dict:
        """Calculate overall model performance summary"""
        if not metrics:
            return {"overall_score": 0, "weighted_score": 0}
        
        total_score = 0
        total_weight = 0
        metric_scores = []
        
        for metric_name, metric_data in metrics.items():
            score = metric_data['average_score']
            weight = metric_data.get('weight', 1.0)
            
            total_score += score * weight
            total_weight += weight
            metric_scores.append(score)
        
        return {
            "overall_score": sum(metric_scores) / len(metric_scores) if metric_scores else 0,
            "weighted_score": total_score / total_weight if total_weight > 0 else 0,
            "num_metrics": len(metrics)
        }
    
    async def evaluate_all_models(self, input_data: Dict) -> Dict:
        """
        Evaluate all models in the input data
        
        Args:
            input_data: Dictionary containing model evaluations
            
        Returns:
            Complete evaluation results with rankings
        """
        if "model_evaluations" not in input_data:
            raise ValueError("Input data must contain 'model_evaluations' key")
        
        results = {}
        model_summaries = []
        
        # Evaluate each model
        for model_name, model_data in input_data['model_evaluations'].items():
            if 'responses' not in model_data:
                print(f"Warning: No responses found for model {model_name}")
                continue
            
            try:
                model_result = await self.evaluate_single_model(
                    model_name, 
                    model_data['responses']
                )
                results[model_name] = model_result
                model_summaries.append({
                    'model': model_name,
                    'overall_score': model_result['summary']['overall_score'],
                    'weighted_score': model_result['summary']['weighted_score']
                })
                
            except Exception as e:
                print(f"Error evaluating model {model_name}: {str(e)}")
                results[model_name] = {
                    "model": model_name,
                    "metrics": {},
                    "summary": {"overall_score": 0, "weighted_score": 0},
                    "error": str(e)
                }
        
        # Add rankings
        results['rankings'] = {
            'by_overall_score': sorted(model_summaries, 
                                     key=lambda x: x['overall_score'], 
                                     reverse=True),
            'by_weighted_score': sorted(model_summaries, 
                                      key=lambda x: x['weighted_score'], 
                                      reverse=True)
        }
        
        return results
    
    def save_results(self, results: Dict, output_path: str) -> None:
        """Save results to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults saved to: {output_path}")
            
            # Also save a summary report
            summary_path = output_path.replace('.json', '_summary.txt')
            self._save_summary_report(results, summary_path)
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def _save_summary_report(self, results: Dict, summary_path: str) -> None:
        """Save human-readable summary report"""
        try:
            with open(summary_path, 'w') as f:
                f.write("SQL EVALUATION SUMMARY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Overall rankings
                if 'rankings' in results:
                    f.write("MODEL RANKINGS (by Overall Score):\n")
                    f.write("-" * 30 + "\n")
                    for i, model in enumerate(results['rankings']['by_overall_score']):
                        f.write(f"{i+1}. {model['model']}: {model['overall_score']:.3f}\n")
                    f.write("\n")
                
                # Detailed results for each model
                for model_name, model_data in results.items():
                    if model_name == 'rankings' or not isinstance(model_data, dict):
                        continue
                    
                    f.write(f"\nMODEL: {model_name}\n")
                    f.write("=" * 40 + "\n")
                    
                    if 'summary' in model_data:
                        summary = model_data['summary']
                        f.write(f"Overall Score: {summary.get('overall_score', 0):.3f}\n")
                        f.write(f"Weighted Score: {summary.get('weighted_score', 0):.3f}\n\n")
                    
                    # Metric details
                    for metric_name, metric_data in model_data.get('metrics', {}).items():
                        f.write(f"{metric_name.upper()}:\n")
                        f.write(f"  Average Score: {metric_data.get('average_score', 0):.3f}\n")
                        f.write(f"  Pass Rate: {metric_data.get('pass_rate', 0):.1%}\n")
                        f.write(f"  Evaluations: {metric_data.get('num_evaluated', 0)}\n")
                        f.write(f"  Threshold: {metric_data.get('threshold', 0):.2f}\n\n")
            
            print(f"Summary report saved to: {summary_path}")
            
        except Exception as e:
            print(f"Error saving summary report: {e}")
    
    def print_final_summary(self, results: Dict) -> None:
        """Print final summary to console"""
        print("\n" + "=" * 60)
        print("FINAL EVALUATION SUMMARY")
        print("=" * 60)
        
        if 'rankings' in results and results['rankings']['by_overall_score']:
            print("\nModel Rankings (by Overall Score):")
            print("-" * 40)
            for i, model in enumerate(results['rankings']['by_overall_score']):
                print(f"{i+1:2d}. {model['model']:<20} {model['overall_score']:.3f}")
            
            # Show metric breakdown for top model
            top_model = results['rankings']['by_overall_score'][0]['model']
            if top_model in results:
                print(f"\nTop Model ({top_model}) Breakdown:")
                print("-" * 30)
                for metric_name, metric_data in results[top_model].get('metrics', {}).items():
                    print(f"  {metric_name:<20} {metric_data.get('average_score', 0):.3f}")
        else:
            print("No valid results to display")


# Main execution function
async def main():
    """Main execution function"""
    
    # Configuration
    INPUT_FILE = "D:/data_sci/v4/benchmarking_tool/llm_consortium/core/judge_data/input.json"
    OUTPUT_FILE = "D:/data_sci/v4/benchmarking_tool/llm_consortium/core/judge_data/evaluation.json"
    MODEL = "gpt-4o-mini"
    
    print("SQL Evaluation System")
    print("=" * 50)
    
    # Load input data
    try:
        with open(INPUT_FILE, 'r') as f:
            input_data = json.load(f)
        print(f"Loaded input data from: {INPUT_FILE}")
    except Exception as e:
        print(f"Error loading input file {INPUT_FILE}: {e}")
        return
    
    # Initialize runner
    runner = SQLEvaluationRunner(model=MODEL)
    print(f"Initialized evaluation runner with model: {MODEL}")
    print(f"Available metrics: {list(runner.metrics.keys())}")
    
    # Run evaluation
    try:
        print("\nStarting evaluation...")
        results = await runner.evaluate_all_models(input_data)
        
        # Save results
        runner.save_results(results, OUTPUT_FILE)
        
        # Print summary
        runner.print_final_summary(results)
        
        print(f"\nEvaluation completed successfully!")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())