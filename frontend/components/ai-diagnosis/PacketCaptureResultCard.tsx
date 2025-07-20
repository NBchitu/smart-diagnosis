'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Network, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Globe,
  Server,
  Zap,
  ChevronDown,
  ChevronUp,
  Monitor,
  Shield,
  TrendingUp,
  Database
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PacketCaptureAnalysis {
  summary: {
    total_packets: number;
    protocols: Record<string, number>;
    top_sources: Record<string, number>;
    top_destinations: Record<string, number>;
  };
  connections: Array<{
    src: string;
    dst: string;
    protocol: string;
    packet_count: number;
    flags: string[];
    avg_response_time?: string;
  }>;
  dns_queries: Array<{
    domain: string;
    response_time: string;
    status: string;
    resolved_ip?: string;
  }>;
  http_requests: Array<{
    method: string;
    url: string;
    status_code: number;
    response_time: string;
    size?: string;
  }>;
  problems_detected: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    count: number;
    recommendation: string;
  }>;
}

interface PacketCaptureResult {
  session_id: string;
  target: string;
  mode: string;
  status: string;
  duration: number;
  packets_captured: number;
  interface: string;
  start_time: string;
  analysis: PacketCaptureAnalysis;
  recommendations: string[];
  error?: string;
}

interface PacketCaptureResultCardProps {
  result: PacketCaptureResult;
  className?: string;
}

