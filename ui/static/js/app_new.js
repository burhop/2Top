/**
 * 2Top Geometry Library - Main Application
 * Initializes and coordinates all UI components
 */

// Initialize UI client and components
const uiClient = new UIClient();
const canvasRenderer = new CanvasRenderer('renderCanvas');
const objectBrowser = new ObjectBrowser('objectList');
const propertyPanel = new PropertyPanel('propertyPanel');
const animationControls = new AnimationControls('animationControls');

// Global state
let currentTool = 'select';
let objectCounter = 0;

// Connect to UI server
uiClient.connect();

// UI Client event handlers
uiClient.on('connected', () => {
    showNotification('Connected to server', 'success');
    updateConnectionStatus(true);
});

uiClient.on('disconnected', () => {
    showNotification('Disconnected from server', 'warning');
    updateConnectionStatus(false);
});

uiClient.on('scene_updated', (data) => {
    console.log('Scene updated:', data);
    objectBrowser.updateObjects(data.objects);
    
    // Request data for all objects to update visualization
    data.objects.forEach(objId => {
        requestObjectData(objId);
    });
});

uiClient.on('object_data_response', (data) => {
    console.log('Received object data:', data);
    if (data.success && data.data) {
        // Add or update object in renderer
        canvasRenderer.addObject(data.obj_id, data.data);
        canvasRenderer.render();
    }
});

// Canvas event handlers
canvasRenderer.on('canvas_click', (data) => {
    handleCanvasClick(data);
});

canvasRenderer.on('object_selected', (objId) => {
    objectBrowser.selectObject(objId);
    propertyPanel.showObject(objId);
});

// Object browser event handlers
objectBrowser.on('object_selected', (objId) => {
    canvasRenderer.selectObject(objId);
    propertyPanel.showObject(objId);
});

objectBrowser.on('object_deleted', (objId) => {
    uiClient.deleteObject(objId)
        .then(() => {
            showNotification(`Deleted object ${objId}`, 'success');
        })
        .catch(err => {
            showNotification(`Failed to delete object: ${err.message}`, 'error');
        });
});

objectBrowser.on('object_visibility_changed', (objId, visible) => {
    canvasRenderer.setObjectVisibility(objId, visible);
});

// Property panel event handlers
propertyPanel.on('parameter_changed', (objId, parameter, value) => {
    uiClient.updateParameter(objId, parameter, value)
        .then(() => {
            requestObjectData(objId); // Refresh visualization
        })
        .catch(err => {
            showNotification(`Failed to update parameter: ${err.message}`, 'error');
        });
});

propertyPanel.on('style_changed', (objId, style) => {
    uiClient.setStyle(objId, style)
        .then(() => {
            requestObjectData(objId); // Refresh visualization
        })
        .catch(err => {
            showNotification(`Failed to update style: ${err.message}`, 'error');
        });
});

// Tool selection
document.querySelectorAll('.btn-tool').forEach(btn => {
    btn.addEventListener('click', (e) => {
        selectTool(e.target.dataset.tool);
    });
});

// Scene management
document.getElementById('new-scene-btn')?.addEventListener('click', () => newScene());
document.getElementById('load-scene-btn')?.addEventListener('click', () => loadScene());
document.getElementById('save-scene-btn')?.addEventListener('click', () => saveScene());

// Export functionality
document.getElementById('export-png-btn')?.addEventListener('click', () => exportToPNG());
document.getElementById('export-svg-btn')?.addEventListener('click', () => exportToSVG());

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey) {
        switch(e.key) {
            case 'n':
                e.preventDefault();
                newScene();
                break;
            case 's':
                e.preventDefault();
                saveScene();
                break;
            case 'o':
                e.preventDefault();
                loadScene();
                break;
        }
    } else {
        // Single-letter tool shortcuts
        switch(e.key.toLowerCase()) {
            case 's':
                selectTool('select');
                break;
            case 'c':
                selectTool('circle');
                break;
            case 'r':
                selectTool('rectangle');
                break;
            case 't':
                selectTool('triangle');
                break;
            case 'e':
                selectTool('ellipse');
                break;
            case 'l':
                selectTool('line');
                break;
        }
    }
});

// Functions
function selectTool(tool) {
    currentTool = tool;
    
    // Update UI
    document.querySelectorAll('.btn-tool').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-tool="${tool}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Update cursor
    const canvas = document.getElementById('renderCanvas');
    if (canvas) {
        canvas.style.cursor = tool === 'select' ? 'default' : 'crosshair';
    }
    
    showNotification(`Selected ${tool} tool`, 'info');
}

