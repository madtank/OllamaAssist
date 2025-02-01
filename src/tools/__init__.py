from .registry import ToolRegistry
from .brave import BraveSearchTool
from .filesystem import FilesystemTool
from .base import BaseTool

# Register available tools
ToolRegistry.register("brave", BraveSearchTool())
ToolRegistry.register("filesystem", FilesystemTool())

__all__ = ['ToolRegistry', 'BaseTool']
