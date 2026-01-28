#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple CLI Test Tool - Minimal dependencies
A simplified command-line interface for Code Regression Tester
"""

import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path

def compile_c_code(source_file, output_file):
    """Compile C code using gcc"""
    try:
        result = subprocess.run(
            ['gcc', source_file, '-o', output_file, '-O2', '-Wall'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Compilation timeout"
    except Exception as e:
        return False, "", str(e)

def execute_program(executable, input_data):
    """Execute program with input data"""
    try:
        result = subprocess.run(
            [executable],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Execution timeout"
    except Exception as e:
        return False, "", str(e)

def compare_outputs(output_a, output_b):
    """Compare two outputs"""
    if output_a == output_b:
        return True, "Outputs are identical", []
    
    # Simple diff
    lines_a = output_a.splitlines()
    lines_b = output_b.splitlines()
    
    differences = []
    max_lines = max(len(lines_a), len(lines_b))
    
    for i in range(max_lines):
        line_a = lines_a[i] if i < len(lines_a) else "<MISSING>"
        line_b = lines_b[i] if i < len(lines_b) else "<MISSING>"
        
        if line_a != line_b:
            differences.append({
                'line': i + 1,
                'file_a': line_a,
                'file_b': line_b,
                'type': 'modified'
            })
    
    return False, f"Found {len(differences)} differences", differences

def generate_html_report(results, output_path):
    """Generate simple HTML report"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Regression Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
        .pass {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .fail {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        .diff {{ font-family: monospace; font-size: 12px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Regression Test Report</h1>
        <p>Generated on: {os.path.basename(output_path)}</p>
    </div>
    
    <h2>Test Summary</h2>
    <table>
        <tr>
            <th>Total Tests</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Success Rate</th>
        </tr>
"""
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    html_content += f"""
        <tr>
            <td>{total}</td>
            <td>{passed}</td>
            <td>{failed}</td>
            <td>{success_rate:.1f}%</td>
        </tr>
    </table>
    
    <h2>Test Details</h2>
"""
    
    for result in results:
        status_class = "pass" if result['passed'] else "fail"
        status_text = "PASS" if result['passed'] else "FAIL"
        
        html_content += f"""
    <div class="test-result {status_class}">
        <h3>{result['test_name']} - {status_text}</h3>
        <p><strong>File:</strong> {result['test_file']}</p>
        <p><strong>Status:</strong> {result['message']}</p>
        <p><strong>Version A Output:</strong></p>
        <pre class="diff">{result['output_a']}</pre>
        <p><strong>Version B Output:</strong></p>
        <pre class="diff">{result['output_b']}</pre>
"""
        
        if not result['passed'] and result['differences']:
            html_content += "<p><strong>Differences:</strong></p><table>"
            html_content += "<tr><th>Line</th><th>Version A</th><th>Version B</th></tr>"
            
            for diff in result['differences'][:20]:  # Limit to first 20 differences
                html_content += f"""
                <tr>
                    <td>{diff['line']}</td>
                    <td>{diff['file_a']}</td>
                    <td>{diff['file_b']}</td>
                </tr>
"""
            
            if len(result['differences']) > 20:
                html_content += f"<tr><td colspan='3'>... and {len(result['differences']) - 20} more differences</td></tr>"
            
            html_content += "</table>"
        
        html_content += "</div>"
    
    html_content += """
</body>
</html>
"""
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"Failed to write report: {e}")
        return False

def run_test(version_a_path, version_b_path, test_data_dir, output_dir="test_results"):
    """Run a complete regression test"""
    
    print("Starting code regression test...")
    print(f"Version A: {version_a_path}")
    print(f"Version B: {version_b_path}")
    print(f"Test data: {test_data_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Compile versions
    print("Compiling version A...")
    success_a, stdout_a, stderr_a = compile_c_code(
        version_a_path, 
        os.path.join(output_dir, "version_a.exe")
    )
    
    if not success_a:
        print(f"ERROR: Version A compilation failed: {stderr_a}")
        return False
    
    print("Compiling version B...")
    success_b, stdout_b, stderr_b = compile_c_code(
        version_b_path,
        os.path.join(output_dir, "version_b.exe")
    )
    
    if not success_b:
        print(f"ERROR: Version B compilation failed: {stderr_b}")
        return False
    
    # Find test data files
    test_files = []
    for ext in ['.input', '.txt', '.dat', '.csv']:
        test_files.extend(Path(test_data_dir).glob(f"*{ext}"))
    
    if not test_files:
        print("ERROR: No test data files found")
        return False
    
    print(f"Found {len(test_files)} test files")
    
    # Run tests
    results = []
    
    for i, test_file in enumerate(test_files, 1):
        print(f"Testing with {test_file.name} ({i}/{len(test_files)})")
        
        # Load test data
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = f.read()
        except Exception as e:
            print(f"  WARNING: Failed to load test data: {e}")
            continue
        
        # Execute both versions
        exec_a = os.path.join(output_dir, "version_a.exe")
        exec_b = os.path.join(output_dir, "version_b.exe")
        
        success_a, output_a, stderr_a = execute_program(exec_a, test_data)
        success_b, output_b, stderr_b = execute_program(exec_b, test_data)
        
        if not success_a or not success_b:
            print(f"  ERROR: Execution failed")
            continue
        
        # Compare outputs
        passed, message, differences = compare_outputs(output_a, output_b)
        
        result = {
            'test_name': f"Test_{i:03d}_{test_file.stem}",
            'test_file': str(test_file),
            'passed': passed,
            'message': message,
            'output_a': output_a,
            'output_b': output_b,
            'differences': differences
        }
        
        results.append(result)
        
        status = "PASS" if passed else "FAIL"
        print(f"  Status: {status}")
    
    # Generate report
    if results:
        report_path = os.path.join(output_dir, "regression_test_report.html")
        if generate_html_report(results, report_path):
            print(f"Report generated: {report_path}")
        else:
            print("WARNING: Report generation failed")
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/total*100:.1f}%" if total > 0 else "Success rate: N/A")
    
    return failed == 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Code Regression Tester - Simple CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simple_cli.py --version-a version1.c --version-b version2.c --test-data ./test_data
  python simple_cli.py -a old.c -b new.c -d ./data -o ./results
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
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())