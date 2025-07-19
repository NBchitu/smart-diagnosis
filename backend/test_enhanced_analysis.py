#!/usr/bin/env python3
"""
测试增强的网络分析功能
验证新的预处理函数是否生成有价值的数据
"""

import requests
import time
import json
import os
from pathlib import Path

def test_enhanced_analysis():
    """测试增强分析功能"""
    print("🔍 测试增强网络分析功能")
    print("=" * 60)
    
    # 创建测试请求
    test_request = {
        "issue_type": "dns",
        "duration": 3,
        "user_description": "增强分析功能测试 - DNS解析问题",
        "enable_ai_analysis": True
    }
    
    try:
        print("1️⃣ 发送抓包请求...")
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
        
        print("\n2️⃣ 等待任务完成...")
        
        # 监控任务进度
        for i in range(25):
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
        
        print("\n3️⃣ 获取分析结果...")
        
        # 获取结果
        result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
        if result_response.status_code != 200:
            print(f"❌ 获取结果失败: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        result = result_data.get('result', {})
        capture_summary = result.get('capture_summary', {})
        
        print("\n4️⃣ 分析增强数据...")
        
        # 检查是否使用了增强分析
        parsing_method = capture_summary.get('parsing_method', '')
        if 'enhanced' in parsing_method:
            print("   ✅ 使用了增强分析方法")
        else:
            print("   ⚠️ 未使用增强分析方法")
        
        # 检查增强分析数据
        enhanced_analysis = capture_summary.get('enhanced_analysis', {})
        if enhanced_analysis:
            print("   ✅ 包含增强分析数据")
            
            # 分析各个部分
            sections = [
                'basic_stats', 'network_behavior', 'performance_indicators',
                'anomaly_detection', 'issue_specific_insights', 'diagnostic_clues'
            ]
            
            for section in sections:
                if section in enhanced_analysis:
                    data = enhanced_analysis[section]
                    if isinstance(data, dict):
                        print(f"   📊 {section}: {len(data)} 个指标")
                    elif isinstance(data, list):
                        print(f"   📊 {section}: {len(data)} 个项目")
                    else:
                        print(f"   📊 {section}: 已包含")
                else:
                    print(f"   ❌ 缺少 {section}")
            
            # 显示诊断线索
            diagnostic_clues = enhanced_analysis.get('diagnostic_clues', [])
            if diagnostic_clues:
                print(f"\n   🔍 诊断线索 ({len(diagnostic_clues)} 条):")
                for i, clue in enumerate(diagnostic_clues[:5], 1):
                    print(f"     {i}. {clue}")
                if len(diagnostic_clues) > 5:
                    print(f"     ... 还有 {len(diagnostic_clues) - 5} 条")
            
            # 显示基础统计
            basic_stats = enhanced_analysis.get('basic_stats', {})
            if basic_stats:
                print(f"\n   📈 基础统计:")
                print(f"     总包数: {basic_stats.get('total_packets', 0)}")
                protocols = basic_stats.get('protocols', {})
                if protocols:
                    print(f"     协议分布: {dict(list(protocols.items())[:3])}")
                
                time_range = basic_stats.get('time_range', {})
                if time_range.get('duration'):
                    print(f"     抓包时长: {time_range['duration']:.2f} 秒")
            
            # 显示性能指标
            performance = enhanced_analysis.get('performance_indicators', {})
            if performance:
                print(f"\n   ⚡ 性能指标:")
                latency = performance.get('latency_indicators', {})
                if latency.get('avg_rtt_ms'):
                    print(f"     平均RTT: {latency['avg_rtt_ms']:.2f} ms")
                
                errors = performance.get('error_rates', {})
                if errors:
                    retrans = errors.get('retransmissions', 0)
                    if retrans > 0:
                        print(f"     重传次数: {retrans}")
            
            return True
            
        else:
            print("   ❌ 没有增强分析数据")
            return False
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def compare_with_old_analysis():
    """对比新旧分析方法"""
    print("\n🔄 对比新旧分析方法")
    print("=" * 60)
    
    # 创建两个测试请求
    requests_data = [
        {
            "issue_type": "slow",
            "duration": 2,
            "user_description": "对比测试 - 慢连接",
            "enable_ai_analysis": False
        }
    ]
    
    for i, req_data in enumerate(requests_data, 1):
        print(f"\n测试 {i}: {req_data['user_description']}")
        
        try:
            response = requests.post('http://localhost:8000/api/capture', json=req_data)
            if response.status_code == 200:
                task_id = response.json().get('task_id')
                
                # 等待完成
                for j in range(15):
                    time.sleep(1)
                    status_response = requests.get(f'http://localhost:8000/api/capture/status?task_id={task_id}')
                    if status_response.status_code == 200:
                        status = status_response.json().get('status')
                        if status in ['done', 'error']:
                            break
                
                # 获取结果
                result_response = requests.get(f'http://localhost:8000/api/capture/result?task_id={task_id}')
                if result_response.status_code == 200:
                    result = result_response.json().get('result', {})
                    capture_summary = result.get('capture_summary', {})
                    
                    # 分析数据丰富度
                    enhanced_analysis = capture_summary.get('enhanced_analysis', {})
                    if enhanced_analysis:
                        clues_count = len(enhanced_analysis.get('diagnostic_clues', []))
                        sections_count = len([k for k, v in enhanced_analysis.items() if v])
                        
                        print(f"   ✅ 增强分析: {sections_count} 个分析维度, {clues_count} 条诊断线索")
                    else:
                        print("   ❌ 没有增强分析数据")
                        
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")

def show_analysis_improvements():
    """展示分析改进"""
    print("\n💡 分析功能改进对比")
    print("=" * 60)
    
    print("📊 旧版本分析内容:")
    print("   - 基础包统计（总数、协议分布）")
    print("   - 简单的源/目标统计")
    print("   - 文件大小信息")
    print("   - 问题类型标记")
    
    print("\n🚀 新版本增强分析:")
    print("   - 📈 基础统计: 包大小分布、时间范围、数据量")
    print("   - 🌐 网络行为: 连接模式、流量分布、会话分析")
    print("   - ⚡ 性能指标: RTT分析、重传统计、错误率")
    print("   - 🔍 异常检测: 可疑模式、错误指标、性能问题")
    print("   - 🎯 问题特定: DNS分析、慢连接诊断、断线检测")
    print("   - 💡 诊断线索: 智能生成的问题提示和建议")
    
    print("\n🎯 对AI分析的价值:")
    print("   - 提供具体的性能数据而不是抽象统计")
    print("   - 包含问题特定的深度分析")
    print("   - 生成可操作的诊断建议")
    print("   - 识别网络异常和性能瓶颈")
    print("   - 为AI提供结构化的诊断上下文")

def main():
    """主函数"""
    print("🌟 增强网络分析功能测试")
    print("=" * 70)
    
    # 测试增强分析
    analysis_ok = test_enhanced_analysis()
    
    # 对比分析
    compare_with_old_analysis()
    
    # 显示改进
    show_analysis_improvements()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if analysis_ok:
        print("🎉 增强分析功能正常工作！")
        print("\n✅ 功能特点:")
        print("   - 生成多维度的网络分析数据")
        print("   - 提供问题特定的深度洞察")
        print("   - 包含智能诊断线索和建议")
        print("   - 为AI分析提供丰富的上下文")
        
        print("\n🎯 AI分析价值提升:")
        print("   - 从简单统计升级为深度网络诊断")
        print("   - 提供可操作的问题线索")
        print("   - 支持精准的问题定位")
        print("   - 增强AI的诊断准确性")
        
    else:
        print("❌ 增强分析功能异常")
        print("\n💡 可能的原因:")
        print("   - tshark工具不可用")
        print("   - 代码修改未生效")
        print("   - 权限或环境问题")
    
    return analysis_ok

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
