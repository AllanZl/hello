# SCD Parser and Logical Link Visualizer

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个基于Python的IEC 61850 SCD文件解析器和逻辑链路可视化工具。

## 功能特性

- **SCD文件解析**：解析IEC 61850标准的SCD文件，提取IED（智能电子设备）信息
- **逻辑链路分析**：自动分析GOOSE、SMV和Client-Server通信链路
- **网络拓扑可视化**：生成清晰的逻辑链路图表
- **多格式导出**：支持PNG、SVG、PDF格式导出
- **Web界面**：提供用户友好的文件上传和可视化界面
- **命令行工具**：支持批处理和自动化集成

## 技术栈

- **Python 3.8+**
- **lxml**：XML解析
- **NetworkX**：网络图分析
- **Graphviz**：专业图形渲染
- **Matplotlib**：科学可视化
- **Flask**：Web框架
- **Bootstrap**：前端UI

## 安装

### 系统依赖

首先安装Graphviz系统包：

```bash
# Ubuntu/Debian
sudo apt-get install graphviz graphviz-dev

# CentOS/RHEL
sudo yum install graphviz graphviz-devel

# macOS
brew install graphviz

# Windows
# 下载并安装 https://graphviz.org/download/
```

### Python包安装

```bash
# 克隆仓库
git clone https://github.com/AllanZl/hello.git
cd hello

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

## 使用方法

### 1. 命令行界面

#### 解析SCD文件
```bash
# 解析SCD文件
scd-parser parse examples/sample_substation.scd --output ./output

# 生成可视化图表
scd-parser visualize ./output --output diagram.png --format png

# 一步完成解析和可视化
scd-parser all examples/sample_substation.scd --output ./output --diagram network.svg --format svg
```

#### 命令选项
- `--format`: 输出格式 (png, svg, pdf, matplotlib)
- `--style`: 图表样式 (modern, classic, minimal)
- `--verbose`: 详细日志输出

### 2. Web界面

启动Web服务器：

```bash
python -m scd_parser.web_app
```

访问 `http://localhost:5000` 使用Web界面：

1. 上传SCD文件
2. 查看IED列表和通信链路
3. 生成网络可视化图表
4. 下载多种格式的图表

### 3. Python API

```python
from scd_parser import SCDParser, LogicalLinkVisualizer

# 解析SCD文件
parser = SCDParser()
parser.load_file('example.scd')

# 提取信息
ieds = parser.extract_ieds()
links = parser.extract_communication_links()
substation_info = parser.get_substation_info()

# 生成可视化
visualizer = LogicalLinkVisualizer()
visualizer.set_data(ieds, links)

# 导出图表
visualizer.export_to_png('network_diagram.png')
visualizer.export_to_svg('network_diagram.svg')

# 获取网络统计
stats = visualizer.get_network_statistics()
print(f"总IED数量: {stats['total_ieds']}")
print(f"总链路数量: {stats['total_links']}")
```

## 数据模型

### IED (智能电子设备)
```python
@dataclass
class IED:
    name: str              # IED名称
    type: str              # IED类型
    manufacturer: str      # 制造商
    config_version: str    # 配置版本
    desc: str             # 描述
    logical_devices: List[str]  # 逻辑设备列表
    access_points: List[str]    # 接入点列表
```

### LogicalLink (逻辑链路)
```python
@dataclass
class LogicalLink:
    source_ied: str        # 源IED
    target_ied: str        # 目标IED
    link_type: str         # 链路类型 (GOOSE, SMV, Client-Server)
    link_id: str           # 链路标识
    multicast_address: str # 组播地址
    vlan_id: str          # VLAN ID
    app_id: str           # 应用ID
    data_set: str         # 数据集
    control_block: str    # 控制块
```

## 示例输出

解析SCD文件后的输出包括：

### 1. IED列表
```json
{
  "name": "ProtIED1",
  "type": "Protection",
  "manufacturer": "TestVendor",
  "logical_devices_count": 1,
  "access_points_count": 1
}
```

### 2. 通信链路
```json
{
  "source_ied": "ProtIED1",
  "target_ied": "ALL_SUBSCRIBERS",
  "link_type": "GOOSE",
  "link_id": "GCB01",
  "vlan_id": "100",
  "app_id": "Events"
}
```

### 3. 网络统计
```json
{
  "total_ieds": 4,
  "total_links": 6,
  "network_density": 0.667,
  "average_degree": 2.0,
  "ied_types": {"Protection": 2, "Control": 1, "Measurement": 1},
  "link_types": {"GOOSE": 1, "SMV": 1, "Client-Server": 4}
}
```

## 可视化示例

生成的网络图表包含：

- **IED节点**：不同颜色表示不同类型的设备
- **通信链路**：不同颜色的箭头表示不同类型的通信
  - 蓝色：GOOSE链路
  - 红色：SMV链路  
  - 绿色：Client-Server链路
- **网络拓扑**：清晰显示设备间的连接关系

## 测试

运行测试套件：

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_scd_parser.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=scd_parser
```

## 目录结构

```
hello/
├── scd_parser/           # 主要源代码
│   ├── __init__.py
│   ├── models.py         # 数据模型
│   ├── parser.py         # SCD解析器
│   ├── visualizer.py     # 可视化模块
│   ├── cli.py           # 命令行接口
│   └── web_app.py       # Web应用
├── templates/           # HTML模板
├── examples/           # 示例SCD文件
├── tests/             # 测试用例
├── requirements.txt   # Python依赖
├── setup.py          # 安装配置
└── README.md         # 文档
```

## 扩展开发

### 添加新的链路类型

1. 在 `models.py` 中扩展 `LogicalLink` 数据模型
2. 在 `parser.py` 中添加对应的解析逻辑
3. 在 `visualizer.py` 中添加可视化样式

### 自定义可视化样式

```python
# 自定义IED颜色
def custom_ied_color(ied_type: str) -> str:
    custom_colors = {
        'MyCustomType': '#FF5733',
        # 添加更多自定义类型
    }
    return custom_colors.get(ied_type, '#B0C4DE')

# 应用自定义样式
visualizer._get_ied_color = custom_ied_color
```

## 故障排除

### 常见问题

1. **Graphviz未安装**
   ```
   Error: Graphviz executables not found
   ```
   解决：安装系统级Graphviz包

2. **XML解析错误**
   ```
   Error: Start tag expected
   ```
   解决：检查SCD文件格式是否正确

3. **内存不足**
   ```
   MemoryError: Unable to allocate array
   ```
   解决：处理大型SCD文件时增加内存限制

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/AllanZl/hello.git
cd hello

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -e .[dev]

# 运行测试
python -m pytest
```

## 支持

如有问题或建议，请：

1. 查看[文档](README.md)
2. 搜索[现有Issues](https://github.com/AllanZl/hello/issues)
3. 创建[新Issue](https://github.com/AllanZl/hello/issues/new)

---

© 2024 SCD Parser Team. 使用开源技术构建，促进电力系统数字化发展。