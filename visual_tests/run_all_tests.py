"""
Master test runner for all visual tests.

Provides both GUI and command-line interfaces for running visual tests.
The GUI includes checkboxes for test selection and displays results.
"""

import sys
import os
import argparse
# Make tkinter optional so CLI can run in headless environments
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False
import threading
import io
from contextlib import redirect_stdout, redirect_stderr

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class TestRunner:
    """Handles running individual test categories."""
    
    @staticmethod
    def run_curve_tests():
        """Run all curve tests."""
        print("\n" + "="*80)
        print("RUNNING CURVE TESTS")
        print("="*80)
        
        try:
            from visual_tests.curve_tests.test_basic_curves import run_all_basic_curve_tests
            from visual_tests.curve_tests.test_composite_curves import run_all_composite_curve_tests
            
            run_all_basic_curve_tests()
            print()
            run_all_composite_curve_tests()
            
            print("\n✓ ALL CURVE TESTS COMPLETED")
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR in curve tests: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def run_region_tests():
        """Run all region tests."""
        print("\n" + "="*80)
        print("RUNNING REGION TESTS")
        print("="*80)
        
        try:
            from visual_tests.region_tests.test_basic_regions import run_all_basic_region_tests
            
            run_all_basic_region_tests()
            
            print("\n✓ ALL REGION TESTS COMPLETED")
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR in region tests: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def run_comprehensive_tests():
        """Run comprehensive showcase tests."""
        print("\n" + "="*80)
        print("RUNNING COMPREHENSIVE TESTS")
        print("="*80)
        
        try:
            from visual_tests.comprehensive.test_grid_showcase import run_all_comprehensive_tests
            
            run_all_comprehensive_tests()
            
            print("\n✓ ALL COMPREHENSIVE TESTS COMPLETED")
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR in comprehensive tests: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def run_demos():
        """Run demonstration scripts."""
        print("\n" + "="*80)
        print("RUNNING DEMONSTRATIONS")
        print("="*80)
        
        try:
            from visual_tests.demos.basic_demo import run_basic_demo
            from visual_tests.demos.advanced_demo import run_advanced_demo
            
            run_basic_demo()
            print()
            run_advanced_demo()
            
            print("\n✓ ALL DEMONSTRATIONS COMPLETED")
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR in demonstrations: {e}")
            import traceback
            traceback.print_exc()
            return False


