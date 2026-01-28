#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple System Test - No Unicode Characters
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test if all modules can be imported"""
    try:
        from core.compiler import CCompiler
        from core.data_manager import DataManager
        from core.comparator import ResultComparator
        from core.report_generator import ReportGenerator
        print("[OK] All core modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_compiler():
    """Test C code compiler with correct method name"""
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
        
        output_file = test_file.replace('.c', '.exe')
        
        try:
            # Test compilation
            compiler = CCompiler()
            result = compiler.compile_code(test_file, output_file)
            
            if result.success:
                print("[OK] Compilation successful")
                print(f"[OK] Executable: {result.output_file}")
                
                # Test execution
                if os.path.exists(result.output_file):
                    proc = subprocess.run([result.output_file], 
                                          capture_output=True, text=True, timeout=5)
                    if "Hello World" in proc.stdout:
                        print("[OK] Execution produces expected output")
                        return True
                    else:
                        print(f"[FAIL] Unexpected output: {proc.stdout}")
                        return False
                else:
                    print("[FAIL] Executable not found")
                    return False
            else:
                print(f"[FAIL] Compilation failed: {result.errors}")
                return False
                
        finally:
            # Cleanup
            for path in [test_file, output_file]:
                if path and os.path.exists(path):
                    os.unlink(path)
                    
    except Exception as e:
        print(f"[FAIL] Compiler test failed: {e}")
        return False

def test_data_manager():
    """Test data manager"""
    try:
        from core.data_manager import DataManager
        
        # Create test data
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, 'test.input')
        
        with open(test_file, 'w') as f:
            f.write('5 3 8 1 9')
        
        try:
            manager = DataManager(data_dir=temp_dir)
            data_files = manager.discover_all_test_files()
            
            if len(data_files) > 0:
                print(f"[OK] Found {len(data_files)} data files")
                return True
            else:
                print("[FAIL] No data files found")
                return False
                
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"[FAIL] Data manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Code Regression Tester - Simple Test ===\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("C Compiler", test_compiler),
        ("Data Manager", test_data_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())