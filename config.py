import ollama

class Config:
    PAGE_TITLE = "Streamlit AI Chatbot with Ollama Integration"
    DEFAULT_MODEL = "llama3.2:latest"

    # Retrieve the list of models using ollama.list()
    models_info = ollama.list()
    # Access the list of models
    model_list = models_info['models']
    # Extract the model names
    OLLAMA_MODELS = tuple(model['model'] for model in model_list)
    
    # Check if the default model is in the list of models
    DEFAULT_MODEL = "llama3.2:latest"
    if DEFAULT_MODEL not in OLLAMA_MODELS:
        # Default to the first model in the list if the default model is not found
        DEFAULT_MODEL = OLLAMA_MODELS[0]