#!/usr/bin/env python3
"""
测试AI调试数据保存功能
验证调试数据是否正确保存到文件
"""

import requests
import time
import json
import os
from pathlib import Path

DEBUG_DIR = Path('/tmp/ai_analysis_debug')

def test_debug_data_saving():
    """测试调试数据保存功能"""
    print("🔍 测试AI调试数据保存功能")
    print("=" * 60)
    
    # 清理旧的调试文件
    if DEBUG_DIR.exists():
        old_files = list(DEBUG_DIR.glob('ai_analysis_*.json'))
        for f in old_files:
            f.unlink()
        print(f"🗑️ 清理了 {len(old_files)} 个旧调试文件")
    
    # 创建测试请求
    test_request = {
        "issue_type": "dns",
        "duration": 2,
        "user_description": "调试数据保存测试 - DNS解析问题",
        "enable_ai_analysis": True
    }
    
    try:
        print("\n1️⃣ 发送抓包请求...")
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
                    break
        
        print("\n3️⃣ 检查调试文件...")
        
        # 检查是否生成了调试文件
        debug_files = list(DEBUG_DIR.glob('ai_analysis_*.json'))
        
        if not debug_files:
            print("   ❌ 没有找到调试文件")
            return False
        
        print(f"   ✅ 找到 {len(debug_files)} 个调试文件")
        
        # 查看最新的调试文件
        latest_file = max(debug_files, key=lambda x: x.stat().st_mtime)
        print(f"   📄 最新文件: {latest_file.name}")
        
        # 验证调试文件内容
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                debug_data = json.load(f)
            
            print("\n4️⃣ 验证调试文件内容...")
            
            # 检查必要字段
            required_sections = ['metadata', 'input_data', 'output_data']
            for section in required_sections:
                if section in debug_data:
                    print(f"   ✅ {section} 部分存在")
                else:
                    print(f"   ❌ {section} 部分缺失")
                    return False
            
            # 检查元数据
            metadata = debug_data['metadata']
            print(f"   📋 任务ID: {metadata.get('task_id', 'N/A')}")
            print(f"   📋 问题类型: {metadata.get('issue_type', 'N/A')}")
            print(f"   📋 AI提供商: {metadata.get('ai_provider', 'N/A')}")
            
            # 检查输入数据
            input_data = debug_data['input_data']
            prompt_length = input_data.get('prompt_length', 0)
            print(f"   📥 Prompt长度: {prompt_length:,} 字符")
            
            if prompt_length > 0:
                print("   ✅ Prompt内容已保存")
            else:
                print("   ❌ Prompt内容为空")
                return False
            
            # 检查输出数据
            output_data = debug_data['output_data']
            ai_response = output_data.get('ai_response', '')
            ai_response_length = output_data.get('ai_response_length', 0)
            
            print(f"   📤 AI响应长度: {ai_response_length:,} 字符")
            
            if ai_response:
                if ai_response.startswith('ERROR:'):
                    print(f"   ⚠️ AI分析失败: {ai_response}")
                else:
                    print("   ✅ AI响应已保存")
            else:
                print("   ❌ AI响应为空")
            
            # 显示部分内容预览
            print("\n5️⃣ 内容预览...")
            
            capture_summary = input_data.get('capture_summary', {})
            if capture_summary:
                stats = capture_summary.get('statistics', {})
                print(f"   📊 抓包统计: {stats.get('total_packets', 0)} 个包")
            
            prompt_content = input_data.get('prompt_content', '')
            if prompt_content:
                print(f"   📝 Prompt预览: {prompt_content[:200]}...")
            
            if ai_response and not ai_response.startswith('ERROR:'):
                print(f"   🤖 AI响应预览: {ai_response[:200]}...")
            
            print(f"\n✅ 调试文件验证通过: {latest_file}")
            return True
            
        except Exception as e:
            print(f"   ❌ 读取调试文件失败: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n💡 使用调试功能的方法:")
    print("=" * 60)
    
    print("1. 查看所有调试文件:")
    print("   python view_ai_debug_data.py list")
    
    print("\n2. 查看最新的调试文件:")
    print("   python view_ai_debug_data.py latest")
    
    print("\n3. 交互式查看:")
    print("   python view_ai_debug_data.py")
    
    print("\n4. 清理调试文件:")
    print("   python view_ai_debug_data.py clean")
    
    print(f"\n📁 调试文件保存位置: {DEBUG_DIR}")
    
    print("\n📋 调试文件包含的信息:")
    print("   - 任务元数据（ID、时间、问题类型等）")
    print("   - 抓包数据摘要")
    print("   - 完整的AI分析Prompt")
    print("   - AI模型的完整响应")
    print("   - 错误信息（如果有）")

def main():
    """主函数"""
    print("🌟 AI调试数据保存功能测试")
    print("=" * 70)
    
    # 测试调试数据保存
    success = test_debug_data_saving()
    
    print("\n" + "=" * 70)
    print("📋 测试总结:")
    print("=" * 70)
    
    if success:
        print("🎉 调试数据保存功能正常！")
        print("\n✅ 功能特点:")
        print("   - 自动保存每次AI分析的输入输出数据")
        print("   - 包含完整的Prompt和AI响应")
        print("   - 保存任务元数据和抓包统计")
        print("   - 支持错误情况的调试信息")
        
        show_usage_examples()
        
    else:
        print("❌ 调试数据保存功能异常")
        print("\n💡 可能的原因:")
        print("   - 后端服务未运行")
        print("   - AI配置问题")
        print("   - 文件权限问题")
        print("   - 代码修改未生效")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
