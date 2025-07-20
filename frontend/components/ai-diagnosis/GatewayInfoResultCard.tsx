'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Router, Wifi, Globe, Server, Clock, CheckCircle, XCircle, AlertCircle, Network, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GatewayInfoResult {
  type: string;
  gateway_ip: string;
  local_ip: string;
  network_interface: string;
  dns_servers: string[];
  route_info: Record<string, any>;
  check_time: string;
  timestamp: string;
  error?: string;
}

interface GatewayInfoResultCardProps {
  result: GatewayInfoResult;
  className?: string;
}

export function GatewayInfoResultCard({ result, className }: GatewayInfoResultCardProps) {
  // 获取状态信息
  const getStatusInfo = () => {
    if (result.error) {
      return {
        icon: <XCircle className="w-5 h-5 text-red-500" />,
        text: '获取失败',
        color: 'border-red-200 bg-red-50',
        textColor: 'text-red-700'
      };
    }

    if (result.gateway_ip && result.gateway_ip !== '未知') {
      return {
        icon: <CheckCircle className="w-5 h-5 text-green-500" />,
        text: '信息完整',
        color: 'border-green-200 bg-green-50',
        textColor: 'text-green-700'
      };
    }

    return {
      icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
      text: '信息不完整',
      color: 'border-yellow-200 bg-yellow-50',
      textColor: 'text-yellow-700'
    };
  };

  const statusInfo = getStatusInfo();

  // 格式化时间
  const formatTime = (timeString: string) => {
    try {
      return new Date(timeString).toLocaleString('zh-CN');
    } catch {
      return timeString;
    }
  };

  // 获取网络接口显示名称
  const getInterfaceDisplayName = (interfaceName: string) => {
    const interfaceMap: Record<string, string> = {
      'en0': 'WiFi (en0)',
      'en1': '以太网 (en1)',
      'eth0': '以太网 (eth0)',
      'wlan0': 'WiFi (wlan0)',
      'unknown': '未知接口'
    };
    return interfaceMap[interfaceName] || interfaceName;
  };

  // 判断IP地址类型
  const getIPType = (ip: string) => {
    if (ip.startsWith('192.168.')) return '私有网络 (192.168.x.x)';
    if (ip.startsWith('10.')) return '私有网络 (10.x.x.x)';
    if (ip.startsWith('172.')) return '私有网络 (172.x.x.x)';
    if (ip.startsWith('169.254.')) return 'APIPA (自动分配)';
    return '公网地址';
  };

  // 分析DNS服务器
  const analyzeDNSServers = (servers: string[]) => {
    return servers.map(server => {
      let provider = '未知';
      let type = 'custom';
      
      if (server === '8.8.8.8' || server === '8.8.4.4') {
        provider = 'Google DNS';
        type = 'public';
      } else if (server === '1.1.1.1' || server === '1.0.0.1') {
        provider = 'Cloudflare DNS';
        type = 'public';
      } else if (server === '114.114.114.114' || server === '114.114.115.115') {
        provider = '114 DNS (中国电信)';
        type = 'public';
      } else if (server === '223.5.5.5' || server === '223.6.6.6') {
        provider = '阿里云 DNS';
        type = 'public';
      } else if (server.startsWith('192.168.') || server.startsWith('10.') || server.startsWith('172.')) {
        provider = '本地路由器';
        type = 'local';
      } else {
        provider = 'ISP DNS';
        type = 'isp';
      }
      
      return { server, provider, type };
    });
  };

  const dnsAnalysis = analyzeDNSServers(result.dns_servers);

  return (
    <Card className={cn("w-full", className, statusInfo.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {statusInfo.icon}
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                网关信息检测
              </CardTitle>
              <p className={cn("text-sm mt-1", statusInfo.textColor)}>
                {result.error ? '获取网关信息失败' : '网络配置详细信息'}
              </p>
            </div>
          </div>
          <Badge 
            variant="outline"
            className={cn("text-xs", statusInfo.textColor)}
          >
            {statusInfo.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {result.error ? (
          <div className="text-center py-4">
            <XCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm text-red-600">{result.error}</p>
          </div>
        ) : (
          <>
            {/* 基本网络信息 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 网关信息 */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Router className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">网关信息</span>
                </div>
                <div className="space-y-1 pl-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">网关地址:</span>
                    <span className="font-mono text-gray-900">{result.gateway_ip}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {getIPType(result.gateway_ip)}
                  </div>
                </div>
              </div>

              {/* 本地IP信息 */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Network className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">本地IP</span>
                </div>
                <div className="space-y-1 pl-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">IP地址:</span>
                    <span className="font-mono text-gray-900">{result.local_ip}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {getIPType(result.local_ip)}
                  </div>
                </div>
              </div>
            </div>

            {/* 网络接口信息 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">网络接口</span>
              </div>
              <div className="pl-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">接口名称:</span>
                  <span className="font-mono text-gray-900">
                    {getInterfaceDisplayName(result.network_interface)}
                  </span>
                </div>
              </div>
            </div>

            {/* DNS配置信息 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">DNS配置</span>
              </div>
              <div className="pl-6 space-y-2">
                {dnsAnalysis.length > 0 ? (
                  dnsAnalysis.map((dns, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Globe className="w-3 h-3 text-gray-400" />
                        <span className="font-mono text-sm text-gray-900">{dns.server}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-600">{dns.provider}</div>
                        <Badge 
                          variant="outline" 
                          className={cn(
                            "text-xs",
                            dns.type === 'public' && "border-blue-200 text-blue-700",
                            dns.type === 'local' && "border-green-200 text-green-700",
                            dns.type === 'isp' && "border-purple-200 text-purple-700"
                          )}
                        >
                          {dns.type === 'public' ? '公共DNS' : 
                           dns.type === 'local' ? '本地DNS' : 
                           dns.type === 'isp' ? 'ISP DNS' : '自定义'}
                        </Badge>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-500 italic">未检测到DNS服务器配置</div>
                )}
              </div>
            </div>

            {/* 检测时间 */}
            <div className="pt-2 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>检测时间: {formatTime(result.check_time)}</span>
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
