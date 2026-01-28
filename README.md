# 代码回灌测试系统

一个专业的C代码回归测试工具，支持两个版本代码的编译、执行、差异分析和报告生成。

## ✨ 主要特性

### 🎯 **核心功能**
- **C代码编译**: 支持GCC编译器，自动错误检测
- **并行执行**: 同时执行两个版本进行对比
- **智能差异分析**: 字符级差异百分比计算
- **实时监控**: 进度条和状态实时更新

### 📊 **增强GUI界面**
- **对比表格**: 4列详细分析（输入、输出A、输出B、差异%）
- **颜色编码**: 绿色(相同)、黄色(轻微)、红色(严重差异)
- **分割布局**: 左侧状态 + 右侧详细对比
- **悬停提示**: 表格单元格悬停查看完整内容

### 🛠️ **多种使用方式**
- **GUI模式**: `python main.py` (推荐)
- **CLI模式**: `python simple_cli.py` (高级用户)
- **启动器**: `python launcher.py` (交互式选择)

## 🚀 快速开始

### 1. 环境要求
- **Python**: 3.8+
- **编译器**: GCC (Linux/macOS) 或 MinGW (Windows)
- **GUI**: PyQt5 (GUI模式需要)
- **系统**: Windows / Linux / macOS

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动应用
```bash
# GUI模式 (推荐)
python main.py

# CLI模式
python simple_cli.py --help

# 交互式启动器
python launcher.py
```

## 📱 GUI使用指南

### 🎯 **界面布局**
```
┌─────────────────────────────────────────────────────────────┐
│ 配置区域                                                 │
│ 版本A: [浏览按钮]  版本B: [浏览按钮]                     │
│ 测试数据: [浏览按钮]                                   │
├─────────────────────────────────────────────────────────────┤
│ 控制区域                                                 │
│ [开始测试] [停止] 进度条: ████████░░░░░ 80%           │
├─────────────────────────────────────────────────────────────┤
│ 对比结果区域 (分割器)                                   │
│ ┌─────────────┬─────────────────────────────────────────┐ │
│ │ 测试状态    │ 详细对比表格                           │ │
│ │ ✓ test1    │ 输入数据  │ A输出    │ B输出    │ 差异% │ │
│ │ ✗ test2    │ 1 2 3 4  │ 1 2 3 4  │ 4 3 2 1 │ 100% │ │
│ │ ✓ test3    │ 5 6 7 8  │ 5 6 7 8  │ 5 6 7 8  │ 0%   │ │
│ └─────────────┴─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 📊 **对比表格说明**

| 列 | 说明 | 特性 |
|-----|------|------|
| 输入数据 | 测试用例输入 | 截断显示，悬停查看完整内容 |
| 版本A输出 | 代码A执行结果 | 完整输出显示 |
| 版本B输出 | 代码B执行结果 | 完整输出显示 |
| 差异百分比 | 量化差异程度 | 颜色编码：<br>🟢0% 🟡<20% 🔴≥20% |

### 🎨 **使用步骤**
1. **选择文件**: 点击浏览按钮选择两个版本的C文件
2. **选择数据**: 选择包含测试用例的目录
3. **开始测试**: 点击"开始测试"按钮
4. **查看结果**: 左侧看状态，右侧看详细对比
5. **分析差异**: 通过颜色和百分比快速识别问题

## 💻 CLI使用指南

### 基本用法
```bash
# 基本测试
python simple_cli.py -a version1.c -b version2.c -d ./test_data

# 指定输出目录
python simple_cli.py -a old.c -b new.c -d ./data -o ./results

