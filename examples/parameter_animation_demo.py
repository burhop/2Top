"""
Parameter Animation Demo for 2Top SceneManager

Demonstrates the parameter animation system with various geometric objects,
showing single-parameter animations, multi-parameter animations, and
frame caching capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scene_management import SceneManager
from geometry.parameter_interface import CircleParameters, RectangleParameters, TriangleParameters


class AnimatableCircle(CircleParameters):
    """Example animatable circle implementation."""
    
    def __init__(self, center_x=0, center_y=0, radius=1):
        super().__init__(center_x, center_y, radius)
        self.expression = None
        self._rebuild_expression()
    
    def _rebuild_expression(self):
        """Rebuild the implicit expression from current parameters."""
        cx = self._parameters['center_x']
        cy = self._parameters['center_y']
        r = self._parameters['radius']
        
        # In a real implementation, this would be a sympy expression
        self.expression = f"(x - {cx})^2 + (y - {cy})^2 - {r}^2"
        print(f"Circle expression updated: {self.expression}")
    
    def _on_parameter_changed(self, name, value):
        """Rebuild expression when parameters change."""
        super()._on_parameter_changed(name, value)
        self._rebuild_expression()
    
    def to_dict(self):
        return {
            'type': 'AnimatableCircle',
            'center_x': self._parameters['center_x'],
            'center_y': self._parameters['center_y'],
            'radius': self._parameters['radius']
        }
    
    def plot(self, xlim=(-3, 3), ylim=(-3, 3), ax=None, **style):
        """Simple plotting for demonstration."""
        if ax is None:
            fig, ax = plt.subplots()
        
        # Draw circle
        theta = np.linspace(0, 2*np.pi, 100)
        cx = self._parameters['center_x']
        cy = self._parameters['center_y']
        r = self._parameters['radius']
        
        x = cx + r * np.cos(theta)
        y = cy + r * np.sin(theta)
        
        color = style.get('color', 'blue')
        linewidth = style.get('linewidth', 2)
        
        ax.plot(x, y, color=color, linewidth=linewidth, label=f'r={r:.1f}')
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)


class AnimatableRectangle(RectangleParameters):
    """Example animatable rectangle implementation."""
    
    def __init__(self, center_x=0, center_y=0, width=2, height=2):
        super().__init__(center_x, center_y, width, height)
        self._rebuild_boundary()
    
    def _rebuild_boundary(self):
        """Rebuild boundary from current parameters."""
        cx = self._parameters['center_x']
        cy = self._parameters['center_y']
        w = self._parameters['width']
        h = self._parameters['height']
        
        print(f"Rectangle boundary updated: center=({cx}, {cy}), size=({w}, {h})")
    
    def to_dict(self):
        return {
            'type': 'AnimatableRectangle',
            'center_x': self._parameters['center_x'],
            'center_y': self._parameters['center_y'],
            'width': self._parameters['width'],
            'height': self._parameters['height']
        }
    
    def plot(self, xlim=(-3, 3), ylim=(-3, 3), ax=None, **style):
        """Simple plotting for demonstration."""
        if ax is None:
            fig, ax = plt.subplots()
        
        # Draw rectangle
        cx = self._parameters['center_x']
        cy = self._parameters['center_y']
        w = self._parameters['width']
        h = self._parameters['height']
        
        x = cx - w/2
        y = cy - h/2
        
        color = style.get('color', 'red')
        linewidth = style.get('linewidth', 2)
        
        rect = plt.Rectangle((x, y), w, h, fill=False, 
                           edgecolor=color, linewidth=linewidth,
                           label=f'{w:.1f}×{h:.1f}')
        ax.add_patch(rect)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)


def demo_single_parameter_animation():
    """Demonstrate single parameter animation."""
    print("\n=== Single Parameter Animation Demo ===")
    
    scene = SceneManager()
    
    # Create animatable circle
    circle = AnimatableCircle(center_x=0, center_y=0, radius=1.0)
    scene.add_object("circle1", circle, style={'color': 'blue', 'linewidth': 3})
    
    print(f"Initial radius: {scene.get_parameter('circle1', 'radius')}")
    
    # Create animation with radius varying from 0.5 to 2.5
    radius_values = np.linspace(0.5, 2.5, 20).tolist()
    
    print(f"Creating animation with {len(radius_values)} frames...")
    print(f"Radius values: {radius_values[:5]}...{radius_values[-5:]}")
    
    # Note: In a real implementation, this would create actual animation files
    # For demo purposes, we'll just show the parameter updates
    try:
        scene.create_parameter_animation(
            obj_id="circle1",
            parameter="radius", 
            values=radius_values,
            filename="circle_radius_animation.gif",
            resolution=(800, 600),
            fps=10,
            cache_frames=True
        )
        print("✅ Single parameter animation created successfully!")
        
        # Show cache info
        cache_info = scene.get_animation_cache_info()
        print(f"Animation cache entries: {len(cache_info)}")
        for cache_id, info in cache_info.items():
            print(f"  {cache_id}: {info['frame_count']} frames, {info['cache_size_mb']:.2f} MB")
            
    except Exception as e:
        print(f"Animation creation failed (expected in demo): {e}")
    
    # Verify parameter was restored
    final_radius = scene.get_parameter('circle1', 'radius')
    print(f"Final radius (should be restored to 1.0): {final_radius}")


def demo_multi_parameter_animation():
    """Demonstrate multi-parameter animation."""
    print("\n=== Multi-Parameter Animation Demo ===")
    
    scene = SceneManager()
    
    # Create multiple animatable objects
    circle = AnimatableCircle(center_x=-1, center_y=0, radius=1.0)
    rectangle = AnimatableRectangle(center_x=1, center_y=0, width=1.5, height=1.0)
    
    scene.add_object("circle", circle, style={'color': 'blue'})
    scene.add_object("rectangle", rectangle, style={'color': 'red'})
    
    # Create synchronized animation
    frame_count = 15
    
    # Circle radius oscillates
    circle_radii = (1.0 + 0.8 * np.sin(np.linspace(0, 2*np.pi, frame_count))).tolist()
    
    # Rectangle width grows and shrinks
    rect_widths = (1.5 + 1.0 * np.sin(np.linspace(0, 2*np.pi, frame_count))).tolist()
    
    # Rectangle height oscillates out of phase
    rect_heights = (1.0 + 0.6 * np.sin(np.linspace(np.pi/2, 2*np.pi + np.pi/2, frame_count))).tolist()
    
    animations = [
        {'obj_id': 'circle', 'parameter': 'radius', 'values': circle_radii},
        {'obj_id': 'rectangle', 'parameter': 'width', 'values': rect_widths},
        {'obj_id': 'rectangle', 'parameter': 'height', 'values': rect_heights}
    ]
    
    print(f"Creating multi-parameter animation with {frame_count} frames...")
    print(f"Circle radius range: {min(circle_radii):.2f} - {max(circle_radii):.2f}")
    print(f"Rectangle width range: {min(rect_widths):.2f} - {max(rect_widths):.2f}")
    print(f"Rectangle height range: {min(rect_heights):.2f} - {max(rect_heights):.2f}")
    
    try:
        scene.create_multi_parameter_animation(
            animations=animations,
            filename="multi_parameter_animation.gif",
            resolution=(1000, 600),
            fps=8,
            cache_frames=True
        )
        print("✅ Multi-parameter animation created successfully!")
        
    except Exception as e:
        print(f"Animation creation failed (expected in demo): {e}")


def demo_dependency_tracking():
    """Demonstrate dependency tracking between objects."""
    print("\n=== Dependency Tracking Demo ===")
    
    scene = SceneManager()
    
    # Create primary circle
    primary = AnimatableCircle(center_x=0, center_y=0, radius=1.0)
    scene.add_object("primary", primary, style={'color': 'blue'})
    
    # Create dependent circle (radius is always 0.5 * primary radius)
    dependent = AnimatableCircle(center_x=2, center_y=0, radius=0.5)
    scene.add_object("dependent", dependent, style={'color': 'green'})
    
    # Register dependency
    scene.register_dependency("dependent", "primary")
    
    print("Dependency registered: dependent circle follows primary circle")
    
    # Show initial state
    print(f"Primary radius: {scene.get_parameter('primary', 'radius')}")
    print(f"Dependent radius: {scene.get_parameter('dependent', 'radius')}")
    
    # Update primary parameter
    print("\nUpdating primary radius to 2.0...")
    scene.update_parameter("primary", "radius", 2.0, update_dependents=True)
    
    print(f"Primary radius after update: {scene.get_parameter('primary', 'radius')}")
    print(f"Dependent radius after update: {scene.get_parameter('dependent', 'radius')}")
    
    # Show dependency information
    deps = scene.get_dependencies("primary")
    print(f"Primary object dependents: {deps['dependents']}")
    
    deps = scene.get_dependencies("dependent")
    print(f"Dependent object sources: {deps['sources']}")


def demo_scene_persistence():
    """Demonstrate scene saving and loading."""
    print("\n=== Scene Persistence Demo ===")
    
    scene = SceneManager()
    
    # Create scene with multiple objects
    circle = AnimatableCircle(center_x=0, center_y=0, radius=1.5)
    rectangle = AnimatableRectangle(center_x=2, center_y=1, width=2.0, height=1.5)
    
    scene.add_object("circle1", circle, style={'color': 'purple', 'linewidth': 3})
    scene.add_object("rect1", rectangle, style={'color': 'orange', 'linewidth': 2})
    
    # Create group
    scene.set_group("shapes", ["circle1", "rect1"])
    
    # Set up dependency
    scene.register_dependency("rect1", "circle1")
    
    print("Scene created with:")
    print(f"  Objects: {scene.list_objects()}")
    print(f"  Groups: {list(scene._groups.keys())}")
    print(f"  Dependencies: {len(scene._dependencies)} relationships")
    
    # Save scene
    filename = "demo_scene.json"
    try:
        scene.save_scene(filename)
        print(f"✅ Scene saved to {filename}")
        
        # Create new scene and load
        new_scene = SceneManager()
        new_scene.load_scene(filename)
        
        print(f"✅ Scene loaded successfully")
        print(f"  Loaded groups: {list(new_scene._groups.keys())}")
        print(f"  Loaded styles: {len(new_scene._styles)} objects")
        
    except Exception as e:
        print(f"Scene persistence failed (expected in demo): {e}")
    
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)


def demo_animation_cache_management():
    """Demonstrate animation cache management."""
    print("\n=== Animation Cache Management Demo ===")
    
    scene = SceneManager()
    circle = AnimatableCircle(radius=1.0)
    scene.add_object("circle", circle)
    
    # Simulate cached animations
    scene._animation_cache = {
        'cache1': {
            'obj_id': 'circle',
            'parameter': 'radius',
            'frame_count': 20,
            'cache_size_mb': 2.5,
            'created': '2024-01-01T10:00:00',
            'frame_files': []
        },
        'cache2': {
            'type': 'multi_parameter',
            'frame_count': 30,
            'cache_size_mb': 4.1,
            'created': '2024-01-01T11:00:00',
            'frame_files': []
        }
    }
    
    print("Animation cache status:")
    cache_info = scene.get_animation_cache_info()
    total_size = sum(info['cache_size_mb'] for info in cache_info.values())
    
    for cache_id, info in cache_info.items():
        print(f"  {cache_id}: {info['frame_count']} frames, "
              f"{info['cache_size_mb']:.1f} MB, {info['type']}")
    
    print(f"Total cache size: {total_size:.1f} MB")
    
    # Clear specific cache
    print("\nClearing cache1...")
    scene.clear_animation_cache('cache1')
    
    remaining = scene.get_animation_cache_info()
    print(f"Remaining caches: {len(remaining)}")
    
    # Clear all caches
    print("Clearing all caches...")
    scene.clear_animation_cache()
    
    final_count = len(scene.get_animation_cache_info())
    print(f"Final cache count: {final_count}")


def main():
    """Run all animation demos."""
    print("🎬 2Top Parameter Animation System Demo")
    print("=" * 50)
    
    try:
        demo_single_parameter_animation()
        demo_multi_parameter_animation()
        demo_dependency_tracking()
        demo_scene_persistence()
        demo_animation_cache_management()
        
        print("\n" + "=" * 50)
        print("✅ All demos completed successfully!")
        print("\nThe SceneManager parameter animation system provides:")
        print("  • Single and multi-parameter animations")
        print("  • Frame caching for performance")
        print("  • Dependency tracking for complex scenes")
        print("  • Scene persistence and loading")
        print("  • Comprehensive cache management")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
