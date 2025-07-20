'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, Activity, Timer, Wifi } from 'lucide-react';

interface PingConfigDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (config: PingConfig) => void;
}

export interface PingConfig {
  target: string;
  count: number;
  timeout: number;
  packetSize: number;
  interval: number;
  category: 'basic' | 'advanced' | 'preset';
}

// 自定义网站图标组件
const SiteIcon = ({ type, className }: { type: string; className?: string }) => {
  const iconProps = { className: className || "w-5 h-5" };
  
  switch (type) {
    case 'baidu':
      return (
        <img 
          src="https://www.baidu.com/favicon.ico" 
          alt="Baidu"
          className={iconProps.className}
          onError={(e) => {
            // 备用SVG图标
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
            target.nextElementSibling?.setAttribute('style', 'display: block');
          }}
        />
      );
    case 'google':
      return (
        <div className={`${iconProps.className} rounded-full bg-white flex items-center justify-center`}>
          <svg viewBox="0 0 24 24" className="w-4 h-4">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.15 2.31-5.15 5.15 0 1.42.58 2.71 1.53 3.65L5.97 14.02c-1.36-1.36-2.2-3.24-2.2-5.32C3.77 5.25 7.02 2 10.97 2c2.08 0 3.96.84 5.32 2.2l-.31.73zM12 8a1 1 0 0 1 1 1v6a1 1 0 0 1-2 0V9a1 1 0 0 1 1-1zm7.23 4.77c0 3.95-3.25 7.2-7.2 7.2-2.08 0-3.96-.84-5.32-2.2l1.36-1.36c.94.95 2.23 1.53 3.65 1.53 2.84 0 5.15-2.31 5.15-5.15 0-1.42-.58-2.71-1.53-3.65l1.36-1.36c1.36 1.36 2.2 3.24 2.2 5.32z"/>
          </svg>
        </div>
      );
    case 'tencent':
      return (
        <div className={`${iconProps.className} rounded-full bg-blue-500 flex items-center justify-center`}>
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="white">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
        </div>
      );
    case 'alibaba':
      return (
        <div className={`${iconProps.className} rounded-full bg-orange-500 flex items-center justify-center`}>
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="white">
            <path d="M15.98 3.93L14.62 5.3c-.94-.95-2.23-1.53-3.65-1.53-2.84 0-5.15 2.31-5.15 5.15 0 1.42.58 2.71 1.53 3.65L5.97 14.02c-1.36-1.36-2.2-3.24-2.2-5.32C3.77 5.25 7.02 2 10.97 2c2.08 0 3.96.84 5.32 2.2l-.31.73zM12 8a1 1 0 0 1 1 1v6a1 1 0 0 1-2 0V9a1 1 0 0 1 1-1zm7.23 4.77c0 3.95-3.25 7.2-7.2 7.2-2.08 0-3.96-.84-5.32-2.2l1.36-1.36c.94.95 2.23 1.53 3.65 1.53 2.84 0 5.15-2.31 5.15-5.15 0-1.42-.58-2.71-1.53-3.65l1.36-1.36c1.36 1.36 2.2 3.24 2.2 5.32z"/>
          </svg>
        </div>
      );
    case 'cloudflare':
      return (
        <div className={`${iconProps.className} rounded-full bg-orange-400 flex items-center justify-center`}>
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="white">
            <path d="M21.1 13.2c-.2-.6-.8-1-1.4-1h-2.9l-.4-1.5c-.6-2.2-2.6-3.7-4.9-3.7-2.1 0-4 1.3-4.7 3.3l-.3 1c-.1 0-.2 0-.3 0-1.7 0-3.2 1.4-3.2 3.2s1.4 3.2 3.2 3.2h13.1c1.1 0 2-.9 2-2 0-.4-.1-.8-.2-1.5zm-8.8-5.4c1.1 0 2.1.6 2.6 1.5l.2.8h-5.6l.2-.8c.5-.9 1.5-1.5 2.6-1.5z"/>
          </svg>
        </div>
      );
    case 'router':
      return (
        <div className={`${iconProps.className} rounded-full bg-gray-600 flex items-center justify-center`}>
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="white">
            <rect width="20" height="8" x="2" y="14" rx="2"/>
            <path d="M6.01 18H6"/>
            <path d="M10.01 18H10"/>
            <path d="M15 10v4"/>
            <path d="M17.84 7.17a4 4 0 0 0-5.66 0"/>
            <path d="M20.66 4.34a8 8 0 0 0-11.31 0"/>
          </svg>
        </div>
      );
    default:
      return <Wifi className={iconProps.className} />;
  }
};

