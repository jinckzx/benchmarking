import os
import streamlit as st
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from ..core.client_init import llm

import os




st.title("SQL Metric Class Generator")

# Step 1: Metric name
metric_name = st.text_input("Enter the metric name (e.g., abhinav)")

# Step 2: Key-value dictionary
n = st.number_input("How many key-value pairs do you want to enter?", min_value=1, max_value=10, step=1)

user_dict = {}
float_dict = {}

st.subheader("Enter key-value pairs (values must be numeric between 0 and 1):")
for i in range(n):
    key = st.text_input(f"Key {i+1}", key=f"key_{i}")
    value = st.text_input(f"Value {i+1}", key=f"value_{i}")
    if key:
        user_dict[key] = value
        try:
            float_val = float(value)
            float_dict[key] = float_val
        except ValueError:
            st.error(f"Value for '{key}' is not a valid number.")

# Check if values are in correct range and sum is valid
valid_sum = False
if float_dict:
    total = sum(float_dict.values())
    if 0 <= total <= 1:
        valid_sum = True
    else:
        st.error(f"Sum of values is {total:.3f}, which is outside the allowed range [0, 1].")

# Step 3: NLQ prompt and sample SQLs
nlq = st.text_input("Enter the Natural Language Query (Prompt to LLM)")
output1 = "SELECT order_id, order_date, customer_id, amount FROM sales_db.orders;"
ex_output1 = "SELECT order_id, order_date, customer_id, amount FROM sales_db.orders;"

st.subheader("SQL Query to Analyze")
st.code(nlq, language="sql")

# Step 4: Generate Python metric script
if st.button("Generate Metric Script"):
    if not valid_sum:
        st.warning("Cannot proceed: Sum of values must be between 0 and 1.")
    elif not metric_name.isidentifier():
        st.error("Metric name must be a valid Python identifier (e.g., abhinav, metric_1).")
    else:
        class_name = f"SQL{metric_name.capitalize()}"
        filename = f"scripts/{metric_name}.py"
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, filename)

        if os.path.exists(filename):
            st.error(f"The file '{filename}' already exists. Choose a different metric name.")
        else:
            # Format user_dict as a Python dictionary string
            user_dict_str = "{\n" + ",\n".join(f'            "{k}": "{v}"' for k, v in user_dict.items()) + "\n        }"

            script_content = f"""from .base_metrics import BaseMetric
from typing import Dict, Any
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from ..core.client_init import llm



class {class_name}(BaseMetric):
    \"\"\"Exact match comparison for SQL queries\"\"\"
    def __init__(self):
        super().__init__(
            name="{metric_name}",
            description="Exact string match between generated and reference SQL",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )

    def check_sql_query(self, nlq: str, output: str, expected_output: str) -> str:
        nlq_prompt = nlq.format(output=output, expected_output=expected_output)
        message = HumanMessage(content=nlq_prompt)
        result = llm([message])
        return result.content.strip()

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        prompt = "{nlq.strip()}"
        user_dict = {user_dict_str}

        result = self.check_sql_query(prompt, generated_sql, gold_sql)
        score = user_dict.get(result, "0.0")
        return {{
            "result": result,
            "{metric_name}": score
        }}
"""

            
            with open(filename, "w") as f:
                f.write(script_content)

            st.success(f"Saved new metric script to '{filename}'")