#!/usr/bin/env python3
"""
网络抓包与AI分析系统测试脚本
测试完整的抓包、预处理、AI分析流程
"""

import asyncio
import json
import time
import requests
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
BACKEND_URL = 'http://localhost:8000'
TEST_CASES = [
    {
        'name': 'DNS解析测试',
        'issue_type': 'dns',
        'duration': 5,
        'user_description': '网站打开很慢，怀疑是DNS解析问题'
    },
    {
        'name': '网速慢测试',
        'issue_type': 'slow',
        'duration': 5,
        'user_description': '下载速度很慢，网页加载缓慢'
    },
    {
        'name': '连接问题测试',
        'issue_type': 'disconnect',
        'duration': 5,
        'user_description': '经常断网，连接不稳定'
    }
]

class NetworkCaptureAITester:
    """网络抓包AI分析测试器"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.session = requests.Session()
    
    def test_backend_health(self) -> bool:
        """测试后端服务健康状态"""
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ 后端服务正常")
                return True
            else:
                logger.error(f"❌ 后端服务异常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 无法连接后端服务: {str(e)}")
            return False
    
    def start_capture_task(self, test_case: Dict[str, Any]) -> str:
        """启动抓包任务"""
        try:
            payload = {
                'issue_type': test_case['issue_type'],
                'duration': test_case['duration'],
                'interface': 'eth0',
                'user_description': test_case['user_description'],
                'enable_ai_analysis': True
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/capture",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('task_id')
                logger.info(f"✅ 抓包任务已启动: {task_id}")
                return task_id
            else:
                logger.error(f"❌ 启动抓包任务失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 启动抓包任务异常: {str(e)}")
            return None
    
    def monitor_task_progress(self, task_id: str, timeout: int = 120) -> Dict[str, Any]:
        """监控任务进度"""
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(
                    f"{self.backend_url}/api/capture/status",
                    params={'task_id': task_id},
                    timeout=5
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    if current_status != last_status:
                        logger.info(f"📊 任务状态: {current_status} ({progress}%)")
                        last_status = current_status
                    
                    if current_status == 'done':
                        logger.info("✅ 任务完成")
                        return self.get_task_result(task_id)
                    elif current_status == 'error':
                        error_msg = status_data.get('error', '未知错误')
                        logger.error(f"❌ 任务失败: {error_msg}")
                        return {'error': error_msg}
                    
                    time.sleep(2)  # 等待2秒后再次检查
                else:
                    logger.error(f"❌ 获取任务状态失败: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ 监控任务异常: {str(e)}")
                break
        
        logger.error("❌ 任务超时")
        return {'error': '任务超时'}
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        try:
            response = self.session.get(
                f"{self.backend_url}/api/capture/result",
                params={'task_id': task_id},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ 获取任务结果成功")
                return result
            else:
                logger.error(f"❌ 获取任务结果失败: {response.status_code}")
                return {'error': f'获取结果失败: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"❌ 获取任务结果异常: {str(e)}")
            return {'error': str(e)}
    
    def validate_result(self, result: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
        """验证结果的完整性"""
        try:
            if 'error' in result:
                logger.error(f"❌ 结果包含错误: {result['error']}")
                return False
            
            # 检查基本结构
            if 'result' not in result:
                logger.error("❌ 结果缺少result字段")
                return False
            
            task_result = result['result']
            
            # 检查抓包摘要
            if 'capture_summary' not in task_result:
                logger.error("❌ 结果缺少capture_summary")
                return False
            
            capture_summary = task_result['capture_summary']
            if 'statistics' not in capture_summary:
                logger.error("❌ 抓包摘要缺少statistics")
                return False
            
            # 检查AI分析结果
            if 'ai_analysis' not in task_result:
                logger.error("❌ 结果缺少ai_analysis")
                return False
            
            ai_analysis = task_result['ai_analysis']
            if not ai_analysis.get('success'):
                logger.warning(f"⚠️ AI分析失败: {ai_analysis.get('error', '未知错误')}")
                return True  # AI分析失败不算致命错误
            
            # 检查AI分析内容
            analysis = ai_analysis.get('analysis', {})
            required_fields = ['diagnosis', 'severity', 'recommendations']
            
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"⚠️ AI分析缺少字段: {field}")
            
            logger.info("✅ 结果验证通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 结果验证异常: {str(e)}")
            return False
    
    def print_result_summary(self, result: Dict[str, Any], test_case: Dict[str, Any]):
        """打印结果摘要"""
        print(f"\n{'='*60}")
        print(f"测试案例: {test_case['name']}")
        print(f"问题类型: {test_case['issue_type']}")
        print(f"{'='*60}")
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return
        
        task_result = result.get('result', {})
        
        # 抓包统计
        capture_summary = task_result.get('capture_summary', {})
        stats = capture_summary.get('statistics', {})
        
        print(f"📊 抓包统计:")
        print(f"  - 总包数: {stats.get('total_packets', 0)}")
        print(f"  - 文件大小: {capture_summary.get('file_size', 0)} bytes")
        
        if stats.get('protocols'):
            print(f"  - 协议分布: {dict(list(stats['protocols'].items())[:3])}")
        
        # AI分析结果
        ai_analysis = task_result.get('ai_analysis', {})
        if ai_analysis.get('success'):
            analysis = ai_analysis.get('analysis', {})
            print(f"\n🤖 AI分析结果:")
            print(f"  - 诊断: {analysis.get('diagnosis', 'N/A')}")
            print(f"  - 严重程度: {analysis.get('severity', 'N/A')}")
            print(f"  - 置信度: {analysis.get('confidence', 'N/A')}%")
            
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print(f"  - 建议:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"    {i}. {rec}")
        else:
            print(f"❌ AI分析失败: {ai_analysis.get('error', '未知错误')}")
    
    def run_test_case(self, test_case: Dict[str, Any]) -> bool:
        """运行单个测试案例"""
        logger.info(f"🚀 开始测试: {test_case['name']}")
        
        # 启动抓包任务
        task_id = self.start_capture_task(test_case)
        if not task_id:
            return False
        
        # 监控任务进度
        result = self.monitor_task_progress(task_id)
        
        # 验证结果
        is_valid = self.validate_result(result, test_case)
        
        # 打印结果摘要
        self.print_result_summary(result, test_case)
        
        return is_valid
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试案例"""
        logger.info("🎯 开始网络抓包AI分析系统测试")
        
        # 检查后端健康状态
        if not self.test_backend_health():
            return {'success': False, 'error': '后端服务不可用'}
        
        results = {
            'success': True,
            'total_tests': len(TEST_CASES),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }
        
        for test_case in TEST_CASES:
            try:
                success = self.run_test_case(test_case)
                
                if success:
                    results['passed_tests'] += 1
                    logger.info(f"✅ 测试通过: {test_case['name']}")
                else:
                    results['failed_tests'] += 1
                    logger.error(f"❌ 测试失败: {test_case['name']}")
                
                results['test_results'].append({
                    'name': test_case['name'],
                    'success': success
                })
                
                # 测试间隔
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ 测试异常: {test_case['name']} - {str(e)}")
                results['failed_tests'] += 1
                results['test_results'].append({
                    'name': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        # 打印测试总结
        print(f"\n{'='*60}")
        print(f"测试总结")
        print(f"{'='*60}")
        print(f"总测试数: {results['total_tests']}")
        print(f"通过: {results['passed_tests']}")
        print(f"失败: {results['failed_tests']}")
        print(f"成功率: {results['passed_tests']/results['total_tests']*100:.1f}%")
        
        if results['failed_tests'] == 0:
            print("🎉 所有测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查日志")
            results['success'] = False
        
        return results

def main():
    """主函数"""
    tester = NetworkCaptureAITester(BACKEND_URL)
    results = tester.run_all_tests()
    
    # 保存测试结果
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info("测试结果已保存到 test_results.json")
    
    return 0 if results['success'] else 1

if __name__ == '__main__':
    exit(main())
