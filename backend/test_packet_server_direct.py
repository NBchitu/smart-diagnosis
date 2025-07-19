#!/usr/bin/env python3
"""
直接测试优化后的抓包服务器
验证网络接口选择和过滤条件优化是否有效
"""

import asyncio
import sys
import os
import time
import json
import threading
import requests
import subprocess

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.mcp.servers.packet_capture_server import PacketCaptureServer

class OptimizedPacketCaptureTest:
    """优化后的抓包服务器测试"""
    
    def __init__(self):
        self.capture_server = PacketCaptureServer()
    
    async def test_interface_detection(self):
        """测试优化后的网络接口检测"""
        print("🌐 测试优化后的网络接口检测...")
        
        result = await self.capture_server.list_interfaces()
        
        if result["success"]:
            interfaces = result["interfaces"]
            print(f"✅ 检测到 {len(interfaces)} 个活跃网络接口:")
            for i, interface in enumerate(interfaces):
                status = "⭐ (首选)" if i == 0 else "📡"
                print(f"   {status} {interface}")
            
            # 验证en0是否在首位
            if interfaces and interfaces[0] == "en0":
                print("✅ en0已正确设为首选接口")
            
            return True
        else:
            print(f"❌ 接口检测失败: {result.get('error', '未知错误')}")
            return False
    
    async def test_capture_with_traffic_generation(self):
        """测试抓包功能并生成流量"""
        print("\n📦 测试抓包功能（带流量生成）...")
        
        # 启动诊断模式抓包
        start_result = await self.capture_server.start_capture(
            target="diagnostic",
            capture_type="diagnostic",
            duration=15
        )
        
        if not start_result["success"]:
            print(f"❌ 抓包启动失败: {start_result.get('error', '未知错误')}")
            return False
        
        session_id = start_result["session_id"]
        print(f"✅ 抓包会话已启动: {session_id}")
        print(f"🔍 使用过滤器: {start_result.get('filter', 'unknown')}")
        
        # 在后台生成网络流量
        def generate_mixed_traffic():
            time.sleep(2)
            
            # 1. 生成HTTP流量
            try:
                requests.get("http://httpbin.org/get", timeout=5)
                print("✅ HTTP流量: httpbin.org")
            except Exception as e:
                print(f"❌ HTTP流量失败: {e}")
            
            time.sleep(1)
            
            # 2. 生成ping流量
            try:
                subprocess.run(["ping", "-c", "3", "baidu.com"], 
                             capture_output=True, timeout=10)
                print("✅ ICMP流量: ping baidu.com")
            except Exception as e:
                print(f"❌ ICMP流量失败: {e}")
            
            time.sleep(1)
            
            # 3. 生成DNS查询
            try:
                import socket
                for domain in ["google.com", "github.com"]:
                    socket.gethostbyname(domain)
                    print(f"✅ DNS查询: {domain}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"❌ DNS查询失败: {e}")
            
            time.sleep(1)
            
            # 4. 生成HTTPS流量
            try:
                requests.get("https://httpbin.org/get", timeout=5)
                print("✅ HTTPS流量: httpbin.org")
            except Exception as e:
                print(f"❌ HTTPS流量失败: {e}")
        
        # 启动流量生成线程
        traffic_thread = threading.Thread(target=generate_mixed_traffic)
        traffic_thread.start()
        
        # 监控抓包进度
        print("📈 监控抓包进度...")
        for i in range(15):
            await asyncio.sleep(1)
            
            if i % 3 == 0:  # 每3秒检查一次
                status_result = await self.capture_server.get_session_status(session_id)
                if status_result["success"]:
                    packets = status_result.get("packets_captured", 0)
                    print(f"   📊 {i+1}/15秒, 已抓取: {packets} 个包")
        
        # 停止抓包并分析
        print("🔍 停止抓包并分析...")
        stop_result = await self.capture_server.stop_capture(session_id)
        
        if stop_result["success"]:
            packets_count = stop_result["packets_captured"]
            analysis = stop_result["analysis"]
            
            print(f"\n📊 抓包分析结果:")
            print(f"   📦 总包数: {packets_count}")
            print(f"   🌐 协议分布: {json.dumps(analysis['summary']['protocols'], ensure_ascii=False)}")
            print(f"   📋 包类型分布: {json.dumps(analysis['summary']['packet_types'], ensure_ascii=False)}")
            print(f"   🔗 连接数: {len(analysis['connections'])}")
            
            if analysis['connections']:
                print(f"   🔗 主要连接:")
                for conn in analysis['connections'][:5]:  # 显示前5个连接
                    print(f"      {conn['src']} ↔ {conn['dst']} ({conn['packet_count']}包)")
            
            if analysis['issues']:
                print(f"\n⚠️  检测到的问题:")
                for issue in analysis['issues']:
                    print(f"   - {issue['type']}: {issue['description']}")
                    print(f"     💡 建议: {issue['recommendation']}")
            
            # 评估测试结果
            success = packets_count > 0
            if success:
                print(f"\n✅ 抓包测试成功！")
                if packets_count >= 10:
                    print(f"📈 捕获包数量良好 ({packets_count})")
                elif packets_count >= 5:
                    print(f"📊 捕获包数量一般 ({packets_count})")
                else:
                    print(f"📉 捕获包数量较少 ({packets_count})")
            else:
                print(f"\n❌ 抓包测试失败：没有捕获到任何数据包")
            
            return success
        else:
            print(f"❌ 抓包分析失败: {stop_result.get('error', '未知错误')}")
            return False
    
    async def test_domain_specific_capture(self):
        """测试特定域名抓包"""
        print("\n🎯 测试特定域名抓包...")
        
        # 抓取baidu.com的流量
        start_result = await self.capture_server.start_capture(
            target="baidu.com",
            capture_type="domain",
            duration=10
        )
        
        if not start_result["success"]:
            print(f"❌ 域名抓包启动失败: {start_result.get('error', '未知错误')}")
            return False
        
        session_id = start_result["session_id"]
        print(f"✅ 域名抓包会话已启动: {session_id}")
        
        # 生成baidu.com相关的流量
        def generate_baidu_traffic():
            time.sleep(2)
            try:
                # ping baidu.com
                subprocess.run(["ping", "-c", "3", "baidu.com"], 
                             capture_output=True, timeout=8)
                print("✅ Ping baidu.com")
                
                # HTTP请求
                requests.get("http://www.baidu.com", timeout=5)
                print("✅ HTTP请求 baidu.com")
            except Exception as e:
                print(f"❌ baidu.com流量生成失败: {e}")
        
        traffic_thread = threading.Thread(target=generate_baidu_traffic)
        traffic_thread.start()
        
        # 等待完成
        await asyncio.sleep(10)
        
        # 分析结果
        stop_result = await self.capture_server.stop_capture(session_id)
        
        if stop_result["success"]:
            packets_count = stop_result["packets_captured"]
            print(f"📊 baidu.com相关包数: {packets_count}")
            
            if packets_count > 0:
                print("✅ 域名特定抓包成功")
                return True
            else:
                print("❌ 没有捕获到域名相关流量")
                return False
        else:
            print(f"❌ 域名抓包分析失败")
            return False
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 优化后抓包服务器综合测试")
        print("=" * 60)
        
        results = []
        
        # 1. 接口检测测试
        interface_result = await self.test_interface_detection()
        results.append(("网络接口检测", interface_result))
        
        # 2. 综合抓包测试
        capture_result = await self.test_capture_with_traffic_generation()
        results.append(("综合抓包测试", capture_result))
        
        # 3. 域名特定抓包测试
        domain_result = await self.test_domain_specific_capture()
        results.append(("域名抓包测试", domain_result))
        
        # 结果汇总
        print("\n" + "=" * 60)
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
            print("🎉 所有测试通过！抓包服务器优化成功")
            print("💡 可以继续集成到MCP客户端")
        elif passed >= total * 0.7:
            print("⚠️  大部分测试通过，抓包服务器基本可用")
            print("💡 建议在实际环境中进一步测试")
        else:
            print("❌ 多个测试失败，需要进一步优化")
        
        return passed >= total * 0.7

async def main():
    """主函数"""
    print("📡 优化后抓包服务器测试")
    print("验证网络接口选择和过滤条件优化效果\n")
    
    if os.geteuid() != 0:
        print("⚠️  警告: 需要管理员权限进行抓包")
        print("   请使用: sudo python3 test_packet_server_direct.py")
        return
    
    tester = OptimizedPacketCaptureTest()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            print("\n✅ 抓包服务器优化成功，准备集成到MCP架构")
        else:
            print("\n❌ 抓包服务器仍需优化")
            
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 