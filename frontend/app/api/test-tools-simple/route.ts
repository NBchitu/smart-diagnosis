import { NextRequest } from 'next/server';
import { streamText, tool } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { z } from 'zod';

export async function POST(req: NextRequest) {
  try {
    console.log('=== 开始简单工具测试 ===');
    
    const { messages } = await req.json();
    console.log('接收到消息:', JSON.stringify(messages, null, 2));

    // 创建AI客户端
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

    // 使用标准的AI SDK工具定义格式
    const tools = {
      pingTest: tool({
        description: '执行 ping 测试检查网络连通性',
        parameters: z.object({
          host: z.string().describe('要测试的主机地址').optional()
        }),
        execute: async ({ host }) => {
          console.log('🔧 执行简单ping工具:', { host });
          // 返回简单的模拟数据
          return {
            success: true,
            host: host || 'baidu.com',
            result: 'ping成功，延迟20ms (模拟数据)'
          };
        }
      })
    };

    console.log('工具定义:', Object.keys(tools));
    console.log('开始调用streamText with standard tools...');
    
    const result = await streamText({
      model: model,
      messages: messages,
      system: '你是一个网络助手。你可以使用pingTest工具测试连接。',
      tools: tools,
      maxTokens: 200
    });

    console.log('streamText调用成功，返回响应');
    return result.toDataStreamResponse();
    
  } catch (error) {
    console.error('=== 简单工具测试错误 ===');
    console.error('错误类型:', error?.constructor?.name);
    console.error('错误消息:', (error as Error)?.message);
    console.error('错误堆栈:', (error as Error)?.stack);
    
    return new Response(
      JSON.stringify({ 
        error: '简单工具测试失败',
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