'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import TextareaAutosize from 'react-textarea-autosize';
import { Send, Bot, User, Loader2, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ToolRecommendationPanel } from './ToolRecommendationPanel';
import { PingResultCard } from './PingResultCard';
import { PacketCaptureResultCard } from './PacketCaptureResultCard';
import { PacketCaptureFullscreenDialog } from './PacketCaptureFullscreenDialog';

// 消息类型定义
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  type?: 'text' | 'tool_recommendation' | 'tool_result';
  data?: any;
}

// 工具推荐数据接口
interface ToolRecommendationData {
  analysis: string;
  reasoning: string;
  urgency: 'high' | 'medium' | 'low';
  recommendations: any[];
  timestamp: string;
}

interface SmartDiagnosisChatInterfaceProps {
  placeholder?: string;
}

export function SmartDiagnosisChatInterface({
  placeholder = "描述您遇到的网络问题，AI将为您推荐合适的诊断工具..."
}: SmartDiagnosisChatInterfaceProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isPacketCaptureDialogOpen, setIsPacketCaptureDialogOpen] = useState(false);

  // 自动滚动到底部
  const scrollToBottom = useCallback(() => {
    if (scrollAreaRef.current) {
      requestAnimationFrame(() => {
        const scrollElement = scrollAreaRef.current;
        if (scrollElement) {
          // 直接滚动到底部
          scrollElement.scrollTo({
            top: scrollElement.scrollHeight,
            behavior: 'smooth'
          });
          
          // 调试信息
          console.log('📜 滚动到底部:', {
            scrollHeight: scrollElement.scrollHeight,
            scrollTop: scrollElement.scrollTop,
            clientHeight: scrollElement.clientHeight
          });
        }
      });
    }
  }, []);

  // 消息变化时滚动
  useEffect(() => {
    const timeoutId = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, scrollToBottom]);

  // 加载状态变化时滚动
  useEffect(() => {
    if (!isLoading && !isAnalyzing) {
      const timeoutId = setTimeout(scrollToBottom, 200);
      return () => clearTimeout(timeoutId);
    }
  }, [isLoading, isAnalyzing, scrollToBottom]);

  // 消息ID计数器，确保ID唯一性
  const messageIdCounter = useRef(0);

  // 添加消息
  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    // 生成唯一ID：时间戳 + 计数器 + 随机字符
    const uniqueId = `${Date.now()}_${++messageIdCounter.current}_${Math.random().toString(36).substr(2, 9)}`;
    
    const newMessage: ChatMessage = {
      ...message,
      id: uniqueId,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  }, []);

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    
    // 添加用户消息
    addMessage({
      role: 'user',
      content: userMessage,
      type: 'text'
    });

    try {
      setIsAnalyzing(true);
      
      // 添加分析中的占位消息
      const analysisMessageId = addMessage({
        role: 'assistant',
        content: '正在分析您的问题并推荐合适的诊断工具...',
        type: 'text'
      });

      // 调用AI工具推荐API
      console.log('🧠 开始AI分析和工具推荐...');
      const response = await fetch('/api/ai-tool-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('工具推荐API调用失败');
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        // 移除分析中的占位消息
        setMessages(prev => prev.filter(msg => msg.id !== analysisMessageId));
        
        // 添加AI分析结果
        addMessage({
          role: 'assistant',
          content: `基于您的问题"${userMessage}"，我分析后推荐以下诊断工具：`,
          type: 'text'
        });

        // 添加工具推荐面板
        addMessage({
          role: 'system',
          content: '',
          type: 'tool_recommendation',
          data: result.data
        });

      } else {
        throw new Error(result.error || '工具推荐失败');
      }

    } catch (error) {
      console.error('❌ 工具推荐失败:', error);
      
      // 移除分析中的消息并添加错误消息
      setMessages(prev => prev.filter(msg => !msg.content.includes('正在分析')));
      
      addMessage({
        role: 'assistant',
        content: `抱歉，分析您的问题时出现错误：${(error as Error).message}。请重试或直接使用具体的诊断工具。`,
        type: 'text'
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 处理输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (formRef.current) {
        formRef.current.requestSubmit();
      }
    }
  };

  // 重新分析
  const handleRefreshAnalysis = async (originalData: ToolRecommendationData) => {
    try {
      setIsLoading(true);
      
      // 找到最后一个用户消息
      const lastUserMessage = [...messages].reverse().find(msg => msg.role === 'user');
      if (!lastUserMessage) {
        throw new Error('找不到原始问题');
      }

      addMessage({
        role: 'assistant',
        content: '正在重新分析并更新工具推荐...',
        type: 'text'
      });

      // 重新调用API
      const response = await fetch('/api/ai-tool-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: lastUserMessage.content }),
      });

      const result = await response.json();
      
      if (result.success && result.data) {
        addMessage({
          role: 'system',
          content: '',
          type: 'tool_recommendation',
          data: result.data
        });
      } else {
        throw new Error(result.error || '重新分析失败');
      }

    } catch (error) {
      console.error('❌ 重新分析失败:', error);
      addMessage({
        role: 'assistant',
        content: `重新分析失败：${(error as Error).message}`,
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理工具执行
  const handleToolExecute = (toolId: string, parameters: Record<string, any>) => {
    console.log('🔧 开始执行工具:', toolId, parameters);
    
    addMessage({
      role: 'assistant',
      content: `正在执行 ${toolId} 工具...`,
      type: 'text'
    });
  };

  // 处理工具结果
  const handleToolResult = (toolId: string, result: any) => {
    console.log('✅ 工具执行完成:', toolId, result);
    
    // 根据工具类型添加相应的结果卡片
    if (result.success && result.data) {
      if (toolId === 'ping' && result.data.type === 'ping_result') {
        addMessage({
          role: 'assistant',
          content: `Ping 测试完成：`,
          type: 'text'
        });
        
        addMessage({
          role: 'system',
          content: '',
          type: 'tool_result',
          data: { type: 'ping_result', result: result.data }
        });
      } else if (toolId === 'packet_capture' && result.data.type === 'packet_capture_result') {
        addMessage({
          role: 'assistant',
          content: `数据包分析完成：`,
          type: 'text'
        });
        
        addMessage({
          role: 'system',
          content: '',
          type: 'tool_result',
          data: { type: 'packet_capture_result', result: result.data }
        });
      } else {
        // 通用结果显示
        addMessage({
          role: 'assistant',
          content: `工具 ${toolId} 执行完成。\n\n结果：${JSON.stringify(result.data, null, 2)}`,
          type: 'text'
        });
      }
    } else {
      addMessage({
        role: 'assistant',
        content: `工具 ${toolId} 执行失败：${result.error || '未知错误'}`,
        type: 'text'
      });
    }
  };

  // 渲染消息
  const renderMessage = (message: ChatMessage, index: number) => {
    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';
    const isSystem = message.role === 'system';

    if (isSystem && message.type === 'tool_recommendation') {
      return (
        <div key={message.id} className="p-4">
          <ToolRecommendationPanel
            data={message.data}
            onRefresh={() => handleRefreshAnalysis(message.data)}
            onToolExecute={handleToolExecute}
            onToolResult={handleToolResult}
            onPacketCaptureOpen={() => setIsPacketCaptureDialogOpen(true)}
            isLoading={isLoading}
          />
        </div>
      );
    }

    if (isSystem && message.type === 'tool_result') {
      return (
        <div key={message.id} className="p-4">
          {message.data.type === 'ping_result' && (
            <PingResultCard result={message.data.result} />
          )}
          {message.data.type === 'packet_capture_result' && (
            <PacketCaptureResultCard result={message.data.result} />
          )}
        </div>
      );
    }

    return (
      <div
        key={message.id}
        className={cn(
          "flex gap-3 p-4",
          isUser && "bg-blue-50",
          isAssistant && "bg-gray-50"
        )}
      >
        <div className="flex-shrink-0">
          {isUser && (
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
          {isAssistant && (
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
          )}
        </div>
        
        <div className="flex-1 space-y-2">
          <div className="text-sm font-medium text-gray-900">
            {isUser && '您'}
            {isAssistant && 'AI 助手'}
          </div>
          
          <div className="prose prose-sm max-w-none">
            <div className="text-gray-700 whitespace-pre-wrap">
              {message.content}
            </div>
          </div>
          
          <div className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div 
        className="flex-1 p-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100" 
        ref={scrollAreaRef}
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center max-w-md">
              <Zap className="w-12 h-12 mx-auto mb-4 text-blue-500" />
              <h3 className="text-lg font-semibold mb-2">智能网络诊断助手</h3>
              <p className="text-sm text-gray-600 mb-4">
                描述您的网络问题，AI将智能分析并推荐最合适的诊断工具
              </p>
              <div className="text-xs text-gray-400 space-y-1">
                <p>✨ AI智能分析故障原因</p>
                <p>🎯 精准推荐诊断工具</p>
                <p>🔧 一键执行网络测试</p>
                <p>📊 可视化结果展示</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-0">
            {messages.map(renderMessage)}
            
            {isAnalyzing && (
              <div className="flex gap-3 p-4 bg-blue-50">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 mb-2">AI 助手</div>
                  <div className="flex items-center space-x-2 text-blue-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">正在智能分析您的问题...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="border-t bg-white p-4">
        <form ref={formRef} onSubmit={handleSubmit} className="flex gap-2" suppressHydrationWarning={true}>
          <div className="flex-1 relative">
            <TextareaAutosize
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              minRows={1}
              maxRows={4}
              disabled={isLoading || isAnalyzing}
              suppressHydrationWarning={true}
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading || isAnalyzing || !input.trim()}
            size="sm"
            className="px-3"
          >
            {(isLoading || isAnalyzing) ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
        
        {/* 快速示例 */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500">快速开始:</span>
          {[
            '网络连接很慢',
            'WiFi信号不稳定',
            '无法访问某个网站',
            '网络经常断线'
          ].map((example) => (
            <button
              key={example}
              onClick={() => setInput(example)}
              className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-600 transition-colors"
              disabled={isLoading || isAnalyzing}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* 数据包分析全屏对话框 */}
      <PacketCaptureFullscreenDialog
        isOpen={isPacketCaptureDialogOpen}
        onClose={() => setIsPacketCaptureDialogOpen(false)}
        onMinimize={() => setIsPacketCaptureDialogOpen(false)}
      />
    </div>
  );
}