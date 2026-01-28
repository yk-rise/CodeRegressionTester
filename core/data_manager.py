import os
import glob
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCase:
    name: str
    input_file: str
    expected_output: Optional[str] = None
    description: str = ""
    timeout: int = 30
    weight: float = 1.0


@dataclass
class TestSuite:
    name: str
    test_cases: List[TestCase]
    description: str = ""
    total_weight: float = 0.0
    
    def __post_init__(self):
        self.total_weight = sum(tc.weight for tc in self.test_cases)


class DataManager:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.supported_extensions = ['.input', '.txt', '.dat', '.csv']
    
    def discover_test_files(self, pattern: str = "*.input") -> List[str]:
        """发现测试数据文件"""
        if not self.data_dir.exists():
            return []
        
        # 搜索匹配的文件
        search_pattern = str(self.data_dir / pattern)
        files = glob.glob(search_pattern)
        
        # 按名称排序
        files.sort()
        
        return files
    
    def discover_all_test_files(self) -> List[str]:
        """发现所有支持的测试数据文件"""
        all_files = []
        
        for ext in self.supported_extensions:
            pattern = f"*{ext}"
            files = self.discover_test_files(pattern)
            all_files.extend(files)
        
        # 去重并排序
        all_files = list(set(all_files))
        all_files.sort()
        
        return all_files
    
    def validate_input_files(self, file_list: List[str]) -> Dict[str, bool]:
        """验证输入文件格式"""
        validation_results = {}
        
        for file_path in file_list:
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    validation_results[file_path] = False
                    continue
                
                # 检查文件是否可读
                if not os.access(file_path, os.R_OK):
                    validation_results[file_path] = False
                    continue
                
                # 检查文件大小
                if os.path.getsize(file_path) == 0:
                    validation_results[file_path] = False
                    continue
                
                # 尝试读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024)  # 读取前1KB检查
                
                # 检查文件内容是否为空
                if not content.strip():
                    validation_results[file_path] = False
                    continue
                
                validation_results[file_path] = True
                
            except Exception:
                validation_results[file_path] = False
        
        return validation_results
    
    def create_test_suite(self, file_list: List[str], 
                         config_file: Optional[str] = None) -> TestSuite:
        """创建测试套件"""
        test_cases = []
        
        # 如果有配置文件，从配置文件加载测试用例
        if config_file and os.path.exists(config_file):
            test_cases = self._load_test_config(config_file)
        else:
            # 否则从文件列表自动创建测试用例
            for i, file_path in enumerate(file_list):
                file_name = Path(file_path).stem
                test_case = TestCase(
                    name=f"Test_{i+1:03d}_{file_name}",
                    input_file=file_path,
                    description=f"Test case for {file_name}"
                )
                test_cases.append(test_case)
        
        # 创建测试套件
        suite_name = self.data_dir.name
        test_suite = TestSuite(
            name=suite_name,
            test_cases=test_cases,
            description=f"Test suite from {self.data_dir}"
        )
        
        return test_suite
    
    def _load_test_config(self, config_file: str) -> List[TestCase]:
        """从配置文件加载测试用例"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            test_cases = []
            
            for test_config in config.get('test_cases', []):
                # 构建完整的文件路径
                input_file = str(self.data_dir / test_config['input_file'])
                
                test_case = TestCase(
                    name=test_config['name'],
                    input_file=input_file,
                    expected_output=test_config.get('expected_output'),
                    description=test_config.get('description', ''),
                    timeout=test_config.get('timeout', 30),
                    weight=test_config.get('weight', 1.0)
                )
                test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"Failed to load test config: {e}")
            return []
    
    def save_test_config(self, test_suite: TestSuite, config_file: str) -> bool:
        """保存测试套件配置到文件"""
        try:
            config = {
                'suite_name': test_suite.name,
                'description': test_suite.description,
                'test_cases': []
            }
            
            for test_case in test_suite.test_cases:
                # 使用相对路径
                input_file = Path(test_case.input_file).relative_to(self.data_dir)
                
                test_config = {
                    'name': test_case.name,
                    'input_file': str(input_file),
                    'description': test_case.description,
                    'timeout': test_case.timeout,
                    'weight': test_case.weight
                }
                
                if test_case.expected_output:
                    test_config['expected_output'] = test_case.expected_output
                
                config['test_cases'].append(test_config)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to save test config: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件详细信息"""
        try:
            file_stat = os.stat(file_path)
            file_path_obj = Path(file_path)
            
            info = {
                'name': file_path_obj.name,
                'stem': file_path_obj.stem,
                'suffix': file_path_obj.suffix,
                'size': file_stat.st_size,
                'size_human': self._format_size(file_stat.st_size),
                'modified_time': file_stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'absolute_path': os.path.abspath(file_path)
            }
            
            # 尝试读取文件内容预览
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024)
                    info['content_preview'] = content
                    info['line_count_estimate'] = content.count('\n') + 1
            except Exception:
                info['content_preview'] = ""
                info['line_count_estimate'] = 0
            
            return info
            
        except Exception:
            return {}
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def create_output_directory(self, base_dir: str) -> str:
        """创建输出目录"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_dir, f"test_results_{timestamp}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        return output_dir
    
    def cleanup_temp_files(self, temp_dir: str) -> None:
        """清理临时文件"""
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Failed to cleanup temp files: {e}")
    
    def validate_data_directory(self) -> Dict[str, Any]:
        """验证数据目录的有效性"""
        result = {
            'valid': True,
            'exists': False,
            'readable': False,
            'file_count': 0,
            'errors': []
        }
        
        try:
            # 检查目录是否存在
            if not self.data_dir.exists():
                result['exists'] = False
                result['valid'] = False
                result['errors'].append(f"Directory does not exist: {self.data_dir}")
                return result
            
            result['exists'] = True
            
            # 检查目录是否可读
            if not os.access(str(self.data_dir), os.R_OK):
                result['readable'] = False
                result['valid'] = False
                result['errors'].append(f"Directory is not readable: {self.data_dir}")
                return result
            
            result['readable'] = True
            
            # 统计文件数量
            all_files = self.discover_all_test_files()
            result['file_count'] = len(all_files)
            
            if result['file_count'] == 0:
                result['valid'] = False
                result['errors'].append("No test files found in directory")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validating directory: {str(e)}")
        
        return result