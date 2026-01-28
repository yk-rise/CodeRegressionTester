import subprocess
import time
import os
import psutil
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    executable: str
    input_file: str
    output_file: str
    return_code: int
    execution_time: float
    stdout: str
    stderr: str
    success: bool
    memory_usage: float


class CodeExecutor:
    def __init__(self, timeout: int = 30, memory_limit: int = 512):
        self.timeout = timeout
        self.memory_limit = memory_limit  # MB
    
    def execute_with_input(self, executable: str, input_file: str, 
                          output_file: str) -> ExecutionResult:
        """
        执行可执行文件并重定向输入输出
        :param executable: 可执行文件路径
        :param input_file: 输入数据文件
        :param output_file: 输出结果文件
        :return: 执行结果
        """
        start_time = time.time()
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            # 检查可执行文件是否存在
            if not os.path.exists(executable):
                return ExecutionResult(
                    executable=executable,
                    input_file=input_file,
                    output_file=output_file,
                    return_code=-1,
                    execution_time=0,
                    stdout="",
                    stderr=f"Executable not found: {executable}",
                    success=False,
                    memory_usage=0.0
                )
            
            # 检查输入文件是否存在
            if not os.path.exists(input_file):
                return ExecutionResult(
                    executable=executable,
                    input_file=input_file,
                    output_file=output_file,
                    return_code=-1,
                    execution_time=0,
                    stdout="",
                    stderr=f"Input file not found: {input_file}",
                    success=False,
                    memory_usage=0.0
                )
            
            # 打开输入文件
            with open(input_file, 'r') as infile:
                # 打开输出文件
                with open(output_file, 'w') as outfile:
                    # 执行进程
                    process = subprocess.Popen(
                        [executable],
                        stdin=infile,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # 监控执行
                    try:
                        return_code, memory_usage = self.monitor_execution(process)
                        
                        # 获取输出
                        stdout, stderr = process.communicate(timeout=self.timeout)
                        
                        # 写入输出文件
                        outfile.write(stdout)
                        
                        execution_time = time.time() - start_time
                        success = return_code == 0
                        
                        return ExecutionResult(
                            executable=executable,
                            input_file=input_file,
                            output_file=output_file,
                            return_code=return_code,
                            execution_time=execution_time,
                            stdout=stdout,
                            stderr=stderr,
                            success=success,
                            memory_usage=memory_usage
                        )
                        
                    except subprocess.TimeoutExpired:
                        process.kill()
                        return ExecutionResult(
                            executable=executable,
                            input_file=input_file,
                            output_file=output_file,
                            return_code=-1,
                            execution_time=self.timeout,
                            stdout="",
                            stderr=f"Execution timeout after {self.timeout} seconds",
                            success=False,
                            memory_usage=0.0
                        )
                        
        except Exception as e:
            return ExecutionResult(
                executable=executable,
                input_file=input_file,
                output_file=output_file,
                return_code=-1,
                execution_time=time.time() - start_time,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                success=False,
                memory_usage=0.0
            )

    def execute_parallel(self, exec1: str, exec2: str, input_file: str) \
                        -> Tuple[ExecutionResult, ExecutionResult]:
        """并行执行两个版本的可执行文件"""
        import threading
        from queue import Queue
        
        results = Queue()
        
        def execute_version(executable, index):
            output_file = f"output_{index}_{os.path.basename(input_file)}"
            result = self.execute_with_input(executable, input_file, output_file)
            results.put((index, result))
        
        # 创建线程
        thread1 = threading.Thread(target=execute_version, args=(exec1, 1))
        thread2 = threading.Thread(target=execute_version, args=(exec2, 2))
        
        # 启动线程
        thread1.start()
        thread2.start()
        
        # 等待完成
        thread1.join()
        thread2.join()
        
        # 获取结果
        result1 = None
        result2 = None
        
        while not results.empty():
            index, result = results.get()
            if index == 1:
                result1 = result
            else:
                result2 = result
        
        return result1, result2
    
    def monitor_execution(self, process: subprocess.Popen) -> Tuple[int, float]:
        """监控进程执行状态和资源使用"""
        try:
            # 获取进程对象
            pid = process.pid
            if pid:
                proc = psutil.Process(pid)
                
                # 等待进程完成
                while process.poll() is None:
                    # 检查内存使用
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    # 如果超过内存限制，终止进程
                    if memory_mb > self.memory_limit:
                        process.kill()
                        return -1, memory_mb
                    
                    time.sleep(0.1)  # 100ms检查间隔
                
                # 获取最终内存使用
                final_memory = proc.memory_info().rss / 1024 / 1024
                return process.poll(), final_memory
            
            return process.poll(), 0.0
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return process.poll(), 0.0
        except Exception:
            return process.poll(), 0.0
    
    def execute_with_timeout(self, executable: str, input_file: str, 
                            output_file: str, timeout: int = None) -> ExecutionResult:
        """使用自定义超时执行"""
        original_timeout = self.timeout
        if timeout:
            self.timeout = timeout
        
        result = self.execute_with_input(executable, input_file, output_file)
        
        self.timeout = original_timeout
        return result
    
    def validate_executable(self, executable: str) -> bool:
        """验证可执行文件是否有效"""
        if not os.path.exists(executable):
            return False
        
        if not os.access(executable, os.X_OK):
            # 在Windows上，检查文件扩展名
            if os.name == 'nt':
                return executable.lower().endswith(('.exe', '.com', '.bat'))
            return False
        
        return True