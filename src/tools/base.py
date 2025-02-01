from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool's main functionality"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used for registration"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """Tool parameters schema"""
        pass
