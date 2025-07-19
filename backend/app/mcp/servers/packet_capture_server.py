#!/usr/bin/env python3
"""
智能抓包分析MCP服务器
专注于网络问题诊断，只抓取关键信息避免token浪费
"""

import asyncio
import json
import sys
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import re
import os
import signal
import platform
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PacketSummary:
    """数据包摘要信息"""
    timestamp: str
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    packet_type: str
    summary: str
    flags: List[str]
    size: int

@dataclass
class ConnectionInfo:
    """连接信息"""
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    state: str
    duration: float
    bytes_sent: int
    bytes_received: int

@dataclass
class CaptureSession:
    """抓包会话"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    target: str
    filter_expr: str
    packets: List[PacketSummary]
    connections: Dict[str, ConnectionInfo]
    is_running: bool
    process: Optional[subprocess.Popen]
    duration: int = 30  # 预设时长
    saved_files: List[str] = None  # 保存的文件路径列表
    
    def __post_init__(self):
        if self.saved_files is None:
            self.saved_files = []

class PacketCaptureServer:
    """智能抓包分析服务器"""
    
    def __init__(self):
        self.sessions: Dict[str, CaptureSession] = {}
        self.running = True
        
        # 配置保存目录
        self.save_directory = Path("data/packet_captures").resolve()
        self.save_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"抓包数据保存目录: {self.save_directory}")
        
        # 保存配置
        self.save_formats = ["json", "summary", "raw"]  # 支持的保存格式
        self.auto_save = True  # 是否自动保存
        
    def _check_permissions(self) -> bool:
        """检查是否有抓包权限"""
        try:
            # 尝试创建一个测试抓包进程
            test_cmd = ["tcpdump", "-c", "1", "-i", "any", "-n"]
            result = subprocess.run(
                test_cmd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_available_interfaces(self) -> List[str]:
        """获取可用的网络接口（优化版）"""
        try:
            # 获取活跃接口的更精确方法
            active_interfaces = []
            
            # 首先尝试找到有IP地址且状态为active的接口
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            
            current_interface = None
            has_inet = False
            is_active = False
            
            for line in result.stdout.split('\n'):
                # 检测接口名
                if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                    # 如果之前的接口符合条件，添加到列表
                    if current_interface and has_inet and is_active:
                        active_interfaces.append(current_interface)
                    
                    # 开始新接口
                    interface = line.split(':')[0].strip()
                    if (interface and 
                        interface != 'lo' and 
                        interface != 'lo0' and
                        not interface.startswith('inet') and
                        not interface.startswith('ether') and
                        not interface.startswith('media') and
                        not interface.startswith('status') and
                        len(interface) <= 10 and
                        interface.replace('en', '').replace('eth', '').replace('wlan', '').isdigit() or 
                        interface in ['en0', 'eth0', 'wlan0']):
                        current_interface = interface
                        has_inet = False
                        is_active = False
                    else:
                        current_interface = None
                
                elif current_interface:
                    # 检查是否有IP地址
                    if 'inet ' in line and not '127.0.0.1' in line:
                        has_inet = True
                    # 检查状态
                    if 'status: active' in line:
                        is_active = True
            
            # 检查最后一个接口
            if current_interface and has_inet and is_active:
                active_interfaces.append(current_interface)
            
            # 如果找到活跃接口，优先使用
            if active_interfaces:
                # 将en0放在首位（如果存在）
                if 'en0' in active_interfaces:
                    active_interfaces.remove('en0')
                    active_interfaces.insert(0, 'en0')
                return active_interfaces
            
            # 后备方案：使用预定义的常见接口
            common_interfaces = ["en0", "eth0", "wlan0", "en1", "wlo1"]
            for iface in common_interfaces:
                test_result = subprocess.run(
                    ["ifconfig", iface], 
                    capture_output=True, 
                    text=True
                )
                if test_result.returncode == 0 and 'inet ' in test_result.stdout:
                    return [iface]
            
            return ["en0"]  # 最终后备
            
        except Exception as e:
            logger.error(f"获取网络接口失败: {e}")
            return ["en0"]
    
    def _save_capture_data(self, session: CaptureSession) -> List[str]:
        """保存抓包数据到本地磁盘"""
        saved_files = []
        
        try:
            # 生成文件名前缀
            timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
            safe_target = re.sub(r'[^\w\-_.]', '_', session.target)
            file_prefix = f"{timestamp}_{session.session_id}_{safe_target}"
            
            # 1. 保存JSON格式的详细数据
            if "json" in self.save_formats:
                json_file = self.save_directory / f"{file_prefix}_detailed.json"
                
                # 准备可序列化的数据
                session_data = {
                    "session_info": {
                        "session_id": session.session_id,
                        "start_time": session.start_time.isoformat(),
                        "end_time": session.end_time.isoformat() if session.end_time else None,
                        "target": session.target,
                        "filter_expr": session.filter_expr,
                        "duration": session.duration,
                        "packets_captured": len(session.packets)
                    },
                    "packets": [
                        {
                            "timestamp": packet.timestamp,
                            "protocol": packet.protocol,
                            "src_ip": packet.src_ip,
                            "dst_ip": packet.dst_ip,
                            "src_port": packet.src_port,
                            "dst_port": packet.dst_port,
                            "packet_type": packet.packet_type,
                            "summary": packet.summary,
                            "flags": packet.flags,
                            "size": packet.size
                        }
                        for packet in session.packets
                    ],
                    "analysis": self._analyze_packets(session.packets)
                }
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                saved_files.append(str(json_file))
                logger.info(f"保存JSON数据: {json_file}")
            
            # 2. 保存可读性摘要
            if "summary" in self.save_formats:
                summary_file = self.save_directory / f"{file_prefix}_summary.txt"
                
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"抓包会话摘要报告\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"会话ID: {session.session_id}\n")
                    f.write(f"目标: {session.target}\n")
                    f.write(f"开始时间: {session.start_time}\n")
                    f.write(f"结束时间: {session.end_time}\n")
                    if session.end_time:
                        duration = (session.end_time - session.start_time).total_seconds()
                        f.write(f"实际时长: {duration:.2f}秒\n")
                    f.write(f"过滤条件: {session.filter_expr}\n")
                    f.write(f"抓取数据包数: {len(session.packets)}\n\n")
                    
                    # 分析结果
                    analysis = self._analyze_packets(session.packets)
                    f.write(f"分析结果:\n")
                    f.write(f"-" * 30 + "\n")
                    f.write(f"协议分布: {analysis.get('protocol_stats', {})}\n")
                    f.write(f"目标服务器: {analysis.get('destination_servers', [])}\n")
                    f.write(f"网络问题: {analysis.get('network_issues', [])}\n")
                    f.write(f"连接统计: {analysis.get('connection_stats', {})}\n\n")
                    
                    # 数据包详情
                    f.write(f"数据包详情:\n")
                    f.write(f"-" * 30 + "\n")
                    for i, packet in enumerate(session.packets[:50], 1):  # 限制显示前50个
                        f.write(f"{i:3d}. {packet.timestamp} | {packet.protocol} | "
                               f"{packet.src_ip}:{packet.src_port or 'N/A'} -> "
                               f"{packet.dst_ip}:{packet.dst_port or 'N/A'} | "
                               f"{packet.summary}\n")
                    
                    if len(session.packets) > 50:
                        f.write(f"... 省略其余 {len(session.packets) - 50} 个数据包\n")
                
                saved_files.append(str(summary_file))
                logger.info(f"保存摘要文件: {summary_file}")
            
            # 3. 保存原始数据包信息
            if "raw" in self.save_formats:
                raw_file = self.save_directory / f"{file_prefix}_raw.txt"
                
                with open(raw_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 原始抓包数据\n")
                    f.write(f"# Session: {session.session_id}\n")
                    f.write(f"# Target: {session.target}\n")
                    f.write(f"# Filter: {session.filter_expr}\n")
                    f.write(f"# Start: {session.start_time}\n")
                    f.write(f"# End: {session.end_time}\n\n")
                    
                    for packet in session.packets:
                        f.write(f"{packet.timestamp} | {packet.protocol} | "
                               f"{packet.src_ip}:{packet.src_port or ''} > "
                               f"{packet.dst_ip}:{packet.dst_port or ''} | "
                               f"Size: {packet.size} | Flags: {','.join(packet.flags)} | "
                               f"{packet.summary}\n")
                
                saved_files.append(str(raw_file))
                logger.info(f"保存原始数据: {raw_file}")
            
            session.saved_files.extend(saved_files)
            return saved_files
            
        except Exception as e:
            logger.error(f"保存抓包数据失败: {e}")
            return saved_files
    
    def _build_capture_filter(self, target: str, capture_type: str) -> str:
        """构建tcpdump过滤表达式（优化版）"""
        
        if capture_type == "domain":
            # 抓取指定域名的流量（更宽松的条件）
            return f"host {target} or (tcp and (port 80 or port 443)) or icmp or (udp and port 53)"
        
        elif capture_type == "port":
            # 抓取指定端口的流量
            return f"port {target} or icmp"
        
        elif capture_type == "process":
            # 抓取常见应用流量
            return "tcp or udp or icmp"
        
        elif capture_type == "web":
            # 抓取Web流量（更全面）
            return "port 80 or port 443 or port 8080 or port 8443 or icmp or (udp and port 53)"
        
        elif capture_type == "diagnostic":
            # 专门用于网络诊断的过滤器
            return "icmp or (udp and port 53) or (tcp and (port 80 or port 443))"
        
        else:
            # 默认抓取常见流量（更宽松）
            return "tcp or udp or icmp"
    
    def _parse_tcpdump_line(self, line: str) -> Optional[PacketSummary]:
        """解析tcpdump输出行"""
        try:
            # tcpdump输出格式: timestamp src > dst: protocol info
            parts = line.strip().split()
            if len(parts) < 5:
                return None
            
            timestamp = parts[0]
            
            # 解析源和目标
            src_dst = None
            for i, part in enumerate(parts):
                if '>' in part:
                    src_dst = parts[i-1:i+2]  # 前一个词、箭头、后一个词
                    break
            
            if not src_dst or len(src_dst) != 3:
                return None
            
            src = src_dst[0]
            dst = src_dst[2].rstrip(':')
            
            # 解析IP和端口
            src_ip, src_port = self._parse_address(src)
            dst_ip, dst_port = self._parse_address(dst)
            
            # 确定协议和类型
            protocol = "Unknown"
            packet_type = "Data"
            flags = []
            
            line_lower = line.lower()
            if "tcp" in line_lower:
                protocol = "TCP"
                if "[s]" in line or "syn" in line_lower:
                    packet_type = "TCP_SYN"
                    flags.append("SYN")
                elif "[f]" in line or "fin" in line_lower:
                    packet_type = "TCP_FIN"
                    flags.append("FIN")
                elif "[r]" in line or "rst" in line_lower:
                    packet_type = "TCP_RST"
                    flags.append("RST")
                elif "http" in line_lower or "get" in line_lower or "post" in line_lower:
                    packet_type = "HTTP_REQUEST"
                    flags.append("HTTP")
            elif "udp" in line_lower:
                protocol = "UDP"
                if "domain" in line_lower or ":53" in line:
                    packet_type = "DNS_QUERY"
                    flags.append("DNS")
            elif "icmp" in line_lower:
                protocol = "ICMP"
                packet_type = "ICMP_MESSAGE"
                flags.append("ICMP")
            
            # 提取包大小
            size = 0
            size_match = re.search(r'length (\d+)', line)
            if size_match:
                size = int(size_match.group(1))
            
            return PacketSummary(
                timestamp=timestamp,
                protocol=protocol,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                packet_type=packet_type,
                summary=line.strip(),
                flags=flags,
                size=size
            )
            
        except Exception as e:
            logger.error(f"解析tcpdump行失败: {e}, 行内容: {line}")
            return None
    
    def _parse_address(self, addr: str) -> tuple[str, Optional[int]]:
        """解析地址，提取IP和端口"""
        try:
            if '.' in addr and addr.count('.') >= 3:
                # IPv4地址
                parts = addr.rsplit('.', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    # 最后一部分是端口
                    ip_parts = parts[0].rsplit('.', 3)
                    if len(ip_parts) == 4:
                        ip = '.'.join(ip_parts)
                        port = int(parts[1])
                        return ip, port
                # 没有端口的情况
                return addr, None
            else:
                # 其他格式
                return addr, None
        except Exception:
            return addr, None
    
    def _analyze_packets(self, packets: List[PacketSummary]) -> Dict[str, Any]:
        """分析抓取的数据包，提取关键信息"""
        analysis = {
            "summary": {
                "total_packets": len(packets),
                "protocols": {},
                "packet_types": {},
                "top_sources": {},
                "top_destinations": {},
                "time_range": {}
            },
            "connections": [],
            "issues": [],
            "recommendations": []
        }
        
        if not packets:
            return analysis
        
        # 统计协议分布
        for packet in packets:
            protocol = packet.protocol
            analysis["summary"]["protocols"][protocol] = \
                analysis["summary"]["protocols"].get(protocol, 0) + 1
            
            packet_type = packet.packet_type
            analysis["summary"]["packet_types"][packet_type] = \
                analysis["summary"]["packet_types"].get(packet_type, 0) + 1
            
            # 统计源和目标
            analysis["summary"]["top_sources"][packet.src_ip] = \
                analysis["summary"]["top_sources"].get(packet.src_ip, 0) + 1
            analysis["summary"]["top_destinations"][packet.dst_ip] = \
                analysis["summary"]["top_destinations"].get(packet.dst_ip, 0) + 1
        
        # 时间范围
        if packets:
            analysis["summary"]["time_range"] = {
                "start": packets[0].timestamp,
                "end": packets[-1].timestamp,
                "duration_seconds": len(packets) * 0.1  # 估算
            }
        
        # 连接分析
        connections = {}
        for packet in packets:
            if packet.protocol == "TCP":
                conn_key = f"{packet.src_ip}:{packet.src_port}-{packet.dst_ip}:{packet.dst_port}"
                if conn_key not in connections:
                    connections[conn_key] = {
                        "src_ip": packet.src_ip,
                        "dst_ip": packet.dst_ip,
                        "src_port": packet.src_port,
                        "dst_port": packet.dst_port,
                        "states": [],
                        "packet_count": 0,
                        "flags": set()
                    }
                
                connections[conn_key]["packet_count"] += 1
                connections[conn_key]["flags"].update(packet.flags)
                
                if packet.packet_type == "TCP_SYN":
                    connections[conn_key]["states"].append("SYN")
                elif packet.packet_type == "TCP_FIN":
                    connections[conn_key]["states"].append("FIN")
                elif packet.packet_type == "TCP_RST":
                    connections[conn_key]["states"].append("RST")
        
        # 转换连接信息
        for conn_key, conn_info in connections.items():
            analysis["connections"].append({
                "connection": conn_key,
                "src": f"{conn_info['src_ip']}:{conn_info['src_port']}",
                "dst": f"{conn_info['dst_ip']}:{conn_info['dst_port']}",
                "packet_count": conn_info["packet_count"],
                "flags": list(conn_info["flags"]),
                "states": conn_info["states"]
            })
        
        # 问题检测
        issues = []
        
        # 检测TCP重置
        rst_count = analysis["summary"]["packet_types"].get("TCP_RST", 0)
        if rst_count > 0:
            issues.append({
                "type": "connection_reset",
                "severity": "warning",
                "description": f"检测到{rst_count}个TCP连接重置",
                "recommendation": "可能存在连接问题或服务器拒绝连接"
            })
        
        # 检测DNS查询
        dns_count = analysis["summary"]["packet_types"].get("DNS_QUERY", 0)
        if dns_count == 0 and len(packets) > 10:
            issues.append({
                "type": "no_dns",
                "severity": "info",
                "description": "未检测到DNS查询",
                "recommendation": "可能使用了IP直连或DNS查询在其他时间段"
            })
        
        # 检测HTTP流量
        http_count = analysis["summary"]["packet_types"].get("HTTP_REQUEST", 0)
        if http_count > 0:
            issues.append({
                "type": "unencrypted_http",
                "severity": "info",
                "description": f"检测到{http_count}个HTTP请求",
                "recommendation": "建议使用HTTPS加密通信"
            })
        
        analysis["issues"] = issues
        
        return analysis

    async def start_capture(
        self,
        target: str,
        capture_type: str = "domain",
        duration: int = 30,
        interface: Optional[str] = None
    ) -> Dict[str, Any]:
        """开始抓包"""
        try:
            # 检查权限
            if not self._check_permissions():
                return {
                    "success": False,
                    "error": "需要管理员权限进行抓包。请使用sudo运行或确保有网络监控权限。",
                    "session_id": None
                }
            
            # 生成新的会话ID（确保唯一性）
            import time
            session_id = f"capture_{int(time.time() * 1000)}"  # 使用毫秒时间戳确保唯一性
            
            # 清理相同目标的旧会话（避免冲突）
            old_sessions_to_remove = []
            for sid, session in self.sessions.items():
                if session.target == target and session.is_running:
                    logger.info(f"发现相同目标的旧会话 {sid}，准备停止")
                    try:
                        if session.process and session.process.poll() is None:
                            session.process.terminate()
                            try:
                                session.process.communicate(timeout=2)
                            except subprocess.TimeoutExpired:
                                session.process.kill()
                        session.is_running = False
                        session.end_time = datetime.now()
                    except Exception as e:
                        logger.warning(f"停止旧会话 {sid} 失败: {e}")
            
            # 获取可用接口
            available_interfaces = self._get_available_interfaces()
            if not interface:
                interface = available_interfaces[0] if available_interfaces else "any"
            
            # 构建过滤器
            filter_expr = self._build_capture_filter(target, capture_type)
            
            # 构建tcpdump命令
            cmd = [
                "tcpdump",
                "-i", interface,
                "-n",  # 不解析主机名
                "-t",  # 不显示时间戳
                "-v",  # 详细输出
                "-c", str(duration * 10),  # 限制包数量
                filter_expr
            ]
            
            logger.info(f"启动新抓包会话: {session_id}")
            logger.info(f"抓包命令: {' '.join(cmd)}")
            logger.info(f"目标: {target}, 模式: {capture_type}, 时长: {duration}秒")
            
            # 启动tcpdump进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 创建会话
            session = CaptureSession(
                session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                target=target,
                filter_expr=filter_expr,
                packets=[],
                connections={},
                is_running=True,
                process=process
            )
            
            # 添加duration属性
            session.duration = duration
            
            self.sessions[session_id] = session
            
            logger.info(f"✅ 抓包会话 {session_id} 启动成功")
            
            return {
                "success": True,
                "session_id": session_id,
                "target": target,
                "mode": capture_type,
                "duration": duration,
                "interface": interface,
                "filter": filter_expr,
                "message": f"开始抓包，目标: {target}，接口: {interface}，会话: {session_id}"
            }
            
        except Exception as e:
            logger.error(f"启动抓包失败: {e}")
            return {
                "success": False,
                "error": f"启动抓包失败: {str(e)}",
                "session_id": None
            }
    
    async def stop_capture(self, session_id: str) -> Dict[str, Any]:
        """停止抓包并返回分析结果"""
        try:
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"会话 {session_id} 不存在"
                }
            
            session = self.sessions[session_id]
            
            if not session.is_running:
                return {
                    "success": False,
                    "error": f"会话 {session_id} 已经停止"
                }
            
            # 停止进程
            if session.process and session.process.poll() is None:
                session.process.terminate()
                
                # 等待进程结束并读取输出
                try:
                    stdout, stderr = session.process.communicate(timeout=5)
                    
                    # 解析输出
                    for line in stdout.split('\n'):
                        if line.strip():
                            packet = self._parse_tcpdump_line(line)
                            if packet:
                                session.packets.append(packet)
                                
                except subprocess.TimeoutExpired:
                    session.process.kill()
                    logger.warning(f"强制终止抓包进程 {session_id}")
            
            # 更新会话状态
            session.is_running = False
            session.end_time = datetime.now()
            
            # 分析数据包
            analysis = self._analyze_packets(session.packets)
            
            # 自动保存抓包数据
            saved_files = []
            if self.auto_save and session.packets:
                saved_files = self._save_capture_data(session)
                logger.info(f"会话 {session_id} 自动保存完成，文件数: {len(saved_files)}")
            
            # 清理会话（可选，保留用于后续查询）
            # del self.sessions[session_id]
            
            return {
                "success": True,
                "session_id": session_id,
                "packets_captured": len(session.packets),
                "analysis": analysis,
                "duration": (session.end_time - session.start_time).total_seconds(),
                "saved_files": saved_files
            }
            
        except Exception as e:
            logger.error(f"停止抓包失败: {e}")
            return {
                "success": False,
                "error": f"停止抓包失败: {str(e)}"
            }
    
    def _read_realtime_packets(self, session: CaptureSession) -> int:
        """实时读取数据包"""
        if not session.process or session.process.poll() is not None:
            return len(session.packets)
        
        try:
            # 非阻塞读取stdout（tcpdump的输出）
            import select
            
            # 只在Linux/Unix系统上使用fcntl
            if platform.system() == 'Linux':
                import fcntl
                import os
                
                # 设置非阻塞模式
                if session.process.stdout:
                    fd = session.process.stdout.fileno()
                    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # 尝试读取新数据
            try:
                if session.process.stdout:
                    ready, _, _ = select.select([session.process.stdout], [], [], 0)
                    if ready:
                        new_data = session.process.stdout.read()
                        if new_data:
                            lines = new_data.split('\n')
                            for line in lines:
                                if line.strip():
                                    packet = self._parse_tcpdump_line(line.strip())
                                    if packet:
                                        session.packets.append(packet)
                                        logger.debug(f"解析数据包: {packet.summary}")
            except (BlockingIOError, OSError):
                pass
                    
        except Exception as e:
            logger.warning(f"读取实时数据包失败: {e}")
        
        return len(session.packets)

    async def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取抓包会话状态"""
        try:
            # 如果没有指定session_id，查找最新的活跃会话
            if not session_id:
                # 首先查找正在运行的会话
                active_sessions = [s for s in self.sessions.values() if s.is_running]
                
                if active_sessions:
                    # 返回最新的活跃会话
                    session = max(active_sessions, key=lambda s: s.start_time)
                    session_id = session.session_id
                    logger.info(f"找到活跃会话: {session_id}")
                else:
                    # 没有活跃会话，查找最近的会话
                    if not self.sessions:
                        return {
                            "success": False,
                            "error": "没有找到任何抓包会话"
                        }
                    
                    # 查找最近2分钟内的会话，避免返回过旧的会话
                    recent_sessions = []
                    current_time = datetime.now()
                    for s in self.sessions.values():
                        time_diff = (current_time - s.start_time).total_seconds()
                        if time_diff <= 120:  # 2分钟内
                            recent_sessions.append(s)
                    
                    if recent_sessions:
                        # 返回最新的近期会话
                        session = max(recent_sessions, key=lambda s: s.start_time)
                        session_id = session.session_id
                        logger.info(f"找到近期会话: {session_id} (开始时间: {session.start_time})")
                    else:
                        # 所有会话都太旧了
                        return {
                            "success": False,
                            "error": "没有找到近期的抓包会话（2分钟内）"
                        }
            else:
                if session_id not in self.sessions:
                    return {
                        "success": False,
                        "error": f"会话 {session_id} 不存在"
                    }
                session = self.sessions[session_id]
                logger.info(f"查询指定会话状态: {session_id}")
            
            elapsed_time = (datetime.now() - session.start_time).total_seconds()
            
            # 获取预设时长
            estimated_duration = 30  # 默认30秒
            if hasattr(session, 'duration'):
                estimated_duration = session.duration
            
            # 检查是否超时
            is_timeout = elapsed_time >= estimated_duration
            
            # 检查进程状态
            is_capturing = session.is_running
            process_running = False
            
            if session.process:
                process_running = session.process.poll() is None
                
                # 如果超时或进程已结束，停止会话
                if (is_timeout or not process_running) and session.is_running:
                    logger.info(f"会话 {session_id} {'超时' if is_timeout else '进程结束'}，自动停止")
                    
                    # 读取剩余输出
                    try:
                        if process_running:
                            session.process.terminate()
                            stdout, stderr = session.process.communicate(timeout=3)
                        else:
                            stdout, stderr = session.process.communicate()
                        
                        # 解析最终输出（tcpdump输出在stdout）
                        if stdout:
                            for line in stdout.split('\n'):
                                if line.strip():
                                    packet = self._parse_tcpdump_line(line.strip())
                                    if packet:
                                        session.packets.append(packet)
                                        
                        logger.info(f"会话 {session_id} 最终捕获 {len(session.packets)} 个数据包")
                                        
                    except subprocess.TimeoutExpired:
                        session.process.kill()
                        logger.warning(f"强制终止会话 {session_id}")
                    except Exception as e:
                        logger.error(f"读取最终输出失败: {e}")
                    
                    # 更新会话状态
                    session.is_running = False
                    session.end_time = datetime.now()
                    is_capturing = False
                    
                    # 自动保存抓包数据
                    if self.auto_save and session.packets:
                        saved_files = self._save_capture_data(session)
                        logger.info(f"会话 {session_id} 自动结束并保存完成，文件数: {len(saved_files)}")
                    
                elif process_running and session.is_running:
                    # 实时读取数据包
                    current_packets = self._read_realtime_packets(session)
            
            # 获取当前包数量
            current_packets = len(session.packets)
            remaining_time = max(0, estimated_duration - elapsed_time) if is_capturing else 0
            
            logger.info(f"会话 {session_id} 状态: is_capturing={is_capturing}, packets={current_packets}, elapsed={int(elapsed_time)}s, remaining={int(remaining_time)}s")
            
            return {
                "success": True,
                "session_id": session_id,
                "status": "running" if is_capturing else "completed",
                "is_capturing": is_capturing,
                "target": session.target,
                "current_packet_count": current_packets,
                "packets_captured": current_packets,
                "start_time": session.start_time.isoformat(),
                "elapsed_time": int(elapsed_time),
                "duration": int(elapsed_time),
                "remaining_time": int(remaining_time),
                "filter": session.filter_expr,
                "auto_stopped": is_timeout if not is_capturing else False,
                "saved_files": session.saved_files if session.saved_files else []
            }
            
        except Exception as e:
            logger.error(f"获取会话状态失败: {e}")
            return {
                "success": False,
                "error": f"获取会话状态失败: {str(e)}"
            }
    
    async def list_interfaces(self) -> Dict[str, Any]:
        """列出可用的网络接口"""
        try:
            interfaces = self._get_available_interfaces()
            return {
                "success": True,
                "interfaces": interfaces,
                "default": interfaces[0] if interfaces else None
            }
        except Exception as e:
            logger.error(f"获取网络接口失败: {e}")
            return {
                "success": False,
                "error": f"获取网络接口失败: {str(e)}",
                "interfaces": []
            }
    
    async def save_capture_data_manual(self, session_id: str, formats: List[str] = None) -> Dict[str, Any]:
        """手动保存抓包数据"""
        try:
            if session_id not in self.sessions:
                return {
                    "success": False,
                    "error": f"会话 {session_id} 不存在"
                }
            
            session = self.sessions[session_id]
            
            if not session.packets:
                return {
                    "success": False,
                    "error": f"会话 {session_id} 没有抓取到任何数据包"
                }
            
            # 临时设置保存格式
            original_formats = self.save_formats
            if formats:
                self.save_formats = formats
            
            # 保存数据
            saved_files = self._save_capture_data(session)
            
            # 恢复原始设置
            self.save_formats = original_formats
            
            return {
                "success": True,
                "session_id": session_id,
                "saved_files": saved_files,
                "formats_used": formats or self.save_formats,
                "packets_saved": len(session.packets),
                "message": f"已保存 {len(saved_files)} 个文件"
            }
            
        except Exception as e:
            logger.error(f"手动保存抓包数据失败: {e}")
            return {
                "success": False,
                "error": f"手动保存抓包数据失败: {str(e)}"
            }
    
    async def configure_auto_save_settings(self, auto_save: bool = None, save_formats: List[str] = None, save_directory: str = None) -> Dict[str, Any]:
        """配置自动保存设置"""
        try:
            old_settings = {
                "auto_save": self.auto_save,
                "save_formats": self.save_formats.copy(),
                "save_directory": str(self.save_directory)
            }
            
            # 更新设置
            if auto_save is not None:
                self.auto_save = auto_save
                logger.info(f"自动保存设置已{'启用' if auto_save else '禁用'}")
            
            if save_formats is not None:
                # 验证格式
                valid_formats = ["json", "summary", "raw"]
                invalid_formats = [f for f in save_formats if f not in valid_formats]
                if invalid_formats:
                    return {
                        "success": False,
                        "error": f"无效的保存格式: {invalid_formats}，有效格式: {valid_formats}"
                    }
                self.save_formats = save_formats
                logger.info(f"保存格式已更新: {save_formats}")
            
            if save_directory is not None:
                new_dir = Path(save_directory)
                try:
                    new_dir.mkdir(parents=True, exist_ok=True)
                    self.save_directory = new_dir
                    logger.info(f"保存目录已更新: {new_dir}")
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"无法创建保存目录 {new_dir}: {str(e)}"
                    }
            
            new_settings = {
                "auto_save": self.auto_save,
                "save_formats": self.save_formats.copy(),
                "save_directory": str(self.save_directory)
            }
            
            return {
                "success": True,
                "message": "自动保存设置已更新",
                "old_settings": old_settings,
                "new_settings": new_settings
            }
            
        except Exception as e:
            logger.error(f"配置自动保存设置失败: {e}")
            return {
                "success": False,
                "error": f"配置自动保存设置失败: {str(e)}"
            }

