from typing import Dict, Any
from abc import ABC, abstractmethod
import logging
from .base import BaseTool

class MCPTool(ABC):
    """Base class for all MCP tools"""
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict:
        pass

class ToolRegistry:
    _tools: Dict[str, BaseTool] = {}
    
    @classmethod
    def register(cls, name: str, tool: BaseTool) -> None:
        if name != tool.name:
            raise ValueError(f"Tool name mismatch: {name} != {tool.name}")
        cls._tools[name] = tool
        logging.debug(f"Registered tool: {name}")
        
    @classmethod
    def get_tool(cls, name: str) -> BaseTool:
        return cls._tools.get(name)
        
    @classmethod
    def get_all_tools(cls) -> Dict[str, BaseTool]:
        return cls._tools.copy()
