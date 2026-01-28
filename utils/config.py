import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_config()
        except Exception:
            return self.get_default_config()
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "compiler": {
                "gcc_path": "gcc",
                "default_flags": ["-O2", "-Wall"],
                "timeout": 60
            },
            "executor": {
                "timeout": 30,
                "memory_limit": 512
            },
            "comparison": {
                "tolerance": 1e-6,
                "ignore_whitespace": True
            },
            "gui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "default"
            },
            "report": {
                "template_dir": "templates",
                "output_format": "html",
                "include_charts": True
            }
        }
    
    def get_compiler_settings(self) -> Dict[str, Any]:
        """获取编译器设置"""
        return self.config.get("compiler", {})
    
    def get_comparison_settings(self) -> Dict[str, Any]:
        """获取比较设置"""
        return self.config.get("comparison", {})
    
    def get_executor_settings(self) -> Dict[str, Any]:
        """获取执行器设置"""
        return self.config.get("executor", {})
    
    def get_gui_settings(self) -> Dict[str, Any]:
        """获取GUI设置"""
        return self.config.get("gui", {})
    
    def get_report_settings(self) -> Dict[str, Any]:
        """获取报告设置"""
        return self.config.get("report", {})
    
    def set_compiler_settings(self, settings: Dict[str, Any]) -> None:
        """设置编译器配置"""
        self.config["compiler"] = {**self.get_compiler_settings(), **settings}
    
    def set_comparison_settings(self, settings: Dict[str, Any]) -> None:
        """设置比较配置"""
        self.config["comparison"] = {**self.get_comparison_settings(), **settings}
    
    def set_executor_settings(self, settings: Dict[str, Any]) -> None:
        """设置执行器配置"""
        self.config["executor"] = {**self.get_executor_settings(), **settings}
    
    def set_gui_settings(self, settings: Dict[str, Any]) -> None:
        """设置GUI配置"""
        self.config["gui"] = {**self.get_gui_settings(), **settings}
    
    def set_report_settings(self, settings: Dict[str, Any]) -> None:
        """设置报告配置"""
        self.config["report"] = {**self.get_report_settings(), **settings}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        config = self.config
        
        # 导航到最后一级的父对象
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置最终值
        config[keys[-1]] = value
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = self.get_default_config()