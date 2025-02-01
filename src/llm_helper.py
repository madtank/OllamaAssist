import json
import ollama

def chat(messages, model, tools=None, stream=True):
    """
    Chat with the Ollama model.
    
    Args:
        messages: List of message dictionaries
        model: Name of the Ollama model to use
        tools: Optional list of tool definitions
        stream: Whether to stream the response
    """
    # Ensure all messages are correctly formatted
    formatted_messages = []
    for msg in messages:
        if msg["role"] in ["user", "assistant", "system"]:
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

    # Prepare the request payload
    payload = {
        "model": model,
        "messages": formatted_messages,
        "stream": stream
    }

    if tools:
        payload["tools"] = tools

    # Print the payload for debugging (can be removed in production)
    print(f"Payload sent to Ollama: {json.dumps(payload, indent=2)}")

    # Make the API call
    response = ollama.chat(**payload)

    return response