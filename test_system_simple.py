# -*- coding: utf-8 -*-

"""
独立版本的代码回灌测试系统
"""

import os
import sys

def create_simple_test_data():
    """创建简单测试数据"""
    test_dir = "simple_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文件
    files = {
        "identical_a.txt": "Hello, world!\n",
        "identical_b.txt": "Hello, world!\n",
        "modified_a.txt": "Hello, Modified World!\n",
        "modified_b.txt": "Hello, Modified Version!\n",
        "numeric_a.txt": "1\n2\n3\n4\n5",
        "numeric_b.txt": "1.1\n1\n1\n1"
    }
    
    for filename, content in files.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
    
    return test_dir, files

def test_core_functionality():
    """测试核心功能"""
    print("🔍 核心功能测试...")
    
    try:
        from core.comparator import ResultComparator
        print("✅ ResultComparator 导入成功")
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
        return False
    
    try:
        from utils.diff_utils import create_enhanced_diff_display
        print("✅ 差异显示工具导入成功")
    except ImportError as e:
        print(f"❌ 差异显示工具导入失败: {e}")
        return False
    
    # 创建测试数据
    test_dir, test_files = create_simple_test_data()
    
    # 执行对比测试
    print("\n📊 测试文件对比...")
    
    comparator = ResultComparator()
    
    try:
        # 测试完全相同的文件
        result1 = comparator.compare_files(
            os.path.join(test_dir, "identical_a.txt"),
            os.path.join(test_dir, "identical_b.txt")
        )
        print(f"  相同文件比较: {result.overall_status}")
        print(f"  相似度: {result.similarity_score:.3f}")
        
        # 测试轻微修改的文件
        result2 = comparator.compare_files(
            os.path.join(test_dir, "identical_a.txt"),
            os.path.join(test_dir, "modified_b.txt")
        )
        print(f" 修改文件比较: {result2.overall_status}")
        print(f" 相似度: {result2.similarity_score:.3f}")
        
        # 测试数值文件
        result3 = comparator.compare_files(
            os.path.join(test_dir, "numeric_a.txt"),
            os.path.join(test_dir, "numeric_b.txt")
        )
        print(f" 数值文件比较: {result3.overall_status}")
        if result3.error_metrics:
            print(f"   平均误差: {result3.error_metrics.mae:.6f}")
        
        # 测试完全不同的文件
        result4 = comparator.compare_files(
            os.path.join(test_dir, "identical_a.txt"),
            os.path.join(test_dir, "error_case.txt")
        )
        print(f" 不同文件比较: {result4.overall_status}")
        print(f" 相似度: {result4.similarity_score:.3f}")
        
        print("\n🎉 所有测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 核心功能测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    
    if success:
        print("\n🎉 所有必要核心功能验证通过!")
        print("\n现在可以开始GUI测试或使用以下命令:")
        print("   python main.py # 启动完整GUI版本")
        print("\n   python test_system_final.py # 启动简化测试版本")
    else:
        print("\n❌ 系统验证失败，请检查错误信息")
        sys.exit(1)