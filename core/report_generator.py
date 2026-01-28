import os
import base64
from typing import List, Dict, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import io


class ReportGenerator:
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_html_report(self, results: List[Any], 
                           output_file: str, config: Dict[str, Any] = None) -> bool:
        """生成HTML格式报告"""
        try:
            # 加载模板
            template = self.jinja_env.get_template('report_template.html')
            
            # 准备报告数据
            report_data = self._prepare_report_data(results, config)
            
            # 渲染模板
            html_content = template.render(**report_data)
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to generate HTML report: {e}")
            return False
    
    def convert_to_pdf(self, html_file: str, pdf_file: str) -> bool:
        """将HTML报告转换为PDF"""
        try:
            import weasyprint
            
            # 转换HTML到PDF
            weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
            
            return True
            
        except ImportError:
            print("WeasyPrint not available. Please install it for PDF conversion.")
            return False
        except Exception as e:
            print(f"Failed to convert to PDF: {e}")
            return False
    
    def create_summary_charts(self, results: List[Any]) -> Dict[str, str]:
        """创建汇总图表"""
        charts = {}
        
        try:
            # 状态分布饼图
            status_chart = self._create_status_pie_chart(results)
            if status_chart:
                charts['status_distribution'] = status_chart
            
            # 误差分析柱状图
            error_chart = self._create_error_bar_chart(results)
            if error_chart:
                charts['error_analysis'] = error_chart
            
            # 执行时间趋势图
            time_chart = self._create_time_line_chart(results)
            if time_chart:
                charts['execution_time'] = time_chart
            
        except Exception as e:
            print(f"Failed to create charts: {e}")
        
        return charts
    
    def _prepare_report_data(self, results: List[Any], 
                           config: Dict[str, Any] = None) -> Dict[str, Any]:
        """准备报告数据"""
        # 统计信息
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.overall_status == 'PASS')
        failed_tests = sum(1 for r in results if r.overall_status == 'FAIL')
        warning_tests = sum(1 for r in results if r.overall_status == 'WARNING')
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 执行时间统计
        execution_times = []
        for result in results:
            if hasattr(result, 'version_a_result') and result.version_a_result:
                execution_times.append(result.version_a_result.execution_time)
            if hasattr(result, 'version_b_result') and result.version_b_result:
                execution_times.append(result.version_b_result.execution_time)
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # 误差统计
        error_metrics = []
        for result in results:
            if result.error_metrics:
                error_metrics.append(result.error_metrics)
        
        # 创建图表
        charts = self.create_summary_charts(results)
        
        return {
            'title': '代码回灌测试报告',
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'config': config or {},
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'warning_tests': warning_tests,
                'pass_rate': f"{pass_rate:.2f}%",
                'avg_execution_time': f"{avg_execution_time:.3f}s"
            },
            'results': results,
            'charts': charts,
            'error_summary': self._calculate_error_summary(error_metrics)
        }
    
    def _create_status_pie_chart(self, results: List[Any]) -> str:
        """创建状态分布饼图"""
        try:
            # 统计状态
            status_counts = {'PASS': 0, 'FAIL': 0, 'WARNING': 0}
            for result in results:
                status_counts[result.overall_status] += 1
            
            # 创建饼图
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#4CAF50', '#F44336', '#FF9800']
            labels = []
            sizes = []
            
            for status, count in status_counts.items():
                if count > 0:
                    labels.append(f"{status} ({count})")
                    sizes.append(count)
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors[:len(sizes)], 
                      autopct='%1.1f%%', startangle=90)
                ax.set_title('测试状态分布', fontsize=14, fontweight='bold')
                
                # 转换为base64
                return self._fig_to_base64(fig)
            
            plt.close(fig)
            return ""
            
        except Exception as e:
            print(f"Failed to create status pie chart: {e}")
            return ""
    
    def _create_error_bar_chart(self, results: List[Any]) -> str:
        """创建误差分析柱状图"""
        try:
            # 收集误差数据
            mae_values = []
            rmse_values = []
            test_names = []
            
            for i, result in enumerate(results):
                if result.error_metrics:
                    mae_values.append(result.error_metrics.mae)
                    rmse_values.append(result.error_metrics.rmse)
                    test_names.append(f"Test{i+1}")
            
            if not mae_values:
                return ""
            
            # 创建柱状图
            fig, ax = plt.subplots(figsize=(12, 6))
            x = range(len(test_names))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], mae_values, width, 
                          label='MAE', color='#2196F3', alpha=0.7)
            bars2 = ax.bar([i + width/2 for i in x], rmse_values, width, 
                          label='RMSE', color='#FF5722', alpha=0.7)
            
            ax.set_xlabel('测试用例')
            ax.set_ylabel('误差值')
            ax.set_title('误差分析', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(test_names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 添加数值标签
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2e}', ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2e}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            
            # 转换为base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Failed to create error bar chart: {e}")
            return ""
    
    def _create_time_line_chart(self, results: List[Any]) -> str:
        """创建执行时间趋势图"""
        try:
            # 收集执行时间数据
            times_a = []
            times_b = []
            test_names = []
            
            for i, result in enumerate(results):
                test_names.append(f"Test{i+1}")
                
                if hasattr(result, 'version_a_result') and result.version_a_result:
                    times_a.append(result.version_a_result.execution_time)
                else:
                    times_a.append(0)
                
                if hasattr(result, 'version_b_result') and result.version_b_result:
                    times_b.append(result.version_b_result.execution_time)
                else:
                    times_b.append(0)
            
            if not times_a and not times_b:
                return ""
            
            # 创建折线图
            fig, ax = plt.subplots(figsize=(12, 6))
            x = range(len(test_names))
            
            if any(times_a):
                ax.plot(x, times_a, marker='o', label='版本A', 
                       color='#4CAF50', linewidth=2, markersize=6)
            
            if any(times_b):
                ax.plot(x, times_b, marker='s', label='版本B', 
                       color='#2196F3', linewidth=2, markersize=6)
            
            ax.set_xlabel('测试用例')
            ax.set_ylabel('执行时间 (秒)')
            ax.set_title('执行时间趋势', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(test_names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 转换为base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Failed to create time line chart: {e}")
            return ""
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图形转换为base64字符串"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Failed to convert figure to base64: {e}")
            plt.close(fig)
            return ""
    
    def _calculate_error_summary(self, error_metrics: List[Any]) -> Dict[str, Any]:
        """计算误差汇总统计"""
        if not error_metrics:
            return {}
        
        try:
            # 提取数值
            mae_values = [em.mae for em in error_metrics]
            mse_values = [em.mse for em in error_metrics]
            rmse_values = [em.rmse for em in error_metrics]
            max_errors = [em.max_error for em in error_metrics]
            relative_errors = [em.relative_error for em in error_metrics]
            correlations = [em.correlation for em in error_metrics]
            
            return {
                'mae': {
                    'mean': sum(mae_values) / len(mae_values),
                    'min': min(mae_values),
                    'max': max(mae_values),
                    'std': self._calculate_std(mae_values)
                },
                'rmse': {
                    'mean': sum(rmse_values) / len(rmse_values),
                    'min': min(rmse_values),
                    'max': max(rmse_values),
                    'std': self._calculate_std(rmse_values)
                },
                'max_error': {
                    'mean': sum(max_errors) / len(max_errors),
                    'min': min(max_errors),
                    'max': max(max_errors)
                },
                'correlation': {
                    'mean': sum(correlations) / len(correlations),
                    'min': min(correlations),
                    'max': max(correlations)
                }
            }
            
        except Exception as e:
            print(f"Failed to calculate error summary: {e}")
            return {}
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance ** 0.5