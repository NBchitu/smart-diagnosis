#!/usr/bin/env python3
"""
带流量生成的抓包功能测试脚本
用于验证抓包分析功能是否能正确捕获和分析网络流量
"""

import asyncio
import sys
import os
import time
import json
import threading
import requests
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.mcp.servers.packet_capture_server import PacketCaptureServer

class TrafficGenerator:
    """网络流量生成器"""
    
    def __init__(self):
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def start_http_traffic(self, duration: int = 10):
        """生成HTTP流量"""
        def make_requests():
            urls = [
                "http://httpbin.org/get",
                "http://httpbin.org/status/200",
                "http://httpbin.org/headers",
                "http://www.baidu.com",
                "http://www.sina.com.cn"
            ]
            
            start_time = time.time()
            while time.time() - start_time < duration and self.running:
                for url in urls:
                    if not self.running:
                        break
                    try:
                        requests.get(url, timeout=5)
                        print(f"✅ HTTP请求: {url}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"❌ HTTP请求失败: {url} - {e}")
                        time.sleep(0.5)
        
        self.running = True
        future = self.executor.submit(make_requests)
        return future
    
    def start_dns_traffic(self, duration: int = 10):
        """生成DNS流量"""
        def make_dns_queries():
            domains = [
                "baidu.com",
                "google.com", 
                "github.com",
                "stackoverflow.com",
                "python.org"
            ]
            
            start_time = time.time()
            while time.time() - start_time < duration and self.running:
                for domain in domains:
                    if not self.running:
                        break
                    try:
                        socket.gethostbyname(domain)
                        print(f"🔍 DNS查询: {domain}")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"❌ DNS查询失败: {domain} - {e}")
                        time.sleep(0.5)
        
        future = self.executor.submit(make_dns_queries)
        return future
    
    def start_tcp_traffic(self, duration: int = 10):
        """生成TCP连接流量"""
        def make_tcp_connections():
            hosts = [
                ("baidu.com", 80),
                ("google.com", 80),
                ("github.com", 443),
                ("stackoverflow.com", 443)
            ]
            
            start_time = time.time()
            while time.time() - start_time < duration and self.running:
                for host, port in hosts:
                    if not self.running:
                        break
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        
                        # 解析主机名
                        ip = socket.gethostbyname(host)
                        
                        # 建立连接
                        sock.connect((ip, port))
                        print(f"🔗 TCP连接: {host}:{port} ({ip})")
                        
                        # 保持连接一小段时间
                        time.sleep(0.5)
                        sock.close()
                        
                        time.sleep(1)
                    except Exception as e:
                        print(f"❌ TCP连接失败: {host}:{port} - {e}")
                        time.sleep(0.5)
        
        future = self.executor.submit(make_tcp_connections)
        return future
    
    def stop(self):
        """停止流量生成"""
        self.running = False

