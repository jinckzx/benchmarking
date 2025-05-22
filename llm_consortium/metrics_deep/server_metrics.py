from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import pandas as pd
import asyncio
import io
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Import your custom metrics
from llm_consortium.metrics_deep.deep_exact import SQLExactMatch
from llm_consortium.metrics_deep.deep_vaibhav import SQLVaibhav
from llm_consortium.metrics_deep.deep_execute import SQLExecutionMatch
from llm_consortium.metrics_deep.geval_llm import SQLClauseCountGEval
from llm_consortium.metrics_deep.geval_correctness import GenerationUseCaseCorrectness

load_dotenv()

app = FastAPI(
    title="SQL Metrics Evaluation API",
    description="API for evaluating SQL queries using various metrics",
    version="1.0.0"
)

class MetricResult(BaseModel):
    metric_name: str
    score: float
    passed: bool
    details: Dict[str, Any] = {}
    error: Optional[str] = None

class EvaluationResponse(BaseModel):
    total_queries: int
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]

class MetricConfig:
    """Configuration for available metrics"""
    AVAILABLE_METRICS = {
        "exact_match": {
            "class": SQLExactMatch,
            "description": "Exact string match between generated and reference SQL",
            "requires": ["generated_sql", "gold_sql"],
            "async": False
        },
        "vaibhav": {
            "class": SQLVaibhav,
            "description": "Clause-level comparison (SELECT, WHERE, GROUP BY, ORDER BY)",
            "requires": ["generated_sql", "gold_sql"],
            "async": False
        },
        "execution_match": {
            "class": SQLExecutionMatch,
            "description": "Result set comparison by executing both queries",
            "requires": ["generated_sql", "gold_sql", "db_id"],
            "async": False
        },
        "clause_count_match": {
            "class": SQLClauseCountGEval,
            "description": "LLM-based clause count matching",
            "requires": ["generated_sql", "gold_sql"],
            "async": True
        },
        "use_case_correctness": {
            "class": GenerationUseCaseCorrectness,
            "description": "LLM-based evaluation of output correctness",
            "requires": ["input", "generated_sql"],
            "async": True
        }
    }

def validate_csv_columns(df: pd.DataFrame) -> None:
    """Validate that CSV has required columns"""
    required_columns = ["input", "generated_sql", "gold_sql"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing_columns}. Required: {required_columns}"
        )

def initialize_metrics(selected_metrics: List[str], db_root_path: str = None) -> Dict[str, Any]:
    """Initialize the selected metrics"""
    metrics = {}
    
    for metric_name in selected_metrics:
        if metric_name not in MetricConfig.AVAILABLE_METRICS:
            continue
            
        metric_info = MetricConfig.AVAILABLE_METRICS[metric_name]
        
        try:
            if metric_name == "execution_match":
                if not db_root_path:
                    db_root_path = os.environ.get("DB_ROOT_PATH", "./dataset/spider_data/spider_data/database")
                metrics[metric_name] = metric_info["class"](db_root_path=db_root_path, threshold=1.0)
            elif metric_name == "exact_match":
                metrics[metric_name] = metric_info["class"](threshold=1.0)
            elif metric_name == "vaibhav":
                metrics[metric_name] = metric_info["class"](threshold=0.7)
            elif metric_name == "clause_count_match":
                metrics[metric_name] = metric_info["class"](threshold=1.0)
            elif metric_name == "use_case_correctness":
                metrics[metric_name] = metric_info["class"](threshold=0.8)
                
        except Exception as e:
            print(f"Failed to initialize {metric_name}: {str(e)}")
            
    return metrics

async def evaluate_single_query(query_data: Dict, metrics: Dict, row_index: int) -> Dict[str, Any]:
    """Evaluate a single query against all selected metrics"""
    results = {
        "row_index": row_index,
        "input": query_data.get("input", ""),
        "generated_sql": query_data.get("generated_sql", ""),
        "gold_sql": query_data.get("gold_sql", ""),
        "db_id": query_data.get("db_id", ""),
        "metrics": {}
    }
    
    for metric_name, metric_instance in metrics.items():
        try:
            metric_info = MetricConfig.AVAILABLE_METRICS[metric_name]
            
            # Check if all required fields are available
            missing_fields = []
            for field in metric_info["requires"]:
                if field == "generated_sql" and not query_data.get("generated_sql"):
                    missing_fields.append(field)
                elif field == "gold_sql" and not query_data.get("gold_sql"):
                    missing_fields.append(field)
                elif field == "input" and not query_data.get("input"):
                    missing_fields.append(field)
                elif field == "db_id" and not query_data.get("db_id"):
                    missing_fields.append(field)
            
            if missing_fields:
                results["metrics"][metric_name] = {
                    "score": 0.0,
                    "passed": False,
                    "error": f"Missing required fields: {missing_fields}"
                }
                continue
            
            # Execute metric evaluation
            if metric_info["async"]:
                if metric_name == "clause_count_match":
                    await metric_instance.measure_async(
                        generated_sql=query_data["generated_sql"],
                        gold_sql=query_data["gold_sql"]
                    )
                elif metric_name == "use_case_correctness":
                    await metric_instance.measure_async(
                        input=query_data["input"],
                        actual_output=query_data["generated_sql"]
                    )
            else:
                if metric_name == "execution_match":
                    metric_instance.measure(
                        generated_sql=query_data["generated_sql"],
                        gold_sql=query_data["gold_sql"],
                        db_id=query_data["db_id"]
                    )
                else:
                    metric_instance.measure(
                        generated_sql=query_data["generated_sql"],
                        gold_sql=query_data["gold_sql"]
                    )
            
            # Get detailed results
            if hasattr(metric_instance, 'calculate'):
                if metric_name == "execution_match":
                    detailed_result = metric_instance.calculate(
                        generated_sql=query_data["generated_sql"],
                        gold_sql=query_data["gold_sql"],
                        db_id=query_data["db_id"]
                    )
                elif metric_name == "use_case_correctness":
                    detailed_result = metric_instance.calculate(
                        input=query_data["input"],
                        actual_output=query_data["generated_sql"]
                    )
                else:
                    detailed_result = metric_instance.calculate(
                        generated_sql=query_data["generated_sql"],
                        gold_sql=query_data["gold_sql"]
                    )
            else:
                detailed_result = {"score": metric_instance.score}
            
            results["metrics"][metric_name] = {
                "score": metric_instance.score,
                "passed": metric_instance.is_successful(),
                "details": detailed_result
            }
            
        except Exception as e:
            results["metrics"][metric_name] = {
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }
    
    return results

