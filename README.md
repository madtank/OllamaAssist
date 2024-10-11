# OllamaAssist

OllamaAssist is a versatile AI chatbot application that leverages the advanced capabilities of function-calling enabled language models, with a current focus on the Llama family of models. By utilizing Ollama for local model execution and integrating sophisticated function calling and self-reflection mechanisms, OllamaAssist provides an enhanced, context-aware interaction experience.

## Key Features

- **Function Calling Optimization**: Designed to work best with models that support function calling, such as Llama models.
- **Advanced Function Calling**: Utilize a range of tools and functions to enhance the AI's capabilities.
- **Self-Reflection Mechanism**: Enables the AI to analyze and improve its own responses.
- **Model Flexibility**: While optimized for Llama models, it's adaptable to other function-calling enabled models.
- **Streamlit Interface**: Easy-to-use chat interface built with Streamlit.
- **Local Execution**: Run models on your local machine for enhanced privacy and control.
- **Model Selection**: Choose from compatible Ollama models at runtime.
- **Streaming Responses**: Get real-time responses as the model generates them.
- **Spark Integration**: Leverage Apache Spark for distributed data processing and analysis.

## How It Works

OllamaAssist leverages a unique architecture that combines function-calling enabled language models with advanced features:

1. **Language Model**: Powered by Ollama, optimized for Llama and other function-calling models.
2. **Function Calling**: The AI can call specific functions to perform tasks or retrieve information.
3. **Self-Reflection**: A special tool that allows the AI to analyze and refine its own thoughts and responses.
4. **Streamlit Frontend**: Provides an intuitive interface for user interactions.
5. **Spark Integration**: Utilize Apache Spark for scalable data processing and analysis.

### Function Calling and Self-Reflection

The core strength of OllamaAssist lies in its ability to use function calling and self-reflection:

1. **Function Calling**: When the AI needs to perform a specific task or retrieve information, it can call predefined functions. This allows for dynamic, context-aware responses and actions.

2. **Self-Reflection**: When the AI wants to improve its response, it uses the self-reflection tool:
   - Generates an initial response
   - Analyzes this response using the reflection tool
   - Generates an improved response based on the reflection

This results in more thoughtful, context-aware, and accurate responses.

### Spark Integration

OllamaAssist now includes integration with Apache Spark, enabling the AI to perform distributed data processing and analysis. This is particularly useful for handling large datasets and performing complex computations efficiently.

1. **Spark Setup**: Ensure Apache Spark is installed and configured on your system.
2. **Spark Functions**: The AI can call Spark functions to process and analyze data. For example, the `spark_data_analysis` function can be used to perform data analysis tasks using Spark.

## Prerequisites

- Python 3.9+
- Ollama installed on your system
- A function-calling enabled model installed via Ollama (e.g., Llama 3.2 or later versions)
- Apache Spark installed and configured on your system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/madtank/OllamaAssist.git
   cd OllamaAssist
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure Ollama is running on your system:
   ```
   ollama serve
   ```

2. Start the Streamlit application:
   ```
   streamlit run ollama_chatbot.py
   ```

3. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

4. Select a compatible function-calling model from the sidebar and start chatting!

## Compatibility Note

OllamaAssist is designed to work best with function-calling enabled models, particularly those in the Llama family. While it can work with various Ollama-supported models, full functionality (including function calling and self-reflection) is only available with compatible models. When using non-function-calling models, some features may be limited.

## Customization

- To add new tools or functionalities, modify the `tools.py` file.
- Adjust system prompts or chat behavior in `llm_helper.py`.
- Customize the Streamlit interface in `ollama_chatbot.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Ollama](https://github.com/jmorganca/ollama) for providing the neural engine.
- [Streamlit](https://streamlit.io/) for the amazing web app framework.
- The teams behind function-calling language models, particularly the Llama model series, for their groundbreaking work.