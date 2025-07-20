'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, Minimize2, Maximize2, BarChart3, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PacketCaptureFullscreenDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onMinimize?: () => void;
}

export function PacketCaptureFullscreenDialog({
  isOpen,
  onClose,
  onMinimize
}: PacketCaptureFullscreenDialogProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [iframeKey, setIframeKey] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  // 重置状态当对话框打开时
  useEffect(() => {
    if (isOpen) {
      setIsMinimized(false);
      setIsLoading(true);
      setHasError(false);
      // 强制重新加载iframe
      setIframeKey(prev => prev + 1);
    }
  }, [isOpen]);

  const handleMinimize = () => {
    setIsMinimized(true);
    onMinimize?.();
  };

  const handleMaximize = () => {
    setIsMinimized(false);
  };

  const handleClose = () => {
    setIsMinimized(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* 全屏对话框 */}
      <div
        className={cn(
          "fixed inset-0 z-50 bg-white transition-all duration-300 ease-in-out",
          isMinimized ? "opacity-0 pointer-events-none" : "opacity-100"
        )}
      >
        {/* 头部工具栏 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">数据包分析</h2>
              <p className="text-xs text-gray-500">智能网络抓包分析工具</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* 最小化按钮 */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMinimize}
              className="h-8 w-8 p-0 hover:bg-gray-100"
              title="最小化"
            >
              <Minimize2 className="w-4 h-4" />
            </Button>

            {/* 关闭按钮 */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="h-8 w-8 p-0 hover:bg-gray-100"
              title="关闭"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* 内容区域 - 嵌入抓包页面 */}
        <div className="flex-1 h-[calc(100vh-73px)] bg-gray-50 relative">
          {/* 加载状态 */}
          {isLoading && (
            <div className="absolute inset-0 bg-white flex items-center justify-center z-10">
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">正在加载数据包分析工具...</p>
              </div>
            </div>
          )}

          {/* 错误状态 */}
          {hasError && (
            <div className="absolute inset-0 bg-white flex items-center justify-center z-10">
              <div className="text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <X className="w-8 h-8 text-red-500" />
                </div>
                <p className="text-gray-600 mb-4">数据包分析工具加载失败</p>
                <Button
                  onClick={() => {
                    setHasError(false);
                    setIsLoading(true);
                    setIframeKey(prev => prev + 1);
                  }}
                  className="bg-blue-500 hover:bg-blue-600 text-white"
                >
                  重新加载
                </Button>
              </div>
            </div>
          )}

          <iframe
            key={iframeKey}
            src="/network-capture-ai-test"
            className="w-full h-full border-0 bg-white"
            title="数据包分析工具"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-downloads"
            onLoad={() => {
              console.log('数据包分析页面加载完成');
              setIsLoading(false);
              setHasError(false);
            }}
            onError={() => {
              console.error('数据包分析页面加载失败');
              setIsLoading(false);
              setHasError(true);
            }}
          />
        </div>
      </div>

      {/* 最小化状态的浮动按钮 */}
      {isMinimized && (
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={handleMaximize}
            className="w-12 h-12  bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-full relative animate-pulse"
            title="展开数据包分析"
          >
            <Activity className="w-full h-full p-3" />
          </button>
        </div>
      )}
    </>
  );
}
