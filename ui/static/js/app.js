/**
 * 2Top Geometry Library - Main Application
 * Initializes and coordinates all UI components
 */

// Initialize UI client and components
const uiClient = new UIClient();
const canvasRenderer = new CanvasRenderer('renderCanvas');
const objectBrowser = new ObjectBrowser(document.getElementById('objectList'));
const propertyPanel = new PropertyPanel(document.getElementById('property-panel'));
const animationControls = new AnimationControls(document.getElementById('animationControls'));
const geometryStudio = window.GeometryStudio ? new GeometryStudio({ canvasRenderer, uiClient }) : null;

// Global state
let currentTool = 'select';
let objectCounter = 0;
let isLoadingActive = false;

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
    if (isLoadingActive) {
        // Skip updating UI components while bulk curve loading is active to prevent race conditions
        return;
    }
    objectBrowser.updateObjects(data.objects);
    // Single fetch replaces N per-object socket calls
    geometryStudio?.refreshSceneData();
    
    // Hide verification panel if there are no database curves loaded and we're not in periodic mode
    if (data.objects && !data.objects.some(id => id.startsWith('db_curve_')) && (!geometryStudio || geometryStudio.suite !== 'periodic')) {
        document.getElementById('db-verification-panel')?.classList.add('hidden');
    }
});


// Canvas event handlers
canvasRenderer.on('canvas_click', (data) => {
    handleCanvasClick(data);
});

canvasRenderer.on('object_selected', (objId) => {
    objectBrowser.setSelectedObject(objId);
    const objectData = objId ? canvasRenderer.getObject(objId) : null;
    if (objId && objectData) {
        propertyPanel.setObject(objId, objectData);
    } else {
        propertyPanel.clear();
    }
});

// Object browser event handlers
objectBrowser.on('object_selected', (objId) => {
    canvasRenderer.selectObject(objId);
    const objectData = objId ? canvasRenderer.getObject(objId) : null;
    if (objId && objectData) {
        propertyPanel.setObject(objId, objectData);
    } else {
        propertyPanel.clear();
    }
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
        .then(() => geometryStudio?.refreshSceneData())
        .catch(err => showNotification(`Failed to update parameter: ${err.message}`, 'error'));
});

propertyPanel.on('style_changed', (objId, style) => {
    uiClient.setStyle(objId, style)
        .then(() => geometryStudio?.refreshSceneData())
        .catch(err => showNotification(`Failed to update style: ${err.message}`, 'error'));
});

// Shape creation buttons — create immediately at viewport center
const CREATE_TOOLS = new Set(['circle','ellipse','line','rectangle','triangle','parabola','hyperbola','cubic','periodic']);
document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tool = e.currentTarget.dataset.tool;
        if (!tool) return;
        if (CREATE_TOOLS.has(tool)) {
            createShapeAtCenter(tool);
        } else {
            selectTool(tool);
        }
    });
});

// Scene management
document.getElementById('fit-btn')?.addEventListener('click', () => canvasRenderer.fitAllObjects());
document.getElementById('new-scene-btn')?.addEventListener('click', () => newScene());
document.getElementById('load-scene-btn')?.addEventListener('click', () => loadScene());
document.getElementById('save-scene-btn')?.addEventListener('click', () => saveScene());

// Database curves controls
document.getElementById('load-db-curve-btn')?.addEventListener('click', () => loadDBCurve());
document.getElementById('load-db-group-btn')?.addEventListener('click', () => loadDBGroup());
document.getElementById('verify-scene-btn')?.addEventListener('click', () => verifyScene(false));
document.getElementById('close-verification-panel')?.addEventListener('click', () => {
    document.getElementById('db-verification-panel')?.classList.add('hidden');
});

// Export functionality
document.getElementById('export-png-btn')?.addEventListener('click', () => exportToPNG());
document.getElementById('export-svg-btn')?.addEventListener('click', () => exportToSVG());

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (isLoadingActive) return; // Block all keyboard shortcuts while loading curves
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
            case 'f':
                canvasRenderer.fitAllObjects();
                break;
        }
    }
});

// Functions
function selectTool(tool) {
    currentTool = tool;
    
    document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tool === tool);
    });
    
    const canvas = document.getElementById('renderCanvas');
    if (canvas) {
        canvas.style.cursor = tool === 'select' ? 'default' : 'crosshair';
    }
}

