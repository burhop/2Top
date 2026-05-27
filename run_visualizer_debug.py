#!/usr/bin/env python3
"""
Run the clean curve visualizer with debug output
"""

import sys
import traceback


def run_visualizer_with_debug():
    """Run the visualizer with comprehensive error catching"""
    print("🔍 Running Clean Curve Visualizer with Debug")

    try:
        # Import and run the visualizer
        from clean_curve_visualizer import main

        print("✅ Successfully imported clean_curve_visualizer")

        print("🚀 Starting visualizer...")
        main()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        traceback.print_exc()


def test_visualizer_imports():
    """Test all the imports used by the visualizer"""
    print("🔍 Testing Visualizer Imports")

    imports_to_test = [
        "tkinter",
        "matplotlib.pyplot",
        "matplotlib.backends.backend_tkagg",
        "numpy",
        "sympy",
        "geometry",
        "geometry.curve_intersections",
    ]

    for import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✅ {import_name}: OK")
        except Exception as e:
            print(f"❌ {import_name}: {e}")


def test_visualizer_class_creation():
    """Test creating the visualizer class without running the GUI"""
    print("\n🔍 Testing Visualizer Class Creation")

    try:
        import tkinter as tk
        from clean_curve_visualizer import CleanCurveVisualizerApp

        # Create root but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window

        print("✅ Tkinter root created")

        # Try to create the app
        app = CleanCurveVisualizerApp(root)
        print("✅ CleanCurveVisualizerApp created successfully")

        # Test adding a square
        print("🔍 Testing square addition...")
        app.add_square()
        print("✅ Square addition completed")

        # Check what curves were added
        print(f"Curves in app: {len(app.curves)}")
        for i, (name, curve) in enumerate(app.curves):
            print(f"  {i}: {name} ({type(curve).__name__})")

        root.destroy()

    except Exception as e:
        print(f"❌ Visualizer class creation failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 CLEAN CURVE VISUALIZER DEBUG")
    print("=" * 50)

    test_visualizer_imports()
    test_visualizer_class_creation()

    # Only run the full visualizer if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        run_visualizer_with_debug()
