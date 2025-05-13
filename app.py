## OG CODE ##
### Streamlit code  ###

# import streamlit as st
# from llm_consortium.core.runner import ConsortiumRunner
# from llm_consortium.config.models import ConsortiumConfig
# import asyncio
# import json
# import tempfile
# import pandas as pd
# import altair as alt
# from llm_consortium.utils.pricing import MODEL_PRICING, AVG_INPUT_TOKENS, AVG_OUTPUT_TOKENS, calculate_cost


# def main():
#     st.set_page_config(
#         layout="wide",
#         page_title="LLM Consortium"
#     )

# Sidebar navigation
    # with st.sidebar:
    #     st.header("Evaluation Types")
    #     app_mode = st.radio(
    #         "Select Evaluation Mode",
    #         ["prompt_eval", "RAG_eval", "Spider_eval"],
    #         index=0
    #     )

    # if app_mode == "prompt_eval":
    #     prompt_eval_page()
    # elif app_mode == "RAG_eval":
    #     rag_eval_page()
    # elif app_mode == "Spider_eval":
    #     spider_eval_page()

# def prompt_eval_page():
#     st.title("LLM Consortium - Prompt Evaluation")


    
#     st.markdown("""
#     <style>
#     .block-container { padding-top: 1rem; padding-bottom: 0rem; }
#     div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
#     </style>
#     """, unsafe_allow_html=True)

#     st.title("LLM Consortium")
#     runner = ConsortiumRunner()
    
#     # Initialize session state for models
#     if 'models' not in st.session_state:
#         st.session_state.models = []
    
#     # Layout with columns
#     col1, col2 = st.columns([2, 3])
    
#     with col1:
#         st.header("Configuration")
        
#         # Model selection
#         model_selector = st.selectbox(
#             "Select Model",
#             ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"]
#         )
#         instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
#         # Add model button
#         if st.button("Add Model"):
#             # Check if model already exists
#             existing_index = -1
#             for idx, (model, count) in enumerate(st.session_state.models):
#                 if model == model_selector:
#                     existing_index = idx
#                     break

#             if existing_index >= 0:
#                 # Update existing entry
#                 st.session_state.models[existing_index] = (model_selector, int(instance_count))
#             else:
#                 # Add new entry
#                 st.session_state.models.append((model_selector, int(instance_count)))
#                 st.rerun() # Refresh the UI to show updated list

#         # Display models with delete buttons
#         if st.session_state.models:
#             st.write("### Selected Models")
#             for idx, (model, count) in enumerate(st.session_state.models):
#                 cols = st.columns([4, 2, 1])
#                 with cols[0]:
#                     st.markdown(f"**{model}**")
#                 with cols[1]:
#                     st.markdown(f"Instances: {count}")
#                 with cols[2]:
#                     if st.button("❌", key=f"delete_{idx}"):
#                         st.session_state.models.pop(idx)
#                         st.rerun()
#         else:
#             st.info("No models added yet")
        
#         # Arbiter and other settings
#         arbiter = st.selectbox(
#             "Arbiter Model",
#             ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"],
#             index=2
#         )
        
#         confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
#         max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
#         min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)
        
    
#     with col2:
#         st.header("Execution")
#         prompt = st.text_area("Input Prompt", height=150)

#         # Cost estimation
#         st.write("### Cost Estimation (Including Arbiter)")
#         if st.session_state.models:

#             #Aggregate models with their instances
#             models_dict = {}
#             for model, count in st.session_state.models:
#                 models_dict[model] = models_dict.get(model, 0) + count
            
#             # Add arbiter as separate entry
#             models_with_arbiter = [(k, v) for k, v in models_dict.items()]
#             models_with_arbiter.append((arbiter, 1))
#             total_cost, cost_df = calculate_cost(models_with_arbiter, max_iter)
#             st.dataframe(cost_df, use_container_width=True)
#             st.write(f"**Estimated Total Cost:** ${total_cost:.4f}")
#         else:
#             st.info("Add models to see cost estimation")
#         st.caption("*Based on average of 500 input tokens and 300 output tokens per request*")
        
#         # Run Consortium button
#         if st.button("Run Consortium", type="primary"):
#             if not st.session_state.models:
#                 st.error("Please add at least one model")
#                 return
            
#             # Convert models list to dictionary
#             models_dict = {model: count for model, count in st.session_state.models}
            
#             # Create ConsortiumConfig
#             config = ConsortiumConfig(
#                 models=models_dict,
#                 arbiter=arbiter,
#                 confidence_threshold=confidence,
#                 max_iterations=int(max_iter),
#                 min_iterations=int(min_iter)
#             )

#             # Run the consortium
#             result = asyncio.run(runner.run_consortium(config, prompt))
            
#             # Get actual iterations completed
#             iterations = result.get("iterations", int(max_iter))

#             # Calculate final cost including arbiter
#             models_with_arbiter = st.session_state.models.copy()
#             models_with_arbiter.append((arbiter, 1))  # Arbiter counts as 1 instance
#             total_cost, cost_df = calculate_cost(models_with_arbiter, result.get("iterations", int(max_iter)))
            
#             # Save results to temporary file
#             with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
#                 json.dump({
#                     **result,
#                     "cost_estimation": {
#                         "total_cost": total_cost,
#                         "breakdown": cost_df.to_dict('records'),
#                         "iterations": result.get("iterations", int(max_iter))
#                     }
#                 }, f, indent=2)
#                 tmp_file = f.name
            
#             # Display results

#             st.subheader("Actual Cost")
#             st.write(f"${total_cost:.4f} (after {result.get('iterations', int(max_iter))} iterations)")
            
#             st.subheader("Synthesized Answer")
#             st.write(result.get("synthesis", {}).get("text", "No synthesis result"))
            
            
#             st.subheader("Individual Responses")
#             responses = [
#                 {
#                     "Model": r.get("model", "Unknown"),
#                     "Response": r.get("response", "")[:100] + "..." if len(r.get("response", "")) > 100 else r.get("response", ""),
#                     "Confidence": r.get("confidence", 0),
#                     "Latency": f"{r.get('latency', 0):.2f}s",
#                     "Cost": f"${(MODEL_PRICING.get(r.get('model', 'Unknown').rsplit('-', 1)[0], {}).get('input', 0) * AVG_INPUT_TOKENS / 1000 * iterations + MODEL_PRICING.get(r.get('model', 'Unknown').rsplit('-', 1)[0], {}).get('output', 0) * AVG_OUTPUT_TOKENS / 1000 * iterations):.4f}"
#                 } for r in result.get("raw_responses", [])
#             ]
#             st.dataframe(pd.DataFrame(responses), use_container_width=True)


#             st.subheader("Model Performance Analysis")
#             # Create dataframe for visualization
#             model_data = pd.DataFrame([
#                 {
#                     "Model": r["model"].split("-")[0],  # Base model name
#                     "Confidence": r["confidence"],
#                     "Latency": r["latency"],
#                     "Response Length": len(r["response"])
#                 } for r in result.get("raw_responses", [])
#             ])
            

#             if not model_data.empty:

#                 # Confidence comparison of Models
#                 st.subheader("Model Confidence Comparison")
                
#                 # Create dataframe with individual model responses
#                 model_comparison_df = pd.DataFrame([
#                 {
#                     "Model": r.get("model", "Unknown"),
#                     "Confidence": r.get("confidence", 0),
#                     "Latency": r.get("latency", 0)
#                     }
#                 for r in result.get("raw_responses", [])
#                     ])

#                 if not model_comparison_df.empty:
#                     # Create bar chart
#                     bar_chart = alt.Chart(model_comparison_df).mark_bar().encode(
#                         x=alt.X('Model:N', title='Model Instance', sort='-y'),
#                         y=alt.Y('Confidence:Q', title='Confidence Score', scale=alt.Scale(domain=[0, 1])),
#                         color=alt.Color('Model:N', legend=None),
#                         tooltip=['Model', 'Confidence', 'Latency']
#                     ).properties(
#                         width=800,
#                         height=400,
#                         title='Confidence Scores by Model Instance'
#                     )
                
#                 # Add text labels
#                 text = bar_chart.mark_text(
#                     align='center',
#                     baseline='bottom',
#                     dy=-5,
#                     color='black'
#                     ).encode(
#                     text=alt.Text('Confidence:Q', format='.2f')
#                 )
#                 st.altair_chart(bar_chart + text)
                
#                 # Latency vs Confidence Scatter Plot
#                 st.write("### Latency vs Confidence")
#                 scatter = alt.Chart(model_data).mark_circle(size=60).encode(
#                     x='Latency:Q',
#                     y='Confidence:Q',
#                     color='Model:N',
#                     tooltip=['Model', 'Confidence', 'Latency']
#                 ).properties(width=600, height=300)
#                 st.altair_chart(scatter)
                
#             else:
#                 st.warning("No response data available for visualization")
            
#             # Download button
#             with open(tmp_file, "rb") as f:
#                 st.download_button(
#                     label="Download Results",
#                     data=f,
#                     file_name="consortium_results.json",
#                     mime="application/json"
#                 )

# def rag_eval_page():
#     st.title("LLM Consortium - RAG Evaluation")
#     st.write("RAG Evaluation Content Will Display here")
#     # Add your RAG-specific content here

# def spider_eval_page():
#     st.title("LLM Consortium - Spider Evaluation")
#     st.write("Spider Evaluation Content Will Display Here")
#     # Add your Spider-specific content here


# if __name__ == "__main__":
#     main()


























import streamlit as st
from llm_consortium.core.runner import ConsortiumRunner
from llm_consortium.config.models import ConsortiumConfig
import asyncio
import json
import tempfile
import pandas as pd
import altair as alt
from llm_consortium.utils.pricing import MODEL_PRICING, AVG_INPUT_TOKENS, AVG_OUTPUT_TOKENS, calculate_cost
import streamlit as st
import asyncio
import pandas as pd
import altair as alt
import tempfile
import json
from llm_consortium.config.models import ConsortiumConfig
from llm_consortium.core.runner import ConsortiumRunner

def main():
    st.set_page_config(
        layout="wide",
        page_title="GenAI App Tuner"
    )

    # Sidebar navigation
    with st.sidebar:
        st.header("Evaluation Types")
        app_mode = st.radio(
            "Select Evaluation Mode",
            ["Non-RAG_eval", "new_sql", "classification new", "sql metrics module"], # ["RAG_eval", "Text2SQL_eval","Classification_Eval"]
            index=0
        )

    if app_mode == "Non-RAG_eval":
        prompt_eval_page()
    # elif app_mode == "RAG_eval":
    #     rag_eval_page()
    # elif app_mode == "Text2SQL_eval":
    #     spider_eval_page()
    # elif app_mode == "Classification_Eval":
    #     classification_page()
    elif app_mode == "new_sql":
        text2sql_ui()
    elif app_mode == "classification new":
        classification_ui()
    elif app_mode =="sql metrics module":
        text2sql_ui_mm()
def prompt_eval_page():
    # st.title("GenAI App Tuner")

    # runner = ConsortiumRunner()
    
    # # Initialize session state for models
    # if 'models' not in st.session_state:
    #     st.session_state.models = []
    
    # # Layout with columns
    # col1, col2 = st.columns([2, 3])
    
    # with col1:
    #     st.header("Configuration")
        
    #     # Model selection
    #     model_selector = st.selectbox(
    #         "Select Model",
    #         ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"]
    #     )
    #     instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
    #     # Add model button
    #     if st.button("Add Model"):
    #         # Check if model already exists
    #         existing_index = -1
    #         for idx, (model, count) in enumerate(st.session_state.models):
    #             if model == model_selector:
    #                 existing_index = idx
    #                 break

    #         if existing_index >= 0:
    #             # Update existing entry
    #             st.session_state.models[existing_index] = (model_selector, int(instance_count))
    #         else:
    #             # Add new entry
    #             st.session_state.models.append((model_selector, int(instance_count)))
    #             st.rerun() # Refresh the UI to show updated list

    #     # Display models with delete buttons
    #     if st.session_state.models:
    #         st.write("### Selected Models")
    #         for idx, (model, count) in enumerate(st.session_state.models):
    #             cols = st.columns([4, 2, 1])
    #             with cols[0]:
    #                 st.markdown(f"**{model}**")
    #             with cols[1]:
    #                 st.markdown(f"Instances: {count}")
    #             with cols[2]:
    #                 if st.button("❌", key=f"delete_{idx}"):
    #                     st.session_state.models.pop(idx)
    #                     st.rerun()
    #     else:
    #         st.info("No models added yet")
        
    #     # Arbiter and other settings
    #     arbiter = st.selectbox(
    #         "Arbiter Model",
    #         ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"],
    #         index=2
    #     )
        
    #     confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
    #     max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
    #     min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)
        
    
    # with col2:
    #     st.header("Execution")
    #     prompt = st.text_area("Input Prompt", height=150)

    #     # Cost estimation
    #     st.write("### Cost Estimation (Including Arbiter)")
    #     if st.session_state.models:

    #         #Aggregate models with their instances
    #         models_dict = {}
    #         for model, count in st.session_state.models:
    #             models_dict[model] = models_dict.get(model, 0) + count
            
    #         # Add arbiter as separate entry
    #         models_with_arbiter = [(k, v) for k, v in models_dict.items()]
    #         models_with_arbiter.append((arbiter, 1))
    #         total_cost, cost_df = calculate_cost(models_with_arbiter, max_iter)
    #         st.dataframe(cost_df, use_container_width=True)
    #         st.write(f"**Estimated Total Cost:** ${total_cost:.4f}")
    #     else:
    #         st.info("Add models to see cost estimation")
    #     st.caption("*Based on average of 500 input tokens and 300 output tokens per request*")
        
    #     # Run Consortium button
    #     if st.button("Run Consortium", type="primary"):
    #         if not st.session_state.models:
    #             st.error("Please add at least one model")
    #             return
            
    #         # Convert models list to dictionary
    #         models_dict = {model: count for model, count in st.session_state.models}
            
    #         # Create ConsortiumConfig
    #         config = ConsortiumConfig(
    #             models=models_dict,
    #             arbiter=arbiter,
    #             confidence_threshold=confidence,
    #             max_iterations=int(max_iter),
    #             min_iterations=int(min_iter)
    #         )

    #         # Run the consortium
    #         result = asyncio.run(runner.run_consortium(config, prompt))
            
    #         # Get actual iterations completed
    #         iterations = result.get("iterations", int(max_iter))

    #         # Calculate final cost including arbiter
    #         models_with_arbiter = st.session_state.models.copy()
    #         models_with_arbiter.append((arbiter, 1))  # Arbiter counts as 1 instance
    #         total_cost, cost_df = calculate_cost(models_with_arbiter, result.get("iterations", int(max_iter)))
            
            # # Save results to temporary file
            # with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            #     json.dump({
            #         **result,
            #         "cost_estimation": {
            #             "total_cost": total_cost,
            #             "breakdown": cost_df.to_dict('records'),
            #             "iterations": result.get("iterations", int(max_iter))
            #         }
            #     }, f, indent=2)
            #     tmp_file = f.name
            
    #         # Display results

    #         st.subheader("Actual Cost")
    #         st.write(f"${total_cost:.4f} (after {result.get('iterations', int(max_iter))} iterations)")
            
    #         st.subheader("Synthesized Answer")
    #         st.write(result.get("synthesis", {}).get("text", "No synthesis result"))
            
            
    #         st.subheader("Individual Responses")
    #         responses = [
    #             {
    #                 "Model": r.get("model", "Unknown"),
    #                 "Response": r.get("response", "")[:100] + "..." if len(r.get("response", "")) > 100 else r.get("response", ""),
    #                 "Confidence": r.get("confidence", 0),
    #                 "Latency": f"{r.get('latency', 0):.2f}s",
    #                 "Cost": f"${(MODEL_PRICING.get(r.get('model', 'Unknown').rsplit('-', 1)[0], {}).get('input', 0) * AVG_INPUT_TOKENS / 1000 * iterations + MODEL_PRICING.get(r.get('model', 'Unknown').rsplit('-', 1)[0], {}).get('output', 0) * AVG_OUTPUT_TOKENS / 1000 * iterations):.4f}"
    #             } for r in result.get("raw_responses", [])
    #         ]
    #         st.dataframe(pd.DataFrame(responses), use_container_width=True)


    #         st.subheader("Model Performance Analysis")
    #         # Create dataframe for visualization
    #         model_data = pd.DataFrame([
    #             {
    #                 "Model": r["model"].split("-")[0],  # Base model name
    #                 "Confidence": r["confidence"],
    #                 "Latency": r["latency"],
    #                 "Response Length": len(r["response"])
    #             } for r in result.get("raw_responses", [])
    #         ])
            

    #         if not model_data.empty:

    #             # Confidence comparison of Models
    #             st.subheader("Model Confidence Comparison")
                
    #             # Create dataframe with individual model responses
    #             model_comparison_df = pd.DataFrame([
    #             {
    #                 "Model": r.get("model", "Unknown"),
    #                 "Confidence": r.get("confidence", 0),
    #                 "Latency": r.get("latency", 0)
    #                 }
    #             for r in result.get("raw_responses", [])
    #                 ])

    #             if not model_comparison_df.empty:
    #                 # Create bar chart
    #                 bar_chart = alt.Chart(model_comparison_df).mark_bar().encode(
    #                     x=alt.X('Model:N', title='Model Instance', sort='-y'),
    #                     y=alt.Y('Confidence:Q', title='Confidence Score', scale=alt.Scale(domain=[0, 1])),
    #                     color=alt.Color('Model:N', legend=None),
    #                     tooltip=['Model', 'Confidence', 'Latency']
    #                 ).properties(
    #                     width=800,
    #                     height=400,
    #                     title='Confidence Scores by Model Instance'
    #                 )
                
    #             # Add text labels
    #             text = bar_chart.mark_text(
    #                 align='center',
    #                 baseline='bottom',
    #                 dy=-5,
    #                 color='black'
    #                 ).encode(
    #                 text=alt.Text('Confidence:Q', format='.2f')
    #             )
    #             st.altair_chart(bar_chart + text)
                
    #             # Latency vs Confidence Scatter Plot
    #             st.write("### Latency vs Confidence")
    #             scatter = alt.Chart(model_data).mark_circle(size=60).encode(
    #                 x='Latency:Q',
    #                 y='Confidence:Q',
    #                 color='Model:N',
    #                 tooltip=['Model', 'Confidence', 'Latency']
    #             ).properties(width=600, height=300)
    #             st.altair_chart(scatter)
                
    #         else:
    #             st.warning("No response data available for visualization")

    
    
    st.title("GenAI App Tuner")
    
    # Initialize session state
    if 'models' not in st.session_state:
        st.session_state.models = []
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.header("Configuration")
        
        # Model selection
        model_selector = st.selectbox(
            "Select Model",
            ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"]
        )
        instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
        if st.button("Add Model"):
            existing_index = -1
            for idx, (model, count) in enumerate(st.session_state.models):
                if model == model_selector:
                    existing_index = idx
                    break
            if existing_index >= 0:
                st.session_state.models[existing_index] = (model_selector, int(instance_count))
            else:
                st.session_state.models.append((model_selector, int(instance_count)))
                st.rerun()

        if st.session_state.models:
            st.write("### Selected Models")
            for idx, (model, count) in enumerate(st.session_state.models):
                cols = st.columns([4, 2, 1])
                cols[0].markdown(f"**{model}**")
                cols[1].markdown(f"Instances: {count}")
                if cols[2].button("❌", key=f"delete_{idx}"):
                    st.session_state.models.pop(idx)
                    st.rerun()
        else:
            st.info("No models added yet")
        
        st.header("Arbiter Tuning")
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.1)
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.9)
        num_trials = st.number_input("Number of Trials", 1, 20, 5)
        if min_temp >= max_temp:
            st.error("Max temperature must be greater than min temperature")

        arbiter = st.selectbox(
            "Arbiter Model",
            ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"],
            index=2
        )
        
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
        max_iter = st.number_input("Max Iterations", 1, 10, 3)
        min_iter = st.number_input("Min Iterations", 1, 10, 1)
    
    with col2:
        st.header("Execution")
        prompt = st.text_area("Input Prompt", height=150)

        if st.session_state.models:
            models_dict = {model: count for model, count in st.session_state.models}
            models_with_arbiter = [(k, v) for k, v in models_dict.items()] + [(arbiter, 1)]
            total_cost, cost_df = calculate_cost(models_with_arbiter, max_iter)
            st.dataframe(cost_df, use_container_width=True)
            st.write(f"**Estimated Total Cost:** ${total_cost:.4f}")
        else:
            st.info("Add models to see cost estimation")
        st.caption("*Based on average of 500 input tokens and 300 output tokens per request*")
        
        if st.button("Run Consortium", type="primary"):
            if not st.session_state.models:
                st.error("Please add at least one model")
                return
            
            config = ConsortiumConfig(
                models={model: count for model, count in st.session_state.models},
                arbiter=arbiter,
                confidence_threshold=confidence,
                max_iterations=max_iter,
                min_iterations=min_iter,
                min_temp=min_temp,
                max_temp=max_temp,
                num_trials=num_trials
            )

            runner = ConsortiumRunner()
            
            with st.spinner("Running consortium..."):
                result = asyncio.run(runner.run_consortium(config, prompt))

            # Save results to temporary file for download
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(result, f, indent=2)
                tmp_file = f.name

            # Display results
            _display_results(result, config, tmp_file)

def _display_results(result, config, tmp_file):
    iterations = result.get("iterations", config.max_iterations)
    
    # Cost display
    models_with_arbiter = list(config.models.items()) + [(config.arbiter, 1)]
    total_cost, _ = calculate_cost(models_with_arbiter, iterations)
    st.subheader("Actual Cost")
    st.write(f"${total_cost:.4f} (after {iterations} iterations)")

    # Temperature tuning results
    if 'temperature_trials' in result:
        st.subheader("Temperature Tuning Results")
        tuning_data = pd.DataFrame(result['temperature_trials'])
        
        chart = alt.Chart(tuning_data).mark_line().encode(
            x='temperature:Q',
            y='confidence:Q',
            tooltip=['temperature', 'confidence']
        ).properties(width=700, height=300)
        
        best_point = alt.Chart(pd.DataFrame([{
            'temperature': result['synthesis']['temperature'],
            'confidence': result['synthesis']['confidence']
        }])).mark_circle(color='red', size=100).encode(
            x='temperature:Q',
            y='confidence:Q'
        )
        
        st.altair_chart(chart + best_point)
        st.write(f"**Best Temperature:** {result['synthesis']['temperature']:.2f}")
        st.write(f"**Achieved Confidence:** {result['synthesis']['confidence']:.2f}")

    # Synthesis result
    st.subheader("Synthesized Answer")
    st.write(result.get("synthesis", {}).get("text", "No synthesis result"))

    # Individual responses
    st.subheader("Individual Responses")
    responses_df = pd.DataFrame([
        {
            "Model": r.get("model", "Unknown"),
            "Response": r.get("response", "")[:100] + ("..." if len(r.get("response", "")) > 100 else ""),
            "Confidence": r.get("confidence", 0),
            "Latency": f"{r.get('latency', 0):.2f}s",
            "Cost": f"{_calculate_response_cost(r, iterations):.4f}"
        } for r in result.get("raw_responses", [])
    ])
    st.dataframe(responses_df, use_container_width=True)

    # Visualization
    _display_visualizations(result)

    # Download button
    with open(tmp_file, "rb") as f:
        st.download_button(
            label="Download Results",
            data=f,
            file_name="consortium_results.json",
            mime="application/json"
        )

def _calculate_response_cost(response, iterations):
    model_name = response.get("model", "Unknown").rsplit('-', 1)[0]
    pricing = MODEL_PRICING.get(model_name, {"input": 0, "output": 0})
    return (pricing["input"] * AVG_INPUT_TOKENS / 1000 * iterations +
            pricing["output"] * AVG_OUTPUT_TOKENS / 1000 * iterations)

def _display_visualizations(result):
    model_data = pd.DataFrame([
        {
            "Model": r.get("model","Unknown"),
            "Confidence": r["confidence"],
            "Latency": r["latency"],
            "Response Length": len(r["response"])
        } for r in result.get("raw_responses", [])
    ])

    if not model_data.empty:
        st.subheader("Model Confidence Comparison")
        bar_chart = alt.Chart(model_data).mark_bar().encode(
            x='Model:N',
            y='mean(Confidence):Q',
            color='Model:N',
            tooltip=['mean(Confidence)']
        ).properties(width=800, height=400)
        st.altair_chart(bar_chart)

        st.subheader("Latency vs Confidence")
        scatter = alt.Chart(model_data).mark_circle(size=60).encode(
            x='Latency:Q',
            y='Confidence:Q',
            color='Model:N',
            tooltip=['Model', 'Confidence', 'Latency']
        ).properties(width=600, height=300)
        st.altair_chart(scatter)
    
        # # Download button
        # with open(tmp_file, "rb") as f:
        #     st.download_button(
        #         label="Download Results",
        #         data=f,
        #         file_name="consortium_results.json",
        #         mime="application/json"
        #     )


