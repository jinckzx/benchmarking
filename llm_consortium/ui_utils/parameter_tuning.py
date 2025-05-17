import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

def create_best_parameter_tab():
    """Creates the Best Parameter tab UI component"""
    
    # Check if we have tuning results
    if not st.session_state.get('sql_tuning_trials'):
        st.info("No parameter tuning results available. Run evaluation with parameter tuning enabled to see results.")
        return
    
    st.header("Best Parameter Selection")
    
    # Get data from session state
    trials = st.session_state.sql_tuning_trials
    
    # Create dataframe from trials
    trials_df = pd.DataFrame(trials)
    
    # Get list of all metrics (excluding temperature)
    metrics = [col for col in trials_df.columns if col != 'temperature']
    
    # Create visualization section
    st.subheader("Temperature vs Metrics Performance")
    
    # Create metric selector
    selected_metrics = st.multiselect(
        "Select metrics to compare", 
        options=metrics,
        default=[m for m in metrics if 'rate' in m or 'score' in m][:2]  # Default to first two rate/score metrics
    )
    
    if selected_metrics:
        # Prepare chart data
        chart_data = trials_df[['temperature'] + selected_metrics].copy()
        
        # Melt the dataframe for visualization
        chart_data_melted = chart_data.melt(
            id_vars=['temperature'], 
            value_vars=selected_metrics,
            var_name='Metric', 
            value_name='Value'
        )
        
        # Create the line chart
        chart = alt.Chart(chart_data_melted).mark_line(point=True).encode(
            x=alt.X('temperature:Q', title='Temperature'),
            y=alt.Y('Value:Q', title='Metric Value'),
            color='Metric:N',
            tooltip=['temperature', 'Metric', 'Value']
        ).properties(
            width=600,
            height=400
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    
    # Create best temperature selector
    st.subheader("Select Best Temperature Based on Metric")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_metric = st.selectbox(
            "Select metric to optimize", 
            options=metrics,
            index=metrics.index('execution_match_rate') if 'execution_match_rate' in metrics else 0
        )
    
    with col2:
        optimize_direction = st.radio(
            "Optimization direction",
            options=["Higher is better", "Lower is better"],
            index=0 if 'rate' in target_metric or 'score' in target_metric else 1
        )
    
    # Find best temperature based on selected metric
    if optimize_direction == "Higher is better":
        best_idx = trials_df[target_metric].idxmax()
    else:
        best_idx = trials_df[target_metric].idxmin()
    
    best_temp = trials_df.loc[best_idx, 'temperature']
    best_value = trials_df.loc[best_idx, target_metric]
    
    # Display recommended temperature
    st.metric("Recommended Temperature", f"{best_temp:.2f}")
    st.metric(f"Best {target_metric} Value", f"{best_value:.2f}" + ("%" if 'rate' in target_metric else ""))
    
    # Display detailed trial results
    st.subheader("All Temperature Trial Results")
    
    # Format the dataframe for display
    display_df = trials_df.copy()
    for col in display_df.columns:
        if 'rate' in col:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")
        elif display_df[col].dtype != 'object':
            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Option to apply selected temperature
    if st.button("Apply Selected Temperature"):
        # Store the selected temperature in session state
        st.session_state.sql_selected_temperature = best_temp
        st.success(f"Temperature {best_temp:.2f} has been selected!")

