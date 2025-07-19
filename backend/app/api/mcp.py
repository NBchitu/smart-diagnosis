"""
MCP工具调用API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..mcp.manager import MCPManager

logger = logging.getLogger(__name__)
router = APIRouter()

# 全局MCP管理器实例
mcp_manager = MCPManager()

class MCPCallRequest(BaseModel):
    """MCP工具调用请求"""
    server_name: str
    tool_name: str
    args: Dict[str, Any] = {}
    timeout: Optional[int] = None

class MCPInitRequest(BaseModel):
    """MCP初始化请求"""
    config_path: Optional[str] = None

@router.post("/call")
async def call_mcp_tool(request: MCPCallRequest):
    """调用MCP工具"""
    try:
        # 检查MCP管理器是否已初始化
        if not mcp_manager.client:
            logger.info("MCP管理器未初始化，正在初始化...")
            await mcp_manager.initialize()
        
        # 调用MCP工具
        result = await mcp_manager.call_tool(
            server_name=request.server_name,
            tool_name=request.tool_name,
            args=request.args,
            timeout=request.timeout
        )
        
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "server": result.server,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"调用MCP工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"调用MCP工具失败: {str(e)}")

@router.get("/tools")
async def get_mcp_tools():
    """获取可用的MCP工具列表"""
    try:
        # 检查MCP管理器是否已初始化
        if not mcp_manager.client:
            logger.info("MCP管理器未初始化，正在初始化...")
            await mcp_manager.initialize()
        
        tools = await mcp_manager.get_available_tools()
        # 打印工具列表以便调试
        logger.info("可用的MCP工具列表:")
        for server, server_tools in tools.items():
            logger.info(f"服务器 {server}:")
            for tool_name, tool_info in server_tools.items():
                logger.info(f"  - {tool_name}: {tool_info['description']}")
        return {
            "success": True,
            "tools": tools,
            "total_servers": len(tools)
        }
        
    except Exception as e:
        logger.error(f"获取MCP工具列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取MCP工具列表失败: {str(e)}")

@router.get("/status")
async def get_mcp_status():
    """获取MCP服务状态"""
    try:
        if not mcp_manager.client:
            return {
                "success": False,
                "message": "MCP管理器未初始化",
                "servers": {}
            }
        
        servers = await mcp_manager.client.list_servers()
        
        return {
            "success": True,
            "servers": servers,
            "initialized": True
        }
        
    except Exception as e:
        logger.error(f"获取MCP状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取MCP状态失败: {str(e)}")

@router.post("/initialize")
async def initialize_mcp(request: MCPInitRequest = None):
    """初始化MCP管理器"""
    try:
        config_path = request.config_path if request else None
        await mcp_manager.initialize(config_path)
        
        return {
            "success": True,
            "message": "MCP管理器初始化成功"
        }
        
    except Exception as e:
        logger.error(f"初始化MCP管理器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"初始化MCP管理器失败: {str(e)}")

@router.post("/diagnose")
async def diagnose_network_issue(request: Dict[str, Any]):
    """智能网络问题诊断"""
    try:
        issue_description = request.get("issue_description", "")
        
        if not issue_description:
            raise HTTPException(status_code=400, detail="缺少问题描述")
        
        # 检查MCP管理器是否已初始化
        if not mcp_manager.client:
            logger.info("MCP管理器未初始化，正在初始化...")
            await mcp_manager.initialize()
        
        # 执行智能诊断
        result = await mcp_manager.diagnose_network_issue(issue_description)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"网络问题诊断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"网络问题诊断失败: {str(e)}")

@router.post("/batch_call")
async def batch_call_mcp_tools(requests: list):
    """批量调用MCP工具"""
    try:
        # 检查MCP管理器是否已初始化
        if not mcp_manager.client:
            logger.info("MCP管理器未初始化，正在初始化...")
            await mcp_manager.initialize()
        
        # 转换请求格式
        mcp_requests = []
        for req in requests:
            mcp_requests.append({
                "server": req.get("server_name"),
                "tool": req.get("tool_name"),
                "args": req.get("args", {}),
                "timeout": req.get("timeout")
            })
        
        # 批量调用
        results = await mcp_manager.client.batch_call(mcp_requests)
        
        # 转换响应格式
        response_results = []
        for result in results:
            response_results.append({
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "server": result.server,
                "execution_time": result.execution_time
            })
        
        return {
            "success": True,
            "results": response_results,
            "total_requests": len(requests)
        }
        
    except Exception as e:
        logger.error(f"批量调用MCP工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量调用MCP工具失败: {str(e)}") 