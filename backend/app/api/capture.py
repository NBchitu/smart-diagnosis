import os
import uuid
import threading
import time
import subprocess
import logging
import asyncio
from fastapi import APIRouter, BackgroundTasks, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import pyshark
import json
from datetime import datetime

from app.services.ai_analysis_service import get_ai_analysis_service

logger = logging.getLogger(__name__)

router = APIRouter()

CAPTURE_DIR = '/tmp/packet_captures'
os.makedirs(CAPTURE_DIR, exist_ok=True)
tasks: Dict[str, Dict] = {}

class CaptureRequest(BaseModel):
    issue_type: str
    duration: int = 10
    interface: Optional[str] = None  # 将在处理时自动设置
    target_ip: Optional[str] = None
    target_port: Optional[int] = None
    custom_filter: Optional[str] = None
    user_description: Optional[str] = None
    enable_ai_analysis: bool = True

@router.post('')
def start_capture(req: CaptureRequest, background_tasks: BackgroundTasks):
    """启动网络抓包任务"""
    try:
        # 如果没有指定接口，使用默认接口
        if not req.interface:
            req.interface = get_default_interface()
            logger.info(f"使用默认网络接口: {req.interface}")

        # 验证接口是否存在
        if not validate_interface(req.interface):
            # 如果指定的接口不存在，尝试使用默认接口
            default_interface = get_default_interface()
            if validate_interface(default_interface):
                logger.warning(f"接口 {req.interface} 不存在，使用默认接口: {default_interface}")
                req.interface = default_interface
            else:
                available_interfaces = list_available_interfaces()
                error_msg = f"网络接口 {req.interface} 不存在"
                if available_interfaces:
                    error_msg += f"，可用接口: {', '.join(available_interfaces[:5])}"
                raise HTTPException(status_code=400, detail=error_msg)

        # 验证抓包时长
        if req.duration < 1 or req.duration > 300:
            raise HTTPException(status_code=400, detail="抓包时长必须在1-300秒之间")

        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            'status': 'pending',
            'result': None,
            'error': None,
            'created_at': datetime.now().isoformat(),
            'request': req.dict()
        }

        background_tasks.add_task(run_capture_wrapper, task_id, req)
        logger.info(f"创建抓包任务: {task_id}, 问题类型: {req.issue_type}")

        return {'task_id': task_id, 'status': 'pending'}

    except Exception as e:
        logger.error(f"启动抓包任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动抓包任务失败: {str(e)}")

@router.get('/status')
def get_status(task_id: str = Query(...)):
    """获取抓包任务状态"""
    task = tasks.get(task_id)
    if not task:
        return {'status': 'not_found', 'error': '任务不存在'}

    return {
        'status': task['status'],
        'error': task.get('error'),
        'created_at': task.get('created_at'),
        'progress': get_task_progress(task['status'])
    }

@router.get('/result')
def get_result(task_id: str = Query(...)):
    """获取抓包分析结果"""
    task = tasks.get(task_id)
    if not task:
        return {'error': '任务不存在'}

    if task['status'] != 'done':
        return {'error': '任务未完成', 'status': task['status']}

    if not task.get('result'):
        return {'error': '结果不可用'}

    return {
        'result': task['result'],
        'status': 'done',
        'created_at': task.get('created_at')
    }

@router.get('/interfaces')
def get_network_interfaces():
    """获取可用的网络接口"""
    try:
        import platform
        interfaces = list_available_interfaces()
        default_interface = get_default_interface()

        return {
            'interfaces': interfaces,
            'default': default_interface,
            'current_system': platform.system().lower()
        }
    except Exception as e:
        logger.error(f"获取网络接口失败: {str(e)}")
        import platform
        return {
            'interfaces': [],
            'default': get_default_interface(),
            'current_system': platform.system().lower(),
            'error': str(e)
        }

def run_capture_wrapper(task_id: str, req: CaptureRequest):
    """同步包装函数，用于在后台任务中运行异步抓包函数"""
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 运行异步函数
        loop.run_until_complete(run_capture(task_id, req))

    except Exception as e:
        logger.error(f"抓包包装函数执行失败: {task_id}, 错误: {str(e)}")
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)
    finally:
        # 清理事件循环
        try:
            loop.close()
        except:
            pass

