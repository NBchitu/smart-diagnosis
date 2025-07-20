import { NextRequest } from 'next/server';
import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export async function POST(req: NextRequest) {
  const { messages } = await req.json();
  
  // 创建AI客户端
  const client = createOpenAI({
    baseURL: 'https://openrouter.ai/api/v1',
    apiKey: process.env.OPENROUTER_API_KEY!,
  });
  
  const result = await streamText({
    model: client('anthropic/claude-3-haiku'),
    messages,
    system: '你是一个网络诊断助手。',
  });
  
  return result.toDataStreamResponse();
}