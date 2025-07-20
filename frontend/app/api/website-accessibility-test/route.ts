import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { url } = await req.json();
    
    if (!url) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: '请提供要测试的网站URL' 
        }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    console.log('🌐 开始网站可访问性对比测试:', url);

    // 调用后端Python服务
    const response = await fetch('http://localhost:8000/api/network/website-accessibility-test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error(`后端服务错误: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success) {
      console.log('✅ 网站可访问性测试完成:', result.data);
      
      return new Response(
        JSON.stringify({
          success: true,
          data: {
            type: 'website_accessibility_result',
            ...result.data,
            timestamp: new Date().toISOString()
          }
        }),
        { 
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      throw new Error(result.error || '网站可访问性测试失败');
    }

  } catch (error) {
    console.error('❌ 网站可访问性测试API错误:', error);
    
    return new Response(
      JSON.stringify({ 
        success: false,
        error: '网站可访问性测试失败',
        details: (error as Error)?.message || 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
} 