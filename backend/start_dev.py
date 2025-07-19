#!/usr/bin/env python3
"""
开发环境启动脚本
用于在开发过程中快速启动FastAPI服务器
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动网络检测工具后端服务...")
    print("📍 API文档地址: http://localhost:8000/docs")
    print("📍 前端连接地址: http://localhost:8000")
    print("📍 WebSocket测试: ws://localhost:8000/ws/")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1) 