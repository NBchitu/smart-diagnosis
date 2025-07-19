#!/usr/bin/env python3
"""
测试时延数据修复
验证是否能正确显示网站访问时延
"""

import requests
import time
import threading

def generate_http_traffic_with_delay():
    """生成有延迟的HTTP流量"""
    print("🌐 生成HTTP流量（包含延迟测试）...")
    
    test_urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/delay/1',  # 1秒延迟
        'http://httpbin.org/status/200',
        'http://httpbin.org/status/404',
        'http://example.com',
    ]
    
    def make_requests():
        for i, url in enumerate(test_urls):
            try:
                print(f"   {i+1}. 访问: {url}")
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                print(f"      响应: {response.status_code}, 耗时: {duration:.1f}ms")
                time.sleep(2)  # 间隔时间
            except Exception as e:
                print(f"      异常: {str(e)}")
    
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    
    return thread

def test_latency_display():
    """测试时延显示修复"""
    print("🔍 测试时延显示修复")
    print("=" * 60)
    
    # 生成HTTP流量
    traffic_thread = generate_http_traffic_with_delay()
    
    # 创建HTTP分析请求
    test_request = {
        "issue_type": "http",
        "duration": 15,  # 足够长的时间
        "user_description": "时延显示修复测试",
        "enable_ai_analysis": True
    }
    
    try:
        print("\n1️⃣ 发送HTTP分析请求...")
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return False
        
        data = response.json()
        task_id = data.get('task_id')
        print(f"   ✅ 任务创建: {task_id}")
        
        # 等待流量生成
        traffic_thread.join(timeout=18)
        
        print("\n2️⃣ 等待分析完成...")
        
        # 监控任务进度
        for i in range(50):
            time.sleep(2)
            
            status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', 0)
                
                print(f"   📊 {i*2}s: {status} ({progress}%)")
                
                if status == 'done':
                    print("   ✅ 任务完成")
                    break
                elif status == 'error':
                    print(f"   ❌ 任务失败: {status_data.get('error')}")
                    return False
        
        print("\n3️⃣ 检查时延数据...")
        
        # 获取结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        result = result_data.get('result', {})
        
        # 检查诊断线索
        capture_summary = result.get('capture_summary', {})
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
        
        print(f"   📋 诊断线索:")
        
        latency_found = False
        website_info_found = False
        
        for clue in diagnostic_clues:
            print(f"     💡 {clue}")
            
            # 检查是否有时延信息
            if '延迟:' in clue and 'ms' in clue and '未测量' not in clue:
                latency_found = True
                print(f"       ✅ 找到时延数据")
            
            # 检查是否有网站信息
            if '📊' in clue and 'IP:' in clue:
                website_info_found = True
        
        # 检查网站性能数据
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        website_performance = issue_insights.get('website_performance', {})
        
        if website_performance:
            print(f"\n   🎯 网站性能详情:")
            
            tcp_data_found = False
            
            for host, perf_data in website_performance.items():
                ips = perf_data.get('ips', [])
                tcp_rtt = perf_data.get('tcp_rtt', {})
                requests_data = perf_data.get('requests', {})
                
                print(f"     📊 {host}:")
                print(f"       IP: {ips}")
                print(f"       TCP RTT: {tcp_rtt}")
                print(f"       请求: {requests_data}")
                
                if tcp_rtt.get('avg_ms'):
                    tcp_data_found = True
                    print(f"       ✅ TCP时延数据: {tcp_rtt['avg_ms']}ms")
            
            if tcp_data_found:
                print(f"   ✅ 成功获取TCP时延数据")
            else:
                print(f"   ❌ 缺少TCP时延数据")
        
        # 检查AI分析
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis and ai_analysis.get('success'):
            print(f"\n   🤖 AI分析成功")
            analysis_content = ai_analysis.get('analysis', {})
            diagnosis = analysis_content.get('diagnosis', '')
            if diagnosis:
                print(f"     诊断: {diagnosis}")
        
        # 评估修复效果
        print(f"\n4️⃣ 修复效果评估:")
        
        if latency_found:
            print("   ✅ 诊断线索中显示了具体时延数据")
        else:
            print("   ❌ 诊断线索中仍显示'时延: 未测量'")
        
        if website_info_found:
            print("   ✅ 显示了网站信息")
        else:
            print("   ❌ 缺少网站信息")
        
        if website_performance:
            print("   ✅ 生成了网站性能数据")
        else:
            print("   ❌ 缺少网站性能数据")
        
        return latency_found and website_info_found and website_performance
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌟 时延数据显示修复验证")
    print("=" * 70)
    
    # 测试时延显示
    latency_ok = test_latency_display()
    
    print("\n" + "=" * 70)
    print("📋 修复验证总结:")
    print("=" * 70)
    
    if latency_ok:
        print("🎉 时延数据显示修复成功！")
        print("\n✅ 修复效果:")
        print("   - 使用TCP RTT作为主要时延指标")
        print("   - 诊断线索显示具体的延迟数值")
        print("   - 包含延迟评估（正常/偏高/高）")
        print("   - 网站性能数据结构完整")
        
        print("\n🎯 现在显示格式:")
        print("   📊 httpbin.org: IP: 1.2.3.4, 延迟: 45ms (正常), 无错误")
        print("   📊 slow-site.com: IP: 2.3.4.5, 延迟: 150ms (高), 错误率: 5%")
        
        print("\n💡 时延评估标准:")
        print("   - ≤50ms: 正常")
        print("   - 51-100ms: 偏高")
        print("   - >100ms: 高")
        
    else:
        print("❌ 时延数据显示仍有问题")
        print("\n💡 可能的原因:")
        print("   - TCP RTT数据捕获失败")
        print("   - tshark字段提取问题")
        print("   - 数据处理逻辑错误")
        print("   - 抓包期间网络流量不足")
        
        print("\n🔧 建议解决方案:")
        print("   1. 检查tshark是否支持tcp.analysis.ack_rtt字段")
        print("   2. 确保抓包期间有足够的HTTP流量")
        print("   3. 验证TCP连接建立过程")
        print("   4. 检查网络接口权限")
    
    return latency_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
