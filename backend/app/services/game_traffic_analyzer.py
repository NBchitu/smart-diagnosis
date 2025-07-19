"""
游戏流量分析器
专门用于识别和分析游戏数据包，判断游戏服务器ISP归属
"""

import subprocess
import logging
import ipaddress
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GameTrafficPattern:
    """游戏流量模式"""
    udp_ratio: float
    avg_packet_size: float
    packet_frequency: float
    bidirectional_ratio: float
    burst_pattern_score: float

@dataclass
class GameServerInfo:
    """游戏服务器信息"""
    ip: str
    port: int
    isp: str
    is_china_mobile: bool
    latency_ms: float
    packet_loss_rate: float
    confidence_score: float

class GameTrafficAnalyzer:
    """游戏流量分析器"""
    
    def __init__(self):
        # 常见游戏端口范围
        self.GAME_PORTS = {
            'moba': [7000, 7001, 7002, 7003, 7004, 7005, 8001, 17500],  # 王者荣耀、LOL等
            'fps': [7777, 7778, 7779, 7780, 7781, 7782, 7783, 7784, 27015, 25565],  # 和平精英、CS等
            'mmorpg': list(range(8080, 8091)) + list(range(9000, 9101)),  # 网络游戏
            'battle_royale': [17502, 10012, 10013, 10014, 10015],  # 吃鸡类游戏
            'mobile_games': list(range(10000, 15001)),  # 手机游戏常用端口
        }
        
        # 中国移动IP段（部分主要段）
        self.CHINA_MOBILE_IP_RANGES = [
            '111.0.0.0/10',
            '120.0.0.0/6', 
            '183.0.0.0/8',
            '39.128.0.0/10',
            '223.0.0.0/11',
            '117.128.0.0/10',
            '112.0.0.0/9',
            '124.128.0.0/10',
        ]
        
        # 游戏流量特征阈值
        self.GAME_TRAFFIC_THRESHOLDS = {
            'min_udp_ratio': 0.6,  # UDP包占比至少60%
            'max_avg_packet_size': 800,  # 平均包大小不超过800字节
            'min_avg_packet_size': 50,   # 平均包大小至少50字节
            'min_packet_frequency': 10,  # 每秒至少10个包
            'min_bidirectional_ratio': 0.3,  # 双向流量比例至少30%
        }

    def analyze_game_traffic(self, tshark_cmd: str, pcap_file: str) -> Dict:
        """分析游戏流量"""
        try:
            logger.info("开始游戏流量分析")
            
            # 1. 识别潜在的游戏流量
            game_traffic = self._identify_game_traffic(tshark_cmd, pcap_file)
            
            # 2. 分析游戏服务器
            game_servers = self._analyze_game_servers(tshark_cmd, pcap_file, game_traffic)
            
            # 3. 评估游戏网络质量
            network_quality = self._evaluate_game_network_quality(game_servers)
            
            # 4. 生成游戏诊断报告
            diagnosis = self._generate_game_diagnosis(game_servers, network_quality)
            
            # 如果没有检测到游戏流量，返回明确的结果
            if len(game_traffic) == 0:
                return {
                    'game_traffic_detected': False,
                    'game_servers': [],
                    'network_quality': '无游戏流量',
                    'diagnosis': {
                        'summary': '未检测到游戏流量',
                        'china_mobile_analysis': {},
                        'performance_analysis': {},
                        'recommendations': ['请确认是否在游戏过程中进行抓包', '检查游戏是否正常运行']
                    },
                    'analysis_summary': {
                        'total_game_servers': 0,
                        'china_mobile_servers': 0,
                        'avg_latency': 0,
                        'avg_packet_loss': 0,
                    }
                }

            return {
                'game_traffic_detected': len(game_traffic) > 0,
                'game_servers': game_servers,
                'network_quality': network_quality,
                'diagnosis': diagnosis,
                'analysis_summary': {
                    'total_game_servers': len(game_servers),
                    'china_mobile_servers': len([s for s in game_servers if s.is_china_mobile]),
                    'avg_latency': sum(s.latency_ms for s in game_servers) / len(game_servers) if game_servers else 0,
                    'avg_packet_loss': sum(s.packet_loss_rate for s in game_servers) / len(game_servers) if game_servers else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"游戏流量分析失败: {str(e)}")
            return {
                'error': str(e),
                'game_traffic_detected': False,
                'game_servers': [],
                'network_quality': 'unknown'
            }

    def _identify_game_traffic(self, tshark_cmd: str, pcap_file: str) -> List[Dict]:
        """识别游戏流量"""
        game_traffic = []

        try:
            # 分析UDP流量，但排除QUIC（HTTP/3）流量
            result = subprocess.run([
                tshark_cmd, '-r', pcap_file, '-T', 'fields',
                '-e', 'ip.src',
                '-e', 'ip.dst',
                '-e', 'udp.srcport',
                '-e', 'udp.dstport',
                '-e', 'frame.len',
                '-e', 'frame.time_relative',
                '-Y', 'udp and not quic and not dns'  # 排除QUIC和DNS流量
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                packets = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t')
                        if len(parts) >= 6:
                            packets.append({
                                'src_ip': parts[0],
                                'dst_ip': parts[1],
                                'src_port': int(parts[2]) if parts[2].isdigit() else 0,
                                'dst_port': int(parts[3]) if parts[3].isdigit() else 0,
                                'size': int(parts[4]) if parts[4].isdigit() else 0,
                                'time': float(parts[5]) if parts[5].replace('.', '').isdigit() else 0,
                            })
                
                # 分析流量模式
                game_traffic = self._analyze_traffic_patterns(packets)
                
        except Exception as e:
            logger.error(f"游戏流量识别失败: {str(e)}")
            
        return game_traffic

    def _analyze_traffic_patterns(self, packets: List[Dict]) -> List[Dict]:
        """分析流量模式，识别游戏流量"""
        game_flows = {}
        
        for packet in packets:
            # 创建流标识（双向）
            flow_key = self._create_flow_key(packet['src_ip'], packet['dst_ip'], 
                                           packet['src_port'], packet['dst_port'])
            
            if flow_key not in game_flows:
                game_flows[flow_key] = {
                    'packets': [],
                    'src_ip': packet['src_ip'],
                    'dst_ip': packet['dst_ip'],
                    'src_port': packet['src_port'],
                    'dst_port': packet['dst_port'],
                }
            
            game_flows[flow_key]['packets'].append(packet)
        
        # 评估每个流是否为游戏流量
        identified_game_traffic = []
        for flow_key, flow_data in game_flows.items():
            if self._is_game_traffic(flow_data):
                identified_game_traffic.append(flow_data)
        
        return identified_game_traffic

    def _create_flow_key(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int) -> str:
        """创建流标识"""
        # 确保双向流量使用同一个key
        if src_ip < dst_ip or (src_ip == dst_ip and src_port < dst_port):
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"
        else:
            return f"{dst_ip}:{dst_port}-{src_ip}:{src_port}"

    def _is_game_traffic(self, flow_data: Dict) -> bool:
        """判断是否为游戏流量"""
        packets = flow_data['packets']
        if len(packets) < 10:  # 包数太少，不太可能是游戏流量
            return False

        # 首先检查端口是否为游戏端口 - 这是最重要的条件
        port_score = self._calculate_port_score(flow_data['src_port'], flow_data['dst_port'])
        if port_score == 0:  # 如果不是游戏端口，直接排除
            return False

        # 计算流量特征
        pattern = self._calculate_traffic_pattern(packets)

        # 综合评分 - 提高阈值，减少误报
        total_score = 0

        # 端口评分（必须条件）
        total_score += port_score

        # UDP比例评分（游戏主要使用UDP）
        if pattern.udp_ratio >= self.GAME_TRAFFIC_THRESHOLDS['min_udp_ratio']:
            total_score += 30

        # 包大小评分
        if (self.GAME_TRAFFIC_THRESHOLDS['min_avg_packet_size'] <=
            pattern.avg_packet_size <= self.GAME_TRAFFIC_THRESHOLDS['max_avg_packet_size']):
            total_score += 25

        # 频率评分
        if pattern.packet_frequency >= self.GAME_TRAFFIC_THRESHOLDS['min_packet_frequency']:
            total_score += 20

        # 双向通信评分
        if pattern.bidirectional_ratio >= self.GAME_TRAFFIC_THRESHOLDS['min_bidirectional_ratio']:
            total_score += 15

        # 提高阈值到80分，减少误报
        return total_score >= 80

    def _calculate_traffic_pattern(self, packets: List[Dict]) -> GameTrafficPattern:
        """计算流量模式"""
        if not packets:
            return GameTrafficPattern(0, 0, 0, 0, 0)
        
        # 计算各项指标
        total_size = sum(p['size'] for p in packets)
        avg_packet_size = total_size / len(packets)
        
        # 计算频率（包/秒）
        time_span = max(p['time'] for p in packets) - min(p['time'] for p in packets)
        packet_frequency = len(packets) / max(time_span, 1)
        
        # 计算双向比例（简化计算）
        src_ips = set(p['src_ip'] for p in packets)
        dst_ips = set(p['dst_ip'] for p in packets)
        bidirectional_ratio = min(len(src_ips), len(dst_ips)) / max(len(src_ips), len(dst_ips))
        
        return GameTrafficPattern(
            udp_ratio=1.0,  # 已经过滤了UDP
            avg_packet_size=avg_packet_size,
            packet_frequency=packet_frequency,
            bidirectional_ratio=bidirectional_ratio,
            burst_pattern_score=0  # 暂不实现
        )

    def _calculate_port_score(self, src_port: int, dst_port: int) -> int:
        """计算端口评分"""
        score = 0
        ports = [src_port, dst_port]
        
        for port in ports:
            for game_type, port_list in self.GAME_PORTS.items():
                if port in port_list:
                    score += 10
                    break
        
        return min(score, 20)  # 最高20分

    def _analyze_game_servers(self, tshark_cmd: str, pcap_file: str, game_traffic: List[Dict]) -> List[GameServerInfo]:
        """分析游戏服务器"""
        servers = []
        
        for flow in game_traffic:
            # 确定哪个是服务器IP（通常是目标IP）
            server_ip = flow['dst_ip']
            server_port = flow['dst_port']
            
            # 分析服务器信息
            server_info = self._analyze_server_info(server_ip, server_port, flow['packets'])
            servers.append(server_info)
        
        return servers

    def _analyze_server_info(self, ip: str, port: int, packets: List[Dict]) -> GameServerInfo:
        """分析服务器信息"""
        # 判断ISP归属
        isp, is_china_mobile = self._resolve_isp(ip)
        
        # 计算延迟（简化计算）
        latency_ms = self._calculate_latency(packets)
        
        # 计算丢包率（简化计算）
        packet_loss_rate = self._calculate_packet_loss(packets)
        
        # 计算置信度
        confidence_score = self._calculate_confidence(ip, port, packets)
        
        return GameServerInfo(
            ip=ip,
            port=port,
            isp=isp,
            is_china_mobile=is_china_mobile,
            latency_ms=latency_ms,
            packet_loss_rate=packet_loss_rate,
            confidence_score=confidence_score
        )

    def _resolve_isp(self, ip: str) -> Tuple[str, bool]:
        """解析IP的ISP归属"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # 检查是否为中国移动IP段
            for ip_range in self.CHINA_MOBILE_IP_RANGES:
                if ip_obj in ipaddress.ip_network(ip_range):
                    return "中国移动", True
            
            # 简化的ISP判断（实际应该使用IP数据库）
            if ip.startswith('111.') or ip.startswith('120.') or ip.startswith('183.'):
                return "中国移动", True
            elif ip.startswith('123.') or ip.startswith('125.') or ip.startswith('140.'):
                return "中国联通", False
            elif ip.startswith('116.') or ip.startswith('117.') or ip.startswith('118.'):
                return "中国电信", False
            else:
                return "未知ISP", False
                
        except Exception as e:
            logger.error(f"ISP解析失败: {str(e)}")
            return "解析失败", False

    def _calculate_latency(self, packets: List[Dict]) -> float:
        """计算延迟（简化实现）"""
        # 这里应该分析TCP RTT或其他延迟指标
        # 暂时返回模拟值
        return 50.0

    def _calculate_packet_loss(self, packets: List[Dict]) -> float:
        """计算丢包率（简化实现）"""
        # 这里应该分析重传、乱序等指标
        # 暂时返回模拟值
        return 0.1

    def _calculate_confidence(self, ip: str, port: int, packets: List[Dict]) -> float:
        """计算识别置信度"""
        confidence = 50.0  # 基础置信度
        
        # 端口匹配加分
        for game_type, port_list in self.GAME_PORTS.items():
            if port in port_list:
                confidence += 20
                break
        
        # 包数量加分
        if len(packets) > 100:
            confidence += 15
        elif len(packets) > 50:
            confidence += 10
        
        # IP段匹配加分
        if self._resolve_isp(ip)[1]:  # 是中国移动
            confidence += 15
        
        return min(confidence, 95.0)  # 最高95%

    def _evaluate_game_network_quality(self, servers: List[GameServerInfo]) -> str:
        """评估游戏网络质量"""
        if not servers:
            return "无游戏流量"
        
        avg_latency = sum(s.latency_ms for s in servers) / len(servers)
        avg_packet_loss = sum(s.packet_loss_rate for s in servers) / len(servers)
        china_mobile_ratio = len([s for s in servers if s.is_china_mobile]) / len(servers)
        
        if avg_latency < 30 and avg_packet_loss < 0.01 and china_mobile_ratio > 0.5:
            return "优秀"
        elif avg_latency < 50 and avg_packet_loss < 0.1:
            return "良好"
        elif avg_latency < 80 and avg_packet_loss < 0.5:
            return "一般"
        else:
            return "较差"

    def _generate_game_diagnosis(self, servers: List[GameServerInfo], quality: str) -> Dict:
        """生成游戏诊断报告"""
        if not servers:
            return {
                'summary': '未检测到游戏流量',
                'recommendations': ['请确认是否在游戏过程中进行抓包', '检查游戏是否正常运行']
            }
        
        china_mobile_servers = [s for s in servers if s.is_china_mobile]
        
        diagnosis = {
            'summary': f'检测到{len(servers)}个游戏服务器，网络质量：{quality}',
            'china_mobile_analysis': {
                'total_servers': len(servers),
                'china_mobile_servers': len(china_mobile_servers),
                'china_mobile_ratio': len(china_mobile_servers) / len(servers) if servers else 0,
                'recommendation': '建议选择中国移动游戏服务器以获得最佳体验' if len(china_mobile_servers) < len(servers) else '当前主要使用中国移动服务器，网络体验较好'
            },
            'performance_analysis': {
                'avg_latency': sum(s.latency_ms for s in servers) / len(servers),
                'avg_packet_loss': sum(s.packet_loss_rate for s in servers) / len(servers),
                'quality_level': quality
            },
            'recommendations': self._generate_recommendations(servers, quality)
        }
        
        return diagnosis

    def _generate_recommendations(self, servers: List[GameServerInfo], quality: str) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        china_mobile_servers = [s for s in servers if s.is_china_mobile]
        
        if len(china_mobile_servers) < len(servers):
            recommendations.append('🎯 建议在游戏设置中选择中国移动服务器以获得更好的网络体验')
        
        if quality in ['一般', '较差']:
            recommendations.extend([
                '📶 建议使用有线网络连接，避免WiFi不稳定',
                '🚀 考虑使用游戏加速器优化网络路径',
                '📱 关闭其他占用网络的应用程序',
                '⚡ 联系运营商升级网络套餐'
            ])
        
        return recommendations
