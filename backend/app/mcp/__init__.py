"""
MCP (Model Context Protocol) 集成模块
用于网络诊断工具的智能体调用
"""

from .client import MCPClient
from .manager import MCPManager
from .config import MCPConfig

__all__ = ['MCPClient', 'MCPManager', 'MCPConfig'] 