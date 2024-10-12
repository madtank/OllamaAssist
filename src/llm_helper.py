import json
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler

def chat(messages, model, tools=None, stream=True):
    # Convert messages to LangChain format
    langchain_messages = [
        SystemMessage(content=msg["content"]) if msg["role"] == "system" else
        HumanMessage(content=msg["content"]) if msg["role"] == "user" else
        AIMessage(content=msg["content"]) if msg["role"] == "assistant" else
        HumanMessage(content=f"Function {msg.get('name', 'unknown')} returned: {msg['content']}")
        for msg in messages
    ]

    # Create ChatOllama instance
    chat_model = ChatOllama(
        model=model,
        streaming=stream,
        callbacks=[StreamingStdOutCallbackHandler()] if stream else None
    )

    if stream:
        callback = AsyncIteratorCallbackHandler()
        chat_model = ChatOllama(
            model=model,
            streaming=True,
            callbacks=[callback]
        )

        async def async_generator():
            full_content = ""
            async for chunk in callback.aiter():
                full_content += chunk.content
                yield {
                    "message": {
                        "role": "assistant",
                        "content": full_content,
                        "is_complete": False
                    }
                }
            # Send a final message indicating the response is complete
            yield {
                "message": {
                    "role": "assistant",
                    "content": full_content,
                    "is_complete": True
                }
            }

        return async_generator()
    else:
        response = chat_model(langchain_messages)
        return {
            "message": {
                "role": "assistant",
                "content": response.content,
                "is_complete": True
            }
        }