import asyncio
import inspect
import json
import logging

import streamlit as st

from config import Config
from src.llm_helper import chat
from src.tools import brave, filesystem
from src.ui import render_system_prompt_editor
from src.prompts import SystemPrompt

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

def display_tool_details(tools):
    """Display available tools and their details in the sidebar."""
    st.sidebar.markdown("## Available Tools")
    for tool in tools:
        if tool['type'] == 'function':
            func = tool['function']
            with st.sidebar.expander(f"🔧 {func['name']}"):
                st.markdown(f"**Description:**\n{func['description']}")
                st.markdown("**Parameters:**")
                for param, details in func['parameters']['properties'].items():
                    st.markdown(f"- `{param}` ({details['type']})")

def setup_sidebar():
    with st.sidebar:
        st.markdown("# Chat Options")
        
        # Add system prompt editor
        render_system_prompt_editor()
        
        # Model selection and tool toggle
        model = st.selectbox('Model:', Config.OLLAMA_MODELS, 
                           index=Config.OLLAMA_MODELS.index(Config.DEFAULT_MODEL))
        use_tools = st.toggle('Use Tools', value=True)
        
        # Display tool details if enabled
        if use_tools:
            tools = load_tools_from_functions()
            display_tool_details(tools)
            
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.rerun()
            
    return model, use_tools

[rest of the file remains unchanged...]