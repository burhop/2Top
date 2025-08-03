import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# Test the contour plotting directly
def test_circle_contour():
    # Circle parameters
    cx, cy, radius = 1.0, 1.0, 1.5
    
    # Create grid
    x_range = (-1, 3)
    y_range = (-1, 3)
    resolution = 1000
    
    x_vals = np.linspace(x_range[0], x_range[1], resolution)
    y_vals = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    
    # Circle equation: (x - cx)^2 + (y - cy)^2 - r^2
    Z = (X - cx)**2 + (Y - cy)**2 - radius**2
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot 1: Contour with filled contours to see the function
    cs1 = ax1.contourf(X, Y, Z, levels=50, cmap='RdBu')
    ax1.contour(X, Y, Z, levels=[0], colors='black', linewidths=3)
    ax1.set_title('Circle Function with Zero Contour')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(cs1, ax=ax1)
    
    # Plot 2: Just the zero contour
    cs2 = ax2.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)
    ax2.set_title('Zero Level Set Only')
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(x_range)
    ax2.set_ylim(y_range)
    
    # Print contour information
    print(f"Contour set type: {type(cs2)}")
    print(f"Number of levels: {len(cs2.levels)}")
    print(f"Levels: {cs2.levels}")
    
    # Check if we have collections attribute
    if hasattr(cs2, 'collections'):
        print(f"Number of contour collections: {len(cs2.collections)}")
        for i, collection in enumerate(cs2.collections):
            print(f"Collection {i}: {len(collection.get_paths())} paths")
            for j, path in enumerate(collection.get_paths()):
                print(f"  Path {j}: {len(path.vertices)} vertices")
    else:
        print("No collections attribute found")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    test_circle_contour()
