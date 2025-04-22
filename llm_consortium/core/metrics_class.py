# metrics.py
from typing import List, Dict
import pandas as pd
from sklearn.metrics import classification_report
from deepeval.metrics import HallucinationMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase


class ClassificationMetricsHandler:
    def __init__(self, valid_classes: List[str] = None):
        self.valid_classes = valid_classes
        self.test_cases: List[LLMTestCase] = []
        
    def create_test_cases(self, results: List[Dict]) -> List[LLMTestCase]:
        """Convert consortium results to DeepEval test cases"""
        test_cases = []
        for result in results:
            test_case = LLMTestCase(
                input=result["question"],
                actual_output=result["arbiter_decision"]["predicted_class"],
                expected_output=result["ground_truth"],
                retrieval_context=self.valid_classes  # Use valid classes as context
            )
            test_cases.append(test_case)
        self.test_cases = test_cases
        return test_cases

    def calculate_metrics(self, results_df: pd.DataFrame) -> Dict:
        """Calculate traditional classification metrics"""
        metrics = {}
        
        # Model-level metrics
        model_cols = [col for col in results_df.columns if col.startswith("model_")]
        for model in model_cols + ["arbiter"]:
            report = classification_report(
                results_df["ground_truth"],
                results_df[model],
                output_dict=True,
                zero_division=0
            )
            metrics[model] = {
                "accuracy": report["accuracy"],
                "precision": report["weighted avg"]["precision"],
                "recall": report["weighted avg"]["recall"],
                "f1": report["weighted avg"]["f1-score"]
            }
        
        return metrics

    def evaluate_with_deepeval(self) -> Dict:
        """Run DeepEval evaluation metrics"""
        if not self.test_cases:
            raise ValueError("No test cases created. Call create_test_cases first.")
            
        hallucination_metric = HallucinationMetric(threshold=0.7)
        contextual_relevancy_metric = ContextualRelevancyMetric(threshold=0.5)

        # Evaluate each test case using each metric
        for test_case in self.test_cases:
            hallucination_metric.evaluate(test_case)
            contextual_relevancy_metric.evaluate(test_case)

        return {
            "hallucination_score": hallucination_metric.score,
            "contextual_relevancy_score": contextual_relevancy_metric.score
        }


    def full_evaluation(self, results: List[Dict]) -> Dict:
        """Run complete evaluation pipeline"""
        # Convert to DataFrame
        results_df = pd.DataFrame([{
            'question': r["question"],
            'ground_truth': r["ground_truth"],
            **{f'model_{i}': resp["predicted_class"] 
               for i, resp in enumerate(r["model_responses"])},
            'arbiter': r["arbiter_decision"]["predicted_class"]
        } for r in results])
        
        # Create test cases
        self.create_test_cases(results)
        
        return {
            "traditional_metrics": self.calculate_metrics(results_df),
            "deepeval_metrics": self.evaluate_with_deepeval()
        }