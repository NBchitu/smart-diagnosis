import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST(req: NextRequest) {
  try {
    console.log('=== 开始最小化AI测试 ===');
    
    const { messages } = await req.json();
    console.log('接收到消息:', JSON.stringify(messages, null, 2));

    // 直接使用环境变量创建客户端
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    console.log('OpenRouter Key:', openRouterKey ? `存在 (${openRouterKey.length} 字符)` : '不存在');
    
    if (!openRouterKey) {
      return new Response(
        JSON.stringify({ error: 'OPENROUTER_API_KEY 未设置' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const client = createOpenAI({
      baseURL: 'https://openrouter.ai/api/v1',
      apiKey: openRouterKey,
    });
    
    const model = client('anthropic/claude-3-haiku');
    console.log('AI模型创建成功');

    console.log('开始调用streamText...');
    
    const result = await streamText({
      model: model,
      messages: messages,
      system: '你是一个助手。请简短回答。',
      maxTokens: 100
    });

    console.log('streamText调用成功，返回响应');
    return result.toDataStreamResponse();
    
  } catch (error) {
    console.error('=== 最小化AI测试错误 ===');
    console.error('错误类型:', error?.constructor?.name);
    console.error('错误消息:', (error as Error)?.message);
    console.error('错误堆栈:', (error as Error)?.stack);
    
    return new Response(
      JSON.stringify({ 
        error: '最小化AI测试失败',
        type: error?.constructor?.name,
        message: (error as Error)?.message,
        stack: (error as Error)?.stack
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 