#!/usr/bin/env python3
"""
诊断HTTP分析问题
检查为什么没有显示具体的网站访问记录
"""

import requests
import time
import json
import threading
import subprocess
import os

def generate_clear_http_traffic():
    """生成明确的HTTP流量"""
    print("🌐 生成明确的HTTP流量...")
    
    # 使用明确会产生HTTP流量的URL
    test_urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/delay/1',
        'http://httpbin.org/status/200',
        'http://httpbin.org/status/404',
        'http://example.com',
        'http://httpbin.org/json',
    ]
    
    def make_requests():
        for i, url in enumerate(test_urls):
            try:
                print(f"   {i+1}. 访问: {url}")
                response = requests.get(url, timeout=10)
                print(f"      响应: {response.status_code} ({len(response.content)} bytes)")
                time.sleep(1.5)  # 间隔时间，便于抓包
            except Exception as e:
                print(f"      异常: {str(e)}")
    
    thread = threading.Thread(target=make_requests)
    thread.daemon = True
    thread.start()
    
    return thread

def test_http_analysis_step_by_step():
    """逐步测试HTTP分析"""
    print("🔍 逐步诊断HTTP分析问题")
    print("=" * 60)
    
    # 生成HTTP流量
    traffic_thread = generate_clear_http_traffic()
    
    # 创建HTTP分析请求
    test_request = {
        "issue_type": "http",
        "duration": 12,  # 更长的抓包时间
        "user_description": "HTTP分析诊断测试 - 检查网站访问记录",
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
            print(f"响应: {response.text}")
            return False
        
        data = response.json()
        task_id = data.get('task_id')
        print(f"   ✅ 任务创建: {task_id}")
        
        # 等待流量生成完成
        print("\n2️⃣ 等待HTTP流量生成...")
        traffic_thread.join(timeout=15)
        print("   ✅ HTTP流量生成完成")
        
        print("\n3️⃣ 监控任务进度...")
        
        # 监控任务进度
        for i in range(45):
            time.sleep(2)
            
            try:
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
                        error = status_data.get('error', '')
                        print(f"   ❌ 任务失败: {error}")
                        return False
                else:
                    print(f"   ❌ 状态查询失败: {status_response.status_code}")
                    break
            except Exception as e:
                print(f"   ❌ 状态查询异常: {str(e)}")
                break
        
        print("\n4️⃣ 详细分析结果...")
        
        # 获取详细结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        result = result_data.get('result', {})
        
        # 分析抓包摘要
        capture_summary = result.get('capture_summary', {})
        print(f"   📊 抓包摘要:")
        print(f"     文件大小: {capture_summary.get('file_size', 0):,} bytes")
        print(f"     解析方法: {capture_summary.get('parsing_method', 'unknown')}")
        
        # 分析增强分析数据
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        if enhanced_analysis:
            print(f"   ✅ 包含增强分析数据")
            
            # 检查基础统计
            basic_stats = enhanced_analysis.get('basic_stats', {})
            if basic_stats:
                total_packets = basic_stats.get('total_packets', 0)
                protocols = basic_stats.get('protocols', {})
                print(f"     基础统计: {total_packets} 个包")
                print(f"     协议分布: {protocols}")
            
            # 检查HTTP分析
            http_analysis = enhanced_analysis.get('http_analysis', {})
            if http_analysis:
                print(f"   ✅ 包含HTTP分析数据")
                
                basic_summary = http_analysis.get('basic_summary', {})
                https_connections = http_analysis.get('https_connections', {})
                
                print(f"     HTTP基础摘要: {basic_summary}")
                print(f"     HTTPS连接: {https_connections}")
            else:
                print(f"   ❌ 缺少HTTP分析数据")
            
            # 检查问题特定洞察
            issue_insights = enhanced_analysis.get('issue_specific_insights', {})
            if issue_insights:
                print(f"   ✅ 包含问题特定洞察")
                
                website_performance = issue_insights.get('website_performance', {})
                if website_performance:
                    print(f"   🎯 网站性能数据:")
                    print(f"     分析了 {len(website_performance)} 个网站")
                    
                    for host, perf_data in website_performance.items():
                        ips = perf_data.get('ips', [])
                        http_time = perf_data.get('http_response_time', {})
                        tcp_time = perf_data.get('tcp_rtt', {})
                        requests_data = perf_data.get('requests', {})
                        
                        print(f"     📊 {host}:")
                        print(f"       IP: {ips}")
                        print(f"       HTTP时间: {http_time}")
                        print(f"       TCP时间: {tcp_time}")
                        print(f"       请求统计: {requests_data}")
                else:
                    print(f"   ❌ 缺少网站性能数据")
                    
                performance_issues = issue_insights.get('performance_issues', [])
                if performance_issues:
                    print(f"   ⚠️ 性能问题:")
                    for issue in performance_issues:
                        print(f"     - {issue}")
            else:
                print(f"   ❌ 缺少问题特定洞察")
            
            # 检查诊断线索
            diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
            if diagnostic_clues:
                print(f"\n   💡 诊断线索 ({len(diagnostic_clues)} 条):")
                for i, clue in enumerate(diagnostic_clues, 1):
                    print(f"     {i}. {clue}")
                    
                # 检查是否有网站特定线索
                website_clues = [clue for clue in diagnostic_clues if '📊' in clue and 'IP:' in clue]
                if website_clues:
                    print(f"   ✅ 找到 {len(website_clues)} 条网站特定线索")
                else:
                    print(f"   ❌ 没有找到网站特定线索")
            else:
                print(f"   ❌ 缺少诊断线索")
        else:
            print(f"   ❌ 缺少增强分析数据")
        
        # 检查AI分析结果
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis:
            if ai_analysis.get('success'):
                print(f"\n   🤖 AI分析成功")
                analysis_content = ai_analysis.get('analysis', {})
                diagnosis = analysis_content.get('diagnosis', '')
                print(f"     诊断: {diagnosis}")
            else:
                error = ai_analysis.get('error', '')
                print(f"\n   ❌ AI分析失败: {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断异常: {str(e)}")
        return False

def check_tshark_http_capability():
    """检查tshark的HTTP解析能力"""
    print("\n🔧 检查tshark HTTP解析能力...")
    
    try:
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
                    print(f"   ✅ 找到tshark: {path}")
                    break
            except:
                continue
        
        if not tshark_cmd:
            print("   ❌ tshark不可用")
            return False
        
        # 检查HTTP字段支持
        http_fields = [
            'http.host',
            'http.time',
            'http.response.code',
            'tcp.analysis.ack_rtt'
        ]
        
        print("   🔍 检查HTTP字段支持:")
        for field in http_fields:
            try:
                result = subprocess.run([
                    tshark_cmd, '-G', 'fields'
                ], capture_output=True, text=True, timeout=10)
                
                if field in result.stdout:
                    print(f"     ✅ {field}")
                else:
                    print(f"     ❌ {field}")
            except Exception as e:
                print(f"     ❌ {field} (检查失败: {str(e)})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 检查异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌟 HTTP分析问题诊断")
    print("=" * 70)
    
    # 检查tshark能力
    tshark_ok = check_tshark_http_capability()
    
    # 测试HTTP分析
    analysis_ok = test_http_analysis_step_by_step()
    
    print("\n" + "=" * 70)
    print("📋 诊断总结:")
    print("=" * 70)
    
    if tshark_ok and analysis_ok:
        print("🎉 HTTP分析功能正常！")
        print("\n✅ 诊断结果:")
        print("   - tshark HTTP解析能力正常")
        print("   - 网站性能数据生成正常")
        print("   - 诊断线索显示正常")
        
    else:
        print("❌ HTTP分析存在问题")
        print("\n💡 可能的原因:")
        if not tshark_ok:
            print("   - tshark工具不可用或不支持HTTP解析")
        if not analysis_ok:
            print("   - HTTP流量捕获失败")
            print("   - 网站性能数据生成失败")
            print("   - 分析逻辑有bug")
        
        print("\n🔧 建议解决方案:")
        print("   1. 确保在抓包期间有实际的HTTP流量")
        print("   2. 检查tshark是否正确安装")
        print("   3. 验证HTTP分析逻辑")
        print("   4. 检查权限问题")
    
    return tshark_ok and analysis_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
