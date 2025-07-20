'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import WebsiteAccessibilityResult from './WebsiteAccessibilityResult';
import { 
  Wifi, 
  Activity, 
  NetworkIcon, 
  WifiIcon,
  Gauge,
  Wrench,
  Loader2,
  Clock,
  CheckCircle,
  XCircle,
  Globe,
  Search
} from 'lucide-react';

interface DiagnosisToolbarProps {
  onToolSelect: (tool: string) => void;
  isAnalyzing: boolean;
}

interface PingResult {
  success: boolean;
  data?: {
    host: string;
    packets_sent: number;
    packets_received: number;
    packet_loss: string;
    min_latency: string;
    avg_latency: string;
    max_latency: string;
    status: string;
    timestamp: string;
  };
  error?: string;
  details?: string;
}

export function DiagnosisToolbar({ onToolSelect, isAnalyzing }: DiagnosisToolbarProps) {
  const [pingResult, setPingResult] = useState<PingResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [websiteTestResult, setWebsiteTestResult] = useState<any>(null);
  const [isWebsiteTestLoading, setIsWebsiteTestLoading] = useState(false);

  const executePingTest = async (host: string = 'baidu.com') => {
    setIsLoading(true);
    setPingResult(null);

    try {
      const response = await fetch('/api/network-ping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ host, count: 4 }),
      });

      const result = await response.json();
      setPingResult(result);
    } catch (error) {
      setPingResult({
        success: false,
        error: '网络请求失败',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const executeWebsiteAccessibilityTest = async () => {
    if (!websiteUrl.trim()) {
      alert('请输入要测试的网站URL');
      return;
    }

    setIsWebsiteTestLoading(true);
    setWebsiteTestResult(null);

    try {
      const response = await fetch('/api/website-accessibility-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: websiteUrl }),
      });

      const result = await response.json();
      setWebsiteTestResult(result);
    } catch (error) {
      setWebsiteTestResult({
        success: false,
        error: '网站可访问性测试失败',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsWebsiteTestLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'failed': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4" />;
      case 'failed': return <XCircle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const tools = [
    {
      id: 'ping',
      name: 'Ping 测试',
      description: '检测网络延迟和连通性',
      icon: Activity,
      category: 'connectivity'
    },
    {
      id: 'speedtest',
      name: '速度测试',
      description: '测试网络带宽和速度',
      icon: Gauge,
      category: 'performance'
    },
    {
      id: 'wifi_scan',
      name: 'WiFi 扫描',
      description: '扫描周边WiFi信号',
      icon: Wifi,
      category: 'wifi'
    },
    {
      id: 'trace_route',
      name: '路由追踪',
      description: '追踪网络路径和节点',
      icon: NetworkIcon,
      category: 'analysis'
    },
    {
      id: 'signal_analysis',
      name: '信号分析',
      description: '分析WiFi信号质量',
      icon: WifiIcon,
      category: 'wifi'
    },
    {
      id: 'packet_loss',
      name: '丢包检测',
      description: '检测网络丢包情况',
      icon: Activity,
      category: 'performance'
    }
  ];

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'connectivity':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'performance':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'wifi':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'analysis':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* 工具栏 */}
      <Card className="border-gray-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Wifi className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-gray-900">网络诊断工具</span>
            </div>
            <div className="flex space-x-2">
              <Button
                onClick={() => executePingTest('baidu.com')}
                disabled={isLoading}
                size="sm"
                variant="outline"
                className="text-xs"
              >
                {isLoading ? (
                  <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                ) : (
                  <Activity className="h-3 w-3 mr-1" />
                )}
                Ping 百度
              </Button>
              <Button
                onClick={() => executePingTest('google.com')}
                disabled={isLoading}
                size="sm"
                variant="outline"
                className="text-xs"
              >
                {isLoading ? (
                  <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                ) : (
                  <Activity className="h-3 w-3 mr-1" />
                )}
                Ping Google
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 网站可访问性测试工具 */}
      <Card className="border-gray-200">
        <CardContent className="p-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-green-600" />
              <span className="font-medium text-gray-900">网站可访问性对比测试</span>
            </div>
            <div className="flex space-x-2">
              <Input
                placeholder="请输入网站URL，如：baidu.com"
                value={websiteUrl}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setWebsiteUrl(e.target.value)}
                className="flex-1 text-sm"
                onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
                  if (e.key === 'Enter') {
                    executeWebsiteAccessibilityTest();
                  }
                }}
              />
              <Button
                onClick={executeWebsiteAccessibilityTest}
                disabled={isWebsiteTestLoading || !websiteUrl.trim()}
                size="sm"
                className="bg-green-600 hover:bg-green-700"
              >
                {isWebsiteTestLoading ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Search className="h-4 w-4 mr-1" />
                )}
                测试
              </Button>
            </div>
            <div className="text-xs text-gray-500">
              比较不同运营商网络对该网站的可访问性
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ping 测试结果 */}
      {pingResult && (
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900 flex items-center">
                  <Activity className="h-4 w-4 mr-2" />
                  Ping 测试结果
                </h4>
                {pingResult.success && pingResult.data && (
                  <Badge 
                    variant={pingResult.data.status === 'success' ? 'default' : 'destructive'}
                    className="text-xs"
                  >
                    <span className={getStatusColor(pingResult.data.status)}>
                      {getStatusIcon(pingResult.data.status)}
                    </span>
                    <span className="ml-1">
                      {pingResult.data.status === 'success' ? '连接正常' : '连接失败'}
                    </span>
                  </Badge>
                )}
              </div>

              {pingResult.success && pingResult.data ? (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">目标主机:</span>
                      <span className="font-medium">{pingResult.data.host}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">发送数据包:</span>
                      <span className="font-medium">{pingResult.data.packets_sent}个</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">接收数据包:</span>
                      <span className="font-medium">{pingResult.data.packets_received}个</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">丢包率:</span>
                      <span className={`font-medium ${
                        pingResult.data.packet_loss === '0.0%' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {pingResult.data.packet_loss}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">平均延迟:</span>
                      <span className="font-medium flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {pingResult.data.avg_latency}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>最小/最大:</span>
                      <span>{pingResult.data.min_latency} / {pingResult.data.max_latency}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-red-600 text-sm">
                  <p className="font-medium">测试失败: {pingResult.error}</p>
                  {pingResult.details && (
                    <p className="text-xs text-gray-500 mt-1">{pingResult.details}</p>
                  )}
                </div>
              )}

              {pingResult.success && pingResult.data && (
                <div className="text-xs text-gray-500 pt-2 border-t">
                  测试时间: {new Date(pingResult.data.timestamp).toLocaleString('zh-CN')}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 网站可访问性测试结果 */}
      {websiteTestResult && (
        <Card className="border-gray-200">
          <CardContent className="p-4">
            {websiteTestResult.success ? (
              <WebsiteAccessibilityResult data={websiteTestResult.data} />
            ) : (
              <div className="text-red-600 text-sm">
                <p className="font-medium flex items-center">
                  <XCircle className="h-4 w-4 mr-2" />
                  测试失败: {websiteTestResult.error}
                </p>
                {websiteTestResult.details && (
                  <p className="text-xs text-gray-500 mt-1">{websiteTestResult.details}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
     
    </div>
  );
} 