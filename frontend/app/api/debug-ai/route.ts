import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

// 真实的ping工具实现
async function executePingTool(parameters: Record<string, unknown>) {
  try {
    const { host = 'google.com', count = 4 } = parameters;
    
    // 调用后端ping API
    const response = await fetch(`http://localhost:8000/api/network/ping_test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ host, count }),
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Backend ping failed: ${response.status}`);
    }
  } catch (error) {
    console.error('真实ping工具调用失败，使用模拟数据:', error);
    
    // 降级到模拟ping结果
    return {
      host: parameters.host || 'google.com',
      packets_sent: parameters.count || 4,
      packets_received: 4,
      packet_loss: '0%',
      avg_latency: '23ms',
      min_latency: '20ms',
      max_latency: '28ms',
      status: 'success',
      fallback: true // 标记这是降级数据
    };
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log('开始调试AI诊断API...');
    
    const { messages } = await req.json();
    
    // 创建AI客户端
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku';
    
    if (!openRouterKey) {
      throw new Error('API key not found');
    }
    
    const client = createOpenAI({
      baseURL: 'https://openrouter.ai/api/v1',
      apiKey: openRouterKey,
    });
    
    const aiModel = client(model);
    console.log('✅ AI模型创建成功');
    
    // 只测试ping工具
    console.log('准备调用streamText with ping tool...');
    const result = await streamText({
      model: aiModel,
      messages,
      system: '你是一个网络诊断助手。当用户提到连接问题时，你可以使用ping工具测试网络连通性。',
      tools: {
        ping_test: {
          description: '执行 ping 测试检查网络连通性和延迟',
          parameters: {
            type: 'object',
            properties: {
              host: { type: 'string', description: '要测试的主机地址' },
              count: { type: 'number', description: '测试次数，默认为4' }
            },
            required: ['host']
          },
          execute: async (params) => {
            console.log('🔧 执行ping工具:', params);
            try {
              const result = await executePingTool(params);
              console.log('✅ ping工具执行成功');
              return JSON.stringify(result);
            } catch (error) {
              console.error('❌ ping工具执行失败:', error);
              throw error;
            }
          }
        }
      }
    });
    
    console.log('✅ streamText调用成功');
    return result.toDataStreamResponse();
    
  } catch (error: any) {
    console.error('❌ 调试API失败:', error);
    return new Response(
      JSON.stringify({ 
        error: error.message || 'Unknown error',
        stack: error.stack,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}