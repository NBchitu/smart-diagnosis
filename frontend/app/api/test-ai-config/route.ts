import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const config = {
      AI_PROVIDER: process.env.AI_PROVIDER || 'not set',
      OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY ? `set (${process.env.OPENROUTER_API_KEY.length} chars)` : 'not set',
      OPENROUTER_MODEL: process.env.OPENROUTER_MODEL || 'not set',
      OPENAI_API_KEY: process.env.OPENAI_API_KEY ? `set (${process.env.OPENAI_API_KEY.length} chars)` : 'not set',
      OPENAI_MODEL: process.env.OPENAI_MODEL || 'not set',
      NODE_ENV: process.env.NODE_ENV || 'not set'
    };

    console.log('AI配置检查:', config);

    return NextResponse.json({
      success: true,
      config,
      message: 'AI配置检查完成'
    });
  } catch (error) {
    console.error('AI配置检查失败:', error);
    return NextResponse.json({
      success: false,
      error: 'AI配置检查失败',
      message: (error as Error)?.message || 'Unknown error'
    }, { status: 500 });
  }
} 