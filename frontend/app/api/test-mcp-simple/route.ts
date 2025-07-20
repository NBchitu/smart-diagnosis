import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

// 创建AI客户端
function createAIClient() {
  try {
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    console.log('AI客户端配置检查:', {
      provider,
      openRouterKey: openRouterKey ? `set (${openRouterKey.length} chars)` : 'not set',
      openAIKey: openAIKey ? `set (${openAIKey.length} chars)` : 'not set'
    });
    
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      const client = createOpenAI({
        baseURL: 'https://openrouter.ai/api/v1',
        apiKey: openRouterKey,
      });
      const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku';
      console.log(`✅ 使用OpenRouter AI模型: ${model}`);
      return client(model);
    }
    
    if (provider === 'openai' && openAIKey && openAIKey.startsWith('sk-')) {
      const client = createOpenAI({
        baseURL: 'https://api.openai.com/v1',
        apiKey: openAIKey,
      });
      const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
      console.log(`✅ 使用OpenAI模型: ${model}`);
      return client(model);
    }

    console.log('⚠️ 未检测到有效的AI API密钥');
    return null;

  } catch (error) {
    console.error('❌ 创建AI客户端失败:', error);
    return null;
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log('📝 开始处理简化MCP测试请求');
    
    const { messages } = await req.json();
    console.log('📝 接收到消息:', messages);

    // 创建AI模型实例
    console.log('🤖 创建AI客户端...');
    const aiModel = createAIClient();
    if (!aiModel) {
      console.error('❌ AI客户端创建失败');
      return new Response(
        JSON.stringify({ error: 'AI配置无效，请检查环境变量' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    console.log('🔄 开始调用streamText (无工具)...');
    
    try {
      // 简单的streamText调用，不使用工具
      const result = await streamText({
        model: aiModel,
        messages,
        system: '你是一个网络诊断助手。请简单回答用户的问题。',
        maxTokens: 200,
        temperature: 0.7
      });

      console.log('✅ streamText调用成功');
      return result.toDataStreamResponse();
    } catch (streamError) {
      console.error('❌ streamText调用失败:', streamError);
      return new Response(
        JSON.stringify({ 
          error: 'AI流式处理失败', 
          details: (streamError as Error).message,
          stack: (streamError as Error).stack 
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
  } catch (error) {
    console.error('❌ 简化MCP测试API错误:', error);
    console.error('错误详情:', {
      message: (error as Error)?.message,
      stack: (error as Error)?.stack
    });
    
    return new Response(
      JSON.stringify({ 
        error: '内部服务器错误',
        details: (error as Error)?.message || 'Unknown error',
        stack: (error as Error)?.stack 
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 