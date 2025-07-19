"""
网络连通性检查MCP服务器
"""

import asyncio
import subprocess
import json
import time
import sys
from typing import Dict, List, Optional
import logging
from fastmcp import FastMCP

# 创建MCP应用
mcp = FastMCP("Network Connectivity Check Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def check_internet_connectivity(
    test_hosts: Optional[List[str]] = None,
    timeout: int = 10
) -> Dict:
    """
    检查互联网连通性
    
    Args:
        test_hosts: 测试主机列表，默认使用常用DNS服务器
        timeout: 超时时间（秒）
    
    Returns:
        互联网连通性检查结果
    """
    if test_hosts is None:
        test_hosts = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "208.67.222.222", # OpenDNS
            "114.114.114.114" # 114 DNS
        ]
    
    try:
        results = {}
        successful_tests = 0
        
        # 并发测试多个主机
        tasks = []
        for host in test_hosts:
            tasks.append(_test_host_connectivity(host, timeout))
        
        connectivity_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(connectivity_results):
            host = test_hosts[i]
            if isinstance(result, Exception):
                results[host] = {
                    "success": False,
                    "error": f"测试异常: {str(result)}",
                    "response_time": 0
                }
            else:
                results[host] = result
                if result["success"]:
                    successful_tests += 1
        
        # 计算整体连通性
        connectivity_score = (successful_tests / len(test_hosts)) * 100
        
        return {
            "success": True,
            "connectivity_score": connectivity_score,
            "internet_accessible": connectivity_score >= 50,
            "total_tests": len(test_hosts),
            "successful_tests": successful_tests,
            "test_results": results,
            "recommendation": _get_connectivity_recommendation(connectivity_score)
        }
        
    except Exception as e:
        logger.error(f"互联网连通性检查失败: {str(e)}")
        return {
            "success": False,
            "error": f"连通性检查异常: {str(e)}",
            "connectivity_score": 0,
            "internet_accessible": False
        }

@mcp.tool()
async def check_dns_resolution(
    domains: Optional[List[str]] = None,
    dns_servers: Optional[List[str]] = None
) -> Dict:
    """
    检查DNS解析
    
    Args:
        domains: 要测试的域名列表
        dns_servers: DNS服务器列表
    
    Returns:
        DNS解析检查结果
    """
    if domains is None:
        domains = [
            "www.google.com",
            "www.baidu.com", 
            "www.qq.com",
            "github.com"
        ]
    
    if dns_servers is None:
        dns_servers = [
            "8.8.8.8",
            "1.1.1.1",
            "114.114.114.114"
        ]
    
    try:
        results = {}
        
        # 测试每个DNS服务器
        for dns_server in dns_servers:
            server_results = {}
            successful_resolutions = 0
            
            # 测试每个域名
            for domain in domains:
                resolution_result = await _test_dns_resolution(domain, dns_server)
                server_results[domain] = resolution_result
                
                if resolution_result["success"]:
                    successful_resolutions += 1
            
            # 计算成功率
            success_rate = (successful_resolutions / len(domains)) * 100
            
            results[dns_server] = {
                "success_rate": success_rate,
                "successful_resolutions": successful_resolutions,
                "total_domains": len(domains),
                "domain_results": server_results
            }
        
        # 分析总体DNS状况
        dns_analysis = _analyze_dns_results(results)
        
        return {
            "success": True,
            "dns_servers_tested": len(dns_servers),
            "domains_tested": len(domains),
            "results": results,
            "analysis": dns_analysis
        }
        
    except Exception as e:
        logger.error(f"DNS解析检查失败: {str(e)}")
        return {
            "success": False,
            "error": f"DNS解析检查异常: {str(e)}",
            "results": {}
        }

