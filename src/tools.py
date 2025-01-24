from typing import Dict, Any, List, Optional, Union
from duckduckgo_search import DDGS
import random
import time
import os
import logging
from requests.exceptions import RequestException
from datetime import datetime, timedelta

class SearchRateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [t for t in self.requests if now - t < timedelta(minutes=1)]
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = (self.requests[0] + timedelta(minutes=1) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.requests.append(now)

def search_duckduckgo(
    query: str,
    search_type: str = "text",
    max_results: int = 5,
    max_retries: int = 3,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    proxy: Optional[str] = None
) -> Union[str, List[Dict[str, Any]]]:
    """
    Enhanced DuckDuckGo search function supporting multiple search types and proxy.
    """
    rate_limiter = SearchRateLimiter()
    proxy = proxy or os.getenv("DDGS_PROXY")
    
    for attempt in range(max_retries):
        try:
            rate_limiter.wait_if_needed()
            
            with DDGS(proxy=proxy, timeout=20) as ddgs:
                time.sleep(random.uniform(0.5, 1.5))
                
                if search_type == "text":
                    # Explicitly convert generator to list and validate results
                    results = list(ddgs.text(
                        keywords=query,
                        region=region,
                        safesearch=safesearch,
                        max_results=max_results
                    ))
                    # Log raw results for debugging
                    logging.debug(f"Raw DuckDuckGo results: {results}")
                    
                    if not results:
                        return f"No results found for query: {query}"
                    
                    return format_text_results(results)
                
                # Handle other search types...
                # ...existing code...
                results = []
                if search_type == "text":
                    results = list(ddgs.text(query, max_results=max_results, region=region, safesearch=safesearch))
                elif search_type == "news":
                    results = list(ddgs.news(query, max_results=max_results, region=region, safesearch=safesearch))
                elif search_type == "images":
                    results = list(ddgs.images(query, max_results=max_results, region=region, safesearch=safesearch))
                elif search_type == "chat":
                    return ddgs.chat(query, model="claude-3-haiku")
                
                if not results:
                    return f"No {search_type} results found for query: {query}"
                
                if search_type == "text":
                    return format_text_results(results)
                return results
                
        except ValueError as ve:
            handle_value_error(ve, attempt, max_retries)
        except RequestException as re:
            handle_request_exception(re, attempt, max_retries)
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Search error: {str(e)}")
                return f"Search error: {str(e)}"
            time.sleep((attempt + 1) * 2)

def format_text_results(results: List[Dict[str, str]]) -> str:
    formatted = []
    for idx, result in enumerate(results, 1):
        # Debug log for missing fields
        if not all(k in result for k in ['title', 'body', 'link']):
            logging.debug(f"Incomplete result data: {result}")
        
        title = result.get('title', 'No Title')
        body = result.get('body', 'No Description')
        # DuckDuckGo API might return URL in different fields
        url = result.get('link') or result.get('url') or result.get('href', 'No URL')
        
        formatted.append(
            f"{idx}. {title}\n"
            f"   {body}\n"
            f"   URL: {url}\n"
        )
    return "\n".join(formatted)

def handle_value_error(error: ValueError, attempt: int, max_retries: int):
    if "_text_extract_json" in str(error):
        logging.warning(f"DuckDuckGo API extraction error: {str(error)}")
        if attempt < max_retries - 1:
            time.sleep((attempt + 1) * 2)
        else:
            raise ValueError("Search service temporarily unavailable")
    raise error

def handle_request_exception(error: RequestException, attempt: int, max_retries: int):
    if '202 Ratelimit' in str(error):
        wait_time = (attempt + 1) * 3
        if attempt < max_retries - 1:
            logging.warning(f"Rate limit hit, waiting {wait_time} seconds")
            time.sleep(wait_time)
        else:
            raise RequestException("Search rate limit reached")
    raise error

def sequential_thinking(tasks: list[str] = None, context: str = "") -> str:
    """
    🔄 Sequential Thinking Process: A structured approach to task planning and execution.
    """
    try:
        # Handle tasks input
        if isinstance(tasks, str):
            # Try to parse if it's a JSON string
            import json
            try:
                tasks = json.loads(tasks)
            except json.JSONDecodeError:
                tasks = [tasks]  # Treat as single task if not valid JSON
        
        if not tasks:
            tasks = ["Analyze requirements", "Identify key components", "Plan execution steps"]
        
        # Ensure tasks is a flat list of strings
        if isinstance(tasks, list) and len(tasks) == 1 and isinstance(tasks[0], str):
            # Handle case where task is a single string that needs to be split
            if ',' in tasks[0]:
                tasks = [t.strip() for t in tasks[0].split(',')]
            elif len(tasks[0]) > 0:
                tasks = [tasks[0]]

        # Format the planning output
        plan = "🎯 Sequential Planning Process:\n\n"
        for idx, task in enumerate(tasks, 1):
            plan += f"{idx}. {task}\n"
        
        if context:
            plan += f"\n📝 Context Analysis:\n{context}\n"
        
        plan += "\n✅ Planning phase complete. Ready for execution."
        return plan
    except Exception as e:
        logging.error(f"Sequential thinking error: {str(e)}")
        return f"Error in sequential thinking process: {str(e)}"