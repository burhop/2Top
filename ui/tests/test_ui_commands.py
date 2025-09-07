import sys
import time
from typing import Dict, Any

import pytest

# Ensure project root on path when running tests from repo root
# so `from ui.app import app, socketio, scene_manager` works

from ui.app import app, socketio, scene_manager


@pytest.fixture(autouse=True)
def clear_scene_before_each_test():
    """Clear the scene to isolate tests."""
    try:
        objs = scene_manager.list_objects()
        if isinstance(objs, dict):
            ids = list(objs.keys())
        else:
            ids = list(objs)
        for oid in ids:
            scene_manager.remove_object(oid)
    except Exception:
        # If clearing fails, that's fine; tests may still proceed
        pass
    yield
    # No teardown needed


def make_client():
    return socketio.test_client(app, flask_test_client=app.test_client())


def drain_events(client, event_name: str, timeout_sec: float = 1.0):
    """Collect events by name within a short timeout."""
    deadline = time.time() + timeout_sec
    collected = []
    while time.time() < deadline:
        events = client.get_received()
        for evt in events:
            if evt.get('name') == event_name:
                collected.append(evt)
        if collected:
            break
        time.sleep(0.01)
    return collected


class CommandSender:
    def __init__(self, client):
        self.client = client
        self.counter = 0

    def send(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.counter += 1
        cid = self.counter
        payload = {
            'command_id': cid,
            'command': {
                'command': command,
                **params,
            }
        }
        self.client.emit('ui_command', payload)
        # Wait for ui_response with matching command_id
        deadline = time.time() + 2.0
        while time.time() < deadline:
            for evt in self.client.get_received():
                if evt.get('name') == 'ui_response':
                    data = evt.get('args', [{}])[0]
                    if data.get('command_id') == cid:
                        return data
            time.sleep(0.01)
        raise TimeoutError('Timed out waiting for ui_response')


def test_connect_receives_connection_response():
    client = make_client()
    events = drain_events(client, 'connection_response')
    assert events, 'No connection_response received'
    data = events[0]['args'][0]
    assert data.get('status') == 'connected'


def test_create_circle_and_scene_updated():
    client = make_client()
    sender = CommandSender(client)

    obj_id = 'circle_test_1'
    resp = sender.send('create_circle', {
        'obj_id': obj_id,
        'center_x': 0,
        'center_y': 0,
        'radius': 1.0,
        'style': {'stroke': '#f00'}
    })
    assert resp.get('success') is True, resp
    assert resp.get('result', {}).get('obj_id') == obj_id

    # Should receive scene_updated broadcast with object IDs array
    updates = drain_events(client, 'scene_updated')
    assert updates, 'No scene_updated broadcast received'
    upd = updates[-1]['args'][0]
    assert isinstance(upd.get('objects'), list)
    assert obj_id in upd.get('objects')


def test_get_object_data_curve():
    client = make_client()
    sender = CommandSender(client)

    obj_id = 'circle_data_1'
    sender.send('create_circle', {
        'obj_id': obj_id,
        'center_x': 1,
        'center_y': 2,
        'radius': 1.2,
    })

    # Request object data
    client.emit('get_object_data', {
        'obj_id': obj_id,
        'type': 'curve',
        'resolution': 50,
    })

    events = drain_events(client, 'object_data_response')
    assert events, 'No object_data_response received'
    data = events[-1]['args'][0]
    assert data.get('success') is True, data
    assert data.get('obj_id') == obj_id
    assert data.get('type') == 'curve'
    # Data structure presence (shape depends on backend; just ensure dict)
    assert isinstance(data.get('data'), dict)


def test_update_parameter_and_broadcast():
    client = make_client()
    sender = CommandSender(client)

    obj_id = 'circle_update_1'
    sender.send('create_circle', {
        'obj_id': obj_id,
        'center_x': 0,
        'center_y': 0,
        'radius': 1.0,
    })

    resp = sender.send('update_parameter', {
        'obj_id': obj_id,
        'parameter': 'radius',
        'value': 2.0,
    })
    assert resp.get('success') is True, resp
    # Should broadcast scene_updated after modification
    updates = drain_events(client, 'scene_updated')
    assert updates, 'No scene_updated after update_parameter'


def test_set_style_and_clear_scene():
    client = make_client()
    sender = CommandSender(client)

    obj_id = 'circle_style_1'
    sender.send('create_circle', {
        'obj_id': obj_id,
        'center_x': 0,
        'center_y': 0,
        'radius': 1.0,
    })

    resp = sender.send('set_style', {
        'obj_id': obj_id,
        'style': {'stroke': '#00f', 'fill': '#ccf'}
    })
    assert resp.get('success') is True, resp

    resp2 = sender.send('clear_scene', {})
    assert resp2.get('success') is True, resp2

    updates = drain_events(client, 'scene_updated')
    assert updates, 'No scene_updated after clear_scene'
    upd = updates[-1]['args'][0]
    assert upd.get('objects') == []
