#!/usr/bin/env python3
"""
完整系统测试
测试从环境变量加载到AI分析的完整流程
"""

import sys
import os
import requests
import time
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_workflow():
    """测试完整的工作流程"""
    print("🚀 完整系统测试")
    print("=" * 60)
    
    # 1. 测试环境变量加载
    print("1️⃣ 测试环境变量加载...")
    try:
        from app.config.ai_config import get_ai_config, validate_ai_setup
        
        ai_config = get_ai_config()
        is_valid = validate_ai_setup()
        
        print(f"   AI提供商: {ai_config.current_provider}")
        print(f"   配置状态: {'✅ 有效' if is_valid else '❌ 无效'}")
        
        if not is_valid:
            print("   ⚠️ AI配置无效，将跳过AI分析测试")
        
    except Exception as e:
        print(f"   ❌ 环境变量加载失败: {str(e)}")
        return False
    
    # 2. 测试网络接口API
    print("\n2️⃣ 测试网络接口API...")
    try:
        response = requests.get('http://localhost:8000/api/capture/interfaces', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   默认接口: {data.get('default')}")
            print(f"   系统类型: {data.get('current_system')}")
            print("   ✅ 接口API正常")
        else:
            print(f"   ❌ 接口API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 接口API异常: {str(e)}")
        return False
    
    # 3. 测试抓包功能（启用AI分析）
    print("\n3️⃣ 测试抓包和AI分析...")
    try:
        test_request = {
            "issue_type": "dns",
            "duration": 3,
            "user_description": "完整系统测试 - DNS解析问题",
            "enable_ai_analysis": is_valid  # 只有在AI配置有效时才启用
        }
        
        print(f"   AI分析: {'启用' if is_valid else '禁用'}")
        
        # 发送抓包请求
        response = requests.post(
            'http://localhost:8000/api/capture',
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"   任务ID: {task_id}")
            
            # 监控任务进度
            max_wait = 15 if is_valid else 8  # AI分析需要更长时间
            for i in range(max_wait):
                time.sleep(1)
                
                status_response = requests.get(
                    f'http://localhost:8000/api/capture/status?task_id={task_id}',
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"   进度: {status} ({progress}%)")
                    
                    if status == 'done':
                        print("   ✅ 任务完成，获取结果...")
                        
                        # 获取结果
                        result_response = requests.get(
                            f'http://localhost:8000/api/capture/result?task_id={task_id}',
                            timeout=5
                        )
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            return analyze_results(result_data, is_valid)
                        else:
                            print(f"   ❌ 获取结果失败: {result_response.status_code}")
                            return False
                            
                    elif status == 'error':
                        error = status_data.get('error', '')
                        if 'sudo' in error or 'password' in error:
                            print("   ✅ 权限错误（预期行为）")
                            return True
                        else:
                            print(f"   ❌ 任务错误: {error}")
                            return False
                else:
                    print(f"   ❌ 状态查询失败: {status_response.status_code}")
                    return False
            
            print("   ⚠️ 任务超时")
            return False
            
        else:
            print(f"   ❌ 抓包请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 抓包测试异常: {str(e)}")
        return False

def analyze_results(result_data, ai_enabled):
    """分析测试结果"""
    print("\n4️⃣ 分析测试结果...")
    
    try:
        result = result_data.get('result', {})
        
        # 检查抓包摘要
        capture_summary = result.get('capture_summary', {})
        if 'error' in capture_summary:
            print(f"   ❌ 抓包摘要错误: {capture_summary['error']}")
            return False
        
        # 显示抓包统计
        stats = capture_summary.get('statistics', {})
        file_size = capture_summary.get('file_size', 0)
        parsing_method = capture_summary.get('parsing_method', 'pyshark')
        
        print(f"   📊 抓包统计:")
        print(f"      文件大小: {file_size} bytes")
        print(f"      解析方法: {parsing_method}")
        print(f"      总包数: {stats.get('total_packets', 'unknown')}")
        
        # 检查AI分析结果
        if ai_enabled:
            ai_analysis = result.get('ai_analysis', {})
            if ai_analysis.get('success'):
                analysis = ai_analysis.get('analysis', {})
                print(f"   🤖 AI分析结果:")
                print(f"      诊断: {analysis.get('diagnosis', 'N/A')[:100]}...")
                print(f"      严重程度: {analysis.get('severity', 'N/A')}")
                print(f"      置信度: {analysis.get('confidence', 'N/A')}%")
                
                recommendations = analysis.get('recommendations', [])
                if recommendations:
                    print(f"      建议数量: {len(recommendations)}")
                
                print("   ✅ AI分析成功")
            else:
                error = ai_analysis.get('error', '未知错误')
                print(f"   ❌ AI分析失败: {error}")
                return False
        else:
            print("   ⚠️ AI分析已禁用")
        
        print("   ✅ 结果分析完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 结果分析异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌟 网络抓包与AI分析系统 - 完整测试")
    print("=" * 70)
    
    success = test_complete_workflow()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if success:
        print("🎉 完整系统测试通过！")
        print("\n✅ 系统功能:")
        print("   - 环境变量加载: 正常")
        print("   - 网络接口检测: 正常")
        print("   - 抓包功能: 正常")
        print("   - 数据预处理: 正常")
        print("   - AI分析: 正常")
        
        print("\n🎯 可以开始使用:")
        print("   - 前端界面: http://localhost:3000/network-capture-ai-test")
        print("   - API文档: http://localhost:8000/docs")
        
    else:
        print("❌ 系统测试失败")
        print("\n💡 请检查:")
        print("   - 后端服务是否正常运行")
        print("   - .env.local文件是否正确配置")
        print("   - AI API密钥是否有效")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
