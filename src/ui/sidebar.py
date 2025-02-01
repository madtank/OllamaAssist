import streamlit as st
from src.prompts.config import SystemPrompt

def render_system_prompt_editor():
    """Render system prompt controls in sidebar"""
    with st.sidebar.expander("System Instructions", expanded=False):
        # Show base prompt (read-only)
        st.markdown("#### Base Instructions")
        st.info(SystemPrompt.BASE_PROMPT)
        
        # Additional instructions editor
        st.markdown("#### Additional Instructions")
        additional_instructions = st.text_area(
            "Add your specific instructions below:",
            value=st.session_state.get('additional_instructions', ''),
            height=200,
            placeholder="""Examples of additional instructions:

- We are reviewing Python files in directory X
- Help me analyze and improve code quality
- We are building a web application with Flask
- Explain concepts clearly and provide examples
- Use web search for current documentation

Your instructions will be added to the base system prompt."""
        )
        
        # Store in session state
        st.session_state['additional_instructions'] = additional_instructions

        if additional_instructions:
            st.info("✓ Additional instructions active")