@mcp.tool()
async def check_port_connectivity(
    host: str,
    ports: List[int],
    timeout: int = 5
) -> Dict:
    """
    检查端口连通性
    
    Args:
        host: 目标主机
        ports: 端口列表
        timeout: 超时时间（秒）
    
    Returns:
        端口连通性检查结果
    """
    try:
        results = {}
        open_ports = []
        closed_ports = []
        
        # 并发测试所有端口
        tasks = []
        for port in ports:
            tasks.append(_test_port_connectivity(host, port, timeout))
        
        port_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(port_results):
            port = ports[i]
            if isinstance(result, Exception):
                results[port] = {
                    "open": False,
                    "error": f"测试异常: {str(result)}",
                    "response_time": 0
                }
                closed_ports.append(port)
            else:
                results[port] = result
                if result["open"]:
                    open_ports.append(port)
                else:
                    closed_ports.append(port)
        
        return {
            "success": True,
            "host": host,
            "total_ports": len(ports),
            "open_ports": open_ports,
            "closed_ports": closed_ports,
            "open_count": len(open_ports),
            "closed_count": len(closed_ports),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"端口连通性检查失败: {str(e)}")
        return {
            "success": False,
            "error": f"端口连通性检查异常: {str(e)}",
            "results": {}
        }

@mcp.tool()
async def bandwidth_test(
    test_duration: int = 30,
    server_url: Optional[str] = None
) -> Dict:
    """
    网络带宽测试
    
    Args:
        test_duration: 测试时长（秒）
        server_url: 测试服务器URL
    
    Returns:
        带宽测试结果
    """
    try:
        # 使用speedtest-cli进行带宽测试
        cmd = ["speedtest-cli", "--json", "--timeout", str(test_duration)]
        
        if server_url:
            cmd.extend(["--server", server_url])
        
        start_time = time.time()
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=test_duration + 30
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": "带宽测试超时",
                "test_duration": test_duration
            }
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        if process.returncode != 0:
            return {
                "success": False,
                "error": stderr.decode('utf-8') if stderr else "带宽测试失败",
                "test_duration": actual_duration
            }
        
        # 解析speedtest结果
        try:
            result = json.loads(stdout.decode('utf-8'))
            
            return {
                "success": True,
                "test_duration": actual_duration,
                "download_speed": result.get("download", 0) / 1024 / 1024,  # Mbps
                "upload_speed": result.get("upload", 0) / 1024 / 1024,      # Mbps
                "ping": result.get("ping", 0),
                "server_info": {
                    "name": result.get("server", {}).get("name", ""),
                    "country": result.get("server", {}).get("country", ""),
                    "sponsor": result.get("server", {}).get("sponsor", "")
                },
                "client_info": {
                    "ip": result.get("client", {}).get("ip", ""),
                    "isp": result.get("client", {}).get("isp", "")
                },
                "raw_result": result
            }
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "无法解析带宽测试结果",
                "test_duration": actual_duration
            }
        
    except Exception as e:
        logger.error(f"带宽测试失败: {str(e)}")
        return {
            "success": False,
            "error": f"带宽测试异常: {str(e)}",
            "test_duration": 0
        }

@mcp.tool()
async def comprehensive_connectivity_test(
    quick_test: bool = False
) -> Dict:
    """
    综合连通性测试
    
    Args:
        quick_test: 是否进行快速测试
    
    Returns:
        综合连通性测试结果
    """
    try:
        test_results = {}
        
        # 1. 互联网连通性测试
        logger.info("开始互联网连通性测试...")
        connectivity_result = await check_internet_connectivity()
        test_results["internet_connectivity"] = connectivity_result
        
        # 2. DNS解析测试
        logger.info("开始DNS解析测试...")
        dns_result = await check_dns_resolution()
        test_results["dns_resolution"] = dns_result
        
        # 3. 常用端口测试
        if not quick_test:
            logger.info("开始端口连通性测试...")
            common_ports = [80, 443, 53, 25, 110, 993, 995]
            port_result = await check_port_connectivity("8.8.8.8", common_ports)
            test_results["port_connectivity"] = port_result
            
            # 4. 带宽测试
            logger.info("开始带宽测试...")
            bandwidth_result = await bandwidth_test(test_duration=15)
            test_results["bandwidth"] = bandwidth_result
        
        # 计算综合评分
        overall_score = _calculate_overall_score(test_results, quick_test)
        
        return {
            "success": True,
            "test_type": "quick" if quick_test else "comprehensive",
            "overall_score": overall_score,
            "test_results": test_results,
            "recommendations": _generate_recommendations(test_results, overall_score)
        }
        
    except Exception as e:
        logger.error(f"综合连通性测试失败: {str(e)}")
        return {
            "success": False,
            "error": f"综合连通性测试异常: {str(e)}",
            "test_results": {}
        }

