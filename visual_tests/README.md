# Visual Tests for 2D Implicit Geometry Library

This directory contains organized visual tests for the geometry library, providing comprehensive testing and demonstration of all geometric functionality.

## Structure

```
visual_tests/
├── README.md                    # This file
├── run_all_tests.py            # Master test runner with GUI
├── __init__.py                 # Package initialization
├── utils/                      # Common utilities
│   ├── __init__.py
│   ├── plotting.py             # PlotManager class for consistent plotting
│   ├── test_objects.py         # Factory classes for creating test objects
│   └── grid_evaluation.py      # GridEvaluator for point testing
├── curve_tests/                # Curve-specific tests
│   ├── __init__.py
│   ├── test_basic_curves.py    # Basic conics and polynomial curves
│   └── test_composite_curves.py # Trimmed and composite curves
├── region_tests/               # Region-specific tests
│   ├── __init__.py
│   └── test_basic_regions.py   # Area regions and containment
├── comprehensive/              # Comprehensive showcases
│   ├── __init__.py
│   └── test_grid_showcase.py   # 4x4 grid comprehensive display
└── demos/                      # Demonstration scripts
    ├── __init__.py
    ├── basic_demo.py           # Basic introduction demo
    └── advanced_demo.py        # Advanced features demo
```

## Quick Start

### GUI Interface (Recommended)

Simply run the test runner without arguments to launch the GUI:

```bash
python visual_tests/run_all_tests.py
```

The GUI provides:
- ✅ Checkboxes to select which test categories to run
- 📊 Real-time output display with scrollable text area
- 📈 Progress bar and results summary
- 🎛️ Control buttons (Run, Select All, Clear All, Clear Output)

### Command Line Interface

```bash
# Run all tests
python visual_tests/run_all_tests.py --category all

# Run specific categories
python visual_tests/run_all_tests.py --category curves
python visual_tests/run_all_tests.py --category regions
python visual_tests/run_all_tests.py --category comprehensive
python visual_tests/run_all_tests.py --category demos

# Launch GUI explicitly
python visual_tests/run_all_tests.py --gui

# List available options
python visual_tests/run_all_tests.py --list
```

## Test Categories

### 1. Curve Tests
- **Basic Curves**: Circles, ellipses, hyperbolas, parabolas, lines
- **Polynomial Curves**: Cubic curves, intersecting lines, complex polynomials
- **Composite Curves**: Trimmed curves, multi-segment composites

### 2. Region Tests
- **Basic Regions**: Circle regions, triangle regions, rectangle regions
- **Containment Testing**: Point-in-region testing, boundary detection
- **Statistical Analysis**: Grid-based analysis and area estimation

### 3. Comprehensive Tests
- **Grid Showcase**: 4x4 comprehensive display of all geometry types
- **Focused Showcases**: Specialized displays for specific categories

### 4. Demonstrations
- **Basic Demo**: Introduction to curves, regions, and containment
- **Advanced Demo**: Trimmed curves, composites, and advanced analysis

## Utility Classes

### PlotManager
Provides consistent plotting functionality:
- `plot_curve_contour()` - Plot curves with contour lines
- `plot_region_filled()` - Plot filled regions with boundaries
- `plot_test_points()` - Plot point classification results
- `create_test_grid()` - Generate uniform test grids

### CurveFactory
Factory for creating standard test curves:
- `create_circle()`, `create_ellipse()`, `create_hyperbola()`, `create_parabola()`
- `create_line()`, `create_cubic_curve()`
- `create_trimmed_circle()`, `create_composite_circle_quarters()`

### RegionFactory
Factory for creating standard test regions:
- `create_circle_region()`, `create_triangle_region()`, `create_rectangle_region()`
- `get_standard_test_regions()` - Get a set of standard test regions

### GridEvaluator
Handles grid-based evaluation and analysis:
- `create_grid()` - Generate test grids
- `evaluate_curve_over_grid()` - Evaluate curves over grids
- `evaluate_region_containment()` - Test region containment
- `test_specific_points()` - Test specific points with detailed results
- `analyze_grid_statistics()` - Statistical analysis of results

## Running Individual Tests

You can also run individual test modules directly:

```bash
# Individual test modules
python visual_tests/curve_tests/test_basic_curves.py
python visual_tests/curve_tests/test_composite_curves.py
python visual_tests/region_tests/test_basic_regions.py
python visual_tests/comprehensive/test_grid_showcase.py

# Individual demos
python visual_tests/demos/basic_demo.py
python visual_tests/demos/advanced_demo.py
```

## Features

- **Modular Design**: Each test category is self-contained
- **Reusable Utilities**: Common functionality in utils package
- **Comprehensive Coverage**: Tests all geometry library features
- **Error Handling**: Graceful handling of evaluation errors
- **Statistical Analysis**: Grid-based analysis with detailed statistics
- **Visual Feedback**: Clear visual representation of results
- **GUI Interface**: User-friendly interface with real-time feedback

## Dependencies

- `numpy` - Numerical computations and arrays
- `matplotlib` - Plotting and visualization
- `sympy` - Symbolic mathematics
- `tkinter` - GUI interface (included with Python)

## Migration from Old Tests

The old visual test files in the project root have been refactored into this organized structure:

- `visual_test_program.py` → Split into multiple focused modules
- `comprehensive_viz.py` → `comprehensive/test_grid_showcase.py`
- `triangle_area_test.py` → Incorporated into `region_tests/test_basic_regions.py`
- `test_plot_demo.py` → Incorporated into `curve_tests/test_basic_curves.py`

The new structure provides better organization, reusability, and maintainability while preserving all original functionality.
