"""
MCP配置管理
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import json
import os

class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    name: str
    description: str
    transport: str = "stdio"  # stdio 或 http
    command: Optional[str] = None  # stdio模式下的启动命令
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    url: Optional[str] = None  # http模式下的URL
    timeout: int = 30
    enabled: bool = True

class MCPConfig(BaseModel):
    """MCP总配置"""
    servers: Dict[str, MCPServerConfig]
    global_timeout: int = 60
    max_concurrent_requests: int = 10
    log_level: str = "INFO"
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "MCPConfig":
        """从配置文件加载"""
        if not os.path.exists(config_path):
            # 创建默认配置
            default_config = cls.get_default_config()
            default_config.save_to_file(config_path)
            return default_config
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def save_to_file(self, config_path: str):
        """保存到配置文件"""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def get_default_config(cls) -> "MCPConfig":
        """获取默认配置"""
        return cls(
            servers={
                "ping": MCPServerConfig(
                    name="ping",
                    description="Ping网络连通性检测服务",
                    command="python",
                    args=["-m", "app.mcp.servers.ping_server"],
                    enabled=True
                ),
                "wifi": MCPServerConfig(
                    name="wifi",
                    description="WiFi信号分析服务",
                    command="python",
                    args=["-m", "app.mcp.servers.wifi_server"],
                    enabled=True
                ),
                "packet": MCPServerConfig(
                    name="packet",
                    description="网络抓包分析服务",
                    command="python",
                    args=["-m", "app.mcp.servers.packet_server"],
                    enabled=True
                ),
                "gateway": MCPServerConfig(
                    name="gateway",
                    description="网关信息获取服务",
                    command="python",
                    args=["-m", "app.mcp.servers.gateway_server"],
                    enabled=True
                ),
                "connectivity": MCPServerConfig(
                    name="connectivity",
                    description="网络连通性检查服务",
                    command="python",
                    args=["-m", "app.mcp.servers.connectivity_server"],
                    enabled=True
                )
            }
        ) 