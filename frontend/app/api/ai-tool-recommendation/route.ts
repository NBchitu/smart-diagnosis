import { NextRequest } from 'next/server';
import { experimental_createMCPClient, generateText } from 'ai';
import { Experimental_StdioMCPTransport } from 'ai/mcp-stdio';
import { createOpenAI } from '@ai-sdk/openai';

// 工具推荐结果接口
interface ToolRecommendation {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet' | 'diagnosis';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  estimatedDuration: string;
  parameters: {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    defaultValue?: any;
    options?: string[];
    required: boolean;
    description: string;
  }[];
  apiEndpoint: string;
  examples: string[];
}

// 创建AI客户端
function createAIClient() {
  try {
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      const openai = createOpenAI({
        baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
        apiKey: openRouterKey,
      });
      return openai(process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku');
    }
    
    if (provider === 'openai' && openAIKey && openAIKey.startsWith('sk-')) {
      const openai = createOpenAI({
        apiKey: openAIKey,
      });
      return openai(process.env.OPENAI_MODEL || 'gpt-4o-mini');
    }

    return null;
  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}

// 预定义的工具推荐模板
const TOOL_TEMPLATES: Record<string, ToolRecommendation> = {
  ping: {
    id: 'ping',
    name: 'Ping测试',
    description: '测试与指定主机的网络连通性和延迟',
    category: 'network',
    priority: 'high',
    icon: '🏓',
    estimatedDuration: '5-10秒',
    parameters: [
      {
        name: 'host',
        type: 'string',
        label: '目标主机',
        defaultValue: 'baidu.com',
        required: true,
        description: '要测试的主机地址或域名'
      },
      {
        name: 'count',
        type: 'number',
        label: '测试次数',
        defaultValue: 4,
        required: false,
        description: 'ping测试的次数'
      },
      {
        name: 'timeout',
        type: 'number',
        label: '超时时间(秒)',
        defaultValue: 10,
        required: false,
        description: '每次ping的超时时间'
      }
    ],
    apiEndpoint: '/api/network-ping',
    examples: ['baidu.com', 'google.com', '8.8.8.8']
  },
  wifi_scan: {
    id: 'wifi_scan',
    name: 'WiFi扫描',
    description: '扫描周围的WiFi网络并分析信号强度',
    category: 'wifi',
    priority: 'medium',
    icon: '📶',
    estimatedDuration: '10-15秒',
    parameters: [],
    apiEndpoint: '/api/wifi-scan',
    examples: []
  },
  connectivity_check: {
    id: 'connectivity_check',
    name: '连通性检查',
    description: '全面检查互联网连接状态',
    category: 'connectivity',
    priority: 'high',
    icon: '🌐',
    estimatedDuration: '15-20秒',
    parameters: [
      {
        name: 'testHosts',
        type: 'select',
        label: '测试目标',
        defaultValue: 'default',
        options: ['default', 'international', 'china'],
        required: false,
        description: '选择测试的目标服务器组'
      }
    ],
    apiEndpoint: '/api/connectivity-check',
    examples: []
  },
  gateway_info: {
    id: 'gateway_info',
    name: '网关信息',
    description: '获取网络网关和路由信息',
    category: 'gateway',
    priority: 'medium',
    icon: '🖥️',
    estimatedDuration: '3-5秒',
    parameters: [],
    apiEndpoint: '/api/gateway-info',
    examples: []
  },
  packet_capture: {
    id: 'packet_capture',
    name: '数据包分析',
    description: '捕获和分析网络数据包',
    category: 'packet',
    priority: 'low',
    icon: '🔍',
    estimatedDuration: '30-60秒',
    parameters: [
      {
        name: 'target',
        type: 'string',
        label: '分析目标',
        defaultValue: 'sina.com',
        required: true,
        description: '要分析的网站或IP地址'
      },
      {
        name: 'duration',
        type: 'number',
        label: '捕获时长(秒)',
        defaultValue: 30,
        required: false,
        description: '数据包捕获的持续时间'
      },
      {
        name: 'mode',
        type: 'select',
        label: '分析模式',
        defaultValue: 'auto',
        options: ['auto', 'web', 'domain', 'port'],
        required: false,
        description: '数据包分析的模式'
      }
    ],
    apiEndpoint: '/api/packet-capture',
    examples: ['sina.com', 'baidu.com', 'qq.com']
  }
};

export async function POST(req: NextRequest) {
  try {
    console.log('📝 开始处理工具推荐请求');
    
    const { message } = await req.json();
    console.log('📝 用户问题:', message);

    // 创建AI模型实例
    const aiModel = createAIClient();
    if (!aiModel) {
      return new Response(
        JSON.stringify({ error: 'AI配置无效，请检查环境变量' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // 构建AI分析提示
    const analysisPrompt = `
作为网络诊断专家，请分析用户的网络问题并推荐合适的诊断工具。

用户问题：${message}

可用工具：
1. ping - 网络连通性测试
2. wifi_scan - WiFi网络扫描
3. connectivity_check - 互联网连接检查  
4. gateway_info - 网关信息获取
5. packet_capture - 数据包分析

请根据用户描述的问题，推荐1-3个最相关的工具，按优先级排序。

请以JSON格式回复，包含：
{
  "analysis": "问题分析",
  "recommendedTools": ["tool_id1", "tool_id2", "tool_id3"],
  "reasoning": "推荐理由",
  "urgency": "high|medium|low"
}

只返回JSON，不要其他内容。
`;

    console.log('🤖 调用AI进行工具推荐分析...');
    
    const result = await generateText({
      model: aiModel,
      prompt: analysisPrompt,
      maxTokens: 500,
      temperature: 0.3,
    });

    console.log('🤖 AI分析结果:', result.text);

    // 解析AI响应
    let aiResponse;
    try {
      // 尝试从AI响应中提取JSON
      const jsonMatch = result.text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        aiResponse = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('无法从AI响应中提取JSON');
      }
    } catch (parseError) {
      console.warn('⚠️ AI响应解析失败，使用默认推荐:', parseError);
      // 默认推荐基于关键词
      aiResponse = {
        analysis: "基于关键词分析的默认推荐",
        recommendedTools: getDefaultRecommendations(message),
        reasoning: "根据问题关键词进行的智能推荐",
        urgency: "medium"
      };
    }

    // 构建工具推荐卡片
    const recommendations: ToolRecommendation[] = aiResponse.recommendedTools
      .filter((toolId: string) => TOOL_TEMPLATES[toolId])
      .map((toolId: string) => ({
        ...TOOL_TEMPLATES[toolId],
        // 根据AI分析调整优先级
        priority: aiResponse.urgency === 'high' ? 'high' : 
                 aiResponse.urgency === 'low' ? 'low' : 'medium'
      }));

    // 如果没有推荐工具，提供默认推荐
    if (recommendations.length === 0) {
      recommendations.push(
        TOOL_TEMPLATES.ping,
        TOOL_TEMPLATES.connectivity_check
      );
    }

    console.log('✅ 工具推荐生成完成:', recommendations.map(r => r.name));

    return new Response(
      JSON.stringify({
        success: true,
        data: {
          analysis: aiResponse.analysis,
          reasoning: aiResponse.reasoning,
          urgency: aiResponse.urgency,
          recommendations,
          timestamp: new Date().toISOString()
        }
      }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );

  } catch (error) {
    console.error('❌ 工具推荐API错误:', error);
    
    return new Response(
      JSON.stringify({ 
        error: '工具推荐失败',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// 基于关键词的默认推荐逻辑
function getDefaultRecommendations(message: string): string[] {
  const lowerMessage = message.toLowerCase();
  const recommendations: string[] = [];

  // 网络连通性相关
  if (lowerMessage.includes('ping') || 
      lowerMessage.includes('连不上') || 
      lowerMessage.includes('无法访问') ||
      lowerMessage.includes('超时')) {
    recommendations.push('ping');
  }

  // WiFi相关
  if (lowerMessage.includes('wifi') || 
      lowerMessage.includes('无线') || 
      lowerMessage.includes('信号')) {
    recommendations.push('wifi_scan');
  }

  // 网络连接相关
  if (lowerMessage.includes('网络') || 
      lowerMessage.includes('上网') || 
      lowerMessage.includes('连接')) {
    recommendations.push('connectivity_check');
  }

  // 路由器/网关相关
  if (lowerMessage.includes('路由器') || 
      lowerMessage.includes('网关') || 
      lowerMessage.includes('IP')) {
    recommendations.push('gateway_info');
  }

  // 网络分析相关
  if (lowerMessage.includes('慢') || 
      lowerMessage.includes('分析') || 
      lowerMessage.includes('抓包')) {
    recommendations.push('packet_capture');
  }

  // 如果没有匹配到关键词，提供基础推荐
  if (recommendations.length === 0) {
    recommendations.push('ping', 'connectivity_check');
  }

  return recommendations.slice(0, 3); // 最多推荐3个工具
} 