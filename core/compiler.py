import subprocess
import os
import time
import shutil
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CompilationResult:
    success: bool
    output_file: str
    compile_time: float
    errors: str
    warnings: str


class CCompiler:
    def __init__(self, gcc_path: str = "gcc", default_flags: Optional[List[str]] = None):
        self.gcc_path = gcc_path
        self.default_flags = default_flags or ["-O2", "-Wall"]
    
    def compile_code(self, source_file: str, output_file: str, 
                    compile_flags: Optional[List[str]] = None) -> CompilationResult:
        """
        编译C代码文件
        :param source_file: C源文件路径
        :param output_file: 输出可执行文件路径
        :param compile_flags: 编译标志列表
        :return: 编译结果
        """
        start_time = time.time()
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 合并编译标志
        flags = self.default_flags.copy()
        if compile_flags:
            flags.extend(compile_flags)
        
        # 构建编译命令
        cmd = [self.gcc_path] + flags + [source_file, "-o", output_file]
        
        try:
            # 执行编译
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
            )
            
            compile_time = time.time() - start_time
            
            if result.returncode == 0:
                return CompilationResult(
                    success=True,
                    output_file=output_file,
                    compile_time=compile_time,
                    errors="",
                    warnings=result.stderr if result.stderr else ""
                )
            else:
                return CompilationResult(
                    success=False,
                    output_file="",
                    compile_time=compile_time,
                    errors=result.stderr,
                    warnings=""
                )
                
        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                output_file="",
                compile_time=time.time() - start_time,
                errors="Compilation timeout after 60 seconds",
                warnings=""
            )
        except Exception as e:
            return CompilationResult(
                success=False,
                output_file="",
                compile_time=time.time() - start_time,
                errors=f"Compilation error: {str(e)}",
                warnings=""
            )
    
    def validate_source(self, source_file: str) -> bool:
        """验证C源文件的有效性"""
        if not os.path.exists(source_file):
            return False
        
        if not source_file.lower().endswith(('.c', '.cpp')):
            return False
        
        try:
            # 检查文件是否为空
            if os.path.getsize(source_file) == 0:
                return False
            
            # 简单的语法检查 - 尝试编译但不生成输出文件
            temp_output = os.path.join(os.path.dirname(source_file), "temp_check")
            result = self.compile_code(source_file, temp_output, ["-fsyntax-only"])
            
            # 清理临时文件
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            return result.success
            
        except Exception:
            return False
    
    def clean_build(self, build_dir: str) -> None:
        """清理编译目录"""
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
                os.makedirs(build_dir)
            except Exception as e:
                print(f"Failed to clean build directory: {e}")
    
    def get_gcc_version(self) -> str:
        """获取GCC版本信息"""
        try:
            result = subprocess.run(
                [self.gcc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.split('\n')[0] if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"
    
    def check_compiler_available(self) -> bool:
        """检查编译器是否可用"""
        try:
            result = subprocess.run(
                [self.gcc_path, "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False