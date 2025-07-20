import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST(req: NextRequest) {
  try {
    console.log('开始测试streamText...');
    
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
    
    // 测试简单的streamText调用（无工具）
    const result = await streamText({
      model: aiModel,
      messages,
      system: '你是一个测试助手，简单回答用户的问题。',
    });
    
    console.log('streamText调用成功');
    return result.toDataStreamResponse();
    
  } catch (error: any) {
    console.error('streamText测试失败:', error);
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