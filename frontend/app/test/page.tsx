import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center text-gray-900">
          CSS样式测试页面
        </h1>
        
        {/* 测试基础Tailwind样式 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-2">蓝色卡片</h2>
            <p className="text-blue-100">这是基础Tailwind CSS样式测试</p>
          </div>
          
          <div className="bg-green-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-2">绿色卡片</h2>
            <p className="text-green-100">测试颜色和布局</p>
          </div>
          
          <div className="bg-purple-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-2">紫色卡片</h2>
            <p className="text-purple-100">测试响应式设计</p>
          </div>
        </div>

        {/* 测试shadcn/ui组件 */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              shadcn/ui组件测试
              <Badge variant="default">正常</Badge>
            </CardTitle>
            <CardDescription>
              测试自定义UI组件是否正常渲染
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <Button variant="default">默认按钮</Button>
              <Button variant="secondary">次要按钮</Button>
              <Button variant="outline">轮廓按钮</Button>
              <Button variant="ghost">幽灵按钮</Button>
              <Button variant="destructive">危险按钮</Button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              <Badge variant="default">默认标签</Badge>
              <Badge variant="secondary">次要标签</Badge>
              <Badge variant="outline">轮廓标签</Badge>
              <Badge variant="destructive">危险标签</Badge>
            </div>
          </CardContent>
        </Card>

        {/* 测试CSS变量和主题 */}
        <Card>
          <CardHeader>
            <CardTitle>CSS变量测试</CardTitle>
            <CardDescription>检查主题变量是否正确加载</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-background border border-border p-4 rounded-md">
                <p className="text-foreground">背景色</p>
              </div>
              <div className="bg-primary text-primary-foreground p-4 rounded-md">
                <p>主色调</p>
              </div>
              <div className="bg-secondary text-secondary-foreground p-4 rounded-md">
                <p>次要色</p>
              </div>
              <div className="bg-muted text-muted-foreground p-4 rounded-md">
                <p>静音色</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* 返回首页按钮 */}
        <div className="text-center">
          <Button asChild>
            <Link href="/">返回首页</Link>
          </Button>
        </div>
      </div>
    </div>
  );
} 