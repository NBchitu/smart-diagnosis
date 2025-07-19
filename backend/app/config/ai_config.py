"""
AI服务配置模块
支持OpenRouter、OpenAI、Anthropic等多种AI提供商
支持从.env.local文件加载环境变量
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_env_file(env_file_path: str = None):
    """加载.env文件中的环境变量"""
    if env_file_path is None:
        # 查找项目根目录下的.env.local或.env文件
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent  # 回到项目根目录

        env_files = [
            project_root / '.env.local',
            project_root / '.env',
            current_dir.parent.parent / '.env.local',  # backend目录下
            current_dir.parent.parent / '.env'
        ]

        logger.info(f"搜索环境变量文件，项目根目录: {project_root}")
        for env_file in env_files:
            logger.info(f"检查文件: {env_file}, 存在: {env_file.exists()}")
            if env_file.exists():
                env_file_path = str(env_file)
                break

    if env_file_path and os.path.exists(env_file_path):
        logger.info(f"加载环境变量文件: {env_file_path}")
        try:
            loaded_vars = []
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        # 强制设置环境变量（覆盖已有的）
                        os.environ[key] = value
                        loaded_vars.append(key)
                        logger.debug(f"设置环境变量: {key} = {'***' if 'API_KEY' in key else value}")

            logger.info(f"环境变量加载完成，共加载 {len(loaded_vars)} 个变量: {loaded_vars}")
        except Exception as e:
            logger.error(f"加载环境变量文件失败: {str(e)}", exc_info=True)
    else:
        logger.warning(f"未找到.env文件，使用系统环境变量。搜索路径: {env_file_path}")

    # 调试：显示关键环境变量状态
    key_vars = ['AI_PROVIDER', 'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL']
    for var in key_vars:
        value = os.getenv(var, 'NOT_SET')
        if 'API_KEY' in var and value != 'NOT_SET':
            logger.info(f"环境变量 {var}: {'***已设置***' if value else '未设置'}")
        else:
            logger.info(f"环境变量 {var}: {value}")

# 在模块加载时自动加载环境变量
load_env_file()

# 临时调试：如果环境变量未设置，使用默认值
if not os.getenv('OPENROUTER_API_KEY'):
    logger.warning("OPENROUTER_API_KEY 未设置，尝试使用.env.local中的值")
    # 这里可以临时设置，但建议通过.env.local文件设置
    default_values = {
        'AI_PROVIDER': 'openrouter',
        'OPENROUTER_API_KEY': 'sk-0yTM8KPelhhqssdxMKZwOU7cTezdB4NG94bSEnHxsltKU0RX',
        'OPENROUTER_BASE_URL': 'https://api.tu-zi.com/v1',
        'OPENROUTER_MODEL': 'claude-3-haiku-20240307'
    }

    for key, value in default_values.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"设置默认环境变量: {key}")

@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    name: str
    base_url: str
    api_key: str
    model: str
    enabled: bool = True
    timeout: int = 30
    max_tokens: int = 4000
    temperature: float = 0.7

class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self):
        self.providers = self._load_providers()
        self.current_provider = os.getenv('AI_PROVIDER', 'openrouter')
        logger.info(f"AI配置管理器初始化完成，当前提供商: {self.current_provider}")

        # 验证当前提供商配置
        current_config = self.get_current_config()
        if current_config:
            logger.info(f"当前AI配置: {current_config.name}, 模型: {current_config.model}")
            logger.info(f"API密钥状态: {'已设置' if current_config.api_key else '未设置'}")
        else:
            logger.error(f"无法获取AI配置，提供商: {self.current_provider}")
    
    def _load_providers(self) -> Dict[str, AIProviderConfig]:
        """加载所有AI提供商配置"""
        return {
            'openrouter': AIProviderConfig(
                name='OpenRouter',
                base_url=os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                api_key=os.getenv('OPENROUTER_API_KEY', ''),
                model=os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3-sonnet'),
                enabled=True
            ),
            'openai': AIProviderConfig(
                name='OpenAI',
                base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
                api_key=os.getenv('OPENAI_API_KEY', ''),
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                enabled=bool(os.getenv('OPENAI_API_KEY'))
            ),
            'anthropic': AIProviderConfig(
                name='Anthropic',
                base_url=os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'),
                api_key=os.getenv('ANTHROPIC_API_KEY', ''),
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                enabled=bool(os.getenv('ANTHROPIC_API_KEY'))
            )
        }
    
    def get_current_config(self) -> Optional[AIProviderConfig]:
        """获取当前AI提供商配置"""
        if self.current_provider not in self.providers:
            logger.warning(f"未找到AI提供商配置: {self.current_provider}")
            return None
        
        config = self.providers[self.current_provider]
        
        if not config.api_key:
            logger.warning(f"AI提供商 {config.name} API密钥未设置")
            return None
        
        return config
    
    def validate_config(self, provider_name: Optional[str] = None) -> bool:
        """验证AI配置是否有效"""
        provider_name = provider_name or self.current_provider
        
        if provider_name not in self.providers:
            return False
        
        config = self.providers[provider_name]
        
        return bool(config.api_key and config.base_url and config.model)
    
    def list_available_providers(self) -> Dict[str, bool]:
        """列出所有可用的AI提供商"""
        return {
            name: self.validate_config(name) 
            for name in self.providers.keys()
        }
    
    def switch_provider(self, provider_name: str) -> bool:
        """切换AI提供商"""
        if provider_name not in self.providers:
            logger.error(f"未知的AI提供商: {provider_name}")
            return False
        
        if not self.validate_config(provider_name):
            logger.error(f"AI提供商 {provider_name} 配置无效")
            return False
        
        self.current_provider = provider_name
        logger.info(f"已切换到AI提供商: {provider_name}")
        return True
    
    def get_client_config(self) -> Dict[str, Any]:
        """获取客户端配置信息"""
        config = self.get_current_config()
        if not config:
            return {}
        
        return {
            'provider': self.current_provider,
            'model': config.model,
            'base_url': config.base_url,
            'timeout': config.timeout,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature
        }

# 全局AI配置管理器实例
ai_config = AIConfigManager()

def get_ai_config() -> AIConfigManager:
    """获取AI配置管理器实例"""
    return ai_config

def validate_ai_setup() -> bool:
    """验证AI设置是否正确"""
    config = ai_config.get_current_config()
    if not config:
        logger.error("AI配置验证失败: 没有有效的配置")
        return False
    
    logger.info(f"AI配置验证成功: {config.name} ({config.model})")
    return True 