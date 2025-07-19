#!/usr/bin/env python3
"""
测试HTTP流量分析功能
验证网站访问请求的分析效果
"""

import requests
import time
import json
import subprocess
import threading

def generate_http_traffic():
    """生成一些HTTP流量用于测试"""
    print("🌐 生成HTTP测试流量...")
    
    # 创建一些HTTP请求来生成流量
    test_urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/post',
        'http://httpbin.org/status/404',
        'http://httpbin.org/status/500',
        'http://httpbin.org/delay/2',
    ]
    
    def make_requests():
        for url in test_urls:
            try:
                if 'post' in url:
                    requests.post(url, json={'test': 'data'}, timeout=5)
                else:
                    requests.get(url, timeout=5)
                time.sleep(0.5)
            except:
                pass  # 忽略错误，我们只是想生成流量
    
    # 在后台线程中生成流量
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    
    return thread

def test_http_analysis():
    """测试HTTP分析功能"""
    print("🔍 测试HTTP流量分析功能")
    print("=" * 60)
    
    # 生成一些HTTP流量
    traffic_thread = generate_http_traffic()
    
    # 创建HTTP问题类型的测试请求
    test_request = {
        "issue_type": "http",
        "duration": 5,  # 较长的抓包时间以捕获HTTP流量
        "user_description": "HTTP网站访问分析测试 - 检测GET/POST请求",
        "enable_ai_analysis": True
    }
    
    try:
        print("1️⃣ 发送HTTP分析请求...")
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
        traffic_thread.join(timeout=6)
        
        print("\n2️⃣ 等待分析完成...")
        
        # 监控任务进度
        for i in range(30):
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
        
        print("\n3️⃣ 分析HTTP流量数据...")
        
        # 获取结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        result = result_data.get('result', {})
        capture_summary = result.get('capture_summary', {})
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        
        if not enhanced_analysis:
            print("   ❌ 没有增强分析数据")
            return False
        
        # 分析HTTP数据
        http_analysis = enhanced_analysis.get('http_analysis', {})
        if http_analysis:
            print("   ✅ 包含HTTP流量分析")
            
            # HTTP请求分析
            http_requests = http_analysis.get('http_requests', {})
            if http_requests:
                methods = http_requests.get('methods', {})
                hosts = http_requests.get('top_hosts', {})
                uris = http_requests.get('top_uris', {})
                
                print(f"\n   📊 HTTP请求统计:")
                if methods:
                    total_requests = sum(methods.values())
                    print(f"     总请求数: {total_requests}")
                    print(f"     请求方法: {dict(list(methods.items())[:5])}")
                
                if hosts:
                    print(f"     访问主机: {len(hosts)} 个")
                    for host, count in list(hosts.items())[:3]:
                        print(f"       - {host}: {count} 次")
                
                if uris:
                    print(f"     请求路径: {len(uris)} 个不同路径")
            
            # HTTP响应分析
            response_analysis = http_analysis.get('response_analysis', {})
            if response_analysis:
                status_codes = response_analysis.get('status_codes', {})
                if status_codes:
                    print(f"\n   📈 HTTP响应统计:")
                    for code, count in list(status_codes.items())[:5]:
                        status_type = "成功" if code.startswith('2') else "错误" if code.startswith('4') or code.startswith('5') else "其他"
                        print(f"     HTTP {code} ({status_type}): {count} 次")
            
            # HTTPS连接分析
            https_connections = http_analysis.get('https_connections', {})
            if https_connections:
                tls_handshakes = https_connections.get('tls_handshakes', 0)
                server_names = https_connections.get('server_names', {})
                
                print(f"\n   🔒 HTTPS连接统计:")
                print(f"     TLS握手: {tls_handshakes} 次")
                if server_names:
                    print(f"     HTTPS网站: {len(server_names)} 个")
                    for site, count in list(server_names.items())[:3]:
                        print(f"       - {site}: {count} 次")
        
        # 问题特定洞察
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        if issue_insights:
            print(f"\n   🎯 HTTP问题特定分析:")
            
            request_analysis = issue_insights.get('request_analysis', {})
            if request_analysis:
                hosts_accessed = request_analysis.get('hosts_accessed', 0)
                host_details = request_analysis.get('host_details', {})
                
                print(f"     访问的主机数: {hosts_accessed}")
                
                for host, details in list(host_details.items())[:3]:
                    total_req = details.get('total_requests', 0)
                    error_count = details.get('error_count', 0)
                    error_rate = details.get('error_rate_percent', 0)
                    
                    print(f"     {host}:")
                    print(f"       请求数: {total_req}, 错误数: {error_count} ({error_rate}%)")
            
            response_timing = issue_insights.get('response_timing', {})
            if response_timing:
                avg_response = response_timing.get('avg_response_ms', 0)
                slow_requests = response_timing.get('slow_requests', 0)
                
                if avg_response > 0:
                    print(f"     平均响应时间: {avg_response:.1f}ms")
                if slow_requests > 0:
                    print(f"     慢请求数量: {slow_requests} 个")
        
        # 诊断线索
        diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
        if diagnostic_clues:
            print(f"\n   💡 诊断线索 ({len(diagnostic_clues)} 条):")
            for i, clue in enumerate(diagnostic_clues[:8], 1):
                print(f"     {i}. {clue}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_different_http_scenarios():
    """测试不同的HTTP场景"""
    print("\n🔄 测试不同HTTP场景")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "DNS问题场景",
            "issue_type": "dns",
            "description": "DNS解析问题测试"
        },
        {
            "name": "慢连接场景", 
            "issue_type": "slow",
            "description": "网络慢问题测试"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n测试场景: {scenario['name']}")
        
        test_request = {
            "issue_type": scenario["issue_type"],
            "duration": 3,
            "user_description": scenario["description"],
            "enable_ai_analysis": False  # 只测试数据收集
        }
        
        try:
            response = requests.post('http://localhost:8000/api/capture', json=test_request)
            if response.status_code == 200:
                task_id = response.json().get('task_id')
                
                # 等待完成
                for i in range(15):
                    time.sleep(1)
                    status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
                    if status_response.status_code == 200:
                        status = status_response.json().get('status')
                        if status in ['done', 'error']:
                            break
                
                # 检查是否包含HTTP分析
                result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
                if result_response.status_code == 200:
                    result = result_response.json().get('result', {})
                    enhanced_analysis = result.get('capture_summary', {}).get('enhanced_analysis', {})
                    
                    http_analysis = enhanced_analysis.get('http_analysis', {})
                    if http_analysis:
                        http_requests = http_analysis.get('http_requests', {})
                        methods = http_requests.get('methods', {})
                        if methods:
                            total_requests = sum(methods.values())
                            print(f"   ✅ 检测到 {total_requests} 个HTTP请求")
                        else:
                            print(f"   ⚠️ 未检测到HTTP请求")
                    else:
                        print(f"   ❌ 没有HTTP分析数据")
                        
        except Exception as e:
            print(f"   ❌ 场景测试异常: {str(e)}")

def main():
    """主函数"""
    print("🌟 HTTP流量分析功能测试")
    print("=" * 70)
    
    # 测试HTTP分析
    http_ok = test_http_analysis()
    
    # 测试不同场景
    test_different_http_scenarios()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if http_ok:
        print("🎉 HTTP流量分析功能正常工作！")
        print("\n✅ 功能特点:")
        print("   - 详细的HTTP请求方法统计 (GET, POST等)")
        print("   - 访问网站和路径分析")
        print("   - HTTP响应码分布统计")
        print("   - HTTPS连接和TLS握手分析")
        print("   - 响应时间和性能指标")
        print("   - 错误率和问题检测")
        
        print("\n🎯 对网站访问分析的价值:")
        print("   - 识别访问的具体网站和页面")
        print("   - 分析HTTP请求的成功率和错误模式")
        print("   - 检测慢请求和性能问题")
        print("   - 提供网站访问行为的详细洞察")
        print("   - 为AI提供丰富的Web流量上下文")
        
    else:
        print("❌ HTTP流量分析功能异常")
        print("\n💡 可能的原因:")
        print("   - tshark工具不支持HTTP解析")
        print("   - 抓包期间没有HTTP流量")
        print("   - 代码修改未生效")
    
    return http_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
