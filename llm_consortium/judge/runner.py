import sys
from .core_runner import run_evaluation_pipeline

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python evaluate_metrics.py <input_file.json> <output_file.json>")
        sys.exit(1)
    
    try:
        run_evaluation_pipeline(sys.argv[1], sys.argv[2])
        print("Evaluation completed successfully!")
    except Exception as e:
        print(f"Error running evaluation: {str(e)}")
        sys.exit(1)