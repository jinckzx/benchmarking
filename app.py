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
            ["Non-RAG_eval", "RAG_eval", "Text2SQL_eval"],
            index=0
        )

    if app_mode == "Non-RAG_eval":
        prompt_eval_page()
    elif app_mode == "RAG_eval":
        rag_eval_page()
    elif app_mode == "Text2SQL_eval":
        spider_eval_page()

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
            "Model": r["model"].split("-")[0],
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
    from llm_consortium.core.runner_sql import ConsortiumRunnerSQL
    from llm_consortium.config.models import ConsortiumConfig
    import asyncio
    import json
    import tempfile
    import pandas as pd
    import altair as alt
    import uuid
    from datetime import datetime
    from llm_consortium.utils.pricing import MODEL_PRICING, AVG_INPUT_TOKENS, AVG_OUTPUT_TOKENS, calculate_cost
    if 'download_key' not in st.session_state:
        st.session_state.download_key = f"spider_init_{uuid.uuid4()}"


        if 'models' not in st.session_state:
            st.session_state.models = []
    st.title("GenAI App Tuner")

    runner_sql=ConsortiumRunnerSQL()

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
        
        arbiter = st.selectbox("Arbiter Model", ["gpt-4o-mini", "gemini-2", "gpt-3.5-turbo"], index=2)
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.8)
        max_iter = st.number_input("Max Iterations", min_value=1, value=3, step=1)
        min_iter = st.number_input("Min Iterations", min_value=1, value=1, step=1)

    with col2:
        st.subheader("Execution")
        
        # Add CSV upload
        uploaded_file = st.file_uploader(
            "Upload CSV with queries must include db_id and question columns",
            type=["csv"],
            help="CSV must contain 'db_id' and 'question' columns"
        )
        
        # Display cost estimation only when CSV is uploaded
        if uploaded_file is not None:
            if st.session_state.models:
                models_dict = {model: count for model, count in st.session_state.models}
                total_cost, cost_df = calculate_cost(
                    [(m, c) for m, c in models_dict.items()] + [(arbiter, 1)], 
                    max_iter
                )
                st.write(f"**Estimated Cost:** ${total_cost:.4f}")
                st.dataframe(cost_df, use_container_width=True)
            else:
                st.info("Add models to see cost estimation")

        if st.button("Run Consortium", type="primary"):
            if not st.session_state.models:
                st.error("Please add at least one model")
                st.stop()
            if not uploaded_file:
                st.error("Please upload a CSV file first")
                st.stop()

            # Save uploaded file to temp
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                csv_path = tmp_file.name
            
            config = ConsortiumConfig(
                models=models_dict,
                arbiter=arbiter,
                confidence_threshold=confidence,
                max_iterations=int(max_iter),
                min_iterations=int(min_iter)
            )
            
            result = asyncio.run(runner_sql.run_consortium(config,csv_path))
            
            st.subheader("Results")

            summary_data = []
            for query_result in result:
                summary_data.append({
                    "Database ID": query_result.get('db_id', 'N/A'),
                    "Question": query_result.get('question', 'N/A'),
                    "Generated SQL": query_result['synthesis'].get('final_query', 'No SQL generated'),
                    "Intent": query_result.get('intent', 'N/A'),
                    "Confidence": query_result['synthesis'].get('confidence', 0),
                    "Iterations": query_result.get('iterations', max_iter)
                })
            summary_df=pd.DataFrame(summary_data)
            st.markdown("### Consolidated Results")
            st.dataframe(
                pd.DataFrame(summary_data),
                column_config={
                    "Generated SQL": st.column_config.TextColumn(
                        "SQL Query",
                        help="Final synthesized SQL",
                        width="large"
                    )
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Detailed results for each query
            for idx, query_result in enumerate(result):
                st.markdown(f"### Query {idx+1} Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Database:** `{query_result.get('db_id', 'N/A')}`")
                    st.markdown(f"**Intent:** {query_result.get('intent', 'N/A')}")
                    
                with col2:
                    st.markdown(f"**Confidence:** {query_result['synthesis'].get('confidence', 0):.2f}")
                    st.markdown(f"**Iterations:** {query_result.get('iterations', max_iter)}")

                st.markdown("#### Final SQL")
                st.code(query_result['synthesis'].get('final_query', 'No SQL generated'), language='sql')
                
                # Model responses
                responses_data = []
                for response in query_result.get("raw_responses", []):
                    responses_data.append({
                        "Model": response.get("model", "Unknown"),
                        "SQL Response": response.get("response", ""),
                        "Confidence": response.get("confidence", 0),
                        "Latency (s)": f"{response.get('latency', 0):.2f}",
                        "Iteration": response.get("iteration", 0)
                    })
                
                if responses_data:
                    df_responses = pd.DataFrame(responses_data)
                    st.dataframe(
                        df_responses,
                        column_config={
                            "SQL Response": st.column_config.TextColumn(
                                "SQL",
                                help="Model-generated SQL",
                                width="large"
                            )
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Visualizations
                    with st.expander("Performance Analysis"):
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
                else:
                    st.warning("No model responses recorded for this query")

                
            csv_data = summary_df.to_csv(index=False).encode('utf-8')
            download_key = f"spider_download_{datetime.now().timestamp()}_{uuid.uuid4()}"
                
            st.download_button(
                "⬇️ Download Consolidated Results (CSV)",
                data=csv_data,
                file_name="consortium_summary.csv",
                mime="text/csv",
                key=download_key,
                help="Download summary data in CSV format"
            )



if __name__ == "__main__":
    main()




















    # import streamlit as st
    # import asyncio
    # from llm_consortium.core.runner import ConsortiumRunner
    # from llm_consortium.utils.handlers import initialize_session_state, process_file_upload, create_consortium_config
    # from llm_consortium.utils.components import configure_sidebar, display_cost_estimation, display_results

    # def main():
    #     st.set_page_config(
    #         layout="wide",
    #         page_title="LLM Consortium",
    #         initial_sidebar_state="expanded"
    #     )
    #     st.title("LLM Consortium")
    #     initialize_session_state()

    #     # Configure sidebar and get parameters
    #     arbiter, confidence, max_iter, min_iter = configure_sidebar()

    #     # Main content area
    #     st.header("Execution Panel")
        
    #     # Execution mode selection
    #     execution_mode = st.radio(
    #         "Execution Mode:",
    #         ["Standard Prompt", "RAG Mode"],
    #         horizontal=True,
    #         help="Select between standard prompt execution or RAG-enhanced execution"
    #     )
        
    #     # Handle RAG file upload
    #     if execution_mode == "RAG Mode":
    #         uploaded_file = st.file_uploader(
    #             "Upload knowledge file (PDF, DOCX, TXT, CSV)",
    #             type=["pdf", "docx", "txt", "csv"]
    #         )
    #         if uploaded_file and (uploaded_file != st.session_state.uploaded_file):
    #             with st.status("🔄 Processing uploaded file..."):
    #                 if process_file_upload(uploaded_file):
    #                     st.success("File processed successfully!")
    #                 else:
    #                     st.error("Unsupported file type")
        
    #     # Common input elements
    #     prompt = st.text_area("Input Prompt", height=150, placeholder="Enter your prompt here...")
        
    #     # Cost estimation
    #     display_cost_estimation(arbiter, max_iter)
        
    #     # Execution button
    #     if st.button("Run Consortium", type="primary", use_container_width=True):
    #         if not st.session_state.models:
    #             st.error("Please add at least one model")
    #             return
            
    #         try:
    #             config = create_consortium_config(arbiter, confidence, max_iter, min_iter)
                
    #             if execution_mode == "RAG Mode" and st.session_state.rag_engine:
    #                 result = st.session_state.rag_engine.query(prompt)
    #             else:
    #                 result = asyncio.run(ConsortiumRunner().run_consortium(config, prompt))
                
    #             display_results(result, arbiter, max_iter)
                
    #         except Exception as e:
    #             st.error(f"Error executing consortium: {str(e)}")

    # if __name__ == "__main__":
    #     main()