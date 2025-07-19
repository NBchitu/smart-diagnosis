"""
网络抓包分析MCP服务器
"""

import asyncio
import subprocess
import json
import tempfile
import os
import sys
from typing import Dict, List, Optional
import logging
from fastmcp import FastMCP

# 创建MCP应用
mcp = FastMCP("Network Packet Analysis Server")

logger = logging.getLogger(__name__)

@mcp.tool()
async def capture_packets(
    interface: str = "wlan0",
    duration: int = 30,
    packet_count: int = 100,
    filter_expression: str = ""
) -> Dict:
    """
    抓取网络数据包
    
    Args:
        interface: 网络接口名称，默认wlan0
        duration: 抓包时长（秒），默认30秒
        packet_count: 最大抓包数量，默认100个
        filter_expression: 过滤表达式（tcpdump格式）
    
    Returns:
        抓包结果和统计信息
    """
    try:
        # 创建临时文件存储抓包结果
        with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as temp_file:
            pcap_file = temp_file.name
        
        # 构建tcpdump命令
        cmd = [
            "sudo", "tcpdump",
            "-i", interface,
            "-c", str(packet_count),
            "-w", pcap_file,
            "-n"  # 不解析主机名
        ]
        
        # 添加超时
        if duration > 0:
            cmd.extend(["-G", str(duration)])
        
        # 添加过滤表达式
        if filter_expression:
            cmd.append(filter_expression)
        
        # 执行抓包
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=duration + 10
            )
        except asyncio.TimeoutError:
            process.kill()
            stdout, stderr = await process.communicate()
        
        # 分析抓包结果
        analysis_result = await _analyze_pcap_file(pcap_file)
        
        # 清理临时文件
        try:
            os.unlink(pcap_file)
        except OSError:
            pass
        
        return {
            "success": process.returncode == 0,
            "interface": interface,
            "duration": duration,
            "packet_count": packet_count,
            "filter": filter_expression,
            "capture_output": stderr.decode('utf-8') if stderr else "",
            "analysis": analysis_result
        }
        
    except Exception as e:
        logger.error(f"抓包失败: {str(e)}")
        return {
            "success": False,
            "error": f"抓包异常: {str(e)}",
            "interface": interface,
            "analysis": {}
        }

@mcp.tool()
async def analyze_network_traffic(
    interface: str = "wlan0",
    duration: int = 60,
    detailed: bool = False
) -> Dict:
    """
    分析网络流量
    
    Args:
        interface: 网络接口名称
        duration: 分析时长（秒）
        detailed: 是否进行详细分析
    
    Returns:
        网络流量分析结果
    """
    try:
        # 抓取数据包进行流量分析
        capture_result = await capture_packets(
            interface=interface,
            duration=duration,
            packet_count=1000
        )
        
        if not capture_result["success"]:
            return {
                "success": False,
                "error": "无法抓取数据包进行流量分析",
                "traffic_analysis": {}
            }
        
        # 获取流量统计
        traffic_stats = await _get_interface_stats(interface)
        
        # 分析协议分布
        protocol_analysis = capture_result["analysis"].get("protocol_distribution", {})
        
        return {
            "success": True,
            "interface": interface,
            "duration": duration,
            "traffic_analysis": {
                "interface_stats": traffic_stats,
                "protocol_distribution": protocol_analysis,
                "packet_analysis": capture_result["analysis"],
                "detailed": detailed
            }
        }
        
    except Exception as e:
        logger.error(f"流量分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"流量分析异常: {str(e)}",
            "traffic_analysis": {}
        }

