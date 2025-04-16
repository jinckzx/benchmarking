# components.py
import streamlit as st
import pandas as pd
import altair as alt
from llm_consortium.utils.pricing import calculate_cost

def configure_sidebar():
    """Configure and render the sidebar components"""
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        model_selector = st.selectbox(
            "Select Model",
            ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"]
        )
        instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
        # Model management buttons
        col1, col2 = st.columns(2)
        with col1:
            add_update = st.button("Add/Update Model")
        with col2:
            clear_all = st.button("Clear All Models")

        # Display current models
        if st.session_state.models:
            st.subheader("Selected Models")
            for idx, (model, count) in enumerate(st.session_state.models):
                cols = st.columns([3, 2, 1])
                cols[0].write(f"**{model}**")
                cols[1].write(f"Instances: {count}")
                if cols[2].button("❌", key=f"delete_{idx}"):
                    st.session_state.models.pop(idx)
                    st.rerun()
        else:
            st.info("No models added yet")

        # Consortium parameters
        st.subheader("Consortium Parameters")
        arbiter = st.selectbox(
            "Arbiter Model",
            ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"],
            index=2
        )
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
        max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
        min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)
        
        return arbiter, confidence, max_iter, min_iter #, model_selector, instance_count, add_update, clear_all
    
        

def display_cost_estimation(arbiter, max_iter):
    """Render the cost estimation panel"""
    st.subheader("Cost Estimation")
    if st.session_state.models:
        models_dict = {}
        for model, count in st.session_state.models:
            models_dict[model] = models_dict.get(model, 0) + count
        
        models_with_arbiter = [(k, v) for k, v in models_dict.items()]
        if models_with_arbiter:
            models_with_arbiter.append((arbiter, 1))
            total_cost, cost_df = calculate_cost(models_with_arbiter, max_iter)
            st.dataframe(cost_df, use_container_width=True)
            st.metric("Estimated Total Cost", f"${total_cost:.4f}")
    else:
        st.info("Add models to see cost estimation")
    st.caption("*Based on average of 500 input tokens and 300 output tokens per request*")

def display_results(result, arbiter, max_iter):
    """Render the results section with visualizations"""
    # Calculate actual cost
    iterations = result.get("iterations", max_iter)
    models_with_arbiter = st.session_state.models.copy()
    models_with_arbiter.append((arbiter, 1))
    total_cost, cost_df = calculate_cost(models_with_arbiter, iterations)
    
    # Display results
    st.subheader("Execution Results")
    
    with st.expander("Synthesized Answer", expanded=True):
        st.write(result.get("synthesis", {}).get("text", "No synthesis result"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Actual Cost", f"${total_cost:.4f}")
    with col2:
        st.metric("Iterations Completed", iterations)
    
    st.subheader("Model Responses")
    responses = [{
        "Model": r.get("model", "Unknown"),
        "Response": (r.get("response", "")[:200] + "...") if len(r.get("response", "")) > 200 else r.get("response", ""),
        "Confidence": r.get("confidence", 0),
        "Latency": f"{r.get('latency', 0):.2f}s"
    } for r in result.get("raw_responses", [])]
    st.dataframe(pd.DataFrame(responses), use_container_width=True)

    # Visualization
    if responses:
        st.subheader("Performance Analysis")
        visualize_performance(responses, iterations)

def visualize_performance(responses, iterations):
    """Render performance visualization charts"""
    df = pd.DataFrame([{
        "Model": r["model"].split("-")[0],  # Base model name
        "Confidence": r["confidence"],
        "Latency": r["latency"],
        "Response Length": len(r["response"])
    } for r in responses])

    # Confidence Comparison
    st.write("### Confidence Distribution")
    confidence_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Model:N', title='Model'),
        y=alt.Y('mean(Confidence):Q', title='Average Confidence'),
        color='Model:N',
        tooltip=['Model', 'mean(Confidence)']
    ).properties(height=300)
    st.altair_chart(confidence_chart, use_container_width=True)

    # Latency vs Confidence
    st.write("### Latency vs Confidence")
    scatter = alt.Chart(df).mark_circle(size=60).encode(
        x='Latency:Q',
        y='Confidence:Q',
        color='Model:N',
        tooltip=['Model', 'Confidence', 'Latency']
    ).properties(height=300)
    st.altair_chart(scatter, use_container_width=True)

def render_file_uploader():
    """Render the RAG file upload component"""
    return st.file_uploader(
        "Upload knowledge file (PDF, DOCX, TXT, CSV)",
        type=["pdf", "docx", "txt", "csv"],
        key="rag_uploader"
    )

def render_execution_mode_selector():
    """Render the execution mode radio buttons"""
    return st.radio(
        "Execution Mode:",
        ["Standard Prompt", "RAG Mode"],
        horizontal=True,
        help="Select between standard prompt execution or RAG-enhanced execution"
    )

def render_main_prompt_input():
    """Render the main prompt input text area"""
    return st.text_area("Input Prompt", height=150, placeholder="Enter your prompt here...")

def render_execution_button():
    """Render the primary execution button"""
    return st.button("Run Consortium", type="primary", use_container_width=True)