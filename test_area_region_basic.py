#!/usr/bin/env python3
"""
Basic test script for AreaRegion functionality.
"""

from geometry import AreaRegion, create_square_from_edges
import traceback

def test_basic_functionality():
    """Test basic AreaRegion functionality."""
    print("Testing AreaRegion basic functionality...")
    
    try:
        # Test 1: Create a simple square region
        print("\n1. Creating simple square region...")
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        print(f"   Created region: {region}")
        
        # Test 2: Test containment
        print("\n2. Testing containment...")
        test_points = [
            (0, 0, "center"),
            (0.5, 0.5, "inside"),
            (2, 0, "outside"),
            (1, 0, "boundary")
        ]
        
        for x, y, desc in test_points:
            try:
                result = region.contains(x, y)
                print(f"   Point ({x}, {y}) [{desc}]: {result}")
            except Exception as e:
                print(f"   Point ({x}, {y}) [{desc}]: ERROR - {e}")
        
        # Test 3: Test area calculation
        print("\n3. Testing area calculation...")
        try:
            area = region.area()
            print(f"   Area: {area}")
        except Exception as e:
            print(f"   Area calculation ERROR: {e}")
            traceback.print_exc()
        
        # Test 4: Test serialization
        print("\n4. Testing serialization...")
        try:
            data = region.to_dict()
            print(f"   Serialized successfully: {data['type']}")
            
            reconstructed = AreaRegion.from_dict(data)
            print(f"   Deserialized successfully: {reconstructed}")
        except Exception as e:
            print(f"   Serialization ERROR: {e}")
            traceback.print_exc()
        
        print("\nBasic functionality test completed!")
        
    except Exception as e:
        print(f"ERROR in basic functionality test: {e}")
        traceback.print_exc()

def test_region_with_hole():
    """Test AreaRegion with a hole."""
    print("\n\nTesting AreaRegion with hole...")
    
    try:
        # Create outer boundary (4x4 square)
        outer = create_square_from_edges((-2, -2), (2, 2))
        
        # Create hole (2x2 square)
        hole = create_square_from_edges((-1, -1), (1, 1))
        
        # Create region with hole
        region = AreaRegion(outer, [hole])
        print(f"Created region with hole: {region}")
        
        # Test containment
        test_points = [
            (0, 0, "center of hole"),
            (1.5, 0, "outside hole, inside outer"),
            (3, 0, "outside outer")
        ]
        
        for x, y, desc in test_points:
            try:
                result = region.contains(x, y)
                print(f"   Point ({x}, {y}) [{desc}]: {result}")
            except Exception as e:
                print(f"   Point ({x}, {y}) [{desc}]: ERROR - {e}")
        
        # Test area
        try:
            area = region.area()
            print(f"   Area with hole: {area}")
        except Exception as e:
            print(f"   Area calculation ERROR: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"ERROR in hole test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
    test_region_with_hole()
