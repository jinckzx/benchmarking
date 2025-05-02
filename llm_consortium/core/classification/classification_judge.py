import json
import asyncio
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    roc_auc_score, 
    confusion_matrix,
    balanced_accuracy_score,
    matthews_corrcoef
)
from ..client_init import llm
from ...utils.logging import logger

class ClassificationJudge:
    """
    A class to judge classification model outputs using metrics and LLM evaluation.
    This evaluates the quality of classification predictions by different models.
    """
    
    def __init__(self, client=None):
        """Initialize the Classification Judge with an LLM client."""
        self.client = client or llm
        # Default judge model to use
        self.judge_model = "gpt-4o-mini"
        
    def set_judge_model(self, model_name: str):
        """Set the judge model to use for qualitative evaluations."""
        self.judge_model = model_name
    
    def calculate_metrics(self, df: pd.DataFrame, model_name: str, 
                         class_labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Calculate essential classification metrics for a model.
        
        Args:
            df: DataFrame containing ground_truth and predicted_class columns
            model_name: Name of the model being evaluated
            class_labels: Optional list of class labels (if not provided, will be inferred)
            
        Returns:
            Dictionary containing calculated metrics
        """
        try:
            if 'ground_truth' not in df.columns or 'predicted_class' not in df.columns:
                logger.error(f"Required columns missing from DataFrame: {df.columns}")
                return {"error": "Required columns missing from evaluation data"}
            
            y_true = df['ground_truth'].values
            y_pred = df['predicted_class'].values
            
            if not class_labels:
                class_labels = sorted(list(set(y_true) | set(y_pred)))
            
            # For binary classification
            binary_classification = len(class_labels) == 2
            
            # Basic metrics
            metrics = {
                "model_name": model_name,
                "accuracy": accuracy_score(y_true, y_pred),
                "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
                "samples_count": len(df),
                "class_distribution": {cls: sum(y_true == cls) for cls in class_labels},
                "prediction_distribution": {cls: sum(y_pred == cls) for cls in class_labels}
            }
            
            # Multi-class metrics
            metrics.update({
                "precision_macro": precision_score(y_true, y_pred, average='macro', zero_division=0),
                "recall_macro": recall_score(y_true, y_pred, average='macro', zero_division=0),
                "f1_macro": f1_score(y_true, y_pred, average='macro', zero_division=0),
                "precision_weighted": precision_score(y_true, y_pred, average='weighted', zero_division=0),
                "recall_weighted": recall_score(y_true, y_pred, average='weighted', zero_division=0),
                "f1_weighted": f1_score(y_true, y_pred, average='weighted', zero_division=0),
                "matthews_correlation": matthews_corrcoef(y_true, y_pred)
            })
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred, labels=class_labels)
            metrics["confusion_matrix"] = {
                "matrix": cm.tolist(),
                "labels": class_labels,
                "normalized": (cm / cm.sum(axis=1)[:, np.newaxis]).tolist() if cm.sum(axis=1).all() else None
            }
            
            # Per-class metrics
            per_class_metrics = {}
            for i, cls in enumerate(class_labels):
                true_cls = (y_true == cls)
                pred_cls = (y_pred == cls)
                
                tp = sum(true_cls & pred_cls)
                fp = sum(~true_cls & pred_cls)
                fn = sum(true_cls & ~pred_cls)
                tn = sum(~true_cls & ~pred_cls)
                
                per_class_metrics[cls] = {
                    "precision": tp / (tp + fp) if (tp + fp) > 0 else 0,
                    "recall": tp / (tp + fn) if (tp + fn) > 0 else 0,
                    "f1": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0,
                    "support": sum(true_cls),
                    "predicted_count": sum(pred_cls),
                    "confusion_matrix": {
                        "tp": int(tp),
                        "fp": int(fp),
                        "fn": int(fn),
                        "tn": int(tn)
                    }
                }
            
            metrics["per_class_metrics"] = per_class_metrics
            
            # Add confidence-based metrics if available
            if 'confidence' in df.columns:
                metrics["avg_confidence"] = df['confidence'].mean()
                metrics["avg_confidence_correct"] = df[df['ground_truth'] == df['predicted_class']]['confidence'].mean()
                metrics["avg_confidence_incorrect"] = df[df['ground_truth'] != df['predicted_class']]['confidence'].mean()
                
                # Add calibration metrics when sufficient data
                if len(df) > 20:  # Only compute for reasonable amount of samples
                    df['is_correct'] = (df['ground_truth'] == df['predicted_class']).astype(int)
                    bin_count = min(10, len(df) // 5)
                    
                    if bin_count > 1:
                        bins = pd.cut(df['confidence'], bins=bin_count, labels=False)
                        calibration_data = []
                        
                        for bin_idx in range(bin_count):
                            bin_df = df[bins == bin_idx]
                            if len(bin_df) > 0:
                                calibration_data.append({
                                    "bin": bin_idx,
                                    "mean_confidence": bin_df['confidence'].mean(),
                                    "actual_accuracy": bin_df['is_correct'].mean(),
                                    "sample_count": len(bin_df)
                                })
                        
                        metrics["calibration_curve"] = calibration_data
            
            # Format latency metrics if available
            if 'latency' in df.columns:
                metrics["avg_latency"] = df['latency'].mean()
                metrics["min_latency"] = df['latency'].min()
                metrics["max_latency"] = df['latency'].max()
                metrics["p95_latency"] = df['latency'].quantile(0.95)
            
            # Error analysis - identify the most misclassified classes
            misclassifications = {}
            for true_class in class_labels:
                for pred_class in class_labels:
                    if true_class != pred_class:
                        count = sum((y_true == true_class) & (y_pred == pred_class))
                        if count > 0:
                            misclassifications[f"{true_class} → {pred_class}"] = count
            
            # Sort by count and get top misclassifications
            sorted_misclass = sorted(misclassifications.items(), key=lambda x: x[1], reverse=True)
            metrics["top_misclassifications"] = dict(sorted_misclass[:5]) if sorted_misclass else {}
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {"error": f"Metrics calculation failed: {str(e)}"}
    # Add to ClassificationJudge class
    async def before_after_tuning_comparison(self, model_name: str, 
                                            before_data: Dict, 
                                            after_data: Dict) -> Dict:
        """
        Compare model performance before and after hyperparameter tuning.
        
        Args:
            model_name: Name of the model being compared
            before_data: Evaluation results before tuning
            after_data: Evaluation results after tuning
            
        Returns:
            Dictionary containing comparison analysis
        """
        try:
            # Extract key metrics
            before_metrics = before_data.get("metrics", {})
            after_metrics = after_data.get("metrics", {})
            
            # Create comparison prompt
            prompt = self._create_comparison_prompt(
                model_name,
                before_metrics,
                after_metrics
            )
            
            # Get LLM comparison
            comparison_response = await self.client.chat(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert analyst comparing model performance changes from hyperparameter tuning."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Process response
            comparison = comparison_response.get("content", "") if isinstance(comparison_response, dict) else str(comparison_response)
            
            # Try to extract structured data
            try:
                if "```json" in comparison:
                    comparison = comparison.split("```json")[1].split("```")[0]
                return json.loads(comparison)
            except json.JSONDecodeError:
                return {
                    "text_analysis": comparison,
                    "before_metrics": before_metrics,
                    "after_metrics": after_metrics
                }
                
        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}")
            return {"error": f"Comparison failed: {str(e)}"}

    def _create_comparison_prompt(self, model_name: str,
                                before_metrics: Dict,
                                after_metrics: Dict) -> str:
        """
        Create a prompt for comparing before/after tuning performance.
        
        Args:
            model_name: Name of the model
            before_metrics: Metrics dictionary before tuning
            after_metrics: Metrics dictionary after tuning
            
        Returns:
            Formatted comparison prompt
        """
        metrics_template = """**{metric}**
    - Before: {before_value}
    - After: {after_value}
    - Change: {change} ({change_percent})"""
        
        metric_comparisons = []
        for metric in ['accuracy', 'f1', 'precision_weighted', 'recall_weighted']:
            before_val = before_metrics.get(metric, 0)
            after_val = after_metrics.get(metric, 0)
            change = after_val - before_val
            change_percent = f"{change*100:.1f}%" if isinstance(before_val, (int, float)) else "N/A"
            
            metric_comparisons.append(metrics_template.format(
                metric=metric.capitalize(),
                before_value=before_val,
                after_value=after_val,
                change=change,
                change_percent=change_percent
            ))
        
        return f"""Compare the performance of {model_name} before and after hyperparameter tuning.

    **Metric Comparisons:**
    {"\n\n".join(metric_comparisons)}

    Analyze:
    1. Significant improvements/regressions
    2. Consistency of improvements across metrics
    3. Tradeoffs between different metrics
    4. Likely effectiveness of the tuning
    5. Recommendations for further improvements

    Format your response as JSON with:
    {{
    "summary": "Overall summary of changes...",
    "key_improvements": ["List of major improvements"],
    "potential_issues": ["List of any regressions or concerns"],
    "effectiveness_score": 0-10,
    "recommendations": ["Suggestions for next steps"]
    }}"""
    async def evaluate_model_outputs(self, evaluation_results: Dict, class_labels: List[str] = None,
                                   criteria: List[str] = None) -> Dict:
        """
        Evaluate multiple models based on their classification output quality.
        
        Args:
            evaluation_results: The evaluation results dictionary containing model outputs
            class_labels: List of valid class labels
            criteria: Optional list of specific criteria to judge on
            
        Returns:
            Dictionary containing judge evaluations for each model
        """
        if not isinstance(criteria, list):
            criteria = [criteria]
            
            criteria_list = "\n- ".join([str(c) for c in criteria])
            
            # Use in prompt template
            prompt = f"""Evaluate model outputs based on:
            - {criteria_list}
            ..."""
        
        
        judge_results = {}
        
        # Evaluate each model
        for model_name, model_data in evaluation_results.items():
            # Get responses and calculate metrics
            responses = model_data.get("responses", [])
            if not responses:
                judge_results[model_name] = {"error": "No responses found for evaluation"}
                continue
            
            # Create DataFrame for metrics calculation
            df = pd.DataFrame(responses)
            
            # Calculate statistical metrics
            metrics = self.calculate_metrics(df, model_name, class_labels)
            
            # Get qualitative LLM evaluation
            llm_eval = await self.evaluate_single_model(model_name, model_data, class_labels, criteria)
            
            # Combine both types of evaluations
            judge_results[model_name] = {
                "statistical_metrics": metrics,
                "qualitative_evaluation": llm_eval
            }
            
        return judge_results
    
    async def evaluate_single_model(self, model_name: str, model_data: Dict, 
                               class_labels: List[str], criteria: List[str]) -> Dict:
        """
        Evaluate a single model's classification outputs using an LLM judge.
        
        Args:
            model_name: Name of the model
            model_data: The model's evaluation data
            class_labels: List of valid class labels 
            criteria: List of criteria to judge on
            
        Returns:
            Dictionary containing judge's evaluation for this model
        """
        responses = model_data.get("responses", [])
        if not responses:
            return {"error": "No responses found for evaluation"}
        
        # We'll evaluate up to 10 responses to keep the context manageable
        sample_responses = responses[:10]
        
        prompt = self._create_judge_prompt(model_name, sample_responses, class_labels, criteria)
        
        try:
            judge_response = await self.client.chat(
                model=self.judge_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in machine learning evaluation who assesses the quality of classification models. You must respond with valid JSON formatted output."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the content from the response
            if isinstance(judge_response, dict) and "content" in judge_response:
                judge_evaluation = judge_response["content"]
            else:
                judge_evaluation = str(judge_response)

            structured_evaluation = {}
            raw_text_analysis = ""
            
            try:
                # First try to extract JSON block
                json_match = re.search(r'```json\n([\s\S]*?)\n```', judge_evaluation)
                if json_match:
                    structured_evaluation = json.loads(json_match.group(1))
                else:
                    # Fallback to direct JSON parse
                    structured_evaluation = json.loads(judge_evaluation)
            except json.JSONDecodeError:
                # If JSON parsing fails, store raw text and try to extract key metrics
                raw_text_analysis = judge_evaluation
                structured_evaluation = {"qualitative_analysis": raw_text_analysis}
                
                # Try to extract final score from text
                score_match = re.search(r"final_score['\"]?:\s*(\d+)", raw_text_analysis)
                if score_match:
                    structured_evaluation["final_score"] = int(score_match.group(1))
                    
                # Try to extract criteria scores from text
                criteria_scores = {}
                for criterion in criteria:
                    criterion = criterion.lower()
                    match = re.search(
                        fr"{criterion}['\"]?:\s*(\d+(?:\.\d+)?)", 
                        raw_text_analysis, 
                        re.IGNORECASE
                    )
                    if match:
                        criteria_scores[criterion] = float(match.group(1))
                if criteria_scores:
                    structured_evaluation["criteria_scores"] = criteria_scores

            # Normalize scores structure
            normalized_evaluation = {}
            try:
                # Normalize criteria scores
                criteria_scores = {}
                for criterion, score_data in structured_evaluation.get("criteria_scores", {}).items():
                    if isinstance(score_data, dict):
                        criteria_scores[criterion] = {
                            "score": float(score_data.get("score", 0)),
                            "comments": score_data.get("comments", "")
                        }
                    else:
                        criteria_scores[criterion] = {
                            "score": float(score_data),
                            "comments": ""
                        }
                normalized_evaluation["criteria_scores"] = criteria_scores

                # Normalize final score
                normalized_evaluation["final_score"] = min(
                    100, 
                    max(0, structured_evaluation.get("final_score", 0))
                )

                # Normalize other fields
                for field in ["strengths", "weaknesses", "recommendations", "summary"]:
                    if field in structured_evaluation:
                        if isinstance(structured_evaluation[field], str):
                            # Split string into list items
                            normalized_evaluation[field] = [
                                line.strip() 
                                for line in structured_evaluation[field].split("\n") 
                                if line.strip()
                            ]
                        else:
                            normalized_evaluation[field] = structured_evaluation.get(field, [])
                            
                # Add raw text if JSON parsing failed
                if raw_text_analysis:
                    normalized_evaluation["raw_analysis"] = raw_text_analysis

            except Exception as e:
                logger.error(f"Error normalizing evaluation structure: {str(e)}")
                normalized_evaluation = {
                    "error": f"Normalization failed: {str(e)}",
                    "raw_response": judge_evaluation
                }

            return {
                "model_name": model_name,
                "evaluation": normalized_evaluation,
                "raw_response": judge_evaluation
            }
            
        except Exception as e:
            logger.error(f"Error during judge evaluation: {str(e)}")
            return {
                "model_name": model_name,
                "error": f"Judge evaluation failed: {str(e)}",
                "raw_response": str(e)
            }
    def _create_judge_prompt(self, model_name: str, responses: List[Dict], 
                            class_labels: List[str], criteria: List[str]) -> str:
        # Handle None case for class labels
        class_labels = class_labels or []
        criteria = criteria or []
        
        # Safely join class labels
        classes_str = ", ".join(class_labels) if class_labels else "Not specified"
        
        # Safely process criteria
        criteria_str = "\n".join([f"- {c}" for c in criteria]) if criteria else "- No specific criteria provided"
        
        examples_str = ""
        for i, response in enumerate(responses):
            examples_str += f"\n\nExample {i+1}:\n"
            examples_str += f"Question/Input: {response.get('question', 'N/A')}\n"
            examples_str += f"Ground Truth Class: {response.get('ground_truth', 'N/A')}\n"
            examples_str += f"Predicted Class: {response.get('predicted_class', 'N/A')}\n"
            examples_str += f"Confidence: {response.get('confidence', 'N/A')}\n"
            examples_str += f"Correct: {'Yes' if response.get('ground_truth') == response.get('predicted_class') else 'No'}"
            if 'latency' in response:
                examples_str += f"\nLatency: {response.get('latency')} seconds"

        prompt = f"""
        I need you to evaluate the classification performance of the model '{model_name}'. 
        You'll analyze the quality of the predicted classes compared to the ground truth classes.

        The valid classes for this classification task are: {classes_str}

        Please evaluate based on the following criteria:
        {criteria_str}

        For each criterion, provide a score from 1-10 and brief comments.

        Below are example predictions to evaluate:
        {examples_str}

        After reviewing these examples, please provide:
        1. A score (1-10) for each criterion
        2. Brief comments explaining your reasoning for each score
        3. Overall strengths of the model
        4. Overall weaknesses of the model
        5. Class-specific insights (which classes it handles well/poorly)
        6. Recommendations for improvement
        7. Summary evaluation of the model's performance
        8. A final score out of 100

        Format your response as JSON with the following structure:
        ```json
        {{
        "criteria_scores": {{
            "Class prediction accuracy": {{
            "score": 8,
            "comments": "The model correctly identified most classes..."
            }},
            // Additional criteria with scores and comments
        }},
        "strengths": ["Strength 1", "Strength 2", ...],
        "weaknesses": ["Weakness 1", "Weakness 2", ...],
        "class_insights": {{
            "well_handled_classes": ["Class A", "Class B"],
            "poorly_handled_classes": ["Class C"],
            "comments": "The model performs exceptionally well on Class A..."
        }},
        "recommendations": ["Recommendation 1", "Recommendation 2", ...],
        "summary": "Overall evaluation summary...",
        "final_score": 85
        }}"""
        prompt += """
        IMPORTANT: Your response MUST be valid JSON format between ```json markers.
        Use only numeric scores between 0-10 and maintain consistent structure.
        Example of valid format:
        ```json
        {
        "criteria_scores": {
            "Accuracy": {"score": 8.5, "comments": "..."},
            "Clarity": {"score": 9.0, "comments": "..."}
        },
        "strengths": ["..."],
        "weaknesses": ["..."],
        "final_score": 85
        }
        """
        return prompt
    
    async def compare_models(self, evaluation_results: Dict, model_names: List[str], 
                        class_labels: List[str] = None) -> Dict:
        """
        Compare multiple classification models side by side.
        
        Args:
            evaluation_results: The evaluation results dictionary 
            model_names: List of model names to compare
            class_labels: Optional list of class labels
            
        Returns:
            Dictionary containing comparison results
        """
        if len(model_names) < 2:
            return {"error": "Need at least 2 models to compare"}
        
        # Filter evaluation results to include only the specified models
        filtered_results = {name: evaluation_results.get(name, {}) for name in model_names}
        
        # Create a comparison prompt
        prompt = self._create_comparison_prompt(filtered_results, class_labels)
        
        try:
            comparison_response = await self.client.chat(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert in machine learning evaluation comparing the performance of different classification models."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the content from the response
            comparison = comparison_response["content"] if isinstance(comparison_response, dict) and "content" in comparison_response else comparison_response
            
            return {
                "comparison": comparison,
                "models_compared": model_names
            }
            
        except Exception as e:
            logger.error(f"Error during model comparison: {str(e)}")
            return {"error": f"Model comparison failed: {str(e)}"}
    
    def _create_comparison_prompt(self, model_results: Dict, class_labels: List[str] = None) -> str:
        """
        Create a comparison prompt for evaluating multiple classification models.
        
        Args:
            model_results: Dictionary of model results to compare
            class_labels: Optional list of class labels
            
        Returns:
            String prompt for model comparison
        """
        classes_context = ""
        if class_labels:
            classes_context = f"The valid classes for this classification task are: {', '.join(class_labels)}.\n\n"
        
        models_info = ""
        for model_name, data in model_results.items():
            # Get metrics for comparison
            metrics = data.get("metrics", {})
            # Filter out non-scalar metrics to keep the prompt clean
            scalar_metrics = {k: v for k, v in metrics.items() 
                            if not isinstance(v, (dict, list)) and k not in ["responses", "model_name"]}
            
            metrics_str = "\n".join([f"- {k}: {v}" for k, v in scalar_metrics.items()])
            models_info += f"\n\nModel: {model_name}\nMetrics:\n{metrics_str}"
        
        prompt = f"""
{classes_context}I need you to compare the following classification models:
{models_info}

Please provide a detailed comparison focusing on:
1. Overall performance differences based on accuracy, F1 score, and other metrics
2. Per-class performance differences (which models are better at which classes)
3. Strengths and weaknesses of each model relative to others
4. Confidence calibration differences between models
5. Latency and efficiency considerations (if available)
6. Recommendations for when to use each model

Format your response as a detailed comparison with clear sections for each point.
Include a final verdict on which model performs best overall and why.
"""
        return prompt
    
    def analyze_error_patterns(self, df: pd.DataFrame, class_labels: List[str] = None) -> Dict[str, Any]:
        """
        Perform detailed error analysis on classification results.
        
        Args:
            df: DataFrame containing ground_truth and predicted_class columns
            class_labels: Optional list of class labels
            
        Returns:
            Dictionary containing error analysis
        """
        if 'ground_truth' not in df.columns or 'predicted_class' not in df.columns:
            return {"error": "Required columns missing from evaluation data"}
        
        if not class_labels:
            class_labels = sorted(list(set(df['ground_truth']) | set(df['predicted_class'])))
        
        error_analysis = {
            "total_samples": len(df),
            "correct_predictions": sum(df['ground_truth'] == df['predicted_class']),
            "incorrect_predictions": sum(df['ground_truth'] != df['predicted_class']),
            "accuracy": sum(df['ground_truth'] == df['predicted_class']) / len(df)
        }
        
        # Per-class accuracy
        per_class_performance = {}
        for cls in class_labels:
            class_samples = df[df['ground_truth'] == cls]
            if len(class_samples) > 0:
                accuracy = sum(class_samples['ground_truth'] == class_samples['predicted_class']) / len(class_samples)
                per_class_performance[cls] = {
                    "samples": len(class_samples),
                    "accuracy": accuracy,
                    "most_confused_with": []
                }
                
                # Find most common misclassifications for this class
                if accuracy < 1.0:
                    misclassified = class_samples[class_samples['ground_truth'] != class_samples['predicted_class']]
                    confused_with = misclassified['predicted_class'].value_counts().to_dict()
                    per_class_performance[cls]["most_confused_with"] = [
                        {"class": other_cls, "count": count}
                        for other_cls, count in confused_with.items()
                    ]
        
        error_analysis["per_class_performance"] = per_class_performance
        
        # Most common error patterns
        errors = df[df['ground_truth'] != df['predicted_class']]
        error_patterns = {}
        for true_cls in class_labels:
            for pred_cls in class_labels:
                if true_cls != pred_cls:
                    pattern = f"{true_cls} → {pred_cls}"
                    count = sum((df['ground_truth'] == true_cls) & (df['predicted_class'] == pred_cls))
                    if count > 0:
                        error_patterns[pattern] = count
        
        # Sort by frequency
        sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
        error_analysis["error_patterns"] = [
            {"pattern": pattern, "count": count} 
            for pattern, count in sorted_patterns
        ]
        
        # Confidence analysis for errors if available
        if 'confidence' in df.columns:
            correct_conf = df[df['ground_truth'] == df['predicted_class']]['confidence'].mean()
            incorrect_conf = df[df['ground_truth'] != df['predicted_class']]['confidence'].mean()
            
            error_analysis["confidence_analysis"] = {
                "avg_confidence_correct": correct_conf,
                "avg_confidence_incorrect": incorrect_conf,
                "confidence_gap": correct_conf - incorrect_conf
            }
        
        return error_analysis