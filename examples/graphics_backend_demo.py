"""
Graphics Backend Interface and MCP Command Handler Demo

Demonstrates the complete API layer for front-end integration and external
service interaction with the 2Top geometry library.
"""

import json
import tempfile
import os
from pathlib import Path
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scene_management.scene_manager import SceneManager
from graphics_backend.graphics_interface import GraphicsBackendInterface
from graphics_backend.mcp_handler import MCPCommandHandler
from visual_tests.utils.test_objects import RegionFactory


def demo_graphics_backend_interface():
    """Demonstrate GraphicsBackendInterface capabilities."""
    print("=" * 60)
    print("GRAPHICS BACKEND INTERFACE DEMO")
    print("=" * 60)
    
    # Create scene with various objects
    scene_manager = SceneManager()
    factory = RegionFactory()
    
    # Add geometric objects
    circle = factory.create_circle_region((0, 0), 1.5)
    rectangle = factory.create_rectangle_region((2, 1.25), (4, 2.75))  # center (3,2), width 2.0, height 1.5
    triangle = factory.create_triangle_region([(-1, -2), (1, -2), (0, 0)])
    
    scene_manager.add_object('main_circle', circle)
    scene_manager.add_object('main_rectangle', rectangle)
    scene_manager.add_object('main_triangle', triangle)
    
    # Set styles
    scene_manager.set_style('main_circle', {
        'color': 'blue', 'fill_color': 'lightblue', 'fill_alpha': 0.3, 'linewidth': 2
    })
    scene_manager.set_style('main_rectangle', {
        'color': 'red', 'fill_color': 'lightcoral', 'fill_alpha': 0.4, 'linewidth': 3
    })
    scene_manager.set_style('main_triangle', {
        'color': 'green', 'fill_color': 'lightgreen', 'fill_alpha': 0.5, 'linewidth': 2
    })
    
    # Create graphics backend
    graphics_backend = GraphicsBackendInterface(scene_manager)
    
    print(f"\n1. SCENE SUMMARY")
    print("-" * 40)
    summary = graphics_backend.get_scene_summary()
    print(f"Objects: {summary['object_count']}")
    print(f"Object types: {summary['object_types']}")
    print(f"Scene bounds: {[f'{x:.2f}' for x in summary['scene_bounds']]}")
    
    print(f"\n2. CURVE PATH EXTRACTION")
    print("-" * 40)
    bounds = graphics_backend.get_scene_bounds(padding=0.2)
    curve_data = graphics_backend.get_curve_paths(bounds=bounds, resolution=100)
    
    for obj_id, data in curve_data.items():
        if data.get('points'):
            print(f"{obj_id}: {len(data['points'])} points, closed={data['closed']}")
            print(f"  Bounds: [{', '.join(f'{x:.2f}' for x in data['bounds'])}]")
        else:
            print(f"{obj_id}: No curve data (may be region-only)")
    
    print(f"\n3. FIELD DATA EXTRACTION")
    print("-" * 40)
    field_data = graphics_backend.get_field_data(bounds=bounds, resolution=(50, 50))
    
    for obj_id, data in field_data.items():
        if data.get('data') is not None:
            stats = data['statistics']
            print(f"{obj_id}: {stats['finite_count']}/{stats['total_count']} finite values")
            print(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}], mean={stats['mean']:.3f}")
        else:
            print(f"{obj_id}: Field evaluation failed")
    
    print(f"\n4. REGION DATA EXTRACTION")
    print("-" * 40)
    region_data = graphics_backend.get_region_data(bounds=bounds, resolution=(60, 60))
    
    for obj_id, data in region_data.items():
        if data.get('inside_mask') is not None:
            stats = data['statistics']
            print(f"{obj_id}: {stats['inside_count']} inside points ({stats['inside_percentage']:.1f}%)")
            print(f"  Boundary: {stats['boundary_count']} points ({stats['boundary_percentage']:.1f}%)")
        else:
            print(f"{obj_id}: Region evaluation failed")
    
    print(f"\n5. SCENE RENDERING")
    print("-" * 40)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        render_file = tmp.name
    
    try:
        render_info = graphics_backend.render_scene_image(
            render_file, 
            bounds=bounds,
            resolution=(800, 600),
            show_grid=True,
            show_axes=True
        )
        
        print(f"Rendered scene to: {render_file}")
        print(f"Rendered objects: {render_info['object_count']}")
        for obj_info in render_info['rendered_objects']:
            print(f"  - {obj_info['id']} ({obj_info['type']})")
        
        # Check file size
        if os.path.exists(render_file):
            file_size = os.path.getsize(render_file)
            print(f"Image file size: {file_size / 1024:.1f} KB")
        
    finally:
        # Clean up
        if os.path.exists(render_file):
            os.unlink(render_file)
    
    print(f"\n6. OBJECT INFORMATION")
    print("-" * 40)
    for obj_id in scene_manager.list_objects():
        info = graphics_backend.get_object_info(obj_id)
        print(f"{obj_id}:")
        print(f"  Type: {info['type']}")
        print(f"  Style: {info['style']}")
        if 'bounds' in info:
            print(f"  Bounds: [{', '.join(f'{x:.2f}' for x in info['bounds'])}]")


