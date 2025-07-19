#!/usr/bin/env python3
"""
简化的抓包功能测试脚本
使用正确的网络接口和宽松的过滤条件来验证抓包基础功能
"""

import asyncio
import subprocess
import time
import signal
import os
import threading
import requests

def test_tcpdump_basic():
    """基础tcpdump测试"""
    print("🔧 测试基础tcpdump功能...")
    
    try:
        # 使用en0接口，简单的过滤条件
        cmd = ["tcpdump", "-i", "en0", "-c", "5", "-n", "tcp"]
        print(f"执行命令: {' '.join(cmd)}")
        
        # 启动tcpdump
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 在后台生成一些流量
        def generate_traffic():
            time.sleep(1)
            try:
                requests.get("http://httpbin.org/get", timeout=5)
                print("✅ 生成了HTTP流量")
            except:
                print("❌ HTTP流量生成失败")
        
        traffic_thread = threading.Thread(target=generate_traffic)
        traffic_thread.start()
        
        # 等待结果
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        print(f"返回码: {process.returncode}")
        
        if stdout:
            lines = stdout.strip().split('\n')
            print(f"✅ 捕获到 {len(lines)} 行输出")
            for i, line in enumerate(lines[:3]):  # 显示前3行
                print(f"   {i+1}: {line}")
            return True
        else:
            print("❌ 没有捕获到任何输出")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ tcpdump超时")
        return False
    except Exception as e:
        print(f"❌ tcpdump测试失败: {e}")
        return False

def test_ping_capture():
    """测试ping流量抓包"""
    print("\n🏓 测试ping流量抓包...")
    
    try:
        # 启动tcpdump抓取ICMP包
        cmd = ["tcpdump", "-i", "en0", "-c", "5", "-n", "icmp"]
        print(f"执行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 生成ping流量
        def generate_ping():
            time.sleep(1)
            try:
                ping_result = subprocess.run(
                    ["ping", "-c", "3", "baidu.com"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                print(f"✅ Ping完成，返回码: {ping_result.returncode}")
            except Exception as e:
                print(f"❌ Ping失败: {e}")
        
        ping_thread = threading.Thread(target=generate_ping)
        ping_thread.start()
        
        # 等待tcpdump结果
        stdout, stderr = process.communicate(timeout=15)
        
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        
        if stdout and "ICMP" in stdout:
            print("✅ 成功捕获到ICMP流量")
            return True
        else:
            print("❌ 没有捕获到ICMP流量")
            return False
            
    except Exception as e:
        print(f"❌ Ping抓包测试失败: {e}")
        return False

def test_dns_capture():
    """测试DNS流量抓包"""
    print("\n🔍 测试DNS流量抓包...")
    
    try:
        # 启动tcpdump抓取DNS包
        cmd = ["tcpdump", "-i", "en0", "-c", "5", "-n", "port 53"]
        print(f"执行命令: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 生成DNS查询
        def generate_dns():
            time.sleep(1)
            try:
                import socket
                # 进行DNS查询
                for domain in ["google.com", "baidu.com", "github.com"]:
                    socket.gethostbyname(domain)
                    print(f"✅ DNS查询: {domain}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"❌ DNS查询失败: {e}")
        
        dns_thread = threading.Thread(target=generate_dns)
        dns_thread.start()
        
        # 等待tcpdump结果
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        
        if stdout and ("53" in stdout or "domain" in stdout):
            print("✅ 成功捕获到DNS流量")
            return True
        else:
            print("❌ 没有捕获到DNS流量")
            return False
            
    except Exception as e:
        print(f"❌ DNS抓包测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("📡 简化抓包功能测试")
    print("使用en0接口和基础过滤条件\n")
    
    if os.geteuid() != 0:
        print("⚠️  警告: 需要管理员权限")
        print("请使用: sudo python3 test_packet_simple.py")
        return
    
    results = []
    
    # 1. 基础TCP抓包测试
    tcp_result = test_tcpdump_basic()
    results.append(("TCP流量抓包", tcp_result))
    
    # 2. ICMP ping抓包测试
    ping_result = test_ping_capture()
    results.append(("ICMP流量抓包", ping_result))
    
    # 3. DNS抓包测试
    dns_result = test_dns_capture()
    results.append(("DNS流量抓包", dns_result))
    
    # 结果汇总
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{total} 通过")
    
    if passed >= total * 0.7:
        print("🎉 抓包基础功能正常！")
        print("💡 可以继续优化抓包服务器的过滤条件和接口选择")
    else:
        print("❌ 抓包功能存在问题，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main()) 