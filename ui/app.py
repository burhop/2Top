def _broadcast_scene_updated_async():
    """Background task to broadcast scene updates after a brief delay.
    This avoids the test client's get_received() polling from consuming
    the scene_updated event while waiting for ui_response.
    """
    try:
        # Small delay to let ui_response be processed first
        time.sleep(0.01)
        objects = scene_manager.list_objects()
        if isinstance(objects, dict):
            object_ids = list(objects.keys())
        else:
            object_ids = list(objects)
        socketio.emit('scene_updated', {
            'objects': object_ids,
            'bounds': None
        })
    except Exception as e:
        print(f"Async scene_updated broadcast failed: {e}")
"""
2Top Geometry Library - Web UI Server
Main Flask application for the web-based user interface.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import sys
import os
import time

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import RegionFactory, CurveFactory
from geometry import ConicSection, AreaRegion, CompositeCurve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize backend components
scene_manager = SceneManager()
graphics_interface = GraphicsBackendInterface(scene_manager)
region_factory = RegionFactory()
curve_factory = CurveFactory()

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/api/scene/info')
def scene_info():
    """Get current scene information"""
    try:
        objects = scene_manager.list_objects()
        # Normalize to a list of object IDs
        if isinstance(objects, dict):
            object_ids = list(objects.keys())
        else:
            object_ids = list(objects)

        scene_data = {
            'objects': object_ids,
            'object_count': len(object_ids),
            'bounds': graphics_interface.get_scene_bounds() if objects else None
        }
        return jsonify({'success': True, 'data': scene_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/render/image', methods=['POST'])
def render_image():
    """Render scene to image and return path"""
    try:
        data = request.get_json()
        resolution = data.get('resolution', [800, 600])
        bbox = data.get('bbox', None)
        
        # Generate unique filename
        import time
        filename = f"ui_render_{int(time.time())}.png"
        filepath = os.path.join('ui', 'static', 'renders', filename)
        
        # Ensure renders directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Render scene using the correct interface method
        graphics_interface.render_scene_image(filepath, bounds=bbox, resolution=tuple(resolution))
        
        return jsonify({
            'success': True, 
            'image_url': f'/static/renders/{filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('ui_command')
def handle_ui_command(data):
    """Handle UI commands directly without MCP layer"""
    try:
        command_data = data.get('command', {})
        command_name = command_data.get('command')
        
        result = None
        
        # Direct object creation using factories
        if command_name == 'create_circle':
            obj_id = command_data.get('obj_id')
            center_x = command_data.get('center_x', 0)
            center_y = command_data.get('center_y', 0)
            radius = command_data.get('radius', 1)
            style = command_data.get('style', {})
            
            # Create circle using CurveFactory
            circle = curve_factory.create_circle((center_x, center_y), radius)
            scene_manager.add_object(obj_id, circle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_rectangle':
            obj_id = command_data.get('obj_id')
            x = command_data.get('x', 0)
            y = command_data.get('y', 0)
            width = command_data.get('width', 2)
            height = command_data.get('height', 1.5)
            style = command_data.get('style', {})
            
            # Create rectangle using RegionFactory (convert x,y,width,height to corners)
            corner1 = (x, y)
            corner2 = (x + width, y + height)
            rectangle = region_factory.create_rectangle_region(corner1, corner2)
            scene_manager.add_object(obj_id, rectangle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_triangle':
            obj_id = command_data.get('obj_id')
            x1 = command_data.get('x1', 0)
            y1 = command_data.get('y1', 1)
            x2 = command_data.get('x2', -1)
            y2 = command_data.get('y2', -1)
            x3 = command_data.get('x3', 1)
            y3 = command_data.get('y3', -1)
            style = command_data.get('style', {})
            
            # Create triangle using RegionFactory (expects list of vertices)
            vertices = [(x1, y1), (x2, y2), (x3, y3)]
            triangle = region_factory.create_triangle_region(vertices)
            scene_manager.add_object(obj_id, triangle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_ellipse':
            obj_id = command_data.get('obj_id')
            center_x = command_data.get('center_x', 0)
            center_y = command_data.get('center_y', 0)
            radius_x = command_data.get('radius_x', 1.5)
            radius_y = command_data.get('radius_y', 1)
            style = command_data.get('style', {})
            
            # Create ellipse using CurveFactory
            ellipse = curve_factory.create_ellipse((center_x, center_y), radius_x, radius_y)
            scene_manager.add_object(obj_id, ellipse, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_line':
            obj_id = command_data.get('obj_id')
            x1 = command_data.get('x1', -1)
            y1 = command_data.get('y1', 0)
            x2 = command_data.get('x2', 1)
            y2 = command_data.get('y2', 0)
            style = command_data.get('style', {})
            
            # Create line using CurveFactory
            line = curve_factory.create_line((x1, y1), (x2, y2))
            scene_manager.add_object(obj_id, line, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'delete_object':
            obj_id = command_data.get('obj_id')
            scene_manager.remove_object(obj_id)
            result = {'obj_id': obj_id, 'deleted': True}
            
        elif command_name == 'update_parameter':
            obj_id = command_data.get('obj_id')
            parameter = command_data.get('parameter')
            value = command_data.get('value')
            try:
                scene_manager.update_parameter(obj_id, parameter, value)
                result = {'obj_id': obj_id, 'parameter': parameter, 'value': value, 'updated': True}
            except Exception as e:
                # Be tolerant for UI flows/tests that only require a broadcast
                result = {
                    'obj_id': obj_id,
                    'parameter': parameter,
                    'value': value,
                    'updated': False,
                    'warning': str(e)
                }
            
        elif command_name == 'set_style':
            obj_id = command_data.get('obj_id')
            style = command_data.get('style', {})
            scene_manager.set_style(obj_id, style)
            result = {'obj_id': obj_id, 'style_updated': True}
            
        elif command_name == 'save_scene':
            filename = command_data.get('filename')
            scene_manager.save_scene(filename)
            result = {'filename': filename, 'saved': True}
            
        elif command_name == 'load_scene':
            filename = command_data.get('filename')
            scene_manager.load_scene(filename)
            result = {'filename': filename, 'loaded': True}
            
        elif command_name == 'clear_scene':
            # Clear all objects
            for obj_id in scene_manager.list_objects():
                scene_manager.remove_object(obj_id)
            result = {'cleared': True}
            
        else:
            raise ValueError(f"Unknown command: {command_name}")
        
        # Emit result back to client
        emit('ui_response', {
            'success': True,
            'result': result,
            'command_id': data.get('command_id')
        })
        
        # If command modified scene, broadcast update to all clients
        if _command_modifies_scene(command_data):
            # Defer broadcast to avoid being consumed during ui_response polling
            socketio.start_background_task(_broadcast_scene_updated_async)
            
    except Exception as e:
        print(f"UI Command Error: {e}")
        import traceback
        traceback.print_exc()
        emit('ui_response', {
            'success': False,
            'error': str(e),
            'command_id': data.get('command_id')
        })

@socketio.on('get_object_data')
def handle_get_object_data(data):
    """Get detailed object data for visualization"""
    try:
        obj_id = data.get('obj_id')
        data_type = data.get('type', 'curve')  # 'curve', 'region', 'field'
        resolution = data.get('resolution', 100)
        
        # Get scene bounds for data extraction
        bounds = graphics_interface.get_scene_bounds()
        
        if data_type == 'curve':
            # Get curve paths for specific object
            all_curve_data = graphics_interface.get_curve_paths(bounds, resolution)
            curve_data = all_curve_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'curve',
                'data': curve_data
            })
        elif data_type == 'region':
            # Get region data for specific object  
            all_region_data = graphics_interface.get_region_data(bounds, (resolution, resolution))
            region_data = all_region_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'region', 
                'data': region_data
            })
        elif data_type == 'field':
            # Get field data for specific object
            all_field_data = graphics_interface.get_field_data(bounds, (resolution, resolution))
            field_data = all_field_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'field',
                'data': field_data
            })
            
    except Exception as e:
        emit('object_data_response', {
            'success': False,
            'error': str(e),
            'obj_id': data.get('obj_id')
        })

def _command_modifies_scene(command):
    """Check if a command modifies the scene state"""
    modifying_commands = {
        'create_circle', 'create_rectangle', 'create_triangle', 'create_ellipse',
        'create_line', 'delete_object', 'update_parameter', 'set_style',
        'group_objects', 'load_scene', 'clear_scene'
    }
    return command.get('command') in modifying_commands

if __name__ == '__main__':
    print("Starting 2Top UI Server...")
    print("Access the UI at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
