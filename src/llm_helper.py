from dataclasses import dataclass

import json
import ollama

@dataclass
class PromptTemplateType:
    """Class for prompt templates"""
    unstructured_without_context: str = """Answer the following question: {question}."""
    unstructured_with_context: str = """Answer the {question} based only on the following context:{context}."""
    unstructured_with_context_and_knowledge_from_model: str = """Answer the {question} both based on your knowledge and the {context}."""
    structured_with_context_only = """                        
                            Answer the {question} based only on the following context: {context}.
                            Structure your response by using section titles and formatting.

                            Always provide at the end of your answer the metadata from the supporting documents:

                            *Document ID
                            *Title
                            *Hyperlink

                            After the above-mentioned metadata, add a brief warning to the user reminding them of the importance to 
                            verify the information provided in this answer.                           
                            """
    

@dataclass
class HyperparametersConfig:
    temperature:float=0.0
    top_k:int=5

    

def chat(messages, model, tools=None, stream=True):
    system_prompt = """You are a helpful assistant looking to provide the most accurate information possible.
                        You always provide at the end of your answer the metadata from the supporting documents:
                        *Document ID
                        *Title
                        *Hyperlink"""

    # Ensure all messages are correctly formatted
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "system" and msg["content"] == system_prompt:
            formatted_messages.append(msg)
        elif msg["role"] in ["user", "assistant", "system"]:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        elif msg["role"] == "function":
            # Convert function messages to user messages
            formatted_messages.append({
                "role": "user",
                "content": f"Function {msg.get('name', 'unknown')} returned: {msg['content']}"
            })

    # Add system message if not present
    if not formatted_messages or formatted_messages[0]["role"] != "system":
        formatted_messages.insert(0, {"role": "system", "content": system_prompt})

    # Prepare the request payload
    payload = {
        "model": model,
        "messages": formatted_messages,
        "stream": stream
    }

    if tools:
        payload["tools"] = tools

    # Print the payload for debugging
    print(f"Payload sent to Ollama: {json.dumps(payload, indent=2)}")

    # Make the API call
    response = ollama.chat(**payload)

    return response