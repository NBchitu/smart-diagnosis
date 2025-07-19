#!/usr/bin/env python3
"""
网络连通性检测功能测试脚本
"""

import asyncio
import json
from app.services.network_service import NetworkService

async def test_connectivity():
    """测试网络连通性检测功能"""
    print("开始测试网络连通性检测功能...")
    
    network_service = NetworkService()
    
    try:
        result = await network_service.check_internet_connectivity()
        
        print("\n=== 网络连通性检测结果 ===")
        print(f"状态: {result.get('status', 'unknown')}")
        print(f"消息: {result.get('message', 'No message')}")
        print(f"检测时间: {result.get('timestamp', 'unknown')}")
        
        print("\n=== 详细检测结果 ===")
        print(f"本地网络: {'✅' if result.get('local_network') else '❌'}")
        print(f"DNS解析: {'✅' if result.get('internet_dns') else '❌'}")
        print(f"HTTP连通: {'✅' if result.get('internet_http') else '❌'}")
        
        details = result.get('details', {})
        print(f"网关可达: {'✅' if details.get('gateway_reachable') else '❌'}")
        print(f"DNS功能: {'✅' if details.get('dns_resolution') else '❌'}")
        print(f"外网ping: {'✅' if details.get('external_ping') else '❌'}")
        print(f"HTTP响应: {'✅' if details.get('http_response') else '❌'}")
        
        latency = result.get('latency', {})
        if latency:
            print("\n=== 延迟信息 ===")
            for host, ms in latency.items():
                print(f"{host}: {ms:.1f}ms")
        
        print(f"\n=== 完整JSON结果 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connectivity()) 