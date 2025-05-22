from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import re
import importlib.util
import sys
from typing import Optional, Dict, Any
import traceback

app = FastAPI(title="Custom Metrics Manager", description="API for managing custom SQL metrics")

# Data models
class MetricCodeRequest(BaseModel):
    code: str
    task: str = "sql"

class MetricResponse(BaseModel):
    success: bool
    message: str
    class_name: Optional[str] = None
    metric_name: Optional[str] = None
    file_path: Optional[str] = None

# Utility functions (adapted from your ui_utils)
def extract_metric_name(code_str: str) -> str:
    """Extract the metric name from the name parameter in __init__"""
    match = re.search(r'name="([^"]+)"', code_str)
    if match:
        return match.group(1)
    # Fallback to class name if no name parameter found
    class_match = re.search(r'class\s+(\w+)\(CustomBaseMetric\):', code_str)
    if class_match:
        return class_match.group(1).lower()
    raise ValueError("No valid metric name or class found.")

def extract_class_name(code_str: str) -> str:
    """Extract the class name from the metric code"""
    match = re.search(r'class\s+(\w+)\(CustomBaseMetric\):', code_str)
    if match:
        return match.group(1)
    raise ValueError("No valid metric class found inheriting CustomBaseMetric.")

def validate_metric_code(code_str: str) -> Dict[str, Any]:
    """Validate that the code contains a proper metric class"""
    try:
        # Check for required imports
        required_patterns = [
            r'from\s+\.base_metrics\s+import\s+CustomBaseMetric',
            r'class\s+\w+\(CustomBaseMetric\):',
            r'def\s+calculate\(',
            r'def\s+measure\('
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, code_str):
                return {
                    "valid": False,
                    "error": f"Missing required pattern: {pattern}"
                }
        
        class_name = extract_class_name(code_str)
        metric_name = extract_metric_name(code_str)
        
        return {
            "valid": True,
            "class_name": class_name,
            "metric_name": metric_name
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def save_custom_metric_to_file(code_str: str, metric_name: str) -> str:
    """Save the metric code to a file named after the metric name"""
    metrics_path = os.path.join("llm_consortium", "metrics")
    filename = f"{metric_name.lower()}.py"
    full_path = os.path.join(metrics_path, filename)
    os.makedirs(metrics_path, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code_str)
    return full_path

def dynamic_import_metric(file_path: str, class_name: str):
    """Dynamically import the metric class from the file"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    full_module_name = f"llm_consortium.metrics.{module_name}"
    spec = importlib.util.spec_from_file_location(full_module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_module_name] = module
    spec.loader.exec_module(module)
    return getattr(module, class_name)

def test_metric_instantiation(file_path: str, class_name: str) -> Dict[str, Any]:
    """Test if the metric can be instantiated properly"""
    try:
        metric_class = dynamic_import_metric(file_path, class_name)
        instance = metric_class()
        
        # Basic validation
        if not hasattr(instance, 'name'):
            return {"success": False, "error": "Metric instance missing 'name' attribute"}
        if not hasattr(instance, 'calculate'):
            return {"success": False, "error": "Metric instance missing 'calculate' method"}
        if not hasattr(instance, 'measure'):
            return {"success": False, "error": "Metric instance missing 'measure' method"}
            
        return {
            "success": True,
            "metric_name": instance.name,
            "description": getattr(instance, 'description', 'No description available')
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to instantiate metric: {str(e)}"
        }

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_form():
    """Serve a simple HTML form for testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Metrics Manager</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            textarea { width: 100%; height: 400px; font-family: monospace; }
            button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
            .result { margin-top: 20px; padding: 10px; border: 1px solid #ccc; }
            .success { background-color: #d4edda; border-color: #c3e6cb; }
            .error { background-color: #f8d7da; border-color: #f5c6cb; }
        </style>
    </head>
    <body>
        <h1>Custom Metrics Manager</h1>
        <form id="metricForm">
            <h3>Enter your custom metric class code:</h3>
            <textarea name="code" placeholder="Paste your metric class code here..."></textarea>
            <br><br>
            <label>Task: <input type="text" name="task" value="sql"></label>
            <br><br>
            <button type="submit">Save Metric</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('metricForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/save-metric', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        code: formData.get('code'),
                        task: formData.get('task')
                    })
                });
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                resultDiv.className = 'result ' + (result.success ? 'success' : 'error');
                resultDiv.innerHTML = '<h3>Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/save-metric", response_model=MetricResponse)
async def save_metric(request: MetricCodeRequest):
    """Save a custom metric from code string"""
    try:
        # Validate the code
        validation = validate_metric_code(request.code)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        class_name = validation["class_name"]
        metric_name = validation["metric_name"]
        
        # Save to file
        file_path = save_custom_metric_to_file(request.code, metric_name)
        
        # Test instantiation
        test_result = test_metric_instantiation(file_path, class_name)
        if not test_result["success"]:
            # Clean up the file if instantiation failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=test_result["error"])
        
        return MetricResponse(
            success=True,
            message=f"Metric '{metric_name}' saved successfully",
            class_name=class_name,
            metric_name=metric_name,
            file_path=file_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/validate-metric")
async def validate_metric(request: MetricCodeRequest):
    """Validate metric code without saving"""
    try:
        validation = validate_metric_code(request.code)
        if validation["valid"]:
            return {
                "valid": True,
                "class_name": validation["class_name"],
                "metric_name": validation["metric_name"],
                "message": "Code validation passed"
            }
        else:
            return {
                "valid": False,
                "error": validation["error"]
            }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }

@app.get("/metrics")
async def list_metrics():
    """List all available metrics"""
    try:
        metrics_path = os.path.join("llm_consortium", "metrics")
        if not os.path.exists(metrics_path):
            return {"metrics": []}
        
        metric_files = []
        for file in os.listdir(metrics_path):
            if file.endswith(".py") and not file.startswith("__"):
                metric_files.append({
                    "filename": file,
                    "name": os.path.splitext(file)[0]
                })
        
        return {"metrics": metric_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing metrics: {str(e)}")

@app.delete("/metrics/{metric_name}")
async def delete_metric(metric_name: str):
    """Delete a metric file"""
    try:
        metrics_path = os.path.join("llm_consortium", "metrics")
        file_path = os.path.join(metrics_path, f"{metric_name.lower()}.py")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Metric file not found")
        
        os.remove(file_path)
        return {"success": True, "message": f"Metric '{metric_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting metric: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Custom Metrics Manager is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)