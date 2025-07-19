"""
互联互通分析器
专门用于分析跨运营商网络访问质量
"""

import subprocess
import logging
import ipaddress
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ISPInfo:
    """ISP信息"""
    name: str
    type: str  # 'mobile', 'unicom', 'telecom', 'other'
    region: str
    confidence: float

@dataclass
class InterconnectionQuality:
    """互联互通质量"""
    local_isp: str
    remote_isp: str
    avg_latency: float
    packet_loss_rate: float
    quality_level: str
    sample_count: int

class InterconnectionAnalyzer:
    """互联互通分析器"""
    
    def __init__(self):
        # ISP IP段数据库（简化版）
        self.ISP_IP_RANGES = {
            'china_mobile': [
                '111.0.0.0/10', '120.0.0.0/6', '183.0.0.0/8',
                '39.128.0.0/10', '223.0.0.0/11', '117.128.0.0/10',
                '112.0.0.0/9', '124.128.0.0/10'
            ],
            'china_unicom': [
                '123.0.0.0/8', '125.0.0.0/8', '140.0.0.0/8',
                '221.0.0.0/11', '222.0.0.0/12', '61.135.0.0/16'
            ],
            'china_telecom': [
                '116.0.0.0/8', '117.0.0.0/9', '118.0.0.0/8',
                '119.0.0.0/8', '124.0.0.0/9', '180.76.0.0/16'
            ]
        }
        
        # 互联互通质量评估标准
        self.QUALITY_THRESHOLDS = {
            'excellent': {'latency': 50, 'loss': 0.1},
            'good': {'latency': 100, 'loss': 0.5},
            'fair': {'latency': 200, 'loss': 1.0},
            'poor': {'latency': float('inf'), 'loss': float('inf')}
        }

    def analyze_interconnection(self, tshark_cmd: str, pcap_file: str) -> Dict:
        """分析互联互通质量"""
        try:
            logger.info("开始互联互通分析")
            
            # 1. 获取本地ISP信息
            local_isp = self._detect_local_isp()
            
            # 2. 分析网络连接
            connections = self._analyze_network_connections(tshark_cmd, pcap_file)
            
            # 3. 识别远程服务器ISP
            remote_servers = self._identify_remote_servers(connections)
            
            # 4. 分析跨ISP连接质量
            interconnection_quality = self._analyze_cross_isp_quality(connections, local_isp, remote_servers)
            
            # 5. 生成互联互通报告
            report = self._generate_interconnection_report(local_isp, interconnection_quality)
            
            return {
                'local_isp': local_isp,
                'remote_servers': remote_servers,
                'interconnection_quality': interconnection_quality,
                'report': report,
                'analysis_summary': {
                    'total_connections': len(connections),
                    'cross_isp_connections': len([q for q in interconnection_quality if q.local_isp != q.remote_isp]),
                    'avg_cross_isp_latency': self._calculate_avg_cross_isp_latency(interconnection_quality),
                    'quality_distribution': self._calculate_quality_distribution(interconnection_quality)
                }
            }
            
        except Exception as e:
            logger.error(f"互联互通分析失败: {str(e)}")
            return {
                'error': str(e),
                'local_isp': 'unknown',
                'interconnection_quality': []
            }

    def _detect_local_isp(self) -> str:
        """检测本地ISP"""
        try:
            # 通过本地网关IP段推测（简化方法）
            return self._detect_isp_by_gateway()

        except Exception as e:
            logger.error(f"本地ISP检测失败: {str(e)}")
            return 'unknown'

    def _detect_isp_by_gateway(self) -> str:
        """通过网关IP段检测ISP"""
        try:
            # 获取默认网关
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        gateway_ip = line.split(':')[1].strip()
                        return self._resolve_isp_by_ip(gateway_ip)[0]
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"网关ISP检测失败: {str(e)}")
            return 'unknown'

    def _analyze_network_connections(self, tshark_cmd: str, pcap_file: str) -> List[Dict]:
        """分析网络连接"""
        connections = []
        
        try:
            # 分析TCP连接
            result = subprocess.run([
                tshark_cmd, '-r', pcap_file, '-T', 'fields',
                '-e', 'ip.src',
                '-e', 'ip.dst',
                '-e', 'tcp.srcport',
                '-e', 'tcp.dstport',
                '-e', 'tcp.analysis.ack_rtt',
                '-e', 'tcp.analysis.initial_rtt',
                '-e', 'frame.time_relative',
                '-e', 'tcp.flags',
                '-Y', 'tcp'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t')
                        if len(parts) >= 8:
                            connection = {
                                'src_ip': parts[0],
                                'dst_ip': parts[1],
                                'src_port': int(parts[2]) if parts[2].isdigit() else 0,
                                'dst_port': int(parts[3]) if parts[3].isdigit() else 0,
                                'ack_rtt': float(parts[4]) * 1000 if parts[4] and parts[4] != '' else 0,  # 转换为ms
                                'initial_rtt': float(parts[5]) * 1000 if parts[5] and parts[5] != '' else 0,
                                'time': float(parts[6]) if parts[6] else 0,
                                'flags': parts[7] if len(parts) > 7 else ''
                            }
                            connections.append(connection)
            
        except Exception as e:
            logger.error(f"网络连接分析失败: {str(e)}")
            
        return connections

    def _identify_remote_servers(self, connections: List[Dict]) -> List[Dict]:
        """识别远程服务器"""
        servers = {}
        
        for conn in connections:
            # 通常目标IP是服务器
            server_ip = conn['dst_ip']
            
            if server_ip not in servers:
                isp_name, isp_type = self._resolve_isp_by_ip(server_ip)
                servers[server_ip] = {
                    'ip': server_ip,
                    'isp': isp_name,
                    'isp_type': isp_type,
                    'connections': [],
                    'avg_latency': 0,
                    'packet_loss_rate': 0
                }
            
            servers[server_ip]['connections'].append(conn)
        
        # 计算每个服务器的性能指标
        for server_ip, server_info in servers.items():
            connections = server_info['connections']
            latencies = [c['ack_rtt'] for c in connections if c['ack_rtt'] > 0]
            
            server_info['avg_latency'] = sum(latencies) / len(latencies) if latencies else 0
            server_info['connection_count'] = len(connections)
            # 简化的丢包率计算
            server_info['packet_loss_rate'] = self._estimate_packet_loss(connections)
        
        return list(servers.values())

    def _resolve_isp_by_ip(self, ip: str) -> Tuple[str, str]:
        """根据IP解析ISP"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # 检查各ISP的IP段
            for isp_type, ip_ranges in self.ISP_IP_RANGES.items():
                for ip_range in ip_ranges:
                    try:
                        if ip_obj in ipaddress.ip_network(ip_range):
                            isp_names = {
                                'china_mobile': '中国移动',
                                'china_unicom': '中国联通', 
                                'china_telecom': '中国电信'
                            }
                            return isp_names.get(isp_type, isp_type), isp_type
                    except ValueError:
                        continue
            
            # 如果不在已知IP段，尝试简单的前缀匹配
            if ip.startswith(('111.', '120.', '183.')):
                return '中国移动', 'china_mobile'
            elif ip.startswith(('123.', '125.', '140.')):
                return '中国联通', 'china_unicom'
            elif ip.startswith(('116.', '117.', '118.')):
                return '中国电信', 'china_telecom'
            else:
                return '其他ISP', 'other'
                
        except Exception as e:
            logger.error(f"IP ISP解析失败: {str(e)}")
            return '未知ISP', 'unknown'

    def _analyze_cross_isp_quality(self, connections: List[Dict], local_isp: str, 
                                 remote_servers: List[Dict]) -> List[InterconnectionQuality]:
        """分析跨ISP连接质量"""
        quality_results = []
        
        # 按ISP分组统计
        isp_stats = defaultdict(list)
        
        for server in remote_servers:
            if server['avg_latency'] > 0:  # 只统计有延迟数据的连接
                isp_stats[server['isp_type']].append({
                    'latency': server['avg_latency'],
                    'packet_loss': server['packet_loss_rate'],
                    'connection_count': server['connection_count']
                })
        
        # 计算每个ISP的互联质量
        for remote_isp_type, stats in isp_stats.items():
            if stats:
                avg_latency = sum(s['latency'] for s in stats) / len(stats)
                avg_packet_loss = sum(s['packet_loss'] for s in stats) / len(stats)
                sample_count = sum(s['connection_count'] for s in stats)
                
                quality_level = self._evaluate_quality_level(avg_latency, avg_packet_loss)
                
                remote_isp_name = {
                    'china_mobile': '中国移动',
                    'china_unicom': '中国联通',
                    'china_telecom': '中国电信',
                    'other': '其他ISP'
                }.get(remote_isp_type, remote_isp_type)
                
                local_isp_name = {
                    'china_mobile': '中国移动',
                    'china_unicom': '中国联通', 
                    'china_telecom': '中国电信'
                }.get(local_isp, local_isp)
                
                quality_results.append(InterconnectionQuality(
                    local_isp=local_isp_name,
                    remote_isp=remote_isp_name,
                    avg_latency=avg_latency,
                    packet_loss_rate=avg_packet_loss,
                    quality_level=quality_level,
                    sample_count=sample_count
                ))
        
        return quality_results

    def _evaluate_quality_level(self, latency: float, packet_loss: float) -> str:
        """评估质量等级"""
        for level, thresholds in self.QUALITY_THRESHOLDS.items():
            if latency <= thresholds['latency'] and packet_loss <= thresholds['loss']:
                return level
        return 'poor'

    def _estimate_packet_loss(self, connections: List[Dict]) -> float:
        """估算丢包率（简化实现）"""
        # 这里应该分析重传、超时等指标
        # 暂时返回基于连接数的估算值
        if len(connections) < 10:
            return 0.5  # 连接数少，可能有问题
        else:
            return 0.1  # 正常情况

    def _calculate_avg_cross_isp_latency(self, quality_results: List[InterconnectionQuality]) -> float:
        """计算跨ISP平均延迟"""
        cross_isp_results = [q for q in quality_results if q.local_isp != q.remote_isp]
        if cross_isp_results:
            return sum(q.avg_latency for q in cross_isp_results) / len(cross_isp_results)
        return 0

    def _calculate_quality_distribution(self, quality_results: List[InterconnectionQuality]) -> Dict:
        """计算质量分布"""
        distribution = defaultdict(int)
        for q in quality_results:
            distribution[q.quality_level] += 1
        return dict(distribution)

    def _generate_interconnection_report(self, local_isp: str, 
                                       quality_results: List[InterconnectionQuality]) -> Dict:
        """生成互联互通报告"""
        if not quality_results:
            return {
                'summary': '未检测到跨运营商连接',
                'recommendations': ['请确认网络连接正常', '尝试访问不同运营商的服务']
            }
        
        # 分析跨ISP连接
        cross_isp_connections = [q for q in quality_results if q.local_isp != q.remote_isp]
        same_isp_connections = [q for q in quality_results if q.local_isp == q.remote_isp]
        
        report = {
            'summary': f'检测到{len(quality_results)}个ISP连接，其中{len(cross_isp_connections)}个跨运营商连接',
            'local_isp': local_isp,
            'cross_isp_analysis': {
                'total_cross_isp': len(cross_isp_connections),
                'avg_cross_isp_latency': self._calculate_avg_cross_isp_latency(quality_results),
                'quality_summary': self._summarize_cross_isp_quality(cross_isp_connections)
            },
            'same_isp_analysis': {
                'total_same_isp': len(same_isp_connections),
                'avg_same_isp_latency': sum(q.avg_latency for q in same_isp_connections) / len(same_isp_connections) if same_isp_connections else 0
            },
            'recommendations': self._generate_interconnection_recommendations(local_isp, quality_results)
        }
        
        return report

    def _summarize_cross_isp_quality(self, cross_isp_connections: List[InterconnectionQuality]) -> Dict:
        """总结跨ISP质量"""
        if not cross_isp_connections:
            return {}
        
        quality_counts = defaultdict(int)
        isp_performance = {}
        
        for conn in cross_isp_connections:
            quality_counts[conn.quality_level] += 1
            
            if conn.remote_isp not in isp_performance:
                isp_performance[conn.remote_isp] = {
                    'latency': [],
                    'packet_loss': [],
                    'quality_levels': []
                }
            
            isp_performance[conn.remote_isp]['latency'].append(conn.avg_latency)
            isp_performance[conn.remote_isp]['packet_loss'].append(conn.packet_loss_rate)
            isp_performance[conn.remote_isp]['quality_levels'].append(conn.quality_level)
        
        # 计算各ISP的平均性能
        for isp, perf in isp_performance.items():
            perf['avg_latency'] = sum(perf['latency']) / len(perf['latency'])
            perf['avg_packet_loss'] = sum(perf['packet_loss']) / len(perf['packet_loss'])
            perf['dominant_quality'] = max(set(perf['quality_levels']), key=perf['quality_levels'].count)
        
        return {
            'quality_distribution': dict(quality_counts),
            'isp_performance': isp_performance
        }

    def _generate_interconnection_recommendations(self, local_isp: str, 
                                                quality_results: List[InterconnectionQuality]) -> List[str]:
        """生成互联互通优化建议"""
        recommendations = []
        
        cross_isp_connections = [q for q in quality_results if q.local_isp != q.remote_isp]
        poor_connections = [q for q in cross_isp_connections if q.quality_level in ['poor', 'fair']]
        
        if poor_connections:
            recommendations.extend([
                '🔄 检测到跨运营商访问质量较差，建议优先选择同运营商服务',
                '🚀 考虑使用CDN加速服务，选择就近节点',
                '📞 如问题持续，可联系运营商反馈互联质量问题'
            ])
        
        # 根据本地ISP给出具体建议
        if local_isp == 'china_mobile':
            recommendations.append('📱 当前使用中国移动网络，建议优先选择移动服务器或CDN节点')
        elif local_isp == 'china_unicom':
            recommendations.append('🔵 当前使用中国联通网络，建议优先选择联通服务器或CDN节点')
        elif local_isp == 'china_telecom':
            recommendations.append('🔴 当前使用中国电信网络，建议优先选择电信服务器或CDN节点')
        
        if len(cross_isp_connections) > len(quality_results) * 0.7:
            recommendations.append('⚡ 跨运营商访问较多，建议考虑多线BGP接入或使用网络加速服务')
        
        return recommendations
