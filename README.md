# 代码回灌测试系统

一个用于对比两个版本C代码功能差异性的GUI测试工具，支持编译、执行、结果比对和报告生成。

## 功能特性

- **C代码编译**: 支持GCC编译器，可配置编译选项
- **并行执行**: 同时执行两个版本的代码进行对比
- **结果比对**: 支持文本和数值数据的差异分析
- **误差计算**: 提供MAE、MSE、RMSE等多种误差指标
- **报告生成**: 生成HTML/PDF格式的详细测试报告
- **GUI界面**: 基于PyQt5的现代化用户界面
- **实时监控**: 显示测试进度和执行状态

## 系统要求

- Python 3.8+
- GCC编译器 (Linux/macOS) 或 MinGW (Windows)
- 操作系统: Windows / Linux / macOS

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd CodeRegressionTester
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. Windows用户额外安装
如果使用Windows，请确保已安装MinGW或Cygwin以获得GCC编译器。

## 使用方法

### GUI模式启动
```bash
python main.py
```

### 命令行参数
```bash
python main.py --help                    # 查看帮助
python main.py --version                 # 显示版本
python main.py --log-level DEBUG         # 设置日志级别
python main.py --config config.json      # 指定配置文件
```

### 基本使用流程

1. **配置测试参数**
   - 选择版本A和版本B的C源文件
   - 选择测试数据目录
   - 设置编译和对比选项

2. **执行测试**
   - 点击"开始测试"按钮
   - 系统会自动编译代码并执行测试
   - 实时显示测试进度和结果

3. **查看结果**
   - 在结果表格中查看各测试用例状态
   - 点击"查看"按钮查看详细差异信息
   - 查看执行时间和误差指标

4. **生成报告**
   - 点击"生成报告"按钮
   - 选择保存位置和格式 (HTML/PDF)
   - 报告包含完整的测试结果和图表分析

## 项目结构

```
CodeRegressionTester/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 使用说明
├── gui/                    # GUI模块
│   ├── __init__.py
│   └── main_window.py      # 主界面
├── core/                   # 核心功能模块
│   ├── __init__.py
│   ├── compiler.py         # C代码编译器
│   ├── executor.py         # 代码执行器
│   ├── comparator.py       # 结果对比分析
│   ├── data_manager.py     # 数据文件管理
│   └── report_generator.py # 报告生成器
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── logger.py           # 日志系统
│   └── file_utils.py       # 文件操作工具
└── templates/              # 报告模板
    ├── report_template.html
    └── styles.css
```

## 配置文件

系统支持JSON格式的配置文件，可以保存和加载测试配置：

```json
{
  "version_a_source": "path/to/version_a.c",
  "version_b_source": "path/to/version_b.c",
  "test_data_dir": "path/to/test_data",
  "compile_flags": ["-O2", "-Wall"],
  "tolerance": 1e-6,
  "ignore_whitespace": true
}
```

## 测试数据格式

测试数据文件支持多种格式：
- `.input` - 标准输入格式
- `.txt` - 纯文本格式
- `.dat` - 数据文件格式
- `.csv` - 逗号分隔值格式

## 报告内容

生成的测试报告包含：
- 测试概览和统计信息
- 状态分布图表
- 误差分析图表
- 执行时间趋势
- 详细的测试结果表格
- 差异详情和上下文
- 误差指标汇总

## 开发说明

### 运行测试
```bash
python -m pytest tests/
```

### 代码规范
- 遵循PEP8编码规范
- 使用类型提示增强代码可读性
- 编写详细的文档字符串

### 扩展开发
系统采用模块化设计，支持以下扩展：
- 自定义比较器插件
- 新的报告格式
- 额外的编译器支持

## 常见问题

### Q: 编译失败怎么办？
A: 检查GCC是否正确安装，确认源文件路径正确，查看详细错误信息。

### Q: 测试数据如何准备？
A: 准备与程序输入格式匹配的数据文件，放在同一目录下。

### Q: 如何提高测试效率？
A: 使用并行执行，优化编译选项，减少不必要的测试数据。

---

**开发者**: 齐熠康  
**版本**: 1.0  
**更新时间**: 2026-01-27