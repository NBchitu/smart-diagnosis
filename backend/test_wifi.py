#!/usr/bin/env python3
"""
WiFi信号强度功能测试脚本
"""

import asyncio
import json
from app.services.wifi_service import WiFiService

async def test_wifi_service():
    """测试WiFi服务功能"""
    print("开始测试WiFi信号强度功能...")
    
    wifi_service = WiFiService()
    
    try:
        print(f"检测到系统类型: {wifi_service.system_type}")
        
        # 测试获取当前WiFi信号
        print("\n=== 测试获取当前WiFi信号 ===")
        signal_info = await wifi_service.get_current_wifi_signal()
        
        print("WiFi信号信息:")
        print(f"  SSID: {signal_info.get('ssid', 'Unknown')}")
        print(f"  信号强度: {signal_info.get('signal_strength', 'N/A')} dBm")
        print(f"  信号质量: {signal_info.get('signal_quality', 'N/A')}%")
        print(f"  信道: {signal_info.get('channel', 'N/A')}")
        print(f"  频率: {signal_info.get('frequency', 'N/A')} MHz")
        print(f"  网络接口: {signal_info.get('interface', 'N/A')}")
        print(f"  加密方式: {signal_info.get('encryption', 'N/A')}")
        print(f"  连接状态: {'已连接' if signal_info.get('connected') else '未连接'}")
        
        if signal_info.get('link_speed'):
            print(f"  连接速度: {signal_info.get('link_speed')} Mbps")
        if signal_info.get('noise_level'):
            print(f"  噪音水平: {signal_info.get('noise_level')} dBm")
        if signal_info.get('tx_rate'):
            print(f"  传输速率: {signal_info.get('tx_rate')} Mbps")
        
        print(f"  时间戳: {signal_info.get('timestamp', 'N/A')}")
        
        # 测试WiFi网络扫描
        print("\n=== 测试WiFi网络扫描 ===")
        networks = await wifi_service.scan_wifi_networks()
        
        print(f"扫描到 {len(networks)} 个WiFi网络:")
        for i, network in enumerate(networks, 1):
            print(f"  网络 {i}:")
            print(f"    SSID: {network.get('ssid', 'Unknown')}")
            print(f"    BSSID: {network.get('bssid', 'Unknown')}")
            print(f"    信号强度: {network.get('signal', 'N/A')} dBm")
            print(f"    信号质量: {network.get('quality', 'N/A')}%")
            print(f"    信道: {network.get('channel', 'N/A')}")
            print(f"    频率: {network.get('frequency', 'N/A')} MHz")
            print(f"    加密方式: {network.get('encryption', 'N/A')}")
        
        print(f"\n=== 完整JSON结果 ===")
        print("WiFi信号信息:")
        print(json.dumps(signal_info, indent=2, ensure_ascii=False))
        print("\nWiFi网络列表:")
        print(json.dumps(networks, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_signal_levels():
    """测试不同信号强度的评级"""
    print("\n=== 测试信号强度评级 ===")
    
    test_signals = [-30, -45, -55, -65, -75, -85, -95]
    
    for signal in test_signals:
        if signal >= -30:
            level = "极强"
        elif signal >= -50:
            level = "强"
        elif signal >= -70:
            level = "中等"
        elif signal >= -80:
            level = "弱"
        else:
            level = "极弱"
        
        quality = max(0, min(100, (signal + 100) * 2))
        
        print(f"  {signal} dBm -> {level} (质量: {quality}%)")

if __name__ == "__main__":
    asyncio.run(test_wifi_service())
    asyncio.run(test_signal_levels()) 