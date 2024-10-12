from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from duckduckgo_search import DDGS

def search_duckduckgo(query, region='wt-wt', safesearch='off', max_results=5):
    """DuckDuckGo web search."""
    return list(DDGS().text(keywords=query, region=region, safesearch=safesearch, max_results=max_results))

def breakthrough_blast(internal_dialogue: str) -> str:
    # Placeholder for the actual implementation of the breakthrough_blast function
    return f"Internal analysis: {internal_dialogue}"

class SearchInput(BaseModel):
    query: str = Field(..., description="The search query")

search_tool = Tool(
    name="search_duckduckgo",
    description="DuckDuckGo web search. You write the query, and we will get the results back directly in our chat.",
    func=search_duckduckgo,
    args_schema=SearchInput
)

class BreakthroughInput(BaseModel):
    internal_dialogue: str = Field(..., description="Your comprehensive internal analysis, planning, and problem-solving thoughts. This is not a message to the user.")

breakthrough_tool = Tool(
    name="breakthrough_blast",
    description="Internal thought process for deep analysis and planning. Use this for private reflection, not direct user communication.",
    func=breakthrough_blast,
    args_schema=BreakthroughInput
)

tools = [search_tool, breakthrough_tool]
