import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    console.log('📶 开始WiFi扫描分析...');

    // 调用后端Python服务的完整WiFi扫描接口
    const response = await fetch('http://localhost:8000/api/wifi/scan', {
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
      console.log('✅ WiFi扫描分析完成:', {
        networks: result.data.networks?.length || 0,
        current_wifi: result.data.current_wifi?.connected ? '已连接' : '未连接',
        channel_analysis: result.data.channel_analysis ? '已分析' : '未分析',
        recommendations: result.data.recommendations ? '已生成' : '未生成'
      });
      
      // 返回完整的WiFi扫描分析数据
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            type: 'wifi_scan_result',
            current_wifi: result.data.current_wifi,
            networks: result.data.networks || [],
            channel_analysis: result.data.channel_analysis || {
              "2.4ghz": {},
              "5ghz": {},
              summary: {
                total_24ghz_networks: 0,
                total_5ghz_networks: 0,
                most_crowded_24ghz: 1,
                least_crowded_24ghz: 11
              }
            },
            recommendations: result.data.recommendations || {
              need_adjustment: false,
              current_channel: null,
              current_band: null,
              recommended_channels: [],
              reasons: []
            },
            scan_time: result.data.scan_time || Date.now(),
            total_networks: result.data.networks?.length || 0,
            timestamp: new Date().toISOString()
          }
        }),
        { 
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      throw new Error(result.error || 'WiFi扫描失败');
    }

  } catch (error) {
    console.error('❌ WiFi扫描API错误:', error);
    
    return new Response(
      JSON.stringify({ 
        success: false,
        error: 'WiFi扫描失败',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 