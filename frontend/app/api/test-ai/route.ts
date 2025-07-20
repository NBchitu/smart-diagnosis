import { NextRequest, NextResponse } from 'next/server';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST() {
  try {
    console.log('测试AI客户端创建...');
    
    // 获取环境变量
    const openRouterKey = process.env.OPENROUTER_API_KEY;
    const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-3-haiku';
    
    console.log('环境变量检查:', {
      hasKey: !!openRouterKey,
      keyLength: openRouterKey?.length || 0,
      model: model
    });
    
    if (!openRouterKey) {
      return NextResponse.json({ 
        error: 'API key not found',
        env: process.env.OPENROUTER_API_KEY ? 'set' : 'not set'
      }, { status: 400 });
    }
    
    // 测试创建OpenAI客户端
    const client = createOpenAI({
      baseURL: 'https://openrouter.ai/api/v1',
      apiKey: openRouterKey,
    });
    
    console.log('客户端创建成功');
    
    // 测试简单的AI调用
    const aiModel = client(model);
    console.log('AI模型实例创建成功');
    
    return NextResponse.json({ 
      success: true,
      message: 'AI客户端创建成功',
      model: model
    });
    
  } catch (error: any) {
    console.error('测试AI客户端失败:', error);
    return NextResponse.json({ 
      error: error.message || 'Unknown error',
      stack: error.stack || 'No stack trace'
    }, { status: 500 });
  }
}