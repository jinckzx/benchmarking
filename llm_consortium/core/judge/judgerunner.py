# modern_sql_judge.py
import json
import asyncio
from typing import Dict, List, Any, Optional
from llm_consortium.utils.logging import logger


class ModernSQLJudge:
    """
    A modern SQL judge that uses GEval-based metrics for evaluation.
    This replaces the old SQLJudge class with a more modular approach.
    """
    
    def __init__(self, client=None):
        """
        Initialize the Modern SQL Judge.
        
        Args:
            client: Optional LLM client (kept for compatibility)
        """
        self.client = client
        
    def _create_metric_instances(self, metric_names: List[str], model: str = "gpt-4o-mini") -> Dict:
        """
        Create metric instances for the given metric names.
        
        Args:
            metric_names: List of metric names to create
            model: Model to use for evaluation
            
        Returns:
            Dictionary of metric instances
        """
        metrics = {}
        
        for metric_name in metric_names:
            try:
                if metric_name == "syntax_correctness":
                    from .syntax_correctness_metric import SyntaxCorrectnessMetric
                    metrics[metric_name] = SyntaxCorrectnessMetric(model=model)
                    
                elif metric_name == "column_accuracy":
                    metrics[metric_name] = self._create_column_accuracy_metric(model)
                    
                elif metric_name == "table_usage":
                    metrics[metric_name] = self._create_table_usage_metric(model)
                    
                elif metric_name == "join_quality":
                    metrics[metric_name] = self._create_join_quality_metric(model)
                    
                elif metric_name == "condition_correctness":
                    metrics[metric_name] = self._create_condition_correctness_metric(model)
                    
                elif metric_name == "query_structure":
                    metrics[metric_name] = self._create_query_structure_metric(model)
                    
                elif metric_name == "optimization":
                    metrics[metric_name] = self._create_optimization_metric(model)
                    
                elif metric_name == "intent_understanding":
                    metrics[metric_name] = self._create_intent_understanding_metric(model)
                    
                else:
                    logger.warning(f"Unknown metric: {metric_name}, skipping")
                    
            except Exception as e:
                logger.error(f"Failed to create metric {metric_name}: {e}")
                continue
                
        return metrics
    
    def _create_column_accuracy_metric(self, model: str):
        """Create a column accuracy metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class ColumnAccuracyMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="column_accuracy",
                        criteria="""Evaluate how accurately the generated SQL query selects the correct columns compared to the reference SQL:
                        1. Column selection accuracy - Are the right columns selected?
                        2. Column aliasing - Are column aliases used correctly?
                        3. Aggregation columns - Are aggregation functions applied to correct columns?
                        4. Calculated columns - Are computed columns structured correctly?
                        5. Column ordering - Is the column order appropriate?""",
                        evaluation_steps=[
                            "Compare selected columns in both queries",
                            "Check column aliases and their correctness",
                            "Verify aggregation functions are applied to correct columns",
                            "Assess calculated/computed column accuracy",
                            "Evaluate overall column selection appropriateness",
                            "Score based on column accuracy (0-1 scale)"
                        ],
                        model=model
                    )
            
            return ColumnAccuracyMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for column_accuracy")
            return None
    
    def _create_table_usage_metric(self, model: str):
        """Create a table usage metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class TableUsageMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="table_usage",
                        criteria="""Evaluate the correctness of table usage in the generated SQL query:
                        1. Table selection - Are the correct tables included?
                        2. Table aliases - Are table aliases used appropriately?
                        3. Table relationships - Are table relationships understood correctly?
                        4. Missing tables - Are any required tables omitted?
                        5. Unnecessary tables - Are any unnecessary tables included?""",
                        evaluation_steps=[
                            "Identify all tables used in both queries",
                            "Check if correct tables are selected for the query intent",
                            "Verify table aliases are used appropriately",
                            "Assess understanding of table relationships",
                            "Check for missing or unnecessary table inclusions",
                            "Score based on table usage correctness (0-1 scale)"
                        ],
                        model=model
                    )
            
            return TableUsageMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for table_usage")
            return None
    
    def _create_join_quality_metric(self, model: str):
        """Create a join quality metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class JoinQualityMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="join_quality",
                        criteria="""Evaluate the quality and correctness of JOIN operations:
                        1. Join type accuracy - Are the correct JOIN types used (INNER, LEFT, RIGHT, FULL)?
                        2. Join conditions - Are join conditions logically correct?
                        3. Join order - Is the join order optimal and logical?
                        4. Missing joins - Are any required joins omitted?
                        5. Unnecessary joins - Are there any redundant joins?""",
                        evaluation_steps=[
                            "Analyze JOIN types used in both queries",
                            "Verify join conditions are logically correct",
                            "Check join order and optimization",
                            "Identify missing required joins",
                            "Check for unnecessary or redundant joins",
                            "Score based on overall join quality (0-1 scale)"
                        ],
                        model=model
                    )
            
            return JoinQualityMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for join_quality")
            return None
    
    def _create_condition_correctness_metric(self, model: str):
        """Create a condition correctness metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class ConditionCorrectnessMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="condition_correctness",
                        criteria="""Evaluate the correctness of WHERE conditions and filters:
                        1. Filter logic - Are WHERE conditions logically correct?
                        2. Condition completeness - Are all necessary conditions included?
                        3. Operator usage - Are comparison operators used correctly?
                        4. Value accuracy - Are filter values and literals correct?
                        5. Boolean logic - Is AND/OR logic structured properly?""",
                        evaluation_steps=[
                            "Compare WHERE conditions in both queries",
                            "Verify logical correctness of filter conditions",
                            "Check completeness of filtering criteria",
                            "Assess operator usage and value accuracy",
                            "Evaluate boolean logic structure",
                            "Score based on condition correctness (0-1 scale)"
                        ],
                        model=model
                    )
            
            return ConditionCorrectnessMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for condition_correctness")
            return None
    
    def _create_query_structure_metric(self, model: str):
        """Create a query structure metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class QueryStructureMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="query_structure",
                        criteria="""Evaluate the overall structure and organization of the SQL query:
                        1. Query organization - Is the query well-structured and readable?
                        2. Clause ordering - Are SQL clauses in the correct order?
                        3. Subquery usage - Are subqueries used appropriately when needed?
                        4. Grouping logic - Is GROUP BY used correctly with aggregations?
                        5. Sorting logic - Is ORDER BY used appropriately?""",
                        evaluation_steps=[
                            "Analyze overall query structure and organization",
                            "Check SQL clause ordering (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY)",
                            "Evaluate subquery usage and nesting appropriateness",
                            "Verify GROUP BY usage with aggregation functions",
                            "Check ORDER BY usage and sorting logic",
                            "Score based on structural quality (0-1 scale)"
                        ],
                        model=model
                    )
            
            return QueryStructureMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for query_structure")
            return None
    
    def _create_optimization_metric(self, model: str):
        """Create a query optimization metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class OptimizationMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="optimization",
                        criteria="""Evaluate the optimization and efficiency of the SQL query:
                        1. Index usage - Does the query structure allow for efficient index usage?
                        2. Query complexity - Is the query unnecessarily complex?
                        3. Performance considerations - Are there obvious performance bottlenecks?
                        4. Redundancy - Are there redundant operations or conditions?
                        5. Best practices - Does the query follow SQL best practices?""",
                        evaluation_steps=[
                            "Analyze query structure for index-friendly patterns",
                            "Check for unnecessary complexity or redundant operations",
                            "Identify potential performance bottlenecks",
                            "Evaluate adherence to SQL best practices",
                            "Compare optimization level with reference query",
                            "Score based on optimization quality (0-1 scale)"
                        ],
                        model=model
                    )
            
            return OptimizationMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for optimization")
            return None
    
    def _create_intent_understanding_metric(self, model: str):
        """Create an intent understanding metric instance"""
        try:
            from .judge_base_metric import JudgeBaseMetric
            
            class IntentUnderstandingMetric(JudgeBaseMetric):
                def __init__(self, model: str = "gpt-4o-mini"):
                    super().__init__(
                        name="intent_understanding",
                        criteria="""Evaluate how well the generated SQL captures the intent of the natural language question:
                        1. Semantic accuracy - Does the query answer the intended question?
                        2. Completeness - Does the query address all aspects of the question?
                        3. Context understanding - Are contextual nuances captured correctly?
                        4. Business logic - Are business rules and constraints understood?
                        5. Data interpretation - Is the data correctly interpreted for the intended use?""",
                        evaluation_steps=[
                            "Compare the natural language question with generated SQL logic",
                            "Verify the query addresses all aspects of the question",
                            "Check understanding of contextual requirements",
                            "Evaluate business logic and constraint handling",
                            "Assess data interpretation accuracy",
                            "Score based on intent understanding (0-1 scale)"
                        ],
                        model=model
                    )
            
            return IntentUnderstandingMetric(model)
        except ImportError:
            logger.error("Could not import JudgeBaseMetric for intent_understanding")
            return None
        
    def _criteria_to_metrics(self, criteria: List[str]) -> List[str]:
        """
        Convert old-style criteria strings to metric names.
        
        Args:
            criteria: List of criteria strings
            
        Returns:
            List of metric names
        """
        criteria_mapping = {
            "Column name accuracy": "column_accuracy",
            "Table usage correctness": "table_usage", 
            "Join quality": "join_quality",
            "Condition correctness": "condition_correctness",
            "Query structure": "query_structure",
            "SQL syntax correctness": "syntax_correctness",
            "Query optimization": "optimization",
            "Intent understanding": "intent_understanding"
        }
        
        metrics = []
        for criterion in criteria:
            if criterion in criteria_mapping:
                metrics.append(criteria_mapping[criterion])
            else:
                # Try to find partial matches
                criterion_lower = criterion.lower()
                if "syntax" in criterion_lower or "correctness" in criterion_lower:
                    metrics.append("syntax_correctness")
                elif "column" in criterion_lower:
                    metrics.append("column_accuracy")
                elif "table" in criterion_lower:
                    metrics.append("table_usage")
                elif "join" in criterion_lower:
                    metrics.append("join_quality")
                elif "condition" in criterion_lower or "where" in criterion_lower:
                    metrics.append("condition_correctness")
                elif "structure" in criterion_lower or "organization" in criterion_lower:
                    metrics.append("query_structure")
                elif "optimization" in criterion_lower or "performance" in criterion_lower:
                    metrics.append("optimization")
                elif "intent" in criterion_lower or "understanding" in criterion_lower:
                    metrics.append("intent_understanding")
                else:
                    logger.warning(f"Unknown criterion '{criterion}', defaulting to syntax_correctness")
                    metrics.append("syntax_correctness")
                
        return list(set(metrics))  # Remove duplicates
    
    async def evaluate_model_outputs(self, evaluation_results: Dict, criteria: List[str] = None) -> Dict:
        """
        Evaluate multiple models using GEval-based metrics.
        
        Args:
            evaluation_results: The evaluation results dictionary containing model outputs
            criteria: Optional list of specific criteria to judge on
            
        Returns:
            Dictionary containing judge evaluations for each model
        """
        if not criteria:
            criteria = [
                "Column name accuracy",
                "Table usage correctness", 
                "Join quality",
                "Condition correctness",
                "Query structure",
                "SQL syntax correctness",
                "Query optimization",
                "Intent understanding"
            ]
        
        # Convert criteria to metric names
        metric_names = self._criteria_to_metrics(criteria)
        logger.info(f"Using metrics: {metric_names}")
        
        judge_results = {}
        
        # Evaluate each model
        for model_name, model_data in evaluation_results.items():
            logger.info(f"Evaluating model: {model_name}")
            judge_results[model_name] = await self.evaluate_single_model(
                model_name, model_data, metric_names
            )
            
        return judge_results
    
    async def evaluate_single_model(self, model_name: str, model_data: Dict, metric_names: List[str]) -> Dict:
        """
        Evaluate a single model's SQL outputs using specified metrics.
        
        Args:
            model_name: Name of the model
            model_data: The model's evaluation data
            metric_names: List of metric names to use
            
        Returns:
            Dictionary containing judge's evaluation for this model
        """
        responses = model_data.get("responses", [])
        if not responses:
            return {"error": "No responses found for evaluation"}
        
        # Sample up to 10 queries for evaluation
        sample_responses = responses[:10]
        
        try:
            # Initialize metrics
            metrics = self._create_metric_instances(metric_names)
            
            if not metrics:
                return {"error": "No valid metrics could be initialized"}
            
            logger.info(f"Successfully initialized {len(metrics)} metrics: {list(metrics.keys())}")
            
            # Evaluate each response with each metric
            metric_results = {name: [] for name in metrics.keys()}
            
            for i, response in enumerate(sample_responses):
                question = response.get('question', '')
                generated_sql = response.get('generated_sql', '')
                gold_sql = response.get('gold_sql', '')
                
                if not all([question, generated_sql, gold_sql]):
                    logger.warning(f"Skipping response {i}: missing required fields")
                    continue
                
                logger.info(f"Evaluating response {i+1}/{len(sample_responses)}")
                
                # Run each metric on this response
                for metric_name, metric in metrics.items():
                    try:
                        result = await metric.calculate_async(
                            question=question,
                            generated_sql=generated_sql,
                            gold_sql=gold_sql
                        )
                        metric_results[metric_name].append(result)
                        logger.debug(f"Metric {metric_name} score: {result.get('score', 0)}")
                    except Exception as e:
                        logger.error(f"Error evaluating {metric_name} on response {i}: {e}")
                        metric_results[metric_name].append({
                            "score": 0.0,
                            "error": str(e)
                        })
            
            # Calculate aggregate scores
            aggregated_results = {}
            for metric_name, results in metric_results.items():
                if results:
                    scores = [r.get('score', 0.0) for r in results if 'score' in r]
                    avg_score = sum(scores) / len(scores) if scores else 0.0
                    
                    aggregated_results[metric_name] = {
                        "average_score": avg_score,
                        "individual_results": results,
                        "total_evaluations": len(results)
                    }
                else:
                    aggregated_results[metric_name] = {
                        "average_score": 0.0,
                        "individual_results": [],
                        "total_evaluations": 0
                    }
            
            # Calculate overall score
            all_scores = [result["average_score"] for result in aggregated_results.values()]
            overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
            
            return {
                "model_name": model_name,
                "evaluation": {
                    "overall_score": overall_score,
                    "metric_scores": aggregated_results,
                    "total_queries_evaluated": len(sample_responses)
                },
                "structured_results": True
            }
            
        except Exception as e:
            logger.error(f"Error during model evaluation: {str(e)}")
            return {"error": f"Model evaluation failed: {str(e)}"}
    
    async def compare_models(self, evaluation_results: Dict, model_names: List[str]) -> Dict:
        """
        Compare multiple models side by side using metric scores.
        
        Args:
            evaluation_results: The evaluation results dictionary 
            model_names: List of model names to compare
            
        Returns:
            Dictionary containing comparison results
        """
        if len(model_names) < 2:
            return {"error": "Need at least 2 models to compare"}
        
        # Get judge results for the specified models
        judge_results = {}
        for model_name in model_names:
            if model_name in evaluation_results:
                # Use default criteria for comparison
                judge_results[model_name] = await self.evaluate_single_model(
                    model_name, 
                    evaluation_results[model_name], 
                    ['syntax_correctness', 'column_accuracy', 'join_quality']
                )
        
        if not judge_results:
            return {"error": "No valid model results to compare"}
        
        # Create comparison analysis
        comparison_data = {}
        for model_name, results in judge_results.items():
            if "evaluation" in results:
                comparison_data[model_name] = {
                    "overall_score": results["evaluation"]["overall_score"],
                    "metric_scores": {
                        metric: data["average_score"] 
                        for metric, data in results["evaluation"]["metric_scores"].items()
                    }
                }
        
        # Find best performing model
        best_model = max(comparison_data.keys(), 
                        key=lambda x: comparison_data[x]["overall_score"])
        
        return {
            "comparison_data": comparison_data,
            "best_model": best_model,
            "models_compared": model_names,
            "ranking": sorted(model_names, 
                            key=lambda x: comparison_data.get(x, {}).get("overall_score", 0), 
                            reverse=True)
        }
    
    async def before_after_tuning_comparison(self, model_name: str, before_data: Dict, after_data: Dict) -> Dict:
        """
        Compare a model's performance before and after tuning using metrics.
        
        Args:
            model_name: Name of the model
            before_data: Model data before tuning
            after_data: Model data after tuning
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Evaluate before and after using key metrics
            key_metrics = ['syntax_correctness', 'column_accuracy', 'join_quality']
            
            before_results = await self.evaluate_single_model(
                f"{model_name}_before", before_data, key_metrics
            )
            
            after_results = await self.evaluate_single_model(
                f"{model_name}_after", after_data, key_metrics
            )
            
            # Calculate improvements
            improvements = {}
            if ("evaluation" in before_results and "evaluation" in after_results):
                before_scores = before_results["evaluation"]["metric_scores"]
                after_scores = after_results["evaluation"]["metric_scores"]
                
                for metric in key_metrics:
                    if metric in before_scores and metric in after_scores:
                        before_score = before_scores[metric]["average_score"]
                        after_score = after_scores[metric]["average_score"]
                        improvement = after_score - before_score
                        improvements[metric] = {
                            "before": before_score,
                            "after": after_score,
                            "improvement": improvement,
                            "improvement_percentage": (improvement / before_score * 100) if before_score > 0 else 0
                        }
            
            overall_improvement = sum(imp["improvement"] for imp in improvements.values()) / len(improvements) if improvements else 0
            
            return {
                "model_name": model_name,
                "tuning_impact_analysis": {
                    "overall_improvement": overall_improvement,
                    "metric_improvements": improvements,
                    "before_results": before_results,
                    "after_results": after_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error during tuning comparison: {str(e)}")
            return {"error": f"Tuning comparison failed: {str(e)}"}


# Compatibility function for your existing Streamlit code
def create_sql_judge(client=None):
    """
    Factory function to create a SQL judge instance.
    This maintains compatibility with your existing code.
    """
    return ModernSQLJudge(client)