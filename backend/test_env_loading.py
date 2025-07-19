#!/usr/bin/env python3
"""
测试环境变量加载功能
验证从.env.local文件读取配置
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_env_loading():
    """测试环境变量加载"""
    print("🔍 测试环境变量加载功能")
    print("=" * 50)
    
    # 显示当前环境变量状态（加载前）
    print("📋 加载前的环境变量:")
    ai_vars = ['OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'AI_PROVIDER']
    for var in ai_vars:
        value = os.environ.get(var, 'Not Set')
        print(f"  {var}: {value}")
    
    print("\n🔄 导入AI配置模块...")
    
    # 导入AI配置模块（这会触发环境变量加载）
    try:
        from app.config.ai_config import get_ai_config, validate_ai_setup
        print("✅ AI配置模块导入成功")
        
        # 显示加载后的环境变量
        print("\n📋 加载后的环境变量:")
        for var in ai_vars:
            value = os.environ.get(var, 'Not Set')
            # 隐藏API密钥的敏感部分
            if 'API_KEY' in var and value != 'Not Set' and len(value) > 10:
                display_value = value[:8] + '...' + value[-4:]
            else:
                display_value = value
            print(f"  {var}: {display_value}")
        
        # 测试AI配置
        print("\n🤖 测试AI配置:")
        ai_config = get_ai_config()
        
        # 显示当前提供商
        print(f"  当前提供商: {ai_config.current_provider}")
        
        # 显示可用提供商
        available_providers = ai_config.list_available_providers()
        print(f"  可用提供商: {available_providers}")
        
        # 验证配置
        is_valid = validate_ai_setup()
        print(f"  配置验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        # 显示当前配置详情
        current_config = ai_config.get_current_config()
        if current_config:
            print(f"  配置详情:")
            print(f"    - 名称: {current_config.name}")
            print(f"    - 模型: {current_config.model}")
            print(f"    - 基础URL: {current_config.base_url}")
            print(f"    - 超时: {current_config.timeout}秒")
            print(f"    - 最大Token: {current_config.max_tokens}")
        else:
            print("  ⚠️ 当前配置无效")
        
        return True
        
    except Exception as e:
        print(f"❌ AI配置模块导入失败: {str(e)}")
        return False

def test_env_file_detection():
    """测试环境文件检测"""
    print("\n🔍 测试环境文件检测")
    print("=" * 50)
    
    from pathlib import Path
    
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    env_files = [
        project_root / '.env.local',
        project_root / '.env',
        current_dir / '.env.local',
        current_dir / '.env'
    ]
    
    print("📁 检查环境文件:")
    found_files = []
    for env_file in env_files:
        exists = env_file.exists()
        status = "✅ 存在" if exists else "❌ 不存在"
        print(f"  {env_file}: {status}")
        if exists:
            found_files.append(env_file)
            # 显示文件大小
            size = env_file.stat().st_size
            print(f"    文件大小: {size} bytes")
    
    if found_files:
        print(f"\n💡 找到 {len(found_files)} 个环境文件")
        print(f"优先使用: {found_files[0]}")
    else:
        print("\n⚠️ 未找到任何环境文件")
        print("💡 请创建 .env.local 文件并添加AI API密钥")

def suggest_configuration():
    """建议配置方案"""
    print("\n💡 配置建议")
    print("=" * 50)
    
    print("1. 创建 .env.local 文件:")
    print("   cp .env.example .env.local")
    
    print("\n2. 编辑 .env.local 文件，添加您的API密钥:")
    print("   # OpenRouter (推荐)")
    print("   OPENROUTER_API_KEY=your-actual-api-key")
    print("   AI_PROVIDER=openrouter")
    
    print("\n3. 或者使用其他AI服务:")
    print("   # OpenAI")
    print("   OPENAI_API_KEY=your-openai-key")
    print("   AI_PROVIDER=openai")
    
    print("\n4. 重启后端服务以应用新配置")

def main():
    """主函数"""
    print("🌟 环境变量加载测试")
    print("=" * 60)
    
    # 测试环境文件检测
    test_env_file_detection()
    
    # 测试环境变量加载
    success = test_env_loading()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print("=" * 60)
    
    if success:
        print("✅ 环境变量加载功能正常")
        
        # 检查是否有有效的AI配置
        from app.config.ai_config import validate_ai_setup
        if validate_ai_setup():
            print("🎉 AI配置完整，可以使用AI分析功能")
        else:
            print("⚠️ AI配置不完整，AI分析功能将不可用")
            suggest_configuration()
    else:
        print("❌ 环境变量加载功能异常")
        suggest_configuration()
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
