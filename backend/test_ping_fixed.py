#!/usr/bin/env python3
"""
测试修复版ping_server的脚本
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_ping_server_fixed():
    """测试修复版ping_server"""
    
    print("=== 测试修复版 ping_server ===")
    
    # 启动修复版ping_server进程
    process = await asyncio.create_subprocess_exec(
        sys.executable, "ping_server_fixed.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("修复版ping_server 进程已启动")
    
    try:
        # 等待服务器启动
        await asyncio.sleep(1)
        
        # 测试1：标准MCP工具调用格式
        print("\n--- 测试1：标准MCP工具调用格式 ---")
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
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    if "result" in response_data:
                        result = response_data["result"]
                        print(f"Ping结果: 主机={result.get('host')}, 成功={result.get('success')}, 丢包率={result.get('packet_loss', 'N/A')}%")
                    else:
                        print(f"错误: {response_data.get('error', {}).get('message', '未知错误')}")
                except json.JSONDecodeError:
                    print(f"响应不是有效JSON: {response}")
            else:
                print("未收到响应")
        except asyncio.TimeoutError:
            print("响应超时")
        
        # 测试2：直接函数调用格式
        print("\n--- 测试2：直接函数调用格式 ---")
        request2 = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "ping_host",
            "params": {
                "host": "google.com",
                "count": 2,
                "timeout": 5
            }
        }
        
        request_json = json.dumps(request2) + "\n"
        print(f"发送请求: {request_json.strip()}")
        
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    if "result" in response_data:
                        result = response_data["result"]
                        print(f"Ping结果: 主机={result.get('host')}, 成功={result.get('success')}, 丢包率={result.get('packet_loss', 'N/A')}%")
                    else:
                        print(f"错误: {response_data.get('error', {}).get('message', '未知错误')}")
                except json.JSONDecodeError:
                    print(f"响应不是有效JSON: {response}")
            else:
                print("未收到响应")
        except asyncio.TimeoutError:
            print("响应超时")
        
        # 测试3：列出工具
        print("\n--- 测试3：列出可用工具 ---")
        request3 = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(request3) + "\n"
        print(f"发送请求: {request_json.strip()}")
        
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5)
            if response_line:
                response = response_line.decode('utf-8').strip()
                print(f"收到响应: {response}")
                try:
                    response_data = json.loads(response)
                    if "result" in response_data:
                        tools = response_data["result"]["tools"]
                        print(f"可用工具: {[tool['name'] for tool in tools]}")
                    else:
                        print(f"错误: {response_data.get('error', {}).get('message', '未知错误')}")
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
    # 切换到正确的目录
    os.chdir("app/mcp/servers")
    asyncio.run(test_ping_server_fixed()) 