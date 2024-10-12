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

# Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title=Config.PAGE_TITLE, initial_sidebar_state="expanded")

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

def setup_sidebar():
    with st.sidebar:
        st.image("images/luna.jpeg")
        st.markdown("# Chat Options")
        model = st.selectbox(
            'Choose an LLM?',
            Config.OLLAMA_MODELS,
            index=Config.OLLAMA_MODELS.index(Config.DEFAULT_MODEL)
        )
        if st.button('New Chat', key='new_chat', help='Start a new chat'):
            st.session_state.messages = []
            st.session_state.conversation_history = [SystemMessage(content=system_prompt)]
            st.rerun()
    return model

def display_previous_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def process_user_input():
    if user_prompt := st.chat_input("Ask me anything"):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        return True
    return False

def generate_response(model):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        stream_handler = StreamlitCallbackHandler(st.empty())
        chat_model = ChatOllama(model=model, streaming=True, callbacks=[stream_handler])

        conversation_history = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages[:-1]  # Exclude the latest message
        ])

        tool_names = ", ".join([tool.name for tool in tools])
        tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + f"""

Use the following tools to assist you in answering questions:

{tools_string}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Conversation history:
{conversation_history}

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}
"""),
            ("human", "{input}")
        ])

        agent = create_openai_tools_agent(chat_model, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            thinking_placeholder = st.empty()
            assistant_response = ""
            thinking_process = ""

            for chunk in agent_executor.stream({
                "input": st.session_state.messages[-1]["content"],
                "conversation_history": conversation_history,
                "agent_scratchpad": "",
                "tools": tools_string,
                "tool_names": tool_names,
            }):
                if isinstance(chunk, dict) and "output" in chunk:
                    output_chunk = chunk["output"]
                    if 'Final Answer:' in output_chunk:
                        final_answer = output_chunk.split('Final Answer:', 1)[1].strip()
                        assistant_response += final_answer
                        response_placeholder.markdown(assistant_response + "▌")
                    else:
                        thinking_process += output_chunk + "\n"
                        thinking_placeholder.markdown(thinking_process)

            # If there's no final answer, use the entire thinking process
            if not assistant_response:
                assistant_response = thinking_process.strip()

            # Ensure we're not sending a blank message
            if not assistant_response:
                assistant_response = "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"

            # Clear the thinking placeholder
            thinking_placeholder.empty()
            # Display the final assistant response without the cursor
            response_placeholder.markdown(assistant_response)

        # Append the assistant response to the session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response,
            "is_complete": True
        })

def main():
    st.title(Config.PAGE_TITLE)
    model = setup_sidebar()

    display_previous_messages()
    if process_user_input():
        generate_response(model)

if __name__ == '__main__':
    main()