import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    console.log('🖥️ 开始获取网关信息...');

    // 调用后端Python服务
    const response = await fetch('http://localhost:8000/api/system/gateway', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`后端服务错误: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success) {
      console.log('✅ 网关信息获取完成:', result.data);
      
      // 格式化返回数据
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            type: 'gateway_info_result',
            gateway_ip: result.data.gateway_ip || '未知',
            local_ip: result.data.local_ip || '未知',
            network_interface: result.data.network_interface || '未知',
            dns_servers: result.data.dns_servers || [],
            route_info: result.data.route_info || {},
            check_time: new Date().toISOString(),
            timestamp: new Date().toISOString()
          }
        }),
        { 
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      throw new Error(result.error || '网关信息获取失败');
    }

  } catch (error) {
    console.error('❌ 网关信息API错误:', error);
    
    return new Response(
      JSON.stringify({ 
        success: false,
        error: '网关信息获取失败',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 