async def run_capture(task_id: str, req: CaptureRequest):
    """执行抓包任务"""
    try:
        logger.info(f"开始执行抓包任务: {task_id}")

        # 1. 生成抓包命令和文件路径
        pcap_file = os.path.join(CAPTURE_DIR, f'{task_id}.pcap')
        filter_expr = get_filter_by_issue(req.issue_type, req.target_ip, req.target_port, req.custom_filter)

        # 构建tcpdump命令
        cmd = build_tcpdump_command(req.interface, pcap_file, req.duration, filter_expr)

        # 2. 执行抓包
        tasks[task_id]['status'] = 'capturing'
        logger.info(f"执行抓包命令: {cmd}")

        # 在macOS下，我们需要手动终止tcpdump进程
        import platform
        system = platform.system().lower()

        if system == 'darwin':
            # macOS下启动tcpdump进程并在指定时间后终止
            import signal
            import time

            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 等待指定的抓包时间
            time.sleep(req.duration)

            # 终止进程
            try:
                process.terminate()
                stdout, stderr = process.communicate(timeout=5)
                result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
        else:
            # Linux下使用原来的方式
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=req.duration + 30)

        if result.returncode != 0:
            raise Exception(f"抓包命令执行失败: {result.stderr}")

        # 检查pcap文件是否生成
        if not os.path.exists(pcap_file) or os.path.getsize(pcap_file) == 0:
            raise Exception("抓包文件未生成或为空")

        # 3. 预处理数据包
        tasks[task_id]['status'] = 'processing'
        logger.info(f"开始预处理数据包: {pcap_file}")

        summary = preprocess_pcap(pcap_file, req.issue_type)

        # 4. AI分析（如果启用）
        ai_analysis = None
        if req.enable_ai_analysis:
            try:
                tasks[task_id]['status'] = 'ai_analyzing'
                logger.info(f"开始AI分析: {task_id}")

                # 在新的线程中执行AI分析，避免事件循环冲突
                import concurrent.futures
                import threading

                def run_ai_analysis():
                    try:
                        logger.info("AI分析线程开始执行")
                        ai_service = get_ai_analysis_service()

                        # 使用同步方式调用AI分析，传递task_id用于调试
                        result = ai_service.analyze_network_issue_sync(
                            req.issue_type,
                            summary,
                            req.user_description,
                            task_id
                        )
                        logger.info("AI分析线程执行完成")
                        return result

                    except Exception as e:
                        logger.error(f"AI分析线程异常: {str(e)}", exc_info=True)
                        return {
                            'success': False,
                            'error': f"AI分析线程异常: {str(e)}",
                            'timestamp': datetime.now().isoformat()
                        }

                # 在线程池中执行AI分析
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        logger.info("提交AI分析任务到线程池")
                        future = executor.submit(run_ai_analysis)
                        ai_analysis = future.result(timeout=30)  # 30秒超时
                        logger.info(f"AI分析完成: {task_id}")

                except concurrent.futures.TimeoutError:
                    logger.error(f"AI分析超时: {task_id}")
                    ai_analysis = {
                        'success': False,
                        'error': 'AI分析超时（30秒）',
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"线程池执行失败: {task_id}, 错误: {str(e)}", exc_info=True)
                    ai_analysis = {
                        'success': False,
                        'error': f"线程池执行失败: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    }

            except Exception as e:
                logger.error(f"AI分析外层异常: {task_id}, 错误: {str(e)}", exc_info=True)
                ai_analysis = {
                    'success': False,
                    'error': f"AI分析外层异常: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

        # 5. 完成任务 - 确保状态始终被更新
        try:
            result = {
                'capture_summary': summary,
                'ai_analysis': ai_analysis,
                'task_info': {
                    'task_id': task_id,
                    'issue_type': req.issue_type,
                    'duration': req.duration,
                    'interface': req.interface,
                    'completed_at': datetime.now().isoformat()
                }
            }

            tasks[task_id]['result'] = result
            tasks[task_id]['status'] = 'done'

            logger.info(f"抓包任务完成: {task_id}")

        except Exception as e:
            logger.error(f"设置任务完成状态失败: {task_id}, 错误: {str(e)}", exc_info=True)
            # 即使设置结果失败，也要确保状态被更新
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['error'] = f"设置任务结果失败: {str(e)}"

    except subprocess.TimeoutExpired:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = '抓包超时'
        logger.error(f"抓包任务超时: {task_id}")

    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)
        logger.error(f"抓包任务失败: {task_id}, 错误: {str(e)}")

    finally:
        # 清理临时文件（可选，保留用于调试）
        # if os.path.exists(pcap_file):
        #     os.remove(pcap_file)
        pass

def get_filter_by_issue(issue_type: str, target_ip: Optional[str] = None,
                       target_port: Optional[int] = None, custom_filter: Optional[str] = None) -> str:
    """根据问题类型生成抓包过滤表达式"""

    # 如果有自定义过滤器，优先使用
    if custom_filter:
        return custom_filter

    # 重新设计的过滤表达式 - 专注于三大核心功能
    base_filters = {
        'website_access': 'tcp port 80 or port 443 or port 8080 or port 8443',  # 网站访问问题
        'interconnection': 'tcp or udp',  # 互联互通访问（需要全流量分析）
        'game_lag': 'udp or (tcp and (port 7000 or port 8001 or port 17500 or port 27015 or port 25565 or port 10012))',  # 游戏卡顿问题
        'custom': ''
    }

    filter_expr = base_filters.get(issue_type, '')

    # 添加目标IP过滤
    if target_ip:
        ip_filter = f"host {target_ip}"
        if filter_expr:
            filter_expr = f"({filter_expr}) and {ip_filter}"
        else:
            filter_expr = ip_filter

    # 添加目标端口过滤
    if target_port:
        port_filter = f"port {target_port}"
        if filter_expr:
            filter_expr = f"({filter_expr}) and {port_filter}"
        else:
            filter_expr = port_filter

    return filter_expr

def validate_interface(interface: str) -> bool:
    """验证网络接口是否存在"""
    try:
        import platform
        system = platform.system().lower()

        if system == 'darwin':  # macOS
            result = subprocess.run(['ifconfig', interface],
                                  capture_output=True, text=True)
            return result.returncode == 0
        else:  # Linux
            result = subprocess.run(['ip', 'link', 'show', interface],
                                  capture_output=True, text=True)
            return result.returncode == 0
    except Exception:
        return False

def get_default_interface() -> str:
    """获取默认网络接口"""
    try:
        import platform
        system = platform.system().lower()

        if system == 'darwin':  # macOS
            # 尝试常见的macOS接口
            common_interfaces = ['en0', 'en1', 'en2', 'lo0']
            for interface in common_interfaces:
                if validate_interface(interface):
                    return interface
            return 'en0'  # 默认返回en0
        else:  # Linux
            # 尝试常见的Linux接口
            common_interfaces = ['eth0', 'wlan0', 'enp0s3', 'ens33', 'lo']
            for interface in common_interfaces:
                if validate_interface(interface):
                    return interface
            return 'eth0'  # 默认返回eth0
    except Exception:
        import platform
        return 'en0' if platform.system().lower() == 'darwin' else 'eth0'

def list_available_interfaces() -> list:
    """列出所有可用的网络接口"""
    try:
        import platform
        system = platform.system().lower()

        if system == 'darwin':  # macOS
            result = subprocess.run(['ifconfig', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split()
        else:  # Linux
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state' in line.lower():
                        interface = line.split(':')[1].strip().split('@')[0]
                        interfaces.append(interface)
                return interfaces
        return []
    except Exception:
        return []

def build_tcpdump_command(interface: str, output_file: str, duration: int, filter_expr: str) -> str:
    """构建tcpdump命令"""
    import platform
    system = platform.system().lower()

    if system == 'darwin':  # macOS
        # macOS下的tcpdump命令，使用gtimeout或者直接依赖后续的subprocess timeout
        cmd_parts = [
            'sudo', 'tcpdump',
            '-i', interface,
            '-w', output_file,
            '-s', '65535',  # 捕获完整数据包
            '-q'  # 安静模式，减少输出
        ]

        if filter_expr:
            # 在macOS下，将复杂的过滤表达式用单引号包围以避免shell解析问题
            cmd_parts.append(f"'{filter_expr}'")

        # macOS下不使用timeout命令，而是依赖subprocess的timeout参数
        return ' '.join(cmd_parts)
    else:  # Linux
        cmd_parts = [
            'sudo', 'tcpdump',
            '-i', interface,
            '-w', output_file,
            '-G', str(duration),
            '-W', '1',
            '-s', '65535',  # 捕获完整数据包
            '-q'  # 安静模式，减少输出
        ]

        if filter_expr:
            # 在Linux下也用单引号包围过滤表达式，保持一致性
            cmd_parts.append(f"'{filter_expr}'")

        return ' '.join(cmd_parts)

def get_task_progress(status: str) -> int:
    """根据任务状态返回进度百分比"""
    progress_map = {
        'pending': 0,
        'capturing': 25,
        'processing': 50,
        'ai_analyzing': 80,
        'done': 100,
        'error': 0
    }
    return progress_map.get(status, 0)

def preprocess_pcap(pcap_file: str, issue_type: str):
    """预处理pcap文件，生成结构化摘要"""
    try:
        # 检查文件是否存在
        if not os.path.exists(pcap_file):
            return {
                'error': f"pcap文件不存在: {pcap_file}",
                'analysis_time': datetime.now().isoformat()
            }

        # 检查文件大小
        file_size = os.path.getsize(pcap_file)
        if file_size == 0:
            return {
                'error': "pcap文件为空",
                'analysis_time': datetime.now().isoformat(),
                'file_size': 0
            }

        # 使用增强的分析方法，生成对AI有价值的数据
        logger.info("使用增强分析方法，生成深度网络洞察")

        # 使用增强的pcap分析
        enhanced_analysis = get_enhanced_pcap_analysis(pcap_file, issue_type)

        return {
            'enhanced_analysis': enhanced_analysis,
            'analysis_time': datetime.now().isoformat(),
            'file_size': file_size,
            'parsing_method': 'enhanced_tshark_analysis',
            # 保持向后兼容
            'statistics': enhanced_analysis.get('basic_stats', {}),
            'sample_packets': []
        }

    except Exception as e:
        logger.error(f"预处理pcap文件失败: {str(e)}")
        return {
            'error': f"预处理失败: {str(e)}",
            'analysis_time': datetime.now().isoformat()
        }

def get_enhanced_pcap_analysis(pcap_file: str, issue_type: str) -> Dict:
    """增强的pcap分析，生成对AI诊断有价值的数据"""
    analysis = {
        'basic_stats': {},
        'network_behavior': {},
        'performance_indicators': {},
        'anomaly_detection': {},
        'issue_specific_insights': {},
        'diagnostic_clues': []
    }

    try:
        import platform
        system = platform.system().lower()

        # 检查tshark是否可用
        tshark_paths = [
            '/opt/homebrew/bin/tshark',
            '/usr/local/bin/tshark',
            '/usr/bin/tshark',
            'tshark'
        ]

        tshark_cmd = None
        for path in tshark_paths:
            try:
                result = subprocess.run([path, '-v'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    tshark_cmd = path
                    break
            except:
                continue

        if not tshark_cmd:
            logger.warning("tshark不可用，使用基础分析")
            return get_basic_file_analysis(pcap_file, issue_type)

        # 1. 基础统计信息
        analysis['basic_stats'] = get_basic_packet_stats(tshark_cmd, pcap_file)

        # 2. 网络行为分析
        analysis['network_behavior'] = analyze_network_behavior(tshark_cmd, pcap_file)

        # 3. 性能指标分析
        analysis['performance_indicators'] = analyze_performance_metrics(tshark_cmd, pcap_file)

        # 4. 异常检测
        analysis['anomaly_detection'] = detect_network_anomalies(tshark_cmd, pcap_file)

        # 5. HTTP/HTTPS流量分析
        analysis['http_analysis'] = analyze_http_traffic(tshark_cmd, pcap_file)

        # 6. 问题特定洞察
        analysis['issue_specific_insights'] = get_issue_specific_insights(tshark_cmd, pcap_file, issue_type)

        # 7. 生成诊断线索
        analysis['diagnostic_clues'] = generate_diagnostic_clues(analysis, issue_type)

        logger.info(f"增强分析完成: {analysis['basic_stats'].get('total_packets', 0)} 个包")

    except Exception as e:
        logger.error(f"增强分析失败: {str(e)}")
        analysis['error'] = str(e)
        # 降级到基础分析
        analysis.update(get_basic_file_analysis(pcap_file, issue_type))

    return analysis

def analyze_interconnection_issues(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析互联互通问题"""
    try:
        from app.services.interconnection_analyzer import InterconnectionAnalyzer

        analyzer = InterconnectionAnalyzer()
        result = analyzer.analyze_interconnection(tshark_cmd, pcap_file)

        return {
            'targeted_analysis': result.get('report', {}),
            'relevant_metrics': {
                'local_isp': result.get('local_isp', 'unknown'),
                'cross_isp_connections': result.get('analysis_summary', {}).get('cross_isp_connections', 0),
                'avg_cross_isp_latency': result.get('analysis_summary', {}).get('avg_cross_isp_latency', 0)
            },
            'diagnostic_hints': [
                f"🏢 本地ISP: {result.get('local_isp', 'unknown')}",
                f"🔄 跨运营商连接: {result.get('analysis_summary', {}).get('cross_isp_connections', 0)}个",
                f"⏱️ 跨网平均延迟: {result.get('analysis_summary', {}).get('avg_cross_isp_latency', 0):.1f}ms"
            ]
        }

    except Exception as e:
        logger.error(f"互联互通分析失败: {str(e)}")
        return {
            'targeted_analysis': {'error': str(e)},
            'relevant_metrics': {},
            'diagnostic_hints': ['互联互通分析失败']
        }

def analyze_game_lag_issues(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析游戏卡顿问题"""
    try:
        from app.services.game_traffic_analyzer import GameTrafficAnalyzer

        analyzer = GameTrafficAnalyzer()
        result = analyzer.analyze_game_traffic(tshark_cmd, pcap_file)

        return {
            'targeted_analysis': result.get('diagnosis', {}),
            'relevant_metrics': {
                'game_traffic_detected': result.get('game_traffic_detected', False),
                'total_game_servers': result.get('analysis_summary', {}).get('total_game_servers', 0),
                'china_mobile_servers': result.get('analysis_summary', {}).get('china_mobile_servers', 0),
                'avg_latency': result.get('analysis_summary', {}).get('avg_latency', 0),
                'network_quality': result.get('network_quality', 'unknown')
            },
            'diagnostic_hints': [
                f"🎮 游戏流量检测: {'是' if result.get('game_traffic_detected', False) else '否'}",
                f"🎯 游戏服务器数量: {result.get('analysis_summary', {}).get('total_game_servers', 0)}个",
                f"📱 中国移动服务器: {result.get('analysis_summary', {}).get('china_mobile_servers', 0)}个",
                f"⏱️ 平均延迟: {result.get('analysis_summary', {}).get('avg_latency', 0):.1f}ms",
                f"📊 网络质量: {result.get('network_quality', 'unknown')}"
            ]
        }

    except Exception as e:
        logger.error(f"游戏卡顿分析失败: {str(e)}")
        return {
            'targeted_analysis': {'error': str(e)},
            'relevant_metrics': {},
            'diagnostic_hints': ['游戏卡顿分析失败']
        }

def get_basic_packet_stats(tshark_cmd: str, pcap_file: str) -> Dict:
    """获取基础包统计"""
    stats = {
        'total_packets': 0,
        'protocols': {},
        'time_range': {'start': None, 'end': None, 'duration': 0},
        'packet_sizes': {'min': 0, 'max': 0, 'avg': 0},
        'data_volume': {'total_bytes': 0, 'avg_rate': 0}
    }

    try:
        # 获取包的基本信息：时间、大小、协议
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'frame.time_epoch',
            '-e', 'frame.len',
            '-e', 'frame.protocols'
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            packet_times = []
            packet_sizes = []
            protocols = {}

            for line in lines:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        # 时间
                        try:
                            timestamp = float(parts[0])
                            packet_times.append(timestamp)
                        except:
                            pass

                        # 大小
                        try:
                            size = int(parts[1])
                            packet_sizes.append(size)
                        except:
                            pass

                        # 协议
                        protocol_stack = parts[2].split(':')
                        if protocol_stack:
                            top_protocol = protocol_stack[-1].upper()
                            protocols[top_protocol] = protocols.get(top_protocol, 0) + 1

            stats['total_packets'] = len(packet_times)
            stats['protocols'] = protocols

            if packet_times:
                stats['time_range']['start'] = min(packet_times)
                stats['time_range']['end'] = max(packet_times)
                stats['time_range']['duration'] = max(packet_times) - min(packet_times)

            if packet_sizes:
                stats['packet_sizes']['min'] = min(packet_sizes)
                stats['packet_sizes']['max'] = max(packet_sizes)
                stats['packet_sizes']['avg'] = sum(packet_sizes) / len(packet_sizes)
                stats['data_volume']['total_bytes'] = sum(packet_sizes)
                if stats['time_range']['duration'] > 0:
                    stats['data_volume']['avg_rate'] = sum(packet_sizes) / stats['time_range']['duration']

    except Exception as e:
        logger.debug(f"基础统计失败: {str(e)}")

    return stats

def analyze_network_behavior(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析网络行为模式 - 简化版，只保留核心连接信息"""
    behavior = {
        'connection_summary': {}
    }

    try:
        # 只统计基础连接信息，不收集技术细节
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'ip.dst', '-e', 'tcp.dstport'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            unique_destinations = set()

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        dst_ip, dst_port = parts[:2]
                        if dst_ip and dst_port:
                            unique_destinations.add(f"{dst_ip}:{dst_port}")

            behavior['connection_summary']['unique_destinations'] = len(unique_destinations)

    except Exception as e:
        logger.debug(f"网络行为分析失败: {str(e)}")

    return behavior

def analyze_http_traffic(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析HTTP/HTTPS流量 - 极简版，只保留核心网站信息"""
    http_analysis = {
        'websites_accessed': {},
        'connection_summary': {}
    }

    try:
        # 只进行基础的HTTP统计，不收集详细信息
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'http.host'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            http_hosts = set()
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    host = line.strip()
                    if host:
                        http_hosts.add(host)

            http_analysis['basic_summary'] = {
                'http_sites_count': len(http_hosts),
                'has_http_traffic': len(http_hosts) > 0
            }

        # 分析HTTPS网站访问 - 只保留核心信息
        https_result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'tls.handshake.extensions_server_name'
        ], capture_output=True, text=True, timeout=10)

        if https_result.returncode == 0:
            websites = {}

            for line in https_result.stdout.strip().split('\n'):
                if line.strip():
                    server_name = line.strip()
                    if server_name:
                        websites[server_name] = websites.get(server_name, 0) + 1

            # 只保留访问次数最多的前10个网站
            http_analysis['websites_accessed'] = dict(sorted(websites.items(), key=lambda x: x[1], reverse=True)[:10])
            http_analysis['connection_summary'] = {
                'total_websites': len(websites),
                'has_https_traffic': len(websites) > 0
            }

    except Exception as e:
        logger.debug(f"HTTP流量分析失败: {str(e)}")
        http_analysis['error'] = str(e)

    return http_analysis

def analyze_performance_metrics(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析性能指标"""
    metrics = {
        'latency_indicators': {},
        'throughput_analysis': {},
        'error_rates': {},
        'quality_metrics': {}
    }

    try:
        # 分析TCP RTT和重传
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'tcp.analysis.ack_rtt',
            '-e', 'tcp.analysis.retransmission',
            '-e', 'tcp.analysis.duplicate_ack',
            '-e', 'tcp.analysis.fast_retransmission'
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            rtt_values = []
            retransmissions = 0
            duplicate_acks = 0
            fast_retrans = 0

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')

                    # RTT分析
                    if len(parts) > 0 and parts[0]:
                        try:
                            rtt = float(parts[0])
                            rtt_values.append(rtt * 1000)  # 转换为毫秒
                        except:
                            pass

                    # 错误统计
                    if len(parts) > 1 and parts[1]:
                        retransmissions += 1
                    if len(parts) > 2 and parts[2]:
                        duplicate_acks += 1
                    if len(parts) > 3 and parts[3]:
                        fast_retrans += 1

            if rtt_values:
                metrics['latency_indicators']['avg_rtt_ms'] = sum(rtt_values) / len(rtt_values)
                metrics['latency_indicators']['min_rtt_ms'] = min(rtt_values)
                metrics['latency_indicators']['max_rtt_ms'] = max(rtt_values)
                metrics['latency_indicators']['rtt_samples'] = len(rtt_values)

            metrics['error_rates']['retransmissions'] = retransmissions
            metrics['error_rates']['duplicate_acks'] = duplicate_acks
            metrics['error_rates']['fast_retransmissions'] = fast_retrans

    except Exception as e:
        logger.debug(f"性能指标分析失败: {str(e)}")

    return metrics

def detect_network_anomalies(tshark_cmd: str, pcap_file: str) -> Dict:
    """检测网络异常"""
    anomalies = {
        'suspicious_patterns': [],
        'error_indicators': [],
        'performance_issues': [],
        'security_concerns': []
    }

    try:
        # 检测DNS异常
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'dns.qry.name', '-e', 'dns.resp.code', '-e', 'dns.time'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            dns_failures = 0
            slow_dns_queries = 0

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        # DNS响应码检查
                        if parts[1] and parts[1] != '0':
                            dns_failures += 1

                        # DNS查询时间检查
                        if len(parts) > 2 and parts[2]:
                            try:
                                dns_time = float(parts[2])
                                if dns_time > 1.0:  # 超过1秒认为是慢查询
                                    slow_dns_queries += 1
                            except:
                                pass

            if dns_failures > 0:
                anomalies['error_indicators'].append(f"DNS查询失败: {dns_failures} 次")
            if slow_dns_queries > 0:
                anomalies['performance_issues'].append(f"DNS慢查询: {slow_dns_queries} 次")

    except Exception as e:
        logger.debug(f"异常检测失败: {str(e)}")

    return anomalies

def get_issue_specific_insights(tshark_cmd: str, pcap_file: str, issue_type: str) -> Dict:
    """获取问题特定的洞察"""
    insights = {
        'targeted_analysis': {},
        'relevant_metrics': {},
        'diagnostic_hints': []
    }

    try:
        if issue_type == 'website_access':
            insights.update(analyze_http_specific_issues(tshark_cmd, pcap_file))
        elif issue_type == 'interconnection':
            insights.update(analyze_interconnection_issues(tshark_cmd, pcap_file))
        elif issue_type == 'game_lag':
            insights.update(analyze_game_lag_issues(tshark_cmd, pcap_file))
        else:
            insights['targeted_analysis'] = {'note': f'通用分析，问题类型: {issue_type}'}

    except Exception as e:
        logger.debug(f"问题特定分析失败: {str(e)}")
        insights['error'] = str(e)

    return insights

def analyze_dns_issues(tshark_cmd: str, pcap_file: str) -> Dict:
    """专门分析DNS问题"""
    dns_analysis = {
        'dns_queries': {},
        'dns_servers': {},
        'response_times': {},
        'failure_analysis': {}
    }

    try:
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'dns.qry.name', '-e', 'dns.qry.type', '-e', 'dns.resp.code',
            '-e', 'dns.time', '-e', 'ip.dst', '-e', 'dns.flags.response'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            queries = {}
            servers = {}
            response_times = []
            failures = {}

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        query_name = parts[0] if parts[0] else 'unknown'
                        query_type = parts[1] if parts[1] else 'A'
                        resp_code = parts[2] if parts[2] else '0'
                        dns_time = parts[3] if parts[3] else '0'
                        server_ip = parts[4] if len(parts) > 4 and parts[4] else 'unknown'
                        is_response = parts[5] if len(parts) > 5 and parts[5] else '0'

                        # 统计查询
                        queries[query_name] = queries.get(query_name, 0) + 1

                        # 统计DNS服务器
                        if is_response == '0':  # 这是查询，不是响应
                            servers[server_ip] = servers.get(server_ip, 0) + 1

                        # 响应时间
                        try:
                            time_val = float(dns_time)
                            if time_val > 0:
                                response_times.append(time_val * 1000)  # 转换为毫秒
                        except:
                            pass

                        # 失败分析
                        if resp_code != '0':
                            failures[resp_code] = failures.get(resp_code, 0) + 1

            dns_analysis['dns_queries']['top_queries'] = dict(sorted(queries.items(), key=lambda x: x[1], reverse=True)[:10])
            dns_analysis['dns_servers']['servers_used'] = servers

            if response_times:
                dns_analysis['response_times']['avg_ms'] = sum(response_times) / len(response_times)
                dns_analysis['response_times']['max_ms'] = max(response_times)
                dns_analysis['response_times']['samples'] = len(response_times)

            dns_analysis['failure_analysis']['error_codes'] = failures

    except Exception as e:
        logger.debug(f"DNS分析失败: {str(e)}")

    return dns_analysis

def analyze_slow_connection_issues(tshark_cmd: str, pcap_file: str) -> Dict:
    """分析连接慢的问题"""
    slow_analysis = {
        'tcp_handshake': {},
        'window_scaling': {},
        'congestion_control': {},
        'bandwidth_utilization': {}
    }

    try:
        # 分析TCP握手时间
        result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'tcp.connection.syn', '-e', 'tcp.connection.synack',
            '-e', 'tcp.window_size', '-e', 'tcp.analysis.ack_rtt'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            handshake_times = []
            window_sizes = []

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')

                    # 窗口大小分析
                    if len(parts) > 2 and parts[2]:
                        try:
                            window_size = int(parts[2])
                            window_sizes.append(window_size)
                        except:
                            pass

            if window_sizes:
                slow_analysis['window_scaling']['avg_window_size'] = sum(window_sizes) / len(window_sizes)
                slow_analysis['window_scaling']['min_window_size'] = min(window_sizes)
                slow_analysis['window_scaling']['max_window_size'] = max(window_sizes)

    except Exception as e:
        logger.debug(f"慢连接分析失败: {str(e)}")

    return slow_analysis

def analyze_http_specific_issues(tshark_cmd: str, pcap_file: str) -> Dict:
    """专门分析HTTP/HTTPS网站访问问题 - 聚焦域名、IP、响应时延关联"""
    http_issues = {
        'website_performance': {},  # 核心：域名-IP-时延关联
        'response_summary': {},     # 简化的响应统计
        'performance_issues': []    # 性能问题列表
    }

    try:
        # 分析HTTP流量（如果有）
        website_performance = {}

        # 1. 分析明文HTTP流量
        http_result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'http.host',                    # 域名
            '-e', 'ip.dst',                       # 目标IP
            '-e', 'http.response.code',           # 响应状态码
            '-e', 'tcp.analysis.ack_rtt',         # TCP RTT
            '-e', 'tcp.analysis.initial_rtt',     # 初始RTT
            '-e', 'frame.time_relative',          # 相对时间
            '-e', 'http.request.method',          # HTTP方法
        ], capture_output=True, text=True, timeout=10)

        if http_result.returncode == 0:
            website_performance.update(process_http_data(http_result.stdout, 'HTTP'))

        # 2. 分析HTTPS流量（通过TLS SNI和TCP连接）
        https_result = subprocess.run([
            tshark_cmd, '-r', pcap_file, '-T', 'fields',
            '-e', 'tls.handshake.extensions_server_name',  # HTTPS域名（SNI）
            '-e', 'ip.dst',                                # 目标IP
            '-e', 'tcp.analysis.ack_rtt',                  # TCP RTT
            '-e', 'tcp.analysis.initial_rtt',              # 初始RTT
            '-e', 'frame.time_relative',                   # 相对时间
            '-e', 'tcp.dstport',                           # 目标端口
        ], capture_output=True, text=True, timeout=10)

        if https_result.returncode == 0:
            website_performance.update(process_https_data(https_result.stdout, 'HTTPS'))

        # 整理最终结果
        performance_data = {}
        performance_issues = []

        for site_key, data in website_performance.items():
            if not data.get('has_traffic', False):
                continue

            # 转换IP集合为列表
            ips = list(data['ips'])

            # 计算TCP RTT统计
            tcp_times = data['tcp_rtts']
            tcp_stats = {}
            if tcp_times:
                tcp_stats = {
                    'avg_ms': round(sum(tcp_times) / len(tcp_times), 1),
                    'min_ms': round(min(tcp_times), 1),
                    'max_ms': round(max(tcp_times), 1),
                    'samples': len(tcp_times)
                }

            # 计算错误率（仅对HTTP有效）
            error_rate = 0
            if data.get('total_requests', 0) > 0:
                error_rate = (data.get('error_count', 0) / data['total_requests']) * 100

            # 组织核心数据
            performance_data[site_key] = {
                'ips': ips,
                'tcp_rtt': tcp_stats,
                'requests': {
                    'total': data.get('total_requests', 0),
                    'errors': data.get('error_count', 0),
                    'error_rate_percent': round(error_rate, 1),
                    'error_codes': data.get('error_codes', {})
                },
                'protocol': data.get('protocol', 'UNKNOWN'),
                'access_duration_seconds': data.get('duration', None)
            }

            # 识别性能问题
            if tcp_stats.get('avg_ms', 0) > 100:
                performance_issues.append(f"📡 {site_key}: 网络延迟高 (平均{tcp_stats['avg_ms']}ms)")
            elif tcp_stats.get('avg_ms', 0) > 50:
                performance_issues.append(f"⏱️ {site_key}: 网络延迟偏高 (平均{tcp_stats['avg_ms']}ms)")

            if error_rate > 10:
                performance_issues.append(f"❌ {site_key}: 错误率高 ({error_rate:.1f}%)")

            if len(ips) > 1:
                performance_issues.append(f"🔄 {site_key}: 多IP访问 ({len(ips)}个IP)")

        http_issues['website_performance'] = performance_data
        http_issues['performance_issues'] = performance_issues

        # 简化的响应统计
        total_sites = len(performance_data)
        total_requests = sum(data['requests']['total'] for data in performance_data.values())
        total_errors = sum(data['requests']['errors'] for data in performance_data.values())

        http_issues['response_summary'] = {
            'websites_accessed': total_sites,
            'total_requests': total_requests,
            'total_errors': total_errors,
            'overall_error_rate_percent': round((total_errors / total_requests) * 100, 1) if total_requests > 0 else 0
        }



    except Exception as e:
        logger.debug(f"HTTP问题分析失败: {str(e)}")
        http_issues['error'] = str(e)

    return http_issues

def process_http_data(stdout_data: str, protocol: str) -> Dict:
    """处理HTTP数据"""
    website_data = {}

    for line in stdout_data.strip().split('\n'):
        if line.strip():
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                host = parts[0] if parts[0] else ''
                dst_ip = parts[1] if parts[1] else ''
                resp_code = parts[2] if parts[2] else ''
                tcp_ack_rtt = parts[3] if parts[3] else ''
                tcp_initial_rtt = parts[4] if parts[4] else ''
                frame_time = parts[5] if parts[5] else ''
                http_method = parts[6] if parts[6] else ''

                if host:  # 只处理有域名的HTTP请求
                    if host not in website_data:
                        website_data[host] = {
                            'ips': set(),
                            'tcp_rtts': [],
                            'total_requests': 0,
                            'error_count': 0,
                            'error_codes': {},
                            'protocol': protocol,
                            'has_traffic': False
                        }

                    site_data = website_data[host]

                    if dst_ip:
                        site_data['ips'].add(dst_ip)

                    if http_method or resp_code:
                        site_data['total_requests'] += 1
                        site_data['has_traffic'] = True

                    # 记录TCP RTT
                    rtt_recorded = False
                    if tcp_ack_rtt:
                        try:
                            rtt_ms = float(tcp_ack_rtt) * 1000
                            if rtt_ms > 0:
                                site_data['tcp_rtts'].append(rtt_ms)
                                rtt_recorded = True
                        except:
                            pass

                    if not rtt_recorded and tcp_initial_rtt:
                        try:
                            rtt_ms = float(tcp_initial_rtt) * 1000
                            if rtt_ms > 0:
                                site_data['tcp_rtts'].append(rtt_ms)
                        except:
                            pass

                    # 记录HTTP错误
                    if resp_code and (resp_code.startswith('4') or resp_code.startswith('5')):
                        site_data['error_count'] += 1
                        site_data['error_codes'][resp_code] = site_data['error_codes'].get(resp_code, 0) + 1

    return website_data

def process_https_data(stdout_data: str, protocol: str) -> Dict:
    """处理HTTPS数据"""
    website_data = {}

    for line in stdout_data.strip().split('\n'):
        if line.strip():
            parts = line.strip().split('\t')
            if len(parts) >= 6:
                server_name = parts[0] if parts[0] else ''
                dst_ip = parts[1] if parts[1] else ''
                tcp_ack_rtt = parts[2] if parts[2] else ''
                tcp_initial_rtt = parts[3] if parts[3] else ''
                frame_time = parts[4] if parts[4] else ''
                dst_port = parts[5] if parts[5] else ''

                # 只处理HTTPS端口的连接
                if server_name and dst_port in ['443', '8443']:
                    if server_name not in website_data:
                        website_data[server_name] = {
                            'ips': set(),
                            'tcp_rtts': [],
                            'total_requests': 0,
                            'error_count': 0,
                            'error_codes': {},
                            'protocol': protocol,
                            'has_traffic': False
                        }

                    site_data = website_data[server_name]

                    if dst_ip:
                        site_data['ips'].add(dst_ip)
                        site_data['has_traffic'] = True  # HTTPS连接就算有流量

                    # 记录TCP RTT
                    rtt_recorded = False
                    if tcp_ack_rtt:
                        try:
                            rtt_ms = float(tcp_ack_rtt) * 1000
                            if rtt_ms > 0:
                                site_data['tcp_rtts'].append(rtt_ms)
                                rtt_recorded = True
                        except:
                            pass

                    if not rtt_recorded and tcp_initial_rtt:
                        try:
                            rtt_ms = float(tcp_initial_rtt) * 1000
                            if rtt_ms > 0:
                                site_data['tcp_rtts'].append(rtt_ms)
                        except:
                            pass

    return website_data

def generate_diagnostic_clues(analysis: Dict, issue_type: str) -> List[str]:
    """生成诊断线索"""
    clues = []

    try:
        basic_stats = analysis.get('basic_stats', {})
        performance = analysis.get('performance_indicators', {})
        anomalies = analysis.get('anomaly_detection', {})
        http_analysis = analysis.get('http_analysis', {})

        # 基于包数量的线索
        total_packets = basic_stats.get('total_packets', 0)
        if total_packets == 0:
            clues.append("⚠️ 没有捕获到数据包，可能是权限问题或网络接口选择错误")
        elif total_packets < 10:
            clues.append("⚠️ 捕获的数据包很少，可能需要更长的抓包时间")

        # 基于协议分布的线索
        protocols = basic_stats.get('protocols', {})
        if 'DNS' in protocols and protocols['DNS'] > total_packets * 0.5:
            clues.append("🔍 DNS流量占比很高，可能存在DNS解析问题")

        # HTTP/HTTPS流量分析线索 - 使用聚焦的分析结果
        if http_analysis:
            # 检查是否有聚焦的网站性能数据（来自issue_specific_insights）
            issue_insights = analysis.get('issue_specific_insights', {})
            website_performance = issue_insights.get('website_performance', {})

            if website_performance:
                # 使用聚焦的网站性能数据
                site_count = len(website_performance)
                clues.append(f"🌍 分析了 {site_count} 个网站的访问性能")

                # 显示具体的网站性能数据（最多3个）
                for host, perf_data in list(website_performance.items())[:3]:
                    ips = perf_data.get('ips', [])
                    tcp_time = perf_data.get('tcp_rtt', {})
                    requests_data = perf_data.get('requests', {})

                    # 构建IP信息
                    if ips:
                        ip_info = f"IP: {', '.join(ips[:2])}"
                        if len(ips) > 2:
                            ip_info += f" (+{len(ips)-2}个)"
                    else:
                        ip_info = "IP: 未知"

                    # 构建时延信息（主要使用TCP RTT）
                    if tcp_time.get('avg_ms'):
                        time_info = f"延迟: {tcp_time['avg_ms']}ms"
                        # 添加延迟评估
                        avg_rtt = tcp_time['avg_ms']
                        if avg_rtt > 100:
                            time_info += " (高)"
                        elif avg_rtt > 50:
                            time_info += " (偏高)"
                        else:
                            time_info += " (正常)"
                    else:
                        time_info = "延迟: 未测量"

                    # 构建错误信息
                    error_rate = requests_data.get('error_rate_percent', 0)
                    if error_rate > 0:
                        error_info = f"错误率: {error_rate}%"
                    else:
                        error_info = "无错误"

                    clues.append(f"📊 {host}: {ip_info}, {time_info}, {error_info}")

                # 显示性能问题
                performance_issues = issue_insights.get('performance_issues', [])
                for issue in performance_issues[:3]:  # 只显示前3个问题
                    clues.append(issue)

            else:
                # 降级到基础HTTP分析
                basic_summary = http_analysis.get('basic_summary', {})
                if basic_summary.get('has_http_traffic'):
                    site_count = basic_summary.get('http_sites_count', 0)
                    if site_count > 0:
                        clues.append(f"🌐 检测到 {site_count} 个HTTP网站访问")
                        clues.append("⚠️ 详细性能数据不可用，建议重新抓包")

            # HTTPS网站访问分析（简化版）
            websites_accessed = http_analysis.get('websites_accessed', {})
            connection_summary = http_analysis.get('connection_summary', {})

            if websites_accessed:
                total_sites = connection_summary.get('total_websites', len(websites_accessed))
                clues.append(f"🌐 访问了 {total_sites} 个HTTPS网站")

                # 显示访问最频繁的前3个网站
                top_sites = list(websites_accessed.items())[:3]
                for site, count in top_sites:
                    clues.append(f"  📊 {site}: {count} 次连接")

        # 基于性能指标的线索
        latency = performance.get('latency_indicators', {})
        if latency.get('avg_rtt_ms', 0) > 100:
            clues.append(f"🐌 平均RTT较高 ({latency['avg_rtt_ms']:.1f}ms)，可能存在网络延迟问题")

        # 基于错误率的线索
        errors = performance.get('error_rates', {})
        retrans = errors.get('retransmissions', 0)
        if retrans > 0:
            clues.append(f"📡 检测到 {retrans} 次TCP重传，可能存在网络质量问题")

        # 基于异常检测的线索
        error_indicators = anomalies.get('error_indicators', [])
        for error in error_indicators:
            clues.append(f"❌ {error}")

        performance_issues = anomalies.get('performance_issues', [])
        for issue in performance_issues:
            clues.append(f"⏱️ {issue}")

        # HTTP问题特定线索 - 聚焦域名-IP-时延关联
        if issue_type == 'http':
            issue_insights = analysis.get('issue_specific_insights', {})
            website_performance = issue_insights.get('website_performance', {})
            performance_issues = issue_insights.get('performance_issues', [])

            if website_performance:
                site_count = len(website_performance)
                clues.append(f"🌍 分析了 {site_count} 个网站的访问性能")

                # 显示具体的网站性能数据
                for host, perf_data in list(website_performance.items())[:3]:  # 只显示前3个
                    ips = perf_data.get('ips', [])
                    http_time = perf_data.get('http_response_time', {})
                    tcp_time = perf_data.get('tcp_rtt', {})
                    requests_data = perf_data.get('requests', {})

                    ip_info = f"IP: {', '.join(ips[:2])}" if ips else "IP: 未知"
                    if len(ips) > 2:
                        ip_info += f" (+{len(ips)-2}个)"

                    time_info = []
                    if http_time.get('avg_ms'):
                        time_info.append(f"HTTP: {http_time['avg_ms']}ms")
                    if tcp_time.get('avg_ms'):
                        time_info.append(f"TCP: {tcp_time['avg_ms']}ms")

                    error_rate = requests_data.get('error_rate_percent', 0)
                    error_info = f"错误率: {error_rate}%" if error_rate > 0 else "无错误"

                    clues.append(f"📊 {host}: {ip_info}, {', '.join(time_info)}, {error_info}")

            # 显示性能问题
            for issue in performance_issues[:5]:  # 只显示前5个问题
                clues.append(issue)

            if not performance_issues and website_performance:
                clues.append("✅ 网站访问性能正常，无明显问题")

        # 其他问题类型的线索
        elif issue_type == 'dns':
            clues.append("🔍 建议检查DNS服务器配置和响应时间")
        elif issue_type == 'slow':
            clues.append("🐌 建议检查网络带宽和TCP窗口大小")
        elif issue_type == 'disconnect':
            clues.append("🔌 建议检查TCP连接重置和超时情况")

        if not clues:
            clues.append("✅ 从抓包数据看，网络行为基本正常")

    except Exception as e:
        logger.debug(f"生成诊断线索失败: {str(e)}")
        clues.append("⚠️ 诊断分析过程中出现异常")

    return clues

def get_basic_file_analysis(pcap_file: str, issue_type: str) -> Dict:
    """基础文件分析（降级方案）"""
    return {
        'basic_stats': {
            'total_packets': 'unknown',
            'file_size': os.path.getsize(pcap_file) if os.path.exists(pcap_file) else 0
        },
        'diagnostic_clues': [
            "⚠️ 使用基础分析模式",
            f"📁 文件大小: {os.path.getsize(pcap_file) if os.path.exists(pcap_file) else 0} bytes"
        ]
    }

def analyze_by_issue_type_simple(pcap_file: str, issue_type: str) -> Dict:
    """简化的问题类型分析，避免复杂的pyshark操作"""
    analysis = {
        'issue_type': issue_type,
        'analysis_method': 'simplified',
        'note': '基于文件大小和问题类型的基础分析'
    }

    try:
        file_size = os.path.getsize(pcap_file) if os.path.exists(pcap_file) else 0

        # 基于文件大小的简单推断
        if file_size == 0:
            analysis['status'] = 'no_data'
            analysis['message'] = '未捕获到数据包'
        elif file_size < 1024:  # 小于1KB
            analysis['status'] = 'low_activity'
            analysis['message'] = '网络活动较少'
        elif file_size > 1024 * 1024:  # 大于1MB
            analysis['status'] = 'high_activity'
            analysis['message'] = '网络活动频繁'
        else:
            analysis['status'] = 'normal_activity'
            analysis['message'] = '网络活动正常'

        # 根据问题类型添加特定信息
        if issue_type == 'dns':
            analysis['focus'] = 'DNS查询和响应'
        elif issue_type == 'slow':
            analysis['focus'] = 'TCP连接和传输性能'
        elif issue_type == 'disconnect':
            analysis['focus'] = 'TCP连接状态'
        elif issue_type == 'lan':
            analysis['focus'] = 'ARP和ICMP协议'
        elif issue_type == 'video':
            analysis['focus'] = 'UDP流媒体传输'

        analysis['file_size_bytes'] = file_size

    except Exception as e:
        logger.error(f"简化分析失败: {str(e)}")
        analysis['error'] = str(e)

    return analysis

def analyze_by_issue_type(pcap_file: str, issue_type: str) -> Dict:
    """根据问题类型进行特定分析（保留原函数以兼容）"""
    # 先尝试简化分析
    return analyze_by_issue_type_simple(pcap_file, issue_type)

def analyze_dns_issues(pcap_file: str) -> Dict:
    """分析DNS相关问题"""
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='dns')

        dns_queries = 0
        dns_responses = 0
        failed_queries = 0
        response_times = []
        slow_queries = []
        query_response_map = {}

        for pkt in cap:
            try:
                if hasattr(pkt, 'dns'):
                    dns_layer = pkt.dns

                    # DNS查询
                    if hasattr(dns_layer, 'qry_name') and dns_layer.qr == '0':
                        dns_queries += 1
                        query_id = dns_layer.id
                        query_time = float(pkt.sniff_timestamp)
                        query_response_map[query_id] = {
                            'query_time': query_time,
                            'query_name': dns_layer.qry_name
                        }

                    # DNS响应
                    elif dns_layer.qr == '1':
                        dns_responses += 1
                        response_id = dns_layer.id
                        response_time = float(pkt.sniff_timestamp)

                        if response_id in query_response_map:
                            query_info = query_response_map[response_id]
                            rtt = (response_time - query_info['query_time']) * 1000  # 转换为毫秒
                            response_times.append(rtt)

                            # 检查是否为慢查询（>100ms）
                            if rtt > 100:
                                slow_queries.append({
                                    'query_name': query_info['query_name'],
                                    'response_time': rtt,
                                    'response_code': getattr(dns_layer, 'rcode', 'unknown')
                                })

                            # 检查是否为失败查询
                            if hasattr(dns_layer, 'rcode') and dns_layer.rcode != '0':
                                failed_queries += 1

                            del query_response_map[response_id]

            except Exception as e:
                logger.debug(f"处理DNS包时出错: {str(e)}")
                continue

        cap.close()

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            'dns_queries': dns_queries,
            'dns_responses': dns_responses,
            'failed_queries': failed_queries,
            'avg_response_time': round(avg_response_time, 2),
            'slow_queries': slow_queries[:10],  # 只返回前10个慢查询
            'total_response_times': len(response_times)
        }

    except Exception as e:
        logger.error(f"DNS分析失败: {str(e)}")
        return {'error': str(e)}

def analyze_performance_issues(pcap_file: str) -> Dict:
    """分析性能相关问题"""
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='tcp')

        tcp_retransmissions = 0
        tcp_resets = 0
        tcp_fins = 0
        connection_times = {}
        high_latency_connections = []
        total_bytes = 0

        for pkt in cap:
            try:
                if hasattr(pkt, 'tcp'):
                    tcp_layer = pkt.tcp

                    # 统计TCP重传
                    if hasattr(tcp_layer, 'analysis_retransmission'):
                        tcp_retransmissions += 1

                    # 统计TCP重置
                    if hasattr(tcp_layer, 'flags_reset') and tcp_layer.flags_reset == '1':
                        tcp_resets += 1

                    # 统计TCP FIN
                    if hasattr(tcp_layer, 'flags_fin') and tcp_layer.flags_fin == '1':
                        tcp_fins += 1

                    # 计算连接延迟（SYN到SYN-ACK）
                    if hasattr(tcp_layer, 'flags_syn') and tcp_layer.flags_syn == '1':
                        conn_key = f"{pkt.ip.src}:{tcp_layer.srcport}-{pkt.ip.dst}:{tcp_layer.dstport}"
                        if hasattr(tcp_layer, 'flags_ack') and tcp_layer.flags_ack == '1':
                            # SYN-ACK包
                            if conn_key in connection_times:
                                rtt = (float(pkt.sniff_timestamp) - connection_times[conn_key]) * 1000
                                if rtt > 100:  # 高延迟连接（>100ms）
                                    high_latency_connections.append({
                                        'connection': conn_key,
                                        'latency': round(rtt, 2)
                                    })
                        else:
                            # SYN包
                            connection_times[conn_key] = float(pkt.sniff_timestamp)

                    # 统计流量
                    if hasattr(pkt, 'length'):
                        total_bytes += int(pkt.length)

            except Exception as e:
                logger.debug(f"处理TCP包时出错: {str(e)}")
                continue

        cap.close()

        return {
            'tcp_retransmissions': tcp_retransmissions,
            'tcp_resets': tcp_resets,
            'tcp_fins': tcp_fins,
            'high_latency_connections': high_latency_connections[:10],
            'total_bytes': total_bytes,
            'bandwidth_mbps': round(total_bytes * 8 / (1024 * 1024), 2)  # 估算带宽
        }

    except Exception as e:
        logger.error(f"性能分析失败: {str(e)}")
        return {'error': str(e)}

def analyze_connection_issues(pcap_file: str) -> Dict:
    """分析连接相关问题"""
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='tcp')

        connection_attempts = 0
        failed_connections = 0
        connection_resets = 0
        successful_connections = 0

        for pkt in cap:
            try:
                if hasattr(pkt, 'tcp'):
                    tcp_layer = pkt.tcp

                    # SYN包 - 连接尝试
                    if (hasattr(tcp_layer, 'flags_syn') and tcp_layer.flags_syn == '1' and
                        hasattr(tcp_layer, 'flags_ack') and tcp_layer.flags_ack == '0'):
                        connection_attempts += 1

                    # SYN-ACK包 - 成功连接
                    elif (hasattr(tcp_layer, 'flags_syn') and tcp_layer.flags_syn == '1' and
                          hasattr(tcp_layer, 'flags_ack') and tcp_layer.flags_ack == '1'):
                        successful_connections += 1

                    # RST包 - 连接重置
                    elif hasattr(tcp_layer, 'flags_reset') and tcp_layer.flags_reset == '1':
                        connection_resets += 1

            except Exception as e:
                logger.debug(f"处理连接包时出错: {str(e)}")
                continue

        cap.close()

        failed_connections = connection_attempts - successful_connections
        success_rate = (successful_connections / connection_attempts * 100) if connection_attempts > 0 else 0

        return {
            'connection_attempts': connection_attempts,
            'successful_connections': successful_connections,
            'failed_connections': max(0, failed_connections),
            'connection_resets': connection_resets,
            'success_rate': round(success_rate, 2)
        }

    except Exception as e:
        logger.error(f"连接分析失败: {str(e)}")
        return {'error': str(e)}

def analyze_lan_issues(pcap_file: str) -> Dict:
    """分析局域网相关问题"""
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='arp or icmp')

        arp_requests = 0
        arp_responses = 0
        icmp_packets = 0
        icmp_unreachable = 0
        ping_requests = 0
        ping_responses = 0

        for pkt in cap:
            try:
                # ARP分析
                if hasattr(pkt, 'arp'):
                    arp_layer = pkt.arp
                    if hasattr(arp_layer, 'opcode'):
                        if arp_layer.opcode == '1':  # ARP请求
                            arp_requests += 1
                        elif arp_layer.opcode == '2':  # ARP响应
                            arp_responses += 1

                # ICMP分析
                elif hasattr(pkt, 'icmp'):
                    icmp_layer = pkt.icmp
                    icmp_packets += 1

                    if hasattr(icmp_layer, 'type'):
                        if icmp_layer.type == '8':  # Echo Request (ping)
                            ping_requests += 1
                        elif icmp_layer.type == '0':  # Echo Reply
                            ping_responses += 1
                        elif icmp_layer.type == '3':  # Destination Unreachable
                            icmp_unreachable += 1

            except Exception as e:
                logger.debug(f"处理LAN包时出错: {str(e)}")
                continue

        cap.close()

        arp_success_rate = (arp_responses / arp_requests * 100) if arp_requests > 0 else 0
        ping_success_rate = (ping_responses / ping_requests * 100) if ping_requests > 0 else 0

        return {
            'arp_requests': arp_requests,
            'arp_responses': arp_responses,
            'arp_success_rate': round(arp_success_rate, 2),
            'icmp_packets': icmp_packets,
            'ping_requests': ping_requests,
            'ping_responses': ping_responses,
            'ping_success_rate': round(ping_success_rate, 2),
            'icmp_unreachable': icmp_unreachable
        }

    except Exception as e:
        logger.error(f"LAN分析失败: {str(e)}")
        return {'error': str(e)}

def analyze_video_issues(pcap_file: str) -> Dict:
    """分析视频相关问题"""
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='udp')

        udp_packets = 0
        total_bytes = 0
        packet_times = []
        packet_sizes = []

        for pkt in cap:
            try:
                if hasattr(pkt, 'udp'):
                    udp_packets += 1

                    if hasattr(pkt, 'length'):
                        packet_size = int(pkt.length)
                        total_bytes += packet_size
                        packet_sizes.append(packet_size)

                    packet_times.append(float(pkt.sniff_timestamp))

            except Exception as e:
                logger.debug(f"处理UDP包时出错: {str(e)}")
                continue

        cap.close()

        # 计算抖动（相邻包到达时间差的变化）
        jitter = 0
        if len(packet_times) > 2:
            intervals = [packet_times[i+1] - packet_times[i] for i in range(len(packet_times)-1)]
            if len(intervals) > 1:
                avg_interval = sum(intervals) / len(intervals)
                jitter = sum(abs(interval - avg_interval) for interval in intervals) / len(intervals)
                jitter = jitter * 1000  # 转换为毫秒

        # 计算平均包大小
        avg_packet_size = sum(packet_sizes) / len(packet_sizes) if packet_sizes else 0

        return {
            'udp_packets': udp_packets,
            'total_bytes': total_bytes,
            'avg_packet_size': round(avg_packet_size, 2),
            'jitter_ms': round(jitter, 2),
            'bandwidth_kbps': round(total_bytes * 8 / 1024, 2) if packet_times else 0
        }

    except Exception as e:
        logger.error(f"视频分析失败: {str(e)}")
        return {'error': str(e)}

@router.get("/debug/tasks")
def debug_tasks():
    """调试：查看所有任务状态"""
    return {
        "total_tasks": len(tasks),
        "task_ids": list(tasks.keys()),
        "tasks_summary": {
            task_id: {
                "status": task.get('status') if task else 'None',
                "has_result": bool(task.get('result')) if task else False,
                "has_capture_summary": bool(task.get('result', {}).get('capture_summary')) if task else False
            } for task_id, task in tasks.items()
        }
    }

@router.get("/debug/ai-config")
def debug_ai_config():
    """调试：查看AI配置状态"""
    try:
        from app.config.ai_config import get_ai_config
        import os

        ai_config = get_ai_config()

        # 获取环境变量（隐藏敏感信息）
        env_vars = {}
        for key in ['AI_PROVIDER', 'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL']:
            value = os.getenv(key, 'NOT_SET')
            if 'API_KEY' in key and value != 'NOT_SET':
                env_vars[key] = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                env_vars[key] = value

        current_config = ai_config.get_current_config()

        return {
            "current_provider": ai_config.current_provider,
            "environment_variables": env_vars,
            "current_config": {
                "name": current_config.name if current_config else None,
                "base_url": current_config.base_url if current_config else None,
                "model": current_config.model if current_config else None,
                "api_key_set": bool(current_config.api_key) if current_config else False,
                "api_key_preview": f"{current_config.api_key[:10]}...{current_config.api_key[-4:]}" if current_config and current_config.api_key else "NOT_SET"
            } if current_config else None,
            "all_providers": {
                name: {
                    "enabled": provider.enabled,
                    "base_url": provider.base_url,
                    "model": provider.model,
                    "api_key_set": bool(provider.api_key)
                } for name, provider in ai_config.providers.items()
            }
        }

    except Exception as e:
        logger.error(f"AI配置调试失败: {str(e)}", exc_info=True)
        return {
            "error": str(e)
        }

@router.post("/test-ai")
async def test_ai_analysis():
    """测试AI分析功能"""
    try:
        from app.services.ai_analysis_service import get_ai_analysis_service

        # 创建测试数据
        test_capture_summary = {
            "statistics": {
                "total_packets": 1000,
                "duration": 30,
                "total_bytes": 500000
            },
            "enhanced_analysis": {
                "network_quality": {
                    "avg_rtt": 45.5,
                    "packet_loss_rate": 0.02,
                    "retransmissions": 5
                },
                "http_analysis": {
                    "total_requests": 50,
                    "unique_domains": 8,
                    "https_ratio": 0.9
                }
            }
        }

        ai_service = get_ai_analysis_service()
        result = await ai_service.analyze_network_issue(
            issue_type="slow",
            capture_summary=test_capture_summary,
            user_description="网络速度很慢，网页加载缓慢"
        )

        return {
            "success": True,
            "test_result": result
        }

    except Exception as e:
        logger.error(f"AI测试失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/analyze-ai")
async def start_ai_analysis(request: dict):
    """启动AI分析（用于网站性能展示后的AI分析）"""
    try:
        task_id = request.get('task_id')
        logger.info(f"收到AI分析请求，任务ID: {task_id}")

        if not task_id:
            raise HTTPException(status_code=400, detail="缺少任务ID")

        if task_id not in tasks:
            logger.error(f"任务不存在: {task_id}, 当前任务列表: {list(tasks.keys())}")
            raise HTTPException(status_code=404, detail="任务不存在")

        task = tasks[task_id]

        # 额外检查task是否为None
        if task is None:
            logger.error(f"任务数据为空: {task_id}")
            raise HTTPException(status_code=404, detail="任务数据异常")

        logger.info(f"任务状态: {task.get('status', 'unknown')}")

        # 检查任务状态
        if task.get('status') != 'done':
            raise HTTPException(status_code=400, detail=f"任务尚未完成数据预处理，当前状态: {task.get('status', 'unknown')}")

        # 检查是否已有AI分析结果
        result = task.get('result', {})
        if not result:
            logger.info(f"任务结果为空: {task_id}")
        else:
            ai_analysis = result.get('ai_analysis')
            if ai_analysis and isinstance(ai_analysis, dict) and ai_analysis.get('success'):
                logger.info(f"AI分析已完成: {task_id}")
                return {"message": "AI分析已完成", "task_id": task_id}

        # 更新任务状态为AI分析中
        task['status'] = 'ai_analyzing'
        task['progress'] = 80
        logger.info(f"开始AI分析: {task_id}")

        # 异步启动AI分析
        asyncio.create_task(run_ai_analysis_async(task_id))

        return {"message": "AI分析已启动", "task_id": task_id}

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"启动AI分析失败: {str(e)}", exc_info=True)

        # 安全地更新任务状态
        if task_id in tasks and tasks[task_id] is not None:
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['error'] = f"启动AI分析失败: {str(e)}"

        raise HTTPException(status_code=500, detail=f"启动AI分析失败: {str(e)}")

async def run_ai_analysis_async(task_id: str):
    """异步运行AI分析"""
    task = tasks.get(task_id)
    if not task or task is None:
        logger.error(f"任务不存在或为空: {task_id}")
        return

    try:
        logger.info(f"开始AI分析: {task_id}")

        # 获取现有结果
        result = task.get('result')
        if not result or not isinstance(result, dict):
            logger.error(f"任务结果为空或格式错误: {task_id}, result type: {type(result)}")
            task['status'] = 'error'
            task['error'] = '任务结果数据为空或格式错误'
            return

        capture_summary = result.get('capture_summary')
        if not capture_summary or not isinstance(capture_summary, dict):
            logger.error(f"抓包摘要为空或格式错误: {task_id}, summary type: {type(capture_summary)}")
            task['status'] = 'error'
            task['error'] = '抓包摘要数据为空或格式错误'
            return

        logger.info(f"抓包摘要数据大小: {len(str(capture_summary))} 字符")

        # 运行AI分析
        ai_service = get_ai_analysis_service()
        logger.info(f"AI服务实例创建成功")

        ai_result = await ai_service.analyze_network_issue(
            issue_type=task.get('issue_type', 'unknown'),
            capture_summary=capture_summary,
            user_description=task.get('user_description', '')
        )

        logger.info(f"AI分析完成，结果: {ai_result.get('success', False)}")

        # 更新结果
        result['ai_analysis'] = ai_result
        task['result'] = result
        task['status'] = 'done'
        task['progress'] = 100

        logger.info(f"AI分析任务完成: {task_id}")

    except Exception as e:
        logger.error(f"AI分析失败: {str(e)}", exc_info=True)

        # 安全地更新任务状态
        if task_id in tasks and tasks[task_id] is not None:
            task = tasks[task_id]
            task['status'] = 'error'
            task['error'] = f"AI分析失败: {str(e)}"

            # 添加错误的AI分析结果
            result = task.get('result')
            if not result or not isinstance(result, dict):
                result = {}
                task['result'] = result

            result['ai_analysis'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'analysis': {
                    'diagnosis': f'AI分析服务错误: {str(e)}',
                    'severity': 'unknown',
                    'root_cause': '服务配置或网络连接问题',
                    'key_findings': ['AI分析过程中发生错误'],
                    'recommendations': ['检查AI服务配置', '验证网络连接', '查看服务日志'],
                    'diagnostic_clues': [
                        f'❌ 错误信息: {str(e)}',
                        '🔧 建议检查AI服务状态',
                        '📋 查看详细日志获取更多信息'
                    ],
                    'technical_details': f'错误详情: {str(e)}',
                    'confidence': 0,
                    'next_steps': '请检查系统配置并重试'
                }
            }
            task['result'] = result