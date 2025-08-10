"""
Graphics Backend Interface for 2Top Geometry Library

Provides rendering data extraction and visualization APIs for front-end
applications and external services.
"""

from .graphics_interface import GraphicsBackendInterface
from .mcp_handler import MCPCommandHandler

__all__ = ['GraphicsBackendInterface', 'MCPCommandHandler']
