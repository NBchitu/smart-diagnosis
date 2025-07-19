# 步进式诊断实现详细文档

## 🎯 功能概述

智能诊断助手2.0现已升级为**步进式诊断模式**，改变了原有的一次性工具推荐方式，采用逐步引导的专业诊断流程。

## 🔄 流程对比

### 原有流程
1. 用户描述问题
2. AI分析问题
3. **一次性展示所有推荐工具**
4. 用户自行选择执行

### 新的步进式流程
1. 用户描述问题
2. AI分析问题并制定诊断计划
3. **第一步工具推荐** → 执行 → AI评估结果
4. **询问用户是否继续**
5. 用户确认 → **第二步工具推荐** → 执行 → AI评估
6. 重复直到所有步骤完成
7. **生成最终诊断报告**

## 🏗️ 技术架构

### 后端API: `/api/ai-diagnosis-stepwise`

```typescript
// 请求类型
interface StepwiseDiagnosisRequest {
  message: string;
  action: 'analyze' | 'get_next_step' | 'evaluate_result';
  context?: DiagnosisContext;
  toolResult?: any;
}

// 响应类型
interface StepwiseDiagnosisResponse {
  success: boolean;
  data?: {
    type: 'analysis' | 'next_step' | 'evaluation' | 'completion';
    // ... 其他字段
  };
  error?: string;
}
```

### 前端组件: `StepwiseDiagnosisInterface`

```typescript
// 主要状态
interface DiagnosisContext {
  originalProblem: string;
  currentStep: number;
  totalSteps: number;
  executedTools: ExecutedTool[];
  isComplete: boolean;
}
```

## 🔧 核心功能

### 1. 问题分析 (analyze)
- 接收用户问题描述
- AI分析问题性质和复杂度
- 制定2-4步的诊断计划
- 确定工具执行顺序

### 2. 获取下一步 (get_next_step)
- 根据当前进度推荐下一个工具
- 提供工具执行的原因说明
- 判断是否到达诊断结束

### 3. 结果评估 (evaluate_result)
- 专业分析工具执行结果
- 提供发现和建议
- 判断是否需要继续下一步

## 📋 支持的诊断工具

| 工具ID | 工具名称 | 适用场景 | 优先级 |
|--------|----------|----------|--------|
| ping | Ping测试 | 基础连通性检查 | 高 |
| connectivity_check | 连通性检查 | 综合网络状态 | 高 |
| wifi_scan | WiFi扫描 | 无线网络问题 | 中 |
| gateway_info | 网关信息 | 路由和网关问题 | 中 |
| packet_capture | 数据包分析 | 复杂网络问题 | 低 |

## 🎨 用户界面设计

### 进度指示器
```typescript
// 显示当前步骤进度
<div className="诊断进度: {currentStep + 1} / {totalSteps}">
  {/* 圆点进度条 */}
</div>
```

### 消息类型
- `analysis`: AI问题分析结果
- `step_tool`: 步骤工具推荐
- `tool_result`: 工具执行结果
- `evaluation`: AI结果评估
- `next_step_prompt`: 下一步确认提示
- `completion`: 诊断完成报告

## 🔄 完整流程示例

### 用户问题: "网络连接很慢"

#### 步骤1: 问题分析
```json
{
  "analysis": "检测到网络性能问题，需要进行基础连通性和速度测试",
  "totalSteps": 3,
  "diagnosticPlan": ["ping", "connectivity_check", "gateway_info"]
}
```

#### 步骤2: 第一步工具 - Ping测试
```json
{
  "nextTool": {
    "id": "ping",
    "name": "Ping测试",
    "reasoning": "首先测试基础连通性和网络延迟"
  }
}
```

#### 步骤3: 结果评估
```json
{
  "evaluation": {
    "summary": "Ping测试显示网络延迟较高",
    "findings": ["平均延迟180ms", "有30%丢包率"],
    "recommendations": ["检查网络连接", "重启路由器"],
    "needsNextStep": true
  }
}
```

#### 步骤4: 用户确认继续
```typescript
// 显示继续提示
<Button onClick={handleNextStep}>进行下一步</Button>
```

#### 步骤5: 第二步工具 - 连通性检查
```json
{
  "nextTool": {
    "id": "connectivity_check",
    "reasoning": "进行全面的网络连通性分析"
  }
}
```

#### 步骤6: 最终报告
```json
{
  "finalSummary": "综合诊断结果显示网络质量不佳，建议检查硬件连接..."
}
```

