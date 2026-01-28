#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码回灌测试系统 - 原始初版
回退到最开始能用的版本
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
        QGroupBox, QFileDialog, QMessageBox, QSplitter, QTableWidget,
        QTableWidgetItem, QHeaderView
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
    
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

class TestThread(QThread):
    """测试线程 - 增强版本"""
    progress = pyqtSignal(int, str)
    result = pyqtSignal(str, bool, str)
    comparison_data = pyqtSignal(list)  # 发送详细的对比数据
    
    def __init__(self, file_a, file_b, data_dir):
        super().__init__()
        self.file_a = file_a
        self.file_b = file_b
        self.data_dir = data_dir
    
    def run(self):
        """运行测试"""
        try:
            # 编译A
            self.progress.emit(10, "编译版本A...")
            exe_a = os.path.join(tempfile.gettempdir(), "test_a.exe")
            if os.system(f'gcc "{self.file_a}" -o "{exe_a}"') != 0:
                self.result.emit("编译A", False, "编译失败")
                return
            
            # 编译B
            self.progress.emit(20, "编译版本B...")
            exe_b = os.path.join(tempfile.gettempdir(), "test_b.exe")
            if os.system(f'gcc "{self.file_b}" -o "{exe_b}"') != 0:
                self.result.emit("编译B", False, "编译失败")
                return
            
            # 查找测试文件
            test_files = []
            for ext in ['*.txt', '*.input', '*.dat']:
                test_files.extend(Path(self.data_dir).glob(ext))
            
            total = len(test_files)
            passed = 0
            comparison_data = []
            
            for i, test_file in enumerate(test_files):
                progress = 30 + int(i * 70 / total)
                self.progress.emit(progress, f"测试 {test_file.name}")
                
                # 读取数据
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                
                # 运行A
                result = subprocess.run([exe_a], input=data, capture_output=True, text=True)
                if result.returncode != 0:
                    self.result.emit(test_file.name, False, "A执行失败")
                    continue
                out_a = result.stdout.strip()
                
                # 运行B
                result = subprocess.run([exe_b], input=data, capture_output=True, text=True)
                if result.returncode != 0:
                    self.result.emit(test_file.name, False, "B执行失败")
                    continue
                out_b = result.stdout.strip()
                
                # 计算差异百分比
                if out_a == out_b:
                    diff_percent = 0.0
                    passed += 1
                    self.result.emit(test_file.name, True, "通过")
                else:
                    # 简单的字符级差异计算
                    max_len = max(len(out_a), len(out_b))
                    if max_len == 0:
                        diff_percent = 0.0
                    else:
                        diff_chars = sum(1 for i in range(min(len(out_a), len(out_b))) 
                                       if out_a[i] != out_b[i])
                        diff_chars += abs(len(out_a) - len(out_b))
                        diff_percent = (diff_chars / max_len) * 100
                    
                    self.result.emit(test_file.name, False, "结果不同")
                
                # 收集对比数据
                comparison_data.append({
                    'filename': test_file.name,
                    'input_data': data[:100] + '...' if len(data) > 100 else data,  # 截断显示
                    'output_a': out_a,
                    'output_b': out_b,
                    'diff_percent': diff_percent
                })
            
            # 发送详细对比数据
            self.comparison_data.emit(comparison_data)
            
            self.progress.emit(100, f"完成: {passed}/{total}")
            
        except Exception as e:
            self.result.emit("系统", False, f"错误: {e}")