def rag_eval_page():
    import streamlit as st
    from charset_normalizer import from_path
    from llm_consortium.core.rag_processor import RAGSystem, RAGConfig
    from pathlib import Path
    import os
    
    st.title("GenAI App Tuner")
    # st.write("RAG Evaluation Content Will Display here")
    
    
    # Initialize RAG system
    if 'rag' not in st.session_state:
        st.session_state.rag = RAGSystem()
    rag = st.session_state.rag
    
    # Configuration expander
    with st.expander("RAG Configuration", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Qdrant Settings")
            rag.config.qdrant_api_key = st.text_input(
                "Qdrant API Key",
                value=os.getenv("QDRANT_API_KEY", ""),
                type="password"
            )
            rag.config.qdrant_url = st.text_input(
                "Qdrant Cluster URL",
                value=os.getenv("QDRANT_URL", "https://localhost:6333")
            )
            rag.config.collection_name = st.text_input(
                "Collection Name",
                value=os.getenv("DOCUMENT_EMBEDDINGS_STORE", "rag_docs")
            )
        
        with col2:
            st.subheader("Model Settings")
            rag.config.embed_model_name = st.selectbox(
                "Embedding Model",
                ["BAAI/bge-base-en-v1.5", "BAAI/bge-small-en-v1.5"],
                index=0
            )
            st.caption(f"Embedding dimension: {rag.config.embedding_dim}")
    
    # Document processing section
    st.subheader("Document Ingestion")
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, TXT, MD, DOCX, etc..)",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        for i, file in enumerate(uploaded_files):
            try:
                progress_bar.progress((i+1)/len(uploaded_files), text=f"Processing {file.name}")
                rag.upload_file(file)
                st.toast(f"✅ {file.name} processed successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
        progress_bar.empty()
    
    # Query interface
    st.subheader("Query Interface")
    query = st.text_area("Enter your question:", height=150)
    
    if st.button("Run RAG Evaluation", type="primary"):
        if not query:
            st.warning("Please enter a question")
            return
        
        with st.spinner("Analyzing documents..."):
            try:
                # Execute query
                response = rag.query(query)
                
                # Display results
                st.subheader("Response")
                st.markdown(f"```\n{response}\n```")
                
                # Show source documents section
                st.subheader("Source Context")
                if rag.config.raw_files_dir.exists():
                    docs = list(rag.config.raw_files_dir.glob("*"))
                    for doc in docs:
                        with st.expander(f"📄 {doc.name}"):
                            try:
                                detected = from_path(doc)
                                best_match = detected.best()

                                if best_match:
                                    content = best_match.output
                                    preview = content[:2000] + ("..." if len(content) > 2000 else "")
                                    st.code(preview, language="text")
                                else:
                                    st.warning("Unsupported file format or encoding")
                            
                            except UnicodeDecodeError as ude:
                                st.error(f"Encoding error in {doc.name}: {str(ude)}")
                            except Exception as e:
                                st.error(f"Error displaying {doc.name}: {str(e)}")
            except Exception as e:
                st.error(f"RAG evaluation failed: {str(e)}")
def spider_eval_page():
    import streamlit as st
    import os
    import asyncio
    import tempfile
    import pandas as pd
    import altair as alt
    import uuid
    from datetime import datetime
    
    from llm_consortium.core.runner_sql import ConsortiumRunnerSQL
    from llm_consortium.config.models import ConsortiumConfig
    from llm_consortium.utils.pricing import calculate_cost
    
    # Import SQLMetrics class
    from llm_consortium.metrics.metrics_sql import SQLMetrics

    # Initialize session state
    if 'download_key' not in st.session_state:
        st.session_state.download_key = f"spider_init_{uuid.uuid4()}"

    if 'models' not in st.session_state:
        st.session_state.models = []
        
    st.title("GenAI App Tuner")

    runner_sql = ConsortiumRunnerSQL()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Configuration")
        model_selector = st.selectbox("Select Model", ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"])
        instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
        if st.button("Add Model"):
            new_models = {(m, c) for m, c in st.session_state.models if m != model_selector}
            new_models.add((model_selector, instance_count))
            st.session_state.models = list(new_models)
            st.rerun()
        
        if st.session_state.models:
            st.write("### Selected Models")
            for idx, (model, count) in enumerate(st.session_state.models):
                cols = st.columns([4, 2, 1])
                with cols[0]:
                    st.markdown(f"**{model}**")
                with cols[1]:
                    st.markdown(f"Instances: {count}")
                with cols[2]:
                    if st.button("❌", key=f"delete_{idx}"):
                        st.session_state.models.remove((model, count))
                        st.rerun()
        else:
            st.info("No models added yet")
        
        st.subheader("Arbiter Tuning")
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.1)
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.9)
        num_trials = st.number_input("Temperature Trials", 1, 20, 5)
        if min_temp >= max_temp:
            st.error("Max temperature must be greater than min temperature")
        
        arbiter = st.selectbox("Arbiter Model", ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"], index=2)
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
        max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
        min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)
        
        # Model temperature tuning section
        st.subheader("Model Temperature Tuning")
        enable_model_temp_tuning = st.checkbox("Enable Model Temperature Tuning", value=True)
        
        model_min_temp = 0.0
        model_max_temp = 0.0
        model_num_trials = 0
        
        if enable_model_temp_tuning:
            model_min_temp = st.slider("Model Min Temperature", 0.0, 1.0, 0.0, key="model_min_temp")
            model_max_temp = st.slider("Model Max Temperature", 0.0, 1.0, 0.7, key="model_max_temp")
            model_num_trials = st.number_input("Model Temperature Trials Per Model", 1, 10, 3, key="model_temp_trials")
            
            if model_min_temp >= model_max_temp:
                st.error("Model max temperature must be greater than min temperature")

    with col2:
        st.subheader("Execution")
        uploaded_file = st.file_uploader(
            "Upload CSV with queries (must include db_id, question, and query columns)",
            type=["csv"],
            help="CSV must contain 'db_id', 'question', and 'query' columns"
        )
        
        if uploaded_file is not None and st.session_state.models:
            models_dict = {model: count for model, count in st.session_state.models}
            total_cost, cost_df = calculate_cost(
                [(m, c) for m, c in models_dict.items()] + [(arbiter, 1)], 
                max_iter
            )
            st.write(f"**Estimated Cost:** ${total_cost:.4f}")
            st.dataframe(cost_df, use_container_width=True)
        elif uploaded_file:
            st.info("Add models to see cost estimation")

        if st.button("Run Consortium", type="primary"):
            if not st.session_state.models:
                st.error("Please add at least one model")
                st.stop()
            if not uploaded_file:
                st.error("Please upload a CSV file first")
                st.stop()

            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                csv_path = tmp_file.name
            
            # Load the CSV to get the ground truth queries
            input_df = pd.read_csv(uploaded_file)
            if not all(col in input_df.columns for col in ['db_id', 'question', 'query']):
                st.error("CSV must contain 'db_id', 'question', and 'query' columns")
                st.stop()
            
            models_dict = {model: count for model, count in st.session_state.models}
            
            # Create config with model temperature tuning parameters
            config = ConsortiumConfig(
                models=models_dict,
                arbiter=arbiter,
                confidence_threshold=confidence,
                max_iterations=int(max_iter),
                min_iterations=int(min_iter),
                min_temp=min_temp,
                max_temp=max_temp,
                num_trials=num_trials,
                # Model temperature parameters
                enable_model_temp_tuning=enable_model_temp_tuning,
                model_min_temp=model_min_temp,
                model_max_temp=model_max_temp,
                model_num_trials=model_num_trials
            )
            
            try:
                with st.spinner("Running consortium..."):
                    result = asyncio.run(runner_sql.run_consortium(config, csv_path))
                
                # Process and display results
                st.subheader("Results")
                
                # Model Temperature Analysis
                if enable_model_temp_tuning:
                    st.subheader("Model Temperature Analysis")
                    
                    # Create a dataframe for model temperature trials
                    model_temp_data = []
                    for query_result in result:
                        for response in query_result.get("raw_responses", []):
                            # Extract the temperature
                            temp = response.get("temperature")
                            if temp is not None:
                                model_temp_data.append({
                                    "Model": response.get("model", "Unknown"),
                                    "Temperature": float(temp),
                                    "Confidence": float(response.get("confidence", 0.0)),
                                    "Question": query_result.get("question", "N/A"),
                                    "DB ID": query_result.get("db_id", "N/A")
                                })
                    
                    if model_temp_data:
                        st.write(f"Found {len(model_temp_data)} temperature data points")
                        model_temp_df = pd.DataFrame(model_temp_data)
                        
                        # Create scatter plot of temperature vs confidence
                        scatter_chart = alt.Chart(model_temp_df).mark_circle(size=60).encode(
                            x=alt.X('Temperature:Q', scale=alt.Scale(domain=[0, 1])),
                            y='Confidence:Q',
                            color='Model:N',
                            tooltip=['Model', 'Temperature', 'Confidence', 'Question']
                        ).properties(
                            width=600,
                            height=400,
                            title="Model Temperature vs Confidence"
                        )
                        
                        st.altair_chart(scatter_chart, use_container_width=True)
                        
                        # Display raw data
                        with st.expander("View Model Temperature Data", expanded=True):
                            st.dataframe(model_temp_df)
                        
                        # Create box plot of confidence by model and temperature range
                        # First bin temperatures
                        model_temp_df['Temp Range'] = pd.cut(
                            model_temp_df['Temperature'], 
                            bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                            labels=['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']
                        )
                        
                        box_chart = alt.Chart(model_temp_df).mark_boxplot().encode(
                            x='Model:N',
                            y='Confidence:Q',
                            color='Model:N',
                            column='Temp Range:N'
                        ).properties(
                            title="Confidence Distribution by Temperature Range"
                        )
                        
                        st.altair_chart(box_chart, use_container_width=True)
                    else:
                        st.warning("No model temperature data available - Check the response structure:")
                        # Display the raw result structure for debugging
                        if result:
                            sample = result[0].get("raw_responses", [])[0] if result[0].get("raw_responses") else {}
                            st.write("Sample response keys:", list(sample.keys()))
                            st.json(sample)
                        else:
                            st.write("No results returned")
                
                # Evaluation metrics processing
                summary_data = []
                model_results = []  # List to track individual model performance
                
                for idx, query_result in enumerate(result):
                    best_result = query_result.get('best', {})
                    db_id = query_result.get('db_id', 'N/A')
                    question = query_result.get('question', 'N/A')
                    generated_sql = best_result.get('final_query', 'No SQL generated')
                    
                    # Find the ground truth query for this question
                    matching_row = input_df[(input_df['db_id'] == db_id) & 
                                          (input_df['question'] == question)]
                    
                    ground_truth_sql = "N/A"
                    exact_match = False
                    exec_match = False
                    
                    if not matching_row.empty:
                        ground_truth_sql = matching_row['query'].iloc[0]
                        
                        # Skip empty queries
                        if generated_sql and generated_sql != 'No SQL generated' and ground_truth_sql:
                            # Perform exact match evaluation
                            exact_match = SQLMetrics.exact_match(generated_sql, ground_truth_sql)
                            
                            # Get database path
                            db_file_path = SQLMetrics.get_db_path(db_id)
                            
                            # Perform execution match evaluation if DB file exists
                            if os.path.exists(db_file_path):
                                try:
                                    exec_match = SQLMetrics.execution_match(
                                        generated_sql, ground_truth_sql, db_file_path
                                    )
                                except Exception as e:
                                    st.error(f"Error with execution match for query {idx+1}: {e}")
                            else:
                                st.warning(f"Database file not found: {db_file_path}")
                    
                    summary_entry = {
                        "Database ID": db_id,
                        "Question": question,
                        "Generated SQL": generated_sql,
                        "Ground Truth SQL": ground_truth_sql,
                        "Exact Match": exact_match,  # Boolean for calculations
                        "Execution Match": exec_match,  # Boolean for calculations
                        "Best Temperature": best_result.get('temperature', 0.0),
                        "Confidence": best_result.get('confidence', 0),
                        "Iterations": query_result.get('iterations', max_iter),
                        "Intent": query_result.get('intent', 'N/A')
                    }
                    summary_data.append(summary_entry)
                    
                    # Evaluate each model response individually
                    for response in query_result.get("raw_responses", []):
                        model_sql = response.get("response", "")
                        model_exact_match = False
                        model_exec_match = False
                        
                        if model_sql and ground_truth_sql and ground_truth_sql != 'N/A':
                            # Perform exact match evaluation
                            model_exact_match = SQLMetrics.exact_match(model_sql, ground_truth_sql)
                            
                            # Get database path
                            db_file_path = SQLMetrics.get_db_path(db_id)
                            
                            # Perform execution match evaluation if DB file exists
                            if os.path.exists(db_file_path):
                                try:
                                    model_exec_match = SQLMetrics.execution_match(
                                        model_sql, ground_truth_sql, db_file_path
                                    )
                                except Exception as e:
                                    pass  # Silently continue, we'll show errors only for the final result
                        
                        model_results.append({
                            "Database ID": db_id,
                            "Question": question,
                            "Model": response.get("model", "Unknown"),
                            "SQL Response": model_sql,
                            "Exact Match": model_exact_match,
                            "Execution Match": model_exec_match,
                            "Confidence": response.get("confidence", 0),
                            "Latency (s)": response.get("latency", 0),
                            "Iteration": response.get("iteration", 0),
                            "Temperature": response.get("temperature", 0.0)
                        })

                if not summary_data:
                    st.warning("No results returned. Check your CSV format.")
                    st.stop()
                
                # Create summary DataFrame and calculate metrics
                summary_df = pd.DataFrame(summary_data)
                
                # Calculate metrics for the arbiter's final results
                arbiter_metrics = SQLMetrics.compute_metrics(summary_df)
                
                # Create and calculate metrics for individual models
                model_results_df = pd.DataFrame(model_results)
                
                # Group model results by model name and calculate performance
                if not model_results_df.empty:
                    model_performance = {}
                    for model_name, group in model_results_df.groupby("Model"):
                        metrics = SQLMetrics.compute_metrics(group)
                        model_performance[model_name] = metrics
                
                # Display overall metrics for the arbiter
                st.markdown("### Arbiter Results")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Exact Match Rate", f"{arbiter_metrics['exact_match_rate']:.1f}%")
                    st.markdown(f"**Exact Matches:** {arbiter_metrics['exact_match_count']} / {arbiter_metrics['total']}")
                with col2:
                    st.metric("Execution Match Rate", f"{arbiter_metrics['execution_match_rate']:.1f}%")
                    st.markdown(f"**Execution Matches:** {arbiter_metrics['execution_match_count']} / {arbiter_metrics['total']}")

                # Display individual model performance metrics
                if model_results_df.empty:
                    st.warning("No individual model results available")
                else:
                    st.markdown("### Individual Model Performance")
                    
                    # Create performance comparison dataframe
                    model_perf_data = []
                    for model_name, metrics in model_performance.items():
                        model_perf_data.append({
                            "Model": model_name,
                            "Exact Match Rate": f"{metrics['exact_match_rate']:.1f}%",
                            "Execution Match Rate": f"{metrics['execution_match_rate']:.1f}%",
                            "Exact Match Count": f"{metrics['exact_match_count']} / {metrics['total']}",
                            "Execution Match Count": f"{metrics['execution_match_count']} / {metrics['total']}",
                            "Exact Match Rate Value": metrics['exact_match_rate'],  # For sorting
                            "Execution Match Rate Value": metrics['execution_match_rate']  # For sorting
                        })
                    
                    model_perf_df = pd.DataFrame(model_perf_data)
                    
                    # Sort by execution match rate (higher is better)
                    model_perf_df = model_perf_df.sort_values("Execution Match Rate Value", ascending=False)
                    
                    # Remove the value columns used for sorting
                    display_model_perf = model_perf_df.drop(columns=["Exact Match Rate Value", "Execution Match Rate Value"])
                    
                    st.dataframe(
                        display_model_perf,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Create charts to visualize model performance
                    chart_data = pd.DataFrame({
                        "Model": model_perf_df["Model"],
                        "Exact Match Rate": model_perf_df["Exact Match Rate Value"],
                        "Execution Match Rate": model_perf_df["Execution Match Rate Value"]
                    })
                    
                    # Melt the dataframe for easier charting
                    chart_data_melted = pd.melt(
                        chart_data, 
                        id_vars=["Model"], 
                        value_vars=["Exact Match Rate", "Execution Match Rate"],
                        var_name="Metric", 
                        value_name="Rate"
                    )
                    
                    # Create bar chart
                    chart = alt.Chart(chart_data_melted).mark_bar().encode(
                        x=alt.X('Model:N', sort='-y'),
                        y=alt.Y('Rate:Q', title='Rate (%)'),
                        color='Metric:N',
                        tooltip=['Model', 'Metric', 'Rate']
                    ).properties(height=300)
                    
                    st.altair_chart(chart, use_container_width=True)

                # For display, convert boolean values to checkmarks in summary df
                display_df = summary_df.copy()
                display_df["Exact Match"] = display_df["Exact Match"].map({True: "✅", False: "❌"})
                display_df["Execution Match"] = display_df["Execution Match"].map({True: "✅", False: "❌"})

                st.markdown("### Consolidated Arbiter Results")
                st.dataframe(
                    display_df,
                    column_config={
                        "Generated SQL": st.column_config.TextColumn("SQL Query", width="large"),
                        "Ground Truth SQL": st.column_config.TextColumn("Ground Truth", width="large"),
                        "Best Temperature": st.column_config.NumberColumn(format="%.2f"),
                        "Confidence": st.column_config.NumberColumn(format="%.2f"),
                        "Exact Match": st.column_config.TextColumn("Exact Match", width="small"),
                        "Execution Match": st.column_config.TextColumn("Execution Match", width="small")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # For display, convert boolean values to checkmarks in model results df
                display_model_df = model_results_df.copy()
                display_model_df["Exact Match"] = display_model_df["Exact Match"].map({True: "✅", False: "❌"})
                display_model_df["Execution Match"] = display_model_df["Execution Match"].map({True: "✅", False: "❌"})

                st.markdown("### All Model Responses")
                st.dataframe(
                    display_model_df,
                    column_config={
                        "SQL Response": st.column_config.TextColumn("SQL Query", width="large"),
                        "Confidence": st.column_config.NumberColumn(format="%.2f"),
                        "Latency (s)": st.column_config.NumberColumn(format="%.2f"),
                        "Temperature": st.column_config.NumberColumn(format="%.2f"),
                        "Exact Match": st.column_config.TextColumn("Exact Match", width="small"),
                        "Execution Match": st.column_config.TextColumn("Execution Match", width="small")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # Per-query detailed results
                for idx, query_result in enumerate(result):
                    st.markdown(f"### Query {idx+1} Details")
                    
                    best_result = query_result.get('best', {})
                    trials_data = query_result.get('trials', [])
                    
                    db_id = query_result.get('db_id', 'N/A')
                    question = query_result.get('question', 'N/A')
                    generated_sql = best_result.get('final_query', 'No SQL generated')
                    
                    # Find matching ground truth for detailed view
                    matching_row = input_df[(input_df['db_id'] == db_id) & 
                                          (input_df['question'] == question)]
                    
                    ground_truth_sql = "N/A"
                    exact_match = False
                    exec_match = False
                    
                    if not matching_row.empty:
                        ground_truth_sql = matching_row['query'].iloc[0]
                        
                        if generated_sql and generated_sql != 'No SQL generated' and ground_truth_sql:
                            # Use SQLMetrics class for evaluation
                            exact_match = SQLMetrics.exact_match(generated_sql, ground_truth_sql)
                            
                            # Get database path
                            db_file_path = SQLMetrics.get_db_path(db_id)
                            
                            if os.path.exists(db_file_path):
                                try:
                                    exec_match = SQLMetrics.execution_match(
                                        generated_sql, ground_truth_sql, db_file_path
                                    )
                                except Exception as e:
                                    st.error(f"Error with execution match for query {idx+1}: {e}")
                            else:
                                st.warning(f"Database file not found: {db_file_path}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Best Temperature", f"{best_result.get('temperature', 0.0):.2f}")
                    with col2:
                        st.metric("Exact Match", "✅" if exact_match else "❌")
                    with col3:
                        st.metric("Execution Match", "✅" if exec_match else "❌")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Database:** `{db_id}`")
                        st.markdown(f"**Intent:** {query_result.get('intent', 'N/A')}")
                    with col2:
                        st.markdown(f"**Confidence:** {best_result.get('confidence', 0):.2f}")
                        st.markdown(f"**Iterations:** {query_result.get('iterations', max_iter)}")

                    st.markdown("#### Question")
                    st.markdown(f"_{question}_")
                    
                    st.markdown("#### Generated SQL (Best Result)")
                    st.code(generated_sql, language='sql')
                    
                    st.markdown("#### Ground Truth SQL")
                    st.code(ground_truth_sql, language='sql')

                    # Temperature tuning analysis
                    if trials_data:
                        with st.expander("Temperature Tuning Analysis"):
                            trial_df = pd.DataFrame(trials_data)
                            
                            if not trial_df.empty and 'temperature' in trial_df.columns and 'confidence' in trial_df.columns:
                                # Get the best temperature and confidence for highlighting
                                best_temp = best_result.get('temperature')
                                best_conf = best_result.get('confidence')
                                
                                chart = alt.Chart(trial_df).mark_line().encode(
                                    x='temperature:Q',
                                    y='confidence:Q',
                                    tooltip=['temperature', 'confidence'] + 
                                           (['sql'] if 'sql' in trial_df.columns else [])
                                ).properties(title="Temperature vs Confidence", height=300)
                                
                                # Add a marker for the best point if we have the data
                                if best_temp is not None and best_conf is not None:
                                    best_point = alt.Chart(pd.DataFrame([{
                                        'temperature': best_temp,
                                        'confidence': best_conf
                                    }])).mark_circle(color='red', size=100).encode(
                                        x='temperature:Q',
                                        y='confidence:Q'
                                    )
                                    chart = chart + best_point
                                    
                                st.altair_chart(chart, use_container_width=True)
                            else:
                                st.warning("Temperature trial data has incorrect format or is empty")

                    # Model response data for this specific query
                    query_responses_data = []
                    for response in query_result.get("raw_responses", []):
                        model_sql = response.get("response", "")
                        model_exact_match = False
                        model_exec_match = False
                        
                        if model_sql and ground_truth_sql and ground_truth_sql != 'N/A':
                            # Perform exact match evaluation
                            model_exact_match = SQLMetrics.exact_match(model_sql, ground_truth_sql)
                            
                            # Get database path
                            db_file_path = SQLMetrics.get_db_path(db_id)
                            
                            # Perform execution match evaluation if DB file exists
                            if os.path.exists(db_file_path):
                                try:
                                    model_exec_match = SQLMetrics.execution_match(
                                        model_sql, ground_truth_sql, db_file_path
                                    )
                                except Exception as e:
                                    # Silently continue
                                    pass
                        
                        query_responses_data.append({
                            "Model": response.get("model", "Unknown"),
                            "SQL Response": model_sql,
                            "Confidence": response.get("confidence", 0),
                            "Latency (s)": f"{response.get('latency', 0):.2f}",
                            "Temperature": response.get("temperature", 0.0),
                            "Iteration": response.get("iteration", 0),
                            "Exact Match": "✅" if model_exact_match else "❌",
                            "Execution Match": "✅" if model_exec_match else "❌"
                        })

                    if query_responses_data:
                        st.markdown("#### Model Responses")
                        df_responses = pd.DataFrame(query_responses_data)
                        st.dataframe(
                            df_responses,
                            column_config={
                                "SQL Response": st.column_config.TextColumn("SQL", help="Model-generated SQL", width="large"),
                                "Temperature": st.column_config.NumberColumn(format="%.2f"),
                                "Exact Match": st.column_config.TextColumn("Exact Match", width="small"),
                                "Execution Match": st.column_config.TextColumn("Execution Match", width="small")
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                        with st.expander("Performance Analysis"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.altair_chart(alt.Chart(df_responses).mark_bar().encode(
                                    x='Model:N',
                                    y='Confidence:Q',
                                    color='Model:N',
                                    tooltip=['Model', 'Confidence', 'Latency (s)', 'Temperature']
                                ).properties(height=300))
                            with col2:
                                st.altair_chart(alt.Chart(df_responses).mark_circle(size=60).encode(
                                    x='Temperature:Q',
                                    y='Confidence:Q',
                                    color='Model:N',
                                    tooltip=['Model', 'Confidence', 'Latency (s)', 'Temperature']
                                ).properties(height=300))
                    else:
                        st.warning("No model responses recorded for this query")

                # Export data - save both summary and model results
                summary_csv = summary_df.to_csv(index=False).encode('utf-8')
                model_results_csv = model_results_df.to_csv(index=False).encode('utf-8')
                
                download_key_summary = f"spider_summary_{datetime.now().timestamp()}_{uuid.uuid4()}"
                download_key_models = f"spider_models_{datetime.now().timestamp()}_{uuid.uuid4()}"
                
                st.download_button(
                    "⬇️ Download Arbiter Results (CSV)",
                    data=summary_csv,
                    file_name="spider_arbiter_results.csv",
                    mime="text/csv",
                    key=download_key_summary,
                    help="Includes evaluation metrics for arbiter results"
                )
                
                st.download_button(
                    "⬇️ Download Model Results (CSV)",
                    data=model_results_csv,
                    file_name="spider_model_results.csv",
                    mime="text/csv",
                    key=download_key_models,
                    help="Includes evaluation metrics for all model responses"
                )
                
            except Exception as e:
                st.error(f"Error running consortium: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")

def classification_page():
    import streamlit as st
    import matplotlib.pyplot as plt
    from llm_consortium.core.runner_class import ConsortiumRunnerClass
    from llm_consortium.config.models import ConsortiumConfig
    import asyncio
    import json
    import tempfile
    import pandas as pd
    import altair as alt
    import uuid
    from datetime import datetime
    from llm_consortium.utils.pricing import calculate_cost
    
    if 'download_key' not in st.session_state:
        st.session_state.download_key = f"classification_init_{uuid.uuid4()}"

    if 'classification_models' not in st.session_state:
        st.session_state.classification_models = []
        
    st.title("Classification Consortium Tuner")

    runner_class = ConsortiumRunnerClass()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Configuration")
        model_selector = st.selectbox("Select Model", ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini", "claude-3-sonnet"])
        instance_count = st.number_input("Instances", min_value=1, value=1, step=1)
        
        if st.button("Add Model"):
            new_models = {(m, c) for m, c in st.session_state.classification_models if m != model_selector}
            new_models.add((model_selector, instance_count))
            st.session_state.classification_models = list(new_models)
            st.rerun()
        
        if st.session_state.classification_models:
            st.write("### Selected Models")
            for idx, (model, count) in enumerate(st.session_state.classification_models):
                cols = st.columns([4, 2, 1])
                with cols[0]:
                    st.markdown(f"**{model}**")
                with cols[1]:
                    st.markdown(f"Instances: {count}")
                with cols[2]:
                    if st.button("❌", key=f"delete_class_{idx}"):
                        st.session_state.classification_models.remove((model, count))
                        st.rerun()
        else:
            st.info("No models added yet")
        
        st.subheader("Arbiter Tuning")
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.1)
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.9)
        num_trials = st.number_input("Temperature Trials", 1, 20, 5)
        if min_temp >= max_temp:
            st.error("Max temperature must be greater than min temperature")
        
        arbiter = st.selectbox("Arbiter Model", ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo", "claude-3-sonnet"], index=2)
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
        max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
        min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)

    with col2:
        st.subheader("Execution")
        uploaded_file = st.file_uploader(
            "Upload CSV with questions and optional class labels",
            type=["csv"],
            help="CSV must contain 'question' column and optionally 'class', 'label', or 'category' column"
        )
        
        if uploaded_file is not None and st.session_state.classification_models:
            models_dict = {model: count for model, count in st.session_state.classification_models}
            total_cost, cost_df = calculate_cost(
                [(m, c) for m, c in models_dict.items()] + [(arbiter, 1)], 
                max_iter
            )
            st.write(f"**Estimated Cost:** ${total_cost:.4f}")
            st.dataframe(cost_df, use_container_width=True)
        elif uploaded_file:
            st.info("Add models to see cost estimation")

        if st.button("Run Classification Consortium", type="primary"):
            if not st.session_state.classification_models:
                st.error("Please add at least one model")
                st.stop()
            if not uploaded_file:
                st.error("Please upload a CSV file first")
                st.stop()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                csv_path = tmp_file.name
                
            # Create output path
            output_path = f"classification_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            
            models_dict = {model: count for model, count in st.session_state.classification_models}
            
            config = ConsortiumConfig(
                models=models_dict,
                arbiter=arbiter,
                confidence_threshold=confidence,
                max_iterations=int(max_iter),
                min_iterations=int(min_iter),
                min_temp=min_temp,
                max_temp=max_temp,
                num_trials=num_trials
            )
            
            try:
                with st.spinner("Running classification consortium..."):
                    result = asyncio.run(runner_class.run_consortium(config, csv_path, output_path))
                
                st.subheader("Classification Results")
                has_true_classes = result.get("has_true_classes", False)
                
                # Process results for display
                summary_data = []
                for query_result in result.get("results", []):
                    best_result = query_result.get('best', {})
                    summary_entry = {
                        "Question": query_result.get('question', 'N/A'),
                        "Predicted Class": best_result.get('final_class', 'UNKNOWN'),
                        "Confidence": best_result.get('confidence', 0),
                        "Best Temperature": best_result.get('temperature', 0.0),
                        "Iterations": query_result.get('iterations', max_iter),
                        "Model Count": sum(count for _, count in models_dict.items())
                    }
                    
                    if has_true_classes:
                        summary_entry["True Class"] = query_result.get('true_class', '')
                        summary_entry["Is Correct"] = summary_entry["Predicted Class"] == summary_entry["True Class"]
                    
                    summary_data.append(summary_entry)

                if not summary_data:
                    st.warning("No results returned. Check your CSV format.")
                    st.stop()
                
                summary_df = pd.DataFrame(summary_data)

                # Display metrics if available
                if "metrics" in result and result["metrics"]:
                    metrics = result["metrics"]["arbiter"]

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
                    with col2:
                        st.metric("F1", f"{metrics.get('f1', 0):.4f}")
                    with col3:
                        st.metric("Recall", f"{metrics.get('recall', 0):.4f}")
                    
                    # Add confusion matrix if available
                    if "confusion_matrix" in metrics:
                        with st.expander("Confusion Matrix"):
                            confusion_matrix = metrics["confusion_matrix"]
                            st.dataframe(confusion_matrix)
                
                # Show main results table
                st.markdown("### Consolidated Results")
                st.dataframe(
                    summary_df,
                    column_config={
                        "Question": st.column_config.TextColumn("Question", width="large"),
                        "Predicted Class": st.column_config.TextColumn("Predicted Class", width="medium"),
                        "Confidence": st.column_config.NumberColumn(format="%.2f"),
                        "Best Temperature": st.column_config.NumberColumn(format="%.2f"),
                        "Is Correct": st.column_config.CheckboxColumn("Is Correct") if has_true_classes else None
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # Display individual results
                for idx, query_result in enumerate(result.get("results", [])):
                    with st.expander(f"Question {idx+1} Details"):
                        best_result = query_result.get('best', {})
                        trials_data = query_result.get('trials', [])
                        
                        st.markdown(f"**Question:** {query_result.get('question', 'N/A')}")
                        
                        if has_true_classes:
                            true_class = query_result.get('true_class', '')
                            st.markdown(f"**True Class:** {true_class}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Predicted Class", best_result.get('final_class', 'UNKNOWN'))
                        with col2:
                            st.metric("Confidence", f"{best_result.get('confidence', 0):.2f}")
                        with col3:
                            st.metric("Best Temperature", f"{best_result.get('temperature', 0.0):.2f}")
                        
                        st.markdown("#### Reasoning")
                        st.write(best_result.get('reasoning', 'No reasoning provided'))
                        
                        # Show temperature trials visualization
                        if trials_data:
                            st.markdown("#### Temperature Tuning Analysis")
                            trial_df = pd.DataFrame(trials_data)
                            
                            if not trial_df.empty and 'temperature' in trial_df.columns and 'confidence' in trial_df.columns:
                                # Get the best temperature and confidence for highlighting
                                best_temp = best_result.get('temperature')
                                best_conf = best_result.get('confidence')
                                
                                if 'final_class' in trial_df.columns:
                                    trial_df = trial_df.dropna(subset=['final_class'])
                                    trial_df['final_class'] = trial_df['final_class'].astype(str)
                                    tooltip_fields = ['temperature', 'confidence', 'final_class']
                                else:
                                    tooltip_fields = ['temperature', 'confidence']

                                chart = alt.Chart(trial_df).mark_line().encode(
                                    x=alt.X('temperature:Q', title='Temperature'),
                                    y=alt.Y('confidence:Q', title='Confidence'),
                                    tooltip=tooltip_fields
                                ).properties(title="Temperature vs Confidence", height=300)
                                
                                # Add a marker for the best point
                                if best_temp is not None and best_conf is not None:
                                    best_point = alt.Chart(pd.DataFrame([{
                                        'temperature': best_temp,
                                        'confidence': best_conf
                                    }])).mark_circle(color='red', size=100).encode(
                                        x='temperature:Q',
                                        y='confidence:Q'
                                    )
                                    chart = chart + best_point
                                    
                                st.altair_chart(chart, use_container_width=True)
                        
                        # Show individual model responses
                        responses_data = []
                        for response in query_result.get("raw_responses", []):
                            responses_data.append({
                                "Model": response.get("model", "Unknown"),
                                "Predicted Class": response.get("predicted_class", "UNKNOWN"),
                                "Confidence": response.get("confidence", 0),
                                "Latency (s)": f"{response.get('latency', 0):.2f}",
                                "Iteration": response.get("iteration", 0)
                            })

                        if responses_data:
                            st.markdown("#### Model Responses")
                            df_responses = pd.DataFrame(responses_data)
                            st.dataframe(
                                df_responses,
                                column_config={
                                    "Predicted Class": st.column_config.TextColumn("Predicted Class", width="medium"),
                                    "Confidence": st.column_config.NumberColumn(format="%.2f"),
                                },
                                use_container_width=True,
                                hide_index=True
                            )

                            # Show model performance charts
                            col1, col2 = st.columns(2)
                            with col1:
                                st.altair_chart(alt.Chart(df_responses).mark_bar().encode(
                                    x='Model:N',
                                    y='Confidence:Q',
                                    color='Model:N',
                                    tooltip=['Model', 'Confidence', 'Latency (s)']
                                ).properties(height=300))
                            with col2:
                                st.altair_chart(alt.Chart(df_responses).mark_circle(size=60).encode(
                                    x='Latency (s):Q',
                                    y='Confidence:Q',
                                    color='Model:N',
                                    tooltip=['Model', 'Confidence', 'Latency (s)']
                                ).properties(height=300))

                # Provide download button for results
                csv_data = summary_df.to_csv(index=False).encode('utf-8')
                download_key = f"classification_download_{datetime.now().timestamp()}_{uuid.uuid4()}"
                st.download_button(
                    "⬇️ Download Classification Results (CSV)",
                    data=csv_data,
                    file_name="classification_consortium_results.csv",
                    mime="text/csv",
                    key=download_key,
                    help="Download consolidated classification results"
                )
                
            except Exception as e:
                st.error(f"Error running classification consortium: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")

def classification_ui():
    import os
    import matplotlib.pyplot as plt
    import streamlit as st
    from llm_consortium.core.classification.classification_model_runner import ClassificationModelRunner
    from llm_consortium.core.classification.classification_judge import ClassificationJudge 
    from llm_consortium.config.models_classification import ModelConfig
    import asyncio
    import json
    import pandas as pd
    import altair as alt
    from llm_consortium.utils.logging import logger
    from datetime import datetime
    from llm_consortium.core.client_init import llm
    from sklearn.metrics import confusion_matrix
    import numpy as np
    import seaborn as sns
    from llm_consortium.utils.pricing import calculate_cost
    try:
        from deepeval.metrics import HallucinationMetric, ContextualRelevanceMetric, FactualConsistencyMetric
        DEEPEVAL_AVAILABLE = True
    except ImportError:
        DEEPEVAL_AVAILABLE = False
    import nest_asyncio
    nest_asyncio.apply()
    # Initialize runner and judge
    runner = ClassificationModelRunner()
    judge = ClassificationJudge(llm)
    
    

    # Title and description
    st.title("Classification Model Evaluation and Tuning")
    st.markdown("""
    This tool evaluates different LLM models for classification tasks and tunes parameters for the best performer.
    Upload your test dataset, select models to evaluate, and configure evaluation parameters.
    """)

    # Initialize session state for storing results between reruns
    if 'classification_evaluation_results' not in st.session_state:
        st.session_state.classification_evaluation_results = None
    if 'classification_best_model' not in st.session_state:
        st.session_state.classification_best_model = None
    if 'classification_best_params' not in st.session_state:
        st.session_state.classification_best_params = None
    if 'classification_tuning_results' not in st.session_state:
        st.session_state.classification_tuning_results = None
    if 'classification_running' not in st.session_state:
        st.session_state.classification_running = False
    if 'classification_progress' not in st.session_state:
        st.session_state.classification_progress = 0
    if 'classification_judge_results' not in st.session_state:
        st.session_state.classification_judge_results = None
    if 'classification_judge_running' not in st.session_state:
        st.session_state.classification_judge_running = False
    if 'classification_tuning_comparison' not in st.session_state:
        st.session_state.classification_tuning_comparison = None
    if 'classification_sampled_dataset' not in st.session_state:
        st.session_state.classification_sampled_dataset = None
    if 'classification_tuning_trials' not in st.session_state:
        st.session_state.classification_tuning_trials = None
    if 'classification_valid_classes' not in st.session_state:
        st.session_state.classification_valid_classes = None
    if 'classification_error_details' not in st.session_state:
        st.session_state.classification_error_details = None

    def reset_results():
        st.session_state.classification_evaluation_results = None
        st.session_state.classification_best_model = None
        st.session_state.classification_best_params = None
        st.session_state.classification_tuning_results = None
        st.session_state.classification_running = False
        st.session_state.classification_progress = 0
        st.session_state.classification_judge_results = None
        st.session_state.classification_judge_running = False
        st.session_state.classification_tuning_comparison = None
        st.session_state.classification_sampled_dataset = None
        st.session_state.classification_tuning_trials = None
        st.session_state.classification_error_details = None

    # Layout with two columns - config panel and results
    col1, col2 = st.columns([1, 3])

    # Configuration panel
    with col1:
        st.header("Configuration")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Test Dataset (CSV)", type=["csv"], key="classification_csv_upload")
        
        # Add dataset sampling option
        if uploaded_file is not None:
            # Read the uploaded file to get the number of rows
            df = pd.read_csv(uploaded_file)
            total_rows = len(df)
            
            # Extract valid classes from the dataset
            if 'ground_truth' in df.columns:
                valid_classes = df['ground_truth'].unique().tolist()
                st.session_state.classification_valid_classes = valid_classes
                st.write(f"**Detected Classes:** {', '.join(valid_classes)}")
            else:
                st.error("CSV must contain a 'ground_truth' column")
            
            # Check if 'question' column exists - this is required for classification
            if 'question' not in df.columns:
                st.error("CSV must contain a 'question' column")
                
            st.subheader("Dataset Sampling")
            enable_sampling = st.checkbox("Enable Dataset Sampling", value=False, key="classification_enable_sampling")
            
            if enable_sampling:
                sample_size = st.slider(
                    "Sample Size", 
                    min_value=min(10, total_rows),
                    max_value=total_rows,
                    value=min(50, total_rows),
                    step=10,
                    help=f"Select number of samples to use from your dataset of {total_rows} records"
                )
                
                # Display percentage of total
                st.caption(f"Selected {sample_size} samples ({(sample_size/total_rows*100):.1f}% of total)")
            else:
                # If sampling is not enabled, use all rows
                sample_size = total_rows
            
            # Reset file position to beginning for later use
            uploaded_file.seek(0)
        
        # Model selection (with default models)
        default_models = ["gpt-4o-mini", "gpt-3.5-turbo"]
        available_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        selected_models = st.multiselect(
            "Select Models to Evaluate", 
            available_models,
            default=default_models,
            key="classification_models"
        )
        
        # Judge model selection
        judge_models = ["gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"] 
        selected_judge = st.selectbox(
            "LLM Judge Model",
            judge_models,
            index=0,
            key="classification_judge_model"
        )
        
        # Base configuration
        st.subheader("Base Settings")
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.2, 0.05, key="classification_base_temp")
        
        # Debug Mode
        debug_mode = st.checkbox("Debug Mode", value=False, key="classification_debug_mode",
                               help="Show additional debugging information")
        
        # Tuning settings
        st.subheader("Parameter Tuning")
        enable_tuning = st.checkbox("Enable Parameter Tuning", value=True, key="classification_enable_tuning")
        
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.0, 0.05, key="classification_min_temp")
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.8, 0.05, key="classification_max_temp")
        num_trials = st.slider("Number of Trials", 3, 10, 5, key="classification_num_trials")
        
        # Judge settings
        st.subheader("Judge Settings")
        judge_criteria = st.multiselect(
            "Judge Criteria",
            options=[
                "Understanding of concepts",
                "Reasoning quality",
                "Classification consistency",
                "Confidence accuracy",
                "Edge case handling",
                "Explanation quality"
            ],
            default=[
                "Understanding of concepts",
                "Reasoning quality",
                "Classification consistency",
                "Confidence accuracy"
            ],
            
        )
        
        # Output settings
        st.subheader("Output Settings")
        output_dir = st.text_input("Output Directory", "results", key="classification_output_dir")
        save_results = st.checkbox("Save Results to File", value=True, key="classification_save_results")
        
        # Run button
        run_button = st.button("Run Evaluation", type="primary", key="classification_run_button", 
                            disabled=len(selected_models) == 0 or uploaded_file is None)

    # Main content area in the second column
    with col2:
        # Show debug information if enabled
        if debug_mode and st.session_state.classification_error_details:
            st.error("Error Details:")
            st.code(st.session_state.classification_error_details, language="text")
        
        async def run_evaluation_async(config, csv_path, sampled_csv_path=None, valid_classes=None, debug_mode=False):
            """Run the evaluation and tuning pipeline asynchronously"""
            try:
                # Step 1: Evaluate all models
                st.session_state.classification_progress = 10
                evaluation_progress.progress(st.session_state.classification_progress/100, "Evaluating models...")
                
                # Use the sampled dataset if available
                eval_csv_path = sampled_csv_path if sampled_csv_path else csv_path
                
                # Make sure CSV has required columns
                df = pd.read_csv(eval_csv_path)
                if 'question' not in df.columns:
                    raise ValueError("CSV must contain a 'question' column")
                if 'ground_truth' not in df.columns:
                    raise ValueError("CSV must contain a 'ground_truth' column")
                
                # Run evaluation
                evaluation_results = await runner.evaluate_models(config, eval_csv_path, valid_classes)
                st.session_state.classification_evaluation_results = evaluation_results
                st.session_state.classification_progress = 50
                evaluation_progress.progress(st.session_state.classification_progress/100, "Evaluation complete, processing results...")
                
                # Step 2: Find the best model
                best_model = runner.find_best_model(evaluation_results)
                st.session_state.classification_best_model = best_model
                st.session_state.classification_progress = 60
                evaluation_progress.progress(st.session_state.classification_progress/100, f"Best model identified: {best_model}")
                
                # Step 3: Tune the best model if enabled
                if config.enable_tuning:
                    evaluation_progress.progress(st.session_state.classification_progress/100, f"Tuning {best_model}...")
                    
                    best_params = await runner.tune_best_model(
                        best_model,
                        eval_csv_path,
                        config,
                        valid_classes
                    )
                    st.session_state.classification_best_params = best_params
                    
                    # Track tuning trials if available from the tuner
                    if hasattr(runner.hyperparameter_tuner, 'trial_results'):
                        st.session_state.classification_tuning_trials = runner.hyperparameter_tuner.trial_results
                        
                    st.session_state.classification_progress = 80
                    evaluation_progress.progress(st.session_state.classification_progress/100, "Tuning complete")
                
                    # Step 4: Optionally evaluate with tuned parameters
                    if config.run_final_evaluation:
                        evaluation_progress.progress(st.session_state.classification_progress/100, f"Final evaluation with tuned parameters...")
                        final_results = await runner.evaluate_with_params(
                            best_model, 
                            best_params, 
                            eval_csv_path,
                            valid_classes
                        )
                        st.session_state.classification_tuning_results = final_results
                        
                # Save results if requested
                if save_results:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"classification_eval_results_{timestamp}.json")
                    
                    # Create metrics summary for all models
                    model_metrics = {}
                    for model_name, results in evaluation_results.items():
                        model_metrics[model_name] = results["metrics"]
                    
                    with open(output_file, "w") as f:
                        json.dump({
                            "model_evaluations": evaluation_results,
                            "best_model": best_model,
                            "best_params": best_params if config.enable_tuning else None,
                            "model_metrics": model_metrics,
                            "sample_size": sample_size if 'sample_size' in locals() else "full dataset",
                            "valid_classes": valid_classes
                        }, f, indent=2, default=str)
                        
                st.session_state.classification_progress = 100
                evaluation_progress.progress(st.session_state.classification_progress/100, "Complete!")
                return model_metrics
                
            except Exception as e:
                error_msg = f"Error during evaluation: {str(e)}"
                if debug_mode:
                    import traceback
                    error_details = traceback.format_exc()
                    st.session_state.classification_error_details = error_details
                    logger.error(f"Evaluation error details: {error_details}")
                st.error(error_msg)
                logger.error(f"Evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.classification_running = False
        
        # Function for evaluating using the judge
        async def run_judge_evaluation_async(judge_criteria):
            """Run the judge evaluation asynchronously"""
            try:
                # Ensure criteria is always a list of strings
                if isinstance(judge_criteria, str):
                    judge_criteria = [judge_criteria]
                    
                if not isinstance(judge_criteria, list):
                    raise ValueError("Judge criteria must be a list")
                    
                # Validate each criterion is a string
                judge_criteria = [str(c) for c in judge_criteria]
                
                # Pass to judge
                judge_results = await judge.evaluate_model_outputs(
                    st.session_state.classification_evaluation_results,
                    criteria=judge_criteria,
                    class_labels=st.session_state.classification_valid_classes  # Add this line
                )
            # try:
            #     if not st.session_state.classification_evaluation_results:
            #         st.error("No evaluation results available to judge")
            #         return None
                
            #     # Evaluate all models using judge
            #     judge_results = await judge.evaluate_model_outputs(
            #         st.session_state.classification_evaluation_results,
            #         criteria=judge_criteria
            #     )
                
                # Store results
                st.session_state.classification_judge_results = judge_results
                
                # If we have before/after tuning results, compare those too
                if st.session_state.classification_best_model and st.session_state.classification_tuning_results:
                    best_model = st.session_state.classification_best_model
                    before_data = st.session_state.classification_evaluation_results[best_model]
                    after_data = st.session_state.classification_tuning_results
                    
                    tuning_comparison = await judge.before_after_tuning_comparison(
                        best_model,
                        before_data,
                        after_data
                    )
                    
                    st.session_state.classification_tuning_comparison = tuning_comparison
                
                return judge_results
                
            except Exception as e:
                st.error(f"Error during judge evaluation: {str(e)}")
                logger.error(f"Judge evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.classification_judge_running = False
        
        if run_button and not st.session_state.classification_running:
            sampled_csv_path = None
            
            # Create sampled dataset if sampling is enabled
            if st.session_state.get('classification_enable_sampling', False) and uploaded_file is not None:
                # Read the full dataset
                df = pd.read_csv(uploaded_file)
                total_rows = len(df)
                
                # Check if sampling is actually needed
                if sample_size < total_rows:
                    # Sample the dataset
                    sampled_df = df.sample(n=sample_size, random_state=42)
                    
                    # Save the sampled dataset to a temporary file
                    sampled_csv_path = "temp_sampled_classification_dataset.csv"
                    sampled_df.to_csv(sampled_csv_path, index=False)
                    st.session_state.classification_sampled_dataset = sampled_csv_path
                    
                    # Display info about sampling
                    st.info(f"Using {sample_size} samples out of {total_rows} records ({(sample_size/total_rows*100):.1f}%)")
            
            # Create config
            config = ModelConfig(
                models=selected_models,
                base_temperature=base_temperature,
                enable_tuning=enable_tuning,
                min_temp=min_temp,
                max_temp=max_temp,
                num_trials=num_trials,
                run_final_evaluation=True
            )
            
            # Save uploaded file temporarily
            temp_csv = "temp_classification_dataset.csv"
            with open(temp_csv, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Reset previous results
            reset_results()
            
            # Show progress bar
            evaluation_progress = st.progress(0, "Starting evaluation...")
            st.session_state.classification_running = True
            
            # Synchronous wrapper for the async evaluation function
            def run_evaluation(config, csv_path, sampled_csv_path, valid_classes, debug_mode):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(run_evaluation_async(config, csv_path, sampled_csv_path, valid_classes, debug_mode))
                finally:
                    loop.close()
            
            # Run the evaluation in the current thread (this will block the UI until complete)
            run_evaluation(config, temp_csv, sampled_csv_path, st.session_state.classification_valid_classes, debug_mode)
        
        # Display tabs for results
        if st.session_state.classification_running or st.session_state.classification_evaluation_results:
            tabs = st.tabs(["Evaluation Results", "Model Comparison", "Best Model", "Best Parameters", "Sample Examples", "LLM Judge", "Confusion Matrix", "DeepEval Metrics", "Cost Estimation"])
            # Add this new tab section
            with tabs[7]:  # DeepEval Metrics tab
                if st.session_state.classification_evaluation_results:
                    st.header("DeepEval Advanced Metrics")
                    
                    if not DEEPEVAL_AVAILABLE:
                        st.warning("DeepEval not installed. Some metrics unavailable. Install with `pip install deepeval`")
                    
                    # Select model to view details
                    model_names = list(st.session_state.classification_evaluation_results.keys())
                    selected_model = st.selectbox("Select Model", model_names, key="deepeval_model_select")
                    
                    model_results = st.session_state.classification_evaluation_results[selected_model]
                    deepeval_metrics = model_results.get("metrics", {}).get("advanced_metrics", {})
                    
                    if deepeval_metrics:
                        # Create columns for key metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Hallucination Rate", 
                                    f"{deepeval_metrics.get('hallucination_rate', 0)*100:.1f}%",
                                    help="Percentage of predictions outside valid classes")
                            
                        with col2:
                            st.metric("Contextual Relevance", 
                                    f"{deepeval_metrics.get('semantic_similarity', {}).get('deepeval_relevance_score', 0)*100:.1f}%",
                                    help="DeepEval's contextual relevance score")
                            
                        with col3:
                            st.metric("Factual Consistency", 
                                    f"{deepeval_metrics.get('factual_consistency', {}).get('factual_consistency_score', 0)*100:.1f}%",
                                    help="DeepEval's factual consistency score")
                        
                        # Detailed sections
                        st.subheader("Detailed Metrics")
                        
                        # Hallucination details
                        with st.expander("Hallucination Analysis"):
                            if deepeval_metrics.get("hallucination_metrics"):
                                cols = st.columns([1, 2])
                                with cols[0]:
                                    st.write("**Basic Statistics**")
                                    st.metric("Total Hallucinations", 
                                            deepeval_metrics["hallucination_metrics"].get("total_hallucinations", 0))
                                    st.metric("DeepEval Score" if DEEPEVAL_AVAILABLE else "Basic Hallucination Rate",
                                            f"{deepeval_metrics['hallucination_metrics'].get('deepeval_hallucination_score', deepeval_metrics['hallucination_metrics'].get('hallucination_rate', 0))*100:.1f}%")
                                
                                with cols[1]:
                                    if deepeval_metrics["hallucination_metrics"].get("examples"):
                                        st.write("**Example Hallucinations**")
                                        for example in deepeval_metrics["hallucination_metrics"]["examples"][:3]:
                                            st.write(f"**Q:** {example['question'][:50]}...")
                                            st.write(f"**GT:** {example['ground_truth']} → **Pred:** {example['predicted_class']}")
                        
                        # Semantic similarity details
                        with st.expander("Semantic Similarity"):
                            if deepeval_metrics.get("semantic_similarity"):
                                st.write("**Similarity Distribution**")
                                similarity_data = deepeval_metrics["semantic_similarity"].get("similarity_distribution", {})
                                
                                cols = st.columns(4)
                                cols[0].metric("Minimum", f"{similarity_data.get('min', 0):.2f}")
                                cols[1].metric("25th %ile", f"{similarity_data.get('q1', 0):.2f}")
                                cols[2].metric("Median", f"{similarity_data.get('median', 0):.2f}")
                                cols[3].metric("75th %ile", f"{similarity_data.get('q3', 0):.2f}")
                                
                                if DEEPEVAL_AVAILABLE:
                                    st.write("**DeepEval Contextual Relevance**")
                                    st.write(f"Score: {deepeval_metrics['semantic_similarity'].get('deepeval_relevance_score', 0)*100:.1f}%")
                                    st.write(f"Threshold: {deepeval_metrics['semantic_similarity'].get('deepeval_threshold', 0)*100:.1f}%")
                                    st.write(f"Passed: {'✅' if deepeval_metrics['semantic_similarity'].get('deepeval_passed', False) else '❌'}")
                        
                        # Factual consistency details
                        with st.expander("Factual Consistency"):
                            if deepeval_metrics.get("factual_consistency"):
                                st.write("**DeepEval Factual Consistency**")
                                st.metric("Score", 
                                        f"{deepeval_metrics['factual_consistency'].get('factual_consistency_score', 0)*100:.1f}%")
                                st.metric("Threshold", 
                                        f"{deepeval_metrics['factual_consistency'].get('deepeval_threshold', 0)*100:.1f}%")
                                st.write(f"Passed: {'✅' if deepeval_metrics['factual_consistency'].get('deepeval_passed', False) else '❌'}")
                                
                    else:
                        st.info("DeepEval metrics not available for this model")
                else:
                    st.info("Run evaluation to see DeepEval metrics")
            # Tab 1: Evaluation Results Table
            with tabs[0]:
                if st.session_state.classification_evaluation_results:
                    st.header("Model Evaluation Results")
                    
                    # Display sampling information if dataset was sampled
                    if st.session_state.classification_sampled_dataset:
                        st.info(f"Results based on sampled dataset ({sample_size} records)")
                    
                    # Add LLM Judge button
                    judge_col1, judge_col2 = st.columns([1, 3])
                    with judge_col1:
                        judge_button = st.button(
                            "Evaluate Using LLM Judge", 
                            type="primary", 
                            key="classification_judge_button",
                            disabled=st.session_state.classification_judge_running
                        )
                    
                    if judge_button and not st.session_state.classification_judge_running:
                        st.session_state.classification_judge_running = True
                        
                        # Run judge evaluation
                        def run_judge():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
                            finally:
                                loop.close()
                        
                        # Show a spinner during evaluation
                        with st.spinner("LLM Judge evaluating models..."):
                            run_judge()
                        
                        # Show completion message
                        st.success("LLM Judge evaluation complete! See the 'LLM Judge' tab for results.")
                    
                    # Create a DataFrame for metrics
                    metrics_data = []
                    
                    for model_name, eval_data in st.session_state.classification_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        responses = eval_data["responses"]
                        
                        # Calculate average latency
                        latencies = [r.get("latency", 0) for r in responses]
                        avg_latency = sum(latencies) / len(latencies) if latencies else 0
                        
                        metrics_data.append({
                            "Model": model_name,
                            "Accuracy (%)": round(metrics.get("accuracy", 0) * 100, 2),
                            "Precision (%)": round(metrics.get("precision", 0) * 100, 2),
                            "Recall (%)": round(metrics.get("recall", 0) * 100, 2),
                            "F1 Score": round(metrics.get("f1", 0), 2),
                            "Hallucination (%)": round(eval_data.get("hallucination_metrics", {}).get("hallucination_rate", 0)*100, 1),
                            "Contextual Relevance (%)": round(eval_data.get("semantic_similarity", {}).get("deepeval_relevance_score", 0)*100, 1),
                            "Factual Consistency (%)": round(eval_data.get("factual_consistency", {}).get("factual_consistency_score", 0)*100, 1),
                            "Avg. Latency (s)": round(avg_latency, 3),
                            "Samples": len(responses)

                        })
                    
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    if st.session_state.classification_best_model:
                        st.success(f"Best model: {st.session_state.classification_best_model}")
                else:
                    st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
            with tabs[8]:  # Cost Estimation tab
                if st.session_state.classification_evaluation_results:
                    st.header("Cost Estimation")
                    
                    # Display sampling information if dataset was sampled
                    if st.session_state.get('classification_sampled_dataset'):
                        st.info(f"Cost estimates based on sampled dataset ({sample_size} records)")
                    
                    # Import pricing module
                    
                    
                    # Get the number of records from the uploaded CSV file
                    if uploaded_file is not None:
                        # Reset the file position to the beginning
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file)
                        total_records = len(df)
                        
                        # Display the total number of records
                        st.write(f"**Total Records in Dataset:** {total_records}")
                        
                        # Get the actual number of records used (sampled or full)
                        records_used = sample_size if st.session_state.get('classification_enable_sampling', False) else total_records
                        st.write(f"**Records Used for Evaluation:** {records_used}")
                        
                        # Get the models being used
                        if selected_models:
                            # Prepare model data for cost calculation
                            model_instances = [(model, 1) for model in selected_models]
                            
                            # Add judge model if used
                            if selected_judge and judge_criteria:
                                model_instances.append((selected_judge, 1))
                            
                            # Calculate cost
                            total_cost, cost_breakdown = calculate_cost(model_instances, records_used)
                            
                            # Display cost breakdown
                            st.subheader("Cost Breakdown")
                            st.dataframe(cost_breakdown, use_container_width=True)
                            
                            # Display total cost with formatted currency
                            st.metric("Total Estimated Cost", f"${total_cost:.2f}")
                            
                            # Add cost per record
                            if records_used > 0:
                                cost_per_record = total_cost / records_used
                                st.metric("Cost Per Record", f"${cost_per_record:.4f}")
                            
                            # Add information about the estimation approach
                            with st.expander("Cost Estimation Details"):
                                st.write("""
                                **How costs are estimated:**
                                - Input tokens: Average of 500 tokens per request
                                - Output tokens: Average of 300 tokens per response
                                - Costs are calculated based on current model pricing
                                
                                **Factors affecting actual costs:**
                                - Actual token usage may vary based on prompt length and complexity
                                - Response length variation
                                - Additional API calls for tuning and judge evaluation
                                """)
                                
                                # Display pricing table
                                st.subheader("Model Pricing (per 1K tokens)")
                                pricing_data = []
                                for model, prices in MODEL_PRICING.items():
                                    pricing_data.append({
                                        "Model": model,
                                        "Input Cost": f"${prices['input']:.5f}",
                                        "Output Cost": f"${prices['output']:.5f}"
                                    })
                                st.dataframe(pd.DataFrame(pricing_data))
                        else:
                            st.warning("No models selected. Please select models for evaluation.")
                    else:
                        st.warning("Please upload a CSV file to estimate costs.")
                else:
                    st.info("Run evaluation to see cost estimation.")                
            # Tab 2: Model Comparison Charts
            with tabs[1]:
                if st.session_state.classification_evaluation_results:
                    st.header("Model Comparison")

                    # Prepare data for visualization
                    models = []
                    accuracy = []
                    f1_scores = []
                    precision_scores = []
                    recall_scores = []
                    latencies = []

                    for model_name, eval_data in st.session_state.classification_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        responses = eval_data["responses"]

                        # Calculate average latency
                        avg_latency = sum([r.get("latency", 0) for r in responses]) / len(responses) if responses else 0

                        models.append(model_name)
                        accuracy.append(metrics.get("accuracy", 0) * 100)
                        precision_scores.append(metrics.get("precision", 0) * 100)
                        recall_scores.append(metrics.get("recall", 0) * 100)
                        f1_scores.append(metrics.get("f1", 0) * 100)
                        latencies.append(avg_latency)

                    # Create performance chart
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

                    metrics_to_plot = [accuracy, precision_scores, recall_scores, f1_scores]
                    metrics_labels = ['Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F1 Score (%)']
                    width = 0.2
                    x = range(len(models))

                    # Plot bars for each metric
                    for i, (metric, label) in enumerate(zip(metrics_to_plot, metrics_labels)):
                        ax1.bar([pos + width*(i-1.5) for pos in x], metric, width, label=label)

                    ax1.set_xticks(x)
                    ax1.set_xticklabels(models, rotation=45, ha='right')
                    ax1.set_ylabel('Performance (%)')
                    ax1.set_title('Model Performance Metrics')
                    ax1.legend()
                    ax1.grid(True, linestyle='--', alpha=0.7)

                    # Latency chart
                    if len(models) > 0:
                        ax2.bar(models, latencies, color='orange')
                        ax2.set_xticks(range(len(models)))
                        ax2.set_xticklabels(models, rotation=45, ha='right')
                        ax2.set_ylabel('Average Latency (s)')
                        ax2.set_title('Model Latency')
                        ax2.grid(True, linestyle='--', alpha=0.7)

                    plt.tight_layout()
                    st.pyplot(fig)

                    # Add interactive Altair chart for comparing metrics across models
                    st.subheader("Interactive Metrics Comparison")

                    # Prepare data for Altair
                    chart_data = []
                    for i, model in enumerate(models):
                        chart_data.extend([
                            {"Model": model, "Metric": "Accuracy", "Value": accuracy[i]},
                            {"Model": model, "Metric": "Precision", "Value": precision_scores[i]},
                            {"Model": model, "Metric": "Recall", "Value": recall_scores[i]},
                            {"Model": model, "Metric": "F1 Score", "Value": f1_scores[i]}
                        ])

                    chart_df = pd.DataFrame(chart_data)

                    # Create interactive chart
                    chart = alt.Chart(chart_df).mark_bar().encode(
                        x=alt.X('Model:N', title='Model'),
                        y=alt.Y('Value:Q', title='Performance (%)'),
                        color='Metric:N',
                        tooltip=['Model', 'Metric', 'Value']
                    ).properties(
                        width=600,
                        height=400
                    ).interactive()

                    st.altair_chart(chart, use_container_width=True)

                    # DeepEval Metrics Comparison
                    st.subheader("DeepEval Metrics Comparison")

                    deepeval_metrics = ["Hallucination (%)", "Contextual Relevance (%)", "Factual Consistency (%)"]
                    deepeval_data = metrics_df[["Model"] + deepeval_metrics].melt(
                        id_vars="Model", var_name="Metric", value_name="Score"
                    )

                    chart = alt.Chart(deepeval_data).mark_bar().encode(
                        x=alt.X('Model:N', title='Model'),
                        y=alt.Y('Score:Q', title='Score (%)'),
                        color='Metric:N',
                        column=alt.Column('Metric:N', header=alt.Header(title=""))
                    )

                    st.altair_chart(chart, use_container_width=True)

                else:
                    st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")

                
            # Tab 3: Best Model Details
            with tabs[2]:
                if st.session_state.classification_best_model:
                    best_model = st.session_state.classification_best_model
                    st.header(f"Best Model: {best_model}")
                    
                    best_model_data = st.session_state.classification_evaluation_results[best_model]
                    metrics = best_model_data["metrics"]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Accuracy", f"{metrics.get('accuracy', 0)*100:.2f}%")
                    col2.metric("Precision", f"{metrics.get('precision', 0)*100:.2f}%")
                    col3.metric("Recall", f"{metrics.get('recall', 0)*100:.2f}%")
                    col4.metric("F1 Score", f"{metrics.get('f1', 0):.2f}")
                    
                    responses = best_model_data["responses"]
                    
                    # Calculate combined score
                    combined_score = (metrics.get('accuracy', 0) + metrics.get('f1', 0)) / 2
                    st.metric("Combined Score (Accuracy+F1)/2", f"{combined_score:.4f}")
                    
                    # Show confidence distribution if confidence values exist
                    confidence_values = [r.get("confidence", None) for r in responses]
                    if any(conf is not None for conf in confidence_values):
                        st.subheader("Confidence Distribution")
                        
                        # Filter out None values
                        confidence_values = [c for c in confidence_values if c is not None]
                        
                        # Differentiate between correct and incorrect predictions
                        confidences_correct = [r.get("confidence", 0) for r in responses if r.get("correct", False) and r.get("confidence") is not None]
                        confidences_incorrect = [r.get("confidence", 0) for r in responses if not r.get("correct", False) and r.get("confidence") is not None]
                        
                        if confidences_correct or confidences_incorrect:
                            fig, ax = plt.subplots(figsize=(10, 5))
                            
                            bins = 10
                            if confidences_correct:
                                ax.hist(confidences_correct, bins=bins, alpha=0.6, label='Correct Predictions', color='green')
                            if confidences_incorrect:
                                ax.hist(confidences_incorrect, bins=bins, alpha=0.6, label='Incorrect Predictions', color='red')
                            
                            ax.set_xlabel('Confidence')
                            ax.set_ylabel('Count')
                            ax.set_title('Model Confidence Distribution')
                            ax.legend()
                            ax.grid(True, linestyle='--', alpha=0.7)
                            st.pyplot(fig)
                        else:
                            st.info("No confidence values available for visualization.")
                else:
                    st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
            
            # Tab 4: Parameter Tuning Results
            with tabs[3]:
                if st.session_state.classification_best_params:
                    st.header("Best Parameters")
                    
                    best_params = st.session_state.classification_best_params
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Best Temperature", f"{best_params.get('temperature', 0):.2f}")
                    col2.metric("Accuracy", f"{best_params.get('accuracy', 0)*100:.2f}%")
                    col3.metric("F1 Score", f"{best_params.get('f1', 0):.2f}")
                    
                    st.metric("Combined Score", f"{best_params.get('combined_score', 0):.4f}")
                    
                    # Add a section to show results for each temperature trial
                    st.subheader("Temperature Trial Results")
                    
                    # Check if we have the full tuning trials available
                    if 'classification_tuning_trials' in st.session_state and st.session_state.classification_tuning_trials:
                        trials = st.session_state.classification_tuning_trials
                        
                        # Create a dataframe to display all trial results
                        trials_data = []
                        for trial in trials:
                            trials_data.append({
                                "Temperature": f"{trial.get('temperature', 0):.2f}",
                                "Accuracy (%)": f"{trial.get('accuracy', 0)*100:.2f}%",
                                "F1 Score": f"{trial.get('f1', 0):.2f}",
                                "Combined Score": f"{trial.get('combined_score', 0):.4f}"
                            })
                        
                        # Display as a table
                        st.table(pd.DataFrame(trials_data))
                        
                        # Create visualization for temperature vs performance
                        st.subheader("Temperature vs. Performance")

                        # Extract data for chart
                        temp_vals = [trial.get('temperature', 0) for trial in trials]
                        accuracy_vals = [trial.get('accuracy', 0)*100 for trial in trials]
                        f1_vals = [trial.get('f1', 0)*100 for trial in trials]
                        combined_vals = [trial.get('combined_score', 0)*100 for trial in trials]

                        # Create DataFrame for visualization
                        temp_df = pd.DataFrame({
                            'Temperature': temp_vals,
                            'Accuracy (%)': accuracy_vals,
                            'F1 Score (%)': f1_vals,
                            'Combined Score (%)': combined_vals
                        }).astype({
                            'Accuracy (%)': 'float',
                            'F1 Score (%)': 'float',
                            'Combined Score (%)': 'float'
                        })

                        # Plot with Altair
                        base = alt.Chart(temp_df).encode(
                            x=alt.X('Temperature:Q', title='Temperature').scale(zero=False)
                        )

                        # Create a layered chart with multiple metrics
                        lines = base.mark_line(point=True).encode(
                            alt.Y('score:Q', title='Score (%)').scale(zero=False),
                            alt.Color('metric:N', title='Metric'),
                            tooltip=[
                                alt.Tooltip('Temperature:Q', title='Temp', format='.2f'),
                                alt.Tooltip('score:Q', title='Score', format='.2f'),
                                alt.Tooltip('metric:N', title='Metric')
                            ]
                        ).transform_fold(
                            fold=['Accuracy (%)', 'F1 Score (%)', 'Combined Score (%)'],
                            as_=['metric', 'score']
                        )

                        st.altair_chart(lines, use_container_width=True)
                        
                        # Show before/after comparison if available
                        if st.session_state.classification_tuning_results:
                            st.subheader("Before/After Tuning Comparison")
                            
                            best_model = st.session_state.classification_best_model
                            before_metrics = st.session_state.classification_evaluation_results[best_model]["metrics"]
                            after_metrics = st.session_state.classification_tuning_results.get("metrics", {})
                            
                            # Create comparison table
                            comparison_data = pd.DataFrame({
                                "Metric": ["Accuracy (%)", "Precision (%)", "Recall (%)", "F1 Score", "Combined Score"],
                                "Before Tuning": [
                                    f"{before_metrics.get('accuracy', 0)*100:.2f}%",
                                    f"{before_metrics.get('precision', 0)*100:.2f}%",
                                    f"{before_metrics.get('recall', 0)*100:.2f}%",
                                    f"{before_metrics.get('f1', 0):.2f}",
                                    f"{(before_metrics.get('accuracy', 0) + before_metrics.get('f1', 0))/2:.4f}"
                                ],
                                "After Tuning": [
                                    f"{after_metrics.get('accuracy', 0)*100:.2f}%",
                                    f"{after_metrics.get('precision', 0)*100:.2f}%",
                                    f"{after_metrics.get('recall', 0)*100:.2f}%",
                                    f"{after_metrics.get('f1', 0):.2f}",
                                    f"{(after_metrics.get('accuracy', 0) + after_metrics.get('f1', 0))/2:.4f}"
                                ]
                            })
                            
                            st.table(comparison_data)
                    else:
                        st.info("Tuning trials data not available for visualization.")
                    
                    # Add settings used for tuning
                    st.subheader("Tuning Settings Used")
                    settings_data = pd.DataFrame({
                        "Setting": ["Temperature Range", "Number of Trials", "Best Temperature Found"],
                        "Value": [
                            f"{min_temp} - {max_temp}",
                            num_trials,
                            f"{best_params.get('temperature', 0):.2f}"
                        ]
                    })
                    
                    st.table(settings_data)
                elif st.session_state.classification_running and st.session_state.classification_enable_tuning:
                    st.info("Tuning in progress...")
                elif st.session_state.classification_evaluation_results and not st.session_state.classification_enable_tuning:
                    st.info("Parameter tuning was disabled in settings")
                else:
                    st.info("Run evaluation with tuning enabled to see results")
            
            # Tab 5: Sample Examples
            with tabs[4]:
                if st.session_state.classification_evaluation_results:
                    st.header("Sample Classification Examples")
                    
                    # Select model to view examples from
                    models = list(st.session_state.classification_evaluation_results.keys())
                    selected_model_for_examples = st.selectbox(
                        "Select Model",
                        models,
                        index=models.index(st.session_state.classification_best_model) if st.session_state.classification_best_model in models else 0
                    )
                    
                    responses = st.session_state.classification_evaluation_results[selected_model_for_examples]["responses"]
                    
                    # Classification filter options
                    st.subheader("Filter Examples")
                    
                    filter_col1, filter_col2 = st.columns(2)
                    
                    with filter_col1:
                        filter_type = st.radio(
                            "Filter by",
                            ["All", "Correct Predictions", "Incorrect Predictions"]
                        )
                    
                    with filter_col2:
                        if st.session_state.classification_valid_classes:
                            class_filter = st.multiselect(
                                "Filter by Class",
                                ["All"] + st.session_state.classification_valid_classes,
                                default=["All"]
                            )
                    
                    # Apply filters
                    filtered_responses = responses
                    
                    if filter_type == "Correct Predictions":
                        filtered_responses = [r for r in responses if r.get("correct", False)]
                    elif filter_type == "Incorrect Predictions":
                        filtered_responses = [r for r in responses if not r.get("correct", False)]
                    
                    if class_filter and "All" not in class_filter:
                        filtered_responses = [r for r in filtered_responses 
                                             if r.get("ground_truth") in class_filter]
                    # In the "Sample Examples" tab, replace the pagination code with:

                    if filtered_responses:
                        st.write(f"Showing {len(filtered_responses)} examples")
                        
                        examples_per_page = 5
                        total_pages = max(1, (len(filtered_responses) + examples_per_page - 1) // examples_per_page)
                        
                        # Only show slider if there's more than one page
                        if total_pages > 1:
                            page = st.slider("Page", 1, total_pages, 1)
                        else:
                            page = 1
                        
                        start_idx = (page - 1) * examples_per_page
                        end_idx = min(start_idx + examples_per_page, len(filtered_responses))
                        
                        # Display paginated examples
                        for i, response in enumerate(filtered_responses[start_idx:end_idx], start=start_idx+1):
                            with st.expander(f"Example {i}: {response.get('question', 'N/A')[:60]}{'...' if len(response.get('question', '')) > 60 else ''}", expanded=i==start_idx+1):
                                # Add error handling for missing keys
                                try:
                                    st.markdown(f"**Question:** {response.get('question', 'N/A')}")
                                    st.markdown(f"**Ground Truth:** {response.get('ground_truth', 'N/A')}")
                                    
                                    # Handle potential missing prediction key
                                    prediction = response.get('prediction', response.get('predicted_class', 'N/A'))
                                    
                                    st.markdown(f"**Prediction:** {prediction}")
                                    
                                    # Determine if correct with error handling
                                    is_correct = response.get('correct', 
                                                            prediction == response.get('ground_truth', ''))
                                    
                                    st.markdown(f"**Correct:** {'✓' if is_correct else '✗'}")
                                    
                                    if 'confidence' in response:
                                        st.markdown(f"**Confidence:** {response['confidence']:.2f}")
                                    
                                    # Display full model response if available
                                    if 'full_response' in response:
                                        with st.expander("View Full Model Response"):
                                            st.text(response['full_response'])
                                    
                                    # Display explanation if available
                                    if 'explanation' in response and response['explanation']:
                                        st.subheader("Explanation")
                                        st.markdown(response['explanation'])
                                except KeyError as e:
                                    st.error(f"Error displaying example: Missing key {e}")
                                    if debug_mode:
                                        st.json(response)
                    else:
                        st.info("No examples match the current filters")
                else:
                    st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
            
            # Tab 6: LLM Judge Results
# Tab 6: LLM Judge Results
            # Tab 6: LLM Judge Results
            # Tab 6: LLM Judge Results
            with tabs[5]:
                if st.session_state.classification_judge_results:
                    st.header("LLM Judge Evaluation")
                    
                    # Debug raw results
                    if debug_mode:
                        with st.expander("Raw Judge Results (Debug)"):
                            st.json(st.session_state.classification_judge_results)

                    # Display overall scores and criteria breakdown
                    st.subheader("Detailed Evaluation Metrics")
                    
                    # Create tabs for different aspects
                    judge_tabs = st.tabs(["Summary Scores", "Criteria Breakdown", "Qualitative Analysis"])
                    
                    with judge_tabs[0]:  # Summary Scores
                        # Create a DataFrame for model scores
                        judge_scores = []
                        
                        for model_name, model_results in st.session_state.classification_judge_results.items():
                            qual_eval = model_results.get("qualitative_evaluation", {})
                            evaluation = qual_eval.get("evaluation", {})
                            
                            # Handle different response formats
                            final_score = evaluation.get("final_score") or evaluation.get("score") or 0
                            criteria_scores = evaluation.get("criteria_scores", {})
                            
                            row = {
                                "Model": model_name,
                                "Final Score": final_score,
                                "Strengths Count": len(evaluation.get("strengths", [])),
                                "Weaknesses Count": len(evaluation.get("weaknesses", []))
                            }
                            
                            # Add average criteria score
                            if criteria_scores:
                                avg_criteria = np.mean([v.get("score", 0) if isinstance(v, dict) else v for v in criteria_scores.values()])
                                row["Avg Criteria Score"] = avg_criteria
                            
                            judge_scores.append(row)
                        
                        if judge_scores:
                            judge_df = pd.DataFrame(judge_scores)
                            
                            # Format numeric columns
                            numeric_cols = judge_df.select_dtypes(include=[np.number]).columns.tolist()
                            st.dataframe(
                                judge_df.style.format(
                                    "{:.2f}", 
                                    subset=numeric_cols,
                                    na_rep="-"
                                ),
                                use_container_width=True
                            )
                            
                            # Visualization
                            st.subheader("Score Distribution")
                            score_cols = [c for c in judge_df.columns if "Score" in c]
                            
                            if score_cols:
                                melt_df = judge_df.melt(id_vars=["Model"], 
                                                    value_vars=score_cols,
                                                    var_name="Metric", 
                                                    value_name="Score")
                                
                                chart = alt.Chart(melt_df).mark_bar().encode(
                                    x=alt.X('Metric:N', title='', axis=alt.Axis(labelAngle=0)),
                                    y=alt.Y('Score:Q', title='Score'),
                                    color='Metric:N',
                                    column=alt.Column('Model:N', header=alt.Header(title="")))
                                st.altair_chart(chart)

                    with judge_tabs[1]:  # Criteria Breakdown
                        st.subheader("Detailed Criteria Scores")
                        
                        # Create a nested DataFrame for criteria scores
                        criteria_data = []
                        for model_name, model_results in st.session_state.classification_judge_results.items():
                            qual_eval = model_results.get("qualitative_evaluation", {})
                            evaluation = qual_eval.get("evaluation", {})
                            criteria_scores = evaluation.get("criteria_scores", {})
                            
                            for criterion, score_data in criteria_scores.items():
                                if isinstance(score_data, dict):
                                    score = score_data.get("score", 0)
                                    comment = score_data.get("comments", "")
                                else:
                                    score = score_data
                                    comment = ""
                                
                                criteria_data.append({
                                    "Model": model_name,
                                    "Criterion": criterion,
                                    "Score": score,
                                    "Comments": comment
                                })
                        
                        if criteria_data:
                            criteria_df = pd.DataFrame(criteria_data)
                            
                            # Pivot table for heatmap
                            pivot_df = criteria_df.pivot(index="Model", columns="Criterion", values="Score")
                            
                            # Heatmap visualization
                            st.subheader("Criteria Score Heatmap")
                            plt.figure(figsize=(10, 4))
                            sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlGnBu")
                            plt.title("Criteria Scores by Model")
                            st.pyplot(plt)
                            
                            # Detailed table
                            st.subheader("Detailed Scores & Comments")
                            st.dataframe(
                                criteria_df.style.format({"Score": "{:.1f}"}),
                                use_container_width=True
                            )
                        else:
                            st.info("No criteria scores available")

                    with judge_tabs[2]:  # Qualitative Analysis
                        st.subheader("Qualitative Evaluation Details")
                        
                        model_selector = st.selectbox(
                            "Select Model for Detailed Analysis",
                            options=list(st.session_state.classification_judge_results.keys())
                        )
                        
                        model_results = st.session_state.classification_judge_results[model_selector]
                        qual_eval = model_results.get("qualitative_evaluation", {})
                        evaluation = qual_eval.get("evaluation", {})
                        
                        # Create columns layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Strengths")
                            strengths = evaluation.get("strengths", [])
                            if isinstance(strengths, str):
                                strengths = [s.strip() for s in strengths.split("\n") if s.strip()]
                            for i, strength in enumerate(strengths[:5], 1):
                                st.markdown(f"{i}. {strength}")
                            
                            st.markdown("### Recommendations")
                            recommendations = evaluation.get("recommendations", [])
                            if isinstance(recommendations, str):
                                recommendations = [r.strip() for r in recommendations.split("\n") if r.strip()]
                            for i, rec in enumerate(recommendations[:5], 1):
                                st.markdown(f"{i}. {rec}")
                        
                        with col2:
                            st.markdown("### Weaknesses")
                            weaknesses = evaluation.get("weaknesses", [])
                            if isinstance(weaknesses, str):
                                weaknesses = [w.strip() for w in weaknesses.split("\n") if w.strip()]
                            for i, weakness in enumerate(weaknesses[:5], 1):
                                st.markdown(f"{i}. {weakness}")
                            
                            st.markdown("### Class Insights")
                            class_insights = evaluation.get("class_insights", {})
                            if class_insights:
                                st.markdown(f"**Well-handled:** {', '.join(class_insights.get('well_handled_classes', []))}")
                                st.markdown(f"**Problematic:** {', '.join(class_insights.get('poorly_handled_classes', []))}")
                                st.markdown(class_insights.get("comments", "No class-specific comments"))



                else:
                    st.info("Use the 'Evaluate Using LLM Judge' button in the Evaluation Results tab to see judge results")

            # Tab 7: Confusion Matrix
            with tabs[6]:
                if st.session_state.classification_evaluation_results:
                    st.header("Confusion Matrix")
                    
                    # Select model to view confusion matrix for
                    models = list(st.session_state.classification_evaluation_results.keys())
                    selected_model_for_matrix = st.selectbox(
                        "Select Model",
                        models,
                        index=models.index(st.session_state.classification_best_model) if st.session_state.classification_best_model in models else 0,
                        key="confusion_matrix_model_selection"
                    )
                    
                    # Get responses for the selected model
                    responses = st.session_state.classification_evaluation_results[selected_model_for_matrix]["responses"]
                    
                    # Extract actual and predicted classes with error handling
                    y_true = []
                    y_pred = []
                    
                    for r in responses:
                        try:
                            ground_truth = r.get("ground_truth")
                            # Try multiple possible keys for the prediction
                            prediction = r.get("predicted_class")
                            
                            if ground_truth is not None and prediction is not None:
                                y_true.append(ground_truth)
                                y_pred.append(prediction)
                        except Exception as e:
                            if debug_mode:
                                st.error(f"Error processing response: {str(e)}")
                                st.json(r)
                    
                    # Create confusion matrix if we have valid data
                    if y_true and y_pred and len(y_true) == len(y_pred):
                        # Get unique classes with order preservation
                        classes = list(dict.fromkeys(y_true + y_pred))
                        
                        # Calculate confusion matrix
                        cm = confusion_matrix(y_true, y_pred, labels=classes)
                        
                        # Create heatmap
                        plt.figure(figsize=(10, 8))
                        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                                   xticklabels=classes, yticklabels=classes)
                        plt.xlabel('Predicted')
                        plt.ylabel('Actual')
                        plt.title(f'Confusion Matrix - {selected_model_for_matrix}')
                        plt.tight_layout()
                        st.pyplot(plt)
                        
                        # Calculate class-wise metrics
                        st.subheader("Class-wise Performance")
                        
                        # Calculate per-class precision, recall, and F1
                        class_metrics = {}
                        for i, cls in enumerate(classes):
                            # True positives
                            tp = cm[i, i]
                            # False positives (sum of column i minus true positives)
                            fp = np.sum(cm[:, i]) - tp
                            # False negatives (sum of row i minus true positives)
                            fn = np.sum(cm[i, :]) - tp
                            
                            # Calculate metrics with handling for division by zero
                            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                            
                            class_metrics[cls] = {
                                'Precision': precision,
                                'Recall': recall,
                                'F1 Score': f1,
                                'Support': np.sum(cm[i, :])  # Total samples for this class
                            }
                        
                        # Convert to DataFrame for display
                        metrics_df = pd.DataFrame.from_dict(class_metrics, orient='index')
                        metrics_df = metrics_df.sort_values('Support', ascending=False)
                        
                        # Format as percentages
                        for col in ['Precision', 'Recall', 'F1 Score']:
                            metrics_df[col] = metrics_df[col].apply(lambda x: f"{x*100:.2f}%")
                        
                        st.dataframe(metrics_df)
                        
                        # Identify problematic classes
                        st.subheader("Class Error Analysis")
                        
                        # Create a DataFrame for error analysis
                        error_data = []
                        
                        for i, actual_cls in enumerate(classes):
                            # Get misclassifications for this class
                            for j, pred_cls in enumerate(classes):
                                if i != j and cm[i, j] > 0:
                                    error_data.append({
                                        'Actual Class': actual_cls,
                                        'Predicted Class': pred_cls,
                                        'Count': cm[i, j],
                                        'Error Rate': cm[i, j] / np.sum(cm[i, :]) if np.sum(cm[i, :]) > 0 else 0
                                    })
                        
                        # Sort by error count
                        if error_data:
                            error_df = pd.DataFrame(error_data).sort_values('Count', ascending=False)
                            error_df['Error Rate'] = error_df['Error Rate'].apply(lambda x: f"{x*100:.2f}%")
                            st.dataframe(error_df)
                            
                            # Show top error examples
                            st.subheader("Top Error Examples")
                            
                            # Find examples of the top errors
                            if error_df.shape[0] > 0:
                                top_error = error_df.iloc[0]
                                actual_cls = top_error['Actual Class']
                                pred_cls = top_error['Predicted Class']
                                
                                st.markdown(f"Examples where **{actual_cls}** was misclassified as **{pred_cls}**:")
                                
                                # Find examples in responses
                                error_examples = []
                                for r in responses:
                                    if r.get("ground_truth") == actual_cls and r.get("prediction", r.get("predicted_class", r.get("class", None))) == pred_cls:
                                        error_examples.append(r)
                                
                                # Show up to 3 examples
                                for i, ex in enumerate(error_examples[:3]):
                                    with st.expander(f"Example {i+1}: {ex.get('question', '')[:60]}{'...' if len(ex.get('question', '')) > 60 else ''}", expanded=i==0):
                                        try:
                                            st.markdown(f"**Question:** {ex.get('question', 'N/A')}")
                                            st.markdown(f"**Actual Class:** {ex.get('ground_truth', 'N/A')}")
                                            st.markdown(f"**Predicted Class:** {ex.get('prediction', ex.get('predicted_class', ex.get('class', 'N/A')))}")
                                            
                                            if 'confidence' in ex:
                                                st.markdown(f"**Confidence:** {ex['confidence']:.2f}")
                                            
                                            if 'explanation' in ex and ex['explanation']:
                                                st.subheader("Model's Explanation")
                                                st.markdown(ex['explanation'])
                                        except Exception as e:
                                            st.error(f"Error displaying error example: {str(e)}")
                        else:
                            st.success("No classification errors found!")
                    else:
                        st.warning("Insufficient data to create confusion matrix. Make sure responses contain valid ground_truth and prediction values.")
                        if debug_mode and (y_true or y_pred):
                            st.write(f"Debug info - True labels: {len(y_true)}, Predicted labels: {len(y_pred)}")
                            if len(y_true) != len(y_pred):
                                st.error("Mismatch in number of true and predicted labels")
                else:
                    st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")

        # Add a section at the bottom for debugging errors
        if debug_mode and st.session_state.classification_error_details:
            st.header("Debug Information")
            st.error("Error occurred during processing")
            st.code(st.session_state.classification_error_details, language="text")
            
            # Add a button to clear error details
            if st.button("Clear Error Details"):
                st.session_state.classification_error_details = None

    return None

def text2sql_ui_mm():
    
    # Import necessary libraries for visualization
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import os
    import matplotlib.pyplot as plt
    import streamlit as st
    from llm_consortium.core.sql_with_mm.sql_model_runner import SQLModelRunner
    from llm_consortium.core.sql.sql_judge import SQLJudge 
    from llm_consortium.config.models_sql_mm import ModelConfig
    from llm_consortium.metrics.registry import MetricRegistry
    import asyncio
    import json
    import tempfile
    import pandas as pd
    import altair as alt
    import uuid
    from llm_consortium.utils.logging import logger
    from datetime import datetime
    from llm_consortium.utils.pricing import calculate_cost
    from llm_consortium.core.client_init import llm
    

    # Initialize judge and metric registry
    judge = SQLJudge(llm)
    metric_registry = MetricRegistry()
    
    # Get available SQL metrics dynamically
    available_metrics = metric_registry.get_metrics_for_task("sql")

    # Title and description
    st.title("SQL Model Evaluation and Tuning")
    st.markdown("""
    This tool evaluates different LLM models for SQL query generation and tunes parameters for the best performer.
    Upload your test dataset, select models to evaluate, and configure evaluation parameters.
    """)

    # Initialize session state for storing results between reruns
    if 'sql_evaluation_results' not in st.session_state:
        st.session_state.sql_evaluation_results = None
    if 'sql_best_model' not in st.session_state:
        st.session_state.sql_best_model = None
    if 'sql_best_params' not in st.session_state:
        st.session_state.sql_best_params = None
    if 'sql_tuning_results' not in st.session_state:
        st.session_state.sql_tuning_results = None
    if 'sql_running' not in st.session_state:
        st.session_state.sql_running = False
    if 'sql_progress' not in st.session_state:
        st.session_state.sql_progress = 0
    if 'sql_judge_results' not in st.session_state:
        st.session_state.sql_judge_results = None
    if 'sql_judge_running' not in st.session_state:
        st.session_state.sql_judge_running = False
    if 'sql_tuning_comparison' not in st.session_state:
        st.session_state.sql_tuning_comparison = None
    if 'sql_sampled_dataset' not in st.session_state:
        st.session_state.sql_sampled_dataset = None
    if 'sql_tuning_trials' not in st.session_state:
        st.session_state.sql_tuning_trials = None

    def reset_results():
        st.session_state.sql_evaluation_results = None
        st.session_state.sql_best_model = None
        st.session_state.sql_best_params = None
        st.session_state.sql_tuning_results = None
        st.session_state.sql_running = False
        st.session_state.sql_progress = 0
        st.session_state.sql_judge_results = None
        st.session_state.sql_judge_running = False
        st.session_state.sql_tuning_comparison = None
        st.session_state.sql_sampled_dataset = None
        st.session_state.sql_tuning_trials = None

    # Layout with two columns - config panel and results
    col1, col2 = st.columns([1, 3])

    # Configuration panel
    with col1:
        st.header("Configuration")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Test Dataset (CSV)", type=["csv"], key="sql_csv_upload")
        
        # Add dataset sampling option
        if uploaded_file is not None:
            # Read the uploaded file to get the number of rows
            df = pd.read_csv(uploaded_file)
            total_rows = len(df)
            
            st.subheader("Dataset Sampling")
            enable_sampling = st.checkbox("Enable Dataset Sampling", value=False, key="sql_enable_sampling")
            
            if enable_sampling:
                sample_size = st.slider(
                    "Sample Size", 
                    min_value=min(10, total_rows),
                    max_value=total_rows,
                    value=min(50, total_rows),
                    step=10,
                    help=f"Select number of samples to use from your dataset of {total_rows} records"
                )
                
                # Display percentage of total
                st.caption(f"Selected {sample_size} samples ({(sample_size/total_rows*100):.1f}% of total)")
            else:
                # If sampling is not enabled, use all rows
                sample_size = total_rows
            
            # Reset file position to beginning for later use
            uploaded_file.seek(0)
        
        # Model selection (with default models)
        default_models = ["gpt-4o-mini", "gpt-4o"]
        available_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        selected_models = st.multiselect(
            "Select Models to Evaluate", 
            available_models,
            default=default_models,
            key="sql_models"
        )
        
        # Judge model selection
        judge_models = ["gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"] 
        selected_judge = st.selectbox(
            "LLM Judge Model",
            judge_models,
            index=0,
            key="sql_judge_model"
        )
        
        # Metrics selection - dynamically populated from the registry
        st.subheader("Metrics Selection")
        
        # Format available metrics for display
        metric_options = {name: metric.description for name, metric in available_metrics.items()}
        
        # Default to select all metrics if none are defined
        default_metrics = list(metric_options.keys()) if metric_options else []
        
        selected_metrics = st.multiselect(
            "Select Evaluation Metrics",
            options=list(metric_options.keys()),
            format_func=lambda x: f"{x} - {metric_options[x]}" if x in metric_options else x,
            default=default_metrics[:2] if len(default_metrics) > 1 else default_metrics,
            help="Select metrics to use for evaluation"
        )
        
        if not selected_metrics:
            st.warning("Please select at least one metric for evaluation")
            
        st.session_state.selected_metrics = selected_metrics
        
        # Base configuration
        st.subheader("Base Settings")
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.2, 0.05, key="sql_base_temp")
        
        # Tuning settings
        st.subheader("Parameter Tuning")
        enable_tuning = st.checkbox("Enable Parameter Tuning", value=True, key="sql_enable_tuning")
        
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.0, 0.05, key="sql_min_temp")
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.8, 0.05, key="sql_max_temp")
        num_trials = st.slider("Number of Trials", 3, 10, 5, key="sql_num_trials")
        
        # Get available judge criteria - dynamically defined
        default_judge_criteria = [
            "Column name accuracy",
            "Table usage correctness",
            "Query structure", 
            "Intent understanding"
        ]
        
        all_judge_criteria = [
            "Column name accuracy",
            "Table usage correctness",
            "Join quality",
            "Condition correctness",
            "Query structure",
            "SQL syntax correctness",
            "Query optimization",
            "Intent understanding"
        ]
        
        # Judge settings
        st.subheader("Judge Settings")
        judge_criteria = st.multiselect(
            "Judge Criteria",
            all_judge_criteria,
            default=default_judge_criteria,
            key="sql_judge_criteria"
        )
        
        # Output settings
        st.subheader("Output Settings")
        output_dir = st.text_input("Output Directory", "results", key="sql_output_dir")
        save_results = st.checkbox("Save Results to File", value=True, key="sql_save_results")
        
        # Run button - disabled if no metrics or models selected
        run_button = st.button(
            "Run Evaluation", 
            type="primary", 
            key="sql_run_button", 
            disabled=len(selected_models) == 0 or uploaded_file is None or len(selected_metrics) == 0
        )

    # Main content area in the second column
    with col2:
        async def run_evaluation_async(config, csv_path, sampled_csv_path=None):
            """Run the evaluation and tuning pipeline asynchronously"""
            try:
                # Initialize runner with selected metrics
                runner = SQLModelRunner(selected_metrics=config.metrics)
                
                # Step 1: Evaluate all models
                st.session_state.sql_progress = 10
                evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluating models...")
                
                # Use the sampled dataset if available
                eval_csv_path = sampled_csv_path if sampled_csv_path else csv_path
                
                # Run evaluation
                evaluation_results = await runner.evaluate_models(config, eval_csv_path)
                st.session_state.sql_evaluation_results = evaluation_results
                st.session_state.sql_progress = 50
                evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluation complete, processing results...")
                
                # Calculate metrics for each model
                model_metrics = {}
                
                # Track which metric to use for ranking (use first selected metric)
                primary_metric = f"{config.metrics[0]}_rate" if config.metrics else None
                
                for model_name, eval_data in evaluation_results.items():
                    metrics = eval_data["metrics"]
                    responses = eval_data["responses"]
                    
                    # Calculate average latency (not directly provided in metrics)
                    latencies = [r.get("latency", 0) for r in responses]
                    avg_latency = sum(latencies) / len(latencies) if latencies else 0
                    
                    # Add all available metrics to the results
                    model_metrics[model_name] = {"avg_latency": avg_latency}
                    
                    # Add all rate metrics from the evaluation
                    for key, value in metrics.items():
                        if key.endswith("_rate") and isinstance(value, (int, float)):
                            model_metrics[model_name][key] = value
                
                # Find best model based on primary metric (first selected), breaking ties with latency
                if primary_metric and model_metrics:
                    best_model = max(
                        model_metrics.items(),
                        key=lambda x: (x[1].get(primary_metric, 0), -x[1]["avg_latency"])
                    )[0]
                    
                    st.session_state.sql_best_model = best_model
                    st.session_state.sql_progress = 60
                    evaluation_progress.progress(st.session_state.sql_progress/100, f"Best model identified: {best_model}")
                else:
                    st.warning("Could not determine best model - no valid metrics available")
                    st.session_state.sql_best_model = selected_models[0] if selected_models else None
                    st.session_state.sql_progress = 60
                    evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluation complete")
                
                # Step 3: Tune the best model if enabled
                if config.enable_tuning and st.session_state.sql_best_model:
                    best_model = st.session_state.sql_best_model
                    evaluation_progress.progress(st.session_state.sql_progress/100, f"Tuning {best_model}...")
                    
                    # Tune the best model
                    best_params = await runner.tune_best_model(
                        best_model,
                        eval_csv_path,  # Use the already sampled dataset
                        config
                    )
                    st.session_state.sql_best_params = best_params
                    
                    # Capture the temperature trial results if available from the tuner
                    if hasattr(runner.hyperparameter_tuner, 'trial_results'):
                        st.session_state.sql_tuning_trials = runner.hyperparameter_tuner.trial_results
                    
                    st.session_state.sql_progress = 80
                    evaluation_progress.progress(st.session_state.sql_progress/100, "Tuning complete")
                
                    # Step 4: Evaluate with tuned parameters
                    if config.run_final_evaluation:
                        evaluation_progress.progress(st.session_state.sql_progress/100, f"Final evaluation with tuned parameters...")
                        final_results = await runner.evaluate_with_params(
                            best_model, 
                            best_params, 
                            eval_csv_path  # Use the already sampled dataset
                        )
                        st.session_state.sql_tuning_results = final_results
                        
                # Save results if requested
                if save_results:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"sql_eval_results_{timestamp}.json")
                    
                    with open(output_file, "w") as f:
                        json.dump({
                            "model_evaluations": evaluation_results,
                            "best_model": st.session_state.sql_best_model,
                            "best_params": st.session_state.sql_best_params if config.enable_tuning else None,
                            "model_metrics": model_metrics,
                            "sample_size": sample_size if 'sample_size' in locals() else "full dataset",
                            "selected_metrics": config.metrics
                        }, f, indent=2, default=str)
                        
                st.session_state.sql_progress = 100
                evaluation_progress.progress(st.session_state.sql_progress/100, "Complete!")
                return model_metrics
                
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
                logger.error(f"Evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.sql_running = False
        
        # Judge evaluation function
        async def run_judge_evaluation_async(judge_criteria):
            """Run the judge evaluation asynchronously"""
            try:
                # Ensure criteria is always a list of strings
                if isinstance(judge_criteria, str):
                    judge_criteria = [judge_criteria]
                    
                if not isinstance(judge_criteria, list):
                    raise ValueError("Judge criteria must be a list")
                    
                # Validate each criterion is a string
                judge_criteria = [str(c) for c in judge_criteria]
                
                # Pass to judge
                judge_results = await judge.evaluate_model_outputs(
                    st.session_state.sql_evaluation_results,
                    criteria=judge_criteria,
                    model=st.session_state.get('sql_judge_model', 'gpt-4o-mini')  # Use the selected judge model
                )
                
                # Store results
                st.session_state.sql_judge_results = judge_results
                
                # If we have before/after tuning results, compare those too
                if st.session_state.sql_best_model and st.session_state.sql_tuning_results:
                    best_model = st.session_state.sql_best_model
                    before_data = st.session_state.sql_evaluation_results[best_model]
                    after_data = st.session_state.sql_tuning_results
                    
                    tuning_comparison = await judge.before_after_tuning_comparison(
                        best_model,
                        before_data,
                        after_data,
                        model=st.session_state.get('sql_judge_model', 'gpt-4o-mini')  # Use the selected judge model
                    )
                    
                    st.session_state.sql_tuning_comparison = tuning_comparison
                
                return judge_results
                
            except Exception as e:
                st.error(f"Error during judge evaluation: {str(e)}")
                logger.error(f"Judge evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.sql_judge_running = False
        
        # Handle run button click
        if run_button and not st.session_state.sql_running:
            sampled_csv_path = None
            
            # Validate at least one metric is selected
            if not selected_metrics:
                st.error("Please select at least one metric for evaluation")
            else:
                # Create sampled dataset if sampling is enabled
                if st.session_state.get('sql_enable_sampling', False) and uploaded_file is not None:
                    # Read the full dataset
                    df = pd.read_csv(uploaded_file)
                    total_rows = len(df)
                    
                    # Check if sampling is actually needed
                    if sample_size < total_rows:
                        # Sample the dataset
                        sampled_df = df.sample(n=sample_size, random_state=42)
                        
                        # Save the sampled dataset to a temporary file
                        sampled_csv_path = "temp_sampled_dataset.csv"
                        sampled_df.to_csv(sampled_csv_path, index=False)
                        st.session_state.sql_sampled_dataset = sampled_csv_path
                        
                        # Display info about sampling
                        st.info(f"Using {sample_size} samples out of {total_rows} records ({(sample_size/total_rows*100):.1f}%)")
                
                # Create config
                config = ModelConfig(
                    models=selected_models,
                    metrics=selected_metrics,
                    base_temperature=base_temperature,
                    enable_tuning=enable_tuning,
                    min_temp=min_temp,
                    max_temp=max_temp,
                    num_trials=num_trials,
                    run_final_evaluation=True
                )
                
                # Save uploaded file temporarily
                temp_csv = "temp_dataset.csv"
                with open(temp_csv, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Reset previous results
                reset_results()
                
                # Show progress bar
                evaluation_progress = st.progress(0, "Starting evaluation...")
                st.session_state.sql_running = True
                
                # Method 1: Using a synchronous wrapper function
                def run_evaluation(config, csv_path, sampled_csv_path):
                    """Synchronous wrapper for the async evaluation function"""
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(run_evaluation_async(config, csv_path, sampled_csv_path))
                    finally:
                        loop.close()
                
                # Run the evaluation in the current thread (this will block the UI until complete)
                run_evaluation(config, temp_csv, sampled_csv_path)
        # Display tabs for results (rest of your UI code remains mostly unchanged

        if st.session_state.sql_running or st.session_state.sql_evaluation_results:
            # Define tabs configuration with properties
            tab_config = {
                "evaluation_results": {
                    "title": "Evaluation Results",
                    "icon": "📊"
                },
                "model_comparison": {
                    "title": "Model Comparison",
                    "icon": "📈"
                },
                "best_model": {
                    "title": "Best Model",
                    "icon": "🥇"
                },
                "best_parameter": {
                    "title": "Best Parameter",
                    "icon": "⚙️"
                },
                "sample_queries": {
                    "title": "Sample Queries",
                    "icon": "📝"
                },
                "llm_judge": {
                    "title": "LLM Judge",
                    "icon": "👨‍⚖️"
                },
                "cost_estimation": {
                    "title": "Cost Estimation",
                    "icon": "💰"
                }
            }
            
            # Create tabs dynamically
            tab_titles = [f"{config['icon']} {config['title']}" for tab_id, config in tab_config.items()]
            tabs = st.tabs(tab_titles)
            
            # Store tab mapping for easy access
            tab_mapping = {tab_id: idx for idx, tab_id in enumerate(tab_config.keys())}
            
            # Tab for Evaluation Results
            with tabs[tab_mapping["evaluation_results"]]:
                if st.session_state.sql_evaluation_results:
                    st.header("Model Evaluation Results")
                    
                    # Display sampling information if dataset was sampled
                    if st.session_state.sql_sampled_dataset:
                        st.info(f"Results based on sampled dataset ({sample_size} records)")
                    
                    # Add LLM Judge button
                    judge_col1, judge_col2 = st.columns([1, 3])
                    with judge_col1:
                        judge_button = st.button(
                            "Evaluate Using LLM Judge", 
                            type="primary", 
                            key="sql_judge_button",
                            disabled=st.session_state.sql_judge_running
                        )
                    
                    if judge_button and not st.session_state.sql_judge_running:
                        st.session_state.sql_judge_running = True
                        
                        # Run judge evaluation
                        def run_judge():
                            """Synchronous wrapper for the async judge evaluation function"""
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
                            finally:
                                loop.close()
                        
                        # Show a spinner during evaluation
                        with st.spinner("LLM Judge evaluating models..."):
                            run_judge()
                        
                        # Show completion message
                        st.success("LLM Judge evaluation complete! See the 'LLM Judge' tab for results.")
                        
                    # Dynamic metrics table
                    metrics_data = []
                    
                    for model_name, eval_data in st.session_state.sql_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        responses = eval_data["responses"]
                        
                        # Base model info
                        model_metrics = {
                            "Model": model_name,
                            "Samples": len(responses),
                            "Avg. Latency (s)": round(sum(r["latency"] for r in responses) / len(responses), 3)
                        }
                        
                        # Add selected metrics
                        for metric in selected_metrics:
                            if metric in metrics:
                                value = metrics[metric]
                                # Convert any objects to string to prevent type errors
                                if not isinstance(value, (str, int, float, bool)):
                                    value = str(value)
                                if isinstance(value, float):
                                    model_metrics[available_metrics[metric]] = f"{value:.2f}%"
                                else:
                                    model_metrics[available_metrics[metric]] = str(value)
                        
                        metrics_data.append(model_metrics)
                    
                    # Create DataFrame with dynamic columns
                    columns_order = ["Model"] + [available_metrics[m] for m in selected_metrics] + ["Avg. Latency (s)", "Samples"]
                    
                    # Filter columns to only those that exist in the dataframe
                    metrics_df = pd.DataFrame(metrics_data)
                    existing_columns = [col for col in columns_order if col in metrics_df.columns]
                    metrics_df = metrics_df[existing_columns]

                    st.dataframe(metrics_df, use_container_width=True)
                    
                    if st.session_state.sql_best_model:
                        st.success(f"Best model: {st.session_state.sql_best_model}")

                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
                    
            # Tab for Model Comparison Charts
            with tabs[tab_mapping["model_comparison"]]:
                if st.session_state.sql_evaluation_results:
                    st.header("Model Comparison")
                    
                    # Prepare data for visualization
                    comparison_data = []
                    
                    for model_name, eval_data in st.session_state.sql_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        entry = {
                            "Model": model_name,
                            "Avg. Latency (s)": sum(r["latency"] for r in eval_data["responses"]) / len(eval_data["responses"])
                        }
                        
                        # Add selected metrics using rate keys
                        for metric in selected_metrics:
                            rate_key = f"{metric}_rate"
                            if rate_key in metrics:
                                # Ensure the value is a float or convert it
                                if isinstance(metrics[rate_key], (int, float)):
                                    entry[rate_key] = metrics[rate_key]
                                else:
                                    # Try to convert to float if possible, otherwise use 0
                                    try:
                                        entry[rate_key] = float(metrics[rate_key])
                                    except (ValueError, TypeError):
                                        entry[rate_key] = 0.0
                            else:
                                entry[rate_key] = 0.0
                        
                        comparison_data.append(entry)
                    
                    # Create DataFrame and rename columns
                    df = pd.DataFrame(comparison_data)
                    rename_dict = {f"{metric}_rate": available_metrics[metric] for metric in selected_metrics}
                    df.rename(columns=rename_dict, inplace=True)
                    
                    # Plotting
                    if len(selected_metrics) > 0 and not df.empty:
                        try:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            metric_cols = [available_metrics[m] for m in selected_metrics if f"{m}_rate" in df.columns or available_metrics[m] in df.columns]
                            
                            # Only proceed if we have valid metric columns
                            if metric_cols:
                                # Make sure DataFrame has all required columns
                                for col in metric_cols:
                                    if col not in df.columns:
                                        df[col] = 0.0
                                
                                df.set_index("Model")[metric_cols].plot.bar(ax=ax)
                                ax.set_title("Model Performance Comparison")
                                ax.set_ylabel("Score (%)")
                                ax.grid(True, linestyle='--', alpha=0.7)
                                plt.xticks(rotation=45, ha='right')
                                st.pyplot(fig)
                            else:
                                st.warning("No valid metrics available for plotting")
                        except Exception as e:
                            st.error(f"Error generating plot: {str(e)}")
                            st.write("Comparison data:", df)
                    else:
                        st.warning("No metrics selected for comparison or no data available")
                else:
                    st.info("Complete evaluation to view model comparison charts")

            # Tab for Best Model Details
            with tabs[tab_mapping["best_model"]]:
                if st.session_state.sql_best_model:
                    st.header(f"Best Model: {st.session_state.sql_best_model}")
                    
                    best_model_data = st.session_state.sql_evaluation_results[st.session_state.sql_best_model]
                    metrics = best_model_data["metrics"]
                    responses = best_model_data["responses"]
                    
                    # Create dynamic columns based on selected metrics
                    num_cols = len(selected_metrics) + 1  # +1 for latency
                    cols = st.columns(num_cols)
                    
                    # Add selected metrics
                    for idx, metric in enumerate(selected_metrics):
                        if idx < len(cols):  # Safety check
                            rate_key = f"{metric}_rate"
                            if rate_key in metrics:
                                # Ensure value is a number or convert to string
                                try:
                                    value = float(metrics[rate_key])
                                    cols[idx].metric(
                                        str(available_metrics[metric]), 
                                        f"{value:.2f}%"
                                    )
                                except (ValueError, TypeError):
                                    cols[idx].metric(
                                        str(available_metrics[metric]), 
                                        str(metrics[rate_key])
                                    )
                            elif metric in metrics:
                                # Always convert to string to avoid type errors
                                cols[idx].metric(
                                    str(available_metrics[metric]), 
                                    str(metrics[metric])
                                )
                    
                    # Add latency in last column
                    if len(cols) > 0:  # Safety check
                        avg_latency = sum(r["latency"] for r in responses) / len(responses)
                        cols[-1].metric("Average Latency", f"{avg_latency:.3f}s")
                else:
                    st.info("Complete evaluation to view best model details")

            # Tab for Parameter Tuning Results
            with tabs[tab_mapping["best_parameter"]]:
                if st.session_state.sql_best_params:
                    st.header("Best Parameter")
                    
                    # Dynamic display based on primary metric
                    primary_metric = available_metrics[selected_metrics[0]] if selected_metrics else "Performance"
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Best Temperature", f"{st.session_state.sql_best_params['temperature']:.2f}")
                    col2.metric(f"{primary_metric} Improvement", 
                            f"{st.session_state.sql_best_params.get('improvement', 0):.2f}%")
                    
                    if 'sql_tuning_trials' in st.session_state:
                        st.subheader("Parameter Trial Results")
                        trials_data = []
                        for trial in st.session_state.sql_tuning_trials:
                            trial_data = {"Temperature": f"{trial['temperature']:.2f}"}
                            for metric in selected_metrics:
                                rate_key = f"{metric}_rate"
                                if rate_key in trial:
                                    # Ensure value is a number
                                    try:
                                        value = float(trial[rate_key])
                                        trial_data[str(available_metrics[metric])] = f"{value:.2f}%"
                                    except (ValueError, TypeError):
                                        trial_data[str(available_metrics[metric])] = str(trial[rate_key])
                            trials_data.append(trial_data)
                        
                        # Create DataFrame only if there's data
                        if trials_data:
                            st.dataframe(pd.DataFrame(trials_data), use_container_width=True)
                        else:
                            st.info("No tuning trial data available")
                else:
                    st.info("Enable parameter tuning and complete evaluation to view tuning results")

            # Tab for Sample Queries
            with tabs[tab_mapping["sample_queries"]]:
                if st.session_state.sql_evaluation_results:
                    st.header("Sample Query Results")
                    
                    # Model selector for viewing samples
                    model_to_view = st.selectbox(
                        "Select model to view samples",
                        list(st.session_state.sql_evaluation_results.keys()),
                        key="sql_model_selector"
                    )
                    
                    if model_to_view:
                        responses = st.session_state.sql_evaluation_results[model_to_view]["responses"]
                        
                        # Filter options
                        filter_col1, filter_col2 = st.columns(2)
                        show_correct = filter_col1.checkbox("Show Correct Queries", value=True, key="sql_show_correct")
                        show_incorrect = filter_col2.checkbox("Show Incorrect Queries", value=True, key="sql_show_incorrect")
                        
                        # Make sure execution_match is a boolean, not an object
                        filtered_responses = []
                        for r in responses:
                            # Convert execution_match to boolean if it's an object
                            if not isinstance(r["execution_match"], bool):
                                r["execution_match"] = bool(r["execution_match"])
                            
                            if (show_correct and r["execution_match"]) or (show_incorrect and not r["execution_match"]):
                                filtered_responses.append(r)
                        
                        # Show samples
                        if filtered_responses:
                            for i, response in enumerate(filtered_responses[:10]):  # Limit to 10 samples
                                with st.expander(
                                    f"Query {i+1}: {'✅' if response['execution_match'] else '❌'} " + 
                                    response["question"][:100] + ("..." if len(response["question"]) > 100 else "")
                                ):
                                    st.markdown("**Question:**")
                                    st.write(response["question"])
                                    
                                    st.markdown("**Generated SQL:**")
                                    st.code(response["generated_sql"], language="sql")
                                    
                                    st.markdown("**Gold SQL:**")
                                    st.code(response["gold_sql"], language="sql")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    # Convert to string for display
                                    exec_match = "✅" if response["execution_match"] else "❌"
                                    exact_match = "✅" if response["exact_match"] else "❌"
                                    
                                    col1.metric("Execution Match", exec_match)
                                    col2.metric("Exact Match", exact_match)
                                    col3.metric("Confidence", f"{response['confidence']:.2f}")
                        else:
                            st.info("No queries matching your filter criteria")
                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see sample queries")
            
            # Tab for LLM Judge Results
            with tabs[tab_mapping["llm_judge"]]:
                st.header("LLM Judge Evaluation")
                
                if st.session_state.sql_judge_running:
                    st.info("LLM judge evaluation in progress...")
                elif st.session_state.sql_judge_results:
                    # Display judge results
                    
                    # Model selection for viewing judge results
                    judge_model_to_view = st.selectbox(
                        "Select model to view judge evaluation",
                        list(st.session_state.sql_judge_results.keys()),
                        key="sql_judge_model_selector"
                    )
                    
                    if judge_model_to_view:
                        judge_result = st.session_state.sql_judge_results[judge_model_to_view]
                        
                        # Display any errors if present
                        if "error" in judge_result:
                            st.error(f"Judge evaluation error: {judge_result['error']}")
                        else:
                            st.subheader(f"Judge Evaluation for {judge_model_to_view}")
                            
                            # If the response has structured evaluation data
                            if "evaluation" in judge_result and isinstance(judge_result["evaluation"], dict):
                                evaluation = judge_result["evaluation"]
                                
                                # Display scores if available
                                if "criteria_scores" in evaluation:
                                    st.subheader("Criteria Scores")
                                    
                                    # Create score visualization
                                    criteria_scores = evaluation["criteria_scores"]
                                    score_data = []
                                    for criterion, data in criteria_scores.items():
                                        score_data.append({
                                            "Criterion": criterion,
                                            "Score": data["score"],
                                            "Comments": data["comments"]
                                        })
                                    
                                    # Display as a table
                                    st.table(pd.DataFrame(score_data))
                                    
                                    # Create radar chart for scores
                                    labels = [item["Criterion"] for item in score_data]
                                    scores = [item["Score"] for item in score_data]
                                    if labels and scores:
                                        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
                                        
                                        # Compute angles for each axis
                                        angles = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
                                        scores += scores[:1]  # close the loop
                                        angles += angles[:1]

                                        # Draw the outline of the radar chart
                                        ax.plot(angles, scores, linewidth=2, linestyle='solid')
                                        ax.fill(angles, scores, alpha=0.4)

                                        ax.set_xticks(angles[:-1])
                                        ax.set_xticklabels(labels)

                                        ax.set_yticklabels([])
                                        ax.set_title("LLM Judge Criteria Radar Chart")
                                        st.pyplot(fig)
                                    else:
                                        st.info("No criteria scores available for visualization.")

                                    # # Only create chart if we have data
                                    # if labels and scores:
                                    #     fig = plt.figure(figsize=(8, 8))
                                    #     ax = fig.add_subplot(111, polar=True)
                                        
                                    #     # Set the angles for each criterion
                                    #     angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
                                    #     angles += angles[:1]  # Close the loop
                                        
                                    #     # Add the scores
                                    #     scores += scores[:1]  # Close the loop
                                        
                                    #     # Plot
                                    #     ax.plot(angles, scores, linewidth=2, linestyle='solid')
                                    #     ax.fill(angles, scores, alpha=0.25)
                                        
                                    #     # Set labels and ticks
                                    #     ax.set_xticks(angles[:-1])
                                    #     ax.set_xticklabels(labels)
                                    #     ax.set_yticks([2, 4, 6, 8, 10])
                                    #     ax.set_yticklabels(['2', '4', '6', '8', '10'])
                                    #     ax.set_ylim(0, 10)
                                        
                                    #     plt.title(f'Judge Scores for {judge_model_to_view}')
                                    #     st.pyplot(fig)
                                
                                # Display strengths and weaknesses
                                if "strengths" in evaluation:
                                    st.subheader("Strengths")
                                    for strength in evaluation["strengths"]:
                                        st.markdown(f"- {strength}")
                                
                                if "weaknesses" in evaluation:
                                    st.subheader("Weaknesses")
                                    for weakness in evaluation["weaknesses"]:
                                        st.markdown(f"- {weakness}")
                                
                                # Display summary and final score
                                if "summary" in evaluation:
                                    st.subheader("Summary")
                                    st.write(evaluation["summary"])
                                
                                if "final_score" in evaluation:
                                    st.metric("Final Score", f"{evaluation['final_score']}/100")
                            else:
                                # Display raw evaluation text
                                st.markdown("### Judge Evaluation")
                                st.write(judge_result.get("raw_response", "No detailed evaluation available"))
                    
                    # Show tuning comparison if available
                    if st.session_state.sql_tuning_comparison:
                        st.markdown("---")
                        st.header("Before vs After Tuning Analysis")
                        
                        tuning_comp = st.session_state.sql_tuning_comparison
                        model_name = tuning_comp.get("model_name")
                        
                        if "error" in tuning_comp:
                            st.error(f"Tuning comparison error: {tuning_comp['error']}")
                        else:
                            st.subheader(f"Tuning Impact Analysis for {model_name}")
                            
                            # Display the analysis
                            st.markdown(tuning_comp.get("tuning_impact_analysis", "No tuning analysis available"))
                
                else:
                    # Show instructions for using the judge
                    st.info("""
                    To get an LLM judge evaluation of your models:
                    1. Complete a model evaluation run
                    2. Go to the "Evaluation Results" tab
                    3. Click the "Evaluate Using LLM Judge" button
                    
                    The judge will evaluate each model's SQL generation quality and provide detailed feedback.
                    """)
                    
                    # If we have evaluation results but no judge results, show reminder
                    if st.session_state.sql_evaluation_results:
                        st.markdown("#### Ready for Judge Evaluation")
                        st.markdown("You have evaluation results ready to be analyzed by the LLM judge.")
                        judge_reminder_button = st.button(
                            "Start Judge Evaluation", 
                            type="primary", 
                            key="sql_judge_reminder_button"
                        )
                        
                        if judge_reminder_button:
                            st.session_state.sql_judge_running = True
                            
                            # Run judge evaluation
                            def run_judge():
                                """Synchronous wrapper for the async judge evaluation function"""
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                try:
                                    return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
                                finally:
                                    loop.close()
                            
                            # Show a spinner during evaluation
                            with st.spinner("LLM Judge evaluating models..."):
                                run_judge()
                            
                            # Rerun to show the results
                            st.rerun()
            
            # Tab for Cost Estimation
            with tabs[tab_mapping["cost_estimation"]]:
                st.header("Cost Estimation")
                
                if st.session_state.sql_evaluation_results:
                    # Calculate cost based on actual completed evaluation
                    selected_models = list(st.session_state.sql_evaluation_results.keys())
                    
                    # Count number of queries processed per model
                    query_counts = {}
                    for model, eval_data in st.session_state.sql_evaluation_results.items():
                        query_counts[model] = len(eval_data["responses"])
                    
                    # Prepare model data for cost calculation
                    model_instances = [(model, 1) for model in selected_models]
                    
                    # Calculate cost for all iterations
                    total_iterations = sum(query_counts.values())
                    total_cost, cost_breakdown = calculate_cost(model_instances, total_iterations)
                    
                    # Display summary
                    st.subheader("Evaluation Cost Summary")
                    col1, col2 = st.columns(2)
                    col1.metric("Total Models", len(selected_models))
                    col2.metric("Total Queries", total_iterations)
                    
                    st.metric("Estimated Total Cost", f"${total_cost:.4f}")
                    
                    # Display cost breakdown table
                    st.subheader("Cost Breakdown by Model")
                    st.dataframe(cost_breakdown, use_container_width=True)
                    
                    # Create a bar chart of costs by model
                    cost_data = []
                    for model in selected_models:
                        row = cost_breakdown[cost_breakdown['Model'] == model]
                        if not row.empty:
                            cost_val = float(row['Total'].iloc[0].replace('$', ''))
                            cost_data.append({"Model": model, "Cost": cost_val})
                    
                    if cost_data:
                        cost_df = pd.DataFrame(cost_data)
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.bar(cost_df['Model'], cost_df['Cost'], color='green')
                        ax.set_xlabel('Model')
                        ax.set_ylabel('Cost ($)')
                        ax.set_title('Cost by Model')
                        ax.grid(True, linestyle='--', alpha=0.7)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                else:
                    # If no evaluation has been run, show cost estimator
                    st.subheader("Cost Estimator")
                    st.markdown("""
                    This tool helps you estimate the cost of running your SQL evaluation based on:
                    - Selected models
                    - Number of test queries
                    - Whether parameter tuning is enabled
                    """)
                    
                    # Get user inputs for estimation
                    estimation_models = st.multiselect(
                        "Select Models for Estimation",
                        ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"],
                        default=["gpt-4o-mini"] if "sql_models" not in st.session_state else st.session_state.sql_models
                    )
                    
                    num_queries = st.slider(
                        "Number of Test Queries",
                        min_value=10,
                        max_value=500,
                        value=50,
                        step=10,
                        help="Estimated number of queries to evaluate"
                    )
                    
                    enable_est_tuning = st.checkbox(
                        "Include Parameter Tuning",
                        value=True,
                        help="Parameter tuning runs additional evaluations with different temperatures"
                    )
                    
                    if enable_est_tuning:
                        num_trials = st.slider(
                            "Number of Tuning Trials",
                            min_value=3,
                            max_value=10,
                            value=5,
                            step=1,
                            help="Number of different parameter configurations to try"
                        )
                    else:
                        num_trials = 1
                        
                    # Calculate estimated cost
                    if estimation_models:
                        # Prepare model data for cost calculation
                        model_instances = [(model, 1) for model in estimation_models]
                        
                        # Basic evaluation cost (one run per model)
                        base_iterations = num_queries * len(estimation_models)
                        
                        # Add tuning iterations if enabled
                        tuning_iterations = 0
                        if enable_est_tuning and estimation_models:
                            # For each trial, we run a subset of queries with one model
                            tuning_iterations = num_queries * num_trials
                            
                        total_iterations = base_iterations + tuning_iterations
                        
                        # Calculate cost
                        total_cost, cost_breakdown = calculate_cost(model_instances, total_iterations)
                        
                        # Display results
                        cost_col1, cost_col2, cost_col3 = st.columns(3)
                        cost_col1.metric("Base Evaluation Queries", base_iterations)
                        cost_col2.metric("Tuning Queries", tuning_iterations)
                        cost_col3.metric("Total Queries", total_iterations)
                        
                        st.metric("Estimated Total Cost", f"${total_cost:.4f}")
                        
                        # Display cost breakdown
                        st.subheader("Cost Breakdown")
                        st.dataframe(cost_breakdown, use_container_width=True)
                        
                        # Show model pricing information
                        st.subheader("Model Pricing (per 1K tokens)")
                        pricing_data = []
                        for model, prices in MODEL_PRICING.items():
                            pricing_data.append({
                                "Model": model,
                                "Input Cost (per 1K tokens)": f"${prices['input']}",
                                "Output Cost (per 1K tokens)": f"${prices['output']}"
                            })
                        
                        st.dataframe(pd.DataFrame(pricing_data), use_container_width=True)
                        
                        # Display assumptions
                        st.subheader("Calculation Assumptions")
                        st.markdown(f"""
                        - Average input tokens per query: {AVG_INPUT_TOKENS}
                        - Average output tokens per query: {AVG_OUTPUT_TOKENS}
                        - Base evaluation: All models process all queries once
                        - Tuning: Best model processes queries {num_trials} times with different parameters
                        """)
                    else:
                        st.warning("Please select at least one model for cost estimation")
def text2sql_ui():
    import os
    import matplotlib.pyplot as plt
    import streamlit as st
    from llm_consortium.core.sql.sql_model_runner import SQLModelRunner
    from llm_consortium.core.sql.sql_judge import SQLJudge 
    from llm_consortium.config.models_sql import ModelConfig
    import asyncio
    import json
    import tempfile
    import pandas as pd
    import altair as alt
    import uuid
    from llm_consortium.utils.logging import logger
    from datetime import datetime
    from llm_consortium.utils.pricing import calculate_cost
    from llm_consortium.core.client_init import llm
    

    # Initialize judge
    judge = SQLJudge(llm)

    # Title and description
    st.title("SQL Model Evaluation and Tuning")
    st.markdown("""
    This tool evaluates different LLM models for SQL query generation and tunes parameters for the best performer.
    Upload your test dataset, select models to evaluate, and configure evaluation parameters.
    """)

    # Initialize session state for storing results between reruns
    if 'sql_evaluation_results' not in st.session_state:
        st.session_state.sql_evaluation_results = None
    if 'sql_best_model' not in st.session_state:
        st.session_state.sql_best_model = None
    if 'sql_best_params' not in st.session_state:
        st.session_state.sql_best_params = None
    if 'sql_tuning_results' not in st.session_state:
        st.session_state.sql_tuning_results = None
    if 'sql_running' not in st.session_state:
        st.session_state.sql_running = False
    if 'sql_progress' not in st.session_state:
        st.session_state.sql_progress = 0
    if 'sql_judge_results' not in st.session_state:
        st.session_state.sql_judge_results = None
    if 'sql_judge_running' not in st.session_state:
        st.session_state.sql_judge_running = False
    if 'sql_tuning_comparison' not in st.session_state:
        st.session_state.sql_tuning_comparison = None
    # Add state for sampled dataset
    if 'sql_sampled_dataset' not in st.session_state:
        st.session_state.sql_sampled_dataset = None

    def reset_results():
        st.session_state.sql_evaluation_results = None
        st.session_state.sql_best_model = None
        st.session_state.sql_best_params = None
        st.session_state.sql_tuning_results = None
        st.session_state.sql_running = False
        st.session_state.sql_progress = 0
        st.session_state.sql_judge_results = None
        st.session_state.sql_judge_running = False
        st.session_state.sql_tuning_comparison = None
        st.session_state.sql_sampled_dataset = None

    # Layout with two columns - config panel and results
    col1, col2 = st.columns([1, 3])

    # Configuration panel
    with col1:
        st.header("Configuration")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Test Dataset (CSV)", type=["csv"], key="sql_csv_upload")
        
        # Add dataset sampling option
        if uploaded_file is not None:
            # Read the uploaded file to get the number of rows
            df = pd.read_csv(uploaded_file)
            total_rows = len(df)
            
            st.subheader("Dataset Sampling")
            enable_sampling = st.checkbox("Enable Dataset Sampling", value=False, key="sql_enable_sampling")
            
            if enable_sampling:
                sample_size = st.slider(
                    "Sample Size", 
                    min_value=min(10, total_rows),
                    max_value=total_rows,
                    value=min(50, total_rows),
                    step=10,
                    help=f"Select number of samples to use from your dataset of {total_rows} records"
                )
                
                # Display percentage of total
                st.caption(f"Selected {sample_size} samples ({(sample_size/total_rows*100):.1f}% of total)")
            else:
                # If sampling is not enabled, use all rows
                sample_size = total_rows
            
            # Reset file position to beginning for later use
            uploaded_file.seek(0)
        
        # Model selection (with default models)
        default_models = ["gpt-4o-mini", "gpt-4o"]
        available_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        selected_models = st.multiselect(
            "Select Models to Evaluate", 
            available_models,
            default=default_models,
            key="sql_models"
        )
        
        # Judge model selection
        judge_models = ["gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"] 
        selected_judge = st.selectbox(
            "LLM Judge Model",
            judge_models,
            index=0,
            key="sql_judge_model"
        )
        
        # Base configuration
        st.subheader("Base Settings")
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.2, 0.05, key="sql_base_temp")
        
        # Tuning settings
        st.subheader("Parameter Tuning")
        enable_tuning = st.checkbox("Enable Parameter Tuning", value=True, key="sql_enable_tuning")
        
        min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.0, 0.05, key="sql_min_temp")
        max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.8, 0.05, key="sql_max_temp")
        num_trials = st.slider("Number of Trials", 3, 10, 5, key="sql_num_trials")
        
        # Judge settings
        st.subheader("Judge Settings")
        judge_criteria = st.multiselect(
            "Judge Criteria",
            [
                "Column name accuracy",
                "Table usage correctness",
                "Join quality",
                "Condition correctness",
                "Query structure",
                "SQL syntax correctness",
                "Query optimization",
                "Intent understanding"
            ],
            default=[
                "Column name accuracy",
                "Table usage correctness",
                "Query structure",
                "Intent understanding"
            ],
            key="sql_judge_criteria"
        )
        
        # Output settings
        st.subheader("Output Settings")
        output_dir = st.text_input("Output Directory", "results", key="sql_output_dir")
        save_results = st.checkbox("Save Results to File", value=True, key="sql_save_results")
        
        # Run button
        run_button = st.button("Run Evaluation", type="primary", key="sql_run_button", 
                            disabled=len(selected_models) == 0 or uploaded_file is None)

    # Main content area in the second column
    with col2:
        async def run_evaluation_async(config, csv_path, sampled_csv_path=None):
            """Run the evaluation and tuning pipeline asynchronously"""
            try:
                runner = SQLModelRunner()
                
                # Step 1: Evaluate all models
                st.session_state.sql_progress = 10
                evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluating models...")
                
                # Use the sampled dataset if available
                eval_csv_path = sampled_csv_path if sampled_csv_path else csv_path
                
                # Run evaluation
                evaluation_results = await runner.evaluate_models(config, eval_csv_path)
                st.session_state.sql_evaluation_results = evaluation_results
                st.session_state.sql_progress = 50
                evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluation complete, processing results...")
                
                # Calculate average latency for each model
                model_metrics = {}
                for model_name, eval_data in evaluation_results.items():
                    metrics = eval_data["metrics"]
                    responses = eval_data["responses"]
                    
                    # Calculate average latency (not directly provided in metrics)
                    latencies = [r["latency"] for r in responses]
                    avg_latency = sum(latencies) / len(latencies) if latencies else 0
                    
                    model_metrics[model_name] = {
                        "execution_match_rate": metrics["execution_match_rate"],
                        "exact_match_rate": metrics["exact_match_rate"],
                        "avg_latency": avg_latency
                    }
                
                # Find best model based on execution match rate, breaking ties with latency
                best_model = max(
                    model_metrics.items(),
                    key=lambda x: (x[1]["execution_match_rate"], -x[1]["avg_latency"])
                )[0]
                
                st.session_state.sql_best_model = best_model
                st.session_state.sql_progress = 60
                evaluation_progress.progress(st.session_state.sql_progress/100, f"Best model identified: {best_model}")
                
                # Step 3: Tune the best model if enabled
                if config.enable_tuning:
                    evaluation_progress.progress(st.session_state.sql_progress/100, f"Tuning {best_model}...")
                    
                    # Note: Removed the tuning_sample_size since we're using the global sampled dataset
                    best_params = await runner.tune_best_model(
                        best_model,
                        eval_csv_path,  # Use the already sampled dataset
                        config
                    )
                    st.session_state.sql_best_params = best_params
                    
                    # Capture the temperature trial results if available from the tuner
                    if hasattr(runner.hyperparameter_tuner, 'trial_results'):
                        st.session_state.sql_tuning_trials = runner.hyperparameter_tuner.trial_results
                    
                    st.session_state.sql_progress = 80
                    evaluation_progress.progress(st.session_state.sql_progress/100, "Tuning complete")
                
                    # Step 4: Optionally evaluate with tuned parameters
                    if config.run_final_evaluation:
                        evaluation_progress.progress(st.session_state.sql_progress/100, f"Final evaluation with tuned parameters...")
                        final_results = await runner.evaluate_with_params(
                            best_model, 
                            best_params, 
                            eval_csv_path  # Use the already sampled dataset
                        )
                        st.session_state.sql_tuning_results = final_results
                        
                # Save results if requested
                if save_results:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"sql_eval_results_{timestamp}.json")
                    
                    with open(output_file, "w") as f:
                        json.dump({
                            "model_evaluations": evaluation_results,
                            "best_model": best_model,
                            "best_params": best_params if config.enable_tuning else None,
                            "model_metrics": model_metrics,
                            "sample_size": sample_size if 'sample_size' in locals() else "full dataset"
                        }, f, indent=2, default=str)
                        
                st.session_state.sql_progress = 100
                evaluation_progress.progress(st.session_state.sql_progress/100, "Complete!")
                return model_metrics
                
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
                logger.error(f"Evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.sql_running = False
        
        # New function for evaluating using the judge
        async def run_judge_evaluation_async(judge_criteria):
            """Run the judge evaluation asynchronously"""
            try:
                    
                # Ensure criteria is always a list of strings
                if isinstance(judge_criteria, str):
                    judge_criteria = [judge_criteria]
                    
                if not isinstance(judge_criteria, list):
                    raise ValueError("Judge criteria must be a list")
                    
                # Validate each criterion is a string
                judge_criteria = [str(c) for c in judge_criteria]
                
                # Pass to judge
                judge_results = await judge.evaluate_model_outputs(
                    st.session_state.sql_evaluation_results,
                    criteria=judge_criteria
        )
                # if not st.session_state.sql_evaluation_results:
                #     st.error("No evaluation results available to judge")
                #     return None
                
                # # Evaluate all models using judge
                # judge_results = await judge.evaluate_model_outputs(
                #     st.session_state.sql_evaluation_results,
                #     criteria=judge_criteria
                # )
                
                # Store results
                st.session_state.sql_judge_results = judge_results
                
                # If we have before/after tuning results, compare those too
                if st.session_state.sql_best_model and st.session_state.sql_tuning_results:
                    best_model = st.session_state.sql_best_model
                    before_data = st.session_state.sql_evaluation_results[best_model]
                    after_data = st.session_state.sql_tuning_results
                    
                    tuning_comparison = await judge.before_after_tuning_comparison(
                        best_model,
                        before_data,
                        after_data
                    )
                    
                    st.session_state.sql_tuning_comparison = tuning_comparison
                
                return judge_results
                
            except Exception as e:
                st.error(f"Error during judge evaluation: {str(e)}")
                logger.error(f"Judge evaluation error: {str(e)}")
                return None
            finally:
                st.session_state.sql_judge_running = False
        
        if run_button and not st.session_state.sql_running:
            sampled_csv_path = None
            
            # Create sampled dataset if sampling is enabled
            if st.session_state.get('sql_enable_sampling', False) and uploaded_file is not None:
                # Read the full dataset
                df = pd.read_csv(uploaded_file)
                total_rows = len(df)
                
                # Check if sampling is actually needed
                if sample_size < total_rows:
                    # Sample the dataset
                    sampled_df = df.sample(n=sample_size, random_state=42)
                    
                    # Save the sampled dataset to a temporary file
                    sampled_csv_path = "temp_sampled_dataset.csv"
                    sampled_df.to_csv(sampled_csv_path, index=False)
                    st.session_state.sql_sampled_dataset = sampled_csv_path
                    
                    # Display info about sampling
                    st.info(f"Using {sample_size} samples out of {total_rows} records ({(sample_size/total_rows*100):.1f}%)")
            
            # Create config - IMPORTANT: Remove tuning_sample_size since we're using global sampling
            config = ModelConfig(
                models=selected_models,
                base_temperature=base_temperature,
                enable_tuning=enable_tuning,
                min_temp=min_temp,
                max_temp=max_temp,
                num_trials=num_trials,
                run_final_evaluation=True
                # Removed tuning_sample_size parameter
            )
            
            # Save uploaded file temporarily
            temp_csv = "temp_dataset.csv"
            with open(temp_csv, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Reset previous results
            reset_results()
            
            # Show progress bar
            evaluation_progress = st.progress(0, "Starting evaluation...")
            st.session_state.sql_running = True
            
            # Method 1: Using a synchronous wrapper function
            def run_evaluation(config, csv_path, sampled_csv_path):
                """Synchronous wrapper for the async evaluation function"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(run_evaluation_async(config, csv_path, sampled_csv_path))
                finally:
                    loop.close()
            
            # Run the evaluation in the current thread (this will block the UI until complete)
            run_evaluation(config, temp_csv, sampled_csv_path)
        
        # Display tabs for results (rest of your UI code remains mostly unchanged)
        if st.session_state.sql_running or st.session_state.sql_evaluation_results:
            tabs = st.tabs(["Evaluation Results", "Model Comparison", "Best Model", "Best Parameter", "Sample Queries", "LLM Judge", "Cost Estimation"])
            # Tab for Cost Estimation
            with tabs[6]:  # Assuming this is the seventh tab (index 6)
                st.header("Cost Estimation")
                
                if st.session_state.sql_evaluation_results:
                    # Calculate cost based on actual completed evaluation
                    selected_models = list(st.session_state.sql_evaluation_results.keys())
                    
                    # Count number of queries processed per model
                    query_counts = {}
                    for model, eval_data in st.session_state.sql_evaluation_results.items():
                        query_counts[model] = len(eval_data["responses"])
                    
                    # Prepare model data for cost calculation
                    model_instances = [(model, 1) for model in selected_models]
                    
                    # Calculate cost for all iterations
                    total_iterations = sum(query_counts.values())
                    total_cost, cost_breakdown = calculate_cost(model_instances, total_iterations)
                    
                    # Display summary
                    st.subheader("Evaluation Cost Summary")
                    col1, col2 = st.columns(2)
                    col1.metric("Total Models", len(selected_models))
                    col2.metric("Total Queries", total_iterations)
                    
                    st.metric("Estimated Total Cost", f"${total_cost:.4f}")
                    
                    # Display cost breakdown table
                    st.subheader("Cost Breakdown by Model")
                    st.dataframe(cost_breakdown, use_container_width=True)
                    
                    # Create a bar chart of costs by model
                    cost_data = []
                    for model in selected_models:
                        row = cost_breakdown[cost_breakdown['Model'] == model]
                        if not row.empty:
                            cost_val = float(row['Total'].iloc[0].replace('$', ''))
                            cost_data.append({"Model": model, "Cost": cost_val})
                    
                    if cost_data:
                        cost_df = pd.DataFrame(cost_data)
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.bar(cost_df['Model'], cost_df['Cost'], color='green')
                        ax.set_xlabel('Model')
                        ax.set_ylabel('Cost ($)')
                        ax.set_title('Cost by Model')
                        ax.grid(True, linestyle='--', alpha=0.7)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                else:
                    # If no evaluation has been run, show cost estimator
                    st.subheader("Cost Estimator")
                    st.markdown("""
                    This tool helps you estimate the cost of running your SQL evaluation based on:
                    - Selected models
                    - Number of test queries
                    - Whether parameter tuning is enabled
                    """)
                    
                    # Get user inputs for estimation
                    estimation_models = st.multiselect(
                        "Select Models for Estimation",
                        ["gpt-4o-mini", "gpt-3.5-turbo", "gemini-2", "o3-mini"],
                        default=["gpt-4o-mini"] if "sql_models" not in st.session_state else st.session_state.sql_models
                    )
                    
                    num_queries = st.slider(
                        "Number of Test Queries",
                        min_value=10,
                        max_value=500,
                        value=50,
                        step=10,
                        help="Estimated number of queries to evaluate"
                    )
                    
                    enable_est_tuning = st.checkbox(
                        "Include Parameter Tuning",
                        value=True,
                        help="Parameter tuning runs additional evaluations with different temperatures"
                    )
                    
                    if enable_est_tuning:
                        num_trials = st.slider(
                            "Number of Tuning Trials",
                            min_value=3,
                            max_value=10,
                            value=5,
                            step=1,
                            help="Number of different parameter configurations to try"
                        )
                    else:
                        num_trials = 1
                        
                    # Calculate estimated cost
                    if estimation_models:
                        # Prepare model data for cost calculation
                        model_instances = [(model, 1) for model in estimation_models]
                        
                        # Basic evaluation cost (one run per model)
                        base_iterations = num_queries * len(estimation_models)
                        
                        # Add tuning iterations if enabled
                        tuning_iterations = 0
                        if enable_est_tuning and estimation_models:
                            # For each trial, we run a subset of queries with one model
                            tuning_iterations = num_queries * num_trials
                            
                        total_iterations = base_iterations + tuning_iterations
                        
                        # Calculate cost
                        total_cost, cost_breakdown = calculate_cost(model_instances, total_iterations)
                        
                        # Display results
                        cost_col1, cost_col2, cost_col3 = st.columns(3)
                        cost_col1.metric("Base Evaluation Queries", base_iterations)
                        cost_col2.metric("Tuning Queries", tuning_iterations)
                        cost_col3.metric("Total Queries", total_iterations)
                        
                        st.metric("Estimated Total Cost", f"${total_cost:.4f}")
                        
                        # Display cost breakdown
                        st.subheader("Cost Breakdown")
                        st.dataframe(cost_breakdown, use_container_width=True)
                        
                        # Show model pricing information
                        st.subheader("Model Pricing (per 1K tokens)")
                        pricing_data = []
                        for model, prices in MODEL_PRICING.items():
                            pricing_data.append({
                                "Model": model,
                                "Input Cost (per 1K tokens)": f"${prices['input']}",
                                "Output Cost (per 1K tokens)": f"${prices['output']}"
                            })
                        
                        st.dataframe(pd.DataFrame(pricing_data), use_container_width=True)
                        
                        # Display assumptions
                        st.subheader("Calculation Assumptions")
                        st.markdown(f"""
                        - Average input tokens per query: {AVG_INPUT_TOKENS}
                        - Average output tokens per query: {AVG_OUTPUT_TOKENS}
                        - Base evaluation: All models process all queries once
                        - Tuning: Best model processes queries {num_trials} times with different parameters
                        """)
                    else:
                        st.warning("Please select at least one model for cost estimation")
            # Tab 1: Evaluation Results Table
            with tabs[0]:
                if st.session_state.sql_evaluation_results:
                    st.header("Model Evaluation Results")
                    
                    # Display sampling information if dataset was sampled
                    if st.session_state.sql_sampled_dataset:
                        st.info(f"Results based on sampled dataset ({sample_size} records)")
                    
                    # Add LLM Judge button
                    judge_col1, judge_col2 = st.columns([1, 3])
                    with judge_col1:
                        judge_button = st.button(
                            "Evaluate Using LLM Judge", 
                            type="primary", 
                            key="sql_judge_button",
                            disabled=st.session_state.sql_judge_running
                        )
                    
                    if judge_button and not st.session_state.sql_judge_running:
                        st.session_state.sql_judge_running = True
                        
                        # Run judge evaluation
                        def run_judge():
                            """Synchronous wrapper for the async judge evaluation function"""
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
                            finally:
                                loop.close()
                        
                        # Show a spinner during evaluation
                        with st.spinner("LLM Judge evaluating models..."):
                            run_judge()
                        
                        # Show completion message
                        st.success("LLM Judge evaluation complete! See the 'LLM Judge' tab for results.")
                    
                    # Create a DataFrame for metrics
                    metrics_data = []
                    
                    for model_name, eval_data in st.session_state.sql_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        responses = eval_data["responses"]
                        
                        # Calculate average latency
                        latencies = [r["latency"] for r in responses]
                        avg_latency = sum(latencies) / len(latencies) if latencies else 0
                        
                        metrics_data.append({
                            "Model": model_name,
                            "Execution Match (%)": round(metrics["execution_match_rate"], 2),
                            "Exact Match (%)": round(metrics["exact_match_rate"], 2),
                            "Avg. Latency (s)": round(avg_latency, 3),
                            "Samples": len(responses)
                        })
                    
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    if st.session_state.sql_best_model:
                        st.success(f"Best model: {st.session_state.sql_best_model}")
                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
                                
            # Tab 2: Model Comparison Charts
            with tabs[1]:
                if st.session_state.sql_evaluation_results:
                    st.header("Model Comparison")
                    
                    # Prepare data for visualization
                    models = []
                    exec_match = []
                    exact_match = []
                    latencies = []
                    
                    for model_name, eval_data in st.session_state.sql_evaluation_results.items():
                        metrics = eval_data["metrics"]
                        responses = eval_data["responses"]
                        
                        # Calculate average latency
                        avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
                        
                        models.append(model_name)
                        exec_match.append(metrics["execution_match_rate"])
                        exact_match.append(metrics["exact_match_rate"])
                        latencies.append(avg_latency)
                    
                    # Create charts
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Match rates chart
                    x = range(len(models))
                    width = 0.35
                    
                    ax1.bar([i - width/2 for i in x], exec_match, width, label='Execution Match (%)')
                    ax1.bar([i + width/2 for i in x], exact_match, width, label='Exact Match (%)')
                    ax1.set_xticks(x)
                    ax1.set_xticklabels(models, rotation=45, ha='right')
                    ax1.set_ylabel('Match Rate (%)')
                    ax1.set_title('Model Match Rates')
                    ax1.legend()
                    ax1.grid(True, linestyle='--', alpha=0.7)
                    
                    # Latency chart
                    ax2.bar(models, latencies, color='orange')
                    ax2.set_xticklabels(models, rotation=45, ha='right')
                    ax2.set_ylabel('Average Latency (s)')
                    ax2.set_title('Model Latency')
                    ax2.grid(True, linestyle='--', alpha=0.7)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
            
            # Tab 3: Best Model Details
            with tabs[2]:
                if st.session_state.sql_best_model:
                    st.header(f"Best Model: {st.session_state.sql_best_model}")
                    
                    best_model_data = st.session_state.sql_evaluation_results[st.session_state.sql_best_model]
                    metrics = best_model_data["metrics"]
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Execution Match Rate", f"{metrics['execution_match_rate']:.2f}%")
                    col2.metric("Exact Match Rate", f"{metrics['exact_match_rate']:.2f}%")
                    
                    
                    responses = best_model_data["responses"]
                    avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
                    col3.metric("Average Latency", f"{avg_latency:.3f}s")
                    
                    # Show confidence distribution
                    st.subheader("Confidence Distribution")
                    confidences = [r["confidence"] for r in responses]
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.hist(confidences, bins=10, alpha=0.7)
                    ax.set_xlabel('Confidence')
                    ax.set_ylabel('Count')
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
            
            # Tab 4: Parameter Tuning Results
            with tabs[3]:
                if st.session_state.sql_best_params:
                    st.header("Best Parameter")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Best Temperature", f"{st.session_state.sql_best_params['temperature']:.2f}")
                    col1.metric("Execution Match Rate", f"{st.session_state.sql_best_params['execution_match_rate']:.2f}%")
                    
                    # Add a section to show results for each temperature trial
                    st.subheader("Temperature Trial Results")
                    
                    # Check if we have the full tuning results available in session state
                    if 'sql_tuning_trials' in st.session_state and st.session_state.sql_tuning_trials:
                        # Create a dataframe to display all trial results
                        trials_data = []
                        for trial in st.session_state.sql_tuning_trials:
                            trials_data.append({
                                "Temperature": f"{trial['temperature']:.2f}",
                                "Execution Match Rate (%)": f"{trial['execution_match_rate']:.2f}%",
                                "Exact Match Rate (%)": f"{trial['exact_match_rate']:.2f}%" if 'exact_match_rate' in trial else "N/A"
                            })
                        
                        # Display as a table
                        st.table(pd.DataFrame(trials_data))
                        
                        # Also create a visualization for the temperature vs performance
                        st.subheader("Temperature vs. Performance")
                        
                        # Create chart data
                        chart_data = pd.DataFrame({
                            'Temperature': [trial['temperature'] for trial in st.session_state.sql_tuning_trials],
                            'Execution Match Rate (%)': [trial['execution_match_rate'] for trial in st.session_state.sql_tuning_trials],
                            'Exact Match Rate (%)': [trial.get('exact_match_rate', None) for trial in st.session_state.sql_tuning_trials]
                        })
                        
                        # Melt the dataframe for Altair
                        chart_data_melted = chart_data.melt(id_vars=['Temperature'], 
                                            value_vars=['Execution Match Rate (%)', 'Exact Match Rate (%)'],
                                            var_name='Metric', 
                                            value_name='Match Rate (%)')
                        
                        # Create a line chart with markers
                        chart = alt.Chart(chart_data_melted).mark_line(point=True).encode(
                            x=alt.X('Temperature:Q', title='Temperature'),
                            y=alt.Y('Match Rate (%):Q', title='Match Rate (%)'),
                            color='Metric:N',
                            tooltip=['Temperature','Metric', 'Match Rate (%)']
                        ).properties(
                            width=600,
                            height=300
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("Detailed temperature trial results are not available. Run evaluation again with the next version to see per-temperature performance.")
                    
                    # Show tuned vs untuned comparison if available
                    if st.session_state.sql_tuning_results:
                        st.subheader("Before vs After Tuning")
                        
                        before_metrics = st.session_state.sql_evaluation_results[st.session_state.sql_best_model]["metrics"]
                        best_trial = max(st.session_state.sql_tuning_trials, key=lambda x: x['execution_match_rate'])
                        
                        # Get the original temperature used before tuning
                        #original_temp = st.session_state.sql_original_temperature if hasattr(st.session_state, 'sql_original_temperature') else 1.0
                        original_temp = base_temperature
                        comp_data = {
                            "Metric": ["Temperature","Execution Match Rate", "Exact Match Rate"],
                            "Before Tuning": [
                                f"{original_temp:.2f}",
                                f"{before_metrics['execution_match_rate']:.2f}%",
                                f"{before_metrics['exact_match_rate']:.2f}%"
                            ],
                            "After Tuning": [
                                f"{best_trial['temperature']:.2f}",
                                f"{best_trial['execution_match_rate']:.2f}%",
                                f"{best_trial.get('exact_match_rate', 0.00):.2f}%"  # Default to 0.00 if not present
                            ]
                        }
                        
                        st.table(pd.DataFrame(comp_data))
                elif enable_tuning:
                    st.info("Parameter tuning in progress..." if st.session_state.sql_running else "Run evaluation to see tuning results")
                else:
                    st.info("Parameter tuning is disabled")

            # Tab 5: Sample Queries
            with tabs[4]:
                if st.session_state.sql_evaluation_results:
                    st.header("Sample Query Results")
                    
                    # Model selector for viewing samples
                    model_to_view = st.selectbox(
                        "Select model to view samples",
                        list(st.session_state.sql_evaluation_results.keys()),
                        key="sql_model_selector"
                    )
                    
                    if model_to_view:
                        responses = st.session_state.sql_evaluation_results[model_to_view]["responses"]
                        
                        # Filter options
                        filter_col1, filter_col2 = st.columns(2)
                        show_correct = filter_col1.checkbox("Show Correct Queries", value=True, key="sql_show_correct")
                        show_incorrect = filter_col2.checkbox("Show Incorrect Queries", value=True, key="sql_show_incorrect")
                        
                        filtered_responses = [
                            r for r in responses 
                            if (show_correct and r["execution_match"]) or (show_incorrect and not r["execution_match"])
                        ]
                        
                        # Show samples
                        if filtered_responses:
                            for i, response in enumerate(filtered_responses[:10]):  # Limit to 10 samples
                                with st.expander(
                                    f"Query {i+1}: {'✅' if response['execution_match'] else '❌'} " + 
                                    response["question"][:100] + ("..." if len(response["question"]) > 100 else "")
                                ):
                                    st.markdown("**Question:**")
                                    st.write(response["question"])
                                    
                                    st.markdown("**Generated SQL:**")
                                    st.code(response["generated_sql"], language="sql")
                                    
                                    st.markdown("**Gold SQL:**")
                                    st.code(response["gold_sql"], language="sql")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    col1.metric("Execution Match", "✅" if response["execution_match"] else "❌")
                                    col2.metric("Exact Match", "✅" if response["exact_match"] else "❌")
                                    col3.metric("Confidence", f"{response['confidence']:.2f}")
                        else:
                            st.info("No queries matching your filter criteria")
                else:
                    st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see sample queries")
            
            # Tab 6: LLM Judge Results (New)
            with tabs[5]:
                st.header("LLM Judge Evaluation")
                
                if st.session_state.sql_judge_running:
                    st.info("LLM judge evaluation in progress...")
                elif st.session_state.sql_judge_results:
                    # Display judge results
                    
                    # Model selection for viewing judge results
                    judge_model_to_view = st.selectbox(
                        "Select model to view judge evaluation",
                        list(st.session_state.sql_judge_results.keys()),
                        key="sql_judge_model_selector"
                    )
                    
                    if judge_model_to_view:
                        judge_result = st.session_state.sql_judge_results[judge_model_to_view]
                        
                        # Display any errors if present
                        if "error" in judge_result:
                            st.error(f"Judge evaluation error: {judge_result['error']}")
                        else:
                            st.subheader(f"Judge Evaluation for {judge_model_to_view}")
                            
                            # If the response has structured evaluation data
                            if "evaluation" in judge_result and isinstance(judge_result["evaluation"], dict):
                                evaluation = judge_result["evaluation"]
                                
                                # Display scores if available
                                if "criteria_scores" in evaluation:
                                    st.subheader("Criteria Scores")
                                    
                                    # Create score visualization
                                    criteria_scores = evaluation["criteria_scores"]
                                    score_data = []
                                    for criterion, data in criteria_scores.items():
                                        score_data.append({
                                            "Criterion": criterion,
                                            "Score": data["score"],
                                            "Comments": data["comments"]
                                        })
                                    
                                    # Display as a table
                                    st.table(pd.DataFrame(score_data))
                                    
                                    # Create radar chart for scores
                                    labels = [item["Criterion"] for item in score_data]
                                    scores = [item["Score"] for item in score_data]
                                    
                                    fig = plt.figure(figsize=(8, 8))
                                    ax = fig.add_subplot(111, polar=True)
                                    
                                    # Set the angles for each criterion
                                    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
                                    angles += angles[:1]  # Close the loop
                                    
                                    # Add the scores
                                    scores += scores[:1]  # Close the loop
                                    
                                    # Plot
                                    ax.plot(angles, scores, linewidth=2, linestyle='solid')
                                    ax.fill(angles, scores, alpha=0.25)
                                    
                                    # Set labels and ticks
                                    ax.set_xticks(angles[:-1])
                                    ax.set_xticklabels(labels)
                                    ax.set_yticks([2, 4, 6, 8, 10])
                                    ax.set_yticklabels(['2', '4', '6', '8', '10'])
                                    ax.set_ylim(0, 10)
                                    
                                    plt.title(f'Judge Scores for {judge_model_to_view}')
                                    st.pyplot(fig)
                                
                                # Display strengths and weaknesses
                                if "strengths" in evaluation:
                                    st.subheader("Strengths")
                                    for strength in evaluation["strengths"]:
                                        st.markdown(f"- {strength}")
                                
                                if "weaknesses" in evaluation:
                                    st.subheader("Weaknesses")
                                    for weakness in evaluation["weaknesses"]:
                                        st.markdown(f"- {weakness}")
                                
                                # Display summary and final score
                                if "summary" in evaluation:
                                    st.subheader("Summary")
                                    st.write(evaluation["summary"])
                                
                                if "final_score" in evaluation:
                                    st.metric("Final Score", f"{evaluation['final_score']}/100")
                            else:
                                # Display raw evaluation text
                                st.markdown("### Judge Evaluation")
                                st.write(judge_result.get("raw_response", "No detailed evaluation available"))
                    
                    # Show tuning comparison if available
                    if st.session_state.sql_tuning_comparison:
                        st.markdown("---")
                        st.header("Before vs After Tuning Analysis")
                        
                        tuning_comp = st.session_state.sql_tuning_comparison
                        model_name = tuning_comp.get("model_name")
                        
                        if "error" in tuning_comp:
                            st.error(f"Tuning comparison error: {tuning_comp['error']}")
                        else:
                            st.subheader(f"Tuning Impact Analysis for {model_name}")
                            
                            # Display the analysis
                            st.markdown(tuning_comp.get("tuning_impact_analysis", "No tuning analysis available"))
                
                else:
                    # Show instructions for using the judge
                    st.info("""
                    To get an LLM judge evaluation of your models:
                    1. Complete a model evaluation run
                    2. Go to the "Evaluation Results" tab
                    3. Click the "Evaluate Using LLM Judge" button
                    
                    The judge will evaluate each model's SQL generation quality and provide detailed feedback.
                    """)
                    
                    # If we have evaluation results but no judge results, show reminder
                    if st.session_state.sql_evaluation_results:
                        st.markdown("#### Ready for Judge Evaluation")
                        st.markdown("You have evaluation results ready to be analyzed by the LLM judge.")
                        judge_reminder_button = st.button(
                            "Start Judge Evaluation", 
                            type="primary", 
                            key="sql_judge_reminder_button"
                        )
                        
                        if judge_reminder_button:
                            st.session_state.sql_judge_running = True
                            
                            # Run judge evaluation
                            def run_judge():
                                """Synchronous wrapper for the async judge evaluation function"""
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                try:
                                    return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
                                finally:
                                    loop.close()
                            
                            # Show a spinner during evaluation
                            with st.spinner("LLM Judge evaluating models..."):
                                run_judge()
                            
                            # Rerun to show the results
                            st.rerun()
# def classification_ui():
#     import os
#     import matplotlib.pyplot as plt
#     import streamlit as st
#     from llm_consortium.core.classification.classification_model_runner import ClassificationModelRunner
#     from llm_consortium.core.classification.classification_judge import ClassificationJudge  # Assuming you have a Judge class
#     from llm_consortium.config.models_classification import ModelConfig
#     import asyncio
#     import json
#     import tempfile
#     import numpy as np
#     import pandas as pd
#     import altair as alt
#     import nest_asyncio
#     nest_asyncio.apply()
#     import uuid
#     from llm_consortium.utils.logging import logger
#     from datetime import datetime
#     from llm_consortium.utils.pricing import calculate_cost
#     from llm_consortium.core.client_init import llm

#     # Initialize judge (assuming you have a ClassificationJudge similar to SQLJudge)
#     judge = ClassificationJudge(llm)

#     # Title and description
#     st.title("Classification Model Evaluation and Tuning")
#     st.markdown("""
#     This tool evaluates different LLM models for classification tasks and tunes parameters for the best performer.
#     Upload your test dataset, select models to evaluate, and configure evaluation parameters.
#     """)

#     # Initialize session state for storing results between reruns
#     if 'classification_evaluation_results' not in st.session_state:
#         st.session_state.classification_evaluation_results = None
#     if 'classification_best_model' not in st.session_state:
#         st.session_state.classification_best_model = None
#     if 'classification_best_params' not in st.session_state:
#         st.session_state.classification_best_params = None
#     if 'classification_tuning_results' not in st.session_state:
#         st.session_state.classification_tuning_results = None
#     if 'classification_running' not in st.session_state:
#         st.session_state.classification_running = False
#     if 'classification_progress' not in st.session_state:
#         st.session_state.classification_progress = 0
#     if 'classification_judge_results' not in st.session_state:
#         st.session_state.classification_judge_results = None
#     if 'classification_judge_running' not in st.session_state:
#         st.session_state.classification_judge_running = False
#     if 'classification_tuning_comparison' not in st.session_state:
#         st.session_state.classification_tuning_comparison = None
#     # Add state for sampled dataset
#     if 'classification_sampled_dataset' not in st.session_state:
#         st.session_state.classification_sampled_dataset = None
#     # Add state for class list
#     if 'classification_valid_classes' not in st.session_state:
#         st.session_state.classification_valid_classes = []

#     def reset_results():
#         st.session_state.classification_evaluation_results = None
#         st.session_state.classification_best_model = None
#         st.session_state.classification_best_params = None
#         st.session_state.classification_tuning_results = None
#         st.session_state.classification_running = False
#         st.session_state.classification_progress = 0
#         st.session_state.classification_judge_results = None
#         st.session_state.classification_judge_running = False
#         st.session_state.classification_tuning_comparison = None
#         st.session_state.classification_sampled_dataset = None
#         # Don't reset classes, as they might be inferred from the dataset

#     # Layout with two columns - config panel and results
#     col1, col2 = st.columns([1, 3])

#     # Configuration panel
#     with col1:
#         st.header("Configuration")

#         # File uploader
#         uploaded_file = st.file_uploader("Upload Test Dataset (CSV)", type=["csv"], key="classification_csv_upload")

#         # Class configuration
#         st.subheader("Class Configuration")

#         class_inference_method = st.radio(
#             "Classification Classes",
#             ["Infer from dataset", "Specify manually"],
#             key="classification_class_method"
#         )

#         valid_classes = []

#         df = None
#         if uploaded_file is not None:
#             try:
#                 uploaded_file.seek(0)
#                 df = pd.read_csv(uploaded_file)

#                 if df.empty:
#                     st.error("The uploaded CSV file is empty.")
#                     df = None
#             except pd.errors.EmptyDataError:
#                 st.error("The uploaded CSV file could not be read (EmptyDataError).")
#             except Exception as e:
#                 st.error(f"Error reading CSV: {e}")
#                 df = None

#         # Handle class selection
#         if class_inference_method == "Specify manually":
#             class_input = st.text_area(
#                 "Enter valid classes (one per line)",
#                 help="Each line will be treated as a separate class",
#                 key="classification_class_input"
#             )
#             if class_input:
#                 valid_classes = [cls.strip() for cls in class_input.split("\n") if cls.strip()]
#                 st.session_state.classification_valid_classes = valid_classes
#         else:
#             if df is not None:
#                 if "ground_truth" in df.columns:
#                     valid_classes = sorted(df["ground_truth"].unique().tolist())
#                     st.session_state.classification_valid_classes = valid_classes
#                     st.write(f"Detected {len(valid_classes)} classes: {', '.join(valid_classes)}")
#                 else:
#                     st.error("CSV must contain a 'ground_truth' column for class inference")

#         # Dataset sampling
#         if df is not None:
#             total_rows = len(df)
#             st.subheader("Dataset Sampling")

#             enable_sampling = st.checkbox("Enable Dataset Sampling", value=False, key="classification_enable_sampling")

#             if enable_sampling:
#                 sample_size = st.slider(
#                     "Sample Size",
#                     min_value=min(10, total_rows),
#                     max_value=total_rows,
#                     value=min(50, total_rows),
#                     step=10,
#                     help=f"Select number of samples to use from your dataset of {total_rows} records"
#                 )
#                 st.caption(f"Selected {sample_size} samples ({(sample_size/total_rows*100):.1f}% of total)")
#             else:
#                 sample_size = total_rows
        
#         # Model selection (with default models)
#         default_models = ["gpt-4o-mini", "gpt-4o"]
#         available_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
#         selected_models = st.multiselect(
#             "Select Models to Evaluate", 
#             available_models,
#             default=default_models,
#             key="classification_models"
#         )
        
#         # Judge model selection
#         judge_models = ["gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"] 
#         selected_judge = st.selectbox(
#             "LLM Judge Model",
#             judge_models,
#             index=0,
#             key="classification_judge_model"
#         )
        
#         # Base configuration
#         st.subheader("Base Settings")
#         base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.2, 0.05, key="classification_base_temp")
        
#         # Tuning settings
#         st.subheader("Parameter Tuning")
#         enable_tuning = st.checkbox("Enable Parameter Tuning", value=True, key="classification_enable_tuning")
        
#         min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.0, 0.05, key="classification_min_temp")
#         max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.8, 0.05, key="classification_max_temp")
#         num_trials = st.slider("Number of Trials", 3, 10, 5, key="classification_num_trials")
        
#         # Judge settings
#         st.subheader("Judge Settings")
#         judge_criteria = st.multiselect(
#             "Judge Criteria",
#             [
#                 "Class relevance accuracy",
#                 "Reasoning quality",
#                 "Confidence calibration",
#                 "Edge case handling",
#                 "Classification robustness",
#                 "Intent understanding"
#             ],
#             default=[
#                 "Class relevance accuracy",
#                 "Reasoning quality",
#                 "Intent understanding"
#             ],
#             key="classification_judge_criteria"
#         )
        
#         # Output settings
#         st.subheader("Output Settings")
#         output_dir = st.text_input("Output Directory", "results", key="classification_output_dir")
#         save_results = st.checkbox("Save Results to File", value=True, key="classification_save_results")
        
#         # Run button
#         run_button = st.button(
#             "Run Evaluation", 
#             type="primary", 
#             key="classification_run_button", 
#             disabled=len(selected_models) == 0 or 
#                     uploaded_file is None or 
#                     len(valid_classes) == 0
#         )

#     # Main content area in the second column
#     with col2:
#             async def run_evaluation_async(config, csv_path, sampled_csv_path=None, valid_classes=None):
#                 """Run the evaluation and tuning pipeline asynchronously"""
#                 try:
#                     runner = ClassificationModelRunner()
                    
#                     # Step 1: Evaluate all models
#                     st.session_state.classification_progress = 10
#                     evaluation_progress.progress(st.session_state.classification_progress/100, "Evaluating models...")
                    
#                     # Use the sampled dataset if available
#                     eval_csv_path = sampled_csv_path if sampled_csv_path else csv_path
                    
#                     # Run evaluation
#                     evaluation_results = await runner.evaluate_models(config, eval_csv_path, valid_classes)
#                     st.session_state.classification_evaluation_results = evaluation_results
#                     st.session_state.classification_progress = 50
#                     evaluation_progress.progress(st.session_state.classification_progress/100, "Evaluation complete, processing results...")
                    
#                     # Find best model
#                     best_model = runner.find_best_model(evaluation_results)
                    
#                     st.session_state.classification_best_model = best_model
#                     st.session_state.classification_progress = 60
#                     evaluation_progress.progress(st.session_state.classification_progress/100, f"Best model identified: {best_model}")
                    
#                     # Step 3: Tune the best model if enabled
#                     if config.enable_tuning:
#                         evaluation_progress.progress(st.session_state.classification_progress/100, f"Tuning {best_model}...")
                        
#                         best_params = await runner.tune_best_model(
#                             best_model,
#                             eval_csv_path,
#                             config,
#                             valid_classes
#                         )
#                         st.session_state.classification_best_params = best_params
                        
#                         # Capture the temperature trial results if available from the tuner
#                         if hasattr(runner.hyperparameter_tuner, 'trial_results'):
#                             st.session_state.classification_tuning_trials = runner.hyperparameter_tuner.trial_results
                        
#                         st.session_state.classification_progress = 80
#                         evaluation_progress.progress(st.session_state.classification_progress/100, "Tuning complete")
                    
#                         # Step 4: Optionally evaluate with tuned parameters
#                         if config.run_final_evaluation:
#                             evaluation_progress.progress(st.session_state.classification_progress/100, f"Final evaluation with tuned parameters...")
#                             final_results = await runner.evaluate_with_params(
#                                 best_model, 
#                                 best_params, 
#                                 eval_csv_path,
#                                 valid_classes
#                             )
#                             st.session_state.classification_tuning_results = final_results
                            
#                     # Save results if requested
#                     if save_results:
#                         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                         os.makedirs(output_dir, exist_ok=True)
#                         output_file = os.path.join(output_dir, f"classification_eval_results_{timestamp}.json")
                        
#                         with open(output_file, "w") as f:
#                             json.dump({
#                                 "model_evaluations": evaluation_results,
#                                 "best_model": best_model,
#                                 "best_params": best_params if config.enable_tuning else None,
#                                 "valid_classes": valid_classes,
#                                 "sample_size": sample_size if 'sample_size' in locals() else "full dataset"
#                             }, f, indent=2, default=str)
                            
#                     st.session_state.classification_progress = 100
#                     evaluation_progress.progress(st.session_state.classification_progress/100, "Complete!")
                    
#                     # Replace the problematic loop with this version
#                     model_metrics = {}
#                     for model_name, eval_data in evaluation_results.items():
#                         # Validate evaluation data structure
#                         if not isinstance(eval_data, dict):
#                             print(f"⚠️ Invalid data format for {model_name}, skipping...")
#                             continue

#                         # Safely get metrics and responses with defaults
#                         metrics = eval_data.get("metrics", {})
#                         responses = eval_data.get("responses", [])

#                         # Validate metrics content
#                         if not metrics:
#                             print(f"⚠️ Missing metrics for {model_name}, using defaults")
#                             metrics = {
#                                 "accuracy": 0,
#                                 "f1": 0,
#                                 "error": "No metrics available"
#                             }

#                         # Safe latency calculation
#                         try:
#                             latencies = [r.get("latency", 0) for r in responses]
#                             avg_latency = sum(latencies)/len(latencies) if latencies else 0
#                         except Exception as e:
#                             print(f"⏱️ Latency calculation failed for {model_name}: {str(e)}")
#                             avg_latency = 0

#                         # Populate metrics with validation
#                         model_metrics[model_name] = {
#                             "accuracy": metrics.get("accuracy", 0),
#                             "f1": metrics.get("f1", 0),
#                             "avg_latency": avg_latency,
#                             "has_errors": "error" in metrics
#                         }
                    
#                 except Exception as e:
#                     st.error(f"Error during evaluation: {str(e)}")
#                     logger.error(f"Evaluation error: {str(e)}")
#                     return None
#                 finally:
#                     st.session_state.classification_running = False
            
#             # New function for evaluating using the judge
#             async def run_judge_evaluation_async(judge_criteria):
#                 """Run the judge evaluation asynchronously"""
#                 try:
#                     if not st.session_state.classification_evaluation_results:
#                         st.error("No evaluation results available to judge")
#                         return None
                    
#                     # Evaluate all models using judge
#                     judge_results = await judge.evaluate_model_outputs(
#                         st.session_state.classification_evaluation_results,
#                         criteria=judge_criteria
#                     )
                    
#                     # Store results
#                     st.session_state.classification_judge_results = judge_results
                    
#                     # If we have before/after tuning results, compare those too
#                     if st.session_state.classification_best_model and st.session_state.classification_tuning_results:
#                         best_model = st.session_state.classification_best_model
#                         before_data = st.session_state.classification_evaluation_results[best_model]
#                         after_data = st.session_state.classification_tuning_results
                        
#                         tuning_comparison = await judge.before_after_tuning_comparison(
#                             best_model,
#                             before_data,
#                             after_data
#                         )
                        
#                         st.session_state.classification_tuning_comparison = tuning_comparison
                    
#                     return judge_results
                    
#                 except Exception as e:
#                     st.error(f"Error during judge evaluation: {str(e)}")
#                     logger.error(f"Judge evaluation error: {str(e)}")
#                     return None
#                 finally:
#                     st.session_state.classification_judge_running = False
            
#             if run_button and not st.session_state.classification_running:
#                 sampled_csv_path = None
                
#                 # Create sampled dataset if sampling is enabled
#                 if st.session_state.get('classification_enable_sampling', False) and uploaded_file is not None:
#                     # Read the full dataset
#                     df = pd.read_csv(uploaded_file)
#                     total_rows = len(df)
                    
#                     # Check if sampling is actually needed
#                     if sample_size < total_rows:
#                         # Sample the dataset
#                         sampled_df = df.sample(n=sample_size, random_state=42)
                        
#                         # Save the sampled dataset to a temporary file
#                         sampled_csv_path = "temp_classification_sampled_dataset.csv"
#                         sampled_df.to_csv(sampled_csv_path, index=False)
#                         st.session_state.classification_sampled_dataset = sampled_csv_path
                        
#                         # Display info about sampling
#                         st.info(f"Using {sample_size} samples out of {total_rows} records ({(sample_size/total_rows*100):.1f}%)")
                
#                 # Get the valid classes
#                 if not valid_classes and st.session_state.classification_valid_classes:
#                     valid_classes = st.session_state.classification_valid_classes
                
#                 # Create config
#                 config = ModelConfig(
#                     models=selected_models,
#                     base_temperature=base_temperature,
#                     enable_tuning=enable_tuning,
#                     min_temp=min_temp,
#                     max_temp=max_temp,
#                     num_trials=num_trials,
#                     run_final_evaluation=True
#                 )
                
#                 # Save uploaded file temporarily
#                 temp_csv = "temp_classification_dataset.csv"
#                 with open(temp_csv, "wb") as f:
#                     f.write(uploaded_file.getvalue())
                
#                 # Reset previous results
#                 reset_results()
                
#                 # Show progress bar
#                 evaluation_progress = st.progress(0, "Starting evaluation...")
                
                
#                 # Replace threading with direct async execution
#                 async def execute_evaluation():
#                     try:
#                         return await run_evaluation_async(config, temp_csv, sampled_csv_path, valid_classes)
#                     except Exception as e:
#                         st.error(f"Evaluation failed: {str(e)}")
#                         logger.error(f"Evaluation pipeline failed: {str(e)}")
#                         return None
#                     finally:
#                         # Clean up temporary files
#                         if os.path.exists(temp_csv):
#                             os.remove(temp_csv)
#                         if sampled_csv_path and os.path.exists(sampled_csv_path):
#                             os.remove(sampled_csv_path)

#                 # Run the async function directly
#                 st.session_state.classification_running = True
#                 st.session_state.classification_evaluation_results = asyncio.run(execute_evaluation())
#                 st.session_state.classification_running = False
                
    
#             # Display tabs for results
#                 if st.session_state.classification_running or st.session_state.classification_evaluation_results:
#                     tabs = st.tabs([
#                         "Evaluation Results", 
#                         "Model Comparison", 
#                         "Best Model", 
#                         "Best Parameter", 
#                         "Sample Classifications", 
#                         "Confusion Matrix", 
#                         "LLM Judge"
#                     ])
#                 # Tab 1: Evaluation Results Table
#                     with tabs[0]:
#                         if st.session_state.classification_evaluation_results:
#                             st.header("Model Evaluation Results")
                            
#                             # Display sampling information if dataset was sampled
#                             if st.session_state.classification_sampled_dataset:
#                                 st.info(f"Results based on sampled dataset ({sample_size} records)")
                            
#                             # Add LLM Judge button
#                             judge_col1, judge_col2 = st.columns([1, 3])
#                             with judge_col1:
#                                 judge_button = st.button(
#                                     "Evaluate Using LLM Judge", 
#                                     type="primary", 
#                                     key="classification_judge_button",
#                                     disabled=st.session_state.classification_judge_running
#                                 )
                            
#                             if judge_button and not st.session_state.classification_judge_running:
#                                 st.session_state.classification_judge_running = True
                                
#                                 # Run judge evaluation
#                                 def run_judge():
#                                     """Synchronous wrapper for the async judge evaluation function"""
#                                     loop = asyncio.new_event_loop()
#                                     asyncio.set_event_loop(loop)
#                                     try:
#                                         return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
#                                     finally:
#                                         loop.close()
                                
#                                 # Show a spinner during evaluation
#                                 with st.spinner("LLM Judge evaluating models..."):
#                                     run_judge()
                                
#                                 # Show completion message
#                                 st.success("LLM Judge evaluation complete! See the 'LLM Judge' tab for results.")
                            
#                             # Create a DataFrame for metrics
#                             metrics_data = []
                            
#                             for model_name, eval_data in st.session_state.classification_evaluation_results.items():
#                                 metrics = eval_data["metrics"]
#                                 responses = eval_data["responses"]
                                
#                                 # Calculate average latency
#                                 latencies = [r["latency"] for r in responses]
#                                 avg_latency = sum(latencies) / len(latencies) if latencies else 0
                                
#                                 metrics_data.append({
#                                     "Model": model_name,
#                                     "Accuracy (%)": round(metrics["accuracy"] * 100, 2),
#                                     "F1 Score": round(metrics["f1"], 2),
#                                     "Precision": round(metrics.get("precision", 0), 2),
#                                     "Recall": round(metrics.get("recall", 0), 2),
#                                     "Avg. Latency (s)": round(avg_latency, 3),
#                                     "Samples": len(responses)
#                                 })
                            
#                             metrics_df = pd.DataFrame(metrics_data)
#                             st.dataframe(metrics_df, use_container_width=True)
                            
#                             if st.session_state.classification_best_model:
#                                 st.success(f"Best model: {st.session_state.classification_best_model}")
#                         else:
#                             st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
                                        
#                     # Tab 2: Model Comparison Charts
#                     with tabs[1]:
#                         if st.session_state.classification_evaluation_results:
#                             st.header("Model Comparison")
                            
#                             # Prepare data for visualization
#                             models = []
#                             accuracies = []
#                             f1_scores = []
#                             latencies = []
                            
#                             for model_name, eval_data in st.session_state.classification_evaluation_results.items():
#                                 metrics = eval_data["metrics"]
#                                 responses = eval_data["responses"]
                                
#                                 # Calculate average latency
#                                 avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
                                
#                                 models.append(model_name)
#                                 accuracies.append(metrics["accuracy"] * 100)  # Convert to percentage
#                                 f1_scores.append(metrics["f1"])
#                                 latencies.append(avg_latency)
                            
#                             # Create charts
#                             fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                            
#                             # Performance metrics chart
#                             x = range(len(models))
#                             width = 0.35
                            
#                             ax1.bar([i - width/2 for i in x], accuracies, width, label='Accuracy (%)')
#                             ax1.bar([i + width/2 for i in x], f1_scores, width, label='F1 Score')
#                             ax1.set_xticks(x)
#                             ax1.set_xticklabels(models, rotation=45, ha='right')
#                             ax1.set_ylabel('Score')
#                             ax1.set_title('Model Performance Metrics')
#                             ax1.legend()
#                             ax1.grid(True, linestyle='--', alpha=0.7)
                            
#                             # Latency chart
#                             ax2.bar(models, latencies, color='orange')
#                             ax2.set_xticklabels(models, rotation=45, ha='right')
#                             ax2.set_ylabel('Average Latency (s)')
#                             ax2.set_title('Model Latency')
#                             ax2.grid(True, linestyle='--', alpha=0.7)
                            
#                             plt.tight_layout()
#                             st.pyplot(fig)
                            
#                             # Create an Altair chart for metrics comparison
#                             chart_data = pd.DataFrame({
#                                 'Model': models,
#                                 'Accuracy': accuracies,
#                                 'F1 Score': f1_scores, 
#                                 'Latency': latencies
#                             })
                            
#                             # Melt the dataframe for Altair
#                             metrics_chart_data = chart_data.melt(
#                                 id_vars=['Model'],
#                                 value_vars=['Accuracy', 'F1 Score'],
#                                 var_name='Metric', 
#                                 value_name='Score'
#                             )
                            
#                             # Create a grouped bar chart
#                             metrics_chart = alt.Chart(metrics_chart_data).mark_bar().encode(
#                                 x=alt.X('Model:N', title='Model'),
#                                 y=alt.Y('Score:Q', title='Score'),
#                                 color='Metric:N',
#                                 column='Metric:N'
#                             ).properties(
#                                 width=250
#                             )
                            
#                             st.altair_chart(metrics_chart, use_container_width=True)
#                         else:
#                             st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
                    
#                     # Tab 3: Best Model Details
#                     with tabs[2]:
#                         if st.session_state.classification_best_model:
#                             st.header(f"Best Model: {st.session_state.classification_best_model}")
                            
#                             best_model_data = st.session_state.classification_evaluation_results[st.session_state.classification_best_model]
#                             metrics = best_model_data["metrics"]
                            
#                             col1, col2, col3, col4 = st.columns(4)
#                             col1.metric("Accuracy", f"{metrics['accuracy'] * 100:.2f}%")
#                             col2.metric("F1 Score", f"{metrics['f1']:.2f}")
#                             col3.metric("Precision", f"{metrics.get('precision', 0):.2f}")
#                             col4.metric("Recall", f"{metrics.get('recall', 0):.2f}")
                            
#                             responses = best_model_data["responses"]
#                             avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
#                             st.metric("Average Latency", f"{avg_latency:.3f}s")
                            
#                             # Show confidence distribution
#                             st.subheader("Confidence Distribution")
#                             confidences = [r["confidence"] for r in responses]
                            
#                             fig, ax = plt.subplots(figsize=(10, 5))
#                             ax.hist(confidences, bins=10, alpha=0.7)
#                             ax.set_xlabel('Confidence')
#                             ax.set_ylabel('Count')
#                             ax.grid(True, linestyle='--', alpha=0.7)
#                             st.pyplot(fig)
                            
#                             # Show accuracy by class
#                             st.subheader("Accuracy by Class")
                            
#                             # Calculate metrics per class
#                             class_metrics = {}
#                             for response in responses:
#                                 cls = response["ground_truth"]
#                                 if cls not in class_metrics:
#                                     class_metrics[cls] = {"total": 0, "correct": 0}
                                
#                                 class_metrics[cls]["total"] += 1
#                                 if response["correct"]:
#                                     class_metrics[cls]["correct"] += 1
                            
#                             # Calculate accuracy per class
#                             class_accuracy = {
#                                 cls: data["correct"] / data["total"] if data["total"] > 0 else 0 
#                                 for cls, data in class_metrics.items()
#                             }
                            
#                             # Create a bar chart
#                             fig, ax = plt.subplots(figsize=(10, 5))
#                             classes = list(class_accuracy.keys())
#                             accuracies = [class_accuracy[cls] * 100 for cls in classes]
                            
#                             ax.bar(classes, accuracies)
#                             ax.set_xlabel('Class')
#                             ax.set_ylabel('Accuracy (%)')
#                             ax.set_ylim(0, 100)
#                             ax.grid(True, linestyle='--', alpha=0.7)
#                             plt.xticks(rotation=45, ha='right')
#                             plt.tight_layout()
                            
#                             st.pyplot(fig)
#                         else:
#                             st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see results")
                    
#                     # Tab 4: Parameter Tuning Results
#                     with tabs[3]:
#                         if st.session_state.classification_best_params:
#                             st.header("Best Parameter")
                            
#                             col1, col2, col3 = st.columns(3)
#                             col1.metric("Best Temperature", f"{st.session_state.classification_best_params['temperature']:.2f}")
#                             col2.metric("Accuracy", f"{st.session_state.classification_best_params['accuracy'] * 100:.2f}%")
#                             col3.metric("F1 Score", f"{st.session_state.classification_best_params['f1']:.2f}")
                            
#                             # Add a section to show results for each temperature trial
#                             st.subheader("Temperature Trial Results")
                            
#                             # Check if we have the full tuning results available in session state
#                             if 'classification_tuning_trials' in st.session_state and st.session_state.classification_tuning_trials:
#                                 # Create a dataframe to display all trial results
#                                 trials_data = []
#                                 for trial in st.session_state.classification_tuning_trials:
#                                     trials_data.append({
#                                         "Temperature": f"{trial['temperature']:.2f}",
#                                         "Accuracy (%)": f"{trial['accuracy'] * 100:.2f}%",
#                                         "F1 Score": f"{trial['f1']:.2f}",
#                                         "Combined Score": f"{trial['combined_score']:.2f}"
#                                     })
                                
#                                 # Display as a table
#                                 st.table(pd.DataFrame(trials_data))
                                
#                                 # Also create a visualization for the temperature vs performance
#                                 st.subheader("Temperature vs. Performance")
                                
#                                 # Create chart data
#                                 chart_data = pd.DataFrame({
#                                     'Temperature': [trial['temperature'] for trial in st.session_state.classification_tuning_trials],
#                                     'Accuracy': [trial['accuracy'] * 100 for trial in st.session_state.classification_tuning_trials],
#                                     'F1 Score': [trial['f1'] for trial in st.session_state.classification_tuning_trials],
#                                     'Combined Score': [trial['combined_score'] for trial in st.session_state.classification_tuning_trials]
#                                 })
                                
#                                 # Melt the dataframe for Altair
#                                 chart_data_melted = chart_data.melt(
#                                     id_vars=['Temperature'], 
#                                     value_vars=['Accuracy', 'F1 Score', 'Combined Score'],
#                                     var_name='Metric', 
#                                     value_name='Score'
#                                 )
                                
#                                 # Create a line chart with markers
#                                 chart = alt.Chart(chart_data_melted).mark_line(point=True).encode(
#                                     x=alt.X('Temperature:Q', title='Temperature'),
#                                     y=alt.Y('Score:Q', title='Score'),
#                                     color='Metric:N',
#                                     tooltip=['Temperature','Metric', 'Score']
#                                 ).properties(
#                                     width=600,
#                                     height=300
#                                 )
                                
#                                 st.altair_chart(chart, use_container_width=True)
#                             else:
#                                 st.info("Detailed temperature trial results are not available. Run evaluation again with the next version to see per-temperature performance.")
                            
#                             # Show tuned vs untuned comparison if available
#                             if st.session_state.classification_tuning_results:
#                                 st.subheader("Before vs After Tuning")
                                
#                                 before_metrics = st.session_state.classification_evaluation_results[st.session_state.classification_best_model]["metrics"]
#                                 best_trial = max(st.session_state.classification_tuning_trials, key=lambda x: x['combined_score'])
                                
#                                 # Get the original temperature used before tuning
#                                 original_temp = base_temperature
#                                 comp_data = {
#                                     "Metric": ["Temperature", "Accuracy", "F1 Score"],
#                                     "Before Tuning": [
#                                         f"{original_temp:.2f}",
#                                         f"{before_metrics['accuracy'] * 100:.2f}%",
#                                         f"{before_metrics['f1']:.2f}"
#                                     ],
#                                     "After Tuning": [
#                                         f"{best_trial['temperature']:.2f}",
#                                         f"{best_trial['accuracy'] * 100:.2f}%",
#                                         f"{best_trial['f1']:.2f}"
#                                     ]
#                                 }
                                
#                                 st.table(pd.DataFrame(comp_data))
#                         elif enable_tuning:
#                             st.info("Parameter tuning in progress..." if st.session_state.classification_running else "Run evaluation to see tuning results")
#                         else:
#                             st.info("Parameter tuning is disabled")

#                     # Tab 5: Sample Classifications
#                     with tabs[4]:
#                         if st.session_state.classification_evaluation_results:
#                             st.header("Sample Classification Results")
                            
#                             # Model selector for viewing samples
#                             model_to_view = st.selectbox(
#                                 "Select model to view samples",
#                                 list(st.session_state.classification_evaluation_results.keys()),
#                                 key="classification_model_selector"
#                             )
                            
#                             if model_to_view:
#                                 responses = st.session_state.classification_evaluation_results[model_to_view]["responses"]
                                
#                                 # Filter options
#                                 filter_col1, filter_col2 = st.columns(2)
#                                 show_correct = filter_col1.checkbox("Show Correct Classifications", value=True, key="classification_show_correct")
#                                 show_incorrect = filter_col2.checkbox("Show Incorrect Classifications", value=True, key="classification_show_incorrect")
                                
#                                 filtered_responses = [
#                                     r for r in responses
#                                     if (show_correct and r["correct"]) or (show_incorrect and not r["correct"])
#                                 ]
                                
#                                 # Show samples
#                                 if filtered_responses:
#                                     for i, response in enumerate(filtered_responses[:10]):  # Limit to 10 samples
#                                         with st.expander(
#                                             f"Example {i+1}: {'✅' if response['correct'] else '❌'} " +
#                                             response["question"][:100] + ("..." if len(response["question"]) > 100 else "")
#                                         ):
#                                             st.markdown("**Text to classify:**")
#                                             st.write(response["question"])
                                            
#                                             st.markdown("**Generated Classification:**")
#                                             st.write(response["predicted_class"])
                                            
#                                             st.markdown("**Ground Truth:**")
#                                             st.write(response["ground_truth"])
                                            
#                                             col1, col2, col3 = st.columns(3)
#                                             col1.metric("Correct", "✅" if response["correct"] else "❌")
#                                             col2.metric("Confidence", f"{response['confidence']:.2f}")
                                            
#                                             if "reasoning" in response:
#                                                 st.markdown("**Model Reasoning:**")
#                                                 st.write(response["reasoning"])
#                                 else:
#                                     st.info("No examples matching your filter criteria")
#                         else:
#                             st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see sample classifications")
                    
#                     # Tab 6: Confusion Matrix
#                     with tabs[5]:
#                         if st.session_state.classification_evaluation_results:
#                             st.header("Confusion Matrix Analysis")
                            
#                             # Model selector for confusion matrix
#                             cm_model_to_view = st.selectbox(
#                                 "Select model for confusion matrix",
#                                 list(st.session_state.classification_evaluation_results.keys()),
#                                 key="classification_cm_model_selector"
#                             )
                            
#                             if cm_model_to_view:
#                                 responses = st.session_state.classification_evaluation_results[cm_model_to_view]["responses"]
                                
#                                 # Generate confusion matrix
#                                 classes = sorted(list(set([r["ground_truth"] for r in responses])))
#                                 cm = np.zeros((len(classes), len(classes)), dtype=int)
                                
#                                 for r in responses:
#                                     true_idx = classes.index(r["ground_truth"])
#                                     pred_idx = classes.index(r["predicted_class"]) if r["predicted_class"] in classes else -1
                                    
#                                     if pred_idx >= 0:
#                                         cm[true_idx][pred_idx] += 1
                                
#                                 # Plot confusion matrix
#                                 fig, ax = plt.subplots(figsize=(10, 8))
#                                 im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
#                                 ax.figure.colorbar(im, ax=ax)
                                
#                                 # Show all ticks and label them with class names
#                                 ax.set_xticks(np.arange(len(classes)))
#                                 ax.set_yticks(np.arange(len(classes)))
#                                 ax.set_xticklabels(classes, rotation=45, ha="right")
#                                 ax.set_yticklabels(classes)
                                
#                                 # Loop over data dimensions and create text annotations
#                                 for i in range(len(classes)):
#                                     for j in range(len(classes)):
#                                         text = ax.text(j, i, cm[i, j],
#                                                     ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
                                
#                                 ax.set_title(f"Confusion Matrix - {cm_model_to_view}")
#                                 ax.set_xlabel('Predicted')
#                                 ax.set_ylabel('True')
#                                 plt.tight_layout()
                                
#                                 st.pyplot(fig)
                                
#                                 # Calculate per-class metrics
#                                 st.subheader("Per-class Metrics")
                                
#                                 class_metrics = []
#                                 for i, cls in enumerate(classes):
#                                     tp = cm[i][i]
#                                     fp = sum(cm[:, i]) - tp
#                                     fn = sum(cm[i, :]) - tp
                                    
#                                     precision = tp / (tp + fp) if (tp + fp) > 0 else 0
#                                     recall = tp / (tp + fn) if (tp + fn) > 0 else 0
#                                     f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                                    
#                                     class_metrics.append({
#                                         "Class": cls,
#                                         "Precision": f"{precision:.2f}",
#                                         "Recall": f"{recall:.2f}",
#                                         "F1 Score": f"{f1:.2f}",
#                                         "Support": sum(cm[i, :])
#                                     })
                                
#                                 st.table(pd.DataFrame(class_metrics))
#                         else:
#                             st.info("Running evaluation..." if st.session_state.classification_running else "Run evaluation to see confusion matrix")
                    
#                     # Tab 7: LLM Judge Results
#                     with tabs[6]:
#                         st.header("LLM Judge Evaluation")
                        
#                         if st.session_state.classification_judge_running:
#                             st.info("LLM judge evaluation in progress...")
#                         elif st.session_state.classification_judge_results:
#                             # Display judge results
                            
#                             # Model selection for viewing judge results
#                             judge_model_to_view = st.selectbox(
#                                 "Select model to view judge evaluation",
#                                 list(st.session_state.classification_judge_results.keys()),
#                                 key="classification_judge_model_selector"
#                             )
                            
#                             if judge_model_to_view:
#                                 judge_result = st.session_state.classification_judge_results[judge_model_to_view]
                                
#                                 # Display any errors if present
#                                 if "error" in judge_result:
#                                     st.error(f"Judge evaluation error: {judge_result['error']}")
#                                 else:
#                                     st.subheader(f"Judge Evaluation for {judge_model_to_view}")
                                    
#                                     # If the response has structured evaluation data
#                                     if "evaluation" in judge_result and isinstance(judge_result["evaluation"], dict):
#                                         evaluation = judge_result["evaluation"]
                                        
#                                         # Display scores if available
#                                         if "criteria_scores" in evaluation:
#                                             st.subheader("Criteria Scores")
                                            
#                                             # Create score visualization
#                                             criteria_scores = evaluation["criteria_scores"]
#                                             score_data = []
#                                             for criterion, data in criteria_scores.items():
#                                                 score_data.append({
#                                                     "Criterion": criterion,
#                                                     "Score": data["score"],
#                                                     "Comments": data["comments"]
#                                                 })
                                            
#                                             # Display as a table
#                                             st.table(pd.DataFrame(score_data))
                                            
#                                             # Create radar chart for scores
#                                             labels = [item["Criterion"] for item in score_data]
#                                             scores = [item["Score"] for item in score_data]
                                            
#                                             fig = plt.figure(figsize=(8, 8))
#                                             ax = fig.add_subplot(111, polar=True)
                                            
#                                             # Set the angles for each criterion
#                                             angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
#                                             angles += angles[:1]  # Close the loop
                                            
#                                             # Add the scores
#                                             scores += scores[:1]  # Close the loop
                                            
#                                             # Plot
#                                             ax.plot(angles, scores, linewidth=2, linestyle='solid')
#                                             ax.fill(angles, scores, alpha=0.25)
                                            
#                                             # Set labels and ticks
#                                             ax.set_xticks(angles[:-1])
#                                             ax.set_xticklabels(labels)
#                                             ax.set_yticks([2, 4, 6, 8, 10])
#                                             ax.set_yticklabels(['2', '4', '6', '8', '10'])
#                                             ax.set_ylim(0, 10)
                                            
#                                             plt.title(f'Judge Scores for {judge_model_to_view}')
#                                             st.pyplot(fig)
                                        
#                                         # Display strengths and weaknesses
#                                         if "strengths" in evaluation:
#                                             st.subheader("Strengths")
#                                             for strength in evaluation["strengths"]:
#                                                 st.markdown(f"- {strength}")
                                        
#                                         if "weaknesses" in evaluation:
#                                             st.subheader("Weaknesses")
#                                             for weakness in evaluation["weaknesses"]:
#                                                 st.markdown(f"- {weakness}")
                                        
#                                         # Display summary and final score
#                                         if "summary" in evaluation:
#                                             st.subheader("Summary")
#                                             st.write(evaluation["summary"])
                                        
#                                         if "final_score" in evaluation:
#                                             st.metric("Final Score", f"{evaluation['final_score']}/100")
#                                     else:
#                                         # Display raw evaluation text
#                                         st.markdown("### Judge Evaluation")
#                                         st.write(judge_result.get("raw_response", "No detailed evaluation available"))
                            
#                             # Show tuning comparison if available
#                             if st.session_state.classification_tuning_comparison:
#                                 st.markdown("---")
#                                 st.header("Before vs After Tuning Analysis")
                                
#                                 tuning_comp = st.session_state.classification_tuning_comparison
#                                 model_name = tuning_comp.get("model_name")
                                
#                                 if "error" in tuning_comp:
#                                     st.error(f"Tuning comparison error: {tuning_comp['error']}")
#                                 else:
#                                     st.subheader(f"Tuning Impact Analysis for {model_name}")
                                    
#                                     # Display the analysis
#                                     st.markdown(tuning_comp.get("tuning_impact_analysis", "No tuning analysis available"))
                        
#                         else:
#                             # Show instructions for using the judge
#                             st.info("""
#                             To get an LLM judge evaluation of your models:
#                             1. Complete a model evaluation run
#                             2. Go to the "Evaluation Results" tab
#                             3. Click the "Evaluate Using LLM Judge" button
                            
#                             The judge will evaluate each model's classification quality and provide detailed feedback.
#                             """)
                            
#                             # If we have evaluation results but no judge results, show reminder
#                             if st.session_state.classification_evaluation_results:
#                                 st.markdown("#### Ready for Judge Evaluation")
#                                 st.markdown("You have evaluation results ready to be analyzed by the LLM judge.")
#                                 judge_reminder_button = st.button(
#                                     "Start Judge Evaluation",
#                                     type="primary",
#                                     key="classification_judge_reminder_button"
#                                 )
                                
#                                 if judge_reminder_button:
#                                     st.session_state.classification_judge_running = True
                                    
#                                     # Run judge evaluation
#                                     def run_judge():
#                                         """Synchronous wrapper for the async judge evaluation function"""
#                                         loop = asyncio.new_event_loop()
#                                         asyncio.set_event_loop(loop)
#                                         try:
#                                             return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
#                                         finally:
#                                             loop.close()
                                    
#                                     # Show a spinner during evaluation
#                                     with st.spinner("LLM Judge evaluating models..."):
#                                         run_judge()
                                    
#                                     # Rerun to show the results
#                                     st.rerun()


if __name__ == "__main__":
    main()