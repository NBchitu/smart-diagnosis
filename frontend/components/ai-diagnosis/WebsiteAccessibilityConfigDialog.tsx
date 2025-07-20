'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { X, Globe, ExternalLink, Sparkles } from 'lucide-react';

interface WebsiteAccessibilityConfigDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (config: WebsiteAccessibilityConfig) => void;
}

export interface WebsiteAccessibilityConfig {
  url: string;
  includeScreenshot: boolean;
}

// 预设网站配置
const presetWebsites = [
  {
    name: '百度',
    url: 'baidu.com',
    icon: '🔍',
    description: '搜索引擎'
  },
  {
    name: '腾讯',
    url: 'qq.com',
    icon: '🐧',
    description: '社交平台'
  },
  {
    name: '阿里巴巴',
    url: 'taobao.com',
    icon: '🛒',
    description: '电商平台'
  },
  {
    name: '新浪',
    url: 'sina.com.cn',
    icon: '📰',
    description: '新闻门户'
  },
  {
    name: '网易',
    url: '163.com',
    icon: '📧',
    description: '门户网站'
  },
  {
    name: 'GitHub',
    url: 'github.com',
    icon: '💻',
    description: '代码托管'
  }
];

export function WebsiteAccessibilityConfigDialog({ isOpen, onClose, onSubmit }: WebsiteAccessibilityConfigDialogProps) {
  const [url, setUrl] = useState('');
  const [includeScreenshot, setIncludeScreenshot] = useState(false);
  const [activeTab, setActiveTab] = useState<'preset' | 'custom'>('preset');

  // 重置表单
  useEffect(() => {
    if (isOpen) {
      setUrl('');
      setIncludeScreenshot(false);
      setActiveTab('preset');
    }
  }, [isOpen]);

  const handleSubmit = () => {
    if (!url.trim()) return;
    
    onSubmit({
      url: url.trim(),
      includeScreenshot
    });
    onClose();
  };

  const handlePresetSelect = (presetUrl: string) => {
    setUrl(presetUrl);
    setActiveTab('custom');
  };

  const formatUrl = (inputUrl: string) => {
    let formatted = inputUrl.trim();
    // 移除协议前缀
    formatted = formatted.replace(/^https?:\/\//, '');
    // 移除末尾斜杠
    formatted = formatted.replace(/\/$/, '');
    return formatted;
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatUrl(e.target.value);
    setUrl(formatted);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/20 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white rounded-t-2xl shadow-2xl animate-in slide-in-from-bottom-4 duration-300">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
              <Globe className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">网站可访问性测试</h3>
              <p className="text-xs text-gray-500">对比不同运营商网络访问情况</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0 hover:bg-gray-100"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* 标签页 */}
        <div className="flex border-b border-gray-100">
          <button
            onClick={() => setActiveTab('preset')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === 'preset'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Sparkles className="w-4 h-4 inline mr-1" />
            常用网站
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === 'custom'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <ExternalLink className="w-4 h-4 inline mr-1" />
            自定义URL
          </button>
        </div>

        {/* 内容区域 */}
        <div className="p-4 max-h-80 overflow-y-auto">
          {activeTab === 'preset' && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600 mb-3">选择要测试的网站：</p>
              <div className="grid grid-cols-2 gap-2">
                {presetWebsites.map((website) => (
                  <button
                    key={website.url}
                    onClick={() => handlePresetSelect(website.url)}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50/50 transition-colors group"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{website.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-gray-900 group-hover:text-blue-700">
                          {website.name}
                        </div>
                        <div className="text-xs text-gray-500 truncate">
                          {website.url}
                        </div>
                        <div className="text-xs text-gray-400">
                          {website.description}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'custom' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  网站地址
                </label>
                <Input
                  placeholder="例如: baidu.com 或 github.com"
                  value={url}
                  onChange={handleUrlChange}
                  className="w-full"
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-1">
                  无需输入 http:// 或 https:// 前缀
                </p>
              </div>

              {/* 高级选项 */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">高级选项</h4>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeScreenshot}
                    onChange={(e) => setIncludeScreenshot(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">包含网页截图</span>
                  <span className="text-xs text-gray-400">(可能增加测试时间)</span>
                </label>
              </div>
            </div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="p-4 border-t border-gray-100 bg-gray-50/50">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              取消
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!url.trim()}
              className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white border-0"
            >
              开始测试
            </Button>
          </div>
          {url && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              将测试: <span className="font-mono text-blue-600">{url}</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