async def _test_host_connectivity(host: str, timeout: int) -> Dict:
    """测试主机连通性"""
    try:
        cmd = ["ping", "-c", "3", "-W", str(timeout), host]
        
        start_time = time.time()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        end_time = time.time()
        
        success = process.returncode == 0
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        result = {
            "success": success,
            "response_time": response_time,
            "host": host
        }
        
        # 解析ping输出获取详细信息
        if success:
            output = stdout.decode('utf-8')
            ping_stats = _parse_ping_output(output)
            result.update(ping_stats)
        else:
            result["error"] = stderr.decode('utf-8') if stderr else "连接失败"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"测试异常: {str(e)}",
            "response_time": 0,
            "host": host
        }

async def _test_dns_resolution(domain: str, dns_server: str) -> Dict:
    """测试DNS解析"""
    try:
        cmd = ["nslookup", domain, dns_server]
        
        start_time = time.time()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        success = process.returncode == 0
        
        result = {
            "success": success,
            "response_time": response_time,
            "domain": domain,
            "dns_server": dns_server
        }
        
        if success:
            output = stdout.decode('utf-8')
            # 提取IP地址
            ips = _extract_ips_from_nslookup(output)
            result["resolved_ips"] = ips
        else:
            result["error"] = stderr.decode('utf-8') if stderr else "解析失败"
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"解析异常: {str(e)}",
            "response_time": 0,
            "domain": domain,
            "dns_server": dns_server
        }