function handleCanvasClick(data) {
    if (currentTool === 'select') {
        return; // Selection handled by renderer
    }
    
    const worldPos = data.world;
    const objId = `${currentTool}_${++objectCounter}`;
    
    switch(currentTool) {
        case 'circle':
            uiClient.createCircle(objId, worldPos.x, worldPos.y, 0.5)
                .then(() => {
                    showNotification(`Created circle ${objId}`, 'success');
                })
                .catch(err => {
                    showNotification(`Failed to create circle: ${err.message}`, 'error');
                });
            break;
            
        case 'rectangle':
            uiClient.createRectangle(objId, worldPos.x - 1, worldPos.y - 0.75, 2, 1.5)
                .then(() => {
                    showNotification(`Created rectangle ${objId}`, 'success');
                })
                .catch(err => {
                    showNotification(`Failed to create rectangle: ${err.message}`, 'error');
                });
            break;
            
        case 'triangle':
            uiClient.createTriangle(objId, 
                worldPos.x, worldPos.y + 1,
                worldPos.x - 1, worldPos.y - 1,
                worldPos.x + 1, worldPos.y - 1)
                .then(() => {
                    showNotification(`Created triangle ${objId}`, 'success');
                })
                .catch(err => {
                    showNotification(`Failed to create triangle: ${err.message}`, 'error');
                });
            break;
            
        case 'ellipse':
            uiClient.createEllipse(objId, worldPos.x, worldPos.y, 1.5, 1)
                .then(() => {
                    showNotification(`Created ellipse ${objId}`, 'success');
                })
                .catch(err => {
                    showNotification(`Failed to create ellipse: ${err.message}`, 'error');
                });
            break;
            
        case 'line':
            uiClient.createLine(objId, worldPos.x - 1, worldPos.y, worldPos.x + 1, worldPos.y)
                .then(() => {
                    showNotification(`Created line ${objId}`, 'success');
                })
                .catch(err => {
                    showNotification(`Failed to create line: ${err.message}`, 'error');
                });
            break;
    }
}

function requestObjectData(objId) {
    // Determine object type from ID
    let type = 'curve';
    if (objId.includes('rectangle') || objId.includes('triangle') || objId.includes('circle') || objId.includes('ellipse')) {
        type = 'region';
    }
    
    const bounds = canvasRenderer.getViewBounds();
    uiClient.socket.emit('get_object_data', {
        obj_id: objId,
        type: type,
        bounds: bounds,
        resolution: 100
    });
}

function newScene() {
    if (confirm('Create new scene? This will clear all current objects.')) {
        uiClient.clearScene()
            .then(() => {
                showNotification('New scene created', 'success');
                canvasRenderer.clear();
                objectBrowser.clear();
                propertyPanel.clear();
            })
            .catch(err => {
                showNotification(`Failed to create new scene: ${err.message}`, 'error');
            });
    }
}

function saveScene() {
    const filename = prompt('Enter filename for scene:');
    if (filename) {
        uiClient.saveScene(filename)
            .then(() => {
                showNotification(`Scene saved as ${filename}`, 'success');
            })
            .catch(err => {
                showNotification(`Failed to save scene: ${err.message}`, 'error');
            });
    }
}

function loadScene() {
    const filename = prompt('Enter filename to load:');
    if (filename) {
        uiClient.loadScene(filename)
            .then(() => {
                showNotification(`Scene loaded from ${filename}`, 'success');
            })
            .catch(err => {
                showNotification(`Failed to load scene: ${err.message}`, 'error');
            });
    }
}

function exportToPNG() {
    const canvas = document.getElementById('renderCanvas');
    const link = document.createElement('a');
    link.download = 'scene.png';
    link.href = canvas.toDataURL();
    link.click();
    showNotification('Exported to PNG', 'success');
}

function exportToSVG() {
    // TODO: Implement SVG export
    showNotification('SVG export not yet implemented', 'warning');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    const container = document.getElementById('notifications') || document.body;
    container.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = connected ? 'Connected' : 'Disconnected';
        statusElement.className = connected ? 'status-connected' : 'status-disconnected';
    }
}

// Initialize with select tool
selectTool('select');

console.log('2Top Geometry UI initialized');
