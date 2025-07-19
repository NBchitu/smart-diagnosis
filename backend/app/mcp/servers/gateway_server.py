"""
网关信息获取MCP服务器
"""

import asyncio
import subprocess
import json
import re
import sys
from typing import Dict, List, Optional
import logging
from fastmcp import FastMCP

# 创建MCP应用
mcp = FastMCP("Gateway Information Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def get_default_gateway() -> Dict:
    """
    获取默认网关信息
    
    Returns:
        默认网关信息
    """
    try:
        # 使用ip route命令获取默认网关
        cmd = ["ip", "route", "show", "default"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "获取默认网关失败",
                "gateway": None
            }
        
        # 解析路由信息
        route_info = _parse_route_output(stdout.decode('utf-8'))
        
        # 获取网关详细信息
        if route_info.get("gateway"):
            gateway_details = await _get_gateway_details(route_info["gateway"])
            route_info.update(gateway_details)
        
        return {
            "success": True,
            "gateway": route_info
        }
        
    except Exception as e:
        logger.error(f"获取默认网关失败: {str(e)}")
        return {
            "success": False,
            "error": f"获取默认网关异常: {str(e)}",
            "gateway": None
        }

@mcp.tool()
async def get_all_gateways() -> Dict:
    """
    获取所有网关信息
    
    Returns:
        所有网关信息列表
    """
    try:
        # 获取所有路由信息
        cmd = ["ip", "route", "show"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "获取路由信息失败",
                "gateways": []
            }
        
        # 解析所有路由
        routes = _parse_all_routes(stdout.decode('utf-8'))
        
        # 提取网关信息
        gateways = []
        gateway_ips = set()
        
        for route in routes:
            if route.get("gateway") and route["gateway"] not in gateway_ips:
                gateway_ips.add(route["gateway"])
                gateway_details = await _get_gateway_details(route["gateway"])
                gateway_details.update({
                    "destination": route.get("destination", ""),
                    "interface": route.get("interface", ""),
                    "metric": route.get("metric", 0)
                })
                gateways.append(gateway_details)
        
        return {
            "success": True,
            "total_gateways": len(gateways),
            "gateways": gateways
        }
        
    except Exception as e:
        logger.error(f"获取所有网关失败: {str(e)}")
        return {
            "success": False,
            "error": f"获取所有网关异常: {str(e)}",
            "gateways": []
        }

@mcp.tool()
async def probe_gateway(
    gateway_ip: str,
    detailed: bool = True
) -> Dict:
    """
    探测网关信息
    
    Args:
        gateway_ip: 网关IP地址
        detailed: 是否进行详细探测
    
    Returns:
        网关探测结果
    """
    try:
        # 基本连通性测试
        ping_result = await _ping_gateway(gateway_ip)
        
        # 获取基本信息
        gateway_info = {
            "ip": gateway_ip,
            "reachable": ping_result["success"],
            "response_time": ping_result.get("avg_time", 0),
            "packet_loss": ping_result.get("packet_loss", 100)
        }
        
        if detailed and ping_result["success"]:
            # 详细探测
            details = await _detailed_gateway_probe(gateway_ip)
            gateway_info.update(details)
        
        return {
            "success": True,
            "gateway_info": gateway_info
        }
        
    except Exception as e:
        logger.error(f"探测网关失败: {str(e)}")
        return {
            "success": False,
            "error": f"探测网关异常: {str(e)}",
            "gateway_info": {}
        }

@mcp.tool()
async def analyze_gateway_performance(
    gateway_ip: Optional[str] = None,
    test_duration: int = 60,
    test_interval: int = 5
) -> Dict:
    """
    分析网关性能
    
    Args:
        gateway_ip: 网关IP地址，None表示使用默认网关
        test_duration: 测试时长（秒）
        test_interval: 测试间隔（秒）
    
    Returns:
        网关性能分析结果
    """
    try:
        # 如果未指定网关，获取默认网关
        if not gateway_ip:
            default_gw = await get_default_gateway()
            if not default_gw["success"]:
                return {
                    "success": False,
                    "error": "无法获取默认网关",
                    "performance": {}
                }
            gateway_ip = default_gw["gateway"]["gateway"]
        
        # 执行性能测试
        test_results = []
        test_count = test_duration // test_interval
        
        for i in range(test_count):
            # Ping测试
            ping_result = await _ping_gateway(gateway_ip, count=3)
            
            test_result = {
                "timestamp": asyncio.get_event_loop().time(),
                "success": ping_result["success"],
                "response_time": ping_result.get("avg_time", 0),
                "packet_loss": ping_result.get("packet_loss", 100),
                "min_time": ping_result.get("min_time", 0),
                "max_time": ping_result.get("max_time", 0)
            }
            test_results.append(test_result)
            
            if i < test_count - 1:
                await asyncio.sleep(test_interval)
        
        # 分析性能数据
        performance_analysis = _analyze_performance_data(test_results)
        
        return {
            "success": True,
            "gateway_ip": gateway_ip,
            "test_duration": test_duration,
            "test_interval": test_interval,
            "test_results": test_results,
            "performance_analysis": performance_analysis
        }
        
    except Exception as e:
        logger.error(f"网关性能分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"网关性能分析异常: {str(e)}",
            "performance": {}
        }

@mcp.tool()
async def check_gateway_services(gateway_ip: str) -> Dict:
    """
    检查网关服务
    
    Args:
        gateway_ip: 网关IP地址
    
    Returns:
        网关服务检查结果
    """
    try:
        services = {}
        common_ports = {
            22: "SSH",
            23: "Telnet", 
            53: "DNS",
            80: "HTTP",
            443: "HTTPS",
            8080: "HTTP-Alt",
            161: "SNMP",
            554: "RTSP"
        }
        
        # 并发检查常用端口
        tasks = []
        for port, service in common_ports.items():
            tasks.append(_check_port(gateway_ip, port, service))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for result in results:
            if isinstance(result, dict):
                port = result["port"]
                services[port] = result
        
        # 尝试识别设备类型
        device_type = _identify_device_type(services)
        
        return {
            "success": True,
            "gateway_ip": gateway_ip,
            "services": services,
            "device_type": device_type,
            "open_ports": [p for p, s in services.items() if s.get("open", False)]
        }
        
    except Exception as e:
        logger.error(f"检查网关服务失败: {str(e)}")
        return {
            "success": False,
            "error": f"检查网关服务异常: {str(e)}",
            "services": {}
        }

async def _get_gateway_details(gateway_ip: str) -> Dict:
    """获取网关详细信息"""
    details = {"gateway": gateway_ip}
    
    try:
        # 获取ARP信息
        arp_info = await _get_arp_info(gateway_ip)
        if arp_info:
            details.update(arp_info)
        
        # 尝试反向DNS解析
        hostname = await _reverse_dns_lookup(gateway_ip)
        if hostname:
            details["hostname"] = hostname
            
    except Exception as e:
        logger.warning(f"获取网关详细信息失败: {str(e)}")
    
    return details

async def _ping_gateway(gateway_ip: str, count: int = 4) -> Dict:
    """Ping网关"""
    try:
        cmd = ["ping", "-c", str(count), "-W", "3", gateway_ip]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        result = {
            "success": process.returncode == 0,
            "output": stdout.decode('utf-8') if stdout else "",
            "error": stderr.decode('utf-8') if stderr else ""
        }
        
        # 解析ping结果
        if result["success"]:
            result.update(_parse_ping_output(result["output"]))
        
        return result
        
    except Exception as e:
        logger.error(f"Ping网关失败: {str(e)}")
        return {"success": False, "error": f"Ping异常: {str(e)}"}

async def _detailed_gateway_probe(gateway_ip: str) -> Dict:
    """详细探测网关"""
    details = {}
    
    try:
        # TTL检测
        ttl_info = await _detect_ttl(gateway_ip)
        if ttl_info:
            details["ttl_info"] = ttl_info
        
        # 操作系统指纹识别
        os_info = await _os_fingerprint(gateway_ip)
        if os_info:
            details["os_info"] = os_info
            
    except Exception as e:
        logger.warning(f"详细探测失败: {str(e)}")
    
    return details

async def _get_arp_info(ip: str) -> Optional[Dict]:
    """获取ARP信息"""
    try:
        cmd = ["arp", "-n", ip]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            # 解析ARP输出
            for line in output.split('\n'):
                if ip in line and "incomplete" not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return {
                            "mac_address": parts[2],
                            "interface": parts[-1] if len(parts) > 3 else ""
                        }
                        
    except Exception as e:
        logger.warning(f"获取ARP信息失败: {str(e)}")
    
    return None

async def _reverse_dns_lookup(ip: str) -> Optional[str]:
    """反向DNS查找"""
    try:
        cmd = ["host", ip]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            # 解析host命令输出
            if "domain name pointer" in output:
                hostname = output.split("domain name pointer")[-1].strip().rstrip('.')
                return hostname
                
    except Exception as e:
        logger.warning(f"反向DNS查找失败: {str(e)}")
    
    return None

async def _check_port(ip: str, port: int, service: str) -> Dict:
    """检查端口是否开放"""
    try:
        # 使用nc命令检查端口
        cmd = ["nc", "-z", "-w", "3", ip, str(port)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "port": port,
            "service": service,
            "open": process.returncode == 0,
            "response_time": 0  # 简化实现
        }
        
    except Exception as e:
        logger.warning(f"检查端口 {port} 失败: {str(e)}")
        return {
            "port": port,
            "service": service,
            "open": False,
            "error": str(e)
        }

def _parse_route_output(output: str) -> Dict:
    """解析路由命令输出"""
    route_info = {}
    
    try:
        # 解析默认路由
        for line in output.split('\n'):
            if line.strip() and "default" in line:
                parts = line.split()
                
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        route_info["gateway"] = parts[i + 1]
                    elif part == "dev" and i + 1 < len(parts):
                        route_info["interface"] = parts[i + 1]
                    elif part == "metric" and i + 1 < len(parts):
                        route_info["metric"] = int(parts[i + 1])
                break
                
    except Exception as e:
        logger.warning(f"解析路由输出失败: {str(e)}")
    
    return route_info

def _parse_all_routes(output: str) -> List[Dict]:
    """解析所有路由"""
    routes = []
    
    try:
        for line in output.split('\n'):
            if not line.strip():
                continue
                
            route = {}
            parts = line.split()
            
            if parts:
                # 目标网络
                route["destination"] = parts[0]
                
                # 查找网关
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        route["gateway"] = parts[i + 1]
                    elif part == "dev" and i + 1 < len(parts):
                        route["interface"] = parts[i + 1]
                    elif part == "metric" and i + 1 < len(parts):
                        route["metric"] = int(parts[i + 1])
                
                routes.append(route)
                
    except Exception as e:
        logger.warning(f"解析所有路由失败: {str(e)}")
    
    return routes

def _parse_ping_output(output: str) -> Dict:
    """解析ping输出"""
    result = {}
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            if "packets transmitted" in line:
                parts = line.split()
                transmitted = int(parts[0])
                received_idx = parts.index("received,") if "received," in parts else parts.index("received")
                received = int(parts[received_idx - 1])
                
                result["packets_transmitted"] = transmitted
                result["packets_received"] = received
                result["packet_loss"] = ((transmitted - received) / transmitted) * 100
                
            elif "round-trip" in line or "rtt" in line:
                # min/avg/max时间
                parts = line.split("=")[-1].strip().split("/")
                if len(parts) >= 3:
                    result["min_time"] = float(parts[0])
                    result["avg_time"] = float(parts[1])
                    result["max_time"] = float(parts[2])
                    
    except Exception as e:
        logger.warning(f"解析ping输出失败: {str(e)}")
    
    return result

def _analyze_performance_data(test_results: List[Dict]) -> Dict:
    """分析性能数据"""
    analysis = {
        "availability": 0,
        "avg_response_time": 0,
        "min_response_time": float('inf'),
        "max_response_time": 0,
        "jitter": 0,
        "total_packet_loss": 0,
        "quality_rating": "unknown"
    }
    
    try:
        if not test_results:
            return analysis
        
        successful_tests = [r for r in test_results if r["success"]]
        response_times = [r["response_time"] for r in successful_tests if r["response_time"] > 0]
        
        # 可用性
        analysis["availability"] = (len(successful_tests) / len(test_results)) * 100
        
        # 响应时间统计
        if response_times:
            analysis["avg_response_time"] = sum(response_times) / len(response_times)
            analysis["min_response_time"] = min(response_times)
            analysis["max_response_time"] = max(response_times)
            
            # 抖动计算（响应时间标准差）
            if len(response_times) > 1:
                avg = analysis["avg_response_time"]
                variance = sum((t - avg) ** 2 for t in response_times) / len(response_times)
                analysis["jitter"] = variance ** 0.5
        
        # 总体丢包率
        total_loss = sum(r["packet_loss"] for r in test_results)
        analysis["total_packet_loss"] = total_loss / len(test_results)
        
        # 质量评级
        analysis["quality_rating"] = _calculate_quality_rating(analysis)
        
    except Exception as e:
        logger.warning(f"性能数据分析失败: {str(e)}")
    
    return analysis

def _calculate_quality_rating(analysis: Dict) -> str:
    """计算质量评级"""
    try:
        availability = analysis["availability"]
        avg_time = analysis["avg_response_time"]
        packet_loss = analysis["total_packet_loss"]
        
        # 评分算法
        if availability >= 99 and avg_time <= 10 and packet_loss <= 1:
            return "excellent"
        elif availability >= 95 and avg_time <= 50 and packet_loss <= 5:
            return "good"
        elif availability >= 90 and avg_time <= 100 and packet_loss <= 10:
            return "fair"
        else:
            return "poor"
            
    except Exception:
        return "unknown"

def _identify_device_type(services: Dict) -> str:
    """识别设备类型"""
    try:
        open_ports = [p for p, s in services.items() if s.get("open", False)]
        
        # 基于开放端口推断设备类型
        if 80 in open_ports or 443 in open_ports:
            if 22 in open_ports:
                return "managed_router"
            else:
                return "router"
        elif 161 in open_ports:
            return "managed_device"
        elif 22 in open_ports:
            return "linux_device"
        elif 23 in open_ports:
            return "legacy_device"
        else:
            return "unknown"
            
    except Exception:
        return "unknown"

async def _detect_ttl(ip: str) -> Optional[Dict]:
    """检测TTL值"""
    try:
        ping_result = await _ping_gateway(ip, count=1)
        if ping_result["success"]:
            output = ping_result["output"]
            # 提取TTL值
            ttl_match = re.search(r'ttl=(\d+)', output)
            if ttl_match:
                ttl = int(ttl_match.group(1))
                return {
                    "ttl": ttl,
                    "estimated_hops": 64 - ttl if ttl <= 64 else 128 - ttl
                }
    except Exception:
        pass
    
    return None

async def _os_fingerprint(ip: str) -> Optional[Dict]:
    """操作系统指纹识别（简化版）"""
    try:
        ttl_info = await _detect_ttl(ip)
        if ttl_info:
            ttl = ttl_info["ttl"]
            
            # 基于TTL推断操作系统
            if ttl >= 60 and ttl <= 64:
                return {"os_family": "Linux/Unix", "confidence": "medium"}
            elif ttl >= 124 and ttl <= 128:
                return {"os_family": "Windows", "confidence": "medium"}
            elif ttl >= 252 and ttl <= 255:
                return {"os_family": "Cisco/Network Device", "confidence": "medium"}
                
    except Exception:
        pass
    
    return None

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