export function PingConfigDialog({ isOpen, onClose, onSubmit }: PingConfigDialogProps) {
  const [activeCategory, setActiveCategory] = useState<'basic' | 'advanced' | 'preset'>('preset');
  const [config, setConfig] = useState<PingConfig>({
    target: '',
    count: 4,
    timeout: 5000,
    packetSize: 32,
    interval: 1000,
    category: 'preset'
  });
  const [gatewayIP, setGatewayIP] = useState<string>('获取中...');
  const [isLoadingGateway, setIsLoadingGateway] = useState(false);

  // 动态预设目标列表，包含真实网关IP和网站图标
  const presetTargets = [
    { 
      name: '百度', 
      value: 'baidu.com', 
      icon: 'baidu',
      description: '百度搜索引擎'
    },
    { 
      name: '谷歌DNS', 
      value: '8.8.8.8', 
      icon: 'google',
      description: 'Google公共DNS'
    },
    { 
      name: '腾讯DNS', 
      value: '119.29.29.29', 
      icon: 'tencent',
      description: '腾讯公共DNS'
    },
    { 
      name: '阿里DNS', 
      value: '223.5.5.5', 
      icon: 'alibaba',
      description: '阿里云公共DNS'
    },
    { 
      name: 'Cloudflare', 
      value: '1.1.1.1', 
      icon: 'cloudflare',
      description: 'Cloudflare DNS'
    },
    { 
      name: '本地网关', 
      value: gatewayIP, 
      icon: 'router',
      description: '本地路由器网关'
    }
  ];

  // 获取网关IP地址
  const fetchGatewayIP = async () => {
    try {
      setIsLoadingGateway(true);
      console.log('🔍 获取网关信息...');
      
      const response = await fetch('/api/gateway-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`API调用失败: ${response.status}`);
      }

      const result = await response.json();
      console.log('📡 网关信息响应:', result);

      if (result.success && result.data && result.data.gateway_ip) {
        setGatewayIP(result.data.gateway_ip);
        console.log('✅ 网关IP获取成功:', result.data.gateway_ip);
      } else {
        console.warn('⚠️ 未获取到网关IP，使用默认值');
        setGatewayIP('192.168.1.1');
      }
    } catch (error) {
      console.error('❌ 获取网关IP失败:', error);
      setGatewayIP('192.168.1.1'); // 使用常见的默认网关IP
    } finally {
      setIsLoadingGateway(false);
    }
  };

  // 重置表单当对话框打开时
  useEffect(() => {
    if (isOpen) {
      setActiveCategory('preset');
      setConfig({
        target: '',
        count: 4,
        timeout: 5000,
        packetSize: 32,
        interval: 1000,
        category: 'preset'
      });
      
      // 获取网关IP
      fetchGatewayIP();
    }
  }, [isOpen]);

  const handleCategoryChange = (category: 'basic' | 'advanced' | 'preset') => {
    setActiveCategory(category);
    setConfig(prev => ({ ...prev, category }));
  };

  const handlePresetSelect = (target: string) => {
    setConfig(prev => ({ ...prev, target }));
  };

  const handleSubmit = () => {
    if (!config.target.trim()) {
      alert('请选择或输入目标地址');
      return;
    }
    onSubmit(config);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center">
      {/* 背景遮罩 - 毛玻璃效果 */}
      <div 
        className="absolute inset-0 bg-black/30 backdrop-blur-md"
        onClick={onClose}
      />
      
      {/* 对话框容器 */}
      <div className="relative w-full max-w-sm mx-4 mb-0 bg-white rounded-t-2xl shadow-2xl transform transition-all duration-300 ease-out animate-in slide-in-from-bottom-4">
        {/* 顶部拖拽指示器 */}
        <div className="flex justify-center pt-2 pb-1">
          <div className="w-8 h-1 bg-gray-300 rounded-full"></div>
        </div>

        {/* 对话框头部 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">Ping测试配置</h2>
              <p className="text-xs text-gray-500">配置网络连通性测试参数</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* 类别选择标签 */}
        <div className="flex border-b border-gray-100">
          {[
            { id: 'preset' as const, name: '预设目标', icon: Activity },
            { id: 'basic' as const, name: '基础配置', icon: Activity },
            { id: 'advanced' as const, name: '高级配置', icon: Timer }
          ].map((category) => {
            const IconComponent = category.icon;
            return (
              <button
                key={category.id}
                onClick={() => handleCategoryChange(category.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-3 px-2 text-sm font-medium transition-all duration-200 ${
                  activeCategory === category.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <IconComponent className="w-3.5 h-3.5" />
                {category.name}
              </button>
            );
          })}
        </div>

        {/* 配置内容区域 */}
        <div className="p-4 min-h-[280px] max-h-[360px] overflow-y-auto">
          {activeCategory === 'preset' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                {presetTargets.map((preset) => {
                  const isSelected = config.target === preset.value;
                  const isGateway = preset.name === '本地网关';
                  
                  return (
                    <button
                      key={preset.value}
                      onClick={() => handlePresetSelect(preset.value)}
                      disabled={isGateway && isLoadingGateway}
                      className={`group relative p-3 rounded-xl border-2 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${
                        isSelected
                          ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-blue-100 shadow-md shadow-blue-200/50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gradient-to-br hover:from-blue-50 hover:to-blue-50 bg-white'
                      }`}
                    >
                      <div className="flex flex-col items-center gap-3">
                        <div className={`transition-all ${
                          isSelected 
                            ? 'scale-110' 
                            : 'group-hover:scale-105'
                        }`}>
                          <SiteIcon 
                            type={preset.icon} 
                            className="w-8 h-8"
                          />
                        </div>
                        <div className="text-center">
                          <div className={`text-sm font-semibold ${
                            isSelected ? 'text-blue-900' : 'text-gray-900'
                          }`}>
                            {preset.name}
                          </div>
                          <div className={`text-xs mt-1 font-mono break-all ${
                            isSelected ? 'text-blue-700' : 'text-gray-500'
                          }`}>
                            {isGateway && isLoadingGateway ? '获取中...' : preset.value}
                          </div>
                          <div className={`text-xs mt-1 ${
                            isSelected ? 'text-blue-600' : 'text-gray-400'
                          }`}>
                            {preset.description}
                          </div>
                        </div>
                      </div>
                      
                      {/* 选中状态指示器 */}
                      {isSelected && (
                        <div className="absolute -top-1 -right-1 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {activeCategory === 'basic' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  目标地址
                </label>
                <input
                  type="text"
                  value={config.target}
                  onChange={(e) => setConfig(prev => ({ ...prev, target: e.target.value }))}
                  placeholder="输入IP地址或域名，如：baidu.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ping次数: {config.count}
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={config.count}
                  onChange={(e) => setConfig(prev => ({ ...prev, count: parseInt(e.target.value) }))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1次</span>
                  <span>20次</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  超时时间: {config.timeout / 1000}秒
                </label>
                <input
                  type="range"
                  min="1000"
                  max="10000"
                  step="500"
                  value={config.timeout}
                  onChange={(e) => setConfig(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1秒</span>
                  <span>10秒</span>
                </div>
              </div>
            </div>
          )}

          {activeCategory === 'advanced' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  目标地址
                </label>
                <input
                  type="text"
                  value={config.target}
                  onChange={(e) => setConfig(prev => ({ ...prev, target: e.target.value }))}
                  placeholder="输入IP地址或域名"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ping次数
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={config.count}
                    onChange={(e) => setConfig(prev => ({ ...prev, count: parseInt(e.target.value) || 1 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    超时(ms)
                  </label>
                  <input
                    type="number"
                    min="1000"
                    max="30000"
                    step="500"
                    value={config.timeout}
                    onChange={(e) => setConfig(prev => ({ ...prev, timeout: parseInt(e.target.value) || 5000 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    数据包大小(bytes)
                  </label>
                  <input
                    type="number"
                    min="8"
                    max="1472"
                    value={config.packetSize}
                    onChange={(e) => setConfig(prev => ({ ...prev, packetSize: parseInt(e.target.value) || 32 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    间隔(ms)
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="5000"
                    step="100"
                    value={config.interval}
                    onChange={(e) => setConfig(prev => ({ ...prev, interval: parseInt(e.target.value) || 1000 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600">
                  <strong>提示：</strong>数据包大小建议保持32-64字节，间隔时间过短可能被目标服务器限制。
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="flex gap-2 p-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            取消
          </Button>
          <Button
            onClick={handleSubmit}
            className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white border-0"
            disabled={!config.target.trim()}
          >
            开始测试
          </Button>
        </div>
      </div>
    </div>
  );
} 