function createShapeAtCenter(tool) {
    const vp = canvasRenderer.viewport;
    // Jitter by up to 15% of visible span so repeated shapes don't stack
    const bounds = canvasRenderer.getViewBounds();
    const span = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY);
    const jitterScale = span * 0.15;
    const cx = vp.x + (Math.random() - 0.5) * jitterScale;
    const cy = vp.y + (Math.random() - 0.5) * jitterScale;
    const r = span * 0.15;
    const objId = `${tool}_${Date.now().toString(36)}_${(Math.random()*0xffff|0).toString(16)}`;

    let promise;
    switch (tool) {
        case 'circle':
            promise = uiClient.createCircle(objId, cx, cy, r);
            break;
        case 'ellipse':
            promise = uiClient.createEllipse(objId, cx, cy, r * 1.5, r);
            break;
        case 'line':
            promise = uiClient.createLine(objId, cx - r, cy, cx + r, cy);
            break;
        case 'rectangle':
            promise = uiClient.createRectangle(objId, cx - r, cy - r * 0.6, r * 2, r * 1.2);
            break;
        case 'triangle':
            promise = uiClient.createTriangle(objId,
                cx, cy + r,
                cx - r, cy - r,
                cx + r, cy - r);
            break;
        case 'parabola':
            promise = uiClient.sendCommand('create_parabola', { obj_id: objId, vertex_x: cx, vertex_y: cy, scale: 1 / Math.max(r, 0.1), direction: 'up' });
            break;
        case 'hyperbola':
            promise = uiClient.sendCommand('create_hyperbola', { obj_id: objId, center_x: cx, center_y: cy, a: r * 0.8, b: r * 0.6 });
            break;
        case 'cubic':
            promise = uiClient.sendCommand('create_cubic', { obj_id: objId, center_x: cx, center_y: cy, scale: 1 / Math.max(r, 0.1) });
            break;
        case 'periodic':
            promise = uiClient.sendCommand('create_periodic', { obj_id: objId, center_x: cx, center_y: cy, scale: 1 / Math.max(r, 0.1) });
            break;
        default:
            return;
    }
    promise
        .then(() => showNotification(`Created ${tool}`, 'success'))
        .catch(err => showNotification(`Failed: ${err.message}`, 'error'));
}

function handleCanvasClick(data) {
    // Canvas click reserved for future select/pick interactions
}

function newScene() {
    uiClient.clearScene()
        .then(() => {
            canvasRenderer.clear();
            objectBrowser.clear();
            propertyPanel.clear();
            geometryStudio?.refreshSceneData();
            showNotification('Scene cleared', 'success');
        })
        .catch(err => {
            showNotification(`Failed to clear scene: ${err.message}`, 'error');
        });
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
                geometryStudio?.refreshSceneData();
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
        statusElement.textContent = connected ? 'connected' : 'offline';
    }
    const countEl = document.getElementById('object-count');
    if (countEl && connected) {
        countEl.textContent = `${objectBrowser.objects.size} obj`;
    }
}

// Resize canvas to fill canvas-wrap
function resizeCanvas() {
    const wrap = document.querySelector('.canvas-wrap');
    const canvas = document.getElementById('renderCanvas');
    if (!wrap || !canvas) return;
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
        canvasRenderer.resize(w, h);
    }
}
window.addEventListener('resize', resizeCanvas);
requestAnimationFrame(resizeCanvas);

// Initialize with select tool
selectTool('select');

console.log('2Top Geometry UI initialized');

// ── Database Curves Loading & Verification Helpers ──

function showLoadingOverlay(title, initialStatus) {
    const overlay = document.getElementById('loading-overlay');
    const titleEl = document.getElementById('loading-title');
    const statusEl = document.getElementById('loading-status');
    const fillEl = document.getElementById('loading-progress-fill');
    
    if (overlay) overlay.classList.add('visible');
    if (titleEl) titleEl.textContent = title;
    if (statusEl) statusEl.textContent = initialStatus;
    if (fillEl) fillEl.style.width = '0%';
}

function updateLoadingProgress(status, percent) {
    const statusEl = document.getElementById('loading-status');
    const fillEl = document.getElementById('loading-progress-fill');
    
    if (statusEl) statusEl.textContent = status;
    if (fillEl) fillEl.style.width = `${percent}%`;
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('visible');
}

