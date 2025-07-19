#!/usr/bin/env python3
"""
直接测试MCP服务器的脚本
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.mcp.manager import MCPManager

async def test_mcp_direct():
    """直接测试MCP服务器"""
    
    # 创建MCP管理器
    manager = MCPManager()
    
    # 初始化
    await manager.initialize()
    
    # 测试ping工具
    print("=== 测试 ping 工具 ===")
    
    # 测试1：简单ping
    print("\n测试1：简单ping")
    response = await manager.call_tool("ping", "ping_host", {"host": "baidu.com"})
    print(f"响应: {response}")
    
    # 测试2：带参数的ping
    print("\n测试2：带参数的ping")
    response = await manager.call_tool("ping", "ping_host", {
        "host": "baidu.com",
        "count": 3,
        "timeout": 5
    })
    print(f"响应: {response}")
    
    # 测试3：无效参数
    print("\n测试3：无效参数")
    response = await manager.call_tool("ping", "ping_host", {
        "invalid_param": "test"
    })
    print(f"响应: {response}")
    
    # 测试4：检查服务器状态
    print("\n测试4：服务器状态")
    status = await manager.get_server_status()
    print(f"状态: {json.dumps(status, indent=2)}")
    
    # 关闭
    await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_mcp_direct()) 