import { NextRequest, NextResponse } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST(req: NextRequest) {
  try {
    console.log('🔍 开始调试AI配置...');
    
    const { message } = await req.json();
    
    // 创建AI客户端
    const provider = process.env.AI_PROVIDER || 'openrouter';
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const openAIKey = process.env.OPENAI_API_KEY;
    
    console.log('AI配置信息:', {
      provider,
      openRouterKey: openRouterKey ? `set (${openRouterKey.length} chars)` : 'not set',
      openAIKey: openAIKey ? `set (${openAIKey.length} chars)` : 'not set'
    });

    let aiModel = null;

    // 根据配置选择API
    if (provider === 'openrouter' && openRouterKey && openRouterKey.length > 10) {
      try {
        const client = createOpenAI({
          baseURL: 'https://openrouter.ai/api/v1',
          apiKey: openRouterKey,
        });
        const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku';
        aiModel = client(model);
        console.log(`✅ 创建OpenRouter AI模型成功: ${model}`);
      } catch (error) {
        console.error('❌ 创建OpenRouter AI模型失败:', error);
        return NextResponse.json({
          success: false,
          error: '创建OpenRouter AI模型失败',
          details: (error as Error)?.message || 'Unknown error'
        }, { status: 500 });
      }
    } else if (provider === 'openai' && openAIKey && openAIKey.startsWith('sk-')) {
      try {
        const client = createOpenAI({
          baseURL: 'https://api.openai.com/v1',
          apiKey: openAIKey,
        });
        const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
        aiModel = client(model);
        console.log(`✅ 创建OpenAI模型成功: ${model}`);
      } catch (error) {
        console.error('❌ 创建OpenAI模型失败:', error);
        return NextResponse.json({
          success: false,
          error: '创建OpenAI模型失败',
          details: (error as Error)?.message || 'Unknown error'
        }, { status: 500 });
      }
    } else {
      console.log('⚠️ 未检测到有效的AI API密钥');
      return NextResponse.json({
        success: false,
        error: '未检测到有效的AI API密钥',
        config: {
          provider,
          openRouterKey: openRouterKey ? 'set' : 'not set',
          openAIKey: openAIKey ? 'set' : 'not set'
        }
      }, { status: 400 });
    }

    if (!aiModel) {
      return NextResponse.json({
        success: false,
        error: 'AI模型创建失败'
      }, { status: 500 });
    }

    console.log('🔄 开始调用streamText...');
    
    // 测试streamText调用
    const result = await streamText({
      model: aiModel,
      messages: [
        { role: 'user', content: message || '你好，这是一个测试消息' }
      ],
      system: '你是一个友好的助手。',
      maxTokens: 100
    });

    console.log('✅ streamText调用成功');
    
    return result.toDataStreamResponse();
    
  } catch (error) {
    console.error('❌ 调试AI配置失败:', error);
    console.error('错误详情:', {
      message: (error as Error)?.message,
      stack: (error as Error)?.stack,
      name: (error as Error)?.name
    });
    
    return NextResponse.json({
      success: false,
      error: '调试AI配置失败',
      details: (error as Error)?.message || 'Unknown error',
      stack: process.env.NODE_ENV === 'development' ? (error as Error)?.stack : undefined
    }, { status: 500 });
  }
} 