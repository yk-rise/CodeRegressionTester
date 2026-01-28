#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Launcher for Code Regression Tester
Choose between GUI and CLI modes
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher"""
    print("🚀 Code Regression Tester - Quick Launcher")
    print("=" * 50)
    print("1. GUI Mode (Recommended for beginners)")
    print("2. CLI Mode (Advanced users)")
    print("3. Exit")
    print("=" * 50)
    
    while True:
        try:
            choice = input("Please choose mode (1-3): ").strip()
            
            if choice == "1":
                print("\n🖥️  Starting GUI Mode...")
                print("   - Browse for C files")
                print("   - Select test data directory")
                print("   - Click 'Start Test'")
                print("   - View results and generate reports")
                print("\n")
                
                # Import and start GUI
                try:
                    from PyQt5.QtWidgets import QApplication
                    from simple_gui import main as gui_main
                    
                    app = QApplication(sys.argv)
                    app.setStyle('Fusion')
                    
                    window = gui_main()
                    sys.exit(app.exec_())
                    
                except ImportError:
                    print("❌ PyQt5 not found. Please install with: pip install PyQt5")
                    return 1
                except Exception as e:
                    print(f"❌ GUI error: {e}")
                    print("   Falling back to CLI mode...")
                    return run_cli()
            
            elif choice == "2":
                print("\n💻 Starting CLI Mode...")
                return run_cli()
            
            elif choice == "3":
                print("👋 Goodbye!")
                return 0
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 0
        except EOFError:
            print("\n👋 Goodbye!")
            return 0

def run_cli():
    """Run CLI mode with examples"""
    print("\n📋 CLI Usage Examples:")
    print("   python simple_cli.py --help")
    print("   python simple_cli.py -a examples/sort_version_a.c -b examples/sort_version_b.c -d examples/test_data/array_test_data")
    print("\n🔧 Quick test with example files:")
    
    # Check if example files exist
    project_root = Path(__file__).parent
    version_a = project_root / "examples" / "sort_version_a.c"
    version_b = project_root / "examples" / "sort_version_b.c"
    test_data = project_root / "examples" / "test_data" / "array_test_data"
    
    if version_a.exists() and version_b.exists() and test_data.exists():
        print("   Running example test...")
        print("   python simple_cli.py -a examples/sort_version_a.c -b examples/sort_version_b.c -d examples/test_data/array_test_data")
        print("\n")
        
        # Run the CLI
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "simple_cli.py",
                "-a", str(version_a),
                "-b", str(version_b), 
                "-d", str(test_data),
                "-o", "gui_results"
            ], cwd=project_root)
            return result.returncode
        except Exception as e:
            print(f"❌ CLI error: {e}")
            return 1
    else:
        print("   Example files not found. Please check the examples/ directory.")
        print("   Use --help to see all options.")
        return 1

if __name__ == "__main__":
    sys.exit(main())