class PacketCaptureTestWithTraffic:
    """带流量生成的抓包功能测试类"""
    
    def __init__(self):
        self.capture_server = PacketCaptureServer()
        self.traffic_generator = TrafficGenerator()
    
    async def test_permissions(self):
        """测试抓包权限"""
        print("🔒 测试抓包权限...")
        has_permission = self.capture_server._check_permissions()
        if has_permission:
            print("✅ 抓包权限检查通过")
        else:
            print("❌ 缺少抓包权限，请使用sudo运行")
        return has_permission
    
    async def test_interfaces(self):
        """测试网络接口获取（改进版）"""
        print("\n🌐 测试网络接口获取...")
        result = await self.capture_server.list_interfaces()
        
        if result["success"]:
            interfaces = result["interfaces"]
            print(f"✅ 发现 {len(interfaces)} 个网络接口:")
            for interface in interfaces[:10]:  # 只显示前10个
                print(f"   - {interface}")
            if len(interfaces) > 10:
                print(f"   ... 还有 {len(interfaces) - 10} 个接口")
        else:
            print("❌ 网络接口获取失败")
        
        return result["success"]
    
    async def test_capture_with_http_traffic(self, duration: int = 15):
        """测试HTTP流量抓包"""
        print(f"\n🌐 测试HTTP流量抓包 (时长: {duration}秒)...")
        
        # 使用实际的网络接口而不是回环接口
        interfaces_result = await self.capture_server.list_interfaces()
        if interfaces_result["success"]:
            interfaces = interfaces_result["interfaces"]
            # 选择一个实际的网络接口
            interface = None
            for iface in interfaces:
                if iface.startswith('en') or iface.startswith('eth') or iface.startswith('wlan'):
                    interface = iface
                    break
            
            if not interface and interfaces:
                interface = interfaces[0]
            
            print(f"使用网络接口: {interface}")
        
        # 启动抓包
        start_result = await self.capture_server.start_capture(
            target="web",
            capture_type="web",
            duration=duration,
            interface=interface
        )
        
        if not start_result["success"]:
            print(f"❌ HTTP抓包启动失败: {start_result.get('error', '未知错误')}")
            return False
        
        session_id = start_result["session_id"]
        print(f"✅ HTTP抓包会话已启动: {session_id}")
        
        # 启动HTTP流量生成
        print("🚀 开始生成HTTP流量...")
        http_future = self.traffic_generator.start_http_traffic(duration - 2)
        
        # 等待并显示进度
        for i in range(duration):
            await asyncio.sleep(1)
            status_result = await self.capture_server.get_session_status(session_id)
            
            if i % 3 == 0:  # 每3秒显示一次状态
                packets_captured = status_result.get("packets_captured", 0) if status_result["success"] else 0
                print(f"   进度: {i+1}/{duration}秒, 已抓取: {packets_captured} 个包")
        
        # 停止流量生成
        self.traffic_generator.stop()
        
        # 停止抓包并分析
        print("📊 停止抓包并分析结果...")
        stop_result = await self.capture_server.stop_capture(session_id)
        
        if stop_result["success"]:
            analysis = stop_result["analysis"]
            packets_count = stop_result["packets_captured"]
            
            print(f"\n📈 HTTP流量抓包分析:")
            print(f"   - 总包数: {packets_count}")
            print(f"   - HTTP请求: {analysis['summary']['packet_types'].get('HTTP_REQUEST', 0)}")
            print(f"   - DNS查询: {analysis['summary']['packet_types'].get('DNS_QUERY', 0)}")
            print(f"   - TCP连接: {analysis['summary']['protocols'].get('TCP', 0)}")
            print(f"   - 连接数: {len(analysis['connections'])}")
            
            if analysis['issues']:
                print("\n⚠️  检测到的问题:")
                for issue in analysis['issues']:
                    print(f"   - {issue['type']}: {issue['description']}")
            
            print("✅ HTTP流量抓包测试完成")
            return packets_count > 0
        else:
            print(f"❌ HTTP抓包分析失败: {stop_result.get('error', '未知错误')}")
            return False
    
    async def test_capture_with_dns_traffic(self, domain: str = "baidu.com", duration: int = 10):
        """测试DNS流量抓包"""
        print(f"\n🔍 测试DNS流量抓包 (目标: {domain}, 时长: {duration}秒)...")
        
        # 启动DNS抓包
        start_result = await self.capture_server.start_capture(
            target=domain,
            capture_type="domain",
            duration=duration
        )
        
        if not start_result["success"]:
            print(f"❌ DNS抓包启动失败: {start_result.get('error', '未知错误')}")
            return False
        
        session_id = start_result["session_id"]
        print(f"✅ DNS抓包会话已启动: {session_id}")
        
        # 启动DNS流量生成
        print("🚀 开始生成DNS查询...")
        dns_future = self.traffic_generator.start_dns_traffic(duration - 2)
        
        # 启动TCP连接生成
        print("🚀 开始生成TCP连接...")
        tcp_future = self.traffic_generator.start_tcp_traffic(duration - 2)
        
        # 等待
        for i in range(duration):
            await asyncio.sleep(1)
            if i % 2 == 0:
                status_result = await self.capture_server.get_session_status(session_id)
                packets_captured = status_result.get("packets_captured", 0) if status_result["success"] else 0
                print(f"   进度: {i+1}/{duration}秒, 已抓取: {packets_captured} 个包")
        
        # 停止流量生成
        self.traffic_generator.stop()
        
        # 停止抓包并分析
        stop_result = await self.capture_server.stop_capture(session_id)
        
        if stop_result["success"]:
            analysis = stop_result["analysis"]
            packets_count = stop_result["packets_captured"]
            
            print(f"\n📈 DNS流量抓包分析:")
            print(f"   - 总包数: {packets_count}")
            print(f"   - 协议分布: {analysis['summary']['protocols']}")
            print(f"   - 包类型分布: {analysis['summary']['packet_types']}")
            print(f"   - 连接数: {len(analysis['connections'])}")
            
            if analysis['connections']:
                print("   - 主要连接:")
                for conn in analysis['connections'][:3]:  # 显示前3个连接
                    print(f"     {conn['src']} -> {conn['dst']} ({conn['packet_count']}包)")
            
            print("✅ DNS流量抓包测试完成")
            return packets_count > 0
        else:
            print(f"❌ DNS抓包分析失败: {stop_result.get('error', '未知错误')}")
            return False
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始抓包功能综合测试（带流量生成）\n")
        print("=" * 70)
        
        results = []
        
        # 1. 权限测试
        perm_result = await self.test_permissions()
        results.append(("权限检查", perm_result))
        
        if not perm_result:
            print("\n❌ 由于权限问题，无法继续测试")
            return False
        
        # 2. 接口测试
        interface_result = await self.test_interfaces()
        results.append(("网络接口", interface_result))
        
        # 3. HTTP流量抓包测试
        http_result = await self.test_capture_with_http_traffic(12)
        results.append(("HTTP流量抓包", http_result))
        
        # 4. DNS流量抓包测试
        dns_result = await self.test_capture_with_dns_traffic("google.com", 10)
        results.append(("DNS流量抓包", dns_result))
        
        # 测试结果汇总
        print("\n" + "=" * 70)
        print("📋 测试结果汇总:")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name:15} : {status}")
            if result:
                passed += 1
        
        print(f"\n📊 总体结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！抓包功能正常工作，可以捕获真实网络流量")
        elif passed >= total * 0.75:
            print("⚠️  大部分测试通过，抓包功能基本正常")
        else:
            print("❌ 多个测试失败，请检查网络配置和权限")
        
        return passed >= total * 0.75

async def main():
    """主函数"""
    print("📡 智能抓包分析功能测试（带流量生成）")
    print("这个测试将生成真实网络流量来验证抓包分析功能")
    print("注意：抓包需要管理员权限\n")
    
    # 检查是否以管理员权限运行
    if os.geteuid() != 0:
        print("⚠️  警告: 当前未以管理员权限运行")
        print("   请使用: sudo python3 test_packet_capture_with_traffic.py")
        print()
        return
    
    tester = PacketCaptureTestWithTraffic()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            print("\n✅ 抓包功能测试完成，可以继续集成到MCP客户端")
            print("💡 建议：在实际使用中选择合适的网络接口和过滤条件")
        else:
            print("\n❌ 抓包功能存在问题，请检查后再集成")
            
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
        tester.traffic_generator.stop()
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        tester.traffic_generator.stop()

if __name__ == "__main__":
    asyncio.run(main()) 