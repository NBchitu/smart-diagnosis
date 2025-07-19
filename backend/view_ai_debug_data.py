#!/usr/bin/env python3
"""
查看AI分析调试数据工具
用于查看保存的AI分析输入输出数据
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

DEBUG_DIR = Path('/tmp/ai_analysis_debug')

def list_debug_files():
    """列出所有调试文件"""
    if not DEBUG_DIR.exists():
        print(f"调试目录不存在: {DEBUG_DIR}")
        return []
    
    debug_files = list(DEBUG_DIR.glob('ai_analysis_*.json'))
    debug_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return debug_files

def display_file_list(files):
    """显示文件列表"""
    if not files:
        print("📁 没有找到调试文件")
        return
    
    print(f"📁 找到 {len(files)} 个调试文件:")
    print("=" * 80)
    
    for i, file_path in enumerate(files, 1):
        try:
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            
            print(f"{i:2d}. {file_path.name}")
            print(f"    修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    文件大小: {size:,} bytes")
            print()
        except Exception as e:
            print(f"{i:2d}. {file_path.name} (读取信息失败: {e})")

def view_debug_file(file_path):
    """查看调试文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📄 查看文件: {file_path.name}")
        print("=" * 80)
        
        # 显示元数据
        metadata = data.get('metadata', {})
        print("🔍 任务信息:")
        print(f"  任务ID: {metadata.get('task_id', 'N/A')}")
        print(f"  时间戳: {metadata.get('timestamp', 'N/A')}")
        print(f"  问题类型: {metadata.get('issue_type', 'N/A')}")
        print(f"  用户描述: {metadata.get('user_description', 'N/A')}")
        print(f"  AI提供商: {metadata.get('ai_provider', 'N/A')}")
        print(f"  AI模型: {metadata.get('ai_model', 'N/A')}")
        
        # 显示输入数据摘要
        input_data = data.get('input_data', {})
        print(f"\n📥 输入数据:")
        print(f"  Prompt长度: {input_data.get('prompt_length', 0):,} 字符")
        
        capture_summary = input_data.get('capture_summary', {})
        if capture_summary:
            stats = capture_summary.get('statistics', {})
            print(f"  抓包统计:")
            print(f"    总包数: {stats.get('total_packets', 'N/A')}")
            print(f"    文件大小: {capture_summary.get('file_size', 0):,} bytes")
            print(f"    协议数量: {len(stats.get('protocols', {}))}")
        
        # 显示输出数据摘要
        output_data = data.get('output_data', {})
        print(f"\n📤 输出数据:")
        print(f"  AI响应长度: {output_data.get('ai_response_length', 0):,} 字符")
        
        ai_response = output_data.get('ai_response', '')
        if ai_response:
            if ai_response.startswith('ERROR:'):
                print(f"  ❌ 错误: {ai_response}")
            else:
                print(f"  ✅ AI响应: {ai_response[:200]}...")
        
        return data
        
    except Exception as e:
        print(f"❌ 读取文件失败: {str(e)}")
        return None

def view_prompt_content(data):
    """查看完整的prompt内容"""
    if not data:
        return
    
    input_data = data.get('input_data', {})
    prompt = input_data.get('prompt_content', '')
    
    if not prompt:
        print("❌ 没有找到prompt内容")
        return
    
    print("\n" + "=" * 80)
    print("📝 完整Prompt内容:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)

def view_ai_response(data):
    """查看完整的AI响应"""
    if not data:
        return
    
    output_data = data.get('output_data', {})
    ai_response = output_data.get('ai_response', '')
    
    if not ai_response:
        print("❌ 没有找到AI响应")
        return
    
    print("\n" + "=" * 80)
    print("🤖 完整AI响应:")
    print("=" * 80)
    print(ai_response)
    print("=" * 80)

def view_capture_data(data):
    """查看抓包数据详情"""
    if not data:
        return
    
    input_data = data.get('input_data', {})
    capture_summary = input_data.get('capture_summary', {})
    
    if not capture_summary:
        print("❌ 没有找到抓包数据")
        return
    
    print("\n" + "=" * 80)
    print("📊 抓包数据详情:")
    print("=" * 80)
    print(json.dumps(capture_summary, indent=2, ensure_ascii=False))
    print("=" * 80)

def interactive_mode():
    """交互模式"""
    while True:
        print("\n🌟 AI分析调试数据查看器")
        print("=" * 50)
        
        files = list_debug_files()
        display_file_list(files)
        
        if not files:
            break
        
        try:
            choice = input(f"\n请选择文件 (1-{len(files)}) 或输入 'q' 退出: ").strip()
            
            if choice.lower() == 'q':
                break
            
            file_index = int(choice) - 1
            if 0 <= file_index < len(files):
                selected_file = files[file_index]
                data = view_debug_file(selected_file)
                
                if data:
                    while True:
                        print(f"\n📋 文件操作菜单:")
                        print("1. 查看完整Prompt")
                        print("2. 查看完整AI响应")
                        print("3. 查看抓包数据详情")
                        print("4. 返回文件列表")
                        
                        sub_choice = input("请选择操作 (1-4): ").strip()
                        
                        if sub_choice == '1':
                            view_prompt_content(data)
                        elif sub_choice == '2':
                            view_ai_response(data)
                        elif sub_choice == '3':
                            view_capture_data(data)
                        elif sub_choice == '4':
                            break
                        else:
                            print("❌ 无效选择")
            else:
                print("❌ 无效的文件编号")
                
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 退出程序")
            break

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == 'list':
            files = list_debug_files()
            display_file_list(files)
        elif sys.argv[1] == 'latest':
            files = list_debug_files()
            if files:
                print("📄 查看最新文件:")
                view_debug_file(files[0])
            else:
                print("❌ 没有找到调试文件")
        elif sys.argv[1] == 'clean':
            files = list_debug_files()
            if files:
                for file_path in files:
                    file_path.unlink()
                print(f"🗑️ 已删除 {len(files)} 个调试文件")
            else:
                print("📁 没有文件需要清理")
        else:
            print("用法:")
            print("  python view_ai_debug_data.py          # 交互模式")
            print("  python view_ai_debug_data.py list     # 列出所有文件")
            print("  python view_ai_debug_data.py latest   # 查看最新文件")
            print("  python view_ai_debug_data.py clean    # 清理所有文件")
    else:
        # 交互模式
        interactive_mode()

if __name__ == '__main__':
    main()
