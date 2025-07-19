#!/usr/bin/env python3
"""
测试聚焦的HTTP分析功能
验证域名-IP-响应时延关联分析
"""

import requests
import time
import json
import threading

def generate_focused_http_traffic():
    """生成聚焦的HTTP测试流量"""
    print("🌐 生成聚焦的HTTP测试流量...")
    
    # 访问不同的网站来生成有意义的流量
    test_sites = [
        'http://httpbin.org/delay/1',    # 1秒延迟
        'http://httpbin.org/delay/2',    # 2秒延迟  
        'http://httpbin.org/status/200', # 正常响应
        'http://httpbin.org/status/404', # 404错误
        'http://httpbin.org/status/500', # 500错误
        'http://httpbin.org/get',        # 正常GET
    ]
    
    def make_test_requests():
        for url in test_sites:
            try:
                print(f"   访问: {url}")
                requests.get(url, timeout=10)
                time.sleep(0.5)
            except Exception as e:
                print(f"   请求失败: {url} - {str(e)}")
    
    # 在后台线程中生成流量
    thread = threading.Thread(target=make_test_requests)
    thread.daemon = True
    thread.start()
    
    return thread

def test_focused_http_analysis():
    """测试聚焦的HTTP分析功能"""
    print("🎯 测试聚焦的HTTP分析功能")
    print("=" * 60)
    
    # 生成测试流量
    traffic_thread = generate_focused_http_traffic()
    
    # 创建HTTP问题类型的测试请求
    test_request = {
        "issue_type": "http",
        "duration": 8,  # 足够的时间捕获HTTP流量
        "user_description": "聚焦HTTP分析测试 - 域名IP时延关联",
        "enable_ai_analysis": True
    }
    
    try:
        print("\n1️⃣ 发送聚焦HTTP分析请求...")
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
        
        # 等待流量生成完成
        traffic_thread.join(timeout=10)
        
        print("\n2️⃣ 等待分析完成...")
        
        # 监控任务进度
        for i in range(35):
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
        
        print("\n3️⃣ 分析聚焦的HTTP数据...")
        
        # 获取结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        result = result_data.get('result', {})
        
        # 检查AI分析结果
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis and ai_analysis.get('success'):
            print("   ✅ AI分析成功完成")
            analysis_content = ai_analysis.get('analysis', {})
            diagnosis = analysis_content.get('diagnosis', '')
            if diagnosis:
                print(f"   🤖 AI诊断: {diagnosis[:200]}...")
        
        # 分析聚焦的HTTP数据
        capture_summary = result.get('capture_summary', {})
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        
        if not enhanced_analysis:
            print("   ❌ 没有增强分析数据")
            return False
        
        # 检查问题特定洞察
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        if issue_insights:
            print("   ✅ 包含HTTP问题特定分析")
            
            # 网站性能数据 - 核心关注点
            website_performance = issue_insights.get('website_performance', {})
            if website_performance:
                print(f"\n   🎯 网站性能分析 (域名-IP-时延关联):")
                print(f"   分析了 {len(website_performance)} 个网站")
                
                for host, perf_data in website_performance.items():
                    print(f"\n   📊 {host}:")
                    
                    # IP地址
                    ips = perf_data.get('ips', [])
                    if ips:
                        print(f"     IP地址: {', '.join(ips)}")
                    
                    # HTTP响应时间
                    http_time = perf_data.get('http_response_time', {})
                    if http_time:
                        avg_ms = http_time.get('avg_ms', 0)
                        max_ms = http_time.get('max_ms', 0)
                        samples = http_time.get('samples', 0)
                        print(f"     HTTP响应时间: 平均{avg_ms}ms, 最大{max_ms}ms ({samples}个样本)")
                    
                    # TCP RTT
                    tcp_time = perf_data.get('tcp_rtt', {})
                    if tcp_time:
                        avg_ms = tcp_time.get('avg_ms', 0)
                        max_ms = tcp_time.get('max_ms', 0)
                        samples = tcp_time.get('samples', 0)
                        print(f"     TCP RTT: 平均{avg_ms}ms, 最大{max_ms}ms ({samples}个样本)")
                    
                    # 请求统计
                    requests_data = perf_data.get('requests', {})
                    if requests_data:
                        total = requests_data.get('total', 0)
                        errors = requests_data.get('errors', 0)
                        error_rate = requests_data.get('error_rate_percent', 0)
                        print(f"     请求统计: {total}个请求, {errors}个错误 ({error_rate}%)")
                        
                        error_codes = requests_data.get('error_codes', {})
                        if error_codes:
                            print(f"     错误详情: {error_codes}")
                    
                    # 访问时长
                    duration = perf_data.get('access_duration_seconds')
                    if duration is not None:
                        print(f"     访问时长: {duration}秒")
            
            # 性能问题列表
            performance_issues = issue_insights.get('performance_issues', [])
            if performance_issues:
                print(f"\n   ⚠️ 检测到的性能问题:")
                for i, issue in enumerate(performance_issues, 1):
                    print(f"     {i}. {issue}")
            else:
                print(f"\n   ✅ 未检测到明显的性能问题")
            
            # 响应摘要
            response_summary = issue_insights.get('response_summary', {})
            if response_summary:
                websites = response_summary.get('websites_accessed', 0)
                total_req = response_summary.get('total_requests', 0)
                total_err = response_summary.get('total_errors', 0)
                error_rate = response_summary.get('overall_error_rate_percent', 0)
                
                print(f"\n   📈 总体摘要:")
                print(f"     访问网站: {websites}个")
                print(f"     总请求数: {total_req}个")
                print(f"     总错误数: {total_err}个")
                print(f"     整体错误率: {error_rate}%")
        
        # 诊断线索
        diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
        if diagnostic_clues:
            print(f"\n   💡 聚焦的诊断线索:")
            for i, clue in enumerate(diagnostic_clues, 1):
                if '🌍' in clue or '📊' in clue or '🐌' in clue or '📡' in clue or '❌' in clue:
                    print(f"     {i}. {clue}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def compare_analysis_focus():
    """对比分析聚焦度"""
    print("\n🔍 分析聚焦度对比")
    print("=" * 60)
    
    print("📊 重构前的HTTP分析:")
    print("   - HTTP方法统计 (GET, POST, PUT...)")
    print("   - 请求URI路径列表")
    print("   - User-Agent统计")
    print("   - 内容类型分布")
    print("   - Cookie和Referer信息")
    print("   - 大文件下载检测")
    print("   ❌ 信息分散，缺乏关联性")
    
    print("\n🎯 重构后的聚焦分析:")
    print("   - 域名 ↔ IP地址映射")
    print("   - 域名 ↔ HTTP响应时间关联")
    print("   - 域名 ↔ TCP RTT关联")
    print("   - 域名 ↔ 错误率关联")
    print("   - 性能问题直接定位到具体网站")
    print("   ✅ 信息聚焦，直接可操作")
    
    print("\n💡 聚焦分析的价值:")
    print("   - 直接回答: '哪个网站慢？'")
    print("   - 直接回答: '慢在哪里？(DNS/TCP/HTTP)'")
    print("   - 直接回答: 'IP地址是否有问题？'")
    print("   - 直接回答: '错误集中在哪个网站？'")

def main():
    """主函数"""
    print("🌟 聚焦HTTP分析功能测试")
    print("=" * 70)
    
    # 测试聚焦分析
    focused_ok = test_focused_http_analysis()
    
    # 对比分析聚焦度
    compare_analysis_focus()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if focused_ok:
        print("🎉 聚焦HTTP分析功能正常工作！")
        print("\n✅ 核心特点:")
        print("   - 域名-IP-时延三元关联分析")
        print("   - 直接定位性能问题到具体网站")
        print("   - 去除无关信息，聚焦核心指标")
        print("   - 提供可操作的诊断线索")
        
        print("\n🎯 分析聚焦度:")
        print("   - 每个网站的IP地址列表")
        print("   - 每个网站的HTTP响应时间统计")
        print("   - 每个网站的TCP RTT统计")
        print("   - 每个网站的错误率和错误类型")
        print("   - 性能问题直接关联到具体域名")
        
        print("\n💡 AI分析价值:")
        print("   - 可以精确回答网站性能问题")
        print("   - 提供具体的优化建议")
        print("   - 支持问题根因分析")
        
    else:
        print("❌ 聚焦HTTP分析功能异常")
        print("\n💡 可能的原因:")
        print("   - 测试流量生成失败")
        print("   - tshark HTTP解析问题")
        print("   - 代码修改未生效")
    
    return focused_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
