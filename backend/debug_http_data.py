#!/usr/bin/env python3
"""
调试HTTP数据生成问题
"""

import requests
import time
import threading
import json

def generate_http_traffic():
    """生成HTTP流量"""
    print("🌐 生成HTTP流量...")
    
    def make_requests():
        urls = ['http://httpbin.org/get', 'http://example.com']
        for url in urls:
            try:
                print(f"   访问: {url}")
                requests.get(url, timeout=8)
                time.sleep(1)
            except Exception as e:
                print(f"   错误: {str(e)}")
    
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    return thread

def debug_test():
    """调试测试"""
    print("🔍 调试HTTP数据生成")
    print("=" * 50)
    
    # 生成流量
    traffic_thread = generate_http_traffic()
    
    # 创建请求
    test_request = {
        "issue_type": "http",
        "duration": 6,
        "user_description": "调试HTTP数据",
        "enable_ai_analysis": False
    }
    
    try:
        response = requests.post('http://localhost:8000/api/capture', json=test_request)
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
        
        task_id = response.json().get('task_id')
        print(f"✅ 任务: {task_id}")
        
        # 等待流量
        traffic_thread.join(timeout=8)
        
        # 等待完成
        for i in range(25):
            time.sleep(1)
            status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
            if status_response.status_code == 200:
                status = status_response.json().get('status')
                print(f"状态: {status}")
                if status == 'done':
                    break
                elif status == 'error':
                    error = status_response.json().get('error', '')
                    print(f"❌ 失败: {error}")
                    return False
        
        # 获取详细结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result = result_response.json().get('result', {})
        
        print("\n📊 结果分析:")
        
        # 检查抓包摘要
        capture_summary = result.get('capture_summary', {})
        print(f"文件大小: {capture_summary.get('file_size', 0)} bytes")
        print(f"解析方法: {capture_summary.get('parsing_method', 'unknown')}")
        
        # 检查增强分析
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        if enhanced_analysis:
            print("✅ 有增强分析数据")
            
            # 基础统计
            basic_stats = enhanced_analysis.get('basic_stats', {})
            if basic_stats:
                print(f"总包数: {basic_stats.get('total_packets', 0)}")
                protocols = basic_stats.get('protocols', {})
                print(f"协议: {protocols}")
            
            # HTTP分析
            http_analysis = enhanced_analysis.get('http_analysis', {})
            if http_analysis:
                print("✅ 有HTTP分析数据")
                print(f"HTTP分析: {json.dumps(http_analysis, indent=2)}")
            else:
                print("❌ 没有HTTP分析数据")
            
            # 问题特定洞察
            issue_insights = enhanced_analysis.get('issue_specific_insights', {})
            if issue_insights:
                print("✅ 有问题特定洞察")
                print(f"洞察数据: {json.dumps(issue_insights, indent=2)}")
                
                website_performance = issue_insights.get('website_performance', {})
                if website_performance:
                    print(f"✅ 网站性能数据: {len(website_performance)} 个网站")
                    for host, data in website_performance.items():
                        print(f"  {host}: {data}")
                else:
                    print("❌ 没有网站性能数据")
            else:
                print("❌ 没有问题特定洞察")
            
            # 诊断线索
            diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
            if diagnostic_clues:
                print(f"✅ 诊断线索 ({len(diagnostic_clues)} 条):")
                for clue in diagnostic_clues:
                    print(f"  💡 {clue}")
            else:
                print("❌ 没有诊断线索")
        else:
            print("❌ 没有增强分析数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_test()
