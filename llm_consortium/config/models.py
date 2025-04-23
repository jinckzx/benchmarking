

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
    # New fields for model temperature tuning
    enable_model_temp_tuning: bool = False
    model_min_temp: float = 0.0
    model_max_temp: float = 0.7
    model_num_trials: int = 2
    
    

# class LogEntry(BaseModel):
#     prompt: str = "" 
#     question: str = "" 
#     model: str
#     response: str
#     predicted_class: str  # This replaces 'response' in your current model
#     confidence: float
#     latency: float
#     iteration: int
#     reasoning: str
#     intent: str = ""  # New field with default
#     db_id: str = ""   # New field with default
#     raw_response: Optional[str] = None  # Add this field to store the complete response
#     timestamp: datetime = datetime.now()
#     error: Optional[str]=None
#     def to_dict(self):
#         """Convert the LogEntry object to a dictionary."""
#         return {
#             "timestamp": self.timestamp.isoformat(),
#             "question": self.question,
#             "prompt":self.prompt,
#             "model": self.model,
#             "response":self.response,
#             "predicted_class": self.predicted_class,
#             "confidence": self.confidence,
#             "latency": self.latency,
#             "iteration": self.iteration,
#             "reasoning": self.reasoning,
#             "raw_response": self.raw_response
#         }
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class LogEntry(BaseModel):
    # Common fields
    model: str
    confidence: float
    latency: float
    iteration: int
    timestamp: datetime = datetime.now()
    error: Optional[str] = None
    
    # Fields with aliases to support both runners
    prompt: str = ""  # SQL runner uses this
    question: str = ""  # Class runner uses this
    
    # Response fields
    response: str = ""  # SQL query for SQL runner, can be empty for Class runner
    predicted_class: str = ""  # For Class runner, empty for SQL runner
    
    # Additional context fields
    reasoning: str = ""  # For Class runner
    intent: str = ""  # For SQL runner
    db_id: str = ""  # For SQL runner
    raw_response: Optional[str] = None  # Full model response for Class runner
    temperature: float = 0.2  # Add temperature field with default
    def to_dict(self):
        """Convert the LogEntry object to a dictionary with all fields."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "prompt": self.prompt,
            "question": self.question,
            "model": self.model,
            "response": self.response,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "latency": self.latency,
            "iteration": self.iteration,
            "reasoning": self.reasoning,
            "intent": self.intent,
            "db_id": self.db_id,
            "raw_response": self.raw_response,
            "error": self.error,
            "temperature": self.temperature
        }