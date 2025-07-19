from fastapi import APIRouter, HTTPException
from typing import Dict, List
from app.services.wifi_service import WiFiService

router = APIRouter()

# WiFi服务实例
wifi_service = WiFiService()

@router.get("/signal")
async def get_current_signal():
    """获取当前WiFi信号强度"""
    try:
        signal_info = await wifi_service.get_current_wifi_signal()
        return {
            "success": True,
            "data": signal_info
        }
    except Exception as e:
        # 如果获取失败，返回模拟数据（用于开发环境）
        return {
            "success": True,
            "data": {
                "ssid": "NetworkTester-Pi5",
                "signal_strength": -45,
                "signal_quality": 85,
                "channel": 7,
                "frequency": 2442,
                "interface": "wlan0",
                "encryption": "WPA2",
                "connected": True,
                "error": str(e)
            }
        }

@router.post("/scan")
async def scan_wifi_networks():
    """扫描周边WiFi网络并分析信道干扰"""
    try:
        # 获取当前连接的WiFi信息
        current_wifi = None
        try:
            current_wifi = await wifi_service.get_current_wifi_signal()
        except:
            pass
        
        # 扫描周边网络
        networks = await wifi_service.scan_wifi_networks()
        
        # 分析信道干扰
        channel_analysis = _analyze_channel_interference(networks, current_wifi)
        
        # 生成调整建议
        recommendations = _generate_channel_recommendations(channel_analysis, current_wifi)
        
        return {
            "success": True,
            "data": {
                "current_wifi": current_wifi,
                "networks": networks,
                "channel_analysis": channel_analysis,
                "recommendations": recommendations,
                "scan_time": networks[0].get("timestamp") if networks else None,
                "total_networks": len(networks)
            }
        }
    except Exception as e:
        # 返回模拟数据用于开发
        return {
            "success": True,
            "data": _get_mock_wifi_scan_data()
        }

def _analyze_channel_interference(networks: List[Dict], current_wifi: Dict = None) -> Dict:
    """分析信道干扰情况"""
    try:
        # 2.4GHz和5GHz信道初始化
        channels_24ghz = {i: {"count": 0, "signal_sum": 0, "networks": []} for i in range(1, 15)}
        channels_5ghz = {i: {"count": 0, "signal_sum": 0, "networks": []} for i in range(36, 166, 4)}
        
        # 首先添加当前连接的网络到分析中
        all_networks = list(networks)  # 复制周边网络列表
        if current_wifi:
            # 将当前连接的网络添加到分析列表中
            current_network = {
                "ssid": current_wifi.get("ssid", "Current"),
                "signal": current_wifi.get("signal_strength", -50),
                "channel": current_wifi.get("channel", 6),
                "is_current": True  # 标记为当前网络
            }
            all_networks.append(current_network)
        
        # 统计每个信道的网络数量和信号强度
        for network in all_networks:
            channel = network.get("channel", 6)
            signal = network.get("signal", -70)
            
            if 1 <= channel <= 14:  # 2.4GHz
                if channel in channels_24ghz:
                    channels_24ghz[channel]["count"] += 1
                    channels_24ghz[channel]["signal_sum"] += abs(signal)
                    channels_24ghz[channel]["networks"].append({
                        "ssid": network.get("ssid"),
                        "signal": signal,
                        "is_current": network.get("is_current", False)
                    })
            elif channel >= 36:  # 5GHz
                if channel in channels_5ghz:
                    channels_5ghz[channel]["count"] += 1
                    channels_5ghz[channel]["signal_sum"] += abs(signal)
                    channels_5ghz[channel]["networks"].append({
                        "ssid": network.get("ssid"),
                        "signal": signal,
                        "is_current": network.get("is_current", False)
                    })
        
        # 计算干扰程度
        def calculate_interference(channel_data):
            interference_levels = {}
            for channel, data in channel_data.items():
                if data["count"] == 0:
                    interference = 0  # 无干扰
                else:
                    # 干扰程度 = 网络数量 * 平均信号强度权重
                    avg_signal = data["signal_sum"] / data["count"]
                    interference = data["count"] * (avg_signal / 100)
                
                interference_levels[channel] = {
                    "level": min(100, interference * 10),  # 转换为0-100的干扰程度
                    "count": data["count"],
                    "avg_signal": data["signal_sum"] / data["count"] if data["count"] > 0 else 0,
                    "networks": data["networks"]
                }
            return interference_levels
        
        return {
            "2.4ghz": calculate_interference(channels_24ghz),
            "5ghz": calculate_interference(channels_5ghz),
            "summary": {
                "total_24ghz_networks": sum(ch["count"] for ch in channels_24ghz.values()),
                "total_5ghz_networks": sum(ch["count"] for ch in channels_5ghz.values()),
                "most_crowded_24ghz": max(channels_24ghz.items(), key=lambda x: x[1]["count"])[0],
                "least_crowded_24ghz": min(channels_24ghz.items(), key=lambda x: x[1]["count"])[0]
            }
        }
    except Exception as e:
        print(f"分析信道干扰失败: {e}")
        return _get_mock_channel_analysis()

