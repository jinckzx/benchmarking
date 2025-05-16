from llm_consortium.metrics.join_clausee import Join_clauseeMetric

# Test instances
metric = Join_clauseeMetric()

# Test with a simple query
test_sql = "SELECT * FROM table1 JOIN table2 ON table1.id = table2.id"
result = metric.calculate(generated_sql=test_sql, gold_sql="SELECT * FROM table")

print(f"Metric result: {result}")
# Should print something like: {'join_clause': 1, 'join_clause_result': 'yes'}