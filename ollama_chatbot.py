import json
import streamlit as st
from config import Config
from src.llm_helper import chat
from src.tools import tools
from src.system_prompt import system_prompt
import logging
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.chat_models import ChatOllama

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

def setup_sidebar():
    with st.sidebar:
        st.image("images/luna.jpeg")
        st.markdown("# Chat Options")
        model = st.selectbox('Choose an LLM?', Config.OLLAMA_MODELS, index=Config.OLLAMA_MODELS.index(Config.DEFAULT_MODEL))
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.rerun()
    use_tools = True  # Set to True or False based on your preference
    return model, use_tools

def display_previous_messages():
    for message in st.session_state.messages:
        if message.get("is_complete", True):  # Assume complete if flag is not present
            if message["role"] == "assistant" and "tool_calls" in message:
                for tool_call in message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]
                    content = f"**Function Call ({function_name}):**\n```json\n{json.dumps(function_args, indent=2)}\n```"
                    with st.chat_message("tool"):
                        st.markdown(content)
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            # Handle incomplete messages if needed
            pass

def process_user_input():
    if user_prompt := st.chat_input("Ask me anything"):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

def generate_response(model, use_tools):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        stream_handler = StreamlitCallbackHandler(st.empty())
        chat_model = ChatOllama(model=model, streaming=True, callbacks=[stream_handler])

        if use_tools:
            # Define tool_names and tools_string
            tool_names = ", ".join([tool.name for tool in tools])
            tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt + "\n\nUse the following tools to assist you in answering questions:\n\n{tools}\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [{tool_names}]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: {input}\nThought: {agent_scratchpad}"),
                ("human", "{input}")
            ])
            agent = create_openai_tools_agent(chat_model, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                assistant_response = ""
                for chunk in agent_executor.stream({
                    "input": st.session_state.messages[-1]["content"],
                    "agent_scratchpad": "",
                    "tools": tools_string,
                    "tool_names": tool_names,
                }):
                    if isinstance(chunk, dict) and "output" in chunk:
                        output_chunk = chunk["output"]
                        assistant_response += output_chunk
                        response_placeholder.markdown(assistant_response + "▌")
                # After the loop, check for 'Final Answer:'
                if 'Final Answer:' in assistant_response:
                    assistant_response = assistant_response.split('Final Answer:', 1)[1].strip()
                response_placeholder.markdown(assistant_response)

        else:
            messages = [SystemMessage(content=system_prompt)] + [
                HumanMessage(content=m["content"]) if m["role"] == "user" else
                AIMessage(content=m["content"]) for m in st.session_state.messages
            ]

            with st.chat_message("assistant"):
                response = chat_model(messages)

            assistant_response = response.content

        # Append the assistant response to the session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response,
            "is_complete": True
        })

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