@mcp.tool()
async def detect_network_anomalies(
    interface: str = "wlan0",
    baseline_duration: int = 300,
    monitor_duration: int = 60
) -> Dict:
    """
    检测网络异常
    
    Args:
        interface: 网络接口名称
        baseline_duration: 基线建立时长（秒）
        monitor_duration: 监控时长（秒）
    
    Returns:
        网络异常检测结果
    """
    try:
        # 建立基线
        logger.info(f"建立网络基线，时长: {baseline_duration}秒")
        baseline_result = await analyze_network_traffic(
            interface=interface,
            duration=baseline_duration,
            detailed=True
        )
        
        if not baseline_result["success"]:
            return {
                "success": False,
                "error": "无法建立网络基线",
                "anomalies": []
            }
        
        # 监控网络
        logger.info(f"监控网络异常，时长: {monitor_duration}秒")
        monitor_result = await analyze_network_traffic(
            interface=interface,
            duration=monitor_duration,
            detailed=True
        )
        
        if not monitor_result["success"]:
            return {
                "success": False,
                "error": "网络监控失败",
                "anomalies": []
            }
        
        # 检测异常
        anomalies = _detect_anomalies(
            baseline_result["traffic_analysis"],
            monitor_result["traffic_analysis"]
        )
        
        return {
            "success": True,
            "interface": interface,
            "baseline_duration": baseline_duration,
            "monitor_duration": monitor_duration,
            "anomalies": anomalies,
            "baseline_stats": baseline_result["traffic_analysis"]["interface_stats"],
            "current_stats": monitor_result["traffic_analysis"]["interface_stats"]
        }
        
    except Exception as e:
        logger.error(f"异常检测失败: {str(e)}")
        return {
            "success": False,
            "error": f"异常检测失败: {str(e)}",
            "anomalies": []
        }

@mcp.tool()
async def analyze_bandwidth_usage(
    interface: str = "wlan0",
    duration: int = 60,
    interval: int = 5
) -> Dict:
    """
    分析带宽使用情况
    
    Args:
        interface: 网络接口名称
        duration: 分析时长（秒）
        interval: 采样间隔（秒）
    
    Returns:
        带宽使用分析结果
    """
    try:
        samples = []
        total_samples = duration // interval
        
        for i in range(total_samples):
            # 获取接口统计
            stats = await _get_interface_stats(interface)
            
            sample = {
                "timestamp": asyncio.get_event_loop().time(),
                "rx_bytes": stats.get("rx_bytes", 0),
                "tx_bytes": stats.get("tx_bytes", 0),
                "rx_packets": stats.get("rx_packets", 0),
                "tx_packets": stats.get("tx_packets", 0)
            }
            samples.append(sample)
            
            if i < total_samples - 1:
                await asyncio.sleep(interval)
        
        # 计算带宽使用率
        bandwidth_analysis = _calculate_bandwidth_usage(samples, interval)
        
        return {
            "success": True,
            "interface": interface,
            "duration": duration,
            "interval": interval,
            "samples": samples,
            "bandwidth_analysis": bandwidth_analysis
        }
        
    except Exception as e:
        logger.error(f"带宽分析失败: {str(e)}")
        return {
            "success": False,
            "error": f"带宽分析异常: {str(e)}",
            "bandwidth_analysis": {}
        }

