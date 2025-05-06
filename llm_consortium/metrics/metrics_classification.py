import sys
import os
from typing import List, Dict, Union, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score

# Import deepeval for LLM evaluation metrics
try:
    from deepeval.metrics import HallucinationMetric, ContextualRelevanceMetric, FactualConsistencyMetric
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    print("Warning: deepeval package not found. Install with 'pip install deepeval' to use deepeval metrics.")
    DEEPEVAL_AVAILABLE = False

class ClassificationMetricsHandler:
    """
    Class for evaluating classification tasks using various metrics
    """
    def __init__(self, valid_classes: List[str] = None):
        self.valid_classes = valid_classes

    def calculate_metrics_single_model(self, results_df: pd.DataFrame, model_name: str) -> Dict[str, float]:
        """
        Calculate metrics for a single model's results
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth and predicted_class columns
            model_name (str): Name of the model being evaluated
            
        Returns:
            dict: Metrics including accuracy, precision, recall, and F1 score
        """
        if results_df.empty:
            return {
                "model": model_name,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "total_samples": 0
            }
            # Filter out invalid predictions
        if self.valid_classes:
            valid_mask = results_df["predicted_class"].isin(self.valid_classes)
            results_df = results_df[valid_mask].copy()
            
        # Check if the required columns exist
        required_columns = ["ground_truth", "predicted_class"]
        missing_columns = [col for col in required_columns if col not in results_df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame is missing required columns: {', '.join(missing_columns)}")
        
        y_true = results_df["ground_truth"]
        y_pred = results_df["predicted_class"]
        
        # Calculate metrics
        try:
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            return {
                "model": model_name,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "total_samples": len(results_df)
            }
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {
                "model": model_name,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "total_samples": len(results_df),
                "error": str(e)
            }
    
    def calculate_metrics_multiple_models(self, results: Union[pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate metrics for multiple models
        
        Args:
            results: Either a DataFrame or a list of dictionaries containing model predictions
            
        Returns:
            dict: Dictionary of model metrics
        """
        metrics = {}
        
        # Convert list to DataFrame if needed
        if isinstance(results, list):
            # Assuming each item in results has model predictions
            results_df = pd.DataFrame([{
                'question': r["question"],
                'ground_truth': r["ground_truth"],
                **{f'model_{i}': resp["predicted_class"] 
                   for i, resp in enumerate(r["raw_responses"])},
                'arbiter': r["best"]["final_class"] if "best" in r else None
            } for r in results])
        else:
            results_df = results
        
        # Model-level metrics
        model_cols = [col for col in results_df.columns if col.startswith("model_")]
        for model_col in model_cols:
            # Create temporary DataFrame with just this model's predictions
            temp_df = pd.DataFrame({
                "ground_truth": results_df["ground_truth"],
                "predicted_class": results_df[model_col]
            })
            metrics[model_col] = self.calculate_metrics_single_model(temp_df, model_col)
        
        # Arbiter metrics if available
        if 'arbiter' in results_df.columns and not results_df['arbiter'].isna().all():
            temp_df = pd.DataFrame({
                "ground_truth": results_df["ground_truth"],
                "predicted_class": results_df["arbiter"]
            })
            metrics["arbiter"] = self.calculate_metrics_single_model(temp_df, "arbiter")
            
        return metrics
        
    def get_confusion_matrix(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate confusion matrix data
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth and predicted_class columns
            
        Returns:
            dict: Confusion matrix data suitable for visualization
        """
        from sklearn.metrics import confusion_matrix
        
        # Get unique classes from both ground truth and predictions
        if self.valid_classes:
            classes = self.valid_classes
        else:
            classes = sorted(set(results_df["ground_truth"].unique()) | 
                           set(results_df["predicted_class"].unique()))
        
        # Calculate confusion matrix
        cm = confusion_matrix(
            results_df["ground_truth"], 
            results_df["predicted_class"],
            labels=classes
        )
        
        # Format for return
        return {
            "matrix": cm.tolist(),
            "classes": classes
        }
        
    def get_per_class_metrics(self, results_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate per-class precision, recall, and F1 scores
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth and predicted_class columns
            
        Returns:
            dict: Per-class metrics
        """
        report = classification_report(
            results_df["ground_truth"],
            results_df["predicted_class"],
            output_dict=True,
            zero_division=0
        )
        
        # Extract per-class metrics, excluding averages
        per_class = {}
        for class_name, metrics in report.items():
            if class_name not in ['accuracy', 'macro avg', 'weighted avg', 'samples avg']:
                per_class[class_name] = {
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1-score": metrics["f1-score"],
                    "support": metrics["support"]
                }
                
        return per_class
        
    def calculate_confidence_correlation(self, results_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate correlation between confidence and correctness
        
        Args:
            results_df (pd.DataFrame): DataFrame with confidence and correct columns
            
        Returns:
            dict: Correlation metrics
        """
        if "confidence" not in results_df.columns or "correct" not in results_df.columns:
            return {"correlation": 0.0, "error": "Missing required columns"}
            
        # Convert correct to numeric (True=1, False=0)
        correct_numeric = results_df["correct"].astype(int)
        
        # Calculate correlation
        correlation = np.corrcoef(results_df["confidence"], correct_numeric)[0, 1]
        
        # Group by confidence bins to see accuracy trend
        results_df["confidence_bin"] = pd.cut(results_df["confidence"], bins=10)
        accuracy_by_confidence = results_df.groupby("confidence_bin")["correct"].mean()
        
        return {
            "correlation": correlation,
            "accuracy_by_confidence": {
                "bins": [str(b) for b in accuracy_by_confidence.index],
                "values": accuracy_by_confidence.values.tolist()
            }
        }
    
    def calculate_hallucination_rate(self, results_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate hallucination rate based on invalid class predictions.
        Uses deepeval's HallucinationMetric when available.
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth and predicted_class columns
            
        Returns:
            dict: Hallucination metrics including rate and examples
        """
        # Basic hallucination detection based on valid classes
        if not self.valid_classes:
            return {"hallucination_rate": 0.0, "error": "No valid classes defined"}
            
        # Identify hallucinations as predictions not in valid classes
        hallucinated = ~results_df["predicted_class"].isin(self.valid_classes)
        hallucination_rate = hallucinated.mean()
        
        # Extract examples of hallucinations
        hallucination_examples = []
        if "question" in results_df.columns:
            hallucination_samples = results_df[hallucinated].sample(min(5, hallucinated.sum()))
            for _, row in hallucination_samples.iterrows():
                hallucination_examples.append({
                    "question": row.get("question", "N/A"),
                    "ground_truth": row["ground_truth"],
                    "predicted_class": row["predicted_class"]
                })
        
        results = {
            "hallucination_rate": hallucination_rate,
            "total_hallucinations": hallucinated.sum(),
            "examples": hallucination_examples if hallucination_examples else None
        }
        
        # Use deepeval's HallucinationMetric when available and appropriate columns exist
        if DEEPEVAL_AVAILABLE and "context" in results_df.columns and "predicted_class" in results_df.columns:
            try:
                # Sample up to 50 rows for deepeval analysis (for efficiency)
                sample_size = min(50, len(results_df))
                sample_df = results_df.sample(sample_size)
                
                # Create test cases for deepeval
                test_cases = []
                for _, row in sample_df.iterrows():
                    test_case = LLMTestCase(
                        input=row.get("question", ""),
                        actual_output=row["predicted_class"],
                        context=[row.get("context", "")]
                    )
                    test_cases.append(test_case)
                
                # Run deepeval hallucination metric
                hallucination_metric = HallucinationMetric()
                hallucination_metric.evaluate(test_cases)
                
                # Add deepeval results
                results["deepeval_hallucination_score"] = hallucination_metric.score
                results["deepeval_evaluation_count"] = len(test_cases)
                results["deepeval_threshold"] = hallucination_metric.threshold
                results["deepeval_passed"] = hallucination_metric.score >= hallucination_metric.threshold
            except Exception as e:
                results["deepeval_error"] = str(e)
        
        return results
    
    def calculate_semantic_similarity(self, results_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate semantic similarity between predicted and ground truth classes.
        Uses deepeval's ContextualRelevanceMetric when available.
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth, predicted_class and 
                                      optionally embedding columns
            
        Returns:
            dict: Semantic similarity metrics
        """
        results = {}
        
        try:
            # Check if embeddings are available for custom similarity calculation
            if "ground_truth_embedding" in results_df.columns and "prediction_embedding" in results_df.columns:
                # Calculate cosine similarity between embeddings
                from sklearn.metrics.pairwise import cosine_similarity
                
                embeddings_gt = np.vstack(results_df["ground_truth_embedding"].values)
                embeddings_pred = np.vstack(results_df["prediction_embedding"].values)
                
                similarities = np.diagonal(cosine_similarity(embeddings_gt, embeddings_pred))
                avg_similarity = similarities.mean()
                
                # Group by correctness to compare semantic similarity
                results_df["correct"] = results_df["ground_truth"] == results_df["predicted_class"]
                
                # Calculate average similarity for correct and incorrect predictions
                # If 'similarity' column exists use it, otherwise compute from embeddings
                if "similarity" in results_df.columns:
                    avg_similarity_correct = results_df[results_df["correct"]]["similarity"].mean()
                    avg_similarity_incorrect = results_df[~results_df["correct"]]["similarity"].mean()
                else:
                    # Add similarity to DataFrame
                    results_df["similarity"] = similarities
                    avg_similarity_correct = results_df[results_df["correct"]]["similarity"].mean()
                    avg_similarity_incorrect = results_df[~results_df["correct"]]["similarity"].mean()
                
                results.update({
                    "average_semantic_similarity": avg_similarity,
                    "similarity_when_correct": avg_similarity_correct,
                    "similarity_when_incorrect": avg_similarity_incorrect,
                    "similarity_distribution": {
                        "min": similarities.min(),
                        "q1": np.percentile(similarities, 25),
                        "median": np.median(similarities),
                        "q3": np.percentile(similarities, 75),
                        "max": similarities.max()
                    }
                })
            else:
                results["custom_similarity_error"] = "Embeddings not available in the DataFrame"
        except Exception as e:
            results["custom_similarity_error"] = f"Error calculating custom semantic similarity: {str(e)}"
        
        # Use deepeval's ContextualRelevanceMetric when available
        if DEEPEVAL_AVAILABLE and "context" in results_df.columns and "predicted_class" in results_df.columns:
            try:
                # Sample up to 50 rows for deepeval analysis (for efficiency)
                sample_size = min(50, len(results_df))
                sample_df = results_df.sample(sample_size)
                
                # Create test cases for deepeval
                test_cases = []
                for _, row in sample_df.iterrows():
                    # Create test case with input, output and context
                    test_case = LLMTestCase(
                        input=row.get("question", ""),
                        actual_output=row["predicted_class"],
                        context=[row.get("context", "")]
                    )
                    test_cases.append(test_case)
                
                # Run deepeval contextual relevance metric
                relevance_metric = ContextualRelevanceMetric()
                relevance_metric.evaluate(test_cases)
                
                # Add deepeval results
                results["deepeval_relevance_score"] = relevance_metric.score
                results["deepeval_evaluation_count"] = len(test_cases)
                results["deepeval_threshold"] = relevance_metric.threshold
                results["deepeval_passed"] = relevance_metric.score >= relevance_metric.threshold
            except Exception as e:
                results["deepeval_error"] = str(e)
        
        return results
    
    def calculate_factual_consistency(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate factual consistency using deepeval's FactualConsistencyMetric.
        
        Args:
            results_df (pd.DataFrame): DataFrame with ground_truth, predicted_class, and context
            
        Returns:
            dict: Factual consistency metrics
        """
        results = {"factual_consistency_score": None}
        
        # Use deepeval's FactualConsistencyMetric when available
        if DEEPEVAL_AVAILABLE and "context" in results_df.columns and "predicted_class" in results_df.columns:
            try:
                # Sample up to 50 rows for deepeval analysis (for efficiency)
                sample_size = min(50, len(results_df))
                sample_df = results_df.sample(sample_size)
                
                # Create test cases for deepeval
                test_cases = []
                for _, row in sample_df.iterrows():
                    test_case = LLMTestCase(
                        input=row.get("question", ""),
                        actual_output=row["predicted_class"],
                        context=[row.get("context", "")]
                    )
                    test_cases.append(test_case)
                
                # Run deepeval factual consistency metric
                factual_metric = FactualConsistencyMetric()
                factual_metric.evaluate(test_cases)
                
                # Add deepeval results
                results["factual_consistency_score"] = factual_metric.score
                results["deepeval_evaluation_count"] = len(test_cases)
                results["deepeval_threshold"] = factual_metric.threshold
                results["deepeval_passed"] = factual_metric.score >= factual_metric.threshold
            except Exception as e:
                results["deepeval_error"] = str(e)
                
        return results
    
    def calculate_robustness_score(self, results_df: pd.DataFrame, perturbation_groups: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Calculate robustness score based on prediction consistency across perturbations
        
        Args:
            results_df (pd.DataFrame): DataFrame with instance_id, perturbation_type, and predicted_class
            perturbation_groups (dict): Dictionary mapping original instance IDs to perturbed instance IDs
            
        Returns:
            dict: Robustness metrics
        """
        if "instance_id" not in results_df.columns or "perturbation_type" not in results_df.columns:
            return {"robustness_score": 0.0, "error": "Missing required columns for robustness calculation"}
            
        try:
            # If perturbation groups not provided, try to infer from instance_id
            if not perturbation_groups:
                # Assume format like "instance_123" and "instance_123_perturbed_1"
                base_instances = results_df[results_df["perturbation_type"] == "original"]["instance_id"].unique()
                perturbation_groups = {}
                
                for base_id in base_instances:
                    # Find all perturbations related to this base instance
                    perturbed_ids = results_df[
                        (results_df["perturbation_type"] != "original") & 
                        (results_df["instance_id"].str.startswith(base_id))
                    ]["instance_id"].unique().tolist()
                    
                    perturbation_groups[base_id] = perturbed_ids
            
            # Calculate robustness as consistency of predictions
            robustness_scores = []
            
            for base_id, perturbed_ids in perturbation_groups.items():
                if not perturbed_ids:
                    continue
                    
                # Get original prediction
                original_pred = results_df[results_df["instance_id"] == base_id]["predicted_class"].iloc[0]
                
                # Get perturbed predictions
                perturbed_preds = results_df[results_df["instance_id"].isin(perturbed_ids)]["predicted_class"].tolist()
                
                # Calculate consistency (what percentage match the original prediction)
                consistency = sum(1 for p in perturbed_preds if p == original_pred) / len(perturbed_preds)
                robustness_scores.append(consistency)
            
            # Aggregate robustness score
            if robustness_scores:
                avg_robustness = sum(robustness_scores) / len(robustness_scores)
                
                return {
                    "robustness_score": avg_robustness,
                    "num_perturbation_groups": len(perturbation_groups),
                    "score_distribution": {
                        "min": min(robustness_scores),
                        "max": max(robustness_scores),
                        "median": np.median(robustness_scores)
                    }
                }
            else:
                return {"robustness_score": 0.0, "error": "No valid perturbation groups found"}
                
        except Exception as e:
            return {"robustness_score": 0.0, "error": f"Error calculating robustness: {str(e)}"}
        
    def full_evaluation(self, results_df: pd.DataFrame, model_name: str) -> Dict[str, Any]:
        """
        Run complete evaluation for a model's results, including deepeval metrics when available
        
        Args:
            results_df (pd.DataFrame): DataFrame with model results
            model_name (str): Name of the model being evaluated
            
        Returns:
            dict: Complete evaluation metrics
        """
        eval_results = {
            "overall_metrics": self.calculate_metrics_single_model(results_df, model_name),
            "confusion_matrix": self.get_confusion_matrix(results_df),
            "per_class_metrics": self.get_per_class_metrics(results_df),
            "confidence_analysis": self.calculate_confidence_correlation(results_df) 
                if "confidence" in results_df.columns else None,
        }
        
        # Add deepeval and advanced metrics when data is available
        if self.valid_classes:
            eval_results["hallucination_metrics"] = self.calculate_hallucination_rate(results_df)
            
        if "ground_truth_embedding" in results_df.columns or "context" in results_df.columns:
            eval_results["semantic_similarity"] = self.calculate_semantic_similarity(results_df)
            
        if "instance_id" in results_df.columns and "perturbation_type" in results_df.columns:
            eval_results["robustness_score"] = self.calculate_robustness_score(results_df)
            
        if "context" in results_df.columns and DEEPEVAL_AVAILABLE:
            eval_results["factual_consistency"] = self.calculate_factual_consistency(results_df)
            
        # Add deepeval availability information
        eval_results["deepeval_available"] = DEEPEVAL_AVAILABLE
        
        return eval_results