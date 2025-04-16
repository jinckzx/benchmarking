from llm_consortium.core.runner import ConsortiumRunner
from llm_consortium.config.models import ConsortiumConfig
import asyncio
import json
import tempfile
import streamlit as st
from llm_consortium.core.file_handler import FileHandler
import pandas as pd
from llm_consortium.utils.pricing import calculate_cost

def initialize_session_state():
    if 'models' not in st.session_state:
        st.session_state.models = []
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

def handle_model_addition(model, instances):
    existing_index = next((idx for idx, (m, _) in enumerate(st.session_state.models) 
                        if m == model), -1)
    if existing_index >= 0:
        st.session_state.models[existing_index] = (model, int(instances))
    else:
        st.session_state.models.append((model, int(instances)))
    st.rerun()

def create_consortium_config(arbiter, confidence, max_iter, min_iter):
    return ConsortiumConfig(
        models=dict(st.session_state.models),
        arbiter=arbiter,
        confidence_threshold=confidence,
        max_iterations=int(max_iter),
        min_iterations=int(min_iter)
    )

def process_file_upload(uploaded_file):
    try:
        file_handler = FileHandler()
        if file_handler.validate_file(uploaded_file):
            st.session_state.rag_engine = ConsortiumRunner().handle_file_upload(uploaded_file)
            st.session_state.uploaded_file = uploaded_file
            return True
        return False
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False