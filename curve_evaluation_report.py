#!/usr/bin/env python3
"""
Comprehensive evaluation report for all implicit curve types
"""

import sympy as sp
import numpy as np
from geometry import *
import time

def comprehensive_evaluation_report():
    """Generate a comprehensive report on curve evaluator correctness"""
    
    x, y = sp.symbols('x y')
    
    print("📋 COMPREHENSIVE CURVE EVALUATION REPORT")
    print("=" * 60)
    
    # Test results storage
    results = {
        'ConicSection': {'passed': 0, 'total': 0, 'issues': []},
        'PolynomialCurve': {'passed': 0, 'total': 0, 'issues': []},
        'Superellipse': {'passed': 0, 'total': 0, 'issues': []},
        'ProceduralCurve': {'passed': 0, 'total': 0, 'issues': []},
        'RFunctionCurve': {'passed': 0, 'total': 0, 'issues': []},
        'CompositeCurve': {'passed': 0, 'total': 0, 'issues': []},
        'AreaRegion': {'passed': 0, 'total': 0, 'issues': []},
    }
    
    def test_curve(curve_type, curve, test_name, test_func):
        """Helper to run a test and record results"""
        try:
            passed = test_func()
            results[curve_type]['total'] += 1
            if passed:
                results[curve_type]['passed'] += 1
                print(f"  ✅ {test_name}")
            else:
                results[curve_type]['issues'].append(test_name)
                print(f"  ❌ {test_name}")
            return passed
        except Exception as e:
            results[curve_type]['total'] += 1
            results[curve_type]['issues'].append(f"{test_name}: {str(e)}")
            print(f"  💥 {test_name}: {str(e)}")
            return False
    
    # 1. ConicSection Tests
    print("\n1. 🔵 ConicSection Evaluation:")
    
    # Circle tests
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    test_curve('ConicSection', circle, 'Circle basic evaluation', 
               lambda: abs(circle.evaluate(0, 0) + 1) < 1e-10)
    test_curve('ConicSection', circle, 'Circle boundary evaluation', 
               lambda: abs(circle.evaluate(1, 0)) < 1e-10)
    test_curve('ConicSection', circle, 'Circle gradient', 
               lambda: abs(circle.gradient(1, 0)[0] - 2) < 1e-10)
    
    # Ellipse tests
    ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
    test_curve('ConicSection', ellipse, 'Ellipse evaluation', 
               lambda: abs(ellipse.evaluate(2, 0)) < 1e-10)
    
    # Parabola tests
    parabola = ConicSection(y - x**2, (x, y))
    test_curve('ConicSection', parabola, 'Parabola evaluation', 
               lambda: abs(parabola.evaluate(2, 4)) < 1e-10)
    
    # Hyperbola tests
    hyperbola = ConicSection(x**2 - y**2 - 1, (x, y))
    test_curve('ConicSection', hyperbola, 'Hyperbola evaluation', 
               lambda: abs(hyperbola.evaluate(1, 0) + 1) < 1e-10)
    
    # 2. PolynomialCurve Tests
    print("\n2. 📐 PolynomialCurve Evaluation:")
    
    # Linear
    line = PolynomialCurve(x + y - 1, (x, y))
    test_curve('PolynomialCurve', line, 'Linear evaluation', 
               lambda: abs(line.evaluate(0.5, 0.5)) < 1e-10)
    test_curve('PolynomialCurve', line, 'Linear gradient', 
               lambda: abs(line.gradient(0, 0)[0] - 1) < 1e-10)
    
    # Quadratic
    quad = PolynomialCurve(x**2 + y**2 - 1, (x, y))
    test_curve('PolynomialCurve', quad, 'Quadratic evaluation', 
               lambda: abs(quad.evaluate(1, 0)) < 1e-10)
    
    # Cubic
    cubic = PolynomialCurve(x**3 + y**3 - 1, (x, y))
    test_curve('PolynomialCurve', cubic, 'Cubic evaluation', 
               lambda: abs(cubic.evaluate(1, 0)) < 1e-10)
    
    # High degree
    high_deg = PolynomialCurve(x**6 + y**6 - 1, (x, y))
    test_curve('PolynomialCurve', high_deg, 'High degree evaluation', 
               lambda: abs(high_deg.evaluate(1, 0)) < 1e-10)
    
    # 3. Superellipse Tests
    print("\n3. ⭐ Superellipse Evaluation:")
    
    # Circle-like (n=2)
    super_circle = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
    test_curve('Superellipse', super_circle, 'Circle-like (n=2)', 
               lambda: abs(super_circle.evaluate(1, 0)) < 1e-10)
    
    # Square-like (n=4)
    super_square = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
    test_curve('Superellipse', super_square, 'Square-like (n=4)', 
               lambda: abs(super_square.evaluate(1, 0)) < 1e-10)
    
    # Diamond-like (n=0.5)
    super_diamond = Superellipse(a=1.0, b=1.0, n=0.5, variables=(x, y))
    test_curve('Superellipse', super_diamond, 'Diamond-like (n=0.5)', 
               lambda: abs(super_diamond.evaluate(1, 0)) < 1e-10)
    
    # Extreme aspect ratio
    super_stretched = Superellipse(a=10.0, b=0.1, n=2.0, variables=(x, y))
    test_curve('Superellipse', super_stretched, 'Extreme aspect ratio', 
               lambda: abs(super_stretched.evaluate(10, 0)) < 1e-10)
    
    # 4. ProceduralCurve Tests
    print("\n4. 🔧 ProceduralCurve Evaluation:")
    
    # Simple function
    def simple_func(x_val, y_val):
        return x_val**2 + y_val**2 - 1
    
    proc_simple = ProceduralCurve(simple_func, variables=(x, y))
    test_curve('ProceduralCurve', proc_simple, 'Simple function', 
               lambda: abs(proc_simple.evaluate(1, 0)) < 1e-10)
    
    # Complex function
    def complex_func(x_val, y_val):
        return np.sin(x_val) + np.cos(y_val) - 1
    
    proc_complex = ProceduralCurve(complex_func, variables=(x, y))
    test_curve('ProceduralCurve', proc_complex, 'Complex function', 
               lambda: abs(proc_complex.evaluate(np.pi/2, 0) - 1) < 1e-10)
    
    # Vectorized function
    test_curve('ProceduralCurve', proc_simple, 'Vectorized evaluation', 
               lambda: len(proc_simple.evaluate(np.array([0, 1]), np.array([0, 0]))) == 2)
    
    # 5. RFunctionCurve Tests (Constructive Geometry)
    print("\n5. 🔗 RFunctionCurve Evaluation:")
    
    c1 = ConicSection(x**2 + y**2 - 1, (x, y))
    c2 = ConicSection((x-1)**2 + y**2 - 1, (x, y))
    
    # Union
    union_curve = union(c1, c2)
    test_curve('RFunctionCurve', union_curve, 'Union evaluation', 
               lambda: union_curve.evaluate(0, 0) < 0)  # Should be inside
    
    # Intersection
    intersect_curve = intersect(c1, c2)
    test_curve('RFunctionCurve', intersect_curve, 'Intersection evaluation', 
               lambda: intersect_curve.evaluate(0.5, 0) < 0)  # Should be in overlap
    
    # Difference
    diff_curve = difference(c1, c2)
    test_curve('RFunctionCurve', diff_curve, 'Difference evaluation', 
               lambda: diff_curve.evaluate(-0.5, 0) < 0)  # Should be in c1 but not c2
    
    # Blend
    blend_curve = blend(c1, c2, alpha=0.5)
    test_curve('RFunctionCurve', blend_curve, 'Blend evaluation', 
               lambda: blend_curve.evaluate(0, 0) < 0)  # Should be inside
    
    # 6. CompositeCurve Tests
    print("\n6. 🔗 CompositeCurve Evaluation:")
    
    # Square
    square = create_square_from_edges((-1, -1), (1, 1))
    test_curve('CompositeCurve', square, 'Square creation', 
               lambda: square.is_closed())
    test_curve('CompositeCurve', square, 'Square corner evaluation', 
               lambda: abs(square.evaluate(1, 1)) < 1e-6)
    test_curve('CompositeCurve', square, 'Square inside evaluation', 
               lambda: square.evaluate(0, 0) < 0)
    
    # Circle from quarters
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.0)
    test_curve('CompositeCurve', circle_quarters, 'Circle quarters creation', 
               lambda: circle_quarters.is_closed())
    test_curve('CompositeCurve', circle_quarters, 'Circle quarters evaluation', 
               lambda: abs(circle_quarters.evaluate(1, 0)) < 0.1)  # Looser tolerance for composite
    
    # 7. AreaRegion Tests
    print("\n7. 🏠 AreaRegion Evaluation:")
    
    region = AreaRegion(square)
    test_curve('AreaRegion', region, 'Region containment (inside)', 
               lambda: region.contains(0, 0))
    test_curve('AreaRegion', region, 'Region containment (outside)', 
               lambda: not region.contains(2, 2))
    test_curve('AreaRegion', region, 'Region boundary detection', 
               lambda: region.contains_boundary(1, 0))
    
    # Region with hole
    outer_square = create_square_from_edges((-2, -2), (2, 2))
    inner_square = create_square_from_edges((-0.5, -0.5), (0.5, 0.5))
    region_with_hole = AreaRegion(outer_square, holes=[inner_square])
    
    test_curve('AreaRegion', region_with_hole, 'Region with hole (outside hole)', 
               lambda: region_with_hole.contains(1, 1))
    test_curve('AreaRegion', region_with_hole, 'Region with hole (inside hole)', 
               lambda: not region_with_hole.contains(0, 0))
    
    # 8. Performance Tests
    print("\n8. ⚡ Performance Tests:")
    
    # Large array performance
    large_x = np.random.uniform(-2, 2, 10000)
    large_y = np.random.uniform(-2, 2, 10000)
    
    start_time = time.time()
    large_results = circle.evaluate(large_x, large_y)
    perf_time = time.time() - start_time
    
    perf_ok = perf_time < 1.0  # Should complete in under 1 second
    test_curve('ConicSection', circle, f'Large array performance ({perf_time:.3f}s)', 
               lambda: perf_ok)
    
    # 9. Generate Summary Report
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY REPORT")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    for curve_type, data in results.items():
        passed = data['passed']
        total = data['total']
        total_passed += passed
        total_tests += total
        
        if total > 0:
            percentage = (passed / total) * 100
            status = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            print(f"{status} {curve_type:15} {passed:2d}/{total:2d} ({percentage:5.1f}%)")
            
            if data['issues']:
                for issue in data['issues']:
                    print(f"    ❌ {issue}")
    
    overall_percentage = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")
    
    # 10. Recommendations
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS FOR CORRECTNESS")
    print("=" * 60)
    
    recommendations = []
    
    if overall_percentage < 100:
        recommendations.append("🔍 Investigate failing tests to identify root causes")
    
    if results['Superellipse']['passed'] < results['Superellipse']['total']:
        recommendations.append("⭐ Review Superellipse implementation for edge cases (extreme n values)")
    
    if results['CompositeCurve']['passed'] < results['CompositeCurve']['total']:
        recommendations.append("🔗 Check CompositeCurve evaluation method for numerical precision")
    
    if results['RFunctionCurve']['passed'] < results['RFunctionCurve']['total']:
        recommendations.append("🔗 Verify R-function implementations match mathematical definitions")
    
    # Always good practices
    recommendations.extend([
        "📊 Add visual plotting tests to verify curve shapes",
        "🧪 Test with extreme parameter values (very large/small numbers)",
        "🎯 Implement tolerance-based equality checks for boundary conditions",
        "⚡ Profile performance with large datasets",
        "🔄 Add property-based testing for mathematical invariants",
        "📝 Document expected behavior for edge cases (NaN, infinity)",
    ])
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i:2d}. {rec}")
    
    print(f"\n🎉 Evaluation complete! Overall system health: {overall_percentage:.1f}%")
    
    return results

if __name__ == "__main__":
    comprehensive_evaluation_report()