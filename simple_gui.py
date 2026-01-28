#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple GUI Test Tool - Working Version
A simplified but functional GUI for Code Regression Tester
"""

import sys
import os
import tempfile
import threading
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QGroupBox, QFileDialog, QStatusBar, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestWorkerThread(QThread):
    """Worker thread for running tests"""
    progress_updated = pyqtSignal(int, str)
    test_completed = pyqtSignal(str, bool, str)
    all_tests_finished = pyqtSignal(int, int)  # total, passed
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.should_stop = False
    
    def run(self):
        """Run the test process"""
        try:
            # Import here to avoid Qt import issues
            import subprocess
            
            # Compile versions
            self.progress_updated.emit(10, "Compiling version A...")
            
            success_a, stdout_a, stderr_a = self.compile_c_code(
                self.config['version_a_source'],
                self.config['version_a_output']
            )
            
            if not success_a:
                self.test_completed.emit("Compilation A", False, stderr_a)
                return
            
            self.progress_updated.emit(20, "Compiling version B...")
            
            success_b, stdout_b, stderr_b = self.compile_c_code(
                self.config['version_b_source'],
                self.config['version_b_output']
            )
            
            if not success_b:
                self.test_completed.emit("Compilation B", False, stderr_b)
                return
            
            # Find test files
            test_files = []
            test_data_dir = self.config['test_data_dir']
            for ext in ['.input', '.txt', '.dat', '.csv']:
                test_files.extend(Path(test_data_dir).glob(f"*{ext}"))
            
            if not test_files:
                self.test_completed.emit("Test Data", False, "No test data files found")
                return
            
            total_tests = len(test_files)
            passed_tests = 0
            
            for i, test_file in enumerate(test_files):
                if self.should_stop:
                    break
                
                progress = 30 + int((i / total_tests) * 60)
                self.progress_updated.emit(progress, f"Testing {test_file.name} ({i+1}/{total_tests})")
                
                # Load test data
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        test_data = f.read()
                except Exception as e:
                    self.test_completed.emit(test_file.name, False, f"Failed to load data: {e}")
                    continue
                
                # Execute both versions
                success_a, output_a, stderr_a = self.execute_program(
                    self.config['version_a_output'], test_data
                )
                success_b, output_b, stderr_b = self.execute_program(
                    self.config['version_b_output'], test_data
                )
                
                if not success_a or not success_b:
                    self.test_completed.emit(test_file.name, False, "Execution failed")
                    continue
                
                # Compare outputs
                passed = output_a == output_b
                if passed:
                    passed_tests += 1
                
                message = "PASS" if passed else f"FAIL - Outputs differ"
                self.test_completed.emit(test_file.name, passed, message)
            
            self.all_tests_finished.emit(total_tests, passed_tests)
            
        except Exception as e:
            self.test_completed.emit("System", False, f"Error: {e}")
    
    def compile_c_code(self, source_file, output_file):
        """Compile C code"""
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
    
    def execute_program(self, executable, input_data):
        """Execute program"""
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
    
    def stop(self):
        """Stop the test"""
        self.should_stop = True

class SimpleMainWindow(QMainWindow):
    """Simple main window for the GUI"""
    
    def __init__(self):
        super().__init__()
        self.test_worker = None
        self.test_results = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Code Regression Tester - Simple GUI")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Configuration group
        config_group = self.create_config_group()
        main_layout.addWidget(config_group)
        
        # Control group
        control_group = self.create_control_group()
        main_layout.addWidget(control_group)
        
        # Results area
        results_splitter = QSplitter(Qt.Horizontal)
        
        # Test results list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Test Results:"))
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumWidth(300)
        left_layout.addWidget(self.results_text)
        
        # Detailed output
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Detailed Output:"))
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        right_layout.addWidget(self.detail_text)
        
        results_splitter.addWidget(left_widget)
        results_splitter.addWidget(right_widget)
        results_splitter.setSizes([300, 700])
        
        main_layout.addWidget(results_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_config_group(self):
        """Create configuration group"""
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Version A
        a_layout = QHBoxLayout()
        a_layout.addWidget(QLabel("Version A:"))
        self.version_a_edit = QLineEdit()
        a_layout.addWidget(self.version_a_edit)
        self.browse_a_btn = QPushButton("Browse")
        self.browse_a_btn.clicked.connect(lambda: self.browse_file(self.version_a_edit, "C Files (*.c)"))
        a_layout.addWidget(self.browse_a_btn)
        config_layout.addLayout(a_layout)
        
        # Version B
        b_layout = QHBoxLayout()
        b_layout.addWidget(QLabel("Version B:"))
        self.version_b_edit = QLineEdit()
        b_layout.addWidget(self.version_b_edit)
        self.browse_b_btn = QPushButton("Browse")
        self.browse_b_btn.clicked.connect(lambda: self.browse_file(self.version_b_edit, "C Files (*.c)"))
        b_layout.addWidget(self.browse_b_btn)
        config_layout.addLayout(b_layout)
        
        # Test data
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("Test Data:"))
        self.test_data_edit = QLineEdit()
        data_layout.addWidget(self.test_data_edit)
        self.browse_data_btn = QPushButton("Browse")
        self.browse_data_btn.clicked.connect(lambda: self.browse_directory(self.test_data_edit))
        data_layout.addWidget(self.browse_data_btn)
        config_layout.addLayout(data_layout)
        
        return config_group
    
    def create_control_group(self):
        """Create control group"""
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout(control_group)
        
        # Buttons
        self.start_btn = QPushButton("Start Test")
        self.start_btn.clicked.connect(self.start_test)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setEnabled(False)
        
        self.report_btn = QPushButton("Generate Report")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.report_btn)
        control_layout.addWidget(self.progress_bar)
        control_layout.addStretch()
        
        return control_group
    
    def browse_file(self, line_edit, file_filter):
        """Browse for file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file_path:
            line_edit.setText(file_path)
    
    def browse_directory(self, line_edit):
        """Browse for directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            line_edit.setText(dir_path)
    
    def start_test(self):
        """Start the test"""
        # Validate configuration
        if not self.version_a_edit.text():
            QMessageBox.warning(self, "Warning", "Please select version A C file")
            return
        if not self.version_b_edit.text():
            QMessageBox.warning(self, "Warning", "Please select version B C file")
            return
        if not self.test_data_edit.text():
            QMessageBox.warning(self, "Warning", "Please select test data directory")
            return
        
        # Get configuration
        import tempfile
        config = {
            'version_a_source': self.version_a_edit.text(),
            'version_b_source': self.version_b_edit.text(),
            'test_data_dir': self.test_data_edit.text(),
            'version_a_output': os.path.join(tempfile.gettempdir(), "version_a.exe"),
            'version_b_output': os.path.join(tempfile.gettempdir(), "version_b.exe")
        }
        
        # Clear previous results
        self.results_text.clear()
        self.detail_text.clear()
        self.test_results.clear()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.report_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.test_worker = TestWorkerThread(config)
        self.test_worker.progress_updated.connect(self.on_progress_updated)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.all_tests_finished.connect(self.on_all_tests_finished)
        self.test_worker.start()
        
        self.status_bar.showMessage("Test running...")
    
    def stop_test(self):
        """Stop the test"""
        if self.test_worker:
            self.test_worker.stop()
        self.status_bar.showMessage("Stopping test...")
    
    def generate_report(self):
        """Generate HTML report"""
        if not self.test_results:
            QMessageBox.information(self, "Info", "No test results to report")
            return
        
        # Simple HTML report
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        pre { background: #f0f0f0; padding: 10px; }
    </style>
</head>
<body>
    <h1>Code Regression Test Report</h1>
"""
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        
        html_content += f"""
    <h2>Summary</h2>
    <p>Total: {total}, Passed: {passed}, Failed: {total - passed}</p>
    <h2>Details</h2>
"""
        
        for result in self.test_results:
            status_class = "pass" if result['passed'] else "fail"
            html_content += f"""
    <div class="{status_class}">
        <h3>{result['name']} - {'PASS' if result['passed'] else 'FAIL'}</h3>
        <p>{result['message']}</p>
        <pre>{result['details']}</pre>
    </div>
"""
        
        html_content += "</body></html>"
        
        # Save report
        report_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "test_report.html", "HTML Files (*.html)"
        )
        
        if report_path:
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                QMessageBox.information(self, "Success", f"Report saved to {report_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {e}")
    
    def on_progress_updated(self, value, message):
        """Handle progress update"""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)
    
    def on_test_completed(self, test_name, passed, message):
        """Handle test completion"""
        status = "PASS" if passed else "FAIL"
        self.results_text.append(f"{test_name}: {status}")
        
        # Store result
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'details': f"Status: {status}\nMessage: {message}"
        })
        
        # Update detail view
        self.detail_text.append(f"=== {test_name} ===")
        self.detail_text.append(f"Status: {status}")
        self.detail_text.append(f"Message: {message}")
        self.detail_text.append("")
    
    def on_all_tests_finished(self, total, passed):
        """Handle all tests finished"""
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.report_btn.setEnabled(True)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        self.status_bar.showMessage(f"Completed: {passed}/{total} ({success_rate:.1f}%)")
        
        QMessageBox.information(
            self, 
            "Test Complete", 
            f"Tests completed!\nTotal: {total}\nPassed: {passed}\nFailed: {total - passed}\nSuccess Rate: {success_rate:.1f}%"
        )

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = SimpleMainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())