async function loadDBCurve() {
    const input = document.getElementById('db-curve-id');
    const btn = document.getElementById('load-db-curve-btn');
    if (!input || !btn) return;
    
    const val = input.value.trim();
    if (!val) {
        showNotification('Please enter a Curve ID', 'warning');
        return;
    }
    
    const curveId = parseInt(val, 10);
    if (isNaN(curveId) || curveId < 0) {
        showNotification('Curve ID must be a non-negative integer', 'warning');
        return;
    }
    
    isLoadingActive = true;
    showLoadingOverlay(`Loading Curve #${curveId}`, 'Contacting server...');
    updateLoadingProgress('Loading database record...', 30);
    
    try {
        const res = await fetch('/api/db/curves/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ curve_id: curveId })
        });
        const payload = await res.json();
        
        if (!payload.success) {
            throw new Error(payload.error || 'Failed to load curve');
        }
        
        updateLoadingProgress('Successfully loaded. Initializing canvas...', 100);
        showNotification(`Curve #${curveId} loaded successfully`, 'success');
        input.value = '';
        
        // Render scene once
        if (geometryStudio) {
            await geometryStudio.refreshSceneData();
        }
        canvasRenderer.fitAllObjects();
        
        
        
    } catch (err) {
        console.error('Failed to load curve', err);
        showNotification(err.message, 'error');
    } finally {
        setTimeout(() => {
            hideLoadingOverlay();
            isLoadingActive = false;
        }, 300); // 300ms delay to let the transition finish beautifully
    }
}

async function loadDBGroup() {
    const input = document.getElementById('db-group-id');
    const btn = document.getElementById('load-db-group-btn');
    if (!input || !btn) return;
    
    const val = input.value.trim();
    if (!val) {
        showNotification('Please enter a Group ID', 'warning');
        return;
    }
    
    const groupId = parseInt(val, 10);
    if (isNaN(groupId) || groupId < 0) {
        showNotification('Group ID must be a non-negative integer', 'warning');
        return;
    }
    
    isLoadingActive = true;
    showLoadingOverlay(`Loading Spatial Group #${groupId}`, 'Fetching group metadata...');
    
    try {
        // Step 1: Discover the curves in this group
        const discoverRes = await fetch(`/api/db/groups/${groupId}/curves`);
        const discoverPayload = await discoverRes.json();
        
        if (!discoverPayload.success) {
            throw new Error(discoverPayload.error || `Group #${groupId} metadata fetch failed`);
        }
        
        const curveIds = discoverPayload.curve_ids;
        if (!curveIds || curveIds.length === 0) {
            throw new Error(`Spatial Group #${groupId} has no registered curves.`);
        }
        
        const total = curveIds.length;
        updateLoadingProgress(`Found ${total} curves. Initializing...`, 10);
        
        // Step 2: Fetch and load each curve sequentially to update progress bar
        for (let i = 0; i < total; i++) {
            const curveId = curveIds[i];
            const pct = Math.round(10 + ((i + 1) / total) * 80); // Scaled from 10% to 90%
            updateLoadingProgress(`Loading curve ${i + 1} of ${total} (ID #${curveId})...`, pct);
            
            const loadRes = await fetch('/api/db/curves/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ curve_id: curveId })
            });
            const loadPayload = await loadRes.json();
            
            if (!loadPayload.success) {
                throw new Error(loadPayload.error || `Failed to load curve #${curveId} in group`);
            }
        }
        
        updateLoadingProgress('Successfully loaded all curves. Initializing canvas...', 95);
        showNotification(`Spatial Group #${groupId} loaded successfully (${total} curves)`, 'success');
        input.value = '';
        
        // Step 3: Trigger a single canvas redraw and viewport zoom
        if (geometryStudio) {
            await geometryStudio.refreshSceneData();
        }
        canvasRenderer.fitAllObjects();
        
        // Step 4: Finished loading all curves successfully
        updateLoadingProgress('Finished loading all curves.', 100);
        
    } catch (err) {
        console.error('Failed to load spatial group', err);
        showNotification(err.message, 'error');
    } finally {
        setTimeout(() => {
            hideLoadingOverlay();
            isLoadingActive = false;
        }, 500); // Elegantly fade out the overlay after loading finishes
    }
}

