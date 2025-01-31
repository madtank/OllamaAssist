import asyncio
import inspect
import json
import logging

import streamlit as st

from config import Config
from src.llm_helper import chat
from src.tools import brave, filesystem

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
        model = st.selectbox('What model would you like to use?', Config.OLLAMA_MODELS, index=Config.OLLAMA_MODELS.index(Config.DEFAULT_MODEL))
        use_tools = st.toggle('Use Tools', value=True)
        
        # Display tool details if enabled
        if use_tools:
            tools = load_tools_from_functions()
            display_tool_details(tools)
            
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.rerun()
    return model, use_tools

def display_previous_messages():
    for message in st.session_state.messages:
        display_role = message["role"]
        if display_role == "assistant" and "tool_calls" in message:
            # Fix: iterate over the tool_calls list properly
            for tool_call in message["tool_calls"]:  # Changed from: for tool_call in message
                function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                content = f"**Function Call ({function_name}):**\n```json\n{json.dumps(function_args, indent=2)}\n```"
                with st.chat_message("tool"):
                    st.markdown(content)
        else:
            with st.chat_message(display_role):
                st.markdown(message["content"])

def process_user_input():
    if user_prompt := st.chat_input("What would you like to ask?"):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

def load_tools_from_functions():
    tools = []
    available_functions = {
        'brave': brave,
        'filesystem': filesystem
    }
    
    for name, func in available_functions.items():
        sig = inspect.signature(func)
        params = {}
        
        for param_name, param in sig.parameters.items():
            param_type = 'string'  # default
            if param.annotation == int:
                param_type = 'integer'
            elif param.annotation == list:
                param_type = 'array'
            elif param.annotation == dict:
                param_type = 'object'
                
            params[param_name] = {
                'type': param_type,
                'description': '',  # Let the docstring explain the parameters
            }
            
            # Add default value if one exists
            if param.default != param.empty:
                params[param_name]['default'] = param.default

        tools.append({
            'type': 'function',
            'function': {
                'name': name,
                'description': func.__doc__,
                'parameters': {
                    'type': 'object',
                    'properties': params
                },
                'is_async': asyncio.iscoroutinefunction(func)
            }
        })
    return tools

def generate_response(model, use_tools):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner('Generating response...'):
            tools = load_tools_from_functions() if use_tools else []
            response = chat(st.session_state.messages, model=model, tools=tools, stream=False)
            
            if "tool_calls" in response['message']:
                assistant_message = response['message']
                st.session_state.messages.append(assistant_message)
                
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]
                    
                    # Debug logging
                    logging.debug(f"Tool call detected: {function_name}")
                    logging.debug(f"Arguments type: {type(function_args)}")
                    logging.debug(f"Arguments content: {function_args}")
                    
                    with st.chat_message("tool"):
                        content = f"**Function Call ({function_name}):**\n```json\n{json.dumps(function_args, indent=2)}\n```"
                        st.markdown(content)
                    
                    available_functions = {
                        'brave': {'func': brave, 'is_async': True},
                        'filesystem': {'func': filesystem, 'is_async': True}
                    }

                    if function_name in available_functions:
                        func_info = available_functions[function_name]
                        try:
                            # Parse arguments if they're a string
                            args = function_args if isinstance(function_args, dict) else json.loads(function_args)
                            
                            logging.debug(f"Calling {function_name} with args: {args}")
                            
                            if func_info['is_async']:
                                try:
                                    function_response = asyncio.run(func_info['func'](**args))
                                    if isinstance(function_response, dict) and 'error' in function_response:
                                        raise Exception(function_response['error'])
                                except Exception as e:
                                    logging.error(f"Async function error: {str(e)}", exc_info=True)
                                    raise
                            else:
                                function_response = func_info['func'](**args)
                            
                            logging.debug(f"Function response: {function_response}")
                            
                            tool_message = {
                                'role': 'function',
                                'name': function_name,
                                'content': str(function_response)
                            }
                            st.session_state.messages.append(tool_message)
                            with st.chat_message("tool"):
                                st.markdown(tool_message['content'])
                        except Exception as e:
                            error_message = f"Error executing {function_name}: {str(e)}"
                            logging.error(f"Error details - Args: {function_args}, Error: {str(e)}")
                            st.error(error_message)
                            logging.error(error_message)

                # Stream the assistant's response
                llm_stream = chat(st.session_state.messages, model=model, stream=True)
                assistant_response = ""
                with st.chat_message("assistant"):
                    stream_placeholder = st.empty()
                    for chunk in llm_stream:
                        content = chunk['message']['content']
                        assistant_response += content
                        stream_placeholder.markdown(assistant_response + "▌")
                    stream_placeholder.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                # Handle responses without tool calls
                llm_stream = chat(st.session_state.messages, model=model, stream=True)
                assistant_response = ""
                with st.chat_message("assistant"):
                    stream_placeholder = st.empty()
                    for chunk in llm_stream:
                        content = chunk['message']['content']
                        assistant_response += content
                        stream_placeholder.markdown(assistant_response + "▌")
                    stream_placeholder.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

def show_quick_start_buttons():
    """Display quick start buttons for tool discovery."""
    st.markdown("### 🚀 Quick Start")
    st.markdown("Choose an action to begin:")
    
    col1, col2, col3 = st.columns(3)  # Changed to 3 columns
    
    # Only show buttons if no messages exist
    if not st.session_state.messages:
        with col1:
            if st.button("📰 Deepseek R1 News"):
                return "Can you tell me about the latest news regarding Deepseek R1?"
        with col2:
            if st.button("📂 Check Local Files"):
                return "Can you help me explore the local files and directories?"
        with col3:
            if st.button("🖥️ Test MCP Servers"):
                return "Could you help me list all available MCP servers and then test their functionality? First, show me the list of servers, and then we can try some basic operations on them."
    return None

def main():
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        initial_sidebar_state="expanded"
    )
    st.title(Config.PAGE_TITLE)
    model, use_tools = setup_sidebar()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Show quick start buttons and handle their actions
    quick_start_action = show_quick_start_buttons()
    if quick_start_action:
        st.session_state.messages.append({
            "role": "user",
            "content": quick_start_action
        })
        st.rerun()
    
    display_previous_messages()
    process_user_input()
    generate_response(model, use_tools)

if __name__ == '__main__':
    main()