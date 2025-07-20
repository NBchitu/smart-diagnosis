'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Brain, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle2,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ToolRecommendationCard } from './ToolRecommendationCard';

// 工具推荐数据接口
interface ToolRecommendation {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'wifi' | 'connectivity' | 'gateway' | 'packet' | 'diagnosis';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  estimatedDuration: string;
  parameters: {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    defaultValue?: any;
    options?: string[];
    required: boolean;
    description: string;
  }[];
  apiEndpoint: string;
  examples: string[];
}

interface ToolRecommendationData {
  analysis: string;
  reasoning: string;
  urgency: 'high' | 'medium' | 'low';
  recommendations: ToolRecommendation[];
  timestamp: string;
}

interface ToolRecommendationPanelProps {
  data: ToolRecommendationData;
  onRefresh?: () => void;
  onToolExecute?: (toolId: string, parameters: Record<string, any>) => void;
  onToolResult?: (toolId: string, result: any) => void;
  isLoading?: boolean;
}

export function ToolRecommendationPanel({
  data,
  onRefresh,
  onToolExecute,
  onToolResult,
  isLoading = false
}: ToolRecommendationPanelProps) {
  const [isAnalysisExpanded, setIsAnalysisExpanded] = useState(false);
  const [executedTools, setExecutedTools] = useState<Set<string>>(new Set());

  // 获取紧急程度样式
  const getUrgencyStyle = () => {
    switch (data.urgency) {
      case 'high':
        return 'border-red-300 bg-red-50';
      case 'medium':
        return 'border-yellow-300 bg-yellow-50';
      case 'low':
        return 'border-blue-300 bg-blue-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  // 获取紧急程度Badge
  const getUrgencyBadge = () => {
    switch (data.urgency) {
      case 'high':
        return (
          <Badge variant="destructive" className="flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>紧急</span>
          </Badge>
        );
      case 'medium':
        return (
          <Badge variant="default" className="bg-yellow-600 flex items-center space-x-1">
            <Lightbulb className="w-3 h-3" />
            <span>一般</span>
          </Badge>
        );
      case 'low':
        return (
          <Badge variant="secondary" className="flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>较低</span>
          </Badge>
        );
      default:
        return null;
    }
  };

  // 处理工具执行
  const handleToolExecute = (toolId: string, parameters: Record<string, any>) => {
    setExecutedTools(prev => new Set(prev).add(toolId));
    if (onToolExecute) {
      onToolExecute(toolId, parameters);
    }
  };

  // 处理工具结果
  const handleToolResult = (toolId: string, result: any) => {
    if (onToolResult) {
      onToolResult(toolId, result);
    }
  };

  return (
    <div className="space-y-4">
      {/* AI分析结果面板 */}
      <Card className={cn("border-2", getUrgencyStyle())}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">AI 诊断分析</h3>
              {getUrgencyBadge()}
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                onClick={onRefresh}
                variant="outline"
                size="sm"
                disabled={isLoading}
                className="flex items-center space-x-1"
              >
                <RefreshCw className={cn("w-3 h-3", isLoading && "animate-spin")} />
                <span>重新分析</span>
              </Button>
              
              <Button
                onClick={() => setIsAnalysisExpanded(!isAnalysisExpanded)}
                variant="ghost"
                size="sm"
                className="flex items-center space-x-1"
              >
                <span>详情</span>
                {isAnalysisExpanded ? (
                  <ChevronUp className="w-3 h-3" />
                ) : (
                  <ChevronDown className="w-3 h-3" />
                )}
              </Button>
            </div>
          </div>

          {/* 简要分析 */}
          <div className="text-sm text-gray-700 mb-3">
            {data.analysis}
          </div>

          {/* 展开的详细分析 */}
          {isAnalysisExpanded && (
            <div className="border-t pt-3 space-y-3">
              <div>
                <h4 className="font-medium text-sm text-gray-900 mb-2">推荐理由</h4>
                <p className="text-sm text-gray-600">{data.reasoning}</p>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>分析时间: {new Date(data.timestamp).toLocaleString()}</span>
                <span>推荐工具数: {data.recommendations.length}</span>
              </div>
            </div>
          )}

          {/* 快速统计 */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t">
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              <span>高优先级: {data.recommendations.filter(r => r.priority === 'high').length}</span>
              <span>中优先级: {data.recommendations.filter(r => r.priority === 'medium').length}</span>
              <span>低优先级: {data.recommendations.filter(r => r.priority === 'low').length}</span>
            </div>
            <div className="text-xs text-gray-500">
              已执行: {executedTools.size} / {data.recommendations.length}
            </div>
          </div>
        </div>
      </Card>

      {/* 推荐工具标题 */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">推荐诊断工具</h3>
        <Badge variant="outline" className="text-xs">
          {data.recommendations.length} 个工具
        </Badge>
      </div>

      {/* 工具卡片网格 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data.recommendations.map((recommendation) => (
          <ToolRecommendationCard
            key={recommendation.id}
            recommendation={recommendation}
            onExecute={handleToolExecute}
            onResult={handleToolResult}
            disabled={isLoading}
          />
        ))}
      </div>

      {/* 空状态 */}
      {data.recommendations.length === 0 && (
        <Card className="p-8 text-center">
          <div className="text-gray-400 mb-3">
            <Brain className="w-12 h-12 mx-auto mb-2" />
            <p className="text-sm">未找到推荐的诊断工具</p>
          </div>
          <Button onClick={onRefresh} variant="outline" size="sm">
            重新分析
          </Button>
        </Card>
      )}

      {/* 提示信息 */}
      <div className="text-xs text-gray-500 text-center">
        💡 点击工具卡片的"立即执行"按钮可快速运行，或展开"参数"配置详细选项
      </div>
    </div>
  );
} 