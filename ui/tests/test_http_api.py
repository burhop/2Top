import json

import pytest

from ui.app import app, scene_manager


@pytest.fixture(autouse=True)
def clear_scene_before_each_test():
    try:
        objs = scene_manager.list_objects()
        if isinstance(objs, dict):
            ids = list(objs.keys())
        else:
            ids = list(objs)
        for oid in ids:
            scene_manager.remove_object(oid)
    except Exception:
        pass
    yield


def test_scene_info_empty():
    client = app.test_client()
    resp = client.get('/api/scene/info')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert isinstance(data['objects'], list)
    assert data['object_count'] == 0


def test_scene_info_after_create_via_socketio():
    # Use socketio test client to create, then check HTTP endpoint
    from ui.app import socketio
    sio_client = socketio.test_client(app, flask_test_client=app.test_client())

    # Create an object
    obj_id = 'circle_http_check_1'
    sio_client.emit('ui_command', {
        'command_id': 1,
        'command': {
            'command': 'create_circle',
            'obj_id': obj_id,
            'center_x': 0,
            'center_y': 0,
            'radius': 1.0,
        }
    })
    # Drain ui_response to ensure command processed
    received = sio_client.get_received()
    assert any(evt['name'] == 'ui_response' for evt in received), 'No ui_response'

    # Now query scene info
    http_client = app.test_client()
    resp = http_client.get('/api/scene/info')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert obj_id in data['objects']
    assert data['object_count'] >= 1


def test_render_image_endpoint_smoke():
    client = app.test_client()
    # Request render with small resolution for speed
    resp = client.post('/api/render/image',
                       data=json.dumps({'resolution': [200, 150]}),
                       content_type='application/json')
    # Endpoint should respond, even if backend uses empty scene
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert isinstance(payload.get('image_url'), str)


def test_geometry_tests_listing():
    client = app.test_client()
    resp = client.get('/api/geometry-tests')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    tests = payload['tests']
    assert isinstance(tests, list) and tests
    assert {'id', 'name', 'description'} <= set(tests[0].keys())


def test_geometry_tests_run_and_scene_data_roundtrip():
    client = app.test_client()

    # Run a known scenario
    resp = client.post(
        '/api/geometry-tests/run',
        data=json.dumps({'test_id': 'circle_line'}),
        content_type='application/json',
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert payload['objects'], 'Expected created objects from test run'

    # Scene data should include the new objects and annotations
    scene_resp = client.get('/api/geometry-scene')
    assert scene_resp.status_code == 200
    scene_payload = scene_resp.get_json()
    assert scene_payload['success'] is True
    scene = scene_payload['data']
    assert isinstance(scene['objects'], list) and len(scene['objects']) >= 2
    assert isinstance(scene['intersections'], list)
    assert len(scene['scene_bounds']) == 4