## 📊 AI提示词设计

### 问题分析提示
```typescript
const analysisPrompt = `
作为网络诊断专家，请分析用户的网络问题并制定逐步诊断计划。

用户问题：${message}

可用的诊断工具：
1. ping - 测试网络连通性和延迟
2. wifi_scan - 扫描WiFi网络
3. connectivity_check - 全面连通性检查
4. gateway_info - 获取网关信息
5. packet_capture - 数据包分析

请以JSON格式回复，包含：
{
  "analysis": "问题分析",
  "reasoning": "诊断思路",
  "urgency": "high|medium|low",
  "totalSteps": 步骤数量,
  "diagnosticPlan": ["tool1", "tool2", "tool3"],
  "stepReasons": ["步骤1原因", "步骤2原因", "步骤3原因"]
}
`;
```

### 结果评估提示
```typescript
const evaluationPrompt = `
作为网络诊断专家，请评估工具执行结果并给出专业分析。

原始问题：${context.originalProblem}
当前步骤：${context.currentStep + 1}/${context.totalSteps}
执行工具：${toolId}
工具结果：${JSON.stringify(result, null, 2)}

请以JSON格式回复：
{
  "summary": "结果总结",
  "findings": ["发现1", "发现2", "发现3"],
  "recommendations": ["建议1", "建议2"],
  "needsNextStep": true/false,
  "nextStepReason": "如果需要下一步，说明原因"
}
`;
```

## 🧪 测试场景

### 测试用例1: 基础连通性问题
```
输入: "无法访问网站"
期望流程: ping → connectivity_check → 完成
```

### 测试用例2: WiFi问题
```
输入: "WiFi信号不稳定"
期望流程: wifi_scan → ping → gateway_info → 完成
```

### 测试用例3: 复杂网络问题
```
输入: "网络时快时慢，不稳定"
期望流程: ping → connectivity_check → packet_capture → 完成
```

## 💡 设计亮点

### 1. 专业引导
- 按照专业网络诊断流程设计
- 从基础到高级的合理工具顺序
- 每步都有明确的诊断目的

### 2. 智能评估
- AI对每步结果进行专业分析
- 提供具体的发现和建议
- 智能判断是否需要继续

### 3. 用户体验
- 进度可视化显示
- 清晰的步骤说明
- 用户可控的节奏

### 4. 可扩展性
- 易于添加新的诊断工具
- 支持自定义诊断流程
- 模块化的组件设计

## 🔍 技术细节

### 状态管理
```typescript
// 使用React useState管理诊断上下文
const [context, setContext] = useState<DiagnosisContext>({
  originalProblem: '',
  currentStep: 0,
  totalSteps: 0,
  executedTools: [],
  isComplete: false
});
```

### 消息ID生成
```typescript
// 确保消息ID唯一性
const uniqueId = `${Date.now()}_${++messageIdCounter.current}_${Math.random().toString(36).substr(2, 9)}`;
```

### 工具结果处理
```typescript
// 统一的工具结果处理
const handleToolResult = (toolId: string, result: any) => {
  // 1. 更新执行工具列表
  // 2. 显示结果卡片
  // 3. 请求AI评估
  // 4. 显示继续提示
};
```

## 🚀 部署和使用

### 1. 环境要求
- Node.js 18+
- AI API密钥 (OpenRouter/OpenAI)
- 网络诊断工具后端

### 2. 配置更新
```bash
# 确保AI配置正确
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

### 3. 页面访问
```
http://localhost:3000/smart-diagnosis
```

## 📈 性能优化

### 1. 响应速度
- 异步API调用
- 消息渐进式显示
- 减少不必要的重渲染

### 2. 用户体验
- 加载状态指示
- 错误处理和重试
- 响应式设计

### 3. 资源管理
- 组件懒加载
- 内存泄漏防护
- 合理的状态清理

## 🔮 未来扩展

### 1. 高级功能
- 自定义诊断流程
- 历史记录和复用
- 批量诊断支持

### 2. 智能优化
- 学习用户习惯
- 动态调整诊断计划
- 预测性故障检测

### 3. 集成扩展
- 第三方工具接入
- 云端诊断服务
- 移动端适配

---

**实现状态**: ✅ 已完成  
**测试状态**: 🧪 待验证  
**文档状态**: 📝 已完成  

这个步进式诊断系统提供了更专业、更友好的网络故障诊断体验，符合用户的期望和专业网络诊断的最佳实践。 