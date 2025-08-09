'use client';

import { useState } from 'react';
import { useChat } from 'ai/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChatInterface } from '@/components/ai-diagnosis/ChatInterface';
import { DiagnosisToolbar } from '@/components/ai-diagnosis/DiagnosisToolbar';
import { 
  Bot, 
  Activity, 
  CheckCircle,
  Settings,
  Wrench,
  Brain 
} from 'lucide-react';

export default function AIDiagnosisPage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [useMCPTools, setUseMCPTools] = useState(true); // 默认使用MCP工具

  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error,
    append
  } = useChat({
    api: useMCPTools ? '/api/ai-diagnosis-with-mcp' : '/api/ai-diagnosis',
    onFinish: () => {
      setIsAnalyzing(false);
    },
    onError: (error) => {
      console.error('AI诊断错误:', error);
      setIsAnalyzing(false);
    },
  });

  // 处理抓包完成回调
  const handlePacketCaptureCompleted = async (analysisResult: any) => {
    console.log('🎉 抓包分析完成，自动显示结果:', analysisResult);
    
    try {
      // 构建分析结果消息
      const analysisMessage = `📊 **抓包分析完成！**

## 🔍 会话信息
- **目标**: ${analysisResult.target}
- **模式**: ${analysisResult.mode}
- **时长**: ${analysisResult.duration}秒
- **捕获包数**: ${analysisResult.packets_captured || 0}个
- **网络接口**: ${analysisResult.interface}

## 🧠 AI智能分析结果

${analysisResult.ai_analysis || '暂无AI分析结果'}

## 📈 详细数据分析

\`\`\`json
{
  "type": "packet_capture_result",
  "data": ${JSON.stringify(analysisResult, null, 2)}
}
\`\`\`

---
*分析完成时间: ${new Date().toLocaleString()}*`;

      // 自动添加分析结果到对话中
      await append({
        role: 'assistant',
        content: analysisMessage
      });

    } catch (error) {
      console.error('❌ 显示抓包分析结果失败:', error);
      
      // 如果自动显示失败，显示简化版本
      await append({
        role: 'assistant',
        content: `抓包分析已完成！捕获了 ${analysisResult.packets_captured || 0} 个数据包。

\`\`\`json
{
  "type": "packet_capture_result",
  "data": ${JSON.stringify(analysisResult, null, 2)}
}
\`\`\``
      });
    }
  };

  const handleToolSelect = (tool: string) => {
    console.log('选择工具:', tool);
    // 可以在这里添加工具相关的逻辑
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col">
      {/* 页面顶部控制栏 */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Bot className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">大Ai哥装维智能体 </h1>
                <p className="text-sm text-gray-600">
                  {useMCPTools ? 'AI宽带网络诊断智能体' : 'AI宽带网络诊断智能体'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Button
                  variant={!useMCPTools ? "default" : "outline"}
                  size="sm"
                  onClick={() => setUseMCPTools(false)}
                  className="flex items-center space-x-1"
                >
                  <Brain className="h-4 w-4" />
                  <span>基础模式</span>
                </Button>
                <Button
                  variant={useMCPTools ? "default" : "outline"}
                  size="sm"
                  onClick={() => setUseMCPTools(true)}
                  className="flex items-center space-x-1"
                >
                  <Wrench className="h-4 w-4" />
                  <span>MCP模式</span>
                </Button>
              </div>
              
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <CheckCircle className="h-3 w-3 mr-1" />
                在线
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* 主要对话区域 */}
      <div className="flex-1 container mx-auto px-4 py-6 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-140px)]">
          {/* 左侧：AI 对话区域 */}
          <div className="lg:col-span-2">
            <Card className="h-full shadow-lg border-0">
              <CardHeader className="border-b bg-gray-50/50">
                <CardTitle className="flex items-center justify-between text-lg">
                  <span className="flex items-center space-x-2">
                    <Bot className="h-5 w-5 text-blue-600" />
                    <span>AI 网络诊断助手</span>
                    <Badge variant="outline" className={useMCPTools ? "bg-green-50 text-green-700" : "bg-blue-50 text-blue-700"}>
                      {useMCPTools ? (
                        <>
                          <Wrench className="h-3 w-3 mr-1" />
                          MCP工具
                        </>
                      ) : (
                        <>
                          <Brain className="h-3 w-3 mr-1" />
                          基础模式
                        </>
                      )}
                    </Badge>
                  </span>
                  {(isAnalyzing || isLoading) && (
                    <Badge variant="secondary" className="animate-pulse">
                      <Activity className="h-3 w-3 mr-1" />
                      AI 分析中...
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="h-full p-0">
                {error && (
                  <div className="p-4 bg-red-50 border-b border-red-200">
                    <div className="text-sm text-red-600">
                      连接错误: {error.message}
                    </div>
                  </div>
                )}
                <ChatInterface
                  messages={messages}
                  input={input}
                  handleInputChange={handleInputChange}
                  handleSubmit={(e) => {
                    setIsAnalyzing(true);
                    handleSubmit(e);
                  }}
                  isLoading={isLoading}
                  placeholder="请描述您遇到的网络问题 (例如: 网速缓慢、连接不稳定、无法访问特定网站等...)"
                  onPacketCaptureCompleted={handlePacketCaptureCompleted}
                  onToolSelect={handleToolSelect}
                />
              </CardContent>
            </Card>
          </div>

          {/* 右侧：诊断工具栏 */}
          <div className="lg:col-span-1">
            <DiagnosisToolbar 
              onToolSelect={handleToolSelect}
              isAnalyzing={isAnalyzing || isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
} 