"""
WiFi信号分析MCP服务器
"""

import asyncio
import subprocess
import json
import re
import sys
from typing import Dict, List, Optional, Tuple
import logging
from fastmcp import FastMCP

# 创建MCP应用
mcp = FastMCP("WiFi Signal Analysis Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def scan_wifi_networks() -> Dict:
    """
    扫描周围的WiFi网络
    
    Returns:
        包含WiFi网络信息的字典
    """
    try:
        # 使用iwlist命令扫描WiFi
        cmd = ["sudo", "iwlist", "scan"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "WiFi扫描失败",
                "networks": []
            }
        
        # 解析WiFi扫描结果
        networks = _parse_iwlist_output(stdout.decode('utf-8'))
        
        return {
            "success": True,
            "total_networks": len(networks),
            "networks": networks,
            "scan_time": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"WiFi扫描失败: {str(e)}")
        return {
            "success": False,
            "error": f"WiFi扫描异常: {str(e)}",
            "networks": []
        }

@mcp.tool()
async def get_current_wifi_info() -> Dict:
    """
    获取当前连接的WiFi信息
    
    Returns:
        当前WiFi连接信息
    """
    try:
        # 获取当前WiFi连接信息
        cmd = ["iwconfig"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "获取WiFi信息失败",
                "connected": False
            }
        
        # 解析当前WiFi信息
        wifi_info = _parse_iwconfig_output(stdout.decode('utf-8'))
        
        return {
            "success": True,
            "connected": wifi_info.get("connected", False),
            "wifi_info": wifi_info
        }
        
    except Exception as e:
        logger.error(f"获取WiFi信息失败: {str(e)}")
        return {
            "success": False,
            "error": f"获取WiFi信息异常: {str(e)}",
            "connected": False
        }

@mcp.tool()
async def analyze_wifi_interference(
    interface: str = "wlan0",
    duration: int = 30
) -> Dict:
    """
    分析WiFi干扰情况
    
    Args:
        interface: WiFi接口名称，默认wlan0
        duration: 监控时长（秒），默认30秒
    
    Returns:
        WiFi干扰分析结果
    """
    try:
        # 使用iw命令监控WiFi
        cmd = ["sudo", "iw", "dev", interface, "scan", "dump"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "WiFi干扰分析失败",
                "interference_analysis": {}
            }
        
        # 分析WiFi干扰
        analysis = _analyze_wifi_interference(stdout.decode('utf-8'))
        
        return {
            "success": True,
            "interface": interface,
            "duration": duration,
            "interference_analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"WiFi干扰分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"WiFi干扰分析异常: {str(e)}",
            "interference_analysis": {}
        }

@mcp.tool()
async def get_wifi_channel_utilization() -> Dict:
    """
    获取WiFi信道利用率
    
    Returns:
        各信道的利用率信息
    """
    try:
        # 扫描WiFi获取信道信息
        scan_result = await scan_wifi_networks()
        
        if not scan_result["success"]:
            return {
                "success": False,
                "error": "无法获取WiFi扫描结果",
                "channel_utilization": {}
            }
        
        # 分析信道利用率
        utilization = _calculate_channel_utilization(scan_result["networks"])
        
        return {
            "success": True,
            "channel_utilization": utilization,
            "recommendations": _get_channel_recommendations(utilization)
        }
        
    except Exception as e:
        logger.error(f"获取信道利用率失败: {str(e)}")
        return {
            "success": False,
            "error": f"获取信道利用率异常: {str(e)}",
            "channel_utilization": {}
        }

@mcp.tool()
async def measure_signal_strength(
    target_ssid: Optional[str] = None,
    duration: int = 10
) -> Dict:
    """
    测量WiFi信号强度
    
    Args:
        target_ssid: 目标WiFi网络SSID，None表示当前连接的网络
        duration: 测量时长（秒），默认10秒
    
    Returns:
        信号强度测量结果
    """
    try:
        measurements = []
        interval = 1  # 每秒测量一次
        
        for i in range(duration):
            # 获取当前信号强度
            cmd = ["iwconfig"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                wifi_info = _parse_iwconfig_output(stdout.decode('utf-8'))
                if wifi_info.get("connected"):
                    measurement = {
                        "timestamp": asyncio.get_event_loop().time(),
                        "signal_level": wifi_info.get("signal_level", 0),
                        "link_quality": wifi_info.get("link_quality", 0),
                        "noise_level": wifi_info.get("noise_level", 0)
                    }
                    measurements.append(measurement)
            
            await asyncio.sleep(interval)
        
        if not measurements:
            return {
                "success": False,
                "error": "无法获取WiFi信号强度数据",
                "measurements": []
            }
        
        # 计算统计信息
        signal_levels = [m["signal_level"] for m in measurements]
        link_qualities = [m["link_quality"] for m in measurements]
        
        return {
            "success": True,
            "target_ssid": target_ssid,
            "duration": duration,
            "total_samples": len(measurements),
            "measurements": measurements,
            "statistics": {
                "avg_signal_level": sum(signal_levels) / len(signal_levels),
                "min_signal_level": min(signal_levels),
                "max_signal_level": max(signal_levels),
                "avg_link_quality": sum(link_qualities) / len(link_qualities),
                "signal_stability": _calculate_signal_stability(signal_levels)
            }
        }
        
    except Exception as e:
        logger.error(f"测量信号强度失败: {str(e)}")
        return {
            "success": False,
            "error": f"测量信号强度异常: {str(e)}",
            "measurements": []
        }

def _parse_iwlist_output(output: str) -> List[Dict]:
    """解析iwlist扫描输出"""
    networks = []
    current_network = {}
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Cell"):
                # 新的网络条目
                if current_network:
                    networks.append(current_network)
                
                current_network = {}
                # 提取MAC地址
                if "Address:" in line:
                    current_network["mac"] = line.split("Address:")[-1].strip()
            
            elif "ESSID:" in line:
                essid = line.split("ESSID:")[-1].strip().strip('"')
                current_network["ssid"] = essid
            
            elif "Quality=" in line:
                # 解析信号质量和强度
                parts = line.split()
                for part in parts:
                    if "Quality=" in part:
                        quality = part.split("=")[1]
                        if "/" in quality:
                            num, denom = quality.split("/")
                            current_network["link_quality"] = int(num)
                            current_network["link_quality_max"] = int(denom)
                    elif "Signal level=" in part:
                        signal = part.split("=")[1]
                        current_network["signal_level"] = int(signal.replace("dBm", ""))
            
            elif "Frequency:" in line:
                # 提取频率和信道
                freq_part = line.split("Frequency:")[1].split()[0]
                current_network["frequency"] = float(freq_part)
                
                if "Channel" in line:
                    channel_part = line.split("Channel")[1].split(")")[0].strip()
                    current_network["channel"] = int(channel_part)
            
            elif "Encryption key:" in line:
                encrypted = "on" in line.lower()
                current_network["encrypted"] = encrypted
            
            elif "IE:" in line and "WPA" in line:
                current_network["security"] = "WPA"
            elif "IE:" in line and "WPS" in line:
                current_network["wps"] = True
        
        # 添加最后一个网络
        if current_network:
            networks.append(current_network)
            
    except Exception as e:
        logger.warning(f"解析iwlist输出失败: {str(e)}")
    
    return networks

def _parse_iwconfig_output(output: str) -> Dict:
    """解析iwconfig输出"""
    wifi_info = {"connected": False}
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if "ESSID:" in line:
                essid = line.split("ESSID:")[-1].strip().strip('"')
                if essid and essid != "off/any":
                    wifi_info["ssid"] = essid
                    wifi_info["connected"] = True
            
            elif "Quality=" in line:
                parts = line.split()
                for part in parts:
                    if "Quality=" in part:
                        quality = part.split("=")[1]
                        if "/" in quality:
                            num, denom = quality.split("/")
                            wifi_info["link_quality"] = int(num)
                            wifi_info["link_quality_max"] = int(denom)
                    elif "Signal level=" in part:
                        signal = part.split("=")[1]
                        wifi_info["signal_level"] = int(signal.replace("dBm", ""))
            
            elif "Frequency:" in line:
                freq_part = line.split("Frequency:")[1].split()[0]
                wifi_info["frequency"] = float(freq_part)
            
            elif "Access Point:" in line:
                ap_mac = line.split("Access Point:")[-1].strip()
                if ap_mac and ap_mac != "Not-Associated":
                    wifi_info["access_point"] = ap_mac
                    
    except Exception as e:
        logger.warning(f"解析iwconfig输出失败: {str(e)}")
    
    return wifi_info

def _analyze_wifi_interference(scan_output: str) -> Dict:
    """分析WiFi干扰"""
    analysis = {
        "total_networks": 0,
        "band_distribution": {"2.4g": 0, "5g": 0},
        "channel_congestion": {},
        "signal_strength_distribution": {"strong": 0, "medium": 0, "weak": 0},
        "encryption_status": {"encrypted": 0, "open": 0}
    }
    
    try:
        # 这里应该解析iw scan输出，简化实现
        analysis["total_networks"] = scan_output.count("BSS ")
        analysis["interference_level"] = "medium" if analysis["total_networks"] > 10 else "low"
        
    except Exception as e:
        logger.warning(f"分析WiFi干扰失败: {str(e)}")
    
    return analysis

def _calculate_channel_utilization(networks: List[Dict]) -> Dict:
    """计算信道利用率"""
    utilization = {}
    
    try:
        # 统计各信道的网络数量
        for network in networks:
            channel = network.get("channel", 0)
            if channel:
                if channel not in utilization:
                    utilization[channel] = {"count": 0, "networks": []}
                
                utilization[channel]["count"] += 1
                utilization[channel]["networks"].append({
                    "ssid": network.get("ssid", ""),
                    "signal_level": network.get("signal_level", 0)
                })
        
        # 计算利用率百分比
        total_networks = len(networks)
        for channel in utilization:
            count = utilization[channel]["count"]
            utilization[channel]["utilization_percent"] = (count / total_networks) * 100
            
    except Exception as e:
        logger.warning(f"计算信道利用率失败: {str(e)}")
    
    return utilization

def _get_channel_recommendations(utilization: Dict) -> Dict:
    """获取信道推荐"""
    recommendations = {
        "best_2_4g_channel": 1,
        "best_5g_channel": 36,
        "reason": "基于当前扫描结果的最优信道选择"
    }
    
    try:
        # 找到利用率最低的信道
        if utilization:
            sorted_channels = sorted(
                utilization.items(),
                key=lambda x: x[1]["utilization_percent"]
            )
            
            # 2.4GHz信道推荐 (1-13)
            for channel, data in sorted_channels:
                if 1 <= channel <= 13:
                    recommendations["best_2_4g_channel"] = channel
                    break
            
            # 5GHz信道推荐 (36+)
            for channel, data in sorted_channels:
                if channel >= 36:
                    recommendations["best_5g_channel"] = channel
                    break
                    
    except Exception as e:
        logger.warning(f"生成信道推荐失败: {str(e)}")
    
    return recommendations

def _calculate_signal_stability(signal_levels: List[int]) -> str:
    """计算信号稳定性"""
    if not signal_levels:
        return "unknown"
    
    try:
        # 计算信号变化范围
        signal_range = max(signal_levels) - min(signal_levels)
        
        if signal_range <= 5:
            return "very_stable"
        elif signal_range <= 10:
            return "stable"
        elif signal_range <= 20:
            return "moderate"
        else:
            return "unstable"
            
    except Exception as e:
        logger.warning(f"计算信号稳定性失败: {str(e)}")
        return "unknown"

def main():
    """运行MCP服务器"""
    # 使用标准的事件循环运行方式
    import asyncio
    
    # 创建新的事件循环并运行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(mcp.run())
    finally:
        loop.close()

if __name__ == "__main__":
    main() 