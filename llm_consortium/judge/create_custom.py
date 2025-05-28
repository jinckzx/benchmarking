import os
def create_custom_criteria():
    criteria_name = input("Enter the criteria name (e.g., 'Query Optimization'): ").strip()
    while not criteria_name:
        print("Metric name cannot be empty.")
        criteria_name = input("Enter the criteria name (e.g., 'Query Optimization'): ").strip()
    class_name = criteria_name.title().replace(" ", "") + "Metric"
    filename = f"{criteria_name.lower().replace(' ', '_')}_criteria.py"
    target_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(target_dir, filename)
    if os.path.exists(file_path):
        overwrite = input(f"The file '{file_path}' already exists. Overwrite? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("File creation aborted.")
            return
    print("\nEnter the criteria line by line. Press Enter on an empty line to finish.")
    criteria_lines = []
    while True:
        line = input("Criteria line (empty to finish): ")
        if line == "":
            if len(criteria_lines) == 0:
                print("At least one criteria line is required.")
                continue
            break
        criteria_lines.append(line)
    print("\nEnter each evaluation step line by line. Press Enter on an empty line to finish.")
    evaluation_steps = []
    while True:
        step = input("Evaluation step (empty to finish): ")
        if step == "":
            if len(evaluation_steps) == 0:
                print("At least one evaluation step is required.")
                continue
            break
        evaluation_steps.append(step)
    threshold = input("\nEnter the threshold (default 0.8): ") or "0.8"
    try:
        threshold = float(threshold)
    except ValueError:
        print("Invalid threshold. Using default 0.8.")
        threshold = 0.8
    model = input("Enter the model name (default 'gpt-4o-mini'): ") or "gpt-4o-mini"
    name_slug = criteria_name.lower().replace(' ', '_')
    criteria_str = '\n'.join(criteria_lines)
    evaluation_steps_str = ',\n                '.join([f'"{step}"' for step in evaluation_steps])
    code = f"""from .judge_base import JudgeBaseMetric

class {class_name}(JudgeBaseMetric):
    \"""Evaluates {criteria_name.lower()} aspects in SQL queries\"""
    
    def __init__(self, threshold: float = {threshold}, model: str = "{model}"):
        super().__init__(
            name="{name_slug}",
            criteria=\"\"\"{criteria_str}\"\"\",
            evaluation_steps=[
                {evaluation_steps_str}
            ],
            threshold=threshold,
            model=model
        )
"""
    with open(file_path, 'w') as f:
        f.write(code)
    print(f"\nSuccessfully created custom criteria file: {file_path}")
if __name__ == "__main__":
    create_custom_criteria()