async function verifyScene(isBackground = false) {
    const verifyBtn = document.getElementById('verify-scene-btn');
    if (!isBackground && verifyBtn) {
        verifyBtn.disabled = true;
        verifyBtn.style.opacity = '0.7';
    }
    
    try {
        const res = await fetch('/api/db/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const payload = await res.json();
        
        if (!payload.success && payload.error) {
            if (!isBackground) {
                showNotification(`Verification error: ${payload.error}`, 'error');
            }
            return;
        }
        
        const panel = document.getElementById('db-verification-panel');
        if (!panel) return;
        
        if (payload.verified === false) {
            // No DB curves in scene to verify
            if (!isBackground) {
                showNotification('No database curves in scene to verify.', 'info');
            }
            panel.classList.add('hidden');
            return;
        }
        
        // Update summary
        const summaryDiv = document.getElementById('verification-summary');
        if (summaryDiv) {
            if (payload.success) {
                summaryDiv.innerHTML = `
                    <div class="v-badge v-badge-success">
                        <span class="v-badge-icon">🛡️</span>
                        <div class="v-badge-text">
                            <strong>VERIFIED</strong><br>Calculations match database ground truth perfectly!
                        </div>
                    </div>
                `;
            } else {
                summaryDiv.innerHTML = `
                    <div class="v-badge v-badge-error">
                        <span class="v-badge-icon">⚠️</span>
                        <div class="v-badge-text">
                            <strong>COORDINATE MISMATCH</strong><br>Calculated coordinates differ from database ground truth.
                        </div>
                    </div>
                `;
            }
        }
        
        // Update details
        const detailsDiv = document.getElementById('verification-details');
        if (detailsDiv) {
            let html = '';
            
            // Endpoints section
            if (payload.endpoints && payload.endpoints.length > 0) {
                html += `<div class="v-section-title">Endpoints</div>`;
                html += `<div class="v-item-list">`;
                payload.endpoints.forEach(item => {
                    const statusClass = item.status.toLowerCase(); // 'match' or 'mismatch' or 'error'
                    html += `
                        <div class="v-item ${statusClass}">
                            <div class="v-item-meta">
                                <span class="v-item-id">Curve #${item.db_id}</span>
                                <span class="v-item-status-label">${item.status}</span>
                            </div>
                            <div class="v-item-msg">${item.message}</div>
                    `;
                    if (item.status === 'MISMATCH') {
                        html += `
                            <div class="v-item-diff">DB:   ${JSON.stringify(item.db_endpoints)}\nCalc: ${JSON.stringify(item.calculated_endpoints)}</div>
                        `;
                    }
                    html += `</div>`;
                });
                html += `</div>`;
            }
            
            // Intersections section
            if (payload.intersections && payload.intersections.length > 0) {
                if (payload.endpoints && payload.endpoints.length > 0) {
                    html += `<div style="height: 8px;"></div>`;
                }
                html += `<div class="v-section-title">Intersections</div>`;
                html += `<div class="v-item-list">`;
                payload.intersections.forEach(item => {
                    const statusClass = item.status.toLowerCase(); // 'match' or 'mismatch' or 'error'
                    html += `
                        <div class="v-item ${statusClass}">
                            <div class="v-item-meta">
                                <span class="v-item-id">Curve #${item.curve_a_id} & #${item.curve_b_id}</span>
                                <span class="v-item-status-label">${item.status}</span>
                            </div>
                            <div class="v-item-msg">${item.message}</div>
                    `;
                    if (item.status === 'MISMATCH') {
                        html += `
                            <div class="v-item-diff">Relation: ${item.relation_type}\nDB:   ${JSON.stringify(item.db_intersections)}\nCalc: ${JSON.stringify(item.calculated_intersections)}</div>
                        `;
                    }
                    html += `</div>`;
                });
                html += `</div>`;
            }
            
            if (!payload.endpoints?.length && !payload.intersections?.length) {
                html = `<div style="font-size:0.7rem; color:var(--muted); text-align:center; padding:10px 0;">No active DB curve relations.</div>`;
            }
            
            detailsDiv.innerHTML = html;
        }
        
        // Show panel if not background or if mismatch occurred in background (auto-open on error)
        if (!isBackground || !payload.success) {
            panel.classList.remove('hidden');
        }
        
    } catch (err) {
        console.error('Failed to verify scene', err);
        if (!isBackground) {
            showNotification(`Verification failed: ${err.message}`, 'error');
        }
    } finally {
        if (!isBackground && verifyBtn) {
            verifyBtn.disabled = false;
            verifyBtn.style.opacity = '1';
        }
    }
}
