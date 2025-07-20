'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Wifi, Network, Activity, Zap, Shield, BarChart3, RefreshCw, CheckCircle, AlertTriangle, XCircle, Bot } from "lucide-react";
import Link from "next/link";
import { useNetworkConnectivity } from "@/hooks/useNetworkConnectivity";
import useWifiSignal from "@/hooks/useWifiSignal";
import { SignalLevelBadge } from "@/components/ui/signal-level-badge";
import { SmoothNumber } from "@/components/ui/smooth-number";

// 这是原来的首页内容备份，已被新的welcome页面替换
export default function OldHomePage() {
  const { result, isChecking, error, checkConnectivity } = useNetworkConnectivity();
  const { 
    wifiData, 
    isLoading: isWifiLoading, 
    error: wifiError, 
    refreshSignal, 
    isAutoRefreshing,
    lastUpdated 
  } = useWifiSignal(5000, true);

  const getStatusIcon = () => {
    if (isChecking) return <RefreshCw className="h-4 w-4 animate-spin" />;
    if (!result) return <Activity className="h-4 w-4 text-muted-foreground" />;
    
    switch (result.status) {
      case 'excellent':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'good':
        return <CheckCircle className="h-4 w-4 text-yellow-500" />;
      case 'limited':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'disconnected':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = () => {
    if (isChecking) return <Badge variant="secondary">检测中...</Badge>;
    if (!result) return <Badge variant="outline">未检测</Badge>;
    
    switch (result.status) {
      case 'excellent':
        return <Badge variant="default">优秀</Badge>;
      case 'good':
        return <Badge variant="secondary">良好</Badge>;
      case 'limited':
        return <Badge variant="outline">受限</Badge>;
      case 'disconnected':
      case 'error':
        return <Badge variant="destructive">异常</Badge>;
      default:
        return <Badge variant="outline">未知</Badge>;
    }
  };

  const getStatusText = () => {
    if (isChecking) return "正在检测...";
    if (error) return "检测失败";
    if (!result) return "点击检测";
    return result.message;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-4">
            网络设备检测面板
          </h1>
          <p className="text-lg text-gray-600">
            基于树莓派5的网络监测与诊断工具
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {/* WiFi扫描功能 */}
          <Link href="/wifi-scan" className="group">
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border-l-4 border-blue-500">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  📶
                </div>
                <h3 className="text-xl font-semibold text-gray-800 group-hover:text-blue-600">
                  WiFi 扫描分析
                </h3>
              </div>
              <p className="text-gray-600 mb-4">
                扫描周边WiFi网络，分析信道干扰，提供优化建议
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <div>✅ 周边网络检测</div>
                <div>✅ 信道干扰分析</div>
                <div>✅ 信号强度监测</div>
                <div>✅ 优化建议</div>
              </div>
            </div>
          </Link>

          {/* AI智能诊断 */}
          <Link href="/smart-diagnosis" className="group">
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border-l-4 border-green-500">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  🤖
                </div>
                <h3 className="text-xl font-semibold text-gray-800 group-hover:text-green-600">
                  AI 智能诊断
                </h3>
              </div>
              <p className="text-gray-600 mb-4">
                AI驱动的网络问题诊断与智能分析
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <div>✅ 智能问题诊断</div>
                <div>✅ 实时网络分析</div>
                <div>✅ 专业建议</div>
                <div>✅ 一键修复</div>
              </div>
            </div>
          </Link>

          {/* 功能测试 */}
          <Link href="/test" className="group">
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border-l-4 border-purple-500">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                  🔧
                </div>
                <h3 className="text-xl font-semibold text-gray-800 group-hover:text-purple-600">
                  功能测试
                </h3>
              </div>
              <p className="text-gray-600 mb-4">
                网络连接测试与系统功能验证
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <div>✅ 连接性测试</div>
                <div>✅ 网络速度测试</div>
                <div>✅ 系统状态检查</div>
                <div>✅ 功能验证</div>
              </div>
            </div>
          </Link>
        </div>

        {/* 快速开始 */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
              🚀 快速开始
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-blue-600">1</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">选择功能</h3>
                <p className="text-sm text-gray-600">
                  根据需要选择WiFi扫描、AI诊断或功能测试
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-green-600">2</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">开始检测</h3>
                <p className="text-sm text-gray-600">
                  点击扫描或诊断按钮，系统自动开始分析
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-purple-600">3</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">查看结果</h3>
                <p className="text-sm text-gray-600">
                  获取详细分析报告和优化建议
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 系统信息 */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-4 bg-white rounded-lg shadow-sm px-6 py-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">系统正常运行</span>
            </div>
            <div className="w-px h-4 bg-gray-300"></div>
            <div className="text-sm text-gray-500">
              适配树莓派5 | 移动端优化
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
