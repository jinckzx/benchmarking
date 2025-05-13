from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any 

class ModelConfig(BaseModel):
    """Configuration for model evaluation and tuning"""
    # Models to evaluate (no instances, just names)
    models: List[str] = ["gpt-4o-mini", "gpt-3.5-turbo"]
    metrics: List[str]
    # Base evaluation settings
    base_temperature: float = 0.2
    
    # Hyperparameter tuning settings
    enable_tuning: bool = True
    min_temp: float = 0.0
    max_temp: float = 0.8
    num_trials: int = 5
    tuning_sample_size: int = 10  # Number of queries to use for tuning
    run_final_evaluation: bool = True  # Whether to run evaluation with tuned params
class LogEntry(BaseModel):
    """Log entry for tracking model responses and evaluation metrics"""
    # Basic information
    prompt: str  # SQL question or prompt
    model: str  # Model name and instance (e.g., "gpt-4o-mini-0")
    metrics: Dict[str, Any] = {} 
    response: str  # Generated SQL query
    confidence: float  # Model's confidence in its response
    latency: float  # Time taken to generate response (seconds)
    iteration: int  # Current iteration number
    
    # Context information
    intent: str = ""  # Extracted query intent
    db_id: str = ""  # Database identifier
    raw_response: Optional[str] = None  # Complete model response
    
    # Evaluation metadata
    temperature: float = 0.2  # Temperature used for generation
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Error tracking
    error: Optional[str] = None  # Any error encountered
    
    def to_dict(self) -> Dict:
        """Convert LogEntry to dictionary format for storage"""
        return {
            "prompt": self.prompt,
            "model": self.model,
            "metrics": self.metrics,
            "response": self.response,
            "confidence": self.confidence,
            "latency": self.latency,
            "iteration": self.iteration,
            "intent": self.intent,
            "db_id": self.db_id,
            "raw_response": self.raw_response,
            "temperature": self.temperature,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LogEntry":
        """Create LogEntry from dictionary data"""
        # Handle timestamp conversion if needed
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)