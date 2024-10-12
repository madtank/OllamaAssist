from typing import Dict, Any
import random
from duckduckgo_search import DDGS
import time
from requests.exceptions import RequestException

def search_duckduckgo(query, max_retries=3, delay=5):
    """
    DuckDuckGo web search with retry logic and backend specification.
    
    Args:
    query (str): The search query.
    max_retries (int): Maximum number of retry attempts.
    delay (int): Delay in seconds between retries.
    
    Returns:
    list: Search results.
    """
    for attempt in range(max_retries):
        try:
            # Specify the backend and limit results
            results = list(DDGS().text(keywords=query, backend='api', max_results=5))
            return results
        except RequestException as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Unable to complete search.")
                    return []
            else:
                print(f"An error occurred: {e}")
                return []

def breakthrough_blast(internal_dialogue: str = "") -> str:
    """
    🧠 Internal Thought Process: A tool for reflection, planning, and idea generation.

    This function serves as Luna's private thinking space. It should be used
    to organize thoughts, reflect on tasks, plan approaches, and generate ideas.

    Args:
        internal_dialogue (str): Luna's comprehensive internal analysis and planning.

    Returns:
        str: A signal indicating the completion of the internal thinking step and transition to user communication.
    """
    responses = [
        "🎇💭✨ Internal reflection complete. Transitioning to user communication.",
        "🌟🔍💡 Thought process finalized. Preparing user-friendly response.",
        "🧠🔄🚀 Mental framework established. Shifting to external dialogue.",
        "🌈🧩🔍 Internal analysis concluded. Adapting insights for user interaction.",
        "⚡🔮💡 Cognitive processing done. Engaging user communication mode."
    ]
    return random.choice(responses)