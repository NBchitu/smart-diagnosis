# 网络抓包与AI分析自动化开发计划

## 1. 项目目标

实现一套在树莓派5系统上运行的自动化网络抓包与AI分析系统，支持根据用户反馈的不同网络问题，自动选择最优抓包方案，精准采集数据并通过大模型（如GPT）进行智能诊断。

---

## 2. 主要功能模块

1. **前端交互**
   - 用户反馈网络问题（如“网速慢”、“DNS慢”、“频繁掉线”等）
   - 展示AI分析结果与建议
2. **后端API服务**
   - 接收前端请求，调度抓包、预处理、AI分析
3. **抓包控制模块**
   - 根据问题类型选择/生成抓包参数
   - 调用tcpdump/scapy等工具进行精准抓包
4. **数据包预处理模块**
   - 解析pcap文件，提取关键信息，生成结构化摘要
   - 针对不同问题类型采用不同预处理模板
5. **AI分析模块**
   - 生成prompt，调用大模型API，返回诊断结论
6. **结果存储与可视化（可选）**
   - 保存抓包摘要、AI分析报告，支持后续查询与展示

---

## 3. 不同网络问题的预设抓包方案

| 问题类型         | 抓包过滤表达式         | 重点关注字段           | 预处理摘要策略           |
|------------------|-----------------------|------------------------|--------------------------|
| 网速慢           | tcp/udp, 端口80/443   | TCP重传、RTT、窗口     | 统计重传、延迟、吞吐量   |
| DNS解析慢        | port 53               | DNS请求/响应时间       | 统计DNS耗时、失败率      |
| 频繁掉线         | tcp                   | TCP FIN/RST、丢包      | 统计断开、重连、丢包     |
| 局域网互通异常   | arp, icmp             | ARP请求/响应、ICMP     | 统计丢包、无响应         |
| 视频卡顿         | udp, 端口1935/554等   | UDP丢包、乱序、抖动    | 统计丢包、延迟、乱序     |

- 每种场景预设抓包时长、包数、过滤表达式，支持自定义

---

## 4. 详细开发流程

### 4.1 前端
- 问题类型选择/输入界面
- 触发抓包分析请求，轮询/等待结果
- 展示AI分析结论、建议、抓包摘要

### 4.2 后端API
- `/api/capture-and-analyze`：接收问题类型、参数，返回AI分析结果
- 参数：问题类型、抓包时长、目标IP/端口（可选）
- 返回：AI诊断结论、建议、抓包摘要

### 4.3 抓包控制
- 根据问题类型查找预设方案，生成tcpdump/scapy命令
- 限定抓包时长/包数，避免数据过大
- 支持多网卡选择

### 4.4 数据包预处理
- 用pyshark/scapy解析pcap
- 只保留关键信息，按问题类型定制摘要
- 统计异常事件、延迟、丢包等
- 生成结构化摘要（json/文本）

### 4.5 AI分析
- 生成prompt（用户问题+抓包摘要）
- 调用大模型API，获取诊断结论
- 支持多模型/多轮分析（可选）

### 4.6 结果返回与展示
- 返回AI结论、建议、摘要到前端
- 支持历史记录、导出（可选）

---

## 5. 关键细节与注意事项

- **token节省**：摘要尽量精简，优先异常、统计信息
- **安全性**：抓包需root权限，注意接口安全
- **可扩展性**：支持后续增加新场景、新模型
- **兼容性**：代码需兼容树莓派5与主流Linux

---

## 6. 任务分解与开发顺序

1. 预设抓包方案与参数模板整理
2. 抓包控制模块开发与测试
3. 数据包预处理与摘要生成
4. AI分析prompt生成与API对接
5. 后端API接口开发
6. 前端交互与结果展示
7. 测试与优化

---

## 7. 后续可扩展方向
- 智能抓包策略推荐
- 多模型融合分析
- 自动化问题定位与修复建议
- 可视化流量分析

---

> **后续开发请严格按照本计划逐步推进，每步完成后及时记录与总结。** 