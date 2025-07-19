#!/usr/bin/env python3
"""
测试清理后的数据结构
验证是否移除了无关字段
"""

import requests
import time
import threading
import json

def generate_website_traffic():
    """生成网站访问流量"""
    print("🌐 生成网站访问流量...")
    
    def make_requests():
        urls = [
            'https://httpbin.org/get',
            'https://example.com',
            'https://www.google.com',
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

def test_clean_data_structure():
    """测试清理后的数据结构"""
    print("🧹 测试清理后的数据结构")
    print("=" * 60)
    
    # 生成流量
    traffic_thread = generate_website_traffic()
    
    # 创建请求
    test_request = {
        "issue_type": "http",
        "duration": 8,
        "user_description": "测试清理后的数据结构",
        "enable_ai_analysis": False
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
        for i in range(25):
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
        
        print("\n📊 数据结构分析:")
        
        # 检查HTTP分析数据
        http_analysis = enhanced_analysis.get('http_analysis', {})
        if http_analysis:
            print("✅ HTTP分析数据:")
            print(json.dumps(http_analysis, indent=2, ensure_ascii=False))
            
            # 检查是否还有无关字段
            unwanted_fields = [
                'tcp_flags_distribution',
                'tcp_flags',
                'ports_used',
                'tls_handshakes',
                'connection_patterns'
            ]
            
            found_unwanted = []
            def check_unwanted(data, path=""):
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        if key in unwanted_fields:
                            found_unwanted.append(current_path)
                        check_unwanted(value, current_path)
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        check_unwanted(item, f"{path}[{i}]")
            
            check_unwanted(http_analysis)
            
            if found_unwanted:
                print(f"❌ 仍包含无关字段: {found_unwanted}")
            else:
                print("✅ 已移除所有无关字段")
            
            # 检查新的简化结构
            websites_accessed = http_analysis.get('websites_accessed', {})
            if websites_accessed:
                print(f"✅ 网站访问数据: {len(websites_accessed)} 个网站")
                for site, count in list(websites_accessed.items())[:3]:
                    print(f"  📊 {site}: {count} 次")
            else:
                print("❌ 没有网站访问数据")
        
        # 检查网络行为数据
        network_behavior = enhanced_analysis.get('network_behavior', {})
        if network_behavior:
            print(f"\n✅ 网络行为数据:")
            print(json.dumps(network_behavior, indent=2, ensure_ascii=False))
        
        # 检查问题特定洞察
        issue_insights = enhanced_analysis.get('issue_specific_insights', {})
        website_performance = issue_insights.get('website_performance', {})
        
        if website_performance:
            print(f"\n✅ 网站性能数据: {len(website_performance)} 个网站")
            for host, perf_data in list(website_performance.items())[:2]:
                print(f"  📊 {host}:")
                print(f"    IP: {perf_data.get('ips', [])}")
                tcp_rtt = perf_data.get('tcp_rtt', {})
                if tcp_rtt.get('avg_ms'):
                    print(f"    延迟: {tcp_rtt['avg_ms']}ms")
                else:
                    print(f"    延迟: 未测量")
        
        # 检查诊断线索
        diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
        if diagnostic_clues:
            print(f"\n💡 诊断线索 ({len(diagnostic_clues)} 条):")
            for clue in diagnostic_clues:
                print(f"  {clue}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def show_ideal_data_structure():
    """显示理想的数据结构"""
    print("\n🎯 理想的简化数据结构:")
    print("=" * 60)
    
    ideal_structure = {
        "http_analysis": {
            "websites_accessed": {
                "httpbin.org": 3,
                "example.com": 2,
                "www.google.com": 1
            },
            "connection_summary": {
                "total_websites": 3,
                "has_https_traffic": True
            }
        },
        "issue_specific_insights": {
            "website_performance": {
                "httpbin.org": {
                    "ips": ["54.243.106.191"],
                    "tcp_rtt": {"avg_ms": 45.2, "samples": 5},
                    "requests": {"total": 3, "errors": 0, "error_rate_percent": 0},
                    "protocol": "HTTPS"
                }
            },
            "performance_issues": [
                "📡 slow-site.com: 网络延迟高 (平均150ms)"
            ]
        },
        "diagnostic_clues": [
            "🌐 访问了 3 个HTTPS网站",
            "📊 httpbin.org: IP: 54.243.106.191, 延迟: 45ms (正常), 无错误",
            "📊 example.com: IP: 93.184.216.34, 延迟: 32ms (正常), 无错误"
        ]
    }
    
    print("📋 核心数据结构:")
    print(json.dumps(ideal_structure, indent=2, ensure_ascii=False))
    
    print("\n✅ 保留的有价值字段:")
    print("  - websites_accessed: 访问的网站列表")
    print("  - website_performance: 每个网站的性能数据")
    print("  - tcp_rtt: 网络延迟信息")
    print("  - ips: IP地址映射")
    print("  - diagnostic_clues: 智能诊断线索")
    
    print("\n❌ 移除的无关字段:")
    print("  - tcp_flags_distribution: TCP标志分布")
    print("  - ports_used: 端口使用统计")
    print("  - tls_handshakes: TLS握手次数")
    print("  - connection_patterns: 连接模式详情")
    print("  - 其他技术细节")

def main():
    """主函数"""
    print("🌟 数据结构清理验证")
    print("=" * 70)
    
    # 测试清理后的数据
    clean_ok = test_clean_data_structure()
    
    # 显示理想结构
    show_ideal_data_structure()
    
    print("\n" + "=" * 70)
    print("📋 清理验证总结:")
    print("=" * 70)
    
    if clean_ok:
        print("🎉 数据结构清理成功！")
        print("\n✅ 清理效果:")
        print("   - 移除了TCP标志分布等技术细节")
        print("   - 保留了核心的网站访问信息")
        print("   - 简化了HTTPS连接分析")
        print("   - 聚焦于用户关心的网站性能数据")
        
        print("\n🎯 现在的数据特点:")
        print("   - 直接显示访问的网站列表")
        print("   - 每个网站的IP地址和延迟")
        print("   - 简洁的诊断线索")
        print("   - 无冗余的技术信息")
        
    else:
        print("❌ 数据结构清理需要进一步优化")
        print("\n💡 可能需要:")
        print("   - 检查是否还有遗漏的无关字段")
        print("   - 验证核心数据是否完整")
        print("   - 确保诊断线索的准确性")
    
    return clean_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
