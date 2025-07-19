from fastapi import WebSocket
from typing import Dict, List
import json

class WebSocketManager:
    def __init__(self):
        # 存储不同端点的WebSocket连接
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, endpoint: str):
        """接受WebSocket连接"""
        await websocket.accept()
        
        if endpoint not in self.active_connections:
            self.active_connections[endpoint] = []
        
        self.active_connections[endpoint].append(websocket)
        print(f"WebSocket连接已建立: {endpoint}")
    
    def disconnect(self, websocket: WebSocket, endpoint: str):
        """断开WebSocket连接"""
        if endpoint in self.active_connections:
            self.active_connections[endpoint].remove(websocket)
            print(f"WebSocket连接已断开: {endpoint}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_endpoint(self, endpoint: str, message: dict):
        """向特定端点广播消息"""
        if endpoint in self.active_connections:
            for connection in self.active_connections[endpoint]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # 连接断开，移除连接
                    self.active_connections[endpoint].remove(connection)
    
    async def broadcast_all(self, message: dict):
        """向所有连接广播消息"""
        for endpoint, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # 连接断开，移除连接
                    connections.remove(connection) 