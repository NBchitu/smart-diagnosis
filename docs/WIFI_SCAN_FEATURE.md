# WiFi扫描功能文档

## 功能概述

WiFi扫描功能提供了完整的无线网络分析能力，包括周边网络检测、信道干扰分析、网络质量评估和优化建议。

### 核心功能

1. **周边网络扫描** - 检测并列出所有可用的WiFi网络
2. **当前网络分析** - 显示当前连接网络的详细信息
3. **信道干扰分析** - 分析2.4GHz和5GHz频段的信道使用情况
4. **优化建议** - 基于分析结果提供信道调整建议
5. **实时监控** - 支持实时刷新和更新
6. **移动端适配** - 完整的响应式设计

## 技术架构

### 后端API

#### 1. 获取当前WiFi信号
```http
GET /api/wifi/signal
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "ssid": "NetworkTester-Pi5",
    "signal_strength": -45,
    "signal_quality": 85,
    "channel": 7,
    "frequency": 2442,
    "interface": "wlan0",
    "encryption": "WPA2",
    "connected": true,
    "timestamp": 1672531200
  }
}
```

#### 2. WiFi网络扫描和分析
```http
POST /api/wifi/scan
```

**响应结构:**
```json
{
  "success": true,
  "data": {
    "current_wifi": { /* 当前网络信息 */ },
    "networks": [ /* 周边网络列表 */ ],
    "channel_analysis": {
      "2.4ghz": {
        "1": {
          "level": 25,
          "count": 1,
          "avg_signal": 52,
          "networks": [...]
        }
        // ... 其他信道
      },
      "5ghz": { /* 5GHz频段分析 */ },
      "summary": {
        "total_24ghz_networks": 6,
        "total_5ghz_networks": 1,
        "most_crowded_24ghz": 6,
        "least_crowded_24ghz": 1
      }
    },
    "recommendations": {
      "need_adjustment": false,
      "current_channel": 7,
      "current_band": "2.4GHz",
      "recommended_channels": [
        {
          "channel": 1,
          "interference_level": 15.2,
          "network_count": 1,
          "improvement": 25.8
        }
      ],
      "reasons": ["信道分析结果说明"]
    },
    "scan_time": 1672531200,
    "total_networks": 5
  }
}
```

### 前端API

#### WiFi扫描接口
```http
POST /api/wifi-scan
```

调用后端扫描API并格式化返回数据。

## 前端组件架构

### 1. WiFiScanResults (主组件)

**文件:** `frontend/components/wifi/WiFiScanResults.tsx`

**功能:**
- 协调所有子组件
- 管理扫描状态和数据
- 实现标签页切换（网络概览、信道分析、优化建议）
- 处理错误状态和加载状态

**主要状态:**
```typescript
interface WiFiScanData {
  current_wifi: CurrentWiFi | null;
  networks: WiFiNetwork[];
  channel_analysis: ChannelAnalysis;
  recommendations: Recommendations;
  scan_time: number;
  total_networks: number;
}
```

### 2. CurrentWiFiCard (当前网络卡片)

**文件:** `frontend/components/wifi/CurrentWiFiCard.tsx`

**功能:**
- 展示当前连接的WiFi详细信息
- 信号强度可视化进度条
- 网络参数网格布局
- 信号质量分析和建议

**展示内容:**
- SSID和网络接口
- 信号强度和质量
- 频段、信道、频率
- 加密类型
- 连接状态和更新时间

### 3. ChannelInterferenceChart (信道干扰图表)

**文件:** `frontend/components/wifi/ChannelInterferenceChart.tsx`

**功能:**
- 柱状图展示信道使用情况
- 2.4GHz和5GHz频段分析
- 实时干扰程度可视化
- 信道详情卡片展示
- 响应式图表设计

**可视化特性:**
- 颜色编码：绿色(良好) → 橙色(轻微) → 黄色(中等) → 红色(严重)
- 当前信道高亮显示
- 悬停提示详细信息
- 移动端支持横向滚动

### 4. WiFiNetworkCard (网络卡片)

**文件:** `frontend/components/wifi/WiFiNetworkCard.tsx`

**功能:**
- 单个WiFi网络信息展示
- 信号强度图标化显示
- 加密类型彩色标识
- 频段标签区分

**设计特点:**
- 信号强度采用4级图标显示
- 加密类型彩色徽章
- BSSID等技术信息
- 信号质量提示

## 页面结构

### WiFi扫描页面

**路径:** `/wifi-scan`
**文件:** `frontend/app/wifi-scan/page.tsx`

**布局:**
```
┌─────────────────────────────────────┐
│ 🔍 WiFi扫描分析         [重新扫描]  │
├─────────────────────────────────────┤
│ [网络概览] [信道分析] [优化建议]    │
├─────────────────────────────────────┤
│                                     │
│ 内容区域 (根据选择的标签页显示)      │
│                                     │
└─────────────────────────────────────┘
```

## 响应式设计