async def _analyze_pcap_file(pcap_file: str) -> Dict:
    """分析PCAP文件"""
    try:
        # 使用tcpdump分析PCAP文件
        cmd = ["tcpdump", "-r", pcap_file, "-n", "-q"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {"error": "无法分析PCAP文件"}
        
        # 解析输出
        output = stdout.decode('utf-8')
        analysis = _parse_tcpdump_output(output)
        
        return analysis
        
    except Exception as e:
        logger.error(f"PCAP分析失败: {str(e)}")
        return {"error": f"PCAP分析异常: {str(e)}"}

async def _get_interface_stats(interface: str) -> Dict:
    """获取网络接口统计信息"""
    try:
        # 读取接口统计文件
        stats_file = f"/sys/class/net/{interface}/statistics"
        
        stats = {}
        stat_files = [
            "rx_bytes", "tx_bytes", "rx_packets", "tx_packets",
            "rx_errors", "tx_errors", "rx_dropped", "tx_dropped"
        ]
        
        for stat_name in stat_files:
            try:
                with open(f"{stats_file}/{stat_name}", 'r') as f:
                    stats[stat_name] = int(f.read().strip())
            except (FileNotFoundError, ValueError):
                stats[stat_name] = 0
        
        return stats
        
    except Exception as e:
        logger.error(f"获取接口统计失败: {str(e)}")
        return {}

def _parse_tcpdump_output(output: str) -> Dict:
    """解析tcpdump输出"""
    analysis = {
        "total_packets": 0,
        "protocol_distribution": {},
        "source_ips": {},
        "destination_ips": {},
        "packet_sizes": []
    }
    
    try:
        lines = output.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            analysis["total_packets"] += 1
            
            # 简单的协议识别
            if "TCP" in line:
                analysis["protocol_distribution"]["TCP"] = \
                    analysis["protocol_distribution"].get("TCP", 0) + 1
            elif "UDP" in line:
                analysis["protocol_distribution"]["UDP"] = \
                    analysis["protocol_distribution"].get("UDP", 0) + 1
            elif "ICMP" in line:
                analysis["protocol_distribution"]["ICMP"] = \
                    analysis["protocol_distribution"].get("ICMP", 0) + 1
            else:
                analysis["protocol_distribution"]["OTHER"] = \
                    analysis["protocol_distribution"].get("OTHER", 0) + 1
        
    except Exception as e:
        logger.warning(f"解析tcpdump输出失败: {str(e)}")
    
    return analysis

def _detect_anomalies(baseline: Dict, current: Dict) -> List[Dict]:
    """检测网络异常"""
    anomalies = []
    
    try:
        # 比较接口统计
        baseline_stats = baseline.get("interface_stats", {})
        current_stats = current.get("interface_stats", {})
        
        # 检测流量异常（简化版）
        for stat_name in ["rx_bytes", "tx_bytes", "rx_packets", "tx_packets"]:
            baseline_val = baseline_stats.get(stat_name, 0)
            current_val = current_stats.get(stat_name, 0)
            
            if baseline_val > 0:
                change_ratio = (current_val - baseline_val) / baseline_val
                
                # 如果变化超过50%，认为是异常
                if abs(change_ratio) > 0.5:
                    anomalies.append({
                        "type": "traffic_anomaly",
                        "metric": stat_name,
                        "baseline_value": baseline_val,
                        "current_value": current_val,
                        "change_ratio": change_ratio,
                        "severity": "high" if abs(change_ratio) > 1.0 else "medium"
                    })
        
        # 检测协议分布异常
        baseline_protocols = baseline.get("protocol_distribution", {})
        current_protocols = current.get("protocol_distribution", {})
        
        for protocol in set(list(baseline_protocols.keys()) + list(current_protocols.keys())):
            baseline_count = baseline_protocols.get(protocol, 0)
            current_count = current_protocols.get(protocol, 0)
            
            if baseline_count > 0:
                change_ratio = (current_count - baseline_count) / baseline_count
                
                if abs(change_ratio) > 1.0:  # 协议流量变化超过100%
                    anomalies.append({
                        "type": "protocol_anomaly",
                        "protocol": protocol,
                        "baseline_count": baseline_count,
                        "current_count": current_count,
                        "change_ratio": change_ratio,
                        "severity": "medium"
                    })
                    
    except Exception as e:
        logger.warning(f"异常检测失败: {str(e)}")
    
    return anomalies

def _calculate_bandwidth_usage(samples: List[Dict], interval: int) -> Dict:
    """计算带宽使用情况"""
    analysis = {
        "avg_rx_rate": 0,
        "avg_tx_rate": 0,
        "max_rx_rate": 0,
        "max_tx_rate": 0,
        "total_rx_bytes": 0,
        "total_tx_bytes": 0,
        "rates": []
    }
    
    try:
        if len(samples) < 2:
            return analysis
        
        rx_rates = []
        tx_rates = []
        
        for i in range(1, len(samples)):
            prev_sample = samples[i-1]
            curr_sample = samples[i]
            
            # 计算速率 (bytes/sec)
            rx_rate = (curr_sample["rx_bytes"] - prev_sample["rx_bytes"]) / interval
            tx_rate = (curr_sample["tx_bytes"] - prev_sample["tx_bytes"]) / interval
            
            rx_rates.append(rx_rate)
            tx_rates.append(tx_rate)
            
            analysis["rates"].append({
                "timestamp": curr_sample["timestamp"],
                "rx_rate": rx_rate,
                "tx_rate": tx_rate
            })
        
        # 计算统计信息
        if rx_rates:
            analysis["avg_rx_rate"] = sum(rx_rates) / len(rx_rates)
            analysis["max_rx_rate"] = max(rx_rates)
        
        if tx_rates:
            analysis["avg_tx_rate"] = sum(tx_rates) / len(tx_rates)
            analysis["max_tx_rate"] = max(tx_rates)
        
        # 总字节数
        if samples:
            first_sample = samples[0]
            last_sample = samples[-1]
            analysis["total_rx_bytes"] = last_sample["rx_bytes"] - first_sample["rx_bytes"]
            analysis["total_tx_bytes"] = last_sample["tx_bytes"] - first_sample["tx_bytes"]
            
    except Exception as e:
        logger.warning(f"带宽计算失败: {str(e)}")
    
    return analysis

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