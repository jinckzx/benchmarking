# from pydantic import BaseModel, Field
# from typing import Dict, Optional
# from datetime import datetime


# class ConsortiumConfig(BaseModel):
#     models: Dict[str, int] = {"gpt-4o-mini": 1}
#     arbiter: str = "gpt-4o-mini"
#     confidence_threshold: float = 0.8
#     max_iterations: int = 3
#     min_iterations: int = 1

# # class LogEntry(BaseModel):
# #     timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
# #     prompt: str
# #     model: str
# #     response: str
# #     confidence: float
# #     latency: float
# #     iteration: int


# class LogEntry(BaseModel):
#     timestamp: datetime = Field(default_factory=datetime.now)
#     prompt: str
#     model: str
#     response: str
#     confidence: float
#     latency: float
#     iteration: int
#     error: Optional[str] = None

#     def to_dict(self):
#         """Convert the LogEntry object to a dictionary."""
#         return {
#             "timestamp": self.timestamp.isoformat(),
#             "prompt": self.prompt,
#             "model": self.model,
#             "response": self.response,
#             "confidence": self.confidence,
#             "latency": self.latency,
#             "iteration": self.iteration,
#             "error": self.error
#         }




from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ConsortiumConfig(BaseModel):
    models: Dict[str, int] = {"gpt-4o-mini": 1}
    arbiter: str = "gpt-4o-mini"
    confidence_threshold: float = 0.8
    max_iterations: int = 3
    min_iterations: int = 1
    min_temp: float
    max_temp: float
    num_trials: int
    

class LogEntry(BaseModel):
    prompt: str = "" 
    question: str = "" 
    model: str
    response: str
    predicted_class: str  # This replaces 'response' in your current model
    confidence: float
    latency: float
    iteration: int
    reasoning: str
    intent: str = ""  # New field with default
    db_id: str = ""   # New field with default
    raw_response: Optional[str] = None  # Add this field to store the complete response
    timestamp: datetime = datetime.now()
    error: Optional[str]=None
    def to_dict(self):
        """Convert the LogEntry object to a dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "prompt":self.prompt,
            "model": self.model,
            "response":self.response,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "latency": self.latency,
            "iteration": self.iteration,
            "reasoning": self.reasoning,
            "raw_response": self.raw_response
        }

# class LogEntry(BaseModel):
#     prompt: str
#     question: str
#     model: str
#     response: str
#     confidence: float
#     latency: float
#     iteration: int
#     intent: str = ""  # New field with default
#     db_id: str = ""   # New field with default
#     timestamp: datetime = datetime.now()
#     error: Optional[str]=None
#     def to_dict(self):
#         """Convert the LogEntry object to a dictionary."""
#         return {
#             "timestamp": self.timestamp.isoformat(),
#             "prompt": self.prompt,
#             "question": self.question,
#             "model": self.model,
#             "response": self.response,
#             "confidence": self.confidence,
#             "latency": self.latency,
#             "iteration": self.iteration,
#             "error": self.error
#         }