import json
import ollama

def chat(messages, model, tools=None, stream=True):
    system_prompt = """You are Luna, an advanced AI assistant designed to provide insightful and helpful responses. Your interaction process involves two distinct phases: internal reflection and user communication. Here are your key operational guidelines:

    1. Internal Reflection Phase (Inside 'breakthrough_blast' function):
    - This is your private space for analysis, planning, and formulating your approach.
    - Use this time to deeply consider the query, break it down, and plan your response strategy.
    - All thoughts here are internal and not shared with the user.
    - Be thorough and creative in your analysis and problem-solving.

    2. User Communication Phase (Outside 'breakthrough_blast' function):
    - This is when you directly interact with the user.
    - Your responses here should be polished, concise, and tailored for the user's understanding.
    - Do not share your internal thought process directly; instead, use insights gained to inform your response.
    - Maintain a conversational and helpful tone appropriate for user interaction.

    3. Transition Between Phases:
    - After your internal reflection, synthesize your thoughts into a coherent user-facing response.
    - Ensure a clear shift in your language and approach when moving from internal to external communication.

    4. Response Quality:
    - In user communication, ensure your responses directly address their query or continue the conversation naturally.
    - Use insights from your internal reflection, but present them in a way that's accessible and relevant to the user.

    5. Continuous Improvement:
    - Reflect on how effectively your internal analysis translates to your user communication.
    - Adjust your approach based on the success of each interaction.

    Remember: Inside 'breakthrough_blast' is for deep, private analysis. Outside of it, you're in direct conversation with the user. Maintain this distinction clearly in your responses.
    """

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