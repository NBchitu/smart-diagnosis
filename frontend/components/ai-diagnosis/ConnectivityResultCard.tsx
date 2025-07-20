'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Clock, 
  Network, 
  Wifi,
  Globe,
  Router,
  ChevronDown,
  ChevronUp,
  Signal
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConnectivityTest {
  name: string;
  status: 'success' | 'failed' | 'unknown';
  latency?: number | null;
  message: string;
}

interface ConnectivityDetails {
  local_network: boolean;
  internet_dns: boolean;
  internet_http: boolean;
  gateway_reachable: boolean;
  dns_resolution: boolean;
  external_ping: boolean;
  http_response: boolean;
}

interface GatewayInfo {
  ip?: string;
  interface?: string;
  reachable?: boolean;
}

interface LatencyInfo {
  gateway?: number;
  average_external?: number;
  [key: string]: number | undefined;
}

interface ConnectivitySummary {
  total_tests: number;
  passed_tests: number;
  success_rate: string;
}

interface ConnectivityResult {
  type: string;
  overall_status: string;
  status: string;
  message: string;
  details: ConnectivityDetails;
  gateway_info: GatewayInfo;
  latency: LatencyInfo;
  tests: ConnectivityTest[];
  summary: ConnectivitySummary;
  check_time: string;
  timestamp: string;
  error?: string;
}

interface ConnectivityResultCardProps {
  result: ConnectivityResult;
  className?: string;
}

export function ConnectivityResultCard({ result, className }: ConnectivityResultCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  // 获取整体状态信息
  const getOverallStatus = () => {
    switch (result.status) {
      case 'excellent':
        return {
          icon: <CheckCircle className="w-5 h-5 text-green-500" />,
          text: '连接优秀',
          color: 'bg-green-50 border-green-200',
          textColor: 'text-green-700'
        };
      case 'good':
        return {
          icon: <CheckCircle className="w-5 h-5 text-blue-500" />,
          text: '连接良好',
          color: 'bg-blue-50 border-blue-200',
          textColor: 'text-blue-700'
        };
      case 'limited':
        return {
          icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
          text: '连接受限',
          color: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-700'
        };
      case 'disconnected':
        return {
          icon: <XCircle className="w-5 h-5 text-red-500" />,
          text: '连接异常',
          color: 'bg-red-50 border-red-200',
          textColor: 'text-red-700'
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-5 h-5 text-gray-500" />,
          text: '检测失败',
          color: 'bg-gray-50 border-gray-200',
          textColor: 'text-gray-700'
        };
      default:
        return {
          icon: <AlertCircle className="w-5 h-5 text-gray-500" />,
          text: '状态未知',
          color: 'bg-gray-50 border-gray-200',
          textColor: 'text-gray-700'
        };
    }
  };

  // 获取测试项图标
  const getTestIcon = (testName: string) => {
    switch (testName) {
      case '网关连通性':
        return <Router className="w-4 h-4" />;
      case 'DNS解析':
        return <Globe className="w-4 h-4" />;
      case '外部网络ping':
        return <Signal className="w-4 h-4" />;
      case 'HTTP连通性':
        return <Network className="w-4 h-4" />;
      default:
        return <Wifi className="w-4 h-4" />;
    }
  };

  // 获取测试状态样式
  const getTestStatusStyle = (status: string) => {
    switch (status) {
      case 'success':
        return {
          icon: <CheckCircle className="w-4 h-4 text-green-500" />,
          badge: 'bg-green-100 text-green-800',
          text: '正常'
        };
      case 'failed':
        return {
          icon: <XCircle className="w-4 h-4 text-red-500" />,
          badge: 'bg-red-100 text-red-800',
          text: '异常'
        };
      default:
        return {
          icon: <AlertCircle className="w-4 h-4 text-gray-500" />,
          badge: 'bg-gray-100 text-gray-800',
          text: '未知'
        };
    }
  };

  const overallStatus = getOverallStatus();
  const successRate = parseFloat(result.summary.success_rate.replace('%', ''));

  return (
    <Card className={cn("w-full", className, overallStatus.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {overallStatus.icon}
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                连通性检查结果
              </CardTitle>
              <p className={cn("text-sm mt-1", overallStatus.textColor)}>
                {result.message}
              </p>
            </div>
          </div>
          <Badge 
            variant="outline"
            className={cn("text-xs", overallStatus.textColor)}
          >
            {overallStatus.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 整体状态和成功率 */}
        <div className="grid grid-cols-2 gap-4">
          {/* 成功率 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">成功率</span>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-gray-900">
                  {result.summary.success_rate}
                </span>
                <span className="text-sm text-gray-500">
                  ({result.summary.passed_tests}/{result.summary.total_tests})
                </span>
              </div>
              <Progress value={successRate} className="h-2" />
            </div>
          </div>

          {/* 网关信息 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Router className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">网关状态</span>
            </div>
            <div className="space-y-1">
              {result.gateway_info.ip ? (
                <div className="text-sm text-gray-600">
                  <div>IP: {result.gateway_info.ip}</div>
                  {result.gateway_info.interface && (
                    <div>接口: {result.gateway_info.interface}</div>
                  )}
                  {result.latency.gateway && (
                    <div>延迟: {result.latency.gateway.toFixed(1)}ms</div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">无网关信息</div>
              )}
            </div>
          </div>
        </div>

        {/* 详细测试结果 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-700">详细测试结果</h4>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
            >
              {showDetails ? '收起' : '展开'}
              {showDetails ? 
                <ChevronUp className="w-4 h-4" /> : 
                <ChevronDown className="w-4 h-4" />
              }
            </button>
          </div>

          {/* 测试项快速预览 */}
          {!showDetails && (
            <div className="grid grid-cols-2 gap-2">
              {result.tests.slice(0, 4).map((test, index) => {
                const testStatus = getTestStatusStyle(test.status);
                return (
                  <div key={index} className="flex items-center gap-2 text-xs">
                    {getTestIcon(test.name)}
                    {testStatus.icon}
                    <span className="text-gray-600">{test.name}</span>
                  </div>
                );
              })}
            </div>
          )}

          {/* 详细测试结果 */}
          {showDetails && (
            <div className="space-y-2">
              {result.tests.map((test, index) => {
                const testStatus = getTestStatusStyle(test.status);
                return (
                  <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                    <div className="flex items-center gap-2">
                      {getTestIcon(test.name)}
                      <span className="text-sm font-medium text-gray-700">{test.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {test.latency && (
                        <span className="text-xs text-gray-500">
                          {test.latency.toFixed(1)}ms
                        </span>
                      )}
                      <div className="flex items-center gap-1">
                        {testStatus.icon}
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs", testStatus.badge)}
                        >
                          {testStatus.text}
                        </Badge>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 延迟信息 */}
        {result.latency.average_external && (
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">网络延迟</span>
            </div>
            <div className="text-xs text-blue-700">
              外部网络平均延迟: {result.latency.average_external.toFixed(1)}ms
            </div>
          </div>
        )}

        {/* 错误信息 */}
        {result.error && (
          <div className="p-3 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-800">错误信息</span>
            </div>
            <div className="text-xs text-red-700">{result.error}</div>
          </div>
        )}

        {/* 检查时间 */}
        <div className="text-xs text-gray-500 text-center">
          检查时间: {new Date(result.check_time).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
} 