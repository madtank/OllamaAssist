import json
import yaml
import streamlit as st
import sys
from pathlib import Path
import asyncio
import logging

# Add project root to Python path to fix imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.llm_helper import chat, mcp_manager
from config import Config
from ollama_model_info import ModelManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_mgr" not in st.session_state:
        st.session_state.model_mgr = ModelManager()

def format_thinking_tag(content: str) -> str:
    """Format thinking tags in the content"""
    if "</think>" in content.lower():
        # Extract content between think tags
        start = content.lower().find("</think>")
        return content[start + 8:]  # Remove the closing tag
    return content

def setup_sidebar():
    """Configure the sidebar with model selection and options."""
    model_mgr = st.session_state.model_mgr
    
    with st.sidebar:
        st.markdown("# Chat Options")
        
        # Get available models
        available_models = model_mgr.get_available_models()
        model_names = sorted(list(set(m["name"].split(":")[0] for m in available_models)))
        
        # Model selection
        selected_model = st.selectbox(
            'Select Model',
            model_names,
            index=model_names.index(Config.DEFAULT_MODEL) if Config.DEFAULT_MODEL in model_names else 0
        )
        
        # Model capabilities section
        if selected_model:
            model_details = model_mgr.get_model_details(selected_model)
            
            with st.expander("Model Information", expanded=True):
                if model_details:
                    capabilities = model_details.get("capabilities", {})
                    st.markdown("### 🔧 Capabilities:")
                    st.markdown(f"- Streaming: {'✅' if capabilities.get('streaming') else '❌'}")
                    st.markdown(f"- Tools: {'✅' if capabilities.get('tool_support') else '❌'}")
                    
                    # Only show tool options if model supports it
                    use_tools = False
                    if capabilities.get("tool_support"):
                        use_tools = st.toggle('Enable Tools', value=True)
                        if use_tools and not mcp_manager.tools_enabled:
                            st.warning("MCP tools not available. Check configuration.")
                            use_tools = False
                    else:
                        st.info("This model doesn't support tools")
                        
                    # Temperature
                    temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=2.0,
                        value=0.7
                    )
                    
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.rerun()
            
    return selected_model, use_tools

def display_previous_messages():
    """Display chat history."""
    for message in st.session_state.messages:
        display_role = message["role"]
        content = message.get("content", "")
        
        if display_role == "assistant":
            # Handle thinking tags
            content = format_thinking_tag(content)
            
            if "tool_calls" in message:
                # Display the message first
                if content:
                    with st.chat_message("assistant"):
                        st.markdown(content)
                
                # Then display tool calls
                for tool_call in message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]
                    if function_name.startswith("mcp_"):
                        _, server, tool = function_name.split("_", 2)
                        display_name = f"MCP Tool - {server}/{tool}"
                    else:
                        display_name = function_name
                        
                    with st.chat_message("tool"):
                        st.markdown(f"**{display_name}:**")
                        st.json(json.loads(function_args))
            else:
                # Regular message
                with st.chat_message("assistant"):
                    st.markdown(content)
                    
        elif display_role == "function":
            with st.chat_message("tool"):
                if message["name"].startswith("mcp_"):
                    _, server, tool = message["name"].split("_", 2)
                    st.markdown(f"**MCP Result - {server}/{tool}:**")
                else:
                    st.markdown("**Tool Result:**")
                st.markdown(content)
        else:
            with st.chat_message(display_role):
                st.markdown(content)

def process_user_input():
    """Get and process user input."""
    if user_prompt := st.chat_input("What would you like to ask?"):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        return True
    return False

def generate_response(model: str, use_tools: bool):
    """Generate model response with tool support."""
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner('Generating response...'):
            try:
                # Get model capabilities
                model_details = st.session_state.model_mgr.get_model_details(model)
                if not model_details:
                    st.error(f"Could not get model details for {model}")
                    return
                
                capabilities = model_details.get("capabilities", {})
                
                # Use streaming if supported
                stream = capabilities.get("streaming", True)
                
                # Only use tools if both model and MCP support them
                enable_tools = use_tools and capabilities.get("tool_support", False)
                
                # Start chat with appropriate settings
                llm_stream = chat(
                    st.session_state.messages, 
                    model=model, 
                    tools=enable_tools, 
                    stream=stream
                )
                
                assistant_response = ""
                tool_calls_detected = False
                current_tool_calls = []
                
                # Display streamed response
                with st.chat_message("assistant"):
                    stream_placeholder = st.empty()
                    
                    for chunk in llm_stream:
                        logger.debug(f"Raw chunk: {chunk}")
                        
                        if isinstance(chunk, dict):
                            # Handle tool calls
                            if "tool_calls" in chunk:
                                tool_calls_detected = True
                                current_tool_calls.extend(chunk["tool_calls"])
                            
                            # Handle message content
                            content = chunk.get("content", "")
                            if not content and "message" in chunk:
                                content = chunk["message"].get("content", "")
                                
                            if content:
                                # Format thinking tags
                                content = format_thinking_tag(content)
                                assistant_response += content
                                stream_placeholder.markdown(assistant_response + "▌")
                    
                    # Final update without cursor
                    if assistant_response:
                        stream_placeholder.markdown(assistant_response)
                    elif tool_calls_detected:
                        stream_placeholder.markdown("Processing with tools...")
                
                # Add to chat history
                if assistant_response or tool_calls_detected:
                    message = {
                        "role": "assistant",
                        "content": assistant_response or "Processing with tools..."
                    }
                    if tool_calls_detected:
                        message["tool_calls"] = current_tool_calls
                    
                    st.session_state.messages.append(message)
                    
                    # Process any tool calls
                    if tool_calls_detected:
                        for tool_call in current_tool_calls:
                            function_name = tool_call["function"]["name"]
                            function_args = tool_call["function"]["arguments"]
                            
                            # Execute tool
                            if function_name.startswith("mcp_"):
                                result = asyncio.run(mcp_manager.execute_tool(
                                    function_name,
                                    json.loads(function_args)
                                ))
                                # Add result to history
                                st.session_state.messages.append({
                                    "role": "function",
                                    "name": function_name,
                                    "content": result
                                })
                
            except Exception as e:
                logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
                st.error(f"Error generating response: {str(e)}")

def show_quick_start_buttons():
    """Display quick start buttons for tool discovery."""
    st.markdown("### 🚀 Quick Start")
    st.markdown("Choose an action to begin:")
    
    col1, col2, col3 = st.columns(3)
    
    if not st.session_state.messages:
        with col1:
            if st.button("🌐 Web Search"):
                return "Let's search the web for information about AI models and their capabilities."
        with col2:
            if st.button("📂 Explore Files"):
                return "Can you help me explore and manage files in my current directory?"
        with col3:
            if st.button("❔ Model Info"):
                return "What are the capabilities and specifications of the currently selected model?"
    return None

def main():
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        initial_sidebar_state="expanded"
    )
    
    st.title(Config.PAGE_TITLE)
    
    # Initialize session state
    setup_session_state()
    
    # Setup sidebar and get model settings
    model, use_tools = setup_sidebar()
    
    # Show quick start options
    quick_start_action = show_quick_start_buttons()
    if quick_start_action:
        st.session_state.messages.append({
            "role": "user",
            "content": quick_start_action
        })
        st.rerun()
    
    # Display chat history
    display_previous_messages()
    
    # Process new input and generate response
    if process_user_input():
        generate_response(model, use_tools)

if __name__ == '__main__':
    main()