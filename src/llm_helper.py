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

                            Start the answer by inserting: "\n\n==================NEW ANSWER==================\n\n"

                            Structure your response by using capitalized section titles and a bit of formatting.

                            Every time, provide at the end of your answer the following metadata of the supporting document 
                            (or documents if there is more than one applicable):
                            \n\n**Document ID**\n\n
                            \n\n**Title**\n\n
                            \n\n**Hyperlink**\n\n

                            After the above-mentioned metadata, add a brief warning to the user reminding them of the importance to 
                            verify the information provided in this answer.                           
                            """

def chat(messages, model, tools=None, stream=True):
    system_prompt = "You are a helpful assistant looking to provide the most accurate information possible. \
                    You add the formatted metadata at the end of your answer, including: document ID, title, and hyperlink."

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