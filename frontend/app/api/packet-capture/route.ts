import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    console.log('🔍 开始数据包捕获...');

    const { target = 'sina.com', duration = 30, mode = 'auto' } = await req.json();

    // 调用后端Python服务启动抓包
    const response = await fetch('http://localhost:8000/api/packet-capture', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target,
        duration,
        mode
      }),
    });

    if (!response.ok) {
      throw new Error(`后端服务错误: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success && result.data && result.data.session_id) {
      console.log('✅ 数据包捕获启动成功:', result.data);
      
      // 启动成功，返回会话信息
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            type: 'packet_capture_started',
            session_id: result.data.session_id,
            target: target,
            duration: duration,
            mode: mode,
            status: 'started',
            message: `已启动对 ${target} 的数据包捕获，预计 ${duration} 秒后完成`,
            timestamp: new Date().toISOString()
          }
        }),
        { 
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      throw new Error(result.error || '数据包捕获启动失败');
    }

  } catch (error) {
    console.error('❌ 数据包捕获API错误:', error);
    
    return new Response(
      JSON.stringify({ 
        success: false,
        error: '数据包捕获失败',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 