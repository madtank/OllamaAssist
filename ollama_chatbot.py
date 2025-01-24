import json
import yaml
import streamlit as st
from config import Config
from src.llm_helper import chat
from src.tools import sequential_thinking, search_duckduckgo, retrieve_database
import logging

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

def setup_sidebar():
    with st.sidebar:
        st.markdown("# Chat Options")
        model = st.selectbox('What model would you like to use?', Config.OLLAMA_MODELS, index=Config.OLLAMA_MODELS.index(Config.DEFAULT_MODEL))
        use_tools = st.toggle('Use Tools', value=True)
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.rerun()
    return model, use_tools

def display_previous_messages():
    for message in st.session_state.messages:
        display_role = message["role"]
        if display_role == "assistant" and "tool_calls" in message:
            for tool_call in message["tool_calls"]:
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

def load_tools_from_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        tools_data = yaml.safe_load(f)
    tools = []
    for tool in tools_data['tools']:
        tools.append({
            'type': 'function',
            'function': {
                'name': tool['name'],
                'description': tool['description'],
                'parameters': tool['parameters']
            }
        })
    return tools

def generate_response(model, use_tools):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner('Generating response...'):
            tools = load_tools_from_yaml('tools.yaml') if use_tools else []
            response = chat(st.session_state.messages, model=model, tools=tools, stream=False)
            print("Response message content:", response['message'])
            
            if "tool_calls" in response['message']:
                print("Tool calls content:", response['message']['tool_calls'])
                assistant_message = response['message']
                st.session_state.messages.append(assistant_message)
                
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]
                    with st.chat_message("tool"):
                        content = f"**Function Call ({function_name}):**\n```json\n{json.dumps(function_args, indent=2)}\n```"
                        st.markdown(content)
                    
                        def no_op():
                            """A no-op function that does nothing."""
                            pass
                        
                        available_functions = {
                            'sequential_thinking': sequential_thinking,
                            'search_duckduckgo': search_duckduckgo,
                            'retrieve_database': retrieve_database,
                            'no_op': no_op,
                        }

                    if function_name in available_functions:
                        function_to_call = available_functions[function_name]
                        function_response = function_to_call(**function_args)
                        tool_message = {
                            'role': 'function',
                            'name': function_name,
                            'content': function_response,  # Direct string return
                        }
                        st.session_state.messages.append(tool_message)
                        with st.chat_message("tool"):
                            st.markdown(tool_message['content'])
                
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

def main():
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        initial_sidebar_state="expanded"
    )
    st.title(Config.PAGE_TITLE)
    model, use_tools = setup_sidebar()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    display_previous_messages()
    process_user_input()
    generate_response(model, use_tools)

if __name__ == '__main__':
    main()