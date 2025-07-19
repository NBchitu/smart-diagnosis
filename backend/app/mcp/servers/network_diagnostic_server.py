"""
综合网络诊断MCP服务器
包含多种网络诊断工具：速度测试、WiFi扫描、信号分析等
"""

import asyncio
import subprocess
import json
import sys
import platform
import re
from typing import Dict, List, Optional, Any
import logging
from fastmcp import FastMCP

# 创建MCP应用
mcp = FastMCP("Network Diagnostic Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def speed_test(
    server_id: Optional[str] = None,
    timeout: int = 120
) -> Dict:
    """
    执行网络速度测试
    
    Args:
        server_id: 指定测试服务器ID（可选）
        timeout: 超时时间（秒），默认120秒
    
    Returns:
        包含速度测试结果的字典
    """
    try:
        # 构建speedtest命令
        cmd = ["speedtest-cli", "--json"]
        if server_id:
            cmd.extend(["--server", server_id])
        
        # 执行speedtest命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": "速度测试超时",
                "timeout": timeout
            }
        
        if process.returncode == 0:
            # 解析speedtest结果
            speed_data = json.loads(stdout.decode('utf-8'))
            
            result = {
                "success": True,
                "download_speed": round(speed_data.get("download", 0) / 1_000_000, 2),  # Mbps
                "upload_speed": round(speed_data.get("upload", 0) / 1_000_000, 2),    # Mbps
                "ping": round(speed_data.get("ping", 0), 2),
                "server": {
                    "name": speed_data.get("server", {}).get("name", "Unknown"),
                    "country": speed_data.get("server", {}).get("country", "Unknown"),
                    "sponsor": speed_data.get("server", {}).get("sponsor", "Unknown"),
                    "id": speed_data.get("server", {}).get("id", "Unknown")
                },
                "client": {
                    "ip": speed_data.get("client", {}).get("ip", "Unknown"),
                    "isp": speed_data.get("client", {}).get("isp", "Unknown"),
                    "country": speed_data.get("client", {}).get("country", "Unknown")
                },
                "timestamp": speed_data.get("timestamp"),
                "share_url": speed_data.get("share")
            }
        else:
            result = {
                "success": False,
                "error": "速度测试失败",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "return_code": process.returncode
            }
        
        return result
        
    except Exception as e:
        logger.error(f"速度测试异常: {str(e)}")
        return {
            "success": False,
            "error": f"速度测试异常: {str(e)}"
        }

@mcp.tool()
async def wifi_scan(
    interface: str = "wlan0",
    timeout: int = 30
) -> Dict:
    """
    扫描周边WiFi网络信号
    
    Args:
        interface: 网络接口名称，默认wlan0
        timeout: 扫描超时时间（秒），默认30秒
    
    Returns:
        包含WiFi扫描结果的字典
    """
    try:
        # 根据系统选择WiFi扫描命令
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ["airport", "-s"]
        elif system == "linux":  # Linux
            cmd = ["iwlist", interface, "scan"]
        elif system == "windows":  # Windows
            cmd = ["netsh", "wlan", "show", "profile"]
        else:
            return {
                "success": False,
                "error": f"不支持的操作系统: {system}"
            }
        
        # 执行WiFi扫描命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": "WiFi扫描超时",
                "timeout": timeout
            }
        
        if process.returncode == 0:
            # 解析WiFi扫描结果
            networks = _parse_wifi_scan_output(stdout.decode('utf-8'), system)
            
            result = {
                "success": True,
                "interface": interface,
                "networks": networks,
                "total_networks": len(networks),
                "scan_timestamp": asyncio.get_event_loop().time()
            }
        else:
            result = {
                "success": False,
                "error": "WiFi扫描失败",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "return_code": process.returncode
            }
        
        return result
        
    except Exception as e:
        logger.error(f"WiFi扫描异常: {str(e)}")
        return {
            "success": False,
            "error": f"WiFi扫描异常: {str(e)}"
        }

