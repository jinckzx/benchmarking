
import streamlit as st
from llm_consortium.ui_utils.custom_metric_utils import (
extract_class_name,
save_custom_metric_to_file,
register_custom_metric,
extract_metric_name

)
from .codegen_llm import generate_metric_code
import textwrap
def render_custom_metric_tabs():
    tabs = st.tabs(["🔮 Prompt (LLM-as-Judge)", "🐍 Python Metric Class"])
    
    # First tab with its own form
# First tab with its own form
    with tabs[0]:
        # Initialize the keys_list in session state if it doesn't exist
        if "llm_judge_keys" not in st.session_state:
            st.session_state.llm_judge_keys = [{"key": "", "score": ""}]

        # ---------------------- Main Form for Metric Definition ----------------------
        with st.form("llm_judge_form"):
            st.text_input(
                "Metric Name",
                key="llm_judge_metric_name",
                placeholder="e.g., joinclause"
            )

            st.text_area(
                "Prompt for LLM-as-Judge",
                key="llm_judge_prompt",
                height=150,
                placeholder="e.g., Check whether [generated_sql] has the join clause or not"
            )

            st.subheader("Response Mapping")
            st.caption("Define how LLM responses map to scores")

            # Display current response mappings
            for i, kv_pair in enumerate(st.session_state.llm_judge_keys):
                cols = st.columns([3, 2])
                with cols[0]:
                    st.session_state.llm_judge_keys[i]["key"] = st.text_input(
                        "Response", value=kv_pair["key"], key=f"llm_key_{i}")
                with cols[1]:
                    st.session_state.llm_judge_keys[i]["score"] = st.text_input(
                        "Score", value=kv_pair["score"], key=f"llm_score_{i}")

            st.form_submit_button("✅ Update Responses")

        # ---------------------- Delete Buttons (outside main form) ----------------------
        st.markdown("### Manage Responses")
        for i in range(len(st.session_state.llm_judge_keys)):
            delete_col = st.columns([1])[0]
            with delete_col:
                if st.button(f"🗑️ Delete Response {i+1}", key=f"delete_key_btn_{i}"):
                    if len(st.session_state.llm_judge_keys) > 1:
                        st.session_state.llm_judge_keys.pop(i)
                        st.rerun()

        # ---------------------- Add Another Response ----------------------
        with st.form("add_response_form"):
            if st.form_submit_button("➕ Add Another Response"):
                st.session_state.llm_judge_keys.append({"key": "", "score": ""})
                st.rerun()

        
# ---------------------- Generate Metric Code ----------------------
        with st.form("generate_metric_code_form"):
            if st.form_submit_button("🚀 Generate Metric Code"):
                try:
                    
                    metric_name = st.session_state.llm_judge_metric_name
                    prompt = st.session_state.llm_judge_prompt
                    keys = st.session_state.llm_judge_keys
                    
                    if not metric_name:
                        st.error("❌ Please provide a metric name")
                        st.stop()
                    
                    if not prompt:
                        st.error("❌ Please provide a prompt for the LLM")
                        st.stop()
                    
                    # Validate we have at least one key-value mapping
                    valid_keys = [kv for kv in keys if kv["key"] and kv["score"]]
                    if not valid_keys:
                        st.error("❌ Please provide at least one valid response mapping")
                        st.stop()
                    
                    metric_code = generate_metric_code(metric_name, prompt, keys)
                    st.session_state.sql_custom_metric_code = metric_code
                    st.success("✅ Metric code generated! Switch to Python tab.")
                    
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")

    # Second tab with its own form
    with tabs[1]:
        with st.form("python_metric_form"):
            st.code('''from .base_metrics import BaseMetric
from typing import Dict, Any

class SQLExactMatch(BaseMetric):
    """Exact match comparison for SQL queries"""
    def __init__(self):
        super().__init__(
            name="exact_match",
            description="Exact string match between generated and reference SQL",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        try:
            generated_norm = generated_sql.lower().strip()
            gold_norm = gold_sql.lower().strip()
            return {"exact_match": generated_norm == gold_norm}
        except AttributeError:
            return {"exact_match": False, "error": "Invalid SQL inputs"}
''', language="python")

            code = st.text_area(
                "Custom metric class code",
                value=st.session_state.get("sql_custom_metric_code", ""),
                key="sql_custom_metric_code",
                height=300,
                placeholder="Write your BaseMetric-compatible class code here..."
            )
            
            if st.form_submit_button("💾 Save Metric"):
                try:
                    custom_code = st.session_state.sql_custom_metric_code
                    class_name = extract_class_name(custom_code)
                    metric_name = extract_metric_name(custom_code)
                    file_path = save_custom_metric_to_file(custom_code, metric_name)
                    register_custom_metric(file_path, class_name, metric_name)
                    st.success(f"✅ Custom metric '{metric_name}' saved and registered!")
                except Exception as e:
                    st.error(f"❌ Error saving metric: {e}")