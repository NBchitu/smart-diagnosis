// AI服务配置
export const aiConfig = {
  // OpenRouter 配置（推荐）
  openrouter: {
    baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
    apiKey: process.env.OPENROUTER_API_KEY || '',
    model: process.env.OPENROUTER_MODEL || 'anthropic/claude-3-sonnet',
    enabled: true
  },
  
  // OpenAI 配置（备用）
  openai: {
    baseURL: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
    apiKey: process.env.OPENAI_API_KEY || '',
    model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
    enabled: false
  },
  
  // 通用配置
  maxTokens: 4000,
  temperature: 0.7,
  timeout: 30000,
  
  // 当前使用的提供商
  provider: process.env.AI_PROVIDER || 'openrouter'
};

// 获取当前AI配置
export function getCurrentAIConfig() {
  const provider = aiConfig.provider;
  
  switch (provider) {
    case 'openrouter':
      return aiConfig.openrouter;
    case 'openai':
      return aiConfig.openai;
    default:
      return aiConfig.openrouter; // 默认使用OpenRouter
  }
}

// 验证配置是否完整
export function validateAIConfig() {
  const config = getCurrentAIConfig();
  
  if (!config.apiKey) {
    console.warn(`AI配置警告: ${aiConfig.provider} API密钥未设置`);
    return false;
  }
  
  if (!config.baseURL) {
    console.warn(`AI配置警告: ${aiConfig.provider} BASE_URL未设置`);
    return false;
  }
  
  return true;
} 