import { NextRequest, NextResponse } from 'next/server';

const PY_BACKEND = 'http://localhost:8000';

export async function GET(req: NextRequest) {
  try {
    console.log('🔍 代理调试任务请求到后端');
    
    const res = await fetch(`${PY_BACKEND}/api/capture/debug/tasks`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    const data = await res.text();
    console.log('📡 后端调试响应:', data);
    
    return new NextResponse(data, { 
      status: res.status, 
      headers: { 'Content-Type': 'application/json' } 
    });
  } catch (error) {
    console.error('❌ 调试代理错误:', error);
    return NextResponse.json(
      { error: '调试请求失败' }, 
      { status: 500 }
    );
  }
}
