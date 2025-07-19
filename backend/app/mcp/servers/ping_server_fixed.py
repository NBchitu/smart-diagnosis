#!/usr/bin/env python3
"""
Ping网络连通性检测MCP服务器 - 标准MCP协议实现
"""

import asyncio
import json
import sys
import platform
import subprocess
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

async def ping_host(host: str, count: int = 3, timeout: int = 5, packet_size: int = 32) -> Dict[str, Any]:
    """
    执行ping命令并返回结果
    """
    try:
        # 根据操作系统构建ping命令
        cmd = _build_ping_command(host, count, timeout, packet_size)
        
        # 执行ping命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 等待完成
        stdout, stderr = await process.communicate()
        
        # 解析结果
        output = stdout.decode('utf-8') if stdout else ""
        error = stderr.decode('utf-8') if stderr else ""
        
        # 解析ping统计信息
        stats = _parse_ping_stats(output)
        
        result = {
            "host": host,
            "success": process.returncode == 0,
            "output": output,
            "error": error,
            "return_code": process.returncode,
            "packets_transmitted": stats.get("packets_transmitted", count),
            "packets_received": stats.get("packets_received", 0),
            "packet_loss": stats.get("packet_loss", 0.0),
            "min_time": stats.get("min_time", 0.0),
            "max_time": stats.get("max_time", 0.0),
            "avg_time": stats.get("avg_time", 0.0),
            "times": stats.get("times", [])
        }
        
        return result
        
    except Exception as e:
        return {
            "host": host,
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1,
            "packets_transmitted": 0,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_time": 0.0,
            "max_time": 0.0,
            "avg_time": 0.0,
            "times": []
        }

def _build_ping_command(host: str, count: int, timeout: int, packet_size: int) -> List[str]:
    """根据操作系统构建ping命令"""
    system = platform.system().lower()
    
    if system == "windows":
        # Windows ping命令
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), "-l", str(packet_size), host]
    elif system == "darwin":  # macOS
        # macOS ping命令
        cmd = ["ping", "-c", str(count), "-W", str(timeout * 1000), "-s", str(packet_size), host]
    else:  # Linux和其他Unix系统
        # Linux ping命令
        cmd = ["ping", "-c", str(count), "-W", str(timeout), "-s", str(packet_size), host]
    
    return cmd

def _parse_ping_stats(output: str) -> Dict:
    """解析ping命令输出"""
    result = {
        "packets_transmitted": 0,
        "packets_received": 0,
        "packet_loss": 0.0,
        "min_time": 0.0,
        "max_time": 0.0,
        "avg_time": 0.0,
        "times": []
    }
    
    try:
        lines = output.split('\n')
        
        # 解析统计信息
        for line in lines:
            if "packets transmitted" in line:
                parts = line.split()
                result["packets_transmitted"] = int(parts[0])
                received_idx = parts.index("received,") if "received," in parts else parts.index("received")
                result["packets_received"] = int(parts[received_idx - 1])
                
                # 提取丢包率
                if "packet loss" in line:
                    loss_part = line.split("packet loss")[0].split()[-1]
                    result["packet_loss"] = float(loss_part.replace('%', ''))
            
            elif "round-trip" in line or "rtt" in line:
                # 解析时间统计 (min/avg/max)
                parts = line.split("=")[-1].strip().split("/")
                if len(parts) >= 3:
                    result["min_time"] = float(parts[0])
                    result["avg_time"] = float(parts[1])
                    result["max_time"] = float(parts[2])
            
            elif "time=" in line:
                # 提取单次ping时间
                time_part = line.split("time=")[1].split()[0]
                result["times"].append(float(time_part))
                
    except (ValueError, IndexError) as e:
        logger.warning(f"解析ping输出失败: {str(e)}")
    
    return result

class MCPServer:
    """标准MCP服务器实现"""
    
    def __init__(self):
        self.tools = {
            "ping_host": {
                "function": ping_host,
                "description": "Ping指定主机检测网络连通性",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "目标主机地址"},
                        "count": {"type": "integer", "description": "Ping次数", "default": 4},
                        "timeout": {"type": "integer", "description": "超时时间(秒)", "default": 10},
                        "packet_size": {"type": "integer", "description": "数据包大小", "default": 32}
                    },
                    "required": ["host"]
                }
            }
        }
    
    async def handle_request(self, request: Dict) -> Dict:
        """处理JSON-RPC请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "tools/call":
                # 标准MCP工具调用格式
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    result = await self._call_tool(tool_name, arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
            
            elif method in self.tools:
                # 直接工具调用格式
                result = await self._call_tool(method, params)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "tools/list":
                # 列出可用工具
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": info["description"],
                                "inputSchema": info["parameters"]
                            }
                            for name, info in self.tools.items()
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """调用指定工具"""
        tool_info = self.tools[tool_name]
        tool_function = tool_info["function"]
        
        # 调用工具函数
        result = await tool_function(**arguments)
        return result
    
    async def run(self):
        """运行MCP服务器"""
        while True:
            try:
                # 读取JSON-RPC请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    
                    # 发送响应
                    response_json = json.dumps(response)
                    print(response_json, flush=True)
                    
                except json.JSONDecodeError as e:
                    # 发送JSON解析错误响应
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    response_json = json.dumps(error_response)
                    print(response_json, flush=True)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"服务器运行错误: {e}")
                break

def main():
    """运行MCP服务器"""
    server = MCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main() 