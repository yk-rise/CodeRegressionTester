import os
import shutil
import hashlib
from typing import List, Optional, Dict, Any
from pathlib import Path


def ensure_directory_exists(directory: str) -> bool:
    """确保目录存在，如果不存在则创建"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory}: {e}")
        return False


def copy_file(source: str, destination: str) -> bool:
    """复制文件"""
    try:
        # 确保目标目录存在
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Failed to copy file from {source} to {destination}: {e}")
        return False


def move_file(source: str, destination: str) -> bool:
    """移动文件"""
    try:
        # 确保目标目录存在
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        shutil.move(source, destination)
        return True
    except Exception as e:
        print(f"Failed to move file from {source} to {destination}: {e}")
        return False


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Failed to delete file {file_path}: {e}")
        return False


def delete_directory(directory: str, ignore_errors: bool = False) -> bool:
    """删除目录及其内容"""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=ignore_errors)
        return True
    except Exception as e:
        print(f"Failed to delete directory {directory}: {e}")
        return False


def get_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
    """计算文件哈希值"""
    try:
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Failed to calculate hash for {file_path}: {e}")
        return None


def are_files_identical(file1: str, file2: str) -> bool:
    """比较两个文件是否相同"""
    try:
        # 首先比较文件大小
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)
        
        if size1 != size2:
            return False
        
        # 如果大小相同，比较哈希值
        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)
        
        return hash1 == hash2
        
    except Exception:
        return False


def find_files_by_pattern(directory: str, pattern: str, 
                         recursive: bool = True) -> List[str]:
    """根据模式查找文件"""
    try:
        if recursive:
            # 使用glob递归搜索
            search_pattern = os.path.join(directory, "**", pattern)
            import glob
            return glob.glob(search_pattern, recursive=True)
        else:
            # 非递归搜索
            search_pattern = os.path.join(directory, pattern)
            import glob
            return glob.glob(search_pattern)
    except Exception as e:
        print(f"Failed to find files with pattern {pattern}: {e}")
        return []


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


def get_file_name_without_extension(file_path: str) -> str:
    """获取不带扩展名的文件名"""
    return Path(file_path).stem


def get_file_size_human_readable(file_path: str) -> str:
    """获取人类可读的文件大小"""
    try:
        size_bytes = os.path.getsize(file_path)
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
        
    except Exception:
        return "Unknown"


def read_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """读取文本文件"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read text file {file_path}: {e}")
        return None


def write_text_file(file_path: str, content: str, 
                   encoding: str = 'utf-8') -> bool:
    """写入文本文件"""
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Failed to write text file {file_path}: {e}")
        return False


def read_binary_file(file_path: str) -> Optional[bytes]:
    """读取二进制文件"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read binary file {file_path}: {e}")
        return None


def write_binary_file(file_path: str, content: bytes) -> bool:
    """写入二进制文件"""
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Failed to write binary file {file_path}: {e}")
        return False


def get_temp_file_path(prefix: str = "temp", suffix: str = "") -> str:
    """获取临时文件路径"""
    import tempfile
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)  # 关闭文件描述符
    return path


def clean_temp_files(directory: str, prefix: str = "temp") -> int:
    """清理临时文件"""
    try:
        cleaned_count = 0
        
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.startswith(prefix):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
        
        return cleaned_count
        
    except Exception as e:
        print(f"Failed to clean temp files in {directory}: {e}")
        return 0


def backup_file(file_path: str, backup_suffix: str = ".bak") -> bool:
    """备份文件"""
    try:
        backup_path = file_path + backup_suffix
        
        # 如果备份文件已存在，添加时间戳
        if os.path.exists(backup_path):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.{timestamp}{backup_suffix}"
        
        return copy_file(file_path, backup_path)
        
    except Exception as e:
        print(f"Failed to backup file {file_path}: {e}")
        return False


def is_text_file(file_path: str) -> bool:
    """判断是否为文本文件"""
    try:
        # 尝试以文本模式读取文件的一小部分
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False


def get_line_count(file_path: str) -> int:
    """获取文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def create_file_info_dict(file_path: str) -> Dict[str, Any]:
    """创建文件信息字典"""
    try:
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        return {
            'path': file_path,
            'name': path_obj.name,
            'stem': path_obj.stem,
            'suffix': path_obj.suffix,
            'size': stat.st_size,
            'size_human': get_file_size_human_readable(file_path),
            'modified_time': stat.st_mtime,
            'created_time': stat.st_ctime,
            'is_file': os.path.isfile(file_path),
            'is_directory': os.path.isdir(file_path),
            'is_readable': os.access(file_path, os.R_OK),
            'is_writable': os.access(file_path, os.W_OK),
            'is_executable': os.access(file_path, os.X_OK),
            'extension': get_file_extension(file_path),
            'line_count': get_line_count(file_path) if is_text_file(file_path) else 0,
            'hash_md5': get_file_hash(file_path, 'md5') if os.path.isfile(file_path) else None
        }
    except Exception as e:
        print(f"Failed to create file info for {file_path}: {e}")
        return {}