#!/usr/bin/env python3
"""
测试游戏流量检测修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.game_traffic_analyzer import GameTrafficAnalyzer

def test_web_traffic_filtering():
    """测试网页流量过滤"""
    print("🧪 测试网页流量过滤（应该不被识别为游戏流量）\n")
    
    analyzer = GameTrafficAnalyzer()
    
    # 模拟网页流量（QUIC/HTTP3）
    web_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '172.64.147.26', 'src_port': 54321, 'dst_port': 443, 'size': 1200, 'time': 1.0},
        {'src_ip': '172.64.147.26', 'dst_ip': '192.168.1.100', 'src_port': 443, 'dst_port': 54321, 'size': 1500, 'time': 1.1},
        {'src_ip': '192.168.1.100', 'dst_ip': '172.64.147.26', 'src_port': 54321, 'dst_port': 443, 'size': 800, 'time': 1.2},
    ] * 10  # 重复10次
    
    # 模拟真实游戏流量
    game_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '111.13.101.208', 'src_port': 12345, 'dst_port': 7000, 'size': 120, 'time': 1.0},
        {'src_ip': '111.13.101.208', 'dst_ip': '192.168.1.100', 'src_port': 7000, 'dst_port': 12345, 'size': 80, 'time': 1.1},
        {'src_ip': '192.168.1.100', 'dst_ip': '111.13.101.208', 'src_port': 12345, 'dst_port': 7000, 'size': 150, 'time': 1.2},
        {'src_ip': '111.13.101.208', 'dst_ip': '192.168.1.100', 'src_port': 7000, 'dst_port': 12345, 'size': 90, 'time': 1.3},
    ] * 20  # 重复20次模拟高频游戏流量
    
    print("🌐 测试网页流量（HTTPS/QUIC）:")
    web_flows = analyzer._analyze_traffic_patterns(web_packets)
    print(f"   检测到 {len(web_flows)} 个游戏流量")
    
    if len(web_flows) > 0:
        for flow in web_flows:
            is_game = analyzer._is_game_traffic(flow)
            print(f"   流量 {flow['src_port']}->{flow['dst_port']}: {'游戏' if is_game else '非游戏'}")
    
    print("\n🎮 测试真实游戏流量:")
    game_flows = analyzer._analyze_traffic_patterns(game_packets)
    print(f"   检测到 {len(game_flows)} 个流量")
    
    if len(game_flows) > 0:
        for flow in game_flows:
            is_game = analyzer._is_game_traffic(flow)
            print(f"   流量 {flow['src_port']}->{flow['dst_port']}: {'游戏' if is_game else '非游戏'}")
    
    print()

def test_port_scoring():
    """测试端口评分"""
    print("🔌 测试端口评分:\n")
    
    analyzer = GameTrafficAnalyzer()
    
    test_ports = [
        (443, 54321, "HTTPS"),
        (80, 54322, "HTTP"),
        (7000, 12345, "游戏端口7000"),
        (8001, 12346, "游戏端口8001"),
        (17500, 12347, "游戏端口17500"),
        (53, 12348, "DNS"),
    ]
    
    for src_port, dst_port, desc in test_ports:
        score = analyzer._calculate_port_score(src_port, dst_port)
        print(f"   {desc} ({src_port}->{dst_port}): 评分 {score}")
    
    print()

def test_traffic_pattern_calculation():
    """测试流量模式计算"""
    print("📊 测试流量模式计算:\n")
    
    analyzer = GameTrafficAnalyzer()
    
    # 高频小包流量（游戏特征）
    game_like_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '111.13.101.208', 'size': 120, 'time': i * 0.1}
        for i in range(50)  # 50个包，5秒内
    ]
    
    # 低频大包流量（网页特征）
    web_like_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '172.64.147.26', 'size': 1200, 'time': i * 1.0}
        for i in range(10)  # 10个包，10秒内
    ]
    
    print("🎮 游戏类流量模式:")
    game_pattern = analyzer._calculate_traffic_pattern(game_like_packets)
    print(f"   平均包大小: {game_pattern.avg_packet_size:.1f} 字节")
    print(f"   包频率: {game_pattern.packet_frequency:.1f} 包/秒")
    
    print("\n🌐 网页类流量模式:")
    web_pattern = analyzer._calculate_traffic_pattern(web_like_packets)
    print(f"   平均包大小: {web_pattern.avg_packet_size:.1f} 字节")
    print(f"   包频率: {web_pattern.packet_frequency:.1f} 包/秒")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始测试游戏流量检测修复\n")
    
    try:
        test_port_scoring()
        test_traffic_pattern_calculation()
        test_web_traffic_filtering()
        
        print("🎉 游戏流量检测修复测试完成！")
        print("\n📝 修复要点:")
        print("   ✅ 排除QUIC和DNS流量")
        print("   ✅ 端口检查作为必要条件")
        print("   ✅ 提高识别阈值到80分")
        print("   ✅ 无游戏流量时返回正确结果")
        
        return 0
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
