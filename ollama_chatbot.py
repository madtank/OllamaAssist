import json
import streamlit as st
from config import Config
from src.llm_helper import chat
from src.tools import tools
import logging
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamlitCallbackHandler

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

def generate_response(model, use_tools):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner('Generating response...'):
            stream_handler = StreamlitCallbackHandler(st.empty())
            chat_model = ChatOllama(model=model, streaming=True, callbacks=[stream_handler])
            
            if use_tools:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are Luna, an advanced AI assistant..."),  # Your system prompt
                    ("human", "{input}")
                ])
                agent = create_openai_tools_agent(chat_model, tools, prompt)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
                
                with st.chat_message("assistant"):
                    response = agent_executor.invoke({
                        "input": st.session_state.messages[-1]["content"]
                    }, callbacks=[stream_handler])
                
                assistant_response = response['output']
            else:
                messages = [SystemMessage(content="You are Luna, an advanced AI assistant...")] + \
                           [HumanMessage(content=m["content"]) if m["role"] == "user" else 
                            AIMessage(content=m["content"]) for m in st.session_state.messages]
                
                with st.chat_message("assistant"):
                    response = chat_model(messages)
                
                assistant_response = response.content

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
