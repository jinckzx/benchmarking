from .judge_base import JudgeBaseMetric
class JoinEfficiencyMetric(JudgeBaseMetric):
    """Evaluates join efficiency aspects in SQL queries"""
    
    def __init__(self, threshold: float = 0.6, model: str = "gpt-3.5-turbo"):
        super().__init__(
            name="join_efficiency",
            criteria=""" I have given you generated sql's and gold sqls with some metrics. 
            I want you to tell me how accurate the responses are, on the basis of execution of the sqls""",
            threshold=threshold,
            model=model
        )
        
