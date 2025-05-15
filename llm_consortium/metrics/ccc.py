from .base_metrics import BaseMetric
from typing import Dict, Any, List
import sqlparse
import re

class SQLccc(BaseMetric):
    """Clause-wise component match between generated and gold SQL"""

    def __init__(self):
        super().__init__(
            name="ccc",
            description="Clause-level comparison between generated and gold SQL (SELECT, WHERE, GROUP BY, ORDER BY)",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )

    def extract_clause(self, sql: str, clause: str) -> str:
        """Extract specific clause content from SQL (naive heuristic-based)"""
        sql = sql.lower()
        pattern_dict = {
            "select": r"select (.+?) from",
            "from": r"from (.+?)( where| group by| order by|$)",
            "where": r"where (.+?)( group by| order by|$)",
            "group by": r"group by (.+?)( order by|$)",
            "order by": r"order by (.+)$"
        }
        pattern = pattern_dict.get(clause)
        if pattern:
            match = re.search(pattern, sql, re.DOTALL)
            return match.group(1).strip() if match else ""
        return ""

    def normalize_clause(self, clause: str) -> List[str]:
        """Normalize clause: remove whitespace, lowercase, sort elements"""
        clause = clause.lower().strip()
        if clause == "":
            return []
        # Split by common separators
        parts = re.split(r',|\band\b|\bor\b', clause)
        return sorted([p.strip() for p in parts if p.strip()])

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        try:
            clause_types = ["select", "where", "group by", "order by"]
            scores = {}

            for clause in clause_types:
                gen_clause = self.extract_clause(generated_sql, clause)
                gold_clause = self.extract_clause(gold_sql, clause)

                gen_parts = self.normalize_clause(gen_clause)
                gold_parts = self.normalize_clause(gold_clause)

                if not gold_parts and not gen_parts:
                    score = 1.0
                elif not gold_parts or not gen_parts:
                    score = 0.0
                else:
                    overlap = len(set(gen_parts) & set(gold_parts))
                    total = len(set(gold_parts) | set(gen_parts))
                    score = overlap / total

                scores[f"{clause.replace(' ', '_')}_match"] = round(score, 4)

            # Average component score
            avg_score = round(sum(scores.values()) / len(scores), 4)
            scores["ccc"] = avg_score

            return scores

        except Exception as e:
            return {
                "ccc": 0.0,
                "error": str(e),
                "generated_sql": generated_sql,
                "gold_sql": gold_sql
            }
