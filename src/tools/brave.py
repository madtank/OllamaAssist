from typing import Any, Dict
from .base import BaseTool
from ..mcp_client import mcp

class BraveSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "brave"
    
    @property
    def description(self) -> str:
        return "Perform web searches using Brave Search API"
    
    @property
    def parameters(self) -> Dict:
        return {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "count": {
                "type": "integer",
                "description": "Number of results",
                "default": 5
            }
        }
        
    async def execute(self, query: str, count: int = 5) -> Any:
        return await mcp(
            server="brave-search",
            tool="brave_web_search",
            arguments={"query": query, "count": count}
        )
