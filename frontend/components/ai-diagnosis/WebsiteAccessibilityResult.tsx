import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertCircle, Globe, Clock, Server } from 'lucide-react';

interface WebsiteAccessibilityResultProps {
  data: {
    url: string;
    test_time: string;
    results: Array<{
      carrier: string;
      description: string;
      dns_servers: string[];
      accessible: boolean;
      status_code: number | null;
      response_time: number | null;
      error: string | null;
      content_length: number | null;
      final_url: string | null;
      ip_address: string | null;
      headers: Record<string, string>;
      screenshot_available: boolean;
      screenshot_url: string | null;
    }>;
  };
}

const WebsiteAccessibilityResult: React.FC<WebsiteAccessibilityResultProps> = ({ data }) => {
  const getStatusIcon = (accessible: boolean, error: string | null) => {
    if (accessible) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (error) {
      return <XCircle className="w-4 h-4 text-red-500" />;
    } else {
      return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (accessible: boolean, error: string | null) => {
    if (accessible) {
      return <Badge className="bg-green-100 text-green-800 border-green-200">可访问</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800 border-red-200">不可访问</Badge>;
    }
  };

  const getCarrierColor = (carrier: string) => {
    switch (carrier) {
      case '本地网络':
        return 'bg-blue-50 border-blue-200';
      case '中国电信':
        return 'bg-cyan-50 border-cyan-200';
      case '中国联通':
        return 'bg-red-50 border-red-200';
      case '中国移动':
        return 'bg-green-50 border-green-200';
      case '公共DNS':
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const accessibleCount = data.results.filter(r => r.accessible).length;
  const totalCount = data.results.length;
  const accessibilityRate = ((accessibleCount / totalCount) * 100).toFixed(1);

  return (
    <div className="space-y-4">
      {/* 测试概览 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            网站可访问性对比测试结果
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{data.url}</div>
              <div className="text-sm text-gray-500">测试网站</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{accessibleCount}/{totalCount}</div>
              <div className="text-sm text-gray-500">可访问运营商数量</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{accessibilityRate}%</div>
              <div className="text-sm text-gray-500">总体可访问率</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 各运营商测试结果 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.results.map((result, index) => (
          <Card key={index} className={`border-2 ${getCarrierColor(result.carrier)}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(result.accessible, result.error)}
                  <CardTitle className="text-lg">{result.carrier}</CardTitle>
                </div>
                {getStatusBadge(result.accessible, result.error)}
              </div>
              <div className="text-sm text-gray-600">{result.description}</div>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* 基本信息 */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="font-medium text-gray-700">状态码</div>
                  <div className="text-gray-600">
                    {result.status_code ? (
                      <span className={result.status_code === 200 ? 'text-green-600' : 'text-red-600'}>
                        {result.status_code}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-700">响应时间</div>
                  <div className="text-gray-600 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {result.response_time ? `${result.response_time}ms` : '-'}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-700">IP地址</div>
                  <div className="text-gray-600">
                    {result.ip_address || '-'}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-700">内容大小</div>
                  <div className="text-gray-600">
                    {result.content_length ? `${(result.content_length / 1024).toFixed(1)}KB` : '-'}
                  </div>
                </div>
              </div>

              {/* DNS服务器 */}
              {result.dns_servers.length > 0 && (
                <div>
                  <div className="font-medium text-gray-700 text-sm mb-1">DNS服务器</div>
                  <div className="flex flex-wrap gap-1">
                    {result.dns_servers.map((dns, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        <Server className="w-3 h-3 mr-1" />
                        {dns}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* 错误信息 */}
              {result.error && (
                <div className="bg-red-50 border border-red-200 rounded p-2">
                  <div className="font-medium text-red-800 text-sm">错误信息</div>
                  <div className="text-red-700 text-xs">{result.error}</div>
                </div>
              )}

              {/* 最终URL（如果有重定向） */}
              {result.final_url && result.final_url !== data.url && (
                <div className="bg-blue-50 border border-blue-200 rounded p-2">
                  <div className="font-medium text-blue-800 text-sm">重定向到</div>
                  <div className="text-blue-700 text-xs break-all">{result.final_url}</div>
                </div>
              )}
            </CardContent>
            {/* 网页截图展示 */}
            {result.screenshot_available && result.screenshot_url && (
              <div className="mt-2 flex flex-col items-center">
                <div className="font-medium text-gray-700 text-xs mb-1">网页截图</div>
                <a href={result.screenshot_url} target="_blank" rel="noopener noreferrer">
                  <img
                    src={result.screenshot_url}
                    alt={`网页截图-${result.carrier}`}
                    className="rounded border border-gray-200 shadow-sm max-w-full max-h-48 object-contain hover:scale-105 transition-transform duration-200"
                    loading="lazy"
                  />
                </a>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* 测试时间 */}
      <div className="text-center text-sm text-gray-500">
        测试时间: {new Date(data.test_time).toLocaleString('zh-CN')}
      </div>
    </div>
  );
};

export default WebsiteAccessibilityResult; 