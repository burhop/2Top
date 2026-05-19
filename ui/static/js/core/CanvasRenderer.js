/**
 * 2Top Geometry Library - Canvas Renderer
 * Handles 2D canvas rendering of geometric objects
 */

class CanvasRenderer extends EventEmitter {
    constructor(canvas) {
        super();
        if (typeof canvas === 'string') {
            canvas = document.getElementById(canvas);
        }
        if (!canvas || typeof canvas.getContext !== 'function') {
            throw new Error('CanvasRenderer requires a canvas element or element id');
        }
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.viewport = {
            x: 0, y: 0,
            width: canvas.width,
            height: canvas.height,
            scale: 1.0
        };
        this.objects = new Map();
        this.selectedObjects = new Set();
        this.showGrid = true;
        this.showBounds = false;
        this.showAxes = true;
        this.showKeyPoints = true;
        this.intersections = [];
        this.showIntersections = true;
        this._fallbackBounds = { minX: -100, maxX: 100, minY: -100, maxY: 100 };
        
        this.setupEventHandlers();
        this.render();
    }

    setupEventHandlers() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        
        this.isDragging = false;
        this.lastMousePos = { x: 0, y: 0 };
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        this.lastMousePos = { x, y };
        this.isDragging = true;
        
        const worldPos = this.screenToWorld(x, y);
        this.emit('mouse_down', { screen: { x, y }, world: worldPos });
        e.preventDefault();
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const worldPos = this.screenToWorld(x, y);
        this.emit('mouse_move', { screen: { x, y }, world: worldPos });

