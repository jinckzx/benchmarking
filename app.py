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
            ["Non-RAG_eval", "RAG_eval", "Text2SQL_eval","Classification_Eval", "new_sql"],
            index=0
        )

    if app_mode == "Non-RAG_eval":
        prompt_eval_page()
    elif app_mode == "RAG_eval":
        rag_eval_page()
    elif app_mode == "Text2SQL_eval":
        spider_eval_page()
    elif app_mode == "Classification_Eval":
        classification_page()
    elif app_mode == "new_sql":
        text2sql_ui()

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
                    metrics = result["metrics"]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
                    with col2:
                        st.metric("Macro F1", f"{metrics.get('macro_f1', 0):.4f}")
                    with col3:
                        st.metric("Weighted F1", f"{metrics.get('weighted_f1', 0):.4f}")
                    
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
                                
                                chart = alt.Chart(trial_df).mark_line().encode(
                                    x=alt.X('temperature:Q', title='Temperature'),
                                    y=alt.Y('confidence:Q', title='Confidence'),
                                    tooltip=['temperature', 'confidence', 'final_class']
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
                if not st.session_state.sql_evaluation_results:
                    st.error("No evaluation results available to judge")
                    return None
                
                # Evaluate all models using judge
                judge_results = await judge.evaluate_model_outputs(
                    st.session_state.sql_evaluation_results,
                    criteria=judge_criteria
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
            tabs = st.tabs(["Evaluation Results", "Model Comparison", "Best Model", "Best Parameter", "Sample Queries", "LLM Judge"])
            
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
            

# def text2sql_ui():
#     import os
#     import matplotlib.pyplot as plt
#     import streamlit as st
#     from llm_consortium.core.sql.sql_model_runner import SQLModelRunner
#     from llm_consortium.core.sql.sql_judge import SQLJudge 
#     from llm_consortium.config.models_sql import ModelConfig
#     import asyncio
#     import json
#     import tempfile
#     import pandas as pd
#     import altair as alt
#     import uuid
#     from llm_consortium.utils.logging import logger
#     from datetime import datetime
#     from llm_consortium.utils.pricing import calculate_cost
#     from llm_consortium.core.client_init import llm

    
#  # Import the newly created judge class

#     # Initialize judge
#     judge = SQLJudge(llm)

#     # Title and description
#     st.title("SQL Model Evaluation and Tuning")
#     st.markdown("""
#     This tool evaluates different LLM models for SQL query generation and tunes parameters for the best performer.
#     Upload your test dataset, select models to evaluate, and configure evaluation parameters.
#     """)

#     # Initialize session state for storing results between reruns
#     if 'sql_evaluation_results' not in st.session_state:
#         st.session_state.sql_evaluation_results = None
#     if 'sql_best_model' not in st.session_state:
#         st.session_state.sql_best_model = None
#     if 'sql_best_params' not in st.session_state:
#         st.session_state.sql_best_params = None
#     if 'sql_tuning_results' not in st.session_state:
#         st.session_state.sql_tuning_results = None
#     if 'sql_running' not in st.session_state:
#         st.session_state.sql_running = False
#     if 'sql_progress' not in st.session_state:
#         st.session_state.sql_progress = 0
#     # Add new states for judge results
#     if 'sql_judge_results' not in st.session_state:
#         st.session_state.sql_judge_results = None
#     if 'sql_judge_running' not in st.session_state:
#         st.session_state.sql_judge_running = False
#     if 'sql_tuning_comparison' not in st.session_state:
#         st.session_state.sql_tuning_comparison = None

#     def reset_results():
#         st.session_state.sql_evaluation_results = None
#         st.session_state.sql_best_model = None
#         st.session_state.sql_best_params = None
#         st.session_state.sql_tuning_results = None
#         st.session_state.sql_running = False
#         st.session_state.sql_progress = 0
#         st.session_state.sql_judge_results = None
#         st.session_state.sql_judge_running = False
#         st.session_state.sql_tuning_comparison = None

#     # Layout with two columns - config panel and results
#     col1, col2 = st.columns([1, 3])

#     # Configuration panel
#     with col1:
#         st.header("Configuration")
        
#         # File uploader
#         uploaded_file = st.file_uploader("Upload Test Dataset (CSV)", type=["csv"], key="sql_csv_upload")
        
#         # Model selection (with default models)
#         default_models = ["gpt-4o-mini", "gpt-4o"]
#         available_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
#         selected_models = st.multiselect(
#             "Select Models to Evaluate", 
#             available_models,
#             default=default_models,
#             key="sql_models"
#         )
        
#         # Judge model selection (new)
#         judge_models = ["gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"] 
#         selected_judge = st.selectbox(
#             "LLM Judge Model",
#             judge_models,
#             index=0,  # Default to first model
#             key="sql_judge_model"
#         )
        
#         # Base configuration
#         st.subheader("Base Settings")
#         base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.2, 0.05, key="sql_base_temp")
        
#         # Tuning settings
#         st.subheader("Parameter Tuning")
#         enable_tuning = st.checkbox("Enable Parameter Tuning", value=True, key="sql_enable_tuning")
        
#         min_temp = st.slider("Min Temperature", 0.0, 1.0, 0.0, 0.05, key="sql_min_temp")
#         max_temp = st.slider("Max Temperature", 0.0, 1.0, 0.8, 0.05, key="sql_max_temp")
#         num_trials = st.slider("Number of Trials", 3, 10, 5, key="sql_num_trials")
#         sample_size = st.slider("Tuning Sample Size", 5, 50, 10, key="sql_sample_size")
        
#         # Judge settings (new)
#         st.subheader("Judge Settings")
#         judge_criteria = st.multiselect(
#             "Judge Criteria",
#             [
#                 "Column name accuracy",
#                 "Table usage correctness",
#                 "Join quality",
#                 "Condition correctness",
#                 "Query structure",
#                 "SQL syntax correctness",
#                 "Query optimization",
#                 "Intent understanding"
#             ],
#             default=[
#                 "Column name accuracy",
#                 "Table usage correctness",
#                 "Query structure",
#                 "Intent understanding"
#             ],
#             key="sql_judge_criteria"
#         )
        
#         # Output settings
#         st.subheader("Output Settings")
#         output_dir = st.text_input("Output Directory", "results", key="sql_output_dir")
#         save_results = st.checkbox("Save Results to File", value=True, key="sql_save_results")
        
#         # Run button
#         run_button = st.button("Run Evaluation", type="primary", key="sql_run_button", 
#                               disabled=len(selected_models) == 0 or uploaded_file is None)

#     # Main content area in the second column
#     with col2:
#         async def run_evaluation_async(config, csv_path):
#             """Run the evaluation and tuning pipeline asynchronously"""
#             try:
#                 runner = SQLModelRunner()
                
#                 # Step 1: Evaluate all models
#                 st.session_state.sql_progress = 10
#                 evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluating models...")
                
#                 # Run evaluation
#                 evaluation_results = await runner.evaluate_models(config, csv_path)
#                 st.session_state.sql_evaluation_results = evaluation_results
#                 st.session_state.sql_progress = 50
#                 evaluation_progress.progress(st.session_state.sql_progress/100, "Evaluation complete, processing results...")
                
#                 # Calculate average latency for each model
#                 model_metrics = {}
#                 for model_name, eval_data in evaluation_results.items():
#                     metrics = eval_data["metrics"]
#                     responses = eval_data["responses"]
                    
#                     # Calculate average latency (not directly provided in metrics)
#                     latencies = [r["latency"] for r in responses]
#                     avg_latency = sum(latencies) / len(latencies) if latencies else 0
                    
#                     model_metrics[model_name] = {
#                         "execution_match_rate": metrics["execution_match_rate"],
#                         "exact_match_rate": metrics["exact_match_rate"],
#                         "avg_latency": avg_latency
#                     }
                
#                 # Find best model based on execution match rate, breaking ties with latency
#                 best_model = max(
#                     model_metrics.items(),
#                     key=lambda x: (x[1]["execution_match_rate"], -x[1]["avg_latency"])
#                 )[0]
                
#                 st.session_state.sql_best_model = best_model
#                 st.session_state.sql_progress = 60
#                 evaluation_progress.progress(st.session_state.sql_progress/100, f"Best model identified: {best_model}")
#                 # Step 3: Tune the best model if enabled
#                 if config.enable_tuning:
#                     evaluation_progress.progress(st.session_state.sql_progress/100, f"Tuning {best_model}...")
#                     best_params = await runner.tune_best_model(
#                         best_model,
#                         csv_path,
#                         config
#                     )
#                     st.session_state.sql_best_params = best_params
                    
#                     # Capture the temperature trial results if available from the tuner
#                     if hasattr(runner.hyperparameter_tuner, 'trial_results'):
#                         st.session_state.sql_tuning_trials = runner.hyperparameter_tuner.trial_results
                    
#                     st.session_state.sql_progress = 80
#                     evaluation_progress.progress(st.session_state.sql_progress/100, "Tuning complete")
                
#                     # Step 4: Optionally evaluate with tuned parameters
#                     if config.run_final_evaluation:
#                         evaluation_progress.progress(st.session_state.sql_progress/100, f"Final evaluation with tuned parameters...")
#                         final_results = await runner.evaluate_with_params(
#                             best_model, 
#                             best_params, 
#                             csv_path
#                         )
#                         st.session_state.sql_tuning_results = final_results
                        
#                 # Save results if requested
#                 if save_results:
#                     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                     os.makedirs(output_dir, exist_ok=True)
#                     output_file = os.path.join(output_dir, f"sql_eval_results_{timestamp}.json")
                    
#                     with open(output_file, "w") as f:
#                         json.dump({
#                             "model_evaluations": evaluation_results,
#                             "best_model": best_model,
#                             "best_params": best_params if config.enable_tuning else None,
#                             "model_metrics": model_metrics
#                         }, f, indent=2, default=str)
                        
#                 st.session_state.sql_progress = 100
#                 evaluation_progress.progress(st.session_state.sql_progress/100, "Complete!")
#                 return model_metrics
                
#             except Exception as e:
#                 st.error(f"Error during evaluation: {str(e)}")
#                 logger.error(f"Evaluation error: {str(e)}")
#                 return None
#             finally:
#                 st.session_state.sql_running = False
        
#         # New function for evaluating using the judge
#         async def run_judge_evaluation_async(judge_criteria):
#             """Run the judge evaluation asynchronously"""
#             try:
#                 if not st.session_state.sql_evaluation_results:
#                     st.error("No evaluation results available to judge")
#                     return None
                
#                 # Evaluate all models using judge
#                 judge_results = await judge.evaluate_model_outputs(
#                     st.session_state.sql_evaluation_results,
#                     criteria=judge_criteria
#                 )
                
#                 # Store results
#                 st.session_state.sql_judge_results = judge_results
                
#                 # If we have before/after tuning results, compare those too
#                 if st.session_state.sql_best_model and st.session_state.sql_tuning_results:
#                     best_model = st.session_state.sql_best_model
#                     before_data = st.session_state.sql_evaluation_results[best_model]
#                     after_data = st.session_state.sql_tuning_results
                    
#                     tuning_comparison = await judge.before_after_tuning_comparison(
#                         best_model,
#                         before_data,
#                         after_data
#                     )
                    
#                     st.session_state.sql_tuning_comparison = tuning_comparison
                
#                 return judge_results
                
#             except Exception as e:
#                 st.error(f"Error during judge evaluation: {str(e)}")
#                 logger.error(f"Judge evaluation error: {str(e)}")
#                 return None
#             finally:
#                 st.session_state.sql_judge_running = False
        
#         if run_button and not st.session_state.sql_running:
#             # Create config
#             config = ModelConfig(
#                 models=selected_models,
#                 base_temperature=base_temperature,
#                 enable_tuning=enable_tuning,
#                 min_temp=min_temp,
#                 max_temp=max_temp,
#                 num_trials=num_trials,
#                 tuning_sample_size=sample_size,
#                 run_final_evaluation=True
#             )
            
#             # Save uploaded file temporarily
#             temp_csv = "temp_dataset.csv"
#             with open(temp_csv, "wb") as f:
#                 f.write(uploaded_file.getvalue())
            
#             # Reset previous results
#             reset_results()
            
#             # Show progress bar
#             evaluation_progress = st.progress(0, "Starting evaluation...")
#             st.session_state.sql_running = True
            
#             # Method 1: Using a synchronous wrapper function
#             def run_evaluation(config, csv_path):
#                 """Synchronous wrapper for the async evaluation function"""
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 try:
#                     return loop.run_until_complete(run_evaluation_async(config, csv_path))
#                 finally:
#                     loop.close()
            
#             # Run the evaluation in the current thread (this will block the UI until complete)
#             run_evaluation(config, temp_csv)
        
#         # Display tabs for results
#         if st.session_state.sql_running or st.session_state.sql_evaluation_results:
#             tabs = st.tabs(["Evaluation Results", "Model Comparison", "Best Model", "Best Parameter", "Sample Queries", "LLM Judge"])
            
#             # Tab 1: Evaluation Results Table
#             with tabs[0]:
#                 if st.session_state.sql_evaluation_results:
#                     st.header("Model Evaluation Results")
                    
#                     # Add LLM Judge button
#                     judge_col1, judge_col2 = st.columns([1, 3])
#                     with judge_col1:
#                         judge_button = st.button(
#                             "Evaluate Using LLM Judge", 
#                             type="primary", 
#                             key="sql_judge_button",
#                             disabled=st.session_state.sql_judge_running
#                         )
                    
#                     if judge_button and not st.session_state.sql_judge_running:
#                         st.session_state.sql_judge_running = True
                        
#                         # Run judge evaluation
#                         def run_judge():
#                             """Synchronous wrapper for the async judge evaluation function"""
#                             loop = asyncio.new_event_loop()
#                             asyncio.set_event_loop(loop)
#                             try:
#                                 return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
#                             finally:
#                                 loop.close()
                        
#                         # Show a spinner during evaluation
#                         with st.spinner("LLM Judge evaluating models..."):
#                             run_judge()
                        
#                         # Show completion message
#                         st.success("LLM Judge evaluation complete! See the 'LLM Judge' tab for results.")
                    
#                     # Create a DataFrame for metrics
#                     metrics_data = []
                    
#                     for model_name, eval_data in st.session_state.sql_evaluation_results.items():
#                         metrics = eval_data["metrics"]
#                         responses = eval_data["responses"]
                        
#                         # Calculate average latency
#                         latencies = [r["latency"] for r in responses]
#                         avg_latency = sum(latencies) / len(latencies) if latencies else 0
                        
#                         metrics_data.append({
#                             "Model": model_name,
#                             "Execution Match (%)": round(metrics["execution_match_rate"], 2),
#                             "Exact Match (%)": round(metrics["exact_match_rate"], 2),
#                             "Avg. Latency (s)": round(avg_latency, 3),
#                             "Samples": len(responses)
#                         })
                    
#                     metrics_df = pd.DataFrame(metrics_data)
#                     st.dataframe(metrics_df, use_container_width=True)
                    
#                     if st.session_state.sql_best_model:
#                         st.success(f"Best model: {st.session_state.sql_best_model}")
#                 else:
#                     st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
            
            # # Tab 2: Model Comparison Charts
            # with tabs[1]:
            #     if st.session_state.sql_evaluation_results:
            #         st.header("Model Comparison")
                    
            #         # Prepare data for visualization
            #         models = []
            #         exec_match = []
            #         exact_match = []
            #         latencies = []
                    
            #         for model_name, eval_data in st.session_state.sql_evaluation_results.items():
            #             metrics = eval_data["metrics"]
            #             responses = eval_data["responses"]
                        
            #             # Calculate average latency
            #             avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
                        
            #             models.append(model_name)
            #             exec_match.append(metrics["execution_match_rate"])
            #             exact_match.append(metrics["exact_match_rate"])
            #             latencies.append(avg_latency)
                    
            #         # Create charts
            #         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
            #         # Match rates chart
            #         x = range(len(models))
            #         width = 0.35
                    
            #         ax1.bar([i - width/2 for i in x], exec_match, width, label='Execution Match (%)')
            #         ax1.bar([i + width/2 for i in x], exact_match, width, label='Exact Match (%)')
            #         ax1.set_xticks(x)
            #         ax1.set_xticklabels(models, rotation=45, ha='right')
            #         ax1.set_ylabel('Match Rate (%)')
            #         ax1.set_title('Model Match Rates')
            #         ax1.legend()
            #         ax1.grid(True, linestyle='--', alpha=0.7)
                    
            #         # Latency chart
            #         ax2.bar(models, latencies, color='orange')
            #         ax2.set_xticklabels(models, rotation=45, ha='right')
            #         ax2.set_ylabel('Average Latency (s)')
            #         ax2.set_title('Model Latency')
            #         ax2.grid(True, linestyle='--', alpha=0.7)
                    
            #         plt.tight_layout()
            #         st.pyplot(fig)
            #     else:
            #         st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
            
            # # Tab 3: Best Model Details
            # with tabs[2]:
            #     if st.session_state.sql_best_model:
            #         st.header(f"Best Model: {st.session_state.sql_best_model}")
                    
            #         best_model_data = st.session_state.sql_evaluation_results[st.session_state.sql_best_model]
            #         metrics = best_model_data["metrics"]
                    
            #         col1, col2, col3 = st.columns(3)
            #         col1.metric("Execution Match Rate", f"{metrics['execution_match_rate']:.2f}%")
            #         col2.metric("Exact Match Rate", f"{metrics['exact_match_rate']:.2f}%")
                    
                    
            #         responses = best_model_data["responses"]
            #         avg_latency = sum([r["latency"] for r in responses]) / len(responses) if responses else 0
            #         col3.metric("Average Latency", f"{avg_latency:.3f}s")
                    
            #         # Show confidence distribution
            #         st.subheader("Confidence Distribution")
            #         confidences = [r["confidence"] for r in responses]
                    
            #         fig, ax = plt.subplots(figsize=(10, 5))
            #         ax.hist(confidences, bins=10, alpha=0.7)
            #         ax.set_xlabel('Confidence')
            #         ax.set_ylabel('Count')
            #         ax.grid(True, linestyle='--', alpha=0.7)
            #         st.pyplot(fig)
            #     else:
            #         st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see results")
            
            # # Tab 4: Parameter Tuning Results
            # with tabs[3]:
            #     if st.session_state.sql_best_params:
            #         st.header("Best Parameter")
                    
            #         col1, col2 = st.columns(2)
            #         col1.metric("Best Temperature", f"{st.session_state.sql_best_params['temperature']:.2f}")
            #         col1.metric("Execution Match Rate", f"{st.session_state.sql_best_params['execution_match_rate']:.2f}%")
                    
            #         # Add a section to show results for each temperature trial
            #         st.subheader("Temperature Trial Results")
                    
            #         # Check if we have the full tuning results available in session state
            #         if 'sql_tuning_trials' in st.session_state and st.session_state.sql_tuning_trials:
            #             # Create a dataframe to display all trial results
            #             trials_data = []
            #             for trial in st.session_state.sql_tuning_trials:
            #                 trials_data.append({
            #                     "Temperature": f"{trial['temperature']:.2f}",
            #                     "Execution Match Rate (%)": f"{trial['execution_match_rate']:.2f}%",
            #                     "Exact Match Rate (%)": f"{trial['exact_match_rate']:.2f}%" if 'exact_match_rate' in trial else "N/A"
            #                 })
                        
            #             # Display as a table
            #             st.table(pd.DataFrame(trials_data))
                        
            #             # Also create a visualization for the temperature vs performance
            #             st.subheader("Temperature vs. Performance")
                        
            #             # Create chart data
            #             chart_data = pd.DataFrame({
            #                 'Temperature': [trial['temperature'] for trial in st.session_state.sql_tuning_trials],
            #                 'Execution Match Rate (%)': [trial['execution_match_rate'] for trial in st.session_state.sql_tuning_trials],
            #                 'Exact Match Rate (%)': [trial.get('exact_match_rate', None) for trial in st.session_state.sql_tuning_trials]
            #             })
                        
            #             # Melt the dataframe for Altair
            #             chart_data_melted = chart_data.melt(id_vars=['Temperature'], 
            #                                 value_vars=['Execution Match Rate (%)', 'Exact Match Rate (%)'],
            #                                 var_name='Metric', 
            #                                 value_name='Match Rate (%)')
                        
            #             # Create a line chart with markers
            #             chart = alt.Chart(chart_data_melted).mark_line(point=True).encode(
            #                 x=alt.X('Temperature:Q', title='Temperature'),
            #                 y=alt.Y('Match Rate (%):Q', title='Match Rate (%)'),
            #                 color='Metric:N',
            #                 tooltip=['Temperature','Metric', 'Match Rate (%)']
            #             ).properties(
            #                 width=600,
            #                 height=300
            #             )
                        
            #             st.altair_chart(chart, use_container_width=True)
            #         else:
            #             st.info("Detailed temperature trial results are not available. Run evaluation again with the next version to see per-temperature performance.")
                    
            #         # Show tuned vs untuned comparison if available
            #         if st.session_state.sql_tuning_results:
            #             st.subheader("Before vs After Tuning")
                        
            #             before_metrics = st.session_state.sql_evaluation_results[st.session_state.sql_best_model]["metrics"]
            #             best_trial = max(st.session_state.sql_tuning_trials, key=lambda x: x['execution_match_rate'])
                        
            #             # Get the original temperature used before tuning
            #             #original_temp = st.session_state.sql_original_temperature if hasattr(st.session_state, 'sql_original_temperature') else 1.0
            #             original_temp = base_temperature
            #             comp_data = {
            #                 "Metric": ["Temperature","Execution Match Rate", "Exact Match Rate"],
            #                 "Before Tuning": [
            #                     f"{original_temp:.2f}",
            #                     f"{before_metrics['execution_match_rate']:.2f}%",
            #                     f"{before_metrics['exact_match_rate']:.2f}%"
            #                 ],
            #                 "After Tuning": [
            #                     f"{best_trial['temperature']:.2f}",
            #                     f"{best_trial['execution_match_rate']:.2f}%",
            #                     f"{best_trial.get('exact_match_rate', 0.00):.2f}%"  # Default to 0.00 if not present
            #                 ]
            #             }
                        
            #             st.table(pd.DataFrame(comp_data))
            #     elif enable_tuning:
            #         st.info("Parameter tuning in progress..." if st.session_state.sql_running else "Run evaluation to see tuning results")
            #     else:
            #         st.info("Parameter tuning is disabled")

            # # Tab 5: Sample Queries
            # with tabs[4]:
            #     if st.session_state.sql_evaluation_results:
            #         st.header("Sample Query Results")
                    
            #         # Model selector for viewing samples
            #         model_to_view = st.selectbox(
            #             "Select model to view samples",
            #             list(st.session_state.sql_evaluation_results.keys()),
            #             key="sql_model_selector"
            #         )
                    
            #         if model_to_view:
            #             responses = st.session_state.sql_evaluation_results[model_to_view]["responses"]
                        
            #             # Filter options
            #             filter_col1, filter_col2 = st.columns(2)
            #             show_correct = filter_col1.checkbox("Show Correct Queries", value=True, key="sql_show_correct")
            #             show_incorrect = filter_col2.checkbox("Show Incorrect Queries", value=True, key="sql_show_incorrect")
                        
            #             filtered_responses = [
            #                 r for r in responses 
            #                 if (show_correct and r["execution_match"]) or (show_incorrect and not r["execution_match"])
            #             ]
                        
            #             # Show samples
            #             if filtered_responses:
            #                 for i, response in enumerate(filtered_responses[:10]):  # Limit to 10 samples
            #                     with st.expander(
            #                         f"Query {i+1}: {'✅' if response['execution_match'] else '❌'} " + 
            #                         response["question"][:100] + ("..." if len(response["question"]) > 100 else "")
            #                     ):
            #                         st.markdown("**Question:**")
            #                         st.write(response["question"])
                                    
            #                         st.markdown("**Generated SQL:**")
            #                         st.code(response["generated_sql"], language="sql")
                                    
            #                         st.markdown("**Gold SQL:**")
            #                         st.code(response["gold_sql"], language="sql")
                                    
            #                         col1, col2, col3 = st.columns(3)
            #                         col1.metric("Execution Match", "✅" if response["execution_match"] else "❌")
            #                         col2.metric("Exact Match", "✅" if response["exact_match"] else "❌")
            #                         col3.metric("Confidence", f"{response['confidence']:.2f}")
            #             else:
            #                 st.info("No queries matching your filter criteria")
            #     else:
            #         st.info("Running evaluation..." if st.session_state.sql_running else "Run evaluation to see sample queries")
            
            # # Tab 6: LLM Judge Results (New)
            # with tabs[5]:
            #     st.header("LLM Judge Evaluation")
                
            #     if st.session_state.sql_judge_running:
            #         st.info("LLM judge evaluation in progress...")
            #     elif st.session_state.sql_judge_results:
            #         # Display judge results
                    
            #         # Model selection for viewing judge results
            #         judge_model_to_view = st.selectbox(
            #             "Select model to view judge evaluation",
            #             list(st.session_state.sql_judge_results.keys()),
            #             key="sql_judge_model_selector"
            #         )
                    
            #         if judge_model_to_view:
            #             judge_result = st.session_state.sql_judge_results[judge_model_to_view]
                        
            #             # Display any errors if present
            #             if "error" in judge_result:
            #                 st.error(f"Judge evaluation error: {judge_result['error']}")
            #             else:
            #                 st.subheader(f"Judge Evaluation for {judge_model_to_view}")
                            
            #                 # If the response has structured evaluation data
            #                 if "evaluation" in judge_result and isinstance(judge_result["evaluation"], dict):
            #                     evaluation = judge_result["evaluation"]
                                
            #                     # Display scores if available
            #                     if "criteria_scores" in evaluation:
            #                         st.subheader("Criteria Scores")
                                    
            #                         # Create score visualization
            #                         criteria_scores = evaluation["criteria_scores"]
            #                         score_data = []
            #                         for criterion, data in criteria_scores.items():
            #                             score_data.append({
            #                                 "Criterion": criterion,
            #                                 "Score": data["score"],
            #                                 "Comments": data["comments"]
            #                             })
                                    
            #                         # Display as a table
            #                         st.table(pd.DataFrame(score_data))
                                    
            #                         # Create radar chart for scores
            #                         labels = [item["Criterion"] for item in score_data]
            #                         scores = [item["Score"] for item in score_data]
                                    
            #                         fig = plt.figure(figsize=(8, 8))
            #                         ax = fig.add_subplot(111, polar=True)
                                    
            #                         # Set the angles for each criterion
            #                         angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
            #                         angles += angles[:1]  # Close the loop
                                    
            #                         # Add the scores
            #                         scores += scores[:1]  # Close the loop
                                    
            #                         # Plot
            #                         ax.plot(angles, scores, linewidth=2, linestyle='solid')
            #                         ax.fill(angles, scores, alpha=0.25)
                                    
            #                         # Set labels and ticks
            #                         ax.set_xticks(angles[:-1])
            #                         ax.set_xticklabels(labels)
            #                         ax.set_yticks([2, 4, 6, 8, 10])
            #                         ax.set_yticklabels(['2', '4', '6', '8', '10'])
            #                         ax.set_ylim(0, 10)
                                    
            #                         plt.title(f'Judge Scores for {judge_model_to_view}')
            #                         st.pyplot(fig)
                                
            #                     # Display strengths and weaknesses
            #                     if "strengths" in evaluation:
            #                         st.subheader("Strengths")
            #                         for strength in evaluation["strengths"]:
            #                             st.markdown(f"- {strength}")
                                
            #                     if "weaknesses" in evaluation:
            #                         st.subheader("Weaknesses")
            #                         for weakness in evaluation["weaknesses"]:
            #                             st.markdown(f"- {weakness}")
                                
            #                     # Display summary and final score
            #                     if "summary" in evaluation:
            #                         st.subheader("Summary")
            #                         st.write(evaluation["summary"])
                                
            #                     if "final_score" in evaluation:
            #                         st.metric("Final Score", f"{evaluation['final_score']}/100")
            #                 else:
            #                     # Display raw evaluation text
            #                     st.markdown("### Judge Evaluation")
            #                     st.write(judge_result.get("raw_response", "No detailed evaluation available"))
                    
            #         # Show tuning comparison if available
            #         if st.session_state.sql_tuning_comparison:
            #             st.markdown("---")
            #             st.header("Before vs After Tuning Analysis")
                        
            #             tuning_comp = st.session_state.sql_tuning_comparison
            #             model_name = tuning_comp.get("model_name")
                        
            #             if "error" in tuning_comp:
            #                 st.error(f"Tuning comparison error: {tuning_comp['error']}")
            #             else:
            #                 st.subheader(f"Tuning Impact Analysis for {model_name}")
                            
            #                 # Display the analysis
            #                 st.markdown(tuning_comp.get("tuning_impact_analysis", "No tuning analysis available"))
                
            #     else:
            #         # Show instructions for using the judge
            #         st.info("""
            #         To get an LLM judge evaluation of your models:
            #         1. Complete a model evaluation run
            #         2. Go to the "Evaluation Results" tab
            #         3. Click the "Evaluate Using LLM Judge" button
                    
            #         The judge will evaluate each model's SQL generation quality and provide detailed feedback.
            #         """)
                    
            #         # If we have evaluation results but no judge results, show reminder
            #         if st.session_state.sql_evaluation_results:
            #             st.markdown("#### Ready for Judge Evaluation")
            #             st.markdown("You have evaluation results ready to be analyzed by the LLM judge.")
            #             judge_reminder_button = st.button(
            #                 "Start Judge Evaluation", 
            #                 type="primary", 
            #                 key="sql_judge_reminder_button"
            #             )
                        
            #             if judge_reminder_button:
            #                 st.session_state.sql_judge_running = True
                            
            #                 # Run judge evaluation
            #                 def run_judge():
            #                     """Synchronous wrapper for the async judge evaluation function"""
            #                     loop = asyncio.new_event_loop()
            #                     asyncio.set_event_loop(loop)
            #                     try:
            #                         return loop.run_until_complete(run_judge_evaluation_async(judge_criteria))
            #                     finally:
            #                         loop.close()
                            
            #                 # Show a spinner during evaluation
            #                 with st.spinner("LLM Judge evaluating models..."):
            #                     run_judge()
                            
            #                 # Rerun to show the results
            #                 st.rerun()



if __name__ == "__main__":
    main()










