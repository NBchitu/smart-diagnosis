#!/usr/bin/env python3
"""
快速测试时延数据修复
"""

import requests
import time
import threading

def generate_simple_http_traffic():
    """生成简单的HTTP流量"""
    print("🌐 生成HTTP流量...")
    
    def make_requests():
        urls = [
            'http://httpbin.org/get',
            'http://httpbin.org/delay/1',
            'http://example.com',
        ]
        for url in urls:
            try:
                print(f"   访问: {url}")
                requests.get(url, timeout=8)
                time.sleep(1)
            except:
                pass
    
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    return thread

def quick_test():
    """快速测试"""
    print("🔍 快速测试时延修复")
    print("=" * 50)
    
    # 生成流量
    traffic_thread = generate_simple_http_traffic()
    
    # 创建请求
    test_request = {
        "issue_type": "http",
        "duration": 8,
        "user_description": "快速时延测试",
        "enable_ai_analysis": False  # 跳过AI分析，加快测试
    }
    
    try:
        response = requests.post('http://localhost:8000/api/capture', json=test_request)
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return False
        
        task_id = response.json().get('task_id')
        print(f"✅ 任务: {task_id}")
        
        # 等待流量
        traffic_thread.join(timeout=10)
        
        # 等待完成
        for i in range(30):
            time.sleep(1)
            status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
            if status_response.status_code == 200:
                status = status_response.json().get('status')
                if status == 'done':
                    break
                elif status == 'error':
                    print(f"❌ 失败: {status_response.json().get('error')}")
                    return False
        
        # 获取结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败")
            return False
        
        result = result_response.json().get('result', {})
        enhanced_analysis = result.get('capture_summary', {}).get('enhanced_analysis', {})
        
        # 检查网站性能数据
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        website_performance = issue_insights.get('website_performance', {})
        
        if website_performance:
            print(f"✅ 网站性能数据: {len(website_performance)} 个网站")
            
            has_latency = False
            for host, perf_data in website_performance.items():
                tcp_rtt = perf_data.get('tcp_rtt', {})
                if tcp_rtt.get('avg_ms'):
                    has_latency = True
                    print(f"📊 {host}: {tcp_rtt['avg_ms']}ms")
                else:
                    print(f"📊 {host}: 无时延数据")
            
            if has_latency:
                print("✅ 时延数据修复成功！")
                return True
            else:
                print("❌ 仍然没有时延数据")
                return False
        else:
            print("❌ 没有网站性能数据")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

if __name__ == '__main__':
    success = quick_test()
    if success:
        print("\n🎉 修复验证成功！现在可以显示具体的网站时延数据了。")
    else:
        print("\n❌ 修复验证失败，需要进一步调试。")
    exit(0 if success else 1)
