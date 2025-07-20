import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST(req: NextRequest) {
  try {
    console.log('开始测试带工具的streamText...');
    
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
    console.log('AI模型创建成功');
    
    // 测试简单工具
    console.log('准备调用streamText...');
    const result = await streamText({
      model: aiModel,
      messages,
      system: '你是一个网络诊断助手，可以使用ping工具测试网络连通性。',
      tools: {
        simple_ping: {
          description: '简单的ping测试',
          parameters: {
            type: 'object',
            properties: {
              host: { type: 'string', description: '要ping的主机' }
            },
            required: ['host']
          },
          execute: async (params) => {
            try {
              console.log('执行简单ping工具:', params);
              const result = {
                host: params.host,
                success: true,
                result: 'ping成功，延迟20ms'
              };
              console.log('工具执行成功:', result);
              return JSON.stringify(result);
            } catch (toolError) {
              console.error('工具执行失败:', toolError);
              throw toolError;
            }
          }
        }
      }
    });
    
    console.log('带工具的streamText调用成功');
    return result.toDataStreamResponse();
    
  } catch (error: any) {
    console.error('带工具的streamText测试失败:', error);
    return new Response(
      JSON.stringify({ 
        error: error.message || 'Unknown error',
        stack: error.stack
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}