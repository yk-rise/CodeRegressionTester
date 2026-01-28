import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget,
                            QTableWidgetItem, QProgressBar, QGroupBox, QCheckBox,
                            QSpinBox, QDoubleSpinBox, QFileDialog, QMenuBar,
                            QMenu, QAction, QMessageBox, QSplitter, QHeaderView,
                            QStatusBar, QTabWidget, QComboBox, QGridLayout)
from utils.diff_utils import create_enhanced_diff_display, get_diff_summary_html
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.compiler import CCompiler
from core.executor import CodeExecutor
from core.comparator import ResultComparator
from core.data_manager import DataManager
from core.report_generator import ReportGenerator


class TestWorkerThread(QThread):
    """测试执行工作线程"""
    progress_updated = pyqtSignal(int, str)  # 进度, 状态信息
    test_completed = pyqtSignal(object)      # 测试结果
    all_tests_finished = pyqtSignal(list)   # 所有测试完成
    error_occurred = pyqtSignal(str)         # 错误信息
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.should_stop = False
    
    def run(self):
        """执行测试"""
        try:
            # 初始化组件
            compiler = CCompiler()
            executor = CodeExecutor()
            comparator = ResultComparator()
            
            # 编译代码
            self.progress_updated.emit(10, "正在编译版本A...")
            result_a = compiler.compile_code(
                self.config['version_a_source'],
                self.config['version_a_output']
            )
            
            if self.should_stop:
                return
            
            if not result_a.success:
                self.error_occurred.emit(f"版本A编译失败: {result_a.errors}")
                return
            
            self.progress_updated.emit(20, "正在编译版本B...")
            result_b = compiler.compile_code(
                self.config['version_b_source'],
                self.config['version_b_output']
            )
            
            if self.should_stop:
                return
            
            if not result_b.success:
                self.error_occurred.emit(f"版本B编译失败: {result_b.errors}")
                return
            
            # 获取测试文件
            data_manager = DataManager(self.config['test_data_dir'])
            test_files = data_manager.discover_all_test_files()
            
            if not test_files:
                self.error_occurred.emit("未找到测试数据文件")
                return
            
            # 执行测试
            results = []
            total_tests = len(test_files)
            
            for i, test_file in enumerate(test_files):
                if self.should_stop:
                    break
                
                progress = 30 + (i * 60 // total_tests)
                self.progress_updated.emit(progress, f"执行测试 {i+1}/{total_tests}: {os.path.basename(test_file)}")
                
                # 并行执行两个版本
                result1, result2 = executor.execute_parallel(
                    self.config['version_a_output'],
                    self.config['version_b_output'],
                    test_file
                )
                
                # 比较结果
                comparison_result = comparator.compare_files(
                    result1.output_file,
                    result2.output_file
                )
                
                # 添加执行结果信息
                comparison_result.version_a_result = result1
                comparison_result.version_b_result = result2
                
                results.append(comparison_result)
                self.test_completed.emit(comparison_result)
            
            if not self.should_stop:
                self.progress_updated.emit(100, "测试完成")
                self.all_tests_finished.emit(results)
                
        except Exception as e:
            self.error_occurred.emit(f"测试执行错误: {str(e)}")
    
    def stop(self):
        """停止测试"""
        self.should_stop = True


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.test_worker = None
        self.test_results = []
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("代码回灌测试系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建配置区域
        config_group = self.create_config_group()
        main_layout.addWidget(config_group)
        
        # 创建控制按钮区域
        control_group = self.create_control_group()
        main_layout.addWidget(control_group)
        
# 创建结果显示区域（优化版）
        result_splitter = QSplitter(Qt.Horizontal)
        result_splitter.setChildrenCollapsible(False)
        
        # 左侧：测试用例列表（更小）
        left_widget = QWidget()
        left_widget.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(2, 2, 2, 2)
        
        # 紧凑的标题
        title_label = QLabel("测试用例")
        title_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        left_layout.addWidget(title_label)
        
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(4)
        self.test_table.setHorizontalHeaderLabels(["用例", "状态", "相似度", "时间"])
        # self.test_table.horizontalHeader().setStretchLastSection(True)
        self.test_table.setSelectionBehavior(QTableWidget.SelectRows)
        # 设置更小的行高
        self.test_table.verticalHeader().setDefaultSectionSize(20)
        self.test_table.setFont(QFont("Arial", 8))
        left_layout.addWidget(self.test_table)
        
        result_splitter.addWidget(left_widget)
        
        # 右侧：详细信息区域（更大）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(2, 2, 2, 2)
        
        # 顶部：进度和状态（更紧凑）
        top_bar = QWidget()
        top_bar.setMaximumHeight(40)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 进度条（更小）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(15)
        top_layout.addWidget(self.progress_bar, 3)
        
        # 状态标签（更小）
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 9px;")
        self.status_label.setMaximumHeight(20)
        top_layout.addWidget(self.status_label, 1)
        
        right_layout.addWidget(top_bar)
        
        # 主要区域：增强的差异显示
        self.detail_tabs = QTabWidget()
        self.detail_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                padding: 2px 8px;
                margin-right: 2px;
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #e0e0e0;
            }
        """)
        
        # 执行信息标签页
        self.exec_info_text = QTextEdit()
        self.exec_info_text.setReadOnly(True)
        self.exec_info_text.setFont(QFont("Consolas", 9))
        self.detail_tabs.addTab(self.exec_info_text, "执行信息")
        
        # 增强的差异详情标签页
        diff_container = QWidget()  # 使用不同的变量名作为容器
        self.diff_layout = QVBoxLayout(diff_container)
        self.diff_layout.setContentsMargins(5, 5, 5, 5)
    
        # 差异控制栏
        diff_control = QWidget()
        diff_control.setMaximumHeight(30)
        diff_control_layout = QHBoxLayout(diff_control)
        diff_control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.diff_mode_combo = QComboBox()
        self.diff_mode_combo.addItems(["并排对比", "统一差异", "只显示差异"])
        self.diff_mode_combo.setMaximumWidth(100)
        diff_control_layout.addWidget(QLabel("显示模式:"))
        diff_control_layout.addWidget(self.diff_mode_combo)
        
        self.highlight_diff_check = QCheckBox("高亮差异")
        self.highlight_diff_check.setChecked(True)
        diff_control_layout.addWidget(self.highlight_diff_check)
        
        self.context_lines_spin = QSpinBox()
        self.context_lines_spin.setRange(0, 10)
        self.context_lines_spin.setValue(3)
        self.context_lines_spin.setSuffix(" 行上下文")
        diff_control_layout.addWidget(self.context_lines_spin)
        
        diff_control_layout.addStretch()
        self.diff_layout.addWidget(diff_control)
        
        # 增强的差异显示区域
        from gui.diff_display import DiffDisplayWidget
        self.diff_display = DiffDisplayWidget()  # 使用不同的变量名
        self.diff_layout.addWidget(self.diff_display)
        
        self.detail_tabs.addTab(diff_container, "差异详情")  # 使用容器添加到标签页
    
        # 日志输出标签页
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 8))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                color: #f8f8f2;
                font-family: 'Consolas', monospace;
                font-size: 8pt;
            }
        """)
        self.detail_tabs.addTab(self.log_text, "日志")
        
        right_layout.addWidget(self.detail_tabs)
        
        result_splitter.addWidget(right_widget)
        
        result_splitter.setSizes([300, 900])
        
        return result_splitter
    
    def create_config_group(self):
        """创建配置区域"""
        config_group = QGroupBox("测试配置")
        config_layout = QGridLayout(config_group)
        
        # 版本A
        config_layout.addWidget(QLabel("版本A:"), 0, 0)
        self.version_a_edit = QLineEdit()
        config_layout.addWidget(self.version_a_edit, 0, 1)
        self.browse_a_btn = QPushButton("浏览")
        self.browse_a_btn.setMaximumWidth(60)
        self.browse_a_btn.clicked.connect(lambda: self.browse_file(self.version_a_edit, "C文件 (*.c)"))
        config_layout.addWidget(self.browse_a_btn, 0, 2)
        
        # 版本B
        config_layout.addWidget(QLabel("版本B:"), 1, 0)
        self.version_b_edit = QLineEdit()
        config_layout.addWidget(self.version_b_edit, 1, 1)
        self.browse_b_btn = QPushButton("浏览")
        self.browse_b_btn.setMaximumWidth(60)
        self.browse_b_btn.clicked.connect(lambda: self.browse_file(self.version_b_edit, "C文件 (*.c)"))
        config_layout.addWidget(self.browse_b_btn, 1, 2)
        
        # 测试数据目录
        config_layout.addWidget(QLabel("测试数据:"), 2, 0)
        self.test_data_edit = QLineEdit()
        config_layout.addWidget(self.test_data_edit, 2, 1)
        self.browse_data_btn = QPushButton("浏览")
        self.browse_data_btn.setMaximumWidth(60)
        self.browse_data_btn.clicked.connect(lambda: self.browse_directory(self.test_data_edit))
        config_layout.addWidget(self.browse_data_btn, 2, 2)
        
        return config_group
    
    def create_control_group(self):
        """创建控制按钮区域"""
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout(control_group)
        
        # 按钮
        self.start_btn = QPushButton("开始测试")
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setMaximumWidth(60)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setMaximumWidth(60)
        self.stop_btn.setEnabled(False)
        
        self.report_btn = QPushButton("生成报告")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setMaximumWidth(60)
        self.report_btn.setEnabled(False)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.report_btn)
        control_layout.addWidget(self.progress_bar)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        
        return control_group
    
    def show_status(self, message):
        """显示状态信息"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def browse_file(self, line_edit, file_filter):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", file_filter)
        if file_path:
            line_edit.setText(file_path)
    
    def browse_directory(self, line_edit):
        """浏览目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            line_edit.setText(dir_path)
    
    def validate_config(self):
        """验证配置"""
        if not self.version_a_edit.text():
            self.show_status("请选择版本A的C文件")
            return False
        if not self.version_b_edit.text():
            self.show_status("请选择版本B的C文件")
            return False
        if not self.test_data_edit.text():
            self.show_status("请选择测试数据目录")
            return False
        return True
    
    def get_test_config(self):
        """获取测试配置"""
        import tempfile
        import os
        
        version_a = self.version_a_edit.text()
        version_b = self.version_b_edit.text()
        test_data_dir = self.test_data_edit.text()
        
        # 生成输出文件路径
        base_name = os.path.splitext(os.path.basename(version_a))[0]
        output_dir = tempfile.gettempdir()
        
        return {
            'version_a_source': version_a,
            'version_b_source': version_b,
            'version_a_output': os.path.join(output_dir, f"{base_name}_a.exe"),
            'version_b_output': os.path.join(output_dir, f"{base_name}_b.exe"),
            'test_data_dir': test_data_dir,
            'timeout': 30,
            'tolerance': 1e-6
        }
    
    def start_test(self):
        """开始测试"""
        # 验证配置
        if not self.validate_config():
            return
        
        # 获取配置
        config = self.get_test_config()
        
        # 禁用控制按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.report_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 模拟测试过程（简化版本）
        self.status_label.setText("测试进行中...")
        self.test_results = []
        
        # 这里应该启动实际的工作线程，现在用简化的方式
        import threading
        def run_test():
            # 模拟测试完成
            import time
            for i in range(10):
                if self.should_stop:
                    return
                time.sleep(0.5)
                self.progress_bar.setValue((i + 1) * 10)
                self.status_label.setText(f"测试进度: {i + 1}/10")
            
            self.status_label.setText("测试完成")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.report_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
        
        self.should_stop = False
        threading.Thread(target=run_test, daemon=True).start()
    
    def stop_test(self):
        """停止测试"""
        self.should_stop = True
        self.status_label.setText("正在停止测试...")
    
    def generate_report(self):
        """生成报告"""
        self.show_status("生成报告功能开发中...")
        self.status_label.setStyleSheet("font-weight: bold; color: #FF9800;")
    
    def stop_test(self):
        """停止测试"""
        if self.test_worker:
            self.test_worker.stop()
            self.test_worker.wait()
        
        self.on_test_stopped()
    
    def on_test_stopped(self):
        """测试停止后的处理"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("测试已停止")
        self.status_label.setStyleSheet("font-weight: bold; color: #F44336;")
    
    def on_progress_updated(self, progress, status):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        self.log_text.append(f"[{progress}%] {status}")
    
    def on_test_completed(self, result):
        """单个测试完成"""
        self.test_results.append(result)
        
        # 添加到表格
        row = self.test_table.rowCount()
        self.test_table.insertRow(row)
        
        self.test_table.setItem(row, 0, QTableWidgetItem(result.test_case))
        self.test_table.setItem(row, 1, QTableWidgetItem(result.overall_status))
        self.test_table.setItem(row, 2, QTableWidgetItem(f"{result.similarity_score:.3f}"))
        
        # 设置状态颜色
        status_item = self.test_table.item(row, 1)
        if result.overall_status == 'PASS':
            status_item.setBackground(QColor(200, 255, 200))
        elif result.overall_status == 'FAIL':
            status_item.setBackground(QColor(255, 200, 200))
        else:
            status_item.setBackground(QColor(255, 255, 200))
        
        # 执行时间
        if hasattr(result, 'version_a_result') and result.version_a_result:
            exec_time = result.version_a_result.execution_time
            self.test_table.setItem(row, 3, QTableWidgetItem(f"{exec_time:.3f}s"))
        
        # 自动选择最新行
        self.test_table.selectRow(row)
        self.show_test_detail(result)
    
    def on_all_tests_finished(self, results):
        """所有测试完成"""
        self.test_results = results
        
        # 统计结果
        total = len(results)
        passed = sum(1 for r in results if r.overall_status == 'PASS')
        failed = sum(1 for r in results if r.overall_status == 'FAIL')
        warning = sum(1 for r in results if r.overall_status == 'WARNING')
        
        summary = f"测试完成! 总计: {total}, 通过: {passed}, 失败: {failed}, 警告: {warning}"
        self.status_label.setText(summary)
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.report_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 显示汇总信息
        self.exec_info_text.append(f"\n{summary}")
        self.exec_info_text.append(f"通过率: {passed/total*100:.1f}%")
    
    def on_error_occurred(self, error_msg):
        """错误发生"""
        self.log_text.append(f"错误: {error_msg}")
        self.status_label.setText(f"错误: {error_msg}")
        self.status_label.setStyleSheet("font-weight: bold; color: #F44336;")
        
        QMessageBox.critical(self, "测试错误", error_msg)
        
        self.on_test_stopped()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 添加文件菜单项
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(lambda: self.open_file())
        file_menu.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(lambda: self.show_status("保存功能开发中..."))
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_test_detail(self, result):
        """显示测试详情"""
        # 执行信息
        exec_info = f"测试用例: {result.test_case}\n"
        exec_info += f"状态: {result.overall_status}\n"
        exec_info += f"相似度: {result.similarity_score:.3f}\n"
        
        if result.error_metrics:
            exec_info += f"\n误差指标:\n"
            exec_info += f"  MAE: {result.error_metrics.mae:.2e}\n"
            exec_info += f"  MSE: {result.error_metrics.mse:.2e}\n"
            exec_info += f"  RMSE: {result.error_metrics.rmse:.2e}\n"
            exec_info += f"  最大误差: {result.error_metrics.max_error:.2e}\n"
            exec_info += f"  相对误差: {result.error_metrics.relative_error:.2e}\n"
            exec_info += f"  相关系数: {result.error_metrics.correlation:.3f}\n"
        
        if hasattr(result, 'version_a_result') and result.version_a_result:
            exec_info += f"\n版本A执行时间: {result.version_a_result.execution_time:.3f}s\n"
            exec_info += f"版本A返回码: {result.version_a_result.return_code}\n"
        
        if hasattr(result, 'version_b_result') and result.version_b_result:
            exec_info += f"\n版本B执行时间: {result.version_b_result.execution_time:.3f}s\n"
            exec_info += f"版本B返回码: {result.version_b_result.return_code}\n"
        
        self.exec_info_text.setText(exec_info)
        
        # 使用增强的差异显示
        enhanced_diff = create_enhanced_diff_display(None, None, result)
        self.diff_text.setText(enhanced_diff)
        self.diff_text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                line-height: 1.4;
                white-space: pre-wrap;
            }
        """)
    
    def generate_report(self):
        """生成报告"""
        if not self.test_results:
            QMessageBox.warning(self, "警告", "没有测试结果可生成报告")
            return
        
        # 选择保存位置
        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存报告", "", "HTML文件 (*.html);;PDF文件 (*.pdf)"
        )
        
        if not output_file:
            return
        
        try:
            # 获取模板目录
            template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
            
            # 创建报告生成器
            report_generator = ReportGenerator(template_dir)
            
            # 生成HTML报告
            if output_file.endswith('.html'):
                success = report_generator.generate_html_report(
                    self.test_results, output_file, self.get_test_config()
                )
            else:
                # 先生成HTML，再转换为PDF
                html_file = output_file.rsplit('.', 1)[0] + '.html'
                success = report_generator.generate_html_report(
                    self.test_results, html_file, self.get_test_config()
                )
                if success:
                    success = report_generator.convert_to_pdf(html_file, output_file)
                    # 删除临时HTML文件
                    if os.path.exists(html_file):
                        os.remove(html_file)
            
            if success:
                QMessageBox.information(self, "成功", f"报告已生成: {output_file}")
                self.status_bar.showMessage(f"报告已生成: {os.path.basename(output_file)}", 5000)
            else:
                QMessageBox.critical(self, "错误", "报告生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"报告生成错误: {str(e)}")
    
    def clear_results(self):
        """清空结果"""
        self.test_results.clear()
        self.test_table.setRowCount(0)
        self.exec_info_text.clear()
        self.diff_text.clear()
        self.log_text.clear()
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.report_btn.setEnabled(False)
    
    def validate_config(self):
        """验证配置"""
        if not self.version_a_edit.text().strip():
            QMessageBox.warning(self, "配置错误", "请选择版本A的源文件")
            return False
        
        if not self.version_b_edit.text().strip():
            QMessageBox.warning(self, "配置错误", "请选择版本B的源文件")
            return False
        
        if not self.test_data_edit.text().strip():
            QMessageBox.warning(self, "配置错误", "请选择测试数据目录")
            return False
        
        if not os.path.exists(self.version_a_edit.text()):
            QMessageBox.warning(self, "配置错误", "版本A源文件不存在")
            return False
        
        if not os.path.exists(self.version_b_edit.text()):
            QMessageBox.warning(self, "配置错误", "版本B源文件不存在")
            return False
        
        if not os.path.exists(self.test_data_edit.text()):
            QMessageBox.warning(self, "配置错误", "测试数据目录不存在")
            return False
        
        return True
    
    def get_test_config(self):
        """获取测试配置"""
        # 构建编译标志
        compile_flags = []
        if self.opt2_check.isChecked():
            compile_flags.append("-O2")
        if self.debug_check.isChecked():
            compile_flags.append("-g")
        if self.wall_check.isChecked():
            compile_flags.append("-Wall")
        
        return {
            'version_a_source': self.version_a_edit.text(),
            'version_b_source': self.version_b_edit.text(),
            'version_a_output': os.path.join(os.path.dirname(self.version_a_edit.text()), 'version_a.exe'),
            'version_b_output': os.path.join(os.path.dirname(self.version_b_edit.text()), 'version_b.exe'),
            'test_data_dir': self.test_data_edit.text(),
            'compile_flags': compile_flags,
            'tolerance': self.tolerance_spin.value(),
            'ignore_whitespace': self.ignore_whitespace_check.isChecked()
        }
    
    def open_config(self):
        """打开配置文件"""
        config_file, _ = QFileDialog.getOpenFileName(
            self, "打开配置", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if config_file:
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载配置到界面
                self.version_a_edit.setText(config.get('version_a_source', ''))
                self.version_b_edit.setText(config.get('version_b_source', ''))
                self.test_data_edit.setText(config.get('test_data_dir', ''))
                
                self.status_bar.showMessage(f"配置已加载: {os.path.basename(config_file)}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"配置文件加载失败: {str(e)}")
    
    def save_config(self):
        """保存配置文件"""
        config_file, _ = QFileDialog.getSaveFileName(
            self, "保存配置", "test_config.json", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if config_file:
            try:
                import json
                config = self.get_test_config()
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"配置已保存: {os.path.basename(config_file)}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"配置文件保存失败: {str(e)}")
    
    def open_file(self):
        """打开配置文件"""
        config_file, _ = QFileDialog.getOpenFileName(
            self, "打开配置", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if config_file:
            self.load_config_file(config_file)
    
    def load_config_file(self, config_file):
        """加载配置文件"""
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 加载配置到界面
            if 'version_a_source' in config:
                self.version_a_edit.setText(config['version_a_source'])
            
            if 'version_b_source' in config:
                self.version_b_edit.setText(config['version_b_source'])
            
            if 'test_data_dir' in config:
                self.test_data_edit.setText(config['test_data_dir'])
            
            if 'tolerance' in config:
                self.tolerance_spin.setValue(config['tolerance'])
            
            if 'ignore_whitespace' in config:
                self.ignore_whitespace_check.setChecked(config['ignore_whitespace'])
            
            self.status_bar.showMessage(f"配置已加载: {os.path.basename(config_file)}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"配置文件加载失败: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
            "代码回灌测试系统 v1.0\n\n"
            "一个用于对比两个版本C代码功能差异性的测试工具。\n"
            "支持编译、执行、结果比对和报告生成。\n\n"
            "开发语言: Python\n"
            "GUI框架: PyQt5\n"
            "测试引擎: 自研")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.test_worker and self.test_worker.isRunning():
            reply = QMessageBox.question(
                self, "确认退出", 
                "测试正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.test_worker.stop()
                self.test_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()