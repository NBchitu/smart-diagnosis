# 网络抓包数据本地磁盘保存功能

## 功能概述

在网络设备面板的抓包监控系统中，新增了本地磁盘保存功能，允许用户将抓包结果保存到本地文件系统，便于后续分析和存档。

## 核心功能

### 1. 自动保存机制
- **默认启用**：抓包会话结束时自动保存数据
- **多格式支持**：同时生成JSON、摘要和原始格式文件
- **智能命名**：文件名包含时间戳、会话ID和目标信息

### 2. 保存格式

#### JSON格式 (`*_detailed.json`)
```json
{
  "session_info": {
    "session_id": "capture_1704623456789",
    "start_time": "2025-01-07T10:30:45.123456",
    "end_time": "2025-01-07T10:31:15.678901",
    "target": "baidu.com",
    "filter_expr": "host baidu.com",
    "duration": 30,
    "packets_captured": 25
  },
  "packets": [
    {
      "timestamp": "10:30:45.123",
      "protocol": "TCP",
      "src_ip": "192.168.1.100",
      "dst_ip": "110.242.68.3",
      "src_port": 12345,
      "dst_port": 80,
      "packet_type": "HTTP_REQUEST",
      "summary": "GET / HTTP/1.1",
      "flags": ["SYN", "ACK"],
      "size": 64
    }
  ],
  "analysis": {
    "protocol_stats": {"TCP": 20, "ICMP": 5},
    "destination_servers": ["110.242.68.3"],
    "network_issues": [],
    "connection_stats": {}
  }
}
```

#### 摘要格式 (`*_summary.txt`)
```
抓包会话摘要报告
==================================================

会话ID: capture_1704623456789
目标: baidu.com
开始时间: 2025-01-07 10:30:45.123456
结束时间: 2025-01-07 10:31:15.678901
实际时长: 30.56秒
过滤条件: host baidu.com
抓取数据包数: 25

分析结果:
------------------------------
协议分布: {'TCP': 20, 'ICMP': 5}
目标服务器: ['110.242.68.3']
网络问题: []
连接统计: {}

数据包详情:
------------------------------
  1. 10:30:45.123 | TCP | 192.168.1.100:12345 -> 110.242.68.3:80 | GET / HTTP/1.1
  2. 10:30:45.234 | TCP | 110.242.68.3:80 -> 192.168.1.100:12345 | HTTP/1.1 200 OK
  ...
```

#### 原始格式 (`*_raw.txt`)
```
# 原始抓包数据
# Session: capture_1704623456789
# Target: baidu.com
# Filter: host baidu.com
# Start: 2025-01-07 10:30:45.123456
# End: 2025-01-07 10:31:15.678901

10:30:45.123 | TCP | 192.168.1.100:12345 > 110.242.68.3:80 | Size: 64 | Flags: SYN,ACK | GET / HTTP/1.1
10:30:45.234 | TCP | 110.242.68.3:80 > 192.168.1.100:12345 | Size: 512 | Flags: ACK | HTTP/1.1 200 OK
...
```

### 3. 文件命名规则

```
格式: {时间戳}_{会话ID}_{目标}_{格式}.{扩展名}
示例: 20250107_103045_capture_1704623456789_baidu.com_detailed.json
```

## 技术实现

### 1. 核心类扩展

#### CaptureSession类新增字段
```python
@dataclass
class CaptureSession:
    # ... 原有字段 ...
    duration: int = 30  # 预设时长
    saved_files: List[str] = None  # 保存的文件路径列表
    
    def __post_init__(self):
        if self.saved_files is None:
            self.saved_files = []
```

#### PacketCaptureServer类新增配置
```python
def __init__(self):
    # ... 原有初始化 ...
    
    # 配置保存目录
    self.save_directory = Path("data/packet_captures").resolve()
    self.save_directory.mkdir(parents=True, exist_ok=True)
    
    # 保存配置
    self.save_formats = ["json", "summary", "raw"]  # 支持的保存格式
    self.auto_save = True  # 是否自动保存
```

### 2. 保存方法实现

#### 核心保存方法
```python
def _save_capture_data(self, session: CaptureSession) -> List[str]:
    """保存抓包数据到本地磁盘"""
    saved_files = []
    
    # 生成文件名前缀
    timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
    safe_target = re.sub(r'[^\w\-_.]', '_', session.target)
    file_prefix = f"{timestamp}_{session.session_id}_{safe_target}"
    
    # 1. 保存JSON格式的详细数据
    # 2. 保存可读性摘要
    # 3. 保存原始数据包信息
    
    return saved_files
```

