"""
MCP客户端管理
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import time

from .config import MCPConfig, MCPServerConfig

logger = logging.getLogger(__name__)

@dataclass
class MCPRequest:
    """MCP请求数据结构"""
    tool: str
    args: Dict[str, Any]
    timeout: int = 30

@dataclass
class MCPResponse:
    """MCP响应数据结构"""
    success: bool
    data: Any = None
    error: str = ""
    server: str = ""
    execution_time: float = 0

class MCPClient:
    """MCP客户端类"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.active_servers = {}
        self.server_processes = {}
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """初始化MCP客户端"""
        try:
            logger.info("初始化MCP客户端...")
            
            # 启动所有启用的服务器
            for server_name, server_config in self.config.servers.items():
                if server_config.enabled:
                    success = await self._start_server(server_name, server_config)
                    if success:
                        logger.info(f"MCP服务器 {server_name} 启动成功")
                    else:
                        logger.warning(f"MCP服务器 {server_name} 启动失败")
            
            logger.info(f"MCP客户端初始化完成，活跃服务器: {len(self.active_servers)}")
            
        except Exception as e:
            logger.error(f"MCP客户端初始化失败: {str(e)}")
            raise
    
    async def _start_server(self, server_name: str, server_config: MCPServerConfig) -> bool:
        """启动MCP服务器"""
        try:
            if server_config.transport == "stdio":
                return await self._start_stdio_server(server_name, server_config)
            elif server_config.transport == "http":
                return await self._start_http_server(server_name, server_config)
            else:
                logger.error(f"不支持的传输方式: {server_config.transport}")
                return False
                
        except Exception as e:
            logger.error(f"启动服务器 {server_name} 失败: {str(e)}")
            return False
    
    async def _start_stdio_server(self, server_name: str, server_config: MCPServerConfig) -> bool:
        """启动stdio模式的MCP服务器"""
        try:
            if not server_config.command:
                logger.error(f"服务器 {server_name} 缺少启动命令")
                return False
            
            # 构建启动命令
            cmd = [server_config.command] + server_config.args
            env = {**server_config.env} if server_config.env else None
            
            logger.info(f"正在启动MCP服务器 {server_name}: {' '.join(cmd)}")
            
            # 启动进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            logger.info(f"MCP服务器 {server_name} 进程已创建，PID: {process.pid}")
            
            # 等待进程启动
            await asyncio.sleep(2)
            
            # 检查进程是否正常运行
            return_code = process.returncode
            logger.info(f"MCP服务器 {server_name} 进程状态检查，返回码: {return_code}")
            
            if return_code is not None:
                # 进程已退出，读取错误信息
                try:
                    stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
                    stderr_text = stderr_output.decode('utf-8') if stderr_output else "无错误输出"
                    logger.error(f"服务器 {server_name} 启动失败，返回码 {return_code}，错误: {stderr_text}")
                except asyncio.TimeoutError:
                    logger.error(f"服务器 {server_name} 启动失败，返回码 {return_code}，无法读取错误输出")
                return False
            
            # 保存服务器信息
            self.active_servers[server_name] = {
                "config": server_config,
                "transport": "stdio",
                "process": process,
                "status": "running"
            }
            
            self.server_processes[server_name] = process
            
            logger.info(f"MCP服务器 {server_name} 启动成功，PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"启动stdio服务器 {server_name} 失败: {str(e)}")
            return False
    
    async def _start_http_server(self, server_name: str, server_config: MCPServerConfig) -> bool:
        """启动HTTP模式的MCP服务器"""
        try:
            # HTTP模式暂时简化实现，假设服务器已经在运行
            if not server_config.url:
                logger.error(f"HTTP服务器 {server_name} 缺少URL配置")
                return False
            
            # 测试连接
            # 这里应该发送健康检查请求
            self.active_servers[server_name] = {
                "config": server_config,
                "transport": "http",
                "url": server_config.url,
                "status": "running"
            }
            
            return True
            
        except Exception as e:
            logger.error(f"启动HTTP服务器 {server_name} 失败: {str(e)}")
            return False
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        args: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> MCPResponse:
        """调用MCP工具"""
        start_time = time.time()
        
        try:
            # 检查服务器是否存在
            if server_name not in self.active_servers:
                return MCPResponse(
                    success=False,
                    error=f"服务器 {server_name} 未找到或未启动",
                    server=server_name,
                    execution_time=time.time() - start_time
                )
            
            server_info = self.active_servers[server_name]
            effective_timeout = timeout or server_info["config"].timeout
            # 打印服务器信息
            print("=== 服务器信息 ===")
            print(f"服务器名称: {server_name}")
            print(f"服务器配置: {server_info}")
            print(f"传输方式: {server_info['transport']}")
            print(f"超时时间: {effective_timeout}秒")
            print(f"工具名称: {tool_name}")
            print(f"工具参数: {args}")
            print("================")
            # 根据传输方式调用工具
            if server_info["transport"] == "stdio":
                result = await self._call_stdio_tool(
                    server_name, tool_name, args, effective_timeout
                )
            elif server_info["transport"] == "http":
                result = await self._call_http_tool(
                    server_name, tool_name, args, effective_timeout
                )
            else:
                result = MCPResponse(
                    success=False,
                    error=f"不支持的传输方式: {server_info['transport']}",
                    server=server_name
                )
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"调用工具 {server_name}.{tool_name} 失败: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"调用异常: {str(e)}",
                server=server_name,
                execution_time=time.time() - start_time
            )
    
    async def _call_stdio_tool(
        self,
        server_name: str,
        tool_name: str,
        args: Dict[str, Any],
        timeout: int
    ) -> MCPResponse:
        """通过stdio调用工具"""
        try:
            server_info = self.active_servers[server_name]
            process = server_info["process"]
            
            logger.info(f"尝试调用MCP工具: {server_name}.{tool_name}")
            logger.info(f"服务器信息: {server_info}")
            logger.info(f"进程对象: {process}")
            
            if process is None:
                logger.error(f"服务器 {server_name} 的进程对象为None")
                return MCPResponse(
                    success=False,
                    error=f"服务器 {server_name} 的进程对象为None",
                    server=server_name
                )
            
            logger.info(f"进程返回码: {process.returncode}")
            # 检查进程状态
            if process.returncode is not None:
                logger.error(f"服务器 {server_name} 进程已退出，返回码: {process.returncode}")
                return MCPResponse(
                    success=False,
                    error=f"服务器进程已退出，返回码: {process.returncode}",
                    server=server_name
                )
            
            # 构建JSON-RPC请求
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args
                }
            }
            
            request_json = json.dumps(request) + "\n"
            logger.info(f"发送JSON-RPC请求: {request_json.strip()}")
            
            # 发送请求
            process.stdin.write(request_json.encode('utf-8'))
            await process.stdin.drain()
            
            # 读取响应
            try:
                response_line = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=timeout
                )
                
                if not response_line:
                    logger.error(f"服务器 {server_name} 无响应")
                    return MCPResponse(
                        success=False,
                        error="服务器无响应",
                        server=server_name
                    )
                
                # 解析响应
                response_text = response_line.decode('utf-8').strip()
                logger.info(f"收到响应: {response_text}")
                
                response_data = json.loads(response_text)
                
                if "error" in response_data:
                    error_msg = response_data["error"].get("message", "未知错误")
                    logger.error(f"MCP工具调用错误: {error_msg}")
                    return MCPResponse(
                        success=False,
                        error=error_msg,
                        server=server_name
                    )
                
                result = response_data.get("result")
                logger.info(f"MCP工具调用成功，结果: {result}")
                return MCPResponse(
                    success=True,
                    data=result,
                    server=server_name
                )
                
            except asyncio.TimeoutError:
                logger.error(f"MCP工具调用超时 (>{timeout}秒)")
                return MCPResponse(
                    success=False,
                    error=f"工具调用超时 (>{timeout}秒)",
                    server=server_name
                )
            except json.JSONDecodeError as e:
                logger.error(f"响应JSON解析失败: {str(e)}")
                return MCPResponse(
                    success=False,
                    error=f"响应JSON解析失败: {str(e)}",
                    server=server_name
                )
                
        except Exception as e:
            logger.error(f"stdio工具调用失败: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"stdio调用异常: {str(e)}",
                server=server_name
            )
    
    async def _call_http_tool(
        self,
        server_name: str,
        tool_name: str,
        args: Dict[str, Any],
        timeout: int
    ) -> MCPResponse:
        """通过HTTP调用工具"""
        try:
            # HTTP调用的简化实现
            # 这里应该使用aiohttp等HTTP客户端
            return MCPResponse(
                success=False,
                error="HTTP传输暂未实现",
                server=server_name
            )
            
        except Exception as e:
            logger.error(f"HTTP工具调用失败: {str(e)}")
            return MCPResponse(
                success=False,
                error=f"HTTP调用异常: {str(e)}",
                server=server_name
            )
    
    async def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """获取服务器状态"""
        try:
            if server_name not in self.active_servers:
                return {
                    "status": "not_found",
                    "message": f"服务器 {server_name} 未找到"
                }
            
            server_info = self.active_servers[server_name]
            
            if server_info["transport"] == "stdio":
                process = server_info["process"]
                if process.returncode is not None:
                    return {
                        "status": "stopped",
                        "return_code": process.returncode,
                        "message": "进程已退出"
                    }
                else:
                    return {
                        "status": "running",
                        "pid": process.pid,
                        "message": "进程正常运行"
                    }
            else:
                # HTTP服务器状态检查
                return {
                    "status": "running",
                    "url": server_info["url"],
                    "message": "HTTP服务器运行中"
                }
                
        except Exception as e:
            logger.error(f"获取服务器状态失败: {str(e)}")
            return {
                "status": "error",
                "message": f"状态检查异常: {str(e)}"
            }
    
    async def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """列出所有服务器及其状态"""
        servers = {}
        
        for server_name in self.active_servers:
            status = await self.get_server_status(server_name)
            servers[server_name] = {
                "config": self.active_servers[server_name]["config"].model_dump(),
                "status": status
            }
        
        return servers
    
    async def restart_server(self, server_name: str) -> bool:
        """重启服务器"""
        try:
            # 停止服务器
            await self.stop_server(server_name)
            
            # 等待一下
            await asyncio.sleep(1)
            
            # 重新启动
            if server_name in self.config.servers:
                server_config = self.config.servers[server_name]
                return await self._start_server(server_name, server_config)
            else:
                logger.error(f"服务器配置 {server_name} 未找到")
                return False
                
        except Exception as e:
            logger.error(f"重启服务器 {server_name} 失败: {str(e)}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """停止服务器"""
        try:
            if server_name not in self.active_servers:
                return True
            
            server_info = self.active_servers[server_name]
            
            if server_info["transport"] == "stdio":
                process = server_info["process"]
                if process.returncode is None:
                    # 优雅关闭
                    process.terminate()
                    
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        # 强制关闭
                        process.kill()
                        await process.wait()
            
            # 移除服务器记录
            del self.active_servers[server_name]
            if server_name in self.server_processes:
                del self.server_processes[server_name]
            
            logger.info(f"服务器 {server_name} 已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止服务器 {server_name} 失败: {str(e)}")
            return False
    
    async def shutdown(self):
        """关闭所有服务器"""
        try:
            logger.info("正在关闭所有MCP服务器...")
            
            # 停止所有服务器
            tasks = []
            for server_name in list(self.active_servers.keys()):
                tasks.append(self.stop_server(server_name))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("所有MCP服务器已关闭")
            
        except Exception as e:
            logger.error(f"关闭MCP服务器失败: {str(e)}")
    
    async def batch_call(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None
    ) -> List[MCPResponse]:
        """批量调用工具"""
        try:
            max_concurrent = max_concurrent or self.config.max_concurrent_requests
            
            # 创建调用任务
            tasks = []
            for req in requests:
                server_name = req.get("server")
                tool_name = req.get("tool")
                args = req.get("args", {})
                timeout = req.get("timeout")
                
                if server_name and tool_name:
                    task = self.call_tool(server_name, tool_name, args, timeout)
                    tasks.append(task)
                else:
                    # 无效请求
                    tasks.append(asyncio.create_task(asyncio.sleep(0)))
            
            # 限制并发数量
            if len(tasks) <= max_concurrent:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # 分批执行
                results = []
                for i in range(0, len(tasks), max_concurrent):
                    batch = tasks[i:i + max_concurrent]
                    batch_results = await asyncio.gather(*batch, return_exceptions=True)
                    results.extend(batch_results)
            
            # 处理异常结果
            responses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    responses.append(MCPResponse(
                        success=False,
                        error=f"批量调用异常: {str(result)}",
                        server=requests[i].get("server", "unknown")
                    ))
                elif isinstance(result, MCPResponse):
                    responses.append(result)
                else:
                    responses.append(MCPResponse(
                        success=False,
                        error="无效的响应类型",
                        server=requests[i].get("server", "unknown")
                    ))
            
            return responses
            
        except Exception as e:
            logger.error(f"批量调用失败: {str(e)}")
            return [MCPResponse(
                success=False,
                error=f"批量调用异常: {str(e)}",
                server="unknown"
            ) for _ in requests] 