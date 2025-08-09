'use client';

import React, { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
// 暂时注释掉Sheet组件，使用简单的弹出层
// import {
//   Sheet,
//   SheetContent,
//   SheetDescription,
//   SheetHeader,
//   SheetTitle,
//   SheetTrigger,
// } from '@/components/ui/sheet';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Wifi,
  Activity,
  Globe,
  Router,
  Shield,
  BarChart3,
  Search,
  Grid3X3,
  Zap,
  Clock,
  Star,
  Filter,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';

// 工具定义接口
interface Tool {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet' | 'performance' | 'security' | 'monitoring';
  priority: 'high' | 'medium' | 'low';
  estimatedDuration: string;
  status: 'available' | 'developing' | 'beta';
  tags: string[];
}

// 工具面板属性
interface ToolsPanelProps {
  onToolSelect: (toolId: string) => void;
  disabled?: boolean;
}

// 工具数据配置
const TOOLS_DATA: Tool[] = [
  // 基础诊断工具
  {
    id: 'ping_test',
    name: 'Ping测试',
    icon: Activity,
    description: '测试网络连通性和延迟',
    category: 'network',
    priority: 'high',
    estimatedDuration: '5-10秒',
    status: 'available',
    tags: ['基础', '连通性', '延迟']
  },
  {
    id: 'speed_test',
    name: '网络测速',
    icon: Zap,
    description: '测试上传下载速度',
    category: 'performance',
    priority: 'high',
    estimatedDuration: '30-60秒',
    status: 'available',
    tags: ['性能', '速度', '带宽']
  },
  {
    id: 'wifi_scan',
    name: 'WiFi扫描',
    icon: Wifi,
    description: '扫描附近WiFi网络',
    category: 'wifi',
    priority: 'high',
    estimatedDuration: '10-15秒',
    status: 'available',
    tags: ['WiFi', '无线', '信号']
  },
  {
    id: 'connectivity_check',
    name: '连通性检查',
    icon: Globe,
    description: '检查网络连接状态',
    category: 'connectivity',
    priority: 'high',
    estimatedDuration: '15-20秒',
    status: 'available',
    tags: ['连通性', '网络', '检查']
  },
  // 高级诊断工具
  {
    id: 'traceroute',
    name: '路由追踪',
    icon: Router,
    description: '追踪数据包传输路径',
    category: 'network',
    priority: 'high',
    estimatedDuration: '15-30秒',
    status: 'available',
    tags: ['路由', '路径', '追踪']
  },
  {
    id: 'dns_test',
    name: 'DNS测试',
    icon: Globe,
    description: '测试域名解析速度',
    category: 'connectivity',
    priority: 'high',
    estimatedDuration: '10-20秒',
    status: 'available',
    tags: ['DNS', '解析', '域名']
  },
  {
    id: 'website_accessibility_test',
    name: '网站访问测试',
    icon: Globe,
    description: '多运营商网站访问对比',
    category: 'connectivity',
    priority: 'medium',
    estimatedDuration: '20-30秒',
    status: 'available',
    tags: ['网站', '访问', '运营商']
  },
  {
    id: 'packet_capture',
    name: '数据包分析',
    icon: BarChart3,
    description: '抓取和分析网络数据包',
    category: 'packet',
    priority: 'medium',
    estimatedDuration: '30-60秒',
    status: 'available',
    tags: ['数据包', '分析', '抓包']
  },
  // 专业工具
  {
    id: 'gateway_info',
    name: '网关信息',
    icon: Router,
    description: '获取网关配置信息',
    category: 'gateway',
    priority: 'medium',
    estimatedDuration: '3-5秒',
    status: 'available',
    tags: ['网关', '配置', '信息']
  },
  {
    id: 'port_scan',
    name: '端口扫描',
    icon: Shield,
    description: '检测目标主机开放端口',
    category: 'security',
    priority: 'medium',
    estimatedDuration: '20-40秒',
    status: 'available',
    tags: ['端口', '扫描', '安全']
  },
  {
    id: 'ssl_check',
    name: 'SSL检查',
    icon: Shield,
    description: '检查网站SSL证书状态',
    category: 'security',
    priority: 'medium',
    estimatedDuration: '5-10秒',
    status: 'available',
    tags: ['SSL', '证书', '安全']
  },
  {
    id: 'network_quality',
    name: '网络质量',
    icon: BarChart3,
    description: '持续监控网络质量',
    category: 'monitoring',
    priority: 'low',
    estimatedDuration: '60-120秒',
    status: 'available',
    tags: ['质量', '监控', '持续']
  }
];

// 分类配置
const CATEGORIES = {
  all: { name: '全部工具', icon: Grid3X3, color: 'bg-gray-100' },
  network: { name: '网络诊断', icon: Activity, color: 'bg-blue-100' },
  performance: { name: '性能测试', icon: Zap, color: 'bg-green-100' },
  wifi: { name: 'WiFi工具', icon: Wifi, color: 'bg-purple-100' },
  connectivity: { name: '连通性', icon: Globe, color: 'bg-cyan-100' },
  security: { name: '安全检测', icon: Shield, color: 'bg-red-100' },
  packet: { name: '数据包', icon: BarChart3, color: 'bg-orange-100' },
  gateway: { name: '网关配置', icon: Router, color: 'bg-indigo-100' },
  monitoring: { name: '监控分析', icon: BarChart3, color: 'bg-yellow-100' }
};

export function ToolsPanel({ onToolSelect, disabled = false }: ToolsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  // 处理工具选择
  const handleToolSelect = (toolId: string) => {
    onToolSelect(toolId);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* 触发按钮 */}
      <Button
        variant="outline"
        size="sm"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className="flex-shrink-0 group relative bg-white/80 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 border border-blue-200/50 hover:border-blue-300/70 rounded-xl px-2.5 py-1.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-lg backdrop-blur-sm"
        title="打开工具面板"
      >
        <Grid3X3 className="w-4 h-4 sm:mr-2 text-blue-600" />
        <span className="hidden sm:inline text-blue-700 font-medium">工具面板</span>
      </Button>

      {/* 弹出面板 - 移动端优化 */}
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <div
            className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />

          {/* 面板内容 - 从底部弹出，适合移动端 */}
          <div className="fixed inset-x-0 bottom-0 z-[101] bg-white rounded-t-2xl shadow-2xl max-h-[80vh] flex flex-col overflow-hidden animate-in slide-in-from-bottom duration-300">
            {/* 头部 */}
            <div className="p-4 border-b bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                    <Grid3X3 className="w-4 h-4 text-white" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">网络诊断工具</h2>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 p-0 rounded-full hover:bg-white/80 transition-colors"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-sm text-gray-600">
                选择合适的工具进行网络诊断和分析
              </p>
            </div>

            {/* 工具九宫格 */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="grid grid-cols-3 gap-3">
                {TOOLS_DATA.map((tool) => (
                  <MobileToolCard key={tool.id} tool={tool} onSelect={handleToolSelect} />
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// 移动端工具卡片组件 - 九宫格布局
function MobileToolCard({ tool, onSelect }: { tool: Tool; onSelect: (toolId: string) => void }) {
  const IconComponent = tool.icon;

  return (
    <div
      className="aspect-square p-3 rounded-xl border border-gray-200 hover:border-blue-300 bg-white hover:bg-gradient-to-br hover:from-blue-50 hover:to-purple-50 transition-all duration-200 cursor-pointer shadow-sm hover:shadow-lg active:scale-95 flex flex-col items-center justify-center text-center"
      onClick={() => onSelect(tool.id)}
    >
      {/* 工具图标 */}
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-2 shadow-lg shadow-blue-500/25">
        <IconComponent className="w-5 h-5 text-white" />
      </div>

      {/* 工具名称 */}
      <h4 className="font-medium text-xs text-gray-900 mb-1 leading-tight">{tool.name}</h4>

      {/* 状态标识 */}
      <div className="flex items-center justify-center">
        <span
          className={cn(
            "px-1.5 py-0.5 rounded-full text-xs font-medium",
            getStatusStyle(tool.status)
          )}
        >
          {getStatusText(tool.status)}
        </span>
      </div>
    </div>
  );
}

// 辅助函数 - 移动端优化
function getStatusStyle(status: string) {
  switch (status) {
    case 'available':
      return 'bg-green-100 text-green-700';
    case 'developing':
      return 'bg-amber-100 text-amber-700';
    case 'beta':
      return 'bg-blue-100 text-blue-700';
    default:
      return 'bg-gray-100 text-gray-600';
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'available': return '可用';
    case 'developing': return '开发中';
    case 'beta': return '测试版';
    default: return '未知';
  }
}
