'use client'

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Smartphone, Monitor, Tablet, Eye, Code, Palette } from "lucide-react";
import Link from "next/link";

export default function WelcomeDemoPage() {
  const [selectedDevice, setSelectedDevice] = useState<'mobile' | 'tablet' | 'desktop'>('mobile');

  const devices = {
    mobile: { width: 'w-80', height: 'h-[640px]', icon: Smartphone, label: '手机端' },
    tablet: { width: 'w-96', height: 'h-[640px]', icon: Tablet, label: '平板端' },
    desktop: { width: 'w-full', height: 'h-[640px]', icon: Monitor, label: '桌面端' }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">
            📱 手机端欢迎页面设计展示
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            时尚优雅 · 透明毛玻璃效果 · 圆角设计
          </p>
          
          {/* 设备选择器 */}
          <div className="flex justify-center space-x-4 mb-8">
            {Object.entries(devices).map(([key, device]) => {
              const IconComponent = device.icon;
              return (
                <Button
                  key={key}
                  variant={selectedDevice === key ? "default" : "outline"}
                  onClick={() => setSelectedDevice(key as any)}
                  className="flex items-center space-x-2"
                >
                  <IconComponent className="w-4 h-4" />
                  <span>{device.label}</span>
                </Button>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {/* 设备预览区域 */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <CardHeader className="text-center pb-4">
                <CardTitle className="flex items-center justify-center space-x-2">
                  <Eye className="w-5 h-5" />
                  <span>实时预览</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex justify-center">
                  <div className={`${devices[selectedDevice].width} ${devices[selectedDevice].height} bg-black rounded-3xl p-2 shadow-2xl`}>
                    <div className="w-full h-full bg-white rounded-2xl overflow-hidden">
                      <iframe
                        src="/"
                        className="w-full h-full border-0"
                        title="Welcome Page Preview"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 设计说明 */}
          <div className="space-y-6">
            {/* 设计特性 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Palette className="w-5 h-5" />
                  <span>设计特性</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
                    <span className="text-sm">毛玻璃背景效果</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
                    <span className="text-sm">圆角卡片设计</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"></div>
                    <span className="text-sm">渐变色彩搭配</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gradient-to-r from-green-500 to-teal-500 rounded-full"></div>
                    <span className="text-sm">流畅动画交互</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-full"></div>
                    <span className="text-sm">响应式布局</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 技术实现 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="w-5 h-5" />
                  <span>技术实现</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <Badge variant="secondary" className="w-full justify-start">
                    backdrop-blur-xl
                  </Badge>
                  <Badge variant="secondary" className="w-full justify-start">
                    bg-white/70
                  </Badge>
                  <Badge variant="secondary" className="w-full justify-start">
                    rounded-3xl
                  </Badge>
                  <Badge variant="secondary" className="w-full justify-start">
                    shadow-xl
                  </Badge>
                  <Badge variant="secondary" className="w-full justify-start">
                    gradient-to-br
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* 颜色方案 */}
            <Card>
              <CardHeader>
                <CardTitle>颜色方案</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <div className="w-full h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg"></div>
                    <p className="text-xs text-center text-gray-600">主色调</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-full h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-lg"></div>
                    <p className="text-xs text-center text-gray-600">辅助色</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-full h-8 bg-white/70 backdrop-blur-sm border rounded-lg"></div>
                    <p className="text-xs text-center text-gray-600">毛玻璃</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-full h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg"></div>
                    <p className="text-xs text-center text-gray-600">强调色</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 操作按钮 */}
            <div className="space-y-3">
              <Link href="/" className="block">
                <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  查看完整页面
                </Button>
              </Link>
              <Link href="/smart-diagnosis" className="block">
                <Button variant="outline" className="w-full">
                  体验AI诊断
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* GPT-4o 插画提示 */}
        <div className="mt-12 max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-center">🎨 GPT-4o Image 插画提示</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-800">主要背景插画</h3>
                  <div className="bg-gray-50 p-4 rounded-lg text-sm">
                    <p className="text-gray-700">
                      "Create a modern, elegant mobile welcome screen illustration for a network device monitoring app. 
                      The style should be glassmorphism with frosted glass effects, soft gradients from blue to purple, 
                      mobile-first vertical composition, clean and minimalist..."
                    </p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-800">功能图标插画</h3>
                  <div className="bg-gray-50 p-4 rounded-lg text-sm">
                    <p className="text-gray-700">
                      "Design a set of modern app icons for network monitoring features: 
                      WiFi Scanner Icon with concentric wifi signal waves in gradient blue-to-cyan, 
                      AI Diagnosis Icon with brain or shield symbol with circuit patterns..."
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-center">
                <Badge variant="outline" className="text-xs">
                  完整提示词请查看源代码注释
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
