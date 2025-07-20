'use client';

import { useState } from 'react';
import { useChat } from 'ai/react';
import { ChatInterface } from '@/components/ai-diagnosis/ChatInterface';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Wrench, Zap, AlertCircle } from 'lucide-react';

export default function TestAIV5Page() {
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testResult, setTestResult] = useState<string>('');

  // 使用新的 AI SDK v5 API 端点
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/ai-diagnosis-v5-mcp',
    onError: (error) => {
      console.error('Chat error:', error);
      setTestStatus('error');
      setTestResult(error.message);
    },
    onFinish: (message) => {
      console.log('Chat finished:', message);
      setTestStatus('success');
    },
  });

  const runQuickTest = async () => {
    setTestStatus('testing');
    setTestResult('');
    
    // 模拟发送一个测试消息
    const testMessage = "请测试ping baidu.com";
    
    try {
      // 这里我们手动触发一个消息来测试
      handleInputChange({ target: { value: testMessage } } as React.ChangeEvent<HTMLTextAreaElement>);
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) {
          form.requestSubmit();
        }
      }, 100);
    } catch (error) {
      setTestStatus('error');
      setTestResult((error as Error).message);
    }
  };

  const getStatusBadge = () => {
    switch (testStatus) {
      case 'testing':
        return <Badge variant="secondary" className="animate-pulse">测试中...</Badge>;
      case 'success':
        return <Badge variant="default" className="bg-green-600">成功 ✅</Badge>;
      case 'error':
        return <Badge variant="destructive">错误 ❌</Badge>;
      default:
        return <Badge variant="outline">待测试</Badge>;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 顶部状态栏 */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Zap className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">AI SDK v5 + MCP 测试</h1>
            </div>
            {getStatusBadge()}
          </div>
          
          <div className="flex items-center gap-3">
            <Button 
              onClick={runQuickTest}
              disabled={isLoading || testStatus === 'testing'}
              size="sm"
              variant="outline"
            >
              <Bot className="w-4 h-4 mr-2" />
              快速测试
            </Button>
          </div>
        </div>
        
        {error && (
          <div className="mt-2 flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span>连接错误: {error.message}</span>
          </div>
        )}
      </div>

      {/* 功能特性说明 */}
      <div className="bg-blue-50 border-b px-6 py-3">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Wrench className="w-4 h-4 text-blue-600" />
            <span className="font-medium">原生 MCP 工具调用</span>
          </div>
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-green-600" />
            <span className="font-medium">多步骤推理</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-purple-600" />
            <span className="font-medium">流式响应</span>
          </div>
          <div className="text-xs text-gray-500">
            支持的工具: ping, wifi扫描, 连通性检查, 网关信息, 数据包分析
          </div>
        </div>
      </div>

      {/* 聊天界面 */}
      <div className="flex-1 flex">
        <div className="flex-1">
          <ChatInterface
            messages={messages}
            input={input}
            handleInputChange={handleInputChange}
            handleSubmit={handleSubmit}
            isLoading={isLoading}
            placeholder="测试 AI SDK v5 + MCP 集成 (例如: ping 测试, WiFi 扫描, 网络诊断等)"
          />
        </div>
        
        {/* 侧边栏：测试指引 */}
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">
          <h3 className="font-semibold text-gray-900 mb-3">测试指引</h3>
          
          <div className="space-y-4">
            <Card className="p-3">
              <h4 className="font-medium text-sm text-gray-900 mb-2">🏓 Ping 测试</h4>
              <p className="text-xs text-gray-600 mb-2">测试网络连通性</p>
              <code className="text-xs bg-gray-100 p-1 rounded block">
                ping baidu.com
              </code>
            </Card>
            
            <Card className="p-3">
              <h4 className="font-medium text-sm text-gray-900 mb-2">📶 WiFi 扫描</h4>
              <p className="text-xs text-gray-600 mb-2">扫描周围 WiFi 网络</p>
              <code className="text-xs bg-gray-100 p-1 rounded block">
                扫描WiFi
              </code>
            </Card>
            
            <Card className="p-3">
              <h4 className="font-medium text-sm text-gray-900 mb-2">🌐 连通性检查</h4>
              <p className="text-xs text-gray-600 mb-2">检查互联网连接</p>
              <code className="text-xs bg-gray-100 p-1 rounded block">
                检查网络连通性
              </code>
            </Card>
            
            <Card className="p-3">
              <h4 className="font-medium text-sm text-gray-900 mb-2">🔍 数据包分析</h4>
              <p className="text-xs text-gray-600 mb-2">智能网络抓包</p>
              <code className="text-xs bg-gray-100 p-1 rounded block">
                抓包分析 sina.com
              </code>
            </Card>
            
            <Card className="p-3">
              <h4 className="font-medium text-sm text-gray-900 mb-2">🖥️ 网关信息</h4>
              <p className="text-xs text-gray-600 mb-2">获取路由器信息</p>
              <code className="text-xs bg-gray-100 p-1 rounded block">
                查看网关信息
              </code>
            </Card>
          </div>
          
          <div className="mt-6 p-3 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-sm text-blue-900 mb-2">✨ 新特性</h4>
            <ul className="text-xs text-blue-800 space-y-1">
              <li>• 真正的工具调用消息类型</li>
              <li>• 多步骤推理能力</li>
              <li>• 原生 MCP 协议支持</li>
              <li>• 自动工具参数验证</li>
              <li>• 更好的错误处理</li>
            </ul>
          </div>
          
          {testResult && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-sm text-gray-900 mb-2">测试结果</h4>
              <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                {testResult}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 