'use client';

import { StepwiseDiagnosisInterface } from '@/components/ai-diagnosis/StepwiseDiagnosisInterface';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Bot, Sparkles, Shield, Activity } from 'lucide-react';
import Link from 'next/link';

export default function SmartDiagnosisPage() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-400/10 to-pink-400/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-cyan-400/5 to-blue-400/5 rounded-full blur-3xl"></div>
      </div>

      {/* 浮动装饰元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-2 h-2 bg-blue-400/30 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-1 h-1 bg-purple-400/30 rounded-full animate-ping"></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-indigo-400/20 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 right-10 w-2 h-2 bg-pink-400/30 rounded-full animate-pulse"></div>
      </div>

      <div className="relative z-10 flex flex-col h-screen">
        {/* 优雅的页面头部 */}
        <div className="bg-white/70 backdrop-blur-xl border-b border-white/20 shadow-sm flex-shrink-0">
          <div className="max-w-6xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              {/* 返回按钮和标题 */}
              <div className="flex items-center space-x-4">
                <Link href="/">
                  <Button variant="ghost" size="sm" className="rounded-xl hover:bg-white/50">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    返回
                  </Button>
                </Link>
                <div className="flex items-center space-x-3">
                  <div>
                    <h1 className="text-xl font-bold text-gray-800 tracking-tight">
                      AI 智能诊断
                    </h1>
                  </div>
                </div>
              </div>

              {/* 状态标识 */}
              <div className="flex items-center space-x-3">
            
                <Badge variant="secondary" className="bg-green-100/60 backdrop-blur-sm border-0 text-green-700">
                  <Activity className="w-3 h-3 mr-1" />
                  在线
                </Badge>
              </div>
            </div>
          </div>
        </div>

        {/* 主要内容区域 */}
        <div className="flex-1 w-full overflow-hidden">
          <div className="h-full max-w-6xl mx-auto px-4 py-6">
            <div className="h-full bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl shadow-black/5 border border-white/20 overflow-hidden">
              <StepwiseDiagnosisInterface />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}