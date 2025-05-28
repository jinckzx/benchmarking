# metrics/registry.py
from .exact_match import SQLExactMatch
from .execution_match import SQLExecutionMatch
from typing import Dict, List
from pathlib import Path
from .base_metrics import BaseMetric
from .vaibhav import SQLVaibhav
from .llmbased_clause_match import Llmbased_clause_matchMetric
from .new_llmbased import New_llmbasedMetric
from .where_clause_1705 import Where_clause_1705Metric
from .join_2205 import Join_2205Metric
from .new_2705 import New_2705Metric
from .new_2805 import New_2805Metric



class MetricRegistry:
    """Registry for available metrics with validation"""
    
    def __init__(self):
        self.metrics = {
            "sql": {
                "exact_match": SQLExactMatch(),
                "execution_match": SQLExecutionMatch(

                    db_root_path="./dataset/spider_data/spider_data/database"

                

                ),
                
                "vaibhav": SQLVaibhav(),
                "llmbased_clause_match": Llmbased_clause_matchMetric(),
                "new_llmbased": New_llmbasedMetric(),
                "where_clause_1705": Where_clause_1705Metric(),
                "join_2205": Join_2205Metric(),
                "new_2705": New_2705Metric(),
                "new_2805": New_2805Metric(),
            }
        }
    
    def get_metrics_for_task(self, task: str) -> Dict[str, BaseMetric]:
        return self.metrics.get(task, {})
    
    def register_metric(self, task: str, metric: BaseMetric):
        if task not in self.metrics:
            self.metrics[task] = {}
        if not isinstance(metric, BaseMetric):
            raise TypeError("Can only register BaseMetric instances")
        self.metrics[task][metric.name] = metric

    def validate_csv_columns(self, task: str, csv_columns: List[str]) -> List[str]:
        required = set()
        for metric in self.get_metrics_for_task(task).values():
            required.update(metric.csv_requires)
        return list(required - set(csv_columns))