export function PacketCaptureResultCard({ result, className }: PacketCaptureResultCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'connections' | 'dns' | 'http' | 'problems'>('overview');

  // 获取状态信息
  const getStatusInfo = () => {
    switch (result.status) {
      case 'completed':
        return {
          icon: <CheckCircle className="w-5 h-5 text-green-500" />,
          text: '分析完成',
          color: 'bg-green-50 border-green-200'
        };
      case 'running':
        return {
          icon: <Activity className="w-5 h-5 text-blue-500 animate-pulse" />,
          text: '抓包中',
          color: 'bg-blue-50 border-blue-200'
        };
      case 'stopped':
        return {
          icon: <Monitor className="w-5 h-5 text-yellow-500" />,
          text: '已停止',
          color: 'bg-yellow-50 border-yellow-200'
        };
      case 'error':
        return {
          icon: <XCircle className="w-5 h-5 text-red-500" />,
          text: '分析失败',
          color: 'bg-red-50 border-red-200'
        };
      default:
        return {
          icon: <Monitor className="w-5 h-5 text-gray-500" />,
          text: '未知状态',
          color: 'bg-gray-50 border-gray-200'
        };
    }
  };

  // 获取严重程度颜色
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-blue-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  // 获取模式显示名称
  const getModeDisplayName = (mode: string) => {
    const modeNames: Record<string, string> = {
      'domain': '域名分析',
      'port': '端口监控',
      'web': 'Web流量',
      'diagnosis': '综合诊断',
      'auto': '智能模式'
    };
    return modeNames[mode] || mode;
  };

  const statusInfo = getStatusInfo();
  const protocolEntries = Object.entries(result.analysis.summary.protocols);
  const totalProblems = result.analysis.problems_detected.length;
  const highPriorityProblems = result.analysis.problems_detected.filter(p => p.severity === 'high').length;

  return (
    <Card className={cn("w-full", className, statusInfo.color)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {statusInfo.icon}
            <div>
              <CardTitle className="text-lg font-semibold text-gray-900">
                网络抓包分析
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                目标: {result.target} | 模式: {getModeDisplayName(result.mode)}
              </p>
            </div>
          </div>
          <Badge 
            variant={result.status === 'completed' ? 'default' : result.status === 'error' ? 'destructive' : 'secondary'}
            className="text-xs"
          >
            {statusInfo.text}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 主要统计信息 */}
        <div className="grid grid-cols-2 gap-4">
          {/* 数据包统计 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">捕获数据包</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-gray-900">
                {result.packets_captured.toLocaleString()}
              </span>
              <span className="text-sm text-gray-500">个</span>
            </div>
          </div>

          {/* 抓包时长 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">抓包时长</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-gray-900">
                {result.duration}
              </span>
              <span className="text-sm text-gray-500">秒</span>
            </div>
          </div>
        </div>

        {/* 协议分布 */}
        {protocolEntries.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">协议分布</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm">
              {protocolEntries.map(([protocol, count]) => (
                <div key={protocol} className="text-center p-2 bg-gray-50 rounded">
                  <div className="font-medium text-gray-900">{count}</div>
                  <div className="text-gray-500">{protocol}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 问题检测摘要 */}
        {totalProblems > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">问题检测</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                总计 {totalProblems} 个问题
              </Badge>
              {highPriorityProblems > 0 && (
                <Badge variant="destructive" className="text-xs">
                  {highPriorityProblems} 个高优先级
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* 会话信息 */}
        <div className="text-xs text-gray-500 space-y-1">
          <div>会话ID: {result.session_id}</div>
          <div>网络接口: {result.interface}</div>
          <div>开始时间: {new Date(result.start_time).toLocaleString()}</div>
        </div>

        {/* 详细信息切换按钮 */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <span>{showDetails ? '收起详细分析' : '查看详细分析'}</span>
          {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {/* 详细信息 */}
        {showDetails && (
          <div className="space-y-4 pt-3 border-t">
            {/* 标签页导航 */}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              {[
                { key: 'overview', label: '概览', icon: TrendingUp },
                { key: 'connections', label: '连接', icon: Network },
                { key: 'dns', label: 'DNS', icon: Globe },
                { key: 'http', label: 'HTTP', icon: Server },
                { key: 'problems', label: '问题', icon: AlertTriangle }
              ].map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key as any)}
                  className={cn(
                    "flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium transition-colors",
                    activeTab === key
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  )}
                >
                  <Icon className="w-3 h-3" />
                  {label}
                </button>
              ))}
            </div>

            {/* 标签页内容 */}
            <div className="min-h-[200px]">
              {activeTab === 'overview' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">流量概览</h4>
                  
                  {/* 主要来源 */}
                  {Object.keys(result.analysis.summary.top_sources).length > 0 && (
                    <div>
                      <h5 className="text-xs font-medium text-gray-600 mb-2">主要来源地址</h5>
                      <div className="space-y-1">
                        {Object.entries(result.analysis.summary.top_sources).slice(0, 3).map(([ip, count]) => (
                          <div key={ip} className="flex items-center justify-between text-sm">
                            <span className="font-mono text-gray-600">{ip}</span>
                            <span className="font-medium">{count} 个包</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 主要目标 */}
                  {Object.keys(result.analysis.summary.top_destinations).length > 0 && (
                    <div>
                      <h5 className="text-xs font-medium text-gray-600 mb-2">主要目标地址</h5>
                      <div className="space-y-1">
                        {Object.entries(result.analysis.summary.top_destinations).slice(0, 3).map(([ip, count]) => (
                          <div key={ip} className="flex items-center justify-between text-sm">
                            <span className="font-mono text-gray-600">{ip}</span>
                            <span className="font-medium">{count} 个包</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'connections' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">网络连接分析</h4>
                  {result.analysis.connections.length > 0 ? (
                    <div className="space-y-2">
                      {result.analysis.connections.slice(0, 5).map((conn, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-mono text-gray-900">{conn.src} → {conn.dst}</span>
                            <Badge variant="outline" className="text-xs">{conn.protocol}</Badge>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>{conn.packet_count} 个包</span>
                            {conn.avg_response_time && <span>平均响应: {conn.avg_response_time}</span>}
                            {conn.flags.length > 0 && <span>标志: {conn.flags.join(', ')}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">未检测到连接信息</p>
                  )}
                </div>
              )}

              {activeTab === 'dns' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">DNS 查询分析</h4>
                  {result.analysis.dns_queries.length > 0 ? (
                    <div className="space-y-2">
                      {result.analysis.dns_queries.map((query, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-900">{query.domain}</span>
                            <Badge 
                              variant={query.status === 'success' ? 'default' : 'destructive'} 
                              className="text-xs"
                            >
                              {query.status}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>响应时间: {query.response_time}</span>
                            {query.resolved_ip && <span>解析IP: {query.resolved_ip}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">未检测到DNS查询</p>
                  )}
                </div>
              )}

              {activeTab === 'http' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">HTTP 请求分析</h4>
                  {result.analysis.http_requests.length > 0 ? (
                    <div className="space-y-2">
                      {result.analysis.http_requests.map((req, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-900">{req.method} {req.url}</span>
                            <Badge 
                              variant={req.status_code < 400 ? 'default' : 'destructive'} 
                              className="text-xs"
                            >
                              {req.status_code}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span>响应时间: {req.response_time}</span>
                            {req.size && <span>大小: {req.size}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">未检测到HTTP请求</p>
                  )}
                </div>
              )}

              {activeTab === 'problems' && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-700">问题检测与建议</h4>
                  {result.analysis.problems_detected.length > 0 ? (
                    <div className="space-y-3">
                      {result.analysis.problems_detected.map((problem, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={cn("text-xs", getSeverityColor(problem.severity))}>
                              {problem.severity.toUpperCase()}
                            </Badge>
                            <span className="text-sm font-medium text-gray-900">{problem.type}</span>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{problem.description}</p>
                          <p className="text-xs text-gray-600">出现次数: {problem.count}</p>
                          <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-800">
                            <strong>建议:</strong> {problem.recommendation}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">未检测到网络问题</p>
                  )}

                  {/* 总体建议 */}
                  {result.recommendations.length > 0 && (
                    <div className="mt-4">
                      <h5 className="text-xs font-medium text-gray-600 mb-2">优化建议</h5>
                      <div className="space-y-1">
                        {result.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start gap-2 text-sm">
                            <Shield className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 错误信息 */}
        {result.error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm">
            <div className="flex items-center gap-2 text-red-600">
              <XCircle className="w-4 h-4" />
              <span className="font-medium">分析错误</span>
            </div>
            <p className="text-red-700 mt-1">{result.error}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 