class VisualTestGUI:
    """GUI for running visual tests with checkboxes and results display."""
    
    def __init__(self, root):
        if not TK_AVAILABLE:
            raise RuntimeError("Tkinter is not available; cannot launch GUI.")
        self.root = root
        self.root.title("Visual Tests - 2D Implicit Geometry Library")
        self.root.geometry("800x700")
        
        # Test categories and their functions
        self.test_categories = {
            "Curve Tests": {
                "function": TestRunner.run_curve_tests,
                "description": "Basic and composite curve tests",
                "var": tk.BooleanVar(value=True)
            },
            "Region Tests": {
                "function": TestRunner.run_region_tests,
                "description": "Area region tests and containment",
                "var": tk.BooleanVar(value=True)
            },
            "Comprehensive Tests": {
                "function": TestRunner.run_comprehensive_tests,
                "description": "Grid showcase and comprehensive visualizations",
                "var": tk.BooleanVar(value=True)
            },
            "Demonstrations": {
                "function": TestRunner.run_demos,
                "description": "Basic and advanced demonstrations",
                "var": tk.BooleanVar(value=True)
            }
        }
        
        self.test_results = {}
        self.running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Visual Tests for 2D Implicit Geometry Library", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Test selection frame
        selection_frame = ttk.LabelFrame(main_frame, text="Select Test Categories", padding="10")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Checkboxes for test categories
        row = 0
        for category, info in self.test_categories.items():
            checkbox = ttk.Checkbutton(selection_frame, text=category, variable=info["var"])
            checkbox.grid(row=row, column=0, sticky=tk.W, pady=2)
            
            desc_label = ttk.Label(selection_frame, text=info["description"], 
                                  foreground="gray", font=('Arial', 9))
            desc_label.grid(row=row, column=1, sticky=tk.W, padx=(20, 0), pady=2)
            
            row += 1
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Buttons
        self.run_button = ttk.Button(button_frame, text="Run Selected Tests", 
                                    command=self.run_selected_tests)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_all_button = ttk.Button(button_frame, text="Select All", 
                                           command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_all_button = ttk.Button(button_frame, text="Clear All", 
                                          command=self.clear_all)
        self.clear_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_output_button = ttk.Button(button_frame, text="Clear Output", 
                                             command=self.clear_output)
        self.clear_output_button.pack(side=tk.LEFT)
        
        # Results and output frame
        results_frame = ttk.LabelFrame(main_frame, text="Test Output and Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results summary
        self.results_label = ttk.Label(results_frame, text="No tests run yet", 
                                      font=('Arial', 10, 'bold'))
        self.results_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def select_all(self):
        """Select all test categories."""
        for info in self.test_categories.values():
            info["var"].set(True)
    
    def clear_all(self):
        """Clear all test category selections."""
        for info in self.test_categories.values():
            info["var"].set(False)
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
        self.results_label.config(text="Output cleared")
    
    def update_output(self, text):
        """Update the output text area."""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_selected_tests(self):
        """Run the selected tests in a separate thread."""
        if self.running:
            messagebox.showwarning("Tests Running", "Tests are already running. Please wait for completion.")
            return
        
        # Check if any tests are selected
        selected_tests = [(category, info) for category, info in self.test_categories.items() 
                         if info["var"].get()]
        
        if not selected_tests:
            messagebox.showwarning("No Tests Selected", "Please select at least one test category to run.")
            return
        
        # Start tests in a separate thread
        self.running = True
        self.run_button.config(state='disabled')
        self.progress.start()
        self.results_label.config(text="Running tests...")
        
        thread = threading.Thread(target=self.run_tests_thread, args=(selected_tests,))
        thread.daemon = True
        thread.start()
    
    def run_tests_thread(self, selected_tests):
        """Run tests in a separate thread to avoid blocking the GUI."""
        try:
            # Capture output
            output_buffer = io.StringIO()
            
            self.test_results = {}
            
            with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
                self.root.after(0, lambda: self.update_output(f"Running {len(selected_tests)} test categories...\n\n"))
                
                for category, info in selected_tests:
                    self.root.after(0, lambda c=category: self.update_output(f"Starting {c}...\n"))
                    
                    try:
                        result = info["function"]()
                        self.test_results[category] = result
                        
                        status = "✓ PASSED" if result else "✗ FAILED"
                        self.root.after(0, lambda c=category, s=status: 
                                      self.update_output(f"{c}: {s}\n\n"))
                        
                    except Exception as e:
                        self.test_results[category] = False
                        self.root.after(0, lambda c=category, e=str(e): 
                                      self.update_output(f"{c}: ✗ FAILED - {e}\n\n"))
            
            # Get captured output
            captured_output = output_buffer.getvalue()
            if captured_output:
                self.root.after(0, lambda: self.update_output(captured_output))
            
            # Update results summary
            self.root.after(0, self.update_results_summary)
            
        except Exception as e:
            self.root.after(0, lambda: self.update_output(f"\nUnexpected error: {e}\n"))
        
        finally:
            # Re-enable UI
            self.root.after(0, self.finish_tests)
    
    def update_results_summary(self):
        """Update the results summary label."""
        if not self.test_results:
            self.results_label.config(text="No test results available")
            return
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        if failed_tests == 0:
            summary = f"🎉 All {total_tests} test categories PASSED!"
            color = "green"
        else:
            summary = f"⚠️ {passed_tests}/{total_tests} test categories passed, {failed_tests} failed"
            color = "red"
        
        self.results_label.config(text=summary, foreground=color)
        
        # Add detailed results
        details = "\n\nDetailed Results:\n" + "="*50 + "\n"
        for category, result in self.test_results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            details += f"{category:<25}: {status}\n"
        
        self.update_output(details)
    
    def finish_tests(self):
        """Clean up after tests complete."""
        self.running = False
        self.run_button.config(state='normal')
        self.progress.stop()


def run_gui():
    """Run the GUI version of the test runner."""
    if not TK_AVAILABLE:
        print("Tkinter is not available; falling back to command-line runner.")
        return run_command_line()
    root = tk.Tk()
    app = VisualTestGUI(root)
    root.mainloop()


def run_command_line():
    """Run the command line version of the test runner."""
    parser = argparse.ArgumentParser(description='Run visual tests for the geometry library')
    parser.add_argument('--category', choices=['curves', 'regions', 'comprehensive', 'demos', 'all'],
                       default='all', help='Test category to run (default: all)')
    parser.add_argument('--list', action='store_true', help='List available test categories')
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    
    args = parser.parse_args()
    
    if args.gui:
        return run_gui() or 0
    
    if args.list:
        print("Available test categories:")
        print("  curves        - Basic and composite curve tests")
        print("  regions       - Area region tests")
        print("  comprehensive - Grid showcase and comprehensive visualizations")
        print("  demos         - Basic and advanced demonstrations")
        print("  all           - Run all test categories (default)")
        print("  --gui         - Launch GUI interface")
        return 0
    
    print("Visual Tests for 2D Implicit Geometry Library")
    print("=" * 50)
    
    if args.category == 'curves':
        success = TestRunner.run_curve_tests()
    elif args.category == 'regions':
        success = TestRunner.run_region_tests()
    elif args.category == 'comprehensive':
        success = TestRunner.run_comprehensive_tests()
    elif args.category == 'demos':
        success = TestRunner.run_demos()
    elif args.category == 'all':
        success = run_all_tests()
    else:
        print(f"Unknown category: {args.category}")
        return 1
    
    return 0 if success else 1


def run_all_tests():
    """Run all visual tests (command line version)."""
    print("\n" + "="*100)
    print("RUNNING ALL VISUAL TESTS")
    print("="*100)
    print("This will run all curve tests, region tests, comprehensive showcases, and demos.")
    print()
    
    results = []
    
    # Run each test category
    results.append(("Curve Tests", TestRunner.run_curve_tests()))
    results.append(("Region Tests", TestRunner.run_region_tests()))
    results.append(("Comprehensive Tests", TestRunner.run_comprehensive_tests()))
    results.append(("Demonstrations", TestRunner.run_demos()))
    
    # Print summary
    print("\n" + "="*100)
    print("VISUAL TESTS SUMMARY")
    print("="*100)
    
    all_passed = True
    for category, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{category:<20}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*100)
    if all_passed:
        print("🎉 ALL VISUAL TESTS COMPLETED SUCCESSFULLY!")
        print("The geometry library visual testing suite is working correctly.")
    else:
        print("⚠️  SOME VISUAL TESTS FAILED")
        print("Please check the error messages above for details.")
    print("="*100)
    
    return all_passed


if __name__ == "__main__":
    # If no arguments provided, try GUI; if unavailable, fallback to CLI
    if len(sys.argv) == 1:
        result = run_gui()
        if isinstance(result, int):
            sys.exit(result)
    else:
        exit_code = run_command_line()
        sys.exit(exit_code)
