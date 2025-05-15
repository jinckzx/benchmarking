# # ui_utils/custom_metric_utils.py

# import os
# import re
# import importlib.util
# import sys
# from llm_consortium.metrics.registry import MetricRegistry

# def extract_class_name(code_str: str) -> str:
#     match = re.search(r'class\s+(\w+)\(BaseMetric\):', code_str)
#     if match:
#         return match.group(1)
#     raise ValueError("No valid metric class found inheriting BaseMetric.")

# def save_custom_metric_to_file(code_str: str, class_name: str) -> str:
#     metrics_path = os.path.join("llm_consortium", "metrics")
#     filename = f"{class_name.lower()}.py"
#     full_path = os.path.join(metrics_path, filename)
#     os.makedirs(metrics_path, exist_ok=True)
#     with open(full_path, "w", encoding="utf-8") as f:
#         f.write(code_str)
#     return full_path

# def dynamic_import_metric(file_path: str, class_name: str):
#     module_name = os.path.splitext(os.path.basename(file_path))[0]
#     full_module_name = f"llm_consortium.metrics.{module_name}"
#     spec = importlib.util.spec_from_file_location(full_module_name, file_path)
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[full_module_name] = module
#     spec.loader.exec_module(module)
#     return getattr(module, class_name)

# def register_custom_metric(file_path: str, class_name: str, task: str = "sql"):
#     metric_class = dynamic_import_metric(file_path, class_name)
#     instance = metric_class()

#     # Add to runtime registry
#     registry = MetricRegistry()
#     registry.register_metric(task, instance)

#     # Persistently update registry.py
#     update_registry_file(class_name)
# def update_registry_file(class_name: str):
#     registry_path = os.path.join("llm_consortium", "metrics", "registry.py")

#     # Read the existing content
#     with open(registry_path, "r", encoding="utf-8") as f:
#         lines = f.readlines()

#     # Prepare new import
#     import_line = f"from .{class_name.lower()} import {class_name}\n"

#     # Check if import already exists
#     if import_line not in lines:
#         # Insert after the last existing import
#         last_import_index = max(i for i, line in enumerate(lines) if line.startswith("from ."))
#         lines.insert(last_import_index + 1, import_line)

#     # Add instantiation inside __init__
#     init_index = next(i for i, line in enumerate(lines) if "def __init__" in line)
#     brace_index = next(i for i in range(init_index, len(lines)) if "{" in lines[i] and '"sql": {' in lines[i])

#     # Compute indentation
#     indent = " " * (len(lines[brace_index]) - len(lines[brace_index].lstrip()) + 4)
#     add_metric_line = f'{indent}"{class_name.lower()}": {class_name}(),\n'

#     # Prevent duplicates
#     if add_metric_line not in lines:
#         # Insert before the closing brace of "sql"
#         close_index = next(i for i in range(brace_index, len(lines)) if "}" in lines[i])
#         lines.insert(close_index, add_metric_line)

#     # Write back the modified content
#     with open(registry_path, "w", encoding="utf-8") as f:
#         f.writelines(lines)

import os
import re
import importlib.util
import sys
from llm_consortium.metrics.registry import MetricRegistry

def extract_metric_name(code_str: str) -> str:
    """Extract the metric name from the name parameter in __init__"""
    match = re.search(r'name="([^"]+)"', code_str)
    if match:
        return match.group(1)
    # Fallback to class name if no name parameter found
    class_match = re.search(r'class\s+(\w+)\(BaseMetric\):', code_str)
    if class_match:
        return class_match.group(1)
    raise ValueError("No valid metric name or class found.")

def extract_class_name(code_str: str) -> str:
    """Extract the class name from the metric code"""
    match = re.search(r'class\s+(\w+)\(BaseMetric\):', code_str)
    if match:
        return match.group(1)
    raise ValueError("No valid metric class found inheriting BaseMetric.")

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

def register_custom_metric(file_path: str, class_name: str, metric_name: str = None, task: str = "sql"):
    """Register the custom metric in the registry"""
    metric_class = dynamic_import_metric(file_path, class_name)
    instance = metric_class()
    
    # If metric_name is not provided, try to get it from the instance
    if metric_name is None:
        try:
            metric_name = instance.name
        except (AttributeError, TypeError):
            # Fallback to class name if instance doesn't have a name attribute
            metric_name = class_name.lower()
    
    # Add to runtime registry
    registry = MetricRegistry()
    registry.register_metric(task, instance)
    
    # Persistently update registry.py
    update_registry_file(class_name, metric_name)

def update_registry_file(class_name: str, metric_name: str):
    """Update the registry file to include the new metric"""
    registry_path = os.path.join("llm_consortium", "metrics", "registry.py")
    # Read the existing content
    with open(registry_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Get the module name from the metric name
    module_name = metric_name.lower()
    
    # Prepare new import
    import_line = f"from .{module_name} import {class_name}\n"
    
    # Check if import already exists
    if import_line not in lines:
        # Insert after the last existing import
        last_import_index = max(i for i, line in enumerate(lines) if line.startswith("from ."))
        lines.insert(last_import_index + 1, import_line)
    
    # Add instantiation inside __init__
    init_index = next(i for i, line in enumerate(lines) if "def __init__" in line)
    brace_index = next(i for i in range(init_index, len(lines)) if "{" in lines[i] and '"sql": {' in lines[i])
    
    # Compute indentation
    indent = " " * (len(lines[brace_index]) - len(lines[brace_index].lstrip()) + 4)
    add_metric_line = f'{indent}"{metric_name.lower()}": {class_name}(),\n'
    
    # Prevent duplicates
    if add_metric_line not in lines:
        # Insert before the closing brace of "sql"
        close_index = next(i for i in range(brace_index, len(lines)) if "}" in lines[i])
        lines.insert(close_index, add_metric_line)
    
    # Write back the modified content
    with open(registry_path, "w", encoding="utf-8") as f:
        f.writelines(lines)