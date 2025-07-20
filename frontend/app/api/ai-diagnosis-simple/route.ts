import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

// 创建AI客户端函数
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
    const { messages } = await req.json();
    console.log('📝 接收到消息:', messages);

    // 创建AI模型实例
    const aiModel = createAIClient();

    if (!aiModel) {
      return new Response('AI配置无效', { status: 400 });
    }

    console.log('🔄 开始调用streamText...');
    
    // 简化的streamText调用，不包含工具
    const result = await streamText({
      model: aiModel,
      messages,
      system: '你是一个网络诊断助手。',
      maxTokens: 200
    });

    console.log('✅ streamText调用成功');
    return result.toDataStreamResponse();
    
  } catch (error) {
    console.error('❌ AI诊断API错误:', error);
    console.error('错误详情:', {
      message: (error as Error)?.message,
      stack: (error as Error)?.stack
    });
    
    return new Response(
      JSON.stringify({ 
        error: '内部服务器错误',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 