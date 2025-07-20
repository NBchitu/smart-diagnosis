import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { 
      target = 'baidu.com', 
      count = 4,
      timeout = 5000,
      packetSize = 32,
      interval = 1000,
      // 兼容旧的host参数
      host
    } = await req.json();
    
    // 使用target优先，如果没有则使用host，最后默认baidu.com
    const pingTarget = target || host || 'baidu.com';
    
    console.log('🔧 执行前端ping测试:', { 
      target: pingTarget, 
      count, 
      timeout, 
      packetSize, 
      interval 
    });
    
    // 调用后端ping API
    const response = await fetch(`http://localhost:8000/api/network/ping_test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        host: pingTarget,
        count,
        timeout,
        packet_size: packetSize,
        interval
      }),
    });

    if (response.ok) {
      const result = await response.json();
      console.log('✅ 后端ping测试成功:', result);
      
      return NextResponse.json({
        success: true,
        data: {
          host: result.data?.host || pingTarget,
          target: result.data?.host || pingTarget,
          packets_sent: result.data?.packets_sent || count,
          packets_received: result.data?.packets_received || 0,
          packet_loss: result.data?.packet_loss || 'N/A',
          min_latency: result.data?.min_latency || 'N/A',
          avg_latency: result.data?.avg_latency || 'N/A',
          max_latency: result.data?.max_latency || 'N/A',
          timeout: timeout,
          packet_size: packetSize,
          interval: interval,
          status: result.status === 'success' ? 'success' : 'failed',
          timestamp: result.timestamp || new Date().toISOString(),
          // 如果后端返回了详细的ping结果
          ping_results: result.data?.ping_results || [],
          summary: result.data?.summary || `Ping ${pingTarget}: ${count}次测试完成`
        }
      });
    } else {
      throw new Error(`后端API响应错误: ${response.status}`);
    }
    
  } catch (error) {
    console.error('❌ ping测试失败:', error);
    
    const { target = 'baidu.com', host, count = 4 } = await req.json().catch(() => ({}));
    const pingTarget = target || host || 'baidu.com';
    
    // 返回模拟数据作为降级方案
    return NextResponse.json({
      success: false,
      error: 'ping测试失败',
      details: (error as Error)?.message || 'Unknown error',
      fallback_data: {
        host: pingTarget,
        target: pingTarget,
        packets_sent: count,
        packets_received: 0,
        packet_loss: '100%',
        status: 'failed',
        message: '无法连接到后端服务或目标主机',
        timestamp: new Date().toISOString()
      }
    }, { status: 500 });
  }
} 