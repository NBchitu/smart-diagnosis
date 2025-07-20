import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    console.log('🌐 开始连通性检查...');

    const { testHosts = 'default' } = await req.json();

    // 调用后端Python服务
    const response = await fetch('http://localhost:8000/api/network/connectivity-check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}), // 后端方法不需要参数
    });

    if (!response.ok) {
      throw new Error(`后端服务错误: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success) {
      console.log('✅ 连通性检查完成:', result.data);
      
      const data = result.data;
      
      // 格式化返回数据，符合前端期望的格式
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            type: 'connectivity_check_result',
            overall_status: data.status || 'unknown',
            status: data.status || 'unknown',
            message: data.message || '连通性检查完成',
            details: {
              local_network: data.local_network || false,
              internet_dns: data.internet_dns || false,
              internet_http: data.internet_http || false,
              gateway_reachable: data.details?.gateway_reachable || false,
              dns_resolution: data.details?.dns_resolution || false,
              external_ping: data.details?.external_ping || false,
              http_response: data.details?.http_response || false
            },
            gateway_info: data.gateway_info || {},
            latency: data.latency || {},
            tests: [
              {
                name: '网关连通性',
                status: data.details?.gateway_reachable ? 'success' : 'failed',
                latency: data.latency?.gateway || null,
                message: data.details?.gateway_reachable ? '网关可达' : '网关不可达'
              },
              {
                name: 'DNS解析',
                status: data.details?.dns_resolution ? 'success' : 'failed',
                message: data.details?.dns_resolution ? 'DNS解析正常' : 'DNS解析失败'
              },
              {
                name: '外部网络ping',
                status: data.details?.external_ping ? 'success' : 'failed',
                latency: data.latency?.average_external || null,
                message: data.details?.external_ping ? '外部网络可达' : '外部网络不可达'
              },
              {
                name: 'HTTP连通性',
                status: data.details?.http_response ? 'success' : 'failed',
                message: data.details?.http_response ? 'HTTP访问正常' : 'HTTP访问失败'
              }
            ],
            summary: {
              total_tests: 4,
              passed_tests: Object.values(data.details || {}).filter(Boolean).length,
              success_rate: `${Math.round(Object.values(data.details || {}).filter(Boolean).length / 4 * 100)}%`
            },
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
      throw new Error(result.error || '连通性检查失败');
    }

  } catch (error) {
    console.error('❌ 连通性检查API错误:', error);
    
    // 返回降级数据
    const fallbackData = {
      success: true,
      data: {
        type: 'connectivity_check_result',
        overall_status: 'unknown',
        status: 'error',
        message: '后端服务不可用，使用降级数据',
        details: {
          local_network: false,
          internet_dns: false,
          internet_http: false,
          gateway_reachable: false,
          dns_resolution: false,
          external_ping: false,
          http_response: false
        },
        gateway_info: {},
        latency: {},
        tests: [
          {
            name: '网关连通性',
            status: 'unknown',
            message: '无法检测'
          },
          {
            name: 'DNS解析',
            status: 'unknown',
            message: '无法检测'
          },
          {
            name: '外部网络ping',
            status: 'unknown',
            message: '无法检测'
          },
          {
            name: 'HTTP连通性',
            status: 'unknown',
            message: '无法检测'
          }
        ],
        summary: {
          total_tests: 4,
          passed_tests: 0,
          success_rate: '0%'
        },
        check_time: new Date().toISOString(),
        timestamp: new Date().toISOString(),
        error: (error as Error)?.message || 'Unknown error'
      }
    };
    
    return new Response(
      JSON.stringify(fallbackData),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 