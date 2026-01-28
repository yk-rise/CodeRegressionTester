#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Test - English Version
Test the core functionality of the Code Regression Tester system
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_compiler():
    """Test C code compiler"""
    print("Testing C code compiler...")
    
    try:
        from core.compiler import CCompiler
        
        # Create test C code
        test_code = '''
#include <stdio.h>

int main() {
    printf("Hello World\\n");
    return 0;
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            test_file = f.name
        
        try:
            # Test compilation
            compiler = CCompiler()
            result = compiler.compile(test_file)
            
            if result.success:
                print("  ✓ Compilation successful")
                print(f"  ✓ Executable: {result.executable_path}")
                
                # Test execution
                if result.executable_path and os.path.exists(result.executable_path):
                    proc = subprocess.run([result.executable_path], 
                                          capture_output=True, text=True, timeout=5)
                    if "Hello World" in proc.stdout:
                        print("  ✓ Execution produces expected output")
                    else:
                        print(f"  ✗ Unexpected output: {proc.stdout}")
                else:
                    print("  ✗ Executable not found")
                    
            else:
                print(f"  ✗ Compilation failed: {result.error_message}")
                
        finally:
            # Cleanup
            for path in [test_file, result.executable_path]:
                if path and os.path.exists(path):
                    os.unlink(path)
                    
        return result.success
        
    except Exception as e:
        print(f"  ✗ Compiler test failed: {e}")
        return False

def test_data_manager():
    """Test data manager"""
    print("Testing data manager...")
    
    try:
        from core.data_manager import DataManager
        
        # Create test data files
        test_data = {
            'test1.txt': '5 3 8 1 9',
            'test2.txt': '10 20 30',
            'test3.csv': '1,2,3\n4,5,6\n'
        }
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Write test files
            for filename, content in test_data.items():
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            # Test data manager
            manager = DataManager()
            data_files = manager.discover_data_files(temp_dir)
            
            if len(data_files) >= 3:
                print(f"  ✓ Found {len(data_files)} data files")
                
                # Test loading data
                for data_file in data_files:
                    data = manager.load_data_file(data_file.file_path)
                    if data:
                        print(f"  ✓ Loaded {data_file.filename}: {len(data)} items")
                    else:
                        print(f"  ✗ Failed to load {data_file.filename}")
                        
                return True
            else:
                print(f"  ✗ Expected at least 3 files, found {len(data_files)}")
                return False
                
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"  ✗ Data manager test failed: {e}")
        return False

def test_comparator():
    """Test result comparator"""
    print("Testing result comparator...")
    
    try:
        from core.comparator import ResultComparator
        
        comparator = ResultComparator()
        
        # Test text comparison
        text1 = "Hello World\nLine 2\nLine 3"
        text2 = "Hello World\nModified Line 2\nLine 3\nLine 4"
        
        comparison = comparator.compare_results(text1, text2, "text_test")
        
        if comparison.has_differences:
            print(f"  ✓ Text comparison found {len(comparison.differences)} differences")
            
            # Check difference types
            diff_types = set(diff.category for diff in comparison.differences)
            if diff_types:
                print(f"  ✓ Difference types: {', '.join(diff_types)}")
            
            return True
        else:
            print("  ✗ Text comparison failed to detect differences")
            return False
            
    except Exception as e:
        print(f"  ✗ Comparator test failed: {e}")
        return False

def test_report_generator():
    """Test report generator"""
    print("Testing report generator...")
    
    try:
        from core.report_generator import ReportGenerator
        
        # Create mock comparison result
        from core.data_structures import ComparisonResult, TestResult
        
        test_result_a = TestResult(
            version="version_a",
            exit_code=0,
            stdout="Result A",
            stderr="",
            execution_time=0.1,
            memory_usage=1024,
            success=True
        )
        
        test_result_b = TestResult(
            version="version_b", 
            exit_code=0,
            stdout="Result B",
            stderr="",
            execution_time=0.15,
            memory_usage=1080,
            success=True
        )
        
        comparison = ComparisonResult(
            test_name="test_comparison",
            result_a=test_result_a,
            result_b=test_result_b,
            has_differences=True
        )
        
        # Test HTML report generation
        generator = ReportGenerator()
        report_path = generator.generate_html_report([comparison], "test_report")
        
        if report_path and os.path.exists(report_path):
            print(f"  ✓ HTML report generated: {report_path}")
            
            # Check file size
            file_size = os.path.getsize(report_path)
            if file_size > 0:
                print(f"  ✓ Report file size: {file_size} bytes")
                return True
            else:
                print("  ✗ Report file is empty")
                return False
        else:
            print("  ✗ Failed to generate HTML report")
            return False
            
    except Exception as e:
        print(f"  ✗ Report generator test failed: {e}")
        return False

def test_gui_imports():
    """Test GUI module imports"""
    print("Testing GUI imports...")
    
    try:
        # Test core GUI imports
        from gui.main_window import MainWindow
        from gui.diff_display import DiffDisplayWidget
        print("  ✓ GUI modules imported successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ GUI import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Code Regression Tester - System Test ===\n")
    
    tests = [
        ("C Compiler", test_compiler),
        ("Data Manager", test_data_manager),
        ("Result Comparator", test_comparator),
        ("Report Generator", test_report_generator),
        ("GUI Imports", test_gui_imports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())