# 详细日志
python simple_cli.py -a file1.c -b file2.c -d ./data --log-level DEBUG
```

### 参数说明
```bash
-a, --version-a    版本A的C文件路径 (必需)
-b, --version-b    版本B的C文件路径 (必需)
-d, --test-data    测试数据目录 (必需)
-o, --output       输出目录 (默认: test_results)
--log-level        日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
```

## 📁 项目结构

```
CodeRegressionTester/
├── main.py                    # 🖥️ GUI主程序 (推荐)
├── simple_cli.py              # 💻 命令行工具
├── launcher.py                # 🚀 交互式启动器
├── requirements.txt           # 📦 依赖包列表
├── README.md                 # 📖 项目说明
├── QUICK_START.md           # ⚡ 快速启动指南
├── ENHANCED_GUI.md         # 🎯 GUI增强说明
├── core/                     # 🔧 核心功能模块
│   ├── compiler.py          # C代码编译器
│   ├── executor.py          # 代码执行器
│   ├── comparator.py        # 结果比较器
│   ├── data_manager.py      # 数据管理器
│   └── report_generator.py   # 报告生成器
├── utils/                    # 🛠️ 工具模块
│   ├── logger.py           # 日志系统
│   ├── config.py           # 配置管理
│   └── diff_utils.py       # 差异处理工具
├── templates/                # 📄 报告模板
│   ├── report_template.html
│   └── styles.css
├── examples/                 # 📝 示例文件
│   ├── math_version_a.c    # 基础数学计算
│   ├── math_version_b.c    # 增强数学计算
│   └── test_data/         # 测试数据集
└── tests/                    # 🧪 测试文件
    ├── test_simple.py      # 核心功能测试
    └── unit_tests/        # 单元测试
```

## 🎯 示例使用


### 数学计算对比
```bash
python simple_cli.py \
  -a examples/math_version_a.c \
  -b examples/math_version_b.c \
  -d examples/test_data/math_test_data
```

## 📊 差异分析

### 🔍 **差异计算方法**
```python
def calculate_difference(output_a, output_b):
    """字符级差异百分比计算"""
    max_len = max(len(output_a), len(output_b))
    if max_len == 0:
        return 0.0
    
    # 计算不同字符数量
    diff_chars = sum(1 for i in range(min_len) 
                    if output_a[i] != output_b[i])
    diff_chars += abs(len(output_a) - len(output_b))
    
    # 计算百分比
    return (diff_chars / max_len) * 100
```

### 🎨 **差异解释**
- **0%**: 完全相同的输出
- **1-19%**: 轻微差异（可能是格式问题）
- **20-50%**: 中等差异（可能有逻辑差异）
- **>50%**: 重大差异（算法实现不同）

## 🐛 故障排除

### 常见问题

#### 1. PyQt5导入错误
```bash
# 解决方案
pip install PyQt5

# 或使用conda
conda install pyqt
```

#### 2. GCC编译器未找到
```bash
# Windows - 安装MinGW
choco install mingw

# Ubuntu/Debian
sudo apt-get install gcc

# macOS
xcode-select --install
```

#### 3. 测试数据格式错误
- 支持格式: `.input`, `.txt`, `.dat`, `.csv`
- 编码: UTF-8
- 内容: 纯文本，适合作为程序输入

#### 4. GUI启动失败
```bash
# 尝试CLI模式
python simple_cli.py --help

# 检查PyQt5安装
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### 调试模式
```bash
# 启用详细日志
python main.py --log-level DEBUG

# 查看详细错误
python simple_cli.py -a file.c -b file2.c -d data --log-level DEBUG
```

## 🔧 高级配置

### 编译选项
```python
# 在代码中修改编译标志
compiler = CCompiler(default_flags=["-O2", "-Wall", "-g"])
```

### 测试超时
```python
# 修改执行超时时间 (秒)
executor = CodeExecutor(timeout=60)
```

### 报告定制
```python
# 自定义HTML模板
generator = ReportGenerator(template_dir="custom_templates")
```


## 👥 作者信息

- **开发者**: 齐熠康
- **版本**: 1.0
- **Python**: 3.8+
- **Qt**: PyQt5

---

## 🎉 总结

**代码回灌测试系统**是一个专业的C代码回归测试工具，提供：

✅ **易用的GUI界面**  
✅ **强大的CLI工具**  
✅ **详细的差异分析**  
✅ **丰富的示例文件**  
✅ **完善的文档支持**  
