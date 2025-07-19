#!/usr/bin/env python3
"""
测试网站信息显示修复
验证是否能看到具体的网站性能信息
"""

import requests
import time
import json
import threading

def generate_website_traffic():
    """生成网站访问流量"""
    print("🌐 生成网站访问流量...")
    
    # 访问一些真实网站来生成有意义的流量
    test_urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/delay/1',
        'http://httpbin.org/status/200',
        'http://httpbin.org/status/404',
        'http://example.com',
    ]
    
    def make_requests():
        for url in test_urls:
            try:
                print(f"   访问: {url}")
                response = requests.get(url, timeout=8)
                print(f"   响应: {response.status_code}")
                time.sleep(1)
            except Exception as e:
                print(f"   请求异常: {url} - {str(e)}")
    
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    
    return thread

def test_website_info_display():
    """测试网站信息显示"""
    print("🔍 测试网站信息显示修复")
    print("=" * 60)
    
    # 生成网站访问流量
    traffic_thread = generate_website_traffic()
    
    # 创建HTTP问题类型的测试请求
    test_request = {
        "issue_type": "http",
        "duration": 10,  # 足够长的时间捕获流量
        "user_description": "网站访问问题 - 测试具体网站信息显示",
        "enable_ai_analysis": True
    }
    
    try:
        print("\n1️⃣ 发送网站分析请求...")
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
        traffic_thread.join(timeout=12)
        
        print("\n2️⃣ 等待分析完成...")
        
        # 监控任务进度
        for i in range(40):
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
        
        print("\n3️⃣ 检查网站信息显示...")
        
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
        
        print(f"   📋 诊断线索数量: {len(diagnostic_clues)}")
        
        # 检查是否包含具体网站信息
        website_info_found = False
        method_distribution_found = False
        
        for clue in diagnostic_clues:
            print(f"   💡 {clue}")
            
            # 检查是否有具体网站信息（域名-IP-时延格式）
            if '📊' in clue and (':' in clue and ('IP:' in clue or 'HTTP:' in clue or 'TCP:' in clue)):
                website_info_found = True
                print(f"     ✅ 找到具体网站信息")
            
            # 检查是否还有旧的HTTP方法分布
            if 'HTTP方法分布' in clue:
                method_distribution_found = True
                print(f"     ❌ 仍显示HTTP方法分布（应该移除）")
        
        # 检查问题特定洞察
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        website_performance = issue_insights.get('website_performance', {})
        
        if website_performance:
            print(f"\n   🎯 网站性能数据:")
            print(f"     分析了 {len(website_performance)} 个网站")
            
            for host, perf_data in list(website_performance.items())[:3]:
                ips = perf_data.get('ips', [])
                http_time = perf_data.get('http_response_time', {})
                tcp_time = perf_data.get('tcp_rtt', {})
                requests_data = perf_data.get('requests', {})
                
                print(f"     📊 {host}:")
                if ips:
                    print(f"       IP: {', '.join(ips)}")
                if http_time.get('avg_ms'):
                    print(f"       HTTP响应: {http_time['avg_ms']}ms")
                if tcp_time.get('avg_ms'):
                    print(f"       TCP RTT: {tcp_time['avg_ms']}ms")
                if requests_data.get('total'):
                    error_rate = requests_data.get('error_rate_percent', 0)
                    print(f"       请求: {requests_data['total']}个, 错误率: {error_rate}%")
        
        # 检查AI分析结果
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis and ai_analysis.get('success'):
            print(f"\n   🤖 AI分析成功")
            analysis_content = ai_analysis.get('analysis', {})
            diagnosis = analysis_content.get('diagnosis', '')
            if diagnosis:
                print(f"     诊断: {diagnosis}")
        
        # 评估修复效果
        print(f"\n4️⃣ 修复效果评估:")
        
        if website_info_found:
            print("   ✅ 成功显示具体网站信息（域名-IP-时延）")
        else:
            print("   ❌ 未找到具体网站信息")
        
        if not method_distribution_found:
            print("   ✅ 成功移除HTTP方法分布显示")
        else:
            print("   ❌ 仍在显示HTTP方法分布")
        
        if website_performance:
            print("   ✅ 网站性能数据结构正确")
        else:
            print("   ❌ 缺少网站性能数据")
        
        return website_info_found and not method_distribution_found and website_performance
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def check_debug_data():
    """检查调试数据中的网站信息"""
    print("\n🔍 检查调试数据...")
    
    try:
        import os
        from pathlib import Path
        
        debug_dir = Path('/tmp/ai_analysis_debug')
        if not debug_dir.exists():
            print("   ❌ 调试目录不存在")
            return False
        
        debug_files = list(debug_dir.glob('ai_analysis_*.json'))
        if not debug_files:
            print("   ❌ 没有调试文件")
            return False
        
        # 获取最新文件
        latest_file = max(debug_files, key=lambda x: x.stat().st_mtime)
        print(f"   📄 检查文件: {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            debug_data = json.load(f)
        
        # 检查输入数据中的网站性能信息
        input_data = debug_data.get('input_data', {})
        capture_summary = input_data.get('capture_summary', {})
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        website_performance = issue_insights.get('website_performance', {})
        
        if website_performance:
            print(f"   ✅ 调试数据包含 {len(website_performance)} 个网站的性能数据")
            for host in list(website_performance.keys())[:3]:
                print(f"     - {host}")
        else:
            print("   ❌ 调试数据中缺少网站性能信息")
        
        # 检查诊断线索
        diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
        website_clues = [clue for clue in diagnostic_clues if '📊' in clue and 'IP:' in clue]
        
        if website_clues:
            print(f"   ✅ 找到 {len(website_clues)} 条网站特定线索")
            for clue in website_clues[:2]:
                print(f"     💡 {clue}")
        else:
            print("   ❌ 没有找到网站特定线索")
        
        return website_performance and website_clues
        
    except Exception as e:
        print(f"   ❌ 检查调试数据异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌟 网站信息显示修复验证")
    print("=" * 70)
    
    # 测试网站信息显示
    display_ok = test_website_info_display()
    
    # 检查调试数据
    debug_ok = check_debug_data()
    
    print("\n" + "=" * 70)
    print("📋 修复验证总结:")
    print("=" * 70)
    
    if display_ok and debug_ok:
        print("🎉 网站信息显示修复成功！")
        print("\n✅ 修复效果:")
        print("   - 移除了无关的HTTP方法分布显示")
        print("   - 显示具体的网站性能信息")
        print("   - 包含域名-IP-时延关联数据")
        print("   - 诊断线索聚焦于网站性能")
        
        print("\n🎯 现在显示的信息:")
        print("   - 📊 具体网站: IP地址, HTTP时延, TCP时延, 错误率")
        print("   - 🐌 性能问题: 直接定位到慢网站")
        print("   - 📡 网络问题: 区分TCP和HTTP延迟")
        print("   - ❌ 错误问题: 按网站分组的错误统计")
        
    else:
        print("❌ 网站信息显示仍有问题")
        print("\n💡 可能的原因:")
        if not display_ok:
            print("   - 诊断线索生成逻辑未正确更新")
        if not debug_ok:
            print("   - 网站性能数据收集有问题")
        print("   - 代码修改未完全生效")
    
    return display_ok and debug_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
