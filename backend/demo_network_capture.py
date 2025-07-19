#!/usr/bin/env python3
"""
网络抓包与AI分析演示脚本
用于快速测试和演示系统功能
"""

import asyncio
import json
import time
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入我们的模块
from app.api.capture import CaptureRequest, run_capture, tasks
from app.services.ai_analysis_service import get_ai_analysis_service

async def demo_capture_and_analysis():
    """演示抓包和AI分析流程"""
    
    print("🚀 网络抓包与AI分析演示")
    print("=" * 50)
    
    # 创建测试请求
    test_cases = [
        {
            'name': 'DNS解析测试',
            'request': CaptureRequest(
                issue_type='dns',
                duration=5,
                interface=None,  # 使用自动检测的接口
                user_description='DNS解析速度测试',
                enable_ai_analysis=False  # 先不启用AI分析，避免API调用
            )
        },
        {
            'name': '网络性能测试',
            'request': CaptureRequest(
                issue_type='slow',
                duration=3,
                interface=None,  # 使用自动检测的接口
                user_description='网络速度慢测试',
                enable_ai_analysis=False
            )
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {test_case['name']}")
        print("-" * 30)
        
        # 生成任务ID
        task_id = f"demo_{int(time.time())}_{i}"
        
        # 初始化任务状态
        tasks[task_id] = {
            'status': 'pending',
            'result': None,
            'error': None,
            'created_at': datetime.now().isoformat(),
            'request': test_case['request'].dict()
        }
        
        try:
            print(f"⏳ 开始执行抓包任务: {task_id}")
            
            # 执行抓包
            await run_capture(task_id, test_case['request'])
            
            # 检查结果
            task = tasks.get(task_id)
            if task['status'] == 'done':
                print("✅ 抓包任务完成")
                
                # 显示结果摘要
                result = task['result']
                if 'capture_summary' in result:
                    summary = result['capture_summary']
                    stats = summary.get('statistics', {})
                    
                    print(f"📊 抓包统计:")
                    print(f"  - 总包数: {stats.get('total_packets', 0)}")
                    print(f"  - 文件大小: {summary.get('file_size', 0)} bytes")
                    
                    if stats.get('protocols'):
                        print(f"  - 协议分布: {dict(list(stats['protocols'].items())[:3])}")
                    
                    # 显示问题特定分析
                    issue_specific = stats.get('issue_specific', {})
                    if issue_specific and not issue_specific.get('error'):
                        print(f"  - 特定分析: {json.dumps(issue_specific, indent=4, ensure_ascii=False)}")
                
            elif task['status'] == 'error':
                print(f"❌ 抓包任务失败: {task['error']}")
            else:
                print(f"⚠️ 任务状态异常: {task['status']}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            logger.error(f"演示执行异常: {str(e)}", exc_info=True)
        
        # 等待一下再执行下一个测试
        if i < len(test_cases):
            print("\n⏸️ 等待3秒后执行下一个测试...")
            await asyncio.sleep(3)
    
    print(f"\n🎉 演示完成!")
    print("=" * 50)

async def demo_ai_analysis():
    """演示AI分析功能（需要配置AI API）"""
    
    print("\n🤖 AI分析功能演示")
    print("=" * 50)
    
    # 模拟抓包数据
    mock_capture_summary = {
        'statistics': {
            'total_packets': 150,
            'protocols': {'TCP': 80, 'UDP': 50, 'ICMP': 20},
            'top_sources': {'192.168.1.1': 60, '8.8.8.8': 40},
            'top_destinations': {'192.168.1.100': 70, '8.8.8.8': 30},
            'issue_specific': {
                'dns_queries': 25,
                'dns_responses': 20,
                'failed_queries': 5,
                'avg_response_time': 150.5,
                'slow_queries': [
                    {'query_name': 'example.com', 'response_time': 200.0, 'response_code': '0'}
                ]
            }
        },
        'sample_packets': [
            {'time': '2024-01-01 12:00:00', 'src': '192.168.1.100', 'dst': '8.8.8.8', 'protocol': 'UDP', 'info': 'DNS query'},
            {'time': '2024-01-01 12:00:01', 'src': '8.8.8.8', 'dst': '192.168.1.100', 'protocol': 'UDP', 'info': 'DNS response'}
        ],
        'file_size': 15360,
        'analysis_time': datetime.now().isoformat()
    }
    
    try:
        ai_service = get_ai_analysis_service()
        
        print("📝 生成AI分析...")
        result = await ai_service.analyze_network_issue(
            issue_type='dns',
            capture_summary=mock_capture_summary,
            user_description='DNS解析经常超时，网站打开很慢'
        )
        
        if result['success']:
            analysis = result['analysis']
            print("✅ AI分析完成")
            print(f"🔍 诊断结论: {analysis.get('diagnosis', 'N/A')}")
            print(f"⚠️ 严重程度: {analysis.get('severity', 'N/A')}")
            print(f"📈 置信度: {analysis.get('confidence', 'N/A')}%")
            
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print("💡 解决建议:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
        else:
            print(f"❌ AI分析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ AI分析异常: {str(e)}")
        print("💡 提示: 请确保已配置AI API密钥")

def check_system_requirements():
    """检查系统要求"""
    
    print("🔍 检查系统要求")
    print("=" * 50)
    
    import subprocess
    import os
    
    # 检查tcpdump
    try:
        result = subprocess.run(['which', 'tcpdump'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ tcpdump 已安装")
        else:
            print("❌ tcpdump 未安装，请运行: sudo apt-get install tcpdump")
    except Exception as e:
        print(f"❌ 检查tcpdump失败: {str(e)}")
    
    # 检查网络接口
    try:
        import platform
        system = platform.system().lower()

        if system == 'darwin':  # macOS
            result = subprocess.run(['ifconfig', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 网络接口可用")
                interfaces = result.stdout.strip().split()
                if interfaces:
                    print(f"📡 可用接口: {', '.join(interfaces[:5])}")
            else:
                print("❌ 无法获取网络接口信息")
        else:  # Linux
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 网络接口可用")
                # 显示可用接口
                lines = result.stdout.split('\n')
                interfaces = []
                for line in lines:
                    if ': ' in line and 'state' in line.lower():
                        interface = line.split(':')[1].strip().split('@')[0]
                        interfaces.append(interface)
                if interfaces:
                    print(f"📡 可用接口: {', '.join(interfaces[:5])}")
            else:
                print("❌ 无法获取网络接口信息")
    except Exception as e:
        print(f"❌ 检查网络接口失败: {str(e)}")
    
    # 检查权限
    if os.geteuid() == 0:
        print("✅ 以root权限运行")
    else:
        print("⚠️ 非root权限，抓包可能需要sudo")
    
    # 检查Python依赖
    required_modules = ['pyshark', 'scapy', 'fastapi', 'aiohttp']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 已安装")
        except ImportError:
            print(f"❌ {module} 未安装")

async def main():
    """主函数"""
    
    print("🌟 网络抓包与AI分析系统演示")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查系统要求
    check_system_requirements()
    
    # 演示抓包功能
    await demo_capture_and_analysis()
    
    # 演示AI分析功能
    await demo_ai_analysis()
    
    print("\n🎯 演示结束")
    print("💡 提示: 要在生产环境中使用，请确保:")
    print("  1. 配置AI API密钥")
    print("  2. 以适当权限运行")
    print("  3. 选择正确的网络接口")

if __name__ == '__main__':
    asyncio.run(main())
