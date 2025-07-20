import { NextRequest, NextResponse } from 'next/server';

const PY_BACKEND = 'http://localhost:8000';

export async function POST(req: NextRequest) {
  try {
    console.log('🧪 代理AI测试请求到后端');
    
    const res = await fetch(`${PY_BACKEND}/api/capture/test-ai`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    const data = await res.text();
    console.log('📡 后端AI测试响应:', data);
    
    return new NextResponse(data, { 
      status: res.status, 
      headers: { 'Content-Type': 'application/json' } 
    });
  } catch (error) {
    console.error('❌ AI测试代理错误:', error);
    return NextResponse.json(
      { error: 'AI测试请求失败' }, 
      { status: 500 }
    );
  }
}
