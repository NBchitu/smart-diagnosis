import { NextRequest, NextResponse } from 'next/server';

const PY_BACKEND = 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    const body = await req.text();
    console.log('🔄 代理AI分析请求到后端:', body);
    
    const res = await fetch(`${PY_BACKEND}/api/capture/analyze-ai`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    
    const data = await res.text();
    console.log('📡 后端AI分析响应:', data);
    
    return new NextResponse(data, { 
      status: res.status, 
      headers: { 'Content-Type': 'application/json' } 
    });
  } catch (error) {
    console.error('❌ AI分析代理错误:', error);
    return NextResponse.json(
      { error: 'AI分析请求失败' }, 
      { status: 500 }
    );
  }
}
