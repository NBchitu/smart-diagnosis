#!/usr/bin/env python3
"""
直接与ping_server进行stdio通信的测试脚本
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_ping_server_direct():
    """直接测试ping_server的stdio通信"""
    
    print("=== 直接测试 ping_server stdio 通信 ===")
    
    # 启动ping_server进程
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "app.mcp.servers.ping_server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("ping_server 进程已启动")
    
    try:
        # 等待服务器启动
        await asyncio.sleep(2)
        
        # 测试不同的JSON-RPC请求格式
        
        # 格式1：标准MCP格式
        print("\n--- 测试格式1：标准MCP工具调用格式 ---")
        request1 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "ping_host",
                "arguments": {
                    "host": "baidu.com",
                    "count": 3
                }
            }
        }
        
        request_json = json.dumps(request1) + "\n"
        print(f"发送请求: {request_json.strip()}")
        
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()
        
        # 读取响应
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    print(f"解析后的响应: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"响应不是有效JSON: {response}")
            else:
                print("未收到响应")
        except asyncio.TimeoutError:
            print("响应超时")
        
        # 格式2：直接函数调用格式
        print("\n--- 测试格式2：直接函数调用格式 ---")
        request2 = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "ping_host",
            "params": {
                "host": "baidu.com",
                "count": 3
            }
        }
        
        request_json = json.dumps(request2) + "\n"
        print(f"发送请求: {request_json.strip()}")
        
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    print(f"解析后的响应: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"响应不是有效JSON: {response}")
            else:
                print("未收到响应")
        except asyncio.TimeoutError:
            print("响应超时")
        
        # 格式3：FastMCP期望的格式（如果有特殊格式）
        print("\n--- 测试格式3：位置参数格式 ---")
        request3 = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "ping_host",
            "params": ["baidu.com", 3, 10, 32]
        }
        
        request_json = json.dumps(request3) + "\n"
        print(f"发送请求: {request_json.strip()}")
        
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    print(f"解析后的响应: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"响应不是有效JSON: {response}")
            else:
                print("未收到响应")
        except asyncio.TimeoutError:
            print("响应超时")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
    
    finally:
        # 清理
        print("\n--- 清理进程 ---")
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        print("ping_server 进程已终止")

if __name__ == "__main__":
    asyncio.run(test_ping_server_direct()) 