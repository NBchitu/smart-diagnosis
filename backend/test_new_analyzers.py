#!/usr/bin/env python3
"""
测试新的分析器功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.game_traffic_analyzer import GameTrafficAnalyzer
from app.services.interconnection_analyzer import InterconnectionAnalyzer

def test_game_analyzer():
    """测试游戏流量分析器"""
    print("🎮 测试游戏流量分析器...")
    
    analyzer = GameTrafficAnalyzer()
    
    # 测试ISP解析
    test_ips = [
        '111.13.101.208',  # 中国移动
        '123.125.114.144', # 中国联通  
        '116.211.167.14',  # 中国电信
        '8.8.8.8'          # 其他
    ]
    
    print("\n📍 ISP解析测试:")
    for ip in test_ips:
        isp, is_mobile = analyzer._resolve_isp(ip)
        print(f"  {ip} -> {isp} {'(中国移动)' if is_mobile else ''}")
    
    # 测试端口评分
    print("\n🔌 端口评分测试:")
    test_ports = [7000, 8001, 17500, 27015, 80, 443]
    for port in test_ports:
        score = analyzer._calculate_port_score(port, 0)
        print(f"  端口 {port} -> 评分: {score}")
    
    print("✅ 游戏流量分析器测试完成\n")

def test_interconnection_analyzer():
    """测试互联互通分析器"""
    print("🔄 测试互联互通分析器...")
    
    analyzer = InterconnectionAnalyzer()
    
    # 测试ISP解析
    test_ips = [
        '111.13.101.208',  # 中国移动
        '123.125.114.144', # 中国联通  
        '116.211.167.14',  # 中国电信
        '8.8.8.8'          # 其他
    ]
    
    print("\n📍 ISP解析测试:")
    for ip in test_ips:
        isp_name, isp_type = analyzer._resolve_isp_by_ip(ip)
        print(f"  {ip} -> {isp_name} ({isp_type})")
    
    # 测试质量评估
    print("\n📊 质量评估测试:")
    test_cases = [
        (30, 0.05),   # 优秀
        (80, 0.3),    # 良好
        (150, 0.8),   # 一般
        (300, 2.0),   # 较差
    ]
    
    for latency, loss in test_cases:
        quality = analyzer._evaluate_quality_level(latency, loss)
        print(f"  延迟: {latency}ms, 丢包: {loss}% -> 质量: {quality}")
    
    print("✅ 互联互通分析器测试完成\n")

def test_game_traffic_patterns():
    """测试游戏流量模式识别"""
    print("🎯 测试游戏流量模式识别...")
    
    analyzer = GameTrafficAnalyzer()
    
    # 模拟游戏流量数据
    game_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '111.13.101.208', 'src_port': 12345, 'dst_port': 7000, 'size': 120, 'time': 1.0},
        {'src_ip': '111.13.101.208', 'dst_ip': '192.168.1.100', 'src_port': 7000, 'dst_port': 12345, 'size': 80, 'time': 1.1},
        {'src_ip': '192.168.1.100', 'dst_ip': '111.13.101.208', 'src_port': 12345, 'dst_port': 7000, 'size': 150, 'time': 1.2},
        {'src_ip': '111.13.101.208', 'dst_ip': '192.168.1.100', 'src_port': 7000, 'dst_port': 12345, 'size': 90, 'time': 1.3},
    ] * 20  # 重复20次模拟高频流量
    
    # 模拟网页流量数据
    web_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '8.8.8.8', 'src_port': 12346, 'dst_port': 443, 'size': 1200, 'time': 1.0},
        {'src_ip': '8.8.8.8', 'dst_ip': '192.168.1.100', 'src_port': 443, 'dst_port': 12346, 'size': 1500, 'time': 2.0},
        {'src_ip': '192.168.1.100', 'dst_ip': '8.8.8.8', 'src_port': 12346, 'dst_port': 443, 'size': 800, 'time': 3.0},
    ]
    
    print("\n🎮 游戏流量测试:")
    game_flows = analyzer._analyze_traffic_patterns(game_packets)
    print(f"  检测到 {len(game_flows)} 个游戏流量")
    
    print("\n🌐 网页流量测试:")
    web_flows = analyzer._analyze_traffic_patterns(web_packets)
    print(f"  检测到 {len(web_flows)} 个游戏流量")
    
    print("✅ 流量模式识别测试完成\n")

def main():
    """主测试函数"""
    print("🚀 开始测试新的分析器功能\n")
    
    try:
        test_game_analyzer()
        test_interconnection_analyzer()
        test_game_traffic_patterns()
        
        print("🎉 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
