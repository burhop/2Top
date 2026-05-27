import sympy as sp
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve


def test_trimmed_circle_closedness():
    # 1. Create a circle centered at (-80, 0) with radius 10
    # Equation: (x + 80)^2 + y^2 - 100 = 0 -> x^2 + 160x + 6400 + y^2 - 100 = 0
    x, y = sp.symbols("x y")
    expr = x**2 + y**2 + 160 * x + 6300
    circle = ConicSection(expr)

    # 2. Trimmed circle with clipping mask (should be open)
    # The circle extends from x = -90 to x = -70.
    # Mask x >= -80 clips the left half of the circle, making it open.
    mask_open = lambda x_val, y_val: x_val >= -80.0
    trimmed_open = TrimmedImplicitCurve(circle, mask_open)
    curve_open = CompositeCurve([trimmed_open])

    # Under the old unit circle test:
    # np.cos(angle) is between -1 and 1. So x_test >= -80 is always True.
    # It would incorrectly return True (closed).
    # With the new fix, it evaluates around the true perimeter where x_test goes down to -90.
    assert not curve_open.is_closed()

    # 3. Trimmed circle with non-clipping mask (should be closed)
    # Mask x >= -100 allows the entire circle.
    mask_closed = lambda x_val, y_val: x_val >= -100.0
    trimmed_closed = TrimmedImplicitCurve(circle, mask_closed)
    curve_closed = CompositeCurve([trimmed_closed])

    assert curve_closed.is_closed()


def test_trimmed_ellipse_closedness():
    # 1. Create an ellipse centered at (0, 50) with semi-axes a = 5, b = 8
    # Equation: x^2 / 25 + (y - 50)^2 / 64 - 1 = 0 -> 64*x^2 + 25*(y - 50)^2 - 1600 = 0
    x, y = sp.symbols("x y")
    expr = 64 * x**2 + 25 * (y - 50) ** 2 - 1600
    ellipse = ConicSection(expr)

    # 2. Trimmed ellipse with clipping mask (should be open)
    # The ellipse extends from y = 42 to y = 58.
    # Mask y <= 50 clips the upper half of the ellipse, making it open.
    mask_open = lambda x_val, y_val: y_val <= 50.0
    trimmed_open = TrimmedImplicitCurve(ellipse, mask_open)
    curve_open = CompositeCurve([trimmed_open])

    assert not curve_open.is_closed()

    # 3. Trimmed ellipse with non-clipping mask (should be closed)
    # Mask y <= 100 allows the entire ellipse.
    mask_closed = lambda x_val, y_val: y_val <= 100.0
    trimmed_closed = TrimmedImplicitCurve(ellipse, mask_closed)
    curve_closed = CompositeCurve([trimmed_closed])

    assert curve_closed.is_closed()
