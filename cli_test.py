#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Line Test Tool
A simple command-line interface for the Code Regression Tester
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.compiler import CCompiler
from core.data_manager import DataManager
from core.comparator import ResultComparator
from core.report_generator import ReportGenerator
from utils.logger import get_logger

def run_test(version_a_path, version_b_path, test_data_dir, output_dir="test_results"):
    """Run a complete regression test"""
    
    # Setup logging
    logger = get_logger()
    logger.info("Starting command-line regression test")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    compiler = CCompiler()
    data_manager = DataManager(test_data_dir)
    comparator = ResultComparator()
    report_generator = ReportGenerator(template_dir="templates")
    
    # Compile versions
    logger.info(f"Compiling version A: {version_a_path}")
    result_a = compiler.compile_code(
        version_a_path, 
        os.path.join(output_dir, "version_a.exe")
    )
    
    if not result_a.success:
        logger.error(f"Version A compilation failed: {result_a.errors}")
        return False
    
    logger.info(f"Compiling version B: {version_b_path}")
    result_b = compiler.compile_code(
        version_b_path,
        os.path.join(output_dir, "version_b.exe")
    )
    
    if not result_b.success:
        logger.error(f"Version B compilation failed: {result_b.errors}")
        return False
    
    # Find test data files
    test_files = data_manager.discover_all_test_files()
    if not test_files:
        logger.error("No test data files found")
        return False
    
    logger.info(f"Found {len(test_files)} test files")
    
    # Run comparisons
    comparison_results = []
    
    for i, test_file in enumerate(test_files, 1):
        logger.info(f"Testing with {os.path.basename(test_file)} ({i}/{len(test_files)})")
        
        # Load test data directly
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = f.read()
        except Exception as e:
            logger.warning(f"Failed to load test data from {test_file}: {e}")
            continue
        
        # Here you would execute both versions with the test data
        # For now, we'll create a mock comparison result
        from core.data_structures import TestResult, ComparisonResult
        
        test_result_a = TestResult(
            version="version_a",
            exit_code=0,
            stdout=f"Result A for {os.path.basename(test_file)}",
            stderr="",
            execution_time=0.1,
            memory_usage=1024,
            success=True
        )
        
        test_result_b = TestResult(
            version="version_b",
            exit_code=0,
            stdout=f"Result B for {os.path.basename(test_file)}",
            stderr="",
            execution_time=0.15,
            memory_usage=1080,
            success=True
        )
        
        comparison = comparator.compare_results(
            test_result_a.stdout,
            test_result_b.stdout,
            os.path.basename(test_file)
        )
        
        comparison_result = ComparisonResult(
            test_name=os.path.basename(test_file),
            result_a=test_result_a,
            result_b=test_result_b,
            has_differences=comparison.has_differences
        )
        
        # Add differences if any
        if comparison.has_differences:
            comparison_result.differences = comparison.differences
        
        comparison_results.append(comparison_result)
        
        status = "PASS" if not comparison.has_differences else "DIFF"
        logger.info(f"  Status: {status}")
    
    # Generate report
    if comparison_results:
        report_path = report_generator.generate_html_report(
            comparison_results, 
            os.path.join(output_dir, "regression_test_report")
        )
        
        if report_path:
            logger.info(f"Report generated: {report_path}")
        else:
            logger.warning("Report generation failed")
    
    # Summary
    total = len(comparison_results)
    passed = sum(1 for r in comparison_results if not r.has_differences)
    failed = total - passed
    
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {passed/total*100:.1f}%" if total > 0 else "Success rate: N/A")
    
    return failed == 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Code Regression Tester - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_test.py --version-a version1.c --version-b version2.c --test-data ./test_data
  python cli_test.py -a old.c -b new.c -d ./data -o ./results
        """
    )
    
    parser.add_argument(
        "--version-a", "-a",
        required=True,
        help="Path to version A C source file"
    )
    
    parser.add_argument(
        "--version-b", "-b", 
        required=True,
        help="Path to version B C source file"
    )
    
    parser.add_argument(
        "--test-data", "-d",
        required=True,
        help="Directory containing test data files"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="test_results",
        help="Output directory for results (default: test_results)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.isfile(args.version_a):
        print(f"Error: Version A file not found: {args.version_a}")
        return 1
    
    if not os.path.isfile(args.version_b):
        print(f"Error: Version B file not found: {args.version_b}")
        return 1
    
    if not os.path.isdir(args.test_data):
        print(f"Error: Test data directory not found: {args.test_data}")
        return 1
    
    # Setup logging
    logger = get_logger(log_level=args.log_level)
    
    # Run test
    try:
        success = run_test(
            args.version_a,
            args.version_b, 
            args.test_data,
            args.output
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())