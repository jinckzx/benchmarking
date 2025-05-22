
from llm_consortium.metrics_deep.deep_exact import SQLExactMatch
from llm_consortium.metrics_deep.deep_vaibhav import SQLVaibhav
from llm_consortium.metrics_deep.deep_execute import SQLExecutionMatch
from llm_consortium.metrics_deep.geval_llm import SQLClauseCountGEval
from llm_consortium.metrics_deep.geval_correctness import GenerationUseCaseCorrectness
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

async def test_with_deepeval():
    """
    Test multiple SQL metrics on sample queries
    """
    queries = [
        { 
            "input": "Count employees over 56 years old",
            "generated_sql": "SELECT count(*) FROM head WHERE age  >  56",
            "gold_sql": "SELECT count(*) FROM head WHERE age  >  56",
            "db_id": "department_management"  # This is just a placeholder for the execution match test
        },
        {
            "input": "Find most common budget type in documents with expenses",
            "generated_sql": "SELECT Budget_Type_Code, COUNT(*) AS Count FROM Documents_with_Expenses GROUP BY Budget_Type_Code ORDER BY Count DESC LIMIT 1;",
            "gold_sql": "SELECT budget_type_code FROM Documents_with_expenses GROUP BY budget_type_code ORDER BY count(*) DESC LIMIT 1",
            "db_id": "cre_Docs_and_Epenses"  # This is just a placeholder for the execution match test
        }
    ]
    	
    exact_metric =SQLExactMatch(threshold=1.0)
    vaibhav_metric = SQLVaibhav(threshold=0.7)
    clause_metric = SQLClauseCountGEval(threshold=1.0)
    db_root_path = os.environ.get("DB_ROOT_PATH", "./dataset/spider_data/spider_data/database")
    correctness_metric = GenerationUseCaseCorrectness(threshold=1)
    print("=" * 60)
    print("SQL METRICS EVALUATION")
    print("=" * 60)
    
    # Test each query
    for i, query in enumerate(queries):
        print(f"\nQuery Pair #{i+1}:")
        print(f"Input: {query['input']}") 
        print(f"Generated: {query['generated_sql']}")
        print(f"Gold: {query['gold_sql']}")
        print("-" * 50)
        
        # Test LlmbasedClauseMatchMetric (async)
        try:
            await clause_metric.measure_async(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql']
            )
            llm_result = {
                "score": clause_metric.score,
                "passed": clause_metric.is_successful(),
                "rationale": clause_metric.geval.reason
            }
            print(f"LLM Clause Match: {llm_result}")
        except Exception as e:
            print(f"LLM Clause Match Error: {str(e)}")
        
         # Test SQLExact (synchronous)
        try:
            exact_metric.measure(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql']
            )
            exact_result = exact_metric.calculate(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql']
            )
            print(f"Exact Metric: {exact_result}")
        except Exception as e:
            print(f"Exact Metric Error: {str(e)}")
        # Test SQLVaibhav (synchronous)
        try:
            vaibhav_metric.measure(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql']
            )
            vaibhav_result = vaibhav_metric.calculate(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql']
            )
            print(f"Vaibhav Metric: {vaibhav_result}")
        except Exception as e:
            print(f"Vaibhav Metric Error: {str(e)}")

        
        execution_metric = SQLExecutionMatch(db_root_path=db_root_path, threshold=1.0)
        try:
            execution_metric.measure(
                generated_sql=query['generated_sql'],
                gold_sql=query['gold_sql'],
                db_id=query['db_id']
            )
            execution_result = {
                "score": execution_metric.score,
                "passed": execution_metric.is_successful()
            }
            print(f"Execution Match: {execution_result}")
        except Exception as e:
            print(f"Execution Match Error: {str(e)}")
        # Test GenerationUseCaseCorrectness (async)
        try:
            await correctness_metric.measure_async(
                input=query['input'],            # Natural language input
                actual_output=query['generated_sql']  # Generated SQL
            )
            correctness_result = {
                "score": correctness_metric.score,
                "passed": correctness_metric.is_successful(),
                "rationale": correctness_metric.geval.reason
            }
            print(f"Use Case Correctness: {correctness_result}")
        except Exception as e:
            print(f"Use Case Correctness Error: {str(e)}")
        
        
        
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_with_deepeval())