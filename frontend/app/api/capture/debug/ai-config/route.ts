import { NextRequest, NextResponse } from 'next/server';

const PY_BACKEND = 'http://localhost:8000';

export async function GET(req: NextRequest) {
  try {
    console.log('🔍 代理AI配置调试请求到后端');
    
    const res = await fetch(`${PY_BACKEND}/api/capture/debug/ai-config`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    const data = await res.text();
    console.log('📡 后端AI配置调试响应:', data);
    
    return new NextResponse(data, { 
      status: res.status, 
      headers: { 'Content-Type': 'application/json' } 
    });
  } catch (error) {
    console.error('❌ AI配置调试代理错误:', error);
    return NextResponse.json(
      { error: 'AI配置调试请求失败' }, 
      { status: 500 }
    );
  }
}
