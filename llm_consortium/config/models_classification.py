from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class LogEntry:
    """Data model for classification log entries"""
    prompt: str
    model: str
    predicted_class: str
    confidence: float
    latency: float
    iteration: int
    raw_response: str = ""
    error: str = ""
    temperature: float = 0.2

@dataclass
class ModelConfig:
    """Configuration for classification model benchmarking"""
    # Models to benchmark
    models: List[str]
    
    # Temperature settings
    base_temperature: float = 0.2
    min_temp: float = 0.0
    max_temp: float = 1.0
    
    # Hyperparameter tuning settings
    enable_tuning: bool = True
    num_trials: int = 5
    tuning_sample_size: int = 10
    
    # Evaluation settings
    run_final_evaluation: bool = True
    
    # Valid classification classes
    valid_classes: List[str] = None
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ModelConfig':
        """Create config from dictionary"""
        return cls(
            models=config_dict.get('models', []),
            base_temperature=config_dict.get('base_temperature', 0.2),
            min_temp=config_dict.get('min_temp', 0.0),
            max_temp=config_dict.get('max_temp', 1.0),
            enable_tuning=config_dict.get('enable_tuning', True),
            num_trials=config_dict.get('num_trials', 5),
            tuning_sample_size=config_dict.get('tuning_sample_size', 10),
            run_final_evaluation=config_dict.get('run_final_evaluation', True),
            valid_classes=config_dict.get('valid_classes', None)
        )

@dataclass
class RunResult:
    """Results of a classification model run"""
    model: str
    config: ModelConfig
    run_id: str
    timestamp: datetime
    accuracy: float
    f1_score: float
    precision: float
    recall: float
    sample_size: int
    temperature: float
    tuned: bool = False