'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Zap, 
  Router, 
  Globe, 
  Shield, 
  BarChart3,
  Loader2,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

interface TestResult {
  success: boolean;
  data?: any;
  error?: string;
  details?: string;
  duration?: number;
}

export default function ToolsTestPage() {
  const [results, setResults] = useState<Record<string, TestResult>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [testTarget, setTestTarget] = useState('baidu.com');
  const [speedTestServers, setSpeedTestServers] = useState<any[]>([]);
  const [selectedServer, setSelectedServer] = useState<string>('');

  const tools = [
    {
      id: 'speed_test',
      name: '网络测速',
      icon: Zap,
      endpoint: '/api/speed-test',
      payload: {
        test_type: 'full',
        server_id: selectedServer || undefined
      }
    },
    {
      id: 'traceroute',
      name: '路由追踪',
      icon: Router,
      endpoint: '/api/traceroute',
      payload: { target: testTarget, max_hops: 15 }
    },
    {
      id: 'dns_test',
      name: 'DNS测试',
      icon: Globe,
      endpoint: '/api/dns-test',
      payload: { domain: testTarget, query_type: 'A' }
    },
    {
      id: 'port_scan',
      name: '端口扫描',
      icon: Shield,
      endpoint: '/api/port-scan',
      payload: { target: testTarget, ports: [80, 443, 22, 21] }
    },
    {
      id: 'ssl_check',
      name: 'SSL检查',
      icon: Shield,
      endpoint: '/api/ssl-check',
      payload: { hostname: testTarget, port: 443 }
    },
    {
      id: 'network_quality',
      name: '网络质量',
      icon: BarChart3,
      endpoint: '/api/network-quality',
      payload: { target: testTarget, duration: 30, interval: 5 }
    }
  ];

  const runTest = async (tool: any) => {
    const toolId = tool.id;
    setLoading(prev => ({ ...prev, [toolId]: true }));
    
    const startTime = Date.now();
    
    try {
      const response = await fetch(tool.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tool.payload),
      });

      const result = await response.json();
      const duration = Date.now() - startTime;

      setResults(prev => ({
        ...prev,
        [toolId]: {
          ...result,
          duration
        }
      }));

    } catch (error) {
      const duration = Date.now() - startTime;
      setResults(prev => ({
        ...prev,
        [toolId]: {
          success: false,
          error: '请求失败',
          details: error instanceof Error ? error.message : 'Unknown error',
          duration
        }
      }));
    } finally {
      setLoading(prev => ({ ...prev, [toolId]: false }));
    }
  };

  const getStatusIcon = (result?: TestResult) => {
    if (!result) return null;
    
    if (result.success) {
      return <CheckCircle className="w-4 h-4 text-green-600" />;
    } else {
      return <XCircle className="w-4 h-4 text-red-600" />;
    }
  };

  const getStatusColor = (result?: TestResult) => {
    if (!result) return 'bg-gray-100 text-gray-600';
    
    if (result.success) {
      return 'bg-green-100 text-green-700';
    } else {
      return 'bg-red-100 text-red-700';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="container mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">网络诊断工具测试</h1>
          <p className="text-gray-600">测试新实现的网络诊断工具是否正常工作</p>
        </div>

        {/* 测试目标设置 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>测试配置</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  测试目标
                </label>
                <Input
                  value={testTarget}
                  onChange={(e) => setTestTarget(e.target.value)}
                  placeholder="输入域名或IP地址"
                />
              </div>
              <Button
                onClick={() => {
                  // 清空之前的结果
                  setResults({});
                }}
                variant="outline"
              >
                重置结果
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 工具测试网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool) => {
            const IconComponent = tool.icon;
            const result = results[tool.id];
            const isLoading = loading[tool.id];

            return (
              <Card key={tool.id} className="relative">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <IconComponent className="w-5 h-5 text-blue-600" />
                      <span>{tool.name}</span>
                    </div>
                    {getStatusIcon(result)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* 测试按钮 */}
                    <Button
                      onClick={() => runTest(tool)}
                      disabled={isLoading}
                      className="w-full"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          测试中...
                        </>
                      ) : (
                        '开始测试'
                      )}
                    </Button>

                    {/* 结果显示 */}
                    {result && (
                      <div className="space-y-2">
                        <Badge className={getStatusColor(result)}>
                          {result.success ? '成功' : '失败'}
                        </Badge>
                        
                        {result.duration && (
                          <div className="flex items-center gap-1 text-sm text-gray-600">
                            <Clock className="w-3 h-3" />
                            <span>{result.duration}ms</span>
                          </div>
                        )}

                        {result.success && result.data && (
                          <div className="text-xs bg-green-50 p-2 rounded border">
                            {tool.id === 'speed_test' ? (
                              // 特殊处理测速结果显示
                              <div className="space-y-1">
                                <div className="font-medium text-green-700">测速结果:</div>
                                <div>📥 下载: {result.data.download_speed} Mbps</div>
                                <div>📤 上传: {result.data.upload_speed} Mbps</div>
                                <div>🏓 延迟: {result.data.ping} ms</div>
                                {result.data.server_info && (
                                  <div>🌐 服务器: {result.data.server_info.name} ({result.data.server_info.distance}km)</div>
                                )}
                                <div>🌍 ISP: {result.data.isp}</div>
                                <div>⏱️ 测试时长: {result.data.test_duration}s</div>
                              </div>
                            ) : (
                              // 其他工具的通用显示
                              <pre className="whitespace-pre-wrap overflow-auto max-h-32">
                                {JSON.stringify(result.data, null, 2)}
                              </pre>
                            )}
                          </div>
                        )}

                        {!result.success && (
                          <div className="text-xs bg-red-50 p-2 rounded border">
                            <div className="font-medium text-red-700">错误: {result.error}</div>
                            {result.details && (
                              <div className="text-red-600 mt-1">{result.details}</div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* 批量测试 */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>批量测试</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => {
                tools.forEach(tool => {
                  setTimeout(() => runTest(tool), Math.random() * 2000);
                });
              }}
              disabled={Object.values(loading).some(Boolean)}
              className="w-full"
            >
              {Object.values(loading).some(Boolean) ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  测试进行中...
                </>
              ) : (
                '运行所有测试'
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