def demo_mcp_command_handler():
    """Demonstrate MCP Command Handler capabilities."""
    print("\n" + "=" * 60)
    print("MCP COMMAND HANDLER DEMO")
    print("=" * 60)
    
    # Create MCP handler
    mcp_handler = MCPCommandHandler()
    
    print(f"\n1. AVAILABLE COMMANDS")
    print("-" * 40)
    result = mcp_handler.handle_command('help.list_commands')
    commands = result['data']
    print(f"Total commands available: {len(commands)}")
    
    # Group commands by category
    categories = {}
    for cmd in commands:
        category = cmd.split('.')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(cmd.split('.', 1)[1])
    
    for category, cmd_list in sorted(categories.items()):
        print(f"  {category}: {len(cmd_list)} commands ({', '.join(cmd_list[:3])}{'...' if len(cmd_list) > 3 else ''})")
    
    print(f"\n2. SCENE CREATION VIA COMMANDS")
    print("-" * 40)
    
    # Create objects using commands
    objects_to_create = [
        ('create.circle', {
            'object_id': 'cmd_circle',
            'center': [0, 0],
            'radius': 2.0,
            'style': {'color': 'blue', 'fill_alpha': 0.3}
        }),
        ('create.rectangle', {
            'object_id': 'cmd_rect',
            'center': [4, 1],
            'width': 3.0,
            'height': 2.0,
            'style': {'color': 'red', 'linewidth': 3}
        }),
        ('create.triangle', {
            'object_id': 'cmd_triangle',
            'vertices': [[-2, -1], [0, -1], [-1, 1]],
            'style': {'color': 'green', 'fill_color': 'lightgreen'}
        }),
        ('create.ellipse', {
            'object_id': 'cmd_ellipse',
            'center': [2, -2],
            'semi_major': 2.5,
            'semi_minor': 1.0,
            'style': {'color': 'purple', 'alpha': 0.7}
        })
    ]
    
    for command, params in objects_to_create:
        result = mcp_handler.handle_command(command, params)
        if result['success']:
            data = result['data']
            print(f"✓ Created {data['type']}: {data['object_id']}")
        else:
            print(f"✗ Failed to create object: {result['error']}")
    
    print(f"\n3. SCENE MANAGEMENT")
    print("-" * 40)
    
    # List objects
    result = mcp_handler.handle_command('scene.list_objects')
    objects = result['data']
    print(f"Scene contains {len(objects)} objects: {', '.join(objects)}")
    
    # Get scene summary
    result = mcp_handler.handle_command('scene.get_summary')
    if result['success']:
        summary = result['data']
        print(f"Object types: {summary['object_types']}")
        bounds = summary['scene_bounds']
        print(f"Scene bounds: [{', '.join(f'{x:.2f}' for x in bounds)}]")
    
    print(f"\n4. OBJECT MANIPULATION")
    print("-" * 40)
    
    # Modify object style
    result = mcp_handler.handle_command('object.set_style', {
        'object_id': 'cmd_circle',
        'style': {'color': 'orange', 'fill_color': 'yellow', 'linewidth': 4}
    })
    if result['success']:
        print("✓ Updated circle style to orange/yellow")
    
    # Get object information
    result = mcp_handler.handle_command('scene.get_object_info', {
        'object_id': 'cmd_circle'
    })
    if result['success']:
        info = result['data']
        print(f"Circle info: type={info['type']}, style={info['style']}")
    
    print(f"\n5. GROUPING AND DEPENDENCIES")
    print("-" * 40)
    
    # Create group
    result = mcp_handler.handle_command('group.create', {
        'group_name': 'geometric_shapes',
        'object_ids': ['cmd_circle', 'cmd_rect', 'cmd_triangle']
    })
    if result['success']:
        print(f"✓ Created group with {result['data']['object_count']} objects")
    
    # Register dependency
    result = mcp_handler.handle_command('dependency.register', {
        'source_id': 'cmd_circle',
        'dependent_id': 'cmd_rect'
    })
    if result['success']:
        print("✓ Registered dependency: rectangle depends on circle")
    
    # Get dependencies
    result = mcp_handler.handle_command('dependency.get', {
        'object_id': 'cmd_circle'
    })
    if result['success']:
        deps = result['data']['dependencies']
        print(f"Circle dependencies: {deps}")
    
    print(f"\n6. RENDERING COMMANDS")
    print("-" * 40)
    
    # Get scene bounds
    result = mcp_handler.handle_command('render.get_scene_bounds', {
        'padding': 0.15
    })
    if result['success']:
        bounds = result['data']
        print(f"Optimal bounds: [{', '.join(f'{x:.2f}' for x in bounds)}]")
    
    # Get curve paths
    result = mcp_handler.handle_command('render.get_curve_paths', {
        'bounds': bounds,
        'resolution': 80
    })
    if result['success']:
        curve_data = result['data']
        print(f"Extracted curve data for {len(curve_data)} objects")
        for obj_id, data in curve_data.items():
            if data.get('points'):
                print(f"  {obj_id}: {len(data['points'])} points")
    
    # Get region data
    result = mcp_handler.handle_command('render.get_region_data', {
        'bounds': bounds,
        'resolution': [40, 40]
    })
    if result['success']:
        region_data = result['data']
        print(f"Extracted region data for {len(region_data)} objects")
        for obj_id, data in region_data.items():
            if data.get('inside_mask'):
                stats = data['statistics']
                print(f"  {obj_id}: {stats['inside_percentage']:.1f}% inside")
    
    # Render scene
    result = mcp_handler.handle_command('render.scene_image', {
        'bounds': bounds,
        'resolution': [600, 400],
        'show_grid': True
    })
    if result['success']:
        render_info = result['data']
        print(f"✓ Rendered scene: {render_info['object_count']} objects")
        print(f"  Image: {render_info['filename']}")
        
        # Clean up rendered file
        if os.path.exists(render_info['filename']):
            os.unlink(render_info['filename'])
    
    print(f"\n7. BATCH COMMAND PROCESSING")
    print("-" * 40)
    
    # Execute multiple commands in batch
    batch_commands = [
        {'command': 'scene.list_objects'},
        {'command': 'scene.get_summary'},
        {'command': 'render.get_scene_bounds', 'params': {'padding': 0.1}},
        {'command': 'animation.get_cache_info'},
        {'command': 'help.get_command_info', 'params': {'command': 'create.circle'}}
    ]
    
    results = mcp_handler.handle_batch_commands(batch_commands)
    
    print(f"Executed {len(batch_commands)} commands in batch:")
    for i, result in enumerate(results):
        cmd_name = batch_commands[i]['command']
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {cmd_name}")
    
    print(f"\n8. SCENE PERSISTENCE")
    print("-" * 40)
    
    # Save scene
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        scene_file = tmp.name
    
    try:
        result = mcp_handler.handle_command('scene.save', {
            'filename': scene_file
        })
        if result['success']:
            print(f"✓ Saved scene to: {scene_file}")
            
            # Check file contents
            with open(scene_file, 'r') as f:
                scene_data = json.load(f)
            print(f"  Scene data keys: {list(scene_data.keys())}")
            print(f"  Objects in file: {len(scene_data.get('objects', {}))}")
        
        # Clear scene
        result = mcp_handler.handle_command('scene.clear')
        if result['success']:
            print(f"✓ Cleared scene ({result['data']['cleared_objects']} objects removed)")
        
        # Load scene back
        result = mcp_handler.handle_command('scene.load', {
            'filename': scene_file
        })
        if result['success']:
            print(f"✓ Loaded scene back from file")
            print(f"  Objects loaded: {result['data']['object_count']}")
        
    finally:
        if os.path.exists(scene_file):
            os.unlink(scene_file)


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING DEMO")
    print("=" * 60)
    
    mcp_handler = MCPCommandHandler()
    
    print(f"\n1. UNKNOWN COMMAND")
    print("-" * 40)
    result = mcp_handler.handle_command('unknown.command')
    print(f"Result: success={result['success']}")
    print(f"Error: {result['error']}")
    print(f"Available commands shown: {len(result['available_commands'])} commands")
    
    print(f"\n2. MISSING PARAMETERS")
    print("-" * 40)
    result = mcp_handler.handle_command('scene.get_object_info', {})
    print(f"Result: success={result['success']}")
    print(f"Error: {result['error']}")
    
    print(f"\n3. INVALID PARAMETER VALUES")
    print("-" * 40)
    result = mcp_handler.handle_command('create.triangle', {
        'vertices': [[0, 0], [1, 1]]  # Only 2 vertices instead of 3
    })
    print(f"Result: success={result['success']}")
    print(f"Error: {result['error']}")
    
    print(f"\n4. NONEXISTENT OBJECT OPERATIONS")
    print("-" * 40)
    result = mcp_handler.handle_command('object.get_style', {
        'object_id': 'nonexistent_object'
    })
    print(f"Result: success={result['success']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    
    print(f"\n5. BATCH COMMAND WITH MIXED SUCCESS")
    print("-" * 40)
    mixed_commands = [
        {'command': 'scene.list_objects'},  # Should succeed
        {'command': 'unknown.command'},     # Should fail
        {'command': 'scene.get_summary'},   # Should succeed
        {'command': 'object.get_style', 'params': {}},  # Should fail (missing param)
    ]
    
    results = mcp_handler.handle_batch_commands(mixed_commands)
    
    print(f"Batch results:")
    for i, result in enumerate(results):
        cmd = mixed_commands[i].get('command', 'malformed')
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {cmd}")
        if not result['success']:
            print(f"    Error: {result['error']}")


def main():
    """Run all demos."""
    print("2Top Graphics Backend and MCP Interface Demo")
    print("=" * 80)
    
    try:
        demo_graphics_backend_interface()
        demo_mcp_command_handler()
        demo_error_handling()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("• GraphicsBackendInterface: Data extraction for front-end integration")
        print("• MCPCommandHandler: Command-based API for external services")
        print("• Scene creation, manipulation, and persistence")
        print("• Rendering data extraction (curves, fields, regions)")
        print("• Object management, grouping, and dependencies")
        print("• Batch command processing")
        print("• Comprehensive error handling")
        print("\nThese APIs provide the foundation for:")
        print("• Web-based UI development")
        print("• AI agent integration")
        print("• External service connectivity")
        print("• Interactive visualization tools")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