#### 自动保存触发
```python
# 在 stop_capture 方法中
if self.auto_save and session.packets:
    saved_files = self._save_capture_data(session)
    logger.info(f"会话 {session_id} 自动保存完成，文件数: {len(saved_files)}")

# 在 get_session_status 会话自动结束时
if self.auto_save and session.packets:
    saved_files = self._save_capture_data(session)
    logger.info(f"会话 {session_id} 自动结束并保存完成，文件数: {len(saved_files)}")
```

### 3. MCP工具扩展

#### 新增工具

1. **save_capture_data** - 手动保存抓包数据
```python
{
    "name": "save_capture_data",
    "description": "手动保存抓包数据到本地磁盘",
    "inputSchema": {
        "properties": {
            "session_id": {"type": "string", "description": "抓包会话ID"},
            "formats": {
                "type": "array",
                "items": {"type": "string", "enum": ["json", "summary", "raw"]},
                "description": "保存格式",
                "default": ["json", "summary", "raw"]
            }
        },
        "required": ["session_id"]
    }
}
```

2. **configure_auto_save** - 配置自动保存设置
```python
{
    "name": "configure_auto_save",
    "description": "配置自动保存设置",
    "inputSchema": {
        "properties": {
            "auto_save": {"type": "boolean", "description": "是否启用自动保存"},
            "save_formats": {
                "type": "array",
                "items": {"type": "string", "enum": ["json", "summary", "raw"]},
                "description": "默认保存格式"
            },
            "save_directory": {"type": "string", "description": "保存目录路径"}
        }
    }
}
```

#### 状态响应扩展
```python
# get_session_status 响应中新增
{
    "success": True,
    "session_id": session_id,
    "status": "completed",
    # ... 其他字段 ...
    "saved_files": session.saved_files  # 新增：保存的文件列表
}
```

## 存储配置

### 默认设置
- **保存目录**: `backend/data/packet_captures/`
- **自动保存**: 启用
- **保存格式**: JSON + 摘要 + 原始格式
- **文件权限**: 用户可读写 (644)

### 目录结构
```
backend/
└── data/
    └── packet_captures/
        ├── 20250107_103045_capture_123_baidu.com_detailed.json
        ├── 20250107_103045_capture_123_baidu.com_summary.txt
        ├── 20250107_103045_capture_123_baidu.com_raw.txt
        └── ...
```

## 使用方式

### 1. 自动保存（默认行为）
```python
# 启动抓包
await server.start_capture(target="baidu.com", duration=30)

# 等待抓包完成（30秒后自动结束并保存）
status = await server.get_session_status()
print(f"保存的文件: {status['saved_files']}")
```

### 2. 手动保存
```python
# 启动抓包
result = await server.start_capture(target="baidu.com", duration=30)
session_id = result["session_id"]

# 手动保存特定格式
save_result = await server.save_capture_data_manual(
    session_id=session_id,
    formats=["json", "summary"]
)
```

### 3. 配置保存设置
```python
# 禁用自动保存
await server.configure_auto_save_settings(auto_save=False)

# 只保存JSON格式
await server.configure_auto_save_settings(save_formats=["json"])

# 更改保存目录
await server.configure_auto_save_settings(save_directory="/custom/path")
```

## 测试验证

### 测试脚本
创建了 `backend/test_packet_save.py` 测试脚本，验证：
- 默认配置检查
- 配置修改功能
- 手动保存功能
- 自动保存逻辑
- 文件内容验证

### 测试结果
```
=== 抓包数据保存功能测试 ===

1. 检查默认保存设置: ✅
2. 测试配置修改: ✅
3. 创建测试抓包会话: ✅
4. 测试手动保存: ✅ (生成3个文件)
5. 验证保存的文件: ✅ (JSON 2532字符, 摘要 566字符, 原始 448字符)
6. 测试自动保存逻辑: ✅

=== 测试完成 ===
```

## 优势特性

### 1. 完整性
- **三种格式**：满足不同分析需求
- **完整元数据**：包含会话信息和分析结果
- **结构化数据**：便于程序化处理

### 2. 可用性
- **自动命名**：文件名包含关键信息，便于查找
- **可读格式**：摘要文件人类可读，适合快速查看
- **程序兼容**：JSON格式便于其他工具导入

### 3. 可配置性
- **格式选择**：可选择保存特定格式
- **目录自定义**：支持自定义保存位置
- **开关控制**：可禁用自动保存

### 4. 健壮性
- **权限处理**：自动创建目录和处理权限
- **错误恢复**：保存失败不影响抓包功能
- **路径安全**：文件名安全转义

## 后续优化方向

1. **压缩存储**：大文件自动压缩
2. **清理策略**：旧文件自动清理
3. **格式扩展**：支持PCAP格式导出
4. **云存储**：支持云端保存选项
5. **搜索功能**：基于元数据的文件搜索

这个功能极大地增强了网络诊断工具的实用性，为用户提供了完整的数据保存和分析解决方案。 