# metrics/registry.py
from .exact_match import SQLExactMatch
from .execution_match import SQLExecutionMatch
from typing import Dict, List
from .base_metrics import BaseMetric
from .component_match import SQLComponentMatch
from .anmol import SQLAnmol
from .abcabc import SQLabcabc
from .xyz import SQLxyz
from .ooo import SQLooo
from .ppp import SQLppp
from .ccc import SQLccc
from .select_check import Select_checkMetric
from .vaibhav import SQLVaibhav
from .joinclause_check import Joinclause_checkMetric
from .where_clause import Where_clauseMetric
from .custom123 import Custom123Metric
from .custom321 import Custom321Metric
from .llmbased_clause_match import Llmbased_clause_matchMetric
from .check1_join import Check1_joinMetric
from .check2_execute import Check2_executeMetric
from .from_clause import From_clauseMetric
from .join123_check import Join123_checkMetric
from .abc1234 import Abc1234Metric
from .new_llmbased import New_llmbasedMetric



class MetricRegistry:
    """Registry for available metrics with validation"""
    
    def __init__(self):
        self.metrics = {
            "sql": {
                "exact_match": SQLExactMatch(),
                "execution_match": SQLExecutionMatch(

                    # db_root_path="D:/data_sci/benchmarking_tool/dataset/spider_data/spider_data/database"

                    db_root_path = "D:/data_sci/version3/benchmarking_tool/dataset/spider_data/spider_data/database"
                ),
                "component_match":SQLComponentMatch(),
                "anmol": SQLAnmol(),
                
                
                "abcabc": SQLabcabc(),
                "xyz": SQLxyz(),
                "ooo": SQLooo(),
                "ppp": SQLppp(),
                
                "ccc": SQLccc(),
                "select_check": Select_checkMetric(),
                
                "vaibhav": SQLVaibhav(),
                
                
                "joinclause_check": Joinclause_checkMetric(),
                "where_clause": Where_clauseMetric(),
                "custom123": Custom123Metric(),
                "custom321": Custom321Metric(),
                "llmbased_clause_match": Llmbased_clause_matchMetric(),
                "check1_join": Check1_joinMetric(),
                "check2_execute": Check2_executeMetric(),
                "from_clause": From_clauseMetric(),
                "join123_check": Join123_checkMetric(),
                "abc1234": Abc1234Metric(),
                "new_llmbased": New_llmbasedMetric(),
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