# MCP服务器实现
class PacketCaptureMCPServer:
    """抓包分析MCP服务器"""
    
    def __init__(self):
        self.capture_server = PacketCaptureServer()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "start_packet_capture",
                                "description": "开始智能抓包分析，专注于网络问题诊断",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "target": {
                                            "type": "string",
                                            "description": "抓包目标（域名、IP、端口号等）"
                                        },
                                        "capture_type": {
                                            "type": "string",
                                            "description": "抓包类型",
                                            "enum": ["domain", "port", "process", "web"],
                                            "default": "domain"
                                        },
                                        "duration": {
                                            "type": "integer",
                                            "description": "抓包时长（秒）",
                                            "default": 30
                                        },
                                        "interface": {
                                            "type": "string",
                                            "description": "网络接口（可选）"
                                        }
                                    },
                                    "required": ["target"]
                                }
                            },
                            {
                                "name": "stop_packet_capture",
                                "description": "停止抓包并获取分析结果",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "抓包会话ID"
                                        }
                                    },
                                    "required": ["session_id"]
                                }
                            },
                            {
                                "name": "get_capture_status",
                                "description": "获取抓包会话状态（如果不指定session_id，返回最新会话状态）",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string",
                                            "description": "抓包会话ID（可选，不指定时返回最新会话）"
                                        }
                                    },
                                    "required": []
                                }
                            },
                            {
                                "name": "list_network_interfaces",
                                "description": "列出可用的网络接口",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            },
                            {
                                "name": "save_capture_data",
                                "description": "手动保存抓包数据到本地磁盘",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {
                                            "type": "string", 
                                            "description": "抓包会话ID"
                                        },
                                        "formats": {
                                            "type": "array",
                                            "items": {"type": "string", "enum": ["json", "summary", "raw"]},
                                            "description": "保存格式（json: 详细JSON数据, summary: 可读摘要, raw: 原始数据包）",
                                            "default": ["json", "summary", "raw"]
                                        }
                                    },
                                    "required": ["session_id"]
                                }
                            },
                            {
                                "name": "configure_auto_save",
                                "description": "配置自动保存设置",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "auto_save": {
                                            "type": "boolean",
                                            "description": "是否启用自动保存",
                                            "default": true
                                        },
                                        "save_formats": {
                                            "type": "array", 
                                            "items": {"type": "string", "enum": ["json", "summary", "raw"]},
                                            "description": "默认保存格式",
                                            "default": ["json", "summary", "raw"]
                                        },
                                        "save_directory": {
                                            "type": "string",
                                            "description": "保存目录路径（可选）"
                                        }
                                    },
                                    "required": []
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "start_packet_capture":
                    result = await self.capture_server.start_capture(
                        target=arguments.get("target"),
                        capture_type=arguments.get("capture_type", "domain"),
                        duration=arguments.get("duration", 30),
                        interface=arguments.get("interface")
                    )
                elif tool_name == "stop_packet_capture":
                    result = await self.capture_server.stop_capture(
                        session_id=arguments.get("session_id")
                    )
                elif tool_name == "get_capture_status":
                    session_id = arguments.get("session_id")
                    result = await self.capture_server.get_session_status(
                        session_id=session_id if session_id else None
                    )
                elif tool_name == "list_network_interfaces":
                    result = await self.capture_server.list_interfaces()
                elif tool_name == "save_capture_data":
                    result = await self.capture_server.save_capture_data_manual(
                        session_id=arguments.get("session_id"),
                        formats=arguments.get("formats")
                    )
                elif tool_name == "configure_auto_save":
                    result = await self.capture_server.configure_auto_save_settings(
                        auto_save=arguments.get("auto_save"),
                        save_formats=arguments.get("save_formats"),
                        save_directory=arguments.get("save_directory")
                    )
                else:
                    result = {
                        "success": False,
                        "error": f"未知工具: {tool_name}"
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知方法: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"内部错误: {str(e)}"
                }
            }
    
    async def run(self):
        """运行MCP服务器"""
        logger.info("抓包分析MCP服务器启动")
        
        try:
            while True:
                # 读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                except Exception as e:
                    logger.error(f"处理请求异常: {e}")
                    
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在关闭...")
        except Exception as e:
            logger.error(f"服务器运行错误: {e}")
        finally:
            # 清理资源
            for session in self.capture_server.sessions.values():
                if session.process and session.process.poll() is None:
                    session.process.terminate()
            logger.info("抓包分析MCP服务器已关闭")

async def main():
    """主函数"""
    server = PacketCaptureMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 