        if (this.isDragging) {
            const dx = x - this.lastMousePos.x;
            const dy = y - this.lastMousePos.y;
            if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
                this._dragMoved = true;
            }
            this.viewport.x -= dx / this.viewport.scale;
            this.viewport.y += dy / this.viewport.scale;
            this.render();
            this._notifyViewportChanged();
            e.preventDefault();
        }

        this.lastMousePos = { x, y };
    }

    handleMouseUp(e) {
        const wasDragging = this._dragMoved;
        this.isDragging = false;
        this._dragMoved = false;
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const worldPos = this.screenToWorld(x, y);
        this.emit('mouse_up', { screen: { x, y }, world: worldPos });
        if (!wasDragging) {
            this.emit('canvas_click', { screen: { x, y }, world: worldPos });
        }
    }

    handleWheel(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const worldPos = this.screenToWorld(x, y);
        
        this.viewport.scale *= scaleFactor;
        this.viewport.scale = Math.max(0.001, Math.min(5000, this.viewport.scale));
        
        const newScreenPos = this.worldToScreen(worldPos.x, worldPos.y);
        this.viewport.x += (x - newScreenPos.x) / this.viewport.scale;
        this.viewport.y -= (y - newScreenPos.y) / this.viewport.scale;
        
        this.render();
        this._notifyViewportChanged();
        e.preventDefault();
    }

    screenToWorld(screenX, screenY) {
        return {
            x: (screenX - this.canvas.width / 2) / this.viewport.scale + this.viewport.x,
            y: -(screenY - this.canvas.height / 2) / this.viewport.scale + this.viewport.y
        };
    }

    worldToScreen(worldX, worldY) {
        return {
            x: (worldX - this.viewport.x) * this.viewport.scale + this.canvas.width / 2,
            y: -(worldY - this.viewport.y) * this.viewport.scale + this.canvas.height / 2
        };
    }

    resize(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;
        this.viewport.width = width;
        this.viewport.height = height;
        this.render();
    }

    addObject(id, objectData) {
        const existing = this.objects.get(id) || {};
        const merged = { ...existing, ...objectData };
        if (typeof merged.visible === 'undefined') {
            merged.visible = true;
        }
        if (!objectData || !('keyPoints' in objectData)) {
            merged.keyPoints = existing.keyPoints;
        }
        this.objects.set(id, merged);
        this.render();
    }

    removeObject(id) {
        this.objects.delete(id);
        this.selectedObjects.delete(id);
        this.render();
    }

    updateObject(id, objectData) {
        if (this.objects.has(id)) {
            const current = this.objects.get(id);
            const merged = { ...current, ...objectData };
            if (!objectData || !('keyPoints' in objectData)) {
                merged.keyPoints = current.keyPoints;
            }
            if (typeof merged.visible === 'undefined') {
                merged.visible = true;
            }
            this.objects.set(id, merged);
            this.render();
        }
    }

    loadGeometryScene(sceneData, autoFit = false) {
        if (!sceneData || !Array.isArray(sceneData.objects)) {
            return;
        }

        this.objects.clear();
        this.selectedObjects.clear();

        sceneData.objects.forEach((obj) => {
            const existing = this.objects.get(obj.id) || {};
            const merged = { ...existing };

            merged.type = obj.type || existing.type || 'curve';

            if (obj.paths && obj.paths.length > 0) {
                merged.data = { paths: obj.paths, closed: obj.closed };
            } else if (obj.points && obj.points.length > 1) {
                merged.data = { paths: [obj.points], closed: obj.closed };
            }

            merged.style = obj.style || existing.style || {};
            merged.bounds = obj.bounds || existing.bounds;
            merged.keyPoints = obj.key_points || existing.keyPoints || [];
            merged.visible = typeof existing.visible === 'boolean' ? existing.visible : true;

            this.objects.set(obj.id, merged);
        });

        this.intersections = sceneData.intersections || [];
        
        if (autoFit) {
            let bounds = sceneData.scene_bounds;
            if (!bounds || bounds.length !== 4 || !bounds.every(Number.isFinite)) {
                // Compute from object polylines
                let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                for (const obj of this.objects.values()) {
                    const paths = obj.data && obj.data.paths;
                    if (paths) {
                        for (const path of paths) {
                            for (const [px, py] of path) {
                                if (px < minX) minX = px;
                                if (px > maxX) maxX = px;
                                if (py < minY) minY = py;
                                if (py > maxY) maxY = py;
                            }
                        }
                    }
                }
                if (Number.isFinite(minX)) {
                    bounds = [minX, maxX, minY, maxY];
                }
            }
            this.fitToBounds(bounds, 1.15);
        } else {
            this.render();
        }
    }

    selectObject(id) {
        this.selectedObjects.clear();
        if (id && this.objects.has(id)) {
            this.selectedObjects.add(id);
        }
        this.render();
        this.emit('object_selected', id);
    }

    clearSelection() {
        if (this.selectedObjects.size === 0) return;
        this.selectedObjects.clear();
        this.render();
    }

    setObjectVisibility(id, visible) {
        if (!this.objects.has(id)) return;
        const obj = this.objects.get(id);
        obj.visible = Boolean(visible);
        this.objects.set(id, obj);
        this.render();
    }

    setGridVisibility(show) {
        this.showGrid = Boolean(show);
        this.render();
    }

    setKeyPointVisibility(show) {
        this.showKeyPoints = Boolean(show);
        this.render();
    }

    setIntersectionVisibility(show) {
        this.showIntersections = Boolean(show);
        this.render();
    }

    getObject(id) {
        return this.objects.get(id) || null;
    }

    _notifyViewportChanged() {
        this.emit('viewport_changed', {
            bounds: this.getViewBounds(),
            zoom: this.viewport.scale,
        });
    }

    fitToBounds(bounds, scaleFactor = 1.2) {
        if (!bounds || bounds.length !== 4) {
            bounds = [this._fallbackBounds.minX, this._fallbackBounds.maxX, this._fallbackBounds.minY, this._fallbackBounds.maxY];
        }

        let [minX, maxX, minY, maxY] = bounds.map((value) => (Number.isFinite(value) ? value : null));

        if (minX === null || maxX === null || minY === null || maxY === null) {
            minX = this._fallbackBounds.minX;
            maxX = this._fallbackBounds.maxX;
            minY = this._fallbackBounds.minY;
            maxY = this._fallbackBounds.maxY;
        }

        const width = Math.max(0.01, maxX - minX);
        const height = Math.max(0.01, maxY - minY);
        const paddedWidth = width * scaleFactor;
        const paddedHeight = height * scaleFactor;

        this.viewport.x = (minX + maxX) / 2;
        this.viewport.y = (minY + maxY) / 2;

        const scaleX = this.canvas.width / paddedWidth;
        const scaleY = this.canvas.height / paddedHeight;
        this.viewport.scale = Math.min(scaleX, scaleY, 5000);

        this.render();
        this._notifyViewportChanged();
    }

    setAxisVisibility(show) {
        this.showAxes = Boolean(show);
        this.render();
    }

    setIntersectionPoints(points) {
        this.intersections = points || [];
        this.render();
    }

    renderIntersections() {
        this.ctx.save();
        this.ctx.fillStyle = '#f94144';
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 1.5;
        this.ctx.shadowColor = 'rgba(249, 65, 68, 0.8)';
        this.ctx.shadowBlur = 12;
        this.intersections.forEach((point) => {
            const screen = this.worldToScreen(point.x, point.y);
            const radius = 7;
            this.ctx.beginPath();
            this.ctx.arc(screen.x, screen.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();

            this.ctx.save();
            this.ctx.shadowBlur = 0;
            this.ctx.fillStyle = '#f8fbff';
            this.ctx.strokeStyle = 'rgba(5, 6, 10, 0.85)';
            this.ctx.lineWidth = 3;
            this.ctx.font = '12px "Space Grotesk", sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.beginPath();
            this.ctx.arc(screen.x, screen.y - 12, radius - 3, 0, Math.PI * 2);
            this.ctx.stroke();
            this.ctx.fillText(point.label || '', screen.x, screen.y - 9);
            this.ctx.restore();
        });
        this.ctx.restore();
    }

    render() {
        this.ctx.fillStyle = '#06080f';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.save();
        this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.scale(this.viewport.scale, -this.viewport.scale);
        this.ctx.translate(-this.viewport.x, -this.viewport.y);

        if (this.showGrid) {
            this.renderGrid();
        }

        if (this.showAxes) {
            this.renderAxes();
        }

        for (const [id, obj] of this.objects) {
            this.renderObject(id, obj);
        }

        this.ctx.restore();

        if (this.showIntersections && this.intersections.length > 0) {
            this.renderIntersections();
        }

        if (this.showAxes) {
            this.renderAxisLabels();
        }
    }

    renderGrid() {
        const gridSize = this.getGridSize();
        const bounds = this.getViewBounds();
        
        this.ctx.strokeStyle = 'rgba(255,255,255,0.07)';
        this.ctx.lineWidth = 0.5 / this.viewport.scale;
        this.ctx.beginPath();

        for (let x = Math.floor(bounds.minX / gridSize) * gridSize; x <= bounds.maxX; x += gridSize) {
            this.ctx.moveTo(x, bounds.minY);
            this.ctx.lineTo(x, bounds.maxY);
        }

        for (let y = Math.floor(bounds.minY / gridSize) * gridSize; y <= bounds.maxY; y += gridSize) {
            this.ctx.moveTo(bounds.minX, y);
            this.ctx.lineTo(bounds.maxX, y);
        }

        this.ctx.stroke();
    }

    renderAxes() {
        const bounds = this.getViewBounds();
        const step = this.getAxisStep();
        const axisLineWidth = 1.25 / this.viewport.scale;
        const accent = 'rgba(255,255,255,0.6)';
        const tickLength = 6 / this.viewport.scale;

        this.ctx.save();
        this.ctx.strokeStyle = accent;
        this.ctx.lineWidth = axisLineWidth;

        // X-axis
        if (bounds.minY <= 0 && bounds.maxY >= 0) {
            this.ctx.beginPath();
            this.ctx.moveTo(bounds.minX, 0);
            this.ctx.lineTo(bounds.maxX, 0);
            this.ctx.stroke();

            for (let x = Math.ceil(bounds.minX / step) * step; x <= bounds.maxX; x += step) {
                this.ctx.beginPath();
                this.ctx.moveTo(x, -tickLength / 2);
                this.ctx.lineTo(x, tickLength / 2);
                this.ctx.stroke();
            }
        }

        // Y-axis
        if (bounds.minX <= 0 && bounds.maxX >= 0) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, bounds.minY);
            this.ctx.lineTo(0, bounds.maxY);
            this.ctx.stroke();

            for (let y = Math.ceil(bounds.minY / step) * step; y <= bounds.maxY; y += step) {
                this.ctx.beginPath();
                this.ctx.moveTo(-tickLength / 2, y);
                this.ctx.lineTo(tickLength / 2, y);
                this.ctx.stroke();
            }
        }

        this.ctx.restore();
    }

    renderAxisLabels() {
        const bounds = this.getViewBounds();
        const step = this.getAxisStep();
        const minPixelSpacing = 45;
        const originScreen = this.worldToScreen(0, 0);
        const stepScreenX = this.worldToScreen(step, 0);
        const stepScreenY = this.worldToScreen(0, step);
        const spacingX = Math.abs(stepScreenX.x - originScreen.x) || 1;
        const spacingY = Math.abs(stepScreenY.y - originScreen.y) || 1;
        const skipX = Math.max(1, Math.ceil(minPixelSpacing / spacingX));
        const skipY = Math.max(1, Math.ceil(minPixelSpacing / spacingY));

        this.ctx.save();
        this.ctx.fillStyle = 'rgba(255,255,255,0.8)';
        this.ctx.font = '12px "Space Grotesk", sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';

        if (bounds.minY <= 0 && bounds.maxY >= 0) {
            let labelIndex = 0;
            for (let x = Math.ceil(bounds.minX / step) * step; x <= bounds.maxX; x += step) {
                if (Math.abs(x) < 1e-6) {
                    labelIndex++;
                    continue;
                }
                if (labelIndex % skipX !== 0) {
                    labelIndex++;
                    continue;
                }
                const screen = this.worldToScreen(x, -step * 0.2);
                this.ctx.fillText(this.formatAxisValue(x), screen.x, screen.y);
                labelIndex++;
            }
        }

        if (bounds.minX <= 0 && bounds.maxX >= 0) {
            this.ctx.textAlign = 'right';
            this.ctx.textBaseline = 'middle';
            let labelIndex = 0;
            for (let y = Math.ceil(bounds.minY / step) * step; y <= bounds.maxY; y += step) {
                if (Math.abs(y) < 1e-6) {
                    labelIndex++;
                    continue;
                }
                if (labelIndex % skipY !== 0) {
                    labelIndex++;
                    continue;
                }
                const screen = this.worldToScreen(step * 0.2, y);
                this.ctx.fillText(this.formatAxisValue(y), screen.x - 4, screen.y);
                labelIndex++;
            }
        }

        // Origin label
        if (bounds.minX <= 0 && bounds.maxX >= 0 && bounds.minY <= 0 && bounds.maxY >= 0) {
            this.ctx.textAlign = 'left';
            this.ctx.textBaseline = 'top';
            const origin = this.worldToScreen(0, 0);
            this.ctx.fillText('0', origin.x + 4, origin.y + 4);
        }

        this.ctx.restore();
    }

    formatAxisValue(value) {
        if (Math.abs(value) >= 1000) {
            return value.toExponential(1);
        }
        if (Math.abs(value) < 1) {
            return value.toFixed(2);
        }
        return value.toFixed(0);
    }

    getGridSize() {
        // Target ~60-120px between grid lines regardless of zoom
        const targetPx = 80;
        const rawStep = targetPx / this.viewport.scale;
        // Snap to a nice number: 1, 2, 5, 10, 20, 50, 100 ...
        const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
        const normalized = rawStep / magnitude;
        let nice;
        if (normalized < 1.5) nice = 1;
        else if (normalized < 3.5) nice = 2;
        else if (normalized < 7.5) nice = 5;
        else nice = 10;
        return nice * magnitude;
    }

    getAxisStep() {
        return this.getGridSize();
    }

    fitAllObjects() {
        if (this.objects.size === 0) {
            this.fitToBounds([-5, 5, -5, 5]);
            return;
        }
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        for (const obj of this.objects.values()) {
            const paths = obj.data && obj.data.paths;
            if (!paths) continue;
            for (const path of paths) {
                for (const [px, py] of path) {
                    if (!isFinite(px) || !isFinite(py)) continue;
                    if (px < minX) minX = px;
                    if (px > maxX) maxX = px;
                    if (py < minY) minY = py;
                    if (py > maxY) maxY = py;
                }
            }
        }
        if (!isFinite(minX)) { this.fitToBounds([-5, 5, -5, 5]); return; }
        this.fitToBounds([minX, maxX, minY, maxY], 1.2);
    }

    getViewBounds() {
        const halfWidth = this.canvas.width / (2 * this.viewport.scale);
        const halfHeight = this.canvas.height / (2 * this.viewport.scale);
        
        return {
            minX: this.viewport.x - halfWidth,
            maxX: this.viewport.x + halfWidth,
            minY: this.viewport.y - halfHeight,
            maxY: this.viewport.y + halfHeight
        };
    }

    renderObject(id, obj) {
        if (!obj.data || obj.visible === false) return;

        this.ctx.save();
        
        const style = obj.style || {};
        this.ctx.strokeStyle = style.color || '#667eea';
        this.ctx.fillStyle = style.fillColor || 'rgba(102, 126, 234, 0.3)';
        this.ctx.lineWidth = (style.lineWidth || 2) / this.viewport.scale;

        if (obj.type === 'curve' && obj.data.paths) {
            this.renderCurvePaths(obj.data.paths);
        } else if (obj.type === 'region' && obj.data.boundary) {
            this.renderRegion(obj.data);
        }

        if (this.showKeyPoints && obj.keyPoints && obj.keyPoints.length > 0) {
            this.renderKeyPoints(obj.keyPoints, style);
        }

        if (this.selectedObjects.has(id)) {
            this.renderSelection(obj);
        }

        this.ctx.restore();
    }

    renderKeyPoints(points, style) {
        const radius = 5 / this.viewport.scale;
        const fill = style.color || '#ff6b6b';

        this.ctx.save();
        this.ctx.fillStyle = fill;
        this.ctx.strokeStyle = '#0d1b2a';
        this.ctx.lineWidth = 1 / this.viewport.scale;

        points.forEach((point) => {
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();

            const screenPos = this.worldToScreen(point.x, point.y);
            this.ctx.save();
            this.ctx.setTransform(1, 0, 0, 1, 0, 0);
            this.ctx.fillStyle = '#0d1b2a';
            this.ctx.font = '12px "Space Grotesk", sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(point.label || point.type || '', screenPos.x, screenPos.y - 14);
            this.ctx.restore();
        });

        this.ctx.restore();
    }

    renderCurvePaths(paths) {
        for (const path of paths) {
            if (path.length < 2) continue;
            
            this.ctx.beginPath();
            this.ctx.moveTo(path[0][0], path[0][1]);
            
            for (let i = 1; i < path.length; i++) {
                this.ctx.lineTo(path[i][0], path[i][1]);
            }
            
            this.ctx.stroke();
        }
    }

    renderRegion(data) {
        if (data.inside_points && data.inside_points.length > 0) {
            const pointSize = 1 / this.viewport.scale;
            for (const point of data.inside_points) {
                this.ctx.fillRect(point[0] - pointSize/2, point[1] - pointSize/2, pointSize, pointSize);
            }
        }
        
        if (data.boundary && data.boundary.length > 0) {
            this.renderCurvePaths([data.boundary]);
        }
    }

    renderSelection(obj) {
        this.ctx.strokeStyle = '#ff6b6b';
        this.ctx.lineWidth = 2 / this.viewport.scale;
        this.ctx.setLineDash([5 / this.viewport.scale, 5 / this.viewport.scale]);
        
        if (obj.bounds) {
            const [minX, maxX, minY, maxY] = obj.bounds;
            this.ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
        }
        
        this.ctx.setLineDash([]);
    }

    setViewOptions(options) {
        if (options.showGrid !== undefined) this.showGrid = options.showGrid;
        if (options.showBounds !== undefined) this.showBounds = options.showBounds;
        this.render();
    }

    fitToObjects() {
        if (this.objects.size === 0) return;
        
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        
        for (const [id, obj] of this.objects) {
            if (obj.bounds) {
                const [objMinX, objMaxX, objMinY, objMaxY] = obj.bounds;
                minX = Math.min(minX, objMinX);
                maxX = Math.max(maxX, objMaxX);
                minY = Math.min(minY, objMinY);
                maxY = Math.max(maxY, objMaxY);
            }
        }
        
        if (isFinite(minX) && isFinite(maxX) && isFinite(minY) && isFinite(maxY)) {
            const width = maxX - minX;
            const height = maxY - minY;
            const padding = 0.1;
            
            this.viewport.x = (minX + maxX) / 2;
            this.viewport.y = (minY + maxY) / 2;
            
            const scaleX = this.canvas.width / (width * (1 + padding));
            const scaleY = this.canvas.height / (height * (1 + padding));
            this.viewport.scale = Math.min(scaleX, scaleY, 10);
            
            this.render();
        }
    }

    clear() {
        this.objects.clear();
        this.selectedObjects.clear();
        this.intersections = [];
        this.render();
    }
}