@mcp.tool()
async def signal_analysis(
    interface: str = "wlan0"
) -> Dict:
    """
    分析当前WiFi信号质量
    
    Args:
        interface: 网络接口名称，默认wlan0
    
    Returns:
        包含信号质量分析结果的字典
    """
    try:
        # 根据系统选择信号分析命令
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ["airport", "-I"]
        elif system == "linux":  # Linux
            cmd = ["iwconfig", interface]
        elif system == "windows":  # Windows
            cmd = ["netsh", "wlan", "show", "interface"]
        else:
            return {
                "success": False,
                "error": f"不支持的操作系统: {system}"
            }
        
        # 执行信号分析命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # 解析信号分析结果
            signal_data = _parse_signal_analysis_output(stdout.decode('utf-8'), system)
            
            result = {
                "success": True,
                "interface": interface,
                **signal_data,
                "analysis_timestamp": asyncio.get_event_loop().time()
            }
        else:
            result = {
                "success": False,
                "error": "信号分析失败",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "return_code": process.returncode
            }
        
        return result
        
    except Exception as e:
        logger.error(f"信号分析异常: {str(e)}")
        return {
            "success": False,
            "error": f"信号分析异常: {str(e)}"
        }

@mcp.tool()
async def network_interfaces() -> Dict:
    """
    获取系统网络接口信息
    
    Returns:
        包含网络接口信息的字典
    """
    try:
        # 根据系统选择网络接口命令
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ["ifconfig"]
        elif system == "linux":  # Linux
            cmd = ["ip", "addr", "show"]
        elif system == "windows":  # Windows
            cmd = ["ipconfig", "/all"]
        else:
            return {
                "success": False,
                "error": f"不支持的操作系统: {system}"
            }
        
        # 执行网络接口命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # 解析网络接口结果
            interfaces = _parse_network_interfaces_output(stdout.decode('utf-8'), system)
            
            result = {
                "success": True,
                "interfaces": interfaces,
                "total_interfaces": len(interfaces),
                "system": system
            }
        else:
            result = {
                "success": False,
                "error": "获取网络接口失败",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "return_code": process.returncode
            }
        
        return result
        
    except Exception as e:
        logger.error(f"获取网络接口异常: {str(e)}")
        return {
            "success": False,
            "error": f"获取网络接口异常: {str(e)}"
        }

@mcp.tool()
async def dns_lookup(
    domain: str,
    record_type: str = "A",
    nameserver: Optional[str] = None
) -> Dict:
    """
    DNS查询
    
    Args:
        domain: 要查询的域名
        record_type: 记录类型（A, AAAA, MX, NS, TXT等），默认A
        nameserver: 指定DNS服务器（可选）
    
    Returns:
        包含DNS查询结果的字典
    """
    try:
        # 构建nslookup命令
        cmd = ["nslookup", "-type=" + record_type, domain]
        if nameserver:
            cmd.append(nameserver)
        
        # 执行DNS查询命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # 解析DNS查询结果
            dns_data = _parse_dns_lookup_output(stdout.decode('utf-8'), record_type)
            
            result = {
                "success": True,
                "domain": domain,
                "record_type": record_type,
                "nameserver": nameserver,
                **dns_data
            }
        else:
            result = {
                "success": False,
                "error": "DNS查询失败",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "return_code": process.returncode
            }
        
        return result
        
    except Exception as e:
        logger.error(f"DNS查询异常: {str(e)}")
        return {
            "success": False,
            "error": f"DNS查询异常: {str(e)}"
        }

# 辅助函数