async def _test_port_connectivity(host: str, port: int, timeout: int) -> Dict:
    """测试端口连通性"""
    try:
        start_time = time.time()
        
        # 使用nc命令测试端口
        cmd = ["nc", "-z", "-w", str(timeout), host, str(port)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        is_open = process.returncode == 0
        
        return {
            "open": is_open,
            "response_time": response_time,
            "port": port,
            "host": host
        }
        
    except Exception as e:
        return {
            "open": False,
            "error": f"测试异常: {str(e)}",
            "response_time": 0,
            "port": port,
            "host": host
        }

def _parse_ping_output(output: str) -> Dict:
    """解析ping输出"""
    stats = {}
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            if "packets transmitted" in line:
                parts = line.split()
                transmitted = int(parts[0])
                received_idx = parts.index("received,") if "received," in parts else parts.index("received")
                received = int(parts[received_idx - 1])
                
                stats["packets_transmitted"] = transmitted
                stats["packets_received"] = received
                stats["packet_loss"] = ((transmitted - received) / transmitted) * 100
                
            elif "round-trip" in line or "rtt" in line:
                # 提取min/avg/max时间
                time_part = line.split("=")[-1].strip()
                times = time_part.split("/")
                if len(times) >= 3:
                    stats["min_time"] = float(times[0])
                    stats["avg_time"] = float(times[1])
                    stats["max_time"] = float(times[2])
                    
    except Exception as e:
        logger.warning(f"解析ping输出失败: {str(e)}")
    
    return stats

def _extract_ips_from_nslookup(output: str) -> List[str]:
    """从nslookup输出中提取IP地址"""
    ips = []
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            if "Address:" in line and "#" not in line:
                # 提取IP地址
                ip = line.split("Address:")[-1].strip()
                if ip and _is_valid_ip(ip):
                    ips.append(ip)
                    
    except Exception as e:
        logger.warning(f"提取IP地址失败: {str(e)}")
    
    return ips

def _is_valid_ip(ip: str) -> bool:
    """验证IP地址格式"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def _analyze_dns_results(results: Dict) -> Dict:
    """分析DNS结果"""
    analysis = {
        "best_dns_server": None,
        "worst_dns_server": None,
        "avg_success_rate": 0,
        "overall_status": "unknown"
    }
    
    try:
        if not results:
            return analysis
        
        success_rates = []
        best_rate = 0
        worst_rate = 100
        
        for dns_server, data in results.items():
            rate = data["success_rate"]
            success_rates.append(rate)
            
            if rate > best_rate:
                best_rate = rate
                analysis["best_dns_server"] = dns_server
            
            if rate < worst_rate:
                worst_rate = rate
                analysis["worst_dns_server"] = dns_server
        
        # 计算平均成功率
        analysis["avg_success_rate"] = sum(success_rates) / len(success_rates)
        
        # 判断总体状态
        if analysis["avg_success_rate"] >= 90:
            analysis["overall_status"] = "excellent"
        elif analysis["avg_success_rate"] >= 70:
            analysis["overall_status"] = "good"
        elif analysis["avg_success_rate"] >= 50:
            analysis["overall_status"] = "fair"
        else:
            analysis["overall_status"] = "poor"
            
    except Exception as e:
        logger.warning(f"DNS结果分析失败: {str(e)}")
    
    return analysis

def _get_connectivity_recommendation(score: float) -> str:
    """获取连通性建议"""
    if score >= 90:
        return "网络连通性优秀，无需调整"
    elif score >= 70:
        return "网络连通性良好，可考虑优化DNS设置"
    elif score >= 50:
        return "网络连通性一般，建议检查网络配置"
    else:
        return "网络连通性较差，需要检查网络连接和设备配置"

def _calculate_overall_score(test_results: Dict, quick_test: bool) -> float:
    """计算综合评分"""
    try:
        scores = []
        
        # 互联网连通性权重 40%
        if "internet_connectivity" in test_results:
            connectivity_score = test_results["internet_connectivity"]["connectivity_score"]
            scores.append(connectivity_score * 0.4)
        
        # DNS解析权重 30%
        if "dns_resolution" in test_results:
            dns_analysis = test_results["dns_resolution"]["analysis"]
            dns_score = dns_analysis.get("avg_success_rate", 0)
            scores.append(dns_score * 0.3)
        
        if not quick_test:
            # 端口连通性权重 15%
            if "port_connectivity" in test_results:
                port_data = test_results["port_connectivity"]
                if port_data["total_ports"] > 0:
                    port_score = (port_data["open_count"] / port_data["total_ports"]) * 100
                    scores.append(port_score * 0.15)
            
            # 带宽权重 15% (基于ping值)
            if "bandwidth" in test_results and test_results["bandwidth"]["success"]:
                ping = test_results["bandwidth"]["ping"]
                # ping越低分数越高 (ping < 50ms = 100分, ping > 200ms = 0分)
                bandwidth_score = max(0, 100 - (ping - 50) * 100 / 150) if ping > 50 else 100
                scores.append(bandwidth_score * 0.15)
        
        return sum(scores) if scores else 0
        
    except Exception as e:
        logger.warning(f"计算综合评分失败: {str(e)}")
        return 0

def _generate_recommendations(test_results: Dict, overall_score: float) -> List[str]:
    """生成改进建议"""
    recommendations = []
    
    try:
        # 基于综合评分的建议
        if overall_score < 50:
            recommendations.append("网络整体状况较差，建议联系网络服务提供商")
        
        # 基于互联网连通性的建议
        if "internet_connectivity" in test_results:
            connectivity = test_results["internet_connectivity"]
            if connectivity["connectivity_score"] < 70:
                recommendations.append("互联网连通性不稳定，检查路由器和网线连接")
        
        # 基于DNS的建议
        if "dns_resolution" in test_results:
            dns_data = test_results["dns_resolution"]
            if dns_data["analysis"]["avg_success_rate"] < 80:
                recommendations.append("DNS解析存在问题，建议更换DNS服务器")
                if dns_data["analysis"]["best_dns_server"]:
                    recommendations.append(f"推荐使用DNS服务器: {dns_data['analysis']['best_dns_server']}")
        
        # 基于带宽的建议
        if "bandwidth" in test_results and test_results["bandwidth"]["success"]:
            bandwidth = test_results["bandwidth"]
            if bandwidth["download_speed"] < 10:  # 小于10Mbps
                recommendations.append("下载速度较慢，考虑升级网络套餐")
            if bandwidth["ping"] > 100:  # ping大于100ms
                recommendations.append("网络延迟较高，检查网络质量")
        
        if not recommendations:
            recommendations.append("网络状况良好，无特殊改进建议")
            
    except Exception as e:
        logger.warning(f"生成建议失败: {str(e)}")
        recommendations.append("无法生成具体建议，请手动检查网络状况")
    
    return recommendations

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