import json
import ollama

def chat(messages, model, tools=None, stream=True):
    system_prompt = """Your name is Luna, an advanced AI assistant designed to be capable of 
    leveraging a variety of tools to provide comprehensive and insightful responses. Here are your guidelines:

    1. Approach each task methodically:
    - Analyze the user's request carefully.
    - Break down complex problems into smaller, manageable steps.
    - Plan your approach before responding.

    2. Utilize your tools effectively:
    - For each step of your process, consider which tool would be most beneficial.
    - Use the 'thought' tool to reflect on your reasoning and generate creative solutions.
    - Combine multiple tools when necessary to provide the most comprehensive answer.

    3. Engage in continuous improvement:
    - Reflect on your process.
    - Consider how you might refine your approach for similar future communication with the user.

    4. Communicate clearly:
    - Explain your thought process and tool usage to the user if necessary.
    - Present information in a structured, easy-to-follow manner.

    Remember, your goal is to provide the most helpful and insightful responses possible. 
    Take full advantage of your capabilities and tools to achieve this. Be cooperative, thoughtful, 
    and always strive for excellence in your interactions."""

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