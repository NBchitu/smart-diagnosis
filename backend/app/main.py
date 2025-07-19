from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
import logging
from typing import Dict, List
from contextlib import asynccontextmanager

from app.api import network, wifi, router, ai, system, mcp, capture
from app.core.websocket import WebSocketManager
from app.mcp.manager import mcp_manager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化MCP管理器
    try:
        logger.info("正在初始化MCP管理器...")
        await mcp_manager.initialize()
        logger.info("MCP管理器初始化完成")
    except Exception as e:
        logger.error(f"MCP管理器初始化失败: {str(e)}")
        # 不中断应用启动，允许在没有MCP的情况下运行
    
    yield
    
    # 关闭时清理MCP资源
    try:
        logger.info("正在关闭MCP管理器...")
        await mcp_manager.shutdown()
        logger.info("MCP管理器已关闭")
    except Exception as e:
        logger.error(f"MCP管理器关闭失败: {str(e)}")

app = FastAPI(
    title="网络检测工具 API",
    description="基于树莓派5的网络检测和诊断工具，集成MCP智能诊断功能",
    version="1.0.0",
    lifespan=lifespan
)

# WebSocket管理器
ws_manager = WebSocketManager()

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.4.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由
app.include_router(network.router, prefix="/api/network", tags=["network"])
app.include_router(wifi.router, prefix="/api/wifi", tags=["wifi"])
app.include_router(router.router, prefix="/api/router", tags=["router"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(capture.router, prefix="/api/capture", tags=["capture"])

# 挂载网站截图静态文件目录
from pathlib import Path
screenshot_static_dir = Path(__file__).parent.parent / "data" / "website_screenshots"
app.mount("/static/website_screenshots", StaticFiles(directory=screenshot_static_dir, html=False), name="website_screenshots")

@app.get("/")
async def root():
    return {"message": "网络检测工具 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API正常运行"}

@app.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket, endpoint: str):
    await ws_manager.connect(websocket, endpoint)
    try:
        while True:
            # 保持连接并处理消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 根据endpoint处理不同的消息
            if endpoint == "network-test":
                await handle_network_test(websocket, message)
            elif endpoint == "wifi-signal":
                await handle_wifi_signal(websocket, message)
            elif endpoint == "system-status":
                await handle_system_status(websocket, message)
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, endpoint)

async def handle_network_test(websocket: WebSocket, message: Dict):
    """处理网络测试WebSocket消息"""
    # 这里将集成网络测试逻辑
    await websocket.send_json({
        "type": "network_test_progress", 
        "data": {"progress": 0, "status": "starting"}
    })

async def handle_wifi_signal(websocket: WebSocket, message: Dict):
    """处理WiFi信号监控WebSocket消息"""
    # 这里将集成WiFi信号监控逻辑
    await websocket.send_json({
        "type": "wifi_signal_update",
        "data": {"strength": -45, "quality": 85}
    })

async def handle_system_status(websocket: WebSocket, message: Dict):
    """处理系统状态监控WebSocket消息"""
    # 这里将集成系统状态监控逻辑
    await websocket.send_json({
        "type": "system_status_update",
        "data": {"cpu": 25, "memory": 512, "temperature": 45}
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 