def _parse_wifi_scan_output(output: str, system: str) -> List[Dict]:
    """解析WiFi扫描输出"""
    networks = []
    
    try:
        if system == "darwin":  # macOS
            lines = output.strip().split('\n')
            for line in lines[1:]:  # 跳过标题行
                parts = line.split()
                if len(parts) >= 6:
                    networks.append({
                        "ssid": parts[0],
                        "bssid": parts[1],
                        "rssi": int(parts[2]),
                        "channel": parts[3],
                        "encryption": parts[4] if len(parts) > 4 else "Open"
                    })
        
        elif system == "linux":  # Linux
            current_network = {}
            for line in output.split('\n'):
                line = line.strip()
                if 'Cell' in line and 'Address:' in line:
                    if current_network:
                        networks.append(current_network)
                    current_network = {}
                elif 'ESSID:' in line:
                    ssid = line.split('ESSID:')[1].strip('"')
                    current_network['ssid'] = ssid
                elif 'Signal level=' in line:
                    match = re.search(r'Signal level=(-?\d+)', line)
                    if match:
                        current_network['rssi'] = int(match.group(1))
                elif 'Frequency:' in line:
                    if '5.' in line:
                        current_network['band'] = '5GHz'
                    else:
                        current_network['band'] = '2.4GHz'
                elif 'Encryption key:' in line:
                    if 'off' in line:
                        current_network['encryption'] = 'Open'
                    else:
                        current_network['encryption'] = 'WPA/WPA2'
            
            if current_network:
                networks.append(current_network)
        
    except Exception as e:
        logger.warning(f"解析WiFi扫描输出失败: {str(e)}")
    
    return networks

def _parse_signal_analysis_output(output: str, system: str) -> Dict:
    """解析信号分析输出"""
    signal_data = {}
    
    try:
        if system == "darwin":  # macOS
            for line in output.split('\n'):
                if 'SSID:' in line:
                    signal_data['ssid'] = line.split('SSID:')[1].strip()
                elif 'BSSID:' in line:
                    signal_data['bssid'] = line.split('BSSID:')[1].strip()
                elif 'RSSI:' in line:
                    signal_data['rssi'] = int(line.split('RSSI:')[1].strip())
                elif 'Channel:' in line:
                    signal_data['channel'] = line.split('Channel:')[1].strip()
        
        elif system == "linux":  # Linux
            for line in output.split('\n'):
                if 'ESSID:' in line:
                    match = re.search(r'ESSID:"([^"]*)"', line)
                    if match:
                        signal_data['ssid'] = match.group(1)
                elif 'Signal level=' in line:
                    match = re.search(r'Signal level=(-?\d+)', line)
                    if match:
                        signal_data['rssi'] = int(match.group(1))
                        # 计算信号质量百分比
                        signal_quality = max(0, min(100, (70 + int(match.group(1))) * 100 // 40))
                        signal_data['quality'] = signal_quality
        
    except Exception as e:
        logger.warning(f"解析信号分析输出失败: {str(e)}")
    
    return signal_data

def _parse_network_interfaces_output(output: str, system: str) -> List[Dict]:
    """解析网络接口输出"""
    interfaces = []
    
    try:
        if system in ["darwin", "linux"]:  # macOS/Linux
            current_interface = {}
            for line in output.split('\n'):
                if ':' in line and not line.startswith(' '):
                    if current_interface:
                        interfaces.append(current_interface)
                    interface_name = line.split(':')[0].strip()
                    current_interface = {
                        "name": interface_name,
                        "addresses": []
                    }
                elif 'inet' in line and current_interface:
                    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        current_interface['addresses'].append({
                            "type": "IPv4",
                            "address": match.group(1)
                        })
            
            if current_interface:
                interfaces.append(current_interface)
        
    except Exception as e:
        logger.warning(f"解析网络接口输出失败: {str(e)}")
    
    return interfaces

def _parse_dns_lookup_output(output: str, record_type: str) -> Dict:
    """解析DNS查询输出"""
    dns_data = {"records": []}
    
    try:
        lines = output.split('\n')
        for line in lines:
            if 'Address:' in line:
                address = line.split('Address:')[1].strip()
                dns_data["records"].append({
                    "type": record_type,
                    "value": address
                })
            elif 'Name:' in line:
                dns_data["canonical_name"] = line.split('Name:')[1].strip()
    
    except Exception as e:
        logger.warning(f"解析DNS查询输出失败: {str(e)}")
    
    return dns_data

def main():
    """运行MCP服务器"""
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