### 断点策略
- **移动端 (默认)**: 宽度 < 640px
- **桌面端 (sm:)**: 宽度 ≥ 640px

### 适配要点

1. **布局调整**
   - 移动端：垂直堆叠布局
   - 桌面端：水平排列布局

2. **字体缩放**
   - 移动端：`text-xs`, `text-sm`
   - 桌面端：`sm:text-sm`, `sm:text-base`

3. **间距优化**
   - 移动端：紧凑间距 `p-2`, `gap-2`
   - 桌面端：舒适间距 `sm:p-4`, `sm:gap-4`

4. **图表适配**
   - 信道图表支持横向滚动
   - 柱状图在小屏幕上保持可读性
   - 悬停提示适配触摸操作

## 功能特性

### 信道干扰分析算法

```typescript
干扰程度 = (网络数量 × 平均信号强度权重) × 10
```

**分级标准:**
- 0-25%: 良好 (绿色)
- 25-50%: 轻微 (橙色)  
- 50-75%: 中等 (黄色)
- 75-100%: 严重 (红色)

### 优化建议逻辑

1. **触发条件**: 当前信道干扰程度 > 50%
2. **推荐标准**: 
   - 干扰程度比当前信道低10%以上
   - 按干扰程度排序，推荐前3个
3. **建议内容**:
   - 推荐信道号
   - 预期改善程度
   - 网络数量对比

### 实时更新机制

1. **自动扫描**: 页面加载时自动执行一次扫描
2. **手动刷新**: 提供重新扫描按钮
3. **错误处理**: 网络异常时显示友好提示
4. **加载状态**: 扫描过程中显示加载动画

## 测试指南

### 运行测试脚本

```bash
# 执行完整功能测试
./scripts/test-wifi-scan.sh
```

**测试内容:**
1. 服务端口检查
2. 后端API测试
3. 前端API测试
4. 页面访问测试
5. 性能测试
6. 移动端测试建议

### 手动测试步骤

1. **启动服务**
   ```bash
   # 后端服务
   cd backend && python start_dev.py
   
   # 前端服务
   cd frontend && yarn dev
   ```

2. **访问页面**
   - 桌面端: http://localhost:3000/wifi-scan
   - 移动端: http://[your-ip]:3000/wifi-scan

3. **功能验证**
   - ✅ 扫描按钮工作正常
   - ✅ 标签页切换正常
   - ✅ 信道图表显示正确
   - ✅ 移动端布局适配
   - ✅ 数据刷新正常

## 部署注意事项

### 树莓派5兼容性

1. **系统依赖**
   - 确保安装 `iwlist` 或 `iw` 命令
   - 检查无线网卡驱动

2. **权限要求**
   - WiFi扫描可能需要管理员权限
   - 建议测试实际扫描功能

3. **性能优化**
   - 扫描频率不宜过高
   - 考虑缓存机制

### 生产环境配置

1. **API端点配置**
   ```typescript
   // 根据环境调整API地址
   const API_BASE = process.env.NODE_ENV === 'production' 
     ? 'https://your-domain.com' 
     : 'http://localhost:8000';
   ```

2. **错误监控**
   - 添加错误日志记录
   - 监控扫描成功率

## 扩展功能建议

### 短期优化

1. **信号历史图表** - 展示信号强度变化趋势
2. **网络性能测试** - 集成速度测试功能
3. **自动信道切换** - 提供一键优化功能
4. **扫描调度** - 支持定时自动扫描

### 长期规划

1. **WiFi 6/6E支持** - 支持新标准分析
2. **网络拓扑图** - 可视化网络关系
3. **干扰源定位** - 识别非WiFi干扰源
4. **多设备协同** - 支持多点测量

## 故障排除

### 常见问题

1. **扫描无结果**
   - 检查无线网卡状态
   - 确认系统权限
   - 验证WiFi功能开启

2. **API调用失败**
   - 检查后端服务状态
   - 确认端口配置
   - 查看网络连接

3. **图表显示异常**
   - 清除浏览器缓存
   - 检查JavaScript控制台错误
   - 验证数据格式

4. **移动端布局问题**
   - 检查CSS样式加载
   - 验证响应式断点
   - 测试不同设备分辨率

### 调试工具

1. **后端调试**
   ```bash
   # 查看后端日志
   tail -f backend/logs/wifi_scan.log
   ```

2. **前端调试**
   - 浏览器开发者工具
   - Network面板查看API调用
   - Console查看错误信息

3. **API测试**
   ```bash
   # 直接测试后端API
   curl -X POST http://localhost:8000/api/wifi/scan
   ```

## 版本更新日志

### v1.0.0 (当前版本)
- ✅ 基础WiFi扫描功能
- ✅ 信道干扰分析
- ✅ 柱状图可视化
- ✅ 优化建议系统
- ✅ 响应式移动端适配
- ✅ 完整的组件化架构

---

*最后更新: 2024年1月*
*技术栈: Next.js + FastAPI + TypeScript + TailwindCSS* 