import { NextRequest, NextResponse } from 'next/server';

// IP地址信息接口
interface IPInfo {
  ip: string;
  city?: string;
  region?: string;
  country?: string;
  country_name?: string;
  postal?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  utc_offset?: string;
  country_calling_code?: string;
  currency?: string;
  languages?: string;
  asn?: string;
  org?: string;
  error?: boolean;
  reason?: string;
}

// 格式化运营商名称
function formatISPName(orgName: string): string {
  if (!orgName) return '';

  const lowerOrg = orgName.toLowerCase();

  // 中国三大运营商识别（不区分大小写）
  if (lowerOrg.includes('china mobile')) {
    return '移动';
  }
  if (lowerOrg.includes('china unicom')) {
    return '联通';
  }
  if (lowerOrg.includes('china telecom')) {
    return '电信';
  }

  // 其他常见运营商简化
  if (lowerOrg.includes('tencent')) {
    return '腾讯云';
  }
  if (lowerOrg.includes('alibaba') || lowerOrg.includes('aliyun')) {
    return '阿里云';
  }
  if (lowerOrg.includes('baidu')) {
    return '百度云';
  }
  if (lowerOrg.includes('huawei')) {
    return '华为云';
  }
  if (lowerOrg.includes('google')) {
    return 'Google';
  }
  if (lowerOrg.includes('amazon') || lowerOrg.includes('aws')) {
    return 'AWS';
  }
  if (lowerOrg.includes('microsoft') || lowerOrg.includes('azure')) {
    return 'Azure';
  }

  // 如果没有匹配，返回原始名称（截断处理）
  return orgName.length > 20 ? orgName.substring(0, 20) + '...' : orgName;
}

// 格式化IP信息为中文显示
function formatIPInfo(data: IPInfo): {
  country: string;
  province: string;
  city: string;
  district: string;
  isp: string;
  zipCode: string;
  areaCode: string;
  networkType: string;
} {
  // 简单的英文到中文映射
  const countryMap: { [key: string]: string } = {
    'China': '中国',
    'United States': '美国',
    'Japan': '日本',
    'South Korea': '韩国',
    'Singapore': '新加坡',
    'Hong Kong': '香港',
    'Taiwan': '台湾',
    'Germany': '德国',
    'United Kingdom': '英国',
    'France': '法国',
    'Canada': '加拿大',
    'Australia': '澳大利亚'
  };

  const formattedISP = formatISPName(data.org || '');

  return {
    country: countryMap[data.country_name || ''] || data.country_name || data.country || '',
    province: data.region || '',
    city: data.city || '',
    district: '',
    isp: formattedISP,
    zipCode: data.postal || '',
    areaCode: '',
    networkType: formattedISP
  };
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const ip = searchParams.get('ip');

    if (!ip) {
      return NextResponse.json({
        success: false,
        error: '缺少IP地址参数'
      }, { status: 400 });
    }

    // 验证IP地址格式
    const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
    const ipv6Regex = /^([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}$/;
    
    if (!ipv4Regex.test(ip) && !ipv6Regex.test(ip)) {
      return NextResponse.json({
        success: false,
        error: '无效的IP地址格式'
      }, { status: 400 });
    }

    // 创建一个带超时的fetch请求
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时

    try {
      // 调用ipapi.co免费服务
      const response = await fetch(`https://ipapi.co/${ip}/json/`, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`IP查询API请求失败: ${response.status}`);
      }

      const data: IPInfo = await response.json();
      console.log('IP查询服务响应:', data);

      // 检查是否有错误
      if (data.error) {
        throw new Error(data.reason || '查询失败');
      }

      // 格式化返回数据
      const formattedInfo = formatIPInfo(data);
      
      return NextResponse.json({
        success: true,
        ip: data.ip,
        info: formattedInfo,
        summary: {
          location: `${formattedInfo.province}${formattedInfo.city ? ' ' + formattedInfo.city : ''}`.replace(/^$/, '未知地区'),
          isp: formattedInfo.isp || '未知运营商',
          networkType: formattedInfo.networkType || ''
        }
      });

    } catch (fetchError) {
      clearTimeout(timeoutId);
      console.error('IP查询服务失败:', fetchError);
      
      // 如果网络查询失败，返回基本信息
      return NextResponse.json({
        success: true,
        ip: ip,
        info: {
          country: '未知',
          province: '未知',
          city: '未知',
          district: '',
          isp: '未知运营商',
          zipCode: '',
          areaCode: '',
          networkType: ''
        },
        summary: {
          location: '未知地区',
          isp: '未知运营商',
          networkType: ''
        }
      });
    }

  } catch (error) {
    console.error('IP信息查询失败:', error);
    return NextResponse.json({
      success: false,
      error: '查询IP信息时发生错误'
    }, { status: 500 });
  }
}