@app.get("/")
async def root():
    return {"message": "SQL Metrics Evaluation API", "version": "1.0.0"}

@app.get("/metrics")
async def get_available_metrics():
    """Get list of available metrics and their descriptions"""
    return {
        "available_metrics": {
            name: {
                "description": info["description"],
                "requires": info["requires"],
                "async": info["async"]
            }
            for name, info in MetricConfig.AVAILABLE_METRICS.items()
        }
    }

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_csv(
    file: UploadFile = File(...),
    metrics: str = Form(default="exact_match,vaibhav"),
    db_root_path: Optional[str] = Form(default=None)
):
    """
    Evaluate SQL queries from uploaded CSV file
    
    Args:
        file: CSV file with columns: input, generated_sql, gold_sql, db_id (optional)
        metrics: Comma-separated list of metrics to evaluate
        db_root_path: Path to database files (for execution_match metric)
    
    Returns:
        Evaluation results for each query and summary statistics
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate CSV structure
        validate_csv_columns(df)
        
        # Parse selected metrics
        selected_metrics = [m.strip() for m in metrics.split(',') if m.strip()]
        invalid_metrics = [m for m in selected_metrics if m not in MetricConfig.AVAILABLE_METRICS]
        
        if invalid_metrics:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metrics: {invalid_metrics}. Available: {list(MetricConfig.AVAILABLE_METRICS.keys())}"
            )
        
        # Initialize metrics
        metric_instances = initialize_metrics(selected_metrics, db_root_path)
        
        if not metric_instances:
            raise HTTPException(status_code=500, detail="Failed to initialize any metrics")
        
        # Process each query
        results = []
        for index, row in df.iterrows():
            query_data = {
                "input": str(row.get("input", "")),
                "generated_sql": str(row.get("generated_sql", "")),
                "gold_sql": str(row.get("gold_sql", "")),
                "db_id": str(row.get("db_id", "")) if "db_id" in row else ""
            }
            
            result = await evaluate_single_query(query_data, metric_instances, index)
            results.append(result)
        
        # Calculate summary statistics
        summary = calculate_summary(results, selected_metrics)
        
        return EvaluationResponse(
            total_queries=len(results),
            results=results,
            summary=summary
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

def calculate_summary(results: List[Dict], selected_metrics: List[str]) -> Dict[str, Any]:
    """Calculate summary statistics across all queries"""
    summary = {
        "metrics_summary": {},
        "overall": {}
    }
    
    total_queries = len(results)
    
    for metric_name in selected_metrics:
        scores = []
        passed_count = 0
        error_count = 0
        
        for result in results:
            metric_result = result["metrics"].get(metric_name, {})
            if "error" not in metric_result:
                scores.append(metric_result.get("score", 0.0))
                if metric_result.get("passed", False):
                    passed_count += 1
            else:
                error_count += 1
        
        if scores:
            summary["metrics_summary"][metric_name] = {
                "average_score": round(sum(scores) / len(scores), 4),
                "min_score": min(scores),
                "max_score": max(scores),
                "pass_rate": round(passed_count / total_queries, 4),
                "error_rate": round(error_count / total_queries, 4),
                "total_evaluated": len(scores)
            }
        else:
            summary["metrics_summary"][metric_name] = {
                "average_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "pass_rate": 0.0,
                "error_rate": 1.0,
                "total_evaluated": 0
            }
    
    # Overall summary
    all_scores = []
    for result in results:
        for metric_name in selected_metrics:
            metric_result = result["metrics"].get(metric_name, {})
            if "error" not in metric_result:
                all_scores.append(metric_result.get("score", 0.0))
    
    summary["overall"] = {
        "total_queries": total_queries,
        "metrics_evaluated": len(selected_metrics),
        "average_score_across_all": round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0
    }
    
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)