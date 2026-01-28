import difflib
import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 简单的numpy/scipy替代实现
class SimpleStats:
    @staticmethod
    def pearsonr(x, y):
        """简单的皮尔逊相关系数计算"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
        
        den = (sum_sq_x * sum_sq_y) ** 0.5
        if den == 0:
            return 0.0
            
        return num / den

@dataclass
class ErrorMetrics:
    mae: float          # 平均绝对误差
    mse: float          # 均方误差
    rmse: float         # 均方根误差
    max_error: float    # 最大误差
    relative_error: float # 相对误差
    correlation: float  # 相关系数

@dataclass
class Difference:
    line_number: int
    type: str           # 'addition', 'deletion', 'change'
    content: str
    context: str

@dataclass
class ComparisonResult:
    test_case: str
    files_identical: bool
    error_metrics: Optional[ErrorMetrics]
    differences: List[Difference]
    similarity_score: float
    overall_status: str  # 'PASS', 'FAIL', 'WARNING'
    version_a_result: Optional['ExecutionResult'] = None
    version_b_result: Optional['ExecutionResult'] = None

class ResultComparator:
    def __init__(self, tolerance: float = 1e-6, ignore_whitespace: bool = True):
        self.tolerance = tolerance
        self.ignore_whitespace = ignore_whitespace
    
    def compare_files(self, file1: str, file2: str) -> ComparisonResult:
        """
        比较两个输出文件
        :param file1: 第一个文件路径
        :param file2: 第二个文件路径
        :return: 比较结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file1) or not os.path.exists(file2):
                return ComparisonResult(
                    test_case=os.path.basename(file1),
                    files_identical=False,
                    error_metrics=None,
                    differences=[],
                    similarity_score=0.0,
                    overall_status='FAIL'
                )
            
            # 读取文件内容
            with open(file1, 'r') as f:
                content1 = f.read()
            
            with open(file2, 'r') as f:
                content2 = f.read()
            
            # 预处理内容
            processed_content1 = self._preprocess_content(content1)
            processed_content2 = self._preprocess_content(content2)
            
            # 检查是否完全相同
            if processed_content1 == processed_content2:
                return ComparisonResult(
                    test_case=os.path.basename(file1),
                    files_identical=True,
                    error_metrics=None,
                    differences=[],
                    similarity_score=1.0,
                    overall_status='PASS'
                )
            
            # 尝试数值比较
            error_metrics = self.analyze_numeric_data(file1, file2)
            
            # 检测文本差异
            differences = self.detect_text_differences(content1, content2)
            
            # 计算相似度分数
            similarity_score = self._calculate_similarity(processed_content1, processed_content2)
            
            # 确定总体状态
            overall_status = self._determine_status(error_metrics, similarity_score)
            
            return ComparisonResult(
                test_case=os.path.basename(file1),
                files_identical=False,
                error_metrics=error_metrics,
                differences=differences,
                similarity_score=similarity_score,
                overall_status=overall_status
            )
            
        except Exception as e:
            return ComparisonResult(
                test_case=os.path.basename(file1),
                files_identical=False,
                error_metrics=None,
                differences=[Difference(line_number=0, type='error', content=str(e), context="")],
                similarity_score=0.0,
                overall_status='FAIL'
            )
    
    def calculate_error_metrics(self, data1, data2) -> ErrorMetrics:
        """计算数值误差指标"""
        if len(data1) == 0 or len(data2) == 0:
            return ErrorMetrics(0, 0, 0, 0, 0, 0)
        
        # 确保数组长度相同
        min_length = min(len(data1), len(data2))
        data1 = data1[:min_length]
        data2 = data2[:min_length]
        
        # 计算各种误差指标
        absolute_errors = [abs(a - b) for a, b in zip(data1, data2)]
        mae = sum(absolute_errors) / len(absolute_errors)
        
        squared_errors = [((a - b) ** 2) for a, b in zip(data1, data2)]
        mse = sum(squared_errors) / len(squared_errors)
        rmse = mse ** 0.5
        
        max_error = max(absolute_errors) if absolute_errors else 0
        
        # 相对误差（避免除零）
        relative_errors = []
        for a, b in zip(data1, data2):
            if abs(a) > 0:
                relative_errors.append(abs(a - b) / abs(a))
            else:
                relative_errors.append(0)
        relative_error = sum(relative_errors) / len(relative_errors)
        
        # 相关系数
        correlation = SimpleStats.pearsonr(data1, data2)
        
        return ErrorMetrics(
            mae=mae,
            mse=mse,
            rmse=rmse,
            max_error=max_error,
            relative_error=relative_error,
            correlation=correlation
        )
    
    def detect_text_differences(self, text1: str, text2: str) -> List[Difference]:
        """检测文本差异"""
        differences = []
        
        # 分割为行
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # 使用difflib比较
        differ = difflib.unified_diff(
            lines1, lines2,
            fromfile='file1',
            tofile='file2',
            lineterm=''
        )
        
        line_number = 0
        for line in differ:
            if line.startswith('@@'):
                # 解析行号信息
                match = re.search(r'-(\d+)', line)
                if match:
                    line_number = int(match.group(1))
            elif line.startswith('-'):
                # 删除行
                content = line[1:].rstrip()
                if content:
                    differences.append(Difference(
                        line_number=line_number,
                        type='deletion',
                        content=content,
                        context=self._get_context(lines1, line_number)
                    ))
                line_number += 1
            elif line.startswith('+'):
                # 添加行
                content = line[1:].rstrip()
                if content:
                    differences.append(Difference(
                        line_number=line_number,
                        type='addition',
                        content=content,
                        context=self._get_context(lines2, line_number)
                    ))
                line_number += 1
            elif not line.startswith('\\') and not line.strip().startswith(' '):
                # 未修改行
                line_number += 1
        
        return differences
    
    def _preprocess_content(self, content: str) -> str:
        """预处理文件内容"""
        if self.ignore_whitespace:
            # 移除多余的空白字符
            content = re.sub(r'\s+', ' ', content.strip())
        
        return content
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """计算相似度分数"""
        # 使用序列匹配器计算相似度
        matcher = difflib.SequenceMatcher(None, content1, content2)
        return matcher.ratio()
    
    def _determine_status(self, error_metrics: Optional[ErrorMetrics], 
                         similarity_score: float) -> str:
        """确定总体状态"""
        if error_metrics is not None:
            # 基于误差指标判断
            if (error_metrics.mae <= self.tolerance and 
                error_metrics.rmse <= self.tolerance * 10):
                return 'PASS'
            elif (error_metrics.mae <= self.tolerance * 100 and 
                  error_metrics.rmse <= self.tolerance * 100):
                return 'WARNING'
            else:
                return 'FAIL'
        else:
            # 基于相似度分数判断
            if similarity_score >= 0.95:
                return 'PASS'
            elif similarity_score >= 0.8:
                return 'WARNING'
            else:
                return 'FAIL'
    
    def _get_context(self, lines: List[str], line_number: int) -> str:
        """获取差异行的上下文"""
        start = max(0, line_number - 2)
        end = min(len(lines), line_number + 3)
        
        context_lines = []
        for i in range(start, end):
            if i < len(lines):
                line = lines[i].rstrip()
                if line:
                    context_lines.append(line)
        
        return '\n'.join(context_lines)