def _generate_channel_recommendations(channel_analysis: Dict, current_wifi: Dict = None) -> Dict:
    """生成信道调整建议"""
    try:
        recommendations = {
            "need_adjustment": False,
            "current_channel": None,
            "current_band": None,
            "recommended_channels": [],
            "reasons": []
        }
        
        if not current_wifi:
            return recommendations
            
        current_channel = current_wifi.get("channel", 6)
        current_frequency = current_wifi.get("frequency", 2437)
        
        # 判断当前频段
        if current_frequency < 3000:  # 2.4GHz
            current_band = "2.4GHz"
            channel_data = channel_analysis.get("2.4ghz", {})
        else:  # 5GHz
            current_band = "5GHz"
            channel_data = channel_analysis.get("5ghz", {})
        
        recommendations["current_channel"] = current_channel
        recommendations["current_band"] = current_band
        
        # 检查当前信道的干扰程度
        current_interference = channel_data.get(current_channel, {}).get("level", 0)
        
        # 如果当前信道干扰超过50，建议调整
        if current_interference > 50:
            recommendations["need_adjustment"] = True
            recommendations["reasons"].append(f"当前信道 {current_channel} 干扰程度较高 ({current_interference:.1f}%)")
            
            # 找到干扰最小的信道
            sorted_channels = sorted(channel_data.items(), key=lambda x: x[1]["level"])
            
            # 推荐前3个干扰最小的信道
            for channel, data in sorted_channels[:3]:
                if data["level"] < current_interference - 10:  # 至少比当前信道好10%
                    recommendations["recommended_channels"].append({
                        "channel": channel,
                        "interference_level": data["level"],
                        "network_count": data["count"],
                        "improvement": current_interference - data["level"]
                    })
        
        if not recommendations["need_adjustment"]:
            recommendations["reasons"].append(f"当前信道 {current_channel} 干扰程度较低，无需调整")
        
        return recommendations
        
    except Exception as e:
        print(f"生成信道建议失败: {e}")
        return {
            "need_adjustment": False,
            "current_channel": 6,
            "current_band": "2.4GHz",
            "recommended_channels": [],
            "reasons": ["无法分析当前网络状态"]
        }

def _get_mock_wifi_scan_data() -> Dict:
    """获取模拟WiFi扫描数据"""
    import random
    import time
    
    # 模拟当前连接的WiFi
    current_wifi = {
        "ssid": "NetworkTester-Pi5",
        "signal_strength": -45,
        "signal_quality": 85,
        "channel": 7,
        "frequency": 2442,
        "interface": "wlan0",
        "encryption": "WPA2",
        "connected": True,
        "timestamp": int(time.time())
    }
    
    # 模拟周边网络
    networks = [
        {
            "ssid": "WiFi-Home-5G",
            "bssid": "aa:bb:cc:dd:ee:f1",
            "signal": -52,
            "quality": 78,
            "channel": 1,
            "frequency": 2412,
            "encryption": "WPA2",
            "timestamp": int(time.time())
        },
        {
            "ssid": "TP-LINK_2.4G",
            "bssid": "aa:bb:cc:dd:ee:f2", 
            "signal": -65,
            "quality": 60,
            "channel": 6,
            "frequency": 2437,
            "encryption": "WPA3",
            "timestamp": int(time.time())
        },
        {
            "ssid": "Xiaomi_Router",
            "bssid": "aa:bb:cc:dd:ee:f3",
            "signal": -58,
            "quality": 70,
            "channel": 11,
            "frequency": 2462,
            "encryption": "WPA2",
            "timestamp": int(time.time())
        },
        {
            "ssid": "FAST_5G_Pro", 
            "bssid": "aa:bb:cc:dd:ee:f4",
            "signal": -48,
            "quality": 82,
            "channel": 44,
            "frequency": 5220,
            "encryption": "WPA3",
            "timestamp": int(time.time())
        },
        {
            "ssid": "ChinaNet-Office",
            "bssid": "aa:bb:cc:dd:ee:f5",
            "signal": -72,
            "quality": 45,
            "channel": 6,
            "frequency": 2437,
            "encryption": "WPA2",
            "timestamp": int(time.time())
        }
    ]
    
    # 分析信道干扰
    channel_analysis = _analyze_channel_interference(networks, current_wifi)
    recommendations = _generate_channel_recommendations(channel_analysis, current_wifi)
    
    return {
        "current_wifi": current_wifi,
        "networks": networks,
        "channel_analysis": channel_analysis,
        "recommendations": recommendations,
        "scan_time": int(time.time()),
        "total_networks": len(networks)
    }

def _get_mock_channel_analysis() -> Dict:
    """获取模拟信道分析数据"""
    return {
        "2.4ghz": {
            1: {"level": 25, "count": 1, "avg_signal": 52, "networks": []},
            6: {"level": 75, "count": 3, "avg_signal": 65, "networks": []},
            11: {"level": 40, "count": 2, "avg_signal": 58, "networks": []}
        },
        "5ghz": {
            44: {"level": 15, "count": 1, "avg_signal": 48, "networks": []}
        },
        "summary": {
            "total_24ghz_networks": 6,
            "total_5ghz_networks": 1,
            "most_crowded_24ghz": 6,
            "least_crowded_24ghz": 1
        }
    } 