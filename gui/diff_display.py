import re
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QFont
from PyQt5.QtCore import Qt

class DiffDisplayWidget(QTextEdit):
    """增强的差异显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setup_styles()
        
    def setup_styles(self):
        """设置差异显示样式"""
        self.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                line-height: 1.4;
                selection-background-color: #3498db;
            }
        """)
        
        # 定义文本格式
        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor("#333333"))
        
        self.addition_format = QTextCharFormat()
        self.addition_format.setBackground(QColor("#d4edda"))  # 浅绿色
        self.addition_format.setForeground(QColor("#155724"))
        
        self.deletion_format = QTextCharFormat()
        self.deletion_format.setBackground(QColor("#f8d7da"))  # 浅红色
        self.deletion_format.setForeground(QColor("#721c24"))
        
        self.change_format = QTextCharFormat()
        self.change_format.setBackground(QColor("#fff3cd"))  # 浅黄色
        self.change_format.setForeground(QColor("#856404"))
        
        self.line_number_format = QTextCharFormat()
        self.line_number_format.setBackground(QColor("#f0f0f0"))
        self.line_number_format.setForeground(QColor("#666666"))
        
        self.context_format = QTextCharFormat()
        self.context_format.setForeground(QColor("#888888"))
    
    def display_unified_diff(self, diff_text):
        """显示统一格式差异"""
        self.clear()
        cursor = self.textCursor()
        
        lines = diff_text.split('\n')
        
        for line in lines:
            if line.startswith('@@'):
                # 文件头信息
                cursor.insertText(line + '\n', self.line_number_format)
            elif line.startswith('-'):
                # 删除行
                display_line = line[1:]  # 移除'-'前缀
                cursor.insertText('- ', self.deletion_format)
                cursor.insertText(display_line + '\n', self.deletion_format)
            elif line.startswith('+'):
                # 添加行
                display_line = line[1:]  # 移除'+'前缀
                cursor.insertText('+ ', self.addition_format)
                cursor.insertText(display_line + '\n', self.addition_format)
            elif line.startswith(' '):
                # 未修改行（上下文）
                display_line = line[1:]  # 移除空格前缀
                cursor.insertText('  ', self.context_format)
                cursor.insertText(display_line + '\n', self.default_format)
            else:
                # 其他行（如文件信息）
                cursor.insertText(line + '\n', self.line_number_format)
    
    def display_side_by_side(self, file1_content, file2_content, differences):
        """并排显示两个文件的差异"""
        self.clear()
        cursor = self.textCursor()
        
        lines1 = file1_content.splitlines()
        lines2 = file2_content.splitlines()
        
        max_lines = max(len(lines1), len(lines2))
        
        # 添加标题
        cursor.insertText("文件A" + " " * 40 + "文件B\n", self.line_number_format)
        cursor.insertText("=" * 40 + " " + "=" * 40 + "\n\n", self.line_number_format)
        
        for i in range(max_lines):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""
            
            # 检查这一行是否有差异
            diff_info = self.get_line_diff_info(i, differences)
            
            if diff_info:
                # 有差异的行
                cursor.insertText(f"{i+1:3d} - ", self.line_number_format)
                if line1:
                    if diff_info['type'] in ['deletion', 'change']:
                        cursor.insertText(line1, self.deletion_format if diff_info['type'] == 'deletion' else self.change_format)
                    else:
                        cursor.insertText(line1, self.default_format)
                else:
                    cursor.insertText("", self.deletion_format)
                
                # 补充空格到固定宽度
                spaces = " " * max(1, 40 - len(line1))
                cursor.insertText(spaces, self.default_format)
                
                cursor.insertText(f"{i+1:3d} + ", self.line_number_format)
                if line2:
                    if diff_info['type'] in ['addition', 'change']:
                        cursor.insertText(line2, self.addition_format if diff_info['type'] == 'addition' else self.change_format)
                    else:
                        cursor.insertText(line2, self.default_format)
                else:
                    cursor.insertText("", self.addition_format)
            else:
                # 无差异的行
                cursor.insertText(f"{i+1:3d}   ", self.line_number_format)
                cursor.insertText(line1, self.default_format)
                spaces = " " * max(1, 40 - len(line1))
                cursor.insertText(spaces, self.default_format)
                cursor.insertText(f"{i+1:3d}   ", self.line_number_format)
                cursor.insertText(line2, self.default_format)
            
            cursor.insertText('\n', self.default_format)
            
            # 在差异行后添加分隔线
            if diff_info:
                cursor.insertText('-' * 90 + '\n', self.line_number_format)
        
        # 添加差异统计
        self.add_diff_summary(cursor, differences)
    
    def get_line_diff_info(self, line_num, differences):
        """获取指定行的差异信息"""
        for diff in differences:
            if diff.line_number == line_num + 1:  # 行号从1开始
                return diff
        return None
    
    def add_diff_summary(self, cursor, differences):
        """添加差异统计信息"""
        if not differences:
            return
        
        cursor.insertText('\n' + '=' * 90 + '\n', self.line_number_format)
        cursor.insertText("差异统计摘要:\n\n", self.line_number_format)
        
        # 统计各种差异类型
        additions = sum(1 for d in differences if d.type == 'addition')
        deletions = sum(1 for d in differences if d.type == 'deletion')
        changes = sum(1 for d in differences if d.type == 'change')
        
        cursor.insertText(f"• 新增行数: {additions}\n", self.addition_format)
        cursor.insertText(f"• 删除行数: {deletions}\n", self.deletion_format)
        cursor.insertText(f"• 修改行数: {changes}\n", self.change_format)
        cursor.insertText(f"• 总差异数: {len(differences)}\n\n", self.line_number_format)
        
        # 显示关键差异位置
        cursor.insertText("关键差异位置:\n", self.line_number_format)
        for diff in differences[:5]:  # 只显示前5个重要差异
            cursor.insertText(f"• 行 {diff.line_number}: {diff.type} - {diff.content[:50]}...\n", 
                          self.get_format_for_type(diff.type))
    
    def get_format_for_type(self, diff_type):
        """根据差异类型获取格式"""
        if diff_type == 'addition':
            return self.addition_format
        elif diff_type == 'deletion':
            return self.deletion_format
        elif diff_type == 'change':
            return self.change_format
        else:
            return self.default_format
    
    def display_enhanced_diff(self, result):
        """显示增强的差异信息"""
        self.clear()
        cursor = self.textCursor()
        
        # 添加测试信息头部
        cursor.insertText(f"测试用例: {result.test_case}\n", self.line_number_format)
        cursor.insertText(f"总体状态: {result.overall_status}\n", 
                       self.get_status_format(result.overall_status))
        cursor.insertText(f"相似度: {result.similarity_score:.3f}\n", self.default_format)
        cursor.insertText("=" * 80 + "\n\n", self.line_number_format)
        
        # 如果有误差指标，显示数值差异分析
        if result.error_metrics:
            cursor.insertText("数值误差分析:\n", self.line_number_format)
            cursor.insertText(f"  平均绝对误差 (MAE): {result.error_metrics.mae:.6e}\n", 
                           self.default_format)
            cursor.insertText(f"  均方根误差 (RMSE): {result.error_metrics.rmse:.6e}\n", 
                           self.default_format)
            cursor.insertText(f"  最大误差: {result.error_metrics.max_error:.6e}\n", 
                           self.default_format)
            cursor.insertText(f"  相关系数: {result.error_metrics.correlation:.4f}\n\n", 
                           self.default_format)
        
        # 显示文本差异
        if result.differences:
            cursor.insertText("文本差异详情:\n", self.line_number_format)
            cursor.insertText("-" * 40 + "\n", self.line_number_format)
            
            for diff in result.differences[:10]:  # 限制显示数量
                self.display_single_diff(cursor, diff)
            
            if len(result.differences) > 10:
                cursor.insertText(f"\n... 还有 {len(result.differences) - 10} 个差异\n", 
                               self.context_format)
        
        # 如果有执行结果，显示输出对比
        if hasattr(result, 'version_a_result') and hasattr(result, 'version_b_result'):
            self.display_output_comparison(cursor, result.version_a_result, result.version_b_result)
    
    def display_single_diff(self, cursor, diff):
        """显示单个差异"""
        # 差异类型标识
        type_symbol = {"addition": "+", "deletion": "-", "change": "~"}.get(diff.type, "?")
        type_format = self.get_format_for_type(diff.type)
        
        cursor.insertText(f"\n{type_symbol} 行 {diff.line_number} [{diff.type}]:\n", type_format)
        cursor.insertText(f"  内容: {diff.content}\n", type_format)
        
        # 显示上下文
        if diff.context:
            cursor.insertText("  上下文:\n", self.context_format)
            context_lines = diff.context.split('\n')
            for line in context_lines:
                cursor.insertText(f"    {line}\n", self.context_format)
    
    def get_status_format(self, status):
        """根据状态获取文本格式"""
        if status == 'PASS':
            format_obj = QTextCharFormat()
            format_obj.setForeground(QColor("#27ae60"))
            format_obj.setFontWeight(QFont.Bold)
            return format_obj
        elif status == 'FAIL':
            format_obj = QTextCharFormat()
            format_obj.setForeground(QColor("#e74c3c"))
            format_obj.setFontWeight(QFont.Bold)
            return format_obj
        elif status == 'WARNING':
            format_obj = QTextCharFormat()
            format_obj.setForeground(QColor("#f39c12"))
            format_obj.setFontWeight(QFont.Bold)
            return format_obj
        else:
            return self.default_format
    
    def display_output_comparison(self, cursor, result_a, result_b):
        """显示两个版本的输出对比"""
        if not (result_a and result_b and result_a.stdout and result_b.stdout):
            return
        
        cursor.insertText("\n" + "=" * 80 + "\n", self.line_number_format)
        cursor.insertText("执行输出对比:\n", self.line_number_format)
        cursor.insertText("-" * 40 + "\n", self.line_number_format)
        
        lines_a = result_a.stdout.splitlines()
        lines_b = result_b.stdout.splitlines()
        
        cursor.insertText("版本A输出" + " " * 30 + "版本B输出\n", self.line_number_format)
        cursor.insertText("-" * 20 + " " + "-" * 20 + "\n", self.line_number_format)
        
        max_lines = max(len(lines_a), len(lines_b))
        
        for i in range(max(10, max_lines)):  # 最多显示10行或所有行
            line_a = lines_a[i] if i < len(lines_a) else ""
            line_b = lines_b[i] if i < len(lines_b) else ""
            
            # 检查行是否不同
            if line_a != line_b:
                cursor.insertText(f"{i+1:2d}: ", self.line_number_format)
                cursor.insertText(line_a + "\n", self.deletion_format if line_a else self.context_format)
                cursor.insertText(f"{i+1:2d}: ", self.line_number_format)
                cursor.insertText(line_b + "\n", self.addition_format if line_b else self.context_format)
                cursor.insertText("-" * 40 + "\n", self.line_number_format)
            else:
                if i < 10:  # 相同行只在开头显示
                    cursor.insertText(f"{i+1:2d}: ", self.line_number_format)
                    cursor.insertText(line_a + "\n", self.default_format)
                    cursor.insertText(f"{i+1:2d}: ", self.line_number_format)
                    cursor.insertText(line_b + "\n", self.default_format)
                elif i < max_lines:
                    cursor.insertText(f"    ... ({max_lines - 10} more identical lines)\n", self.context_format)
                    break