class OriginalMainWindow(QMainWindow):
    """原始主窗口 - 初版版本"""
    
    def __init__(self):
        super().__init__()
        self.thread = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面 - 原始风格"""
        self.setWindowTitle("代码回灌测试系统")
        self.setGeometry(100, 100, 900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 配置区域
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout()
        
        # 文件选择
        a_layout = QHBoxLayout()
        a_layout.addWidget(QLabel("版本A:"))
        self.file_a_edit = QLineEdit()
        a_layout.addWidget(self.file_a_edit)
        btn_a = QPushButton("浏览")
        btn_a.clicked.connect(lambda: self.browse_file(self.file_a_edit))
        a_layout.addWidget(btn_a)
        config_layout.addLayout(a_layout)
        
        b_layout = QHBoxLayout()
        b_layout.addWidget(QLabel("版本B:"))
        self.file_b_edit = QLineEdit()
        b_layout.addWidget(self.file_b_edit)
        btn_b = QPushButton("浏览")
        btn_b.clicked.connect(lambda: self.browse_file(self.file_b_edit))
        b_layout.addWidget(btn_b)
        config_layout.addLayout(b_layout)
        
        d_layout = QHBoxLayout()
        d_layout.addWidget(QLabel("测试数据:"))
        self.data_edit = QLineEdit()
        d_layout.addWidget(self.data_edit)
        btn_d = QPushButton("浏览")
        btn_d.clicked.connect(lambda: self.browse_dir(self.data_edit))
        d_layout.addWidget(btn_d)
        config_layout.addLayout(d_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 控制区域
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始测试")
        self.start_btn.clicked.connect(self.start_test)
        
        self.progress = QProgressBar()
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.progress)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 结果区域 - 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：简单结果文本
        left_group = QGroupBox("测试状态")
        left_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Consolas", 9))
        self.result_text.setMaximumWidth(350)
        left_layout.addWidget(self.result_text)
        
        left_group.setLayout(left_layout)
        splitter.addWidget(left_group)
        
        # 右侧：详细对比表格
        right_group = QGroupBox("详细对比分析")
        right_layout = QVBoxLayout()
        
        # 表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['输入数据', '版本A输出', '版本B输出', '差异百分比'])
        
        # 设置表格属性
        header = self.result_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # 设置行高
        self.result_table.verticalHeader().setDefaultSectionSize(60)
        self.result_table.setFont(QFont("Consolas", 8))
        self.result_table.setAlternatingRowColors(True)
        
        right_layout.addWidget(self.result_table)
        right_group.setLayout(right_layout)
        splitter.addWidget(right_group)
        
        # 设置分割比例
        splitter.setSizes([350, 650])
        layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def browse_file(self, edit):
        """浏览文件"""
        file, _ = QFileDialog.getOpenFileName(self, "选择C文件", "", "C文件 (*.c)")
        if file:
            edit.setText(file)
    
    def browse_dir(self, edit):
        """浏览目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择测试数据目录")
        if dir_path:
            edit.setText(dir_path)
    
    def start_test(self):
        """开始测试"""
        if not all([self.file_a_edit.text(), self.file_b_edit.text(), self.data_edit.text()]):
            QMessageBox.warning(self, "警告", "请填写所有配置")
            return
        
        # 清空之前的结果
        self.result_text.clear()
        self.result_table.setRowCount(0)
        self.start_btn.setEnabled(False)
        
        # 启动测试线程
        self.thread = TestThread(
            self.file_a_edit.text(),
            self.file_b_edit.text(),
            self.data_edit.text()
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.result.connect(self.show_result)
        self.thread.comparison_data.connect(self.update_table)
        self.thread.finished.connect(lambda: self.start_btn.setEnabled(True))
        self.thread.start()
    
    def update_progress(self, value, message):
        """更新进度"""
        self.progress.setValue(value)
        self.statusBar().showMessage(message)
    
    def show_result(self, name, success, message):
        """显示结果"""
        status = "✓" if success else "✗"
        self.result_text.append(f"{status} {name}: {message}")
    
    def update_table(self, comparison_data):
        """更新对比表格"""
        self.result_table.setRowCount(len(comparison_data))
        
        for row, data in enumerate(comparison_data):
            # 输入数据
            item1 = QTableWidgetItem(data['input_data'])
            item1.setToolTip(data['input_data'])  # 完整数据作为提示
            self.result_table.setItem(row, 0, item1)
            
            # 版本A输出
            item2 = QTableWidgetItem(data['output_a'])
            item2.setToolTip(data['output_a'])
            self.result_table.setItem(row, 1, item2)
            
            # 版本B输出
            item3 = QTableWidgetItem(data['output_b'])
            item3.setToolTip(data['output_b'])
            self.result_table.setItem(row, 2, item3)
            
            # 差异百分比
            diff_percent = data['diff_percent']
            item4 = QTableWidgetItem(f"{diff_percent:.1f}%")
            
            # 根据差异程度设置颜色
            if diff_percent == 0:
                item4.setBackground(Qt.green)
            elif diff_percent < 20:
                item4.setBackground(Qt.yellow)
            else:
                item4.setBackground(Qt.red)
            
            self.result_table.setItem(row, 3, item4)

def main():
    """主入口 - 原始版本"""
    if not GUI_AVAILABLE:
        print("GUI不可用，请安装PyQt5: pip install PyQt5")
        return 1
    
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    
    window = OriginalMainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())