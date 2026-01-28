import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    def __init__(self, name: str = "CodeRegressionTester", 
                 log_file: str = "app.log", log_level: str = "INFO"):
        """初始化日志器"""
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        self.setup_logger(log_level)
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        self.setup_logger(log_level)
    
    def setup_logger(self, log_level: str) -> None:
        """设置日志配置"""
        # 清除现有的处理器
        self.logger.handlers.clear()
        
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（带轮转）
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Failed to setup file logger: {e}")
    
    def log_compilation(self, source_file: str, result) -> None:
        """记录编译日志"""
        if result.success:
            self.logger.info(f"Compilation successful: {source_file} -> {result.output_file} ({result.compile_time:.3f}s)")
            if result.warnings:
                self.logger.warning(f"Compilation warnings for {source_file}: {result.warnings}")
        else:
            self.logger.error(f"Compilation failed for {source_file}: {result.errors}")
    
    def log_execution(self, test_case: str, result) -> None:
        """记录执行日志"""
        if result.success:
            self.logger.info(f"Execution successful: {test_case} ({result.execution_time:.3f}s, memory: {result.memory_usage:.1f}MB)")
        else:
            self.logger.error(f"Execution failed for {test_case}: {result.stderr}")
    
    def log_comparison(self, test_case: str, result) -> None:
        """记录比较日志"""
        self.logger.info(f"Comparison for {test_case}: status={result.overall_status}, similarity={result.similarity_score:.3f}")
        
        if result.error_metrics:
            self.logger.info(f"Error metrics for {test_case}: MAE={result.error_metrics.mae:.2e}, RMSE={result.error_metrics.rmse:.2e}")
        
        if result.differences:
            diff_count = len(result.differences)
            self.logger.warning(f"Found {diff_count} differences in {test_case}")
    
    def log_test_start(self, config) -> None:
        """记录测试开始"""
        self.logger.info("=" * 50)
        self.logger.info("Starting code regression test")
        self.logger.info(f"Version A: {config.get('version_a_source', 'N/A')}")
        self.logger.info(f"Version B: {config.get('version_b_source', 'N/A')}")
        self.logger.info(f"Test data: {config.get('test_data_dir', 'N/A')}")
        self.logger.info(f"Tolerance: {config.get('tolerance', 'N/A')}")
        self.logger.info("=" * 50)
    
    def log_test_complete(self, results) -> None:
        """记录测试完成"""
        total = len(results)
        passed = sum(1 for r in results if r.overall_status == 'PASS')
        failed = sum(1 for r in results if r.overall_status == 'FAIL')
        warning = sum(1 for r in results if r.overall_status == 'WARNING')
        
        self.logger.info("=" * 50)
        self.logger.info("Test completed")
        self.logger.info(f"Total: {total}, Passed: {passed}, Failed: {failed}, Warning: {warning}")
        self.logger.info(f"Pass rate: {passed/total*100:.1f}%" if total > 0 else "Pass rate: N/A")
        self.logger.info("=" * 50)
    
    def log_report_generation(self, report_file: str, success: bool) -> None:
        """记录报告生成"""
        if success:
            self.logger.info(f"Report generated successfully: {report_file}")
        else:
            self.logger.error(f"Report generation failed: {report_file}")
    
    def debug(self, message: str) -> None:
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """严重错误日志"""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """异常日志（包含堆栈跟踪）"""
        self.logger.exception(message)


# 全局日志实例
_global_logger = None


def get_logger(name: str = "CodeRegressionTester", 
              log_file: str = "app.log", log_level: str = "INFO") -> Logger:
    """获取全局日志实例"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Logger(name, log_file, log_level)
    
    return _global_logger


def setup_logging(log_file: str = "app.log", log_level: str = "INFO") -> None:
    """设置全局日志"""
    global _global_logger
    _global_logger = Logger("CodeRegressionTester", log_file, log_level)