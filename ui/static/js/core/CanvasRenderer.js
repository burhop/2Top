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
        this.showHeatmap = true;
        this.fields = [];
        this._fallbackBounds = { minX: -100, maxX: 100, minY: -100, maxY: 100 };
        this.fieldExtent = null;
        this.isExplicitFieldExtent = false;
        this.glowSliderValue = 10.0;
        
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
        this.fields = sceneData.fields || [];
        if (!this.isExplicitFieldExtent) {
            this.fieldExtent = null;
            this.glowSliderValue = 10.0;
        }

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

    setHeatmapVisibility(show) {
        this.showHeatmap = Boolean(show);
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
        this.intersections.forEach((point) => {
            const screen = this.worldToScreen(point.x, point.y);
            const radius = 5.5; // Slightly smaller, refined dot
            
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.arc(screen.x, screen.y, radius, 0, Math.PI * 2);
            this.ctx.fillStyle = point.color || '#ff4d6d'; // Premium bright neon rose/red or custom
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 1.5;
            this.ctx.shadowColor = point.color || 'rgba(255, 77, 109, 0.5)';
            this.ctx.shadowBlur = 6; // Refined, clean glow
            this.ctx.fill();
            this.ctx.stroke();
            this.ctx.restore();

            this.ctx.save();
            this.ctx.fillStyle = '#f8fbff'; // Clean off-white
            this.ctx.strokeStyle = 'rgba(5, 6, 10, 0.85)'; // High-contrast dark outline
            this.ctx.lineWidth = 3;
            this.ctx.font = 'bold 11px "Space Grotesk", sans-serif'; // Refined size
            this.ctx.textAlign = 'center';
            
            // Draw beautiful, clean text above the dot (at -14px) with high-contrast outline
            this.ctx.strokeText(point.label || '', screen.x, screen.y - 14);
            this.ctx.fillText(point.label || '', screen.x, screen.y - 14);
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

        if (this.showHeatmap) {
            this.renderHeatmaps();
        }

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

        if (bounds.minY <= 0 && bounds.maxY >= 0) {
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'top';
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
                const screen = this.worldToScreen(x, 0);
                this.ctx.fillText(this.formatAxisValue(x), screen.x, originScreen.y + 8);
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
                const screen = this.worldToScreen(0, y);
                this.ctx.fillText(this.formatAxisValue(y), originScreen.x - 8, screen.y);
                labelIndex++;
            }
        }

        // Origin label
        if (bounds.minX <= 0 && bounds.maxX >= 0 && bounds.minY <= 0 && bounds.maxY >= 0) {
            this.ctx.textAlign = 'left';
            this.ctx.textBaseline = 'top';
            this.ctx.fillText('0', originScreen.x + 4, originScreen.y + 4);
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
        if (!obj.data || obj.visible === false || obj.type === 'field') return;

        this.ctx.save();
        
        const style = obj.style || {};
        this.ctx.strokeStyle = style.color || '#667eea';
        this.ctx.fillStyle = style.fillColor || 'rgba(102, 126, 234, 0.3)';
        const rawWidth = style.lineWidth || style.linewidth || 2.5;
        this.ctx.lineWidth = Math.max(rawWidth / this.viewport.scale, 1.5 / this.viewport.scale);

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

        this.ctx.save();
        points.forEach((point) => {
            const fill = point.color || style.color || '#ff6b6b';
            this.ctx.fillStyle = fill;
            this.ctx.strokeStyle = '#0d1b2a';
            this.ctx.lineWidth = 1 / this.viewport.scale;
            
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();

            const screenPos = this.worldToScreen(point.x, point.y);
            this.ctx.save();
            this.ctx.setTransform(1, 0, 0, 1, 0, 0);
            this.ctx.fillStyle = '#f8fbff';
            this.ctx.strokeStyle = 'rgba(5, 6, 10, 0.85)';
            this.ctx.lineWidth = 3;
            this.ctx.font = '12px "Space Grotesk", sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.strokeText(point.label || point.type || '', screenPos.x, screenPos.y - 14);
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
        this.fieldExtent = null;
        this.isExplicitFieldExtent = false;
        this.glowSliderValue = 10.0;
        this.render();
    }

    renderHeatmaps() {
        if (!this.fields || this.fields.length === 0) return;
        
        if (this.glowSliderValue === undefined || this.glowSliderValue === null) {
            this.glowSliderValue = 10.0;
        }
        if (this.fieldExtent === null) {
            this.fieldExtent = (this.glowSliderValue / 100.0) * 20.0;
        }

        // Configure the glow slider range statically from 0 to 100
        const slider = document.getElementById('field-extent-slider');
        const label = document.getElementById('field-extent-val');
        if (slider) {
            slider.min = "0";
            slider.max = "100";
            slider.step = "1";
            slider.value = this.glowSliderValue;
        }
        if (label) {
            label.textContent = Math.round(this.glowSliderValue);
        }

        this.fields.forEach((field) => {
            if (field.error || !field.data || !field.bounds) return;
            
            const resolution = field.resolution;
            const bounds = field.bounds;
            const [xmin, xmax, ymin, ymax] = bounds;
            const vmin = field.vmin;
            const vmax = field.vmax;
            
            // Create an upscaled offscreen canvas for ultra-smooth grid interpolation
            const renderRes = 512;
            const offscreen = document.createElement('canvas');
            offscreen.width = renderRes;
            offscreen.height = renderRes;
            const octx = offscreen.getContext('2d');
            const imgData = octx.createImageData(renderRes, renderRes);
            const data = imgData.data;
            
            const dx = (xmax - xmin) / (resolution - 1 || 1);
            const dy = (ymax - ymin) / (resolution - 1 || 1);
            const vrange = vmax - vmin || 1e-9;
            
            const flippedData = [...field.data].reverse();

            // Bilinear grid interpolation to completely eliminate blocky pixels!
            const interpolateGrid = (grid, r, c) => {
                const r_idx = Math.floor(r);
                const c_idx = Math.floor(c);
                const r_next = Math.min(resolution - 1, r_idx + 1);
                const c_next = Math.min(resolution - 1, c_idx + 1);
                
                const tr = r - r_idx;
                const tc = c - c_idx;
                
                const v00 = grid[r_idx] ? grid[r_idx][c_idx] : null;
                const v01 = grid[r_idx] ? grid[r_idx][c_next] : null;
                const v10 = grid[r_next] ? grid[r_next][c_idx] : null;
                const v11 = grid[r_next] ? grid[r_next][c_next] : null;
                
                const w00 = (v00 !== null && v00 !== undefined && !isNaN(v00)) ? v00 : 0;
                const w01 = (v01 !== null && v01 !== undefined && !isNaN(v01)) ? v01 : w00;
                const w10 = (v10 !== null && v10 !== undefined && !isNaN(v10)) ? v10 : w00;
                const w11 = (v11 !== null && v11 !== undefined && !isNaN(v11)) ? v11 : w00;
                
                return (1 - tr) * ((1 - tc) * w00 + tc * w01) + tr * ((1 - tc) * w10 + tc * w11);
            };
            
            const dx_render = (xmax - xmin) / (renderRes - 1 || 1);
            const dy_render = (ymax - ymin) / (renderRes - 1 || 1);
            
            for (let r = 0; r < renderRes; r++) {
                const gridR = (r / (renderRes - 1)) * (resolution - 1);
                for (let c = 0; c < renderRes; c++) {
                    const gridC = (c / (renderRes - 1)) * (resolution - 1);
                    const val = interpolateGrid(flippedData, gridR, gridC);
                    const idx = (r * renderRes + c) * 4;
                    
                    if (val === null || val === undefined || isNaN(val)) {
                        data[idx] = 0;
                        data[idx + 1] = 0;
                        data[idx + 2] = 0;
                        data[idx + 3] = 0;
                    } else {
                        // Estimate distance to zero isoline in world units and compute fade multiplier
                        let fade = 1.0;
                        if (field.type !== 'OccupancyField') {
                            let d_world;
                            if (field.type === 'SignedDistanceField') {
                                d_world = Math.abs(val);
                            } else {
                                const prev_c = c > 0 ? c - 1 : c;
                                const next_c = c < renderRes - 1 ? c + 1 : c;
                                const prev_r = r > 0 ? r - 1 : r;
                                const next_r = r < renderRes - 1 ? r + 1 : r;
                                
                                const val_prev_c = interpolateGrid(flippedData, gridR, (prev_c / (renderRes - 1)) * (resolution - 1));
                                const val_next_c = interpolateGrid(flippedData, gridR, (next_c / (renderRes - 1)) * (resolution - 1));
                                const val_prev_r = interpolateGrid(flippedData, (prev_r / (renderRes - 1)) * (resolution - 1), gridC);
                                const val_next_r = interpolateGrid(flippedData, (next_r / (renderRes - 1)) * (resolution - 1), gridC);
                                
                                const df_dx = (val_next_c - val_prev_c) / (((next_c - prev_c) || 1) * dx_render);
                                const df_dy = (val_next_r - val_prev_r) / (((next_r - prev_r) || 1) * dy_render);
                                
                                const grad_norm = Math.sqrt(df_dx * df_dx + df_dy * df_dy);
                                d_world = Math.abs(val) / (grad_norm + 1e-6);
                            }
                            
                            if (this.fieldExtent !== null) {
                                const fade_start = 0.15 * this.fieldExtent;
                                const fade_end = this.fieldExtent;
                                if (d_world <= fade_start) {
                                    fade = 1.0;
                                } else if (d_world >= fade_end) {
                                    fade = 0.0;
                                } else {
                                    const u = (d_world - fade_start) / (fade_end - fade_start);
                                    fade = 0.5 + 0.5 * Math.cos(u * Math.PI);
                                }
                            }
                        }

                        // Normalize val to [0, 1]
                        const t = (val - vmin) / vrange;
                        const [colorR, colorG, colorB, colorA] = this.getColorForT(t, field.type);
                        data[idx] = colorR;
                        data[idx + 1] = colorG;
                        data[idx + 2] = colorB;
                        data[idx + 3] = Math.round(colorA * fade * 255);
                    }
                }
            }
            
            octx.putImageData(imgData, 0, 0);
            
            const screenMin = this.worldToScreen(xmin, ymax); // ymax is top of screen in world coordinates
            const screenMax = this.worldToScreen(xmax, ymin); // ymin is bottom of screen in world coordinates
            
            // Draw onto main canvas
            this.ctx.save();
            this.ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset transform to draw in screen pixel coordinates
            this.ctx.drawImage(offscreen, screenMin.x, screenMin.y, screenMax.x - screenMin.x, screenMax.y - screenMin.y);
            this.ctx.restore();
        });
    }

    getColorForT(t, fieldType = 'SignedDistanceField') {
        t = Math.max(0, Math.min(1, t));
        let stops;
        if (fieldType === 'OccupancyField') {
            stops = [
                { t: 0.0,  r: 20,  g: 22,  b: 30,  a: 0.0 },
                { t: 0.5,  r: 20,  g: 22,  b: 30,  a: 0.0 },
                { t: 0.75, r: 160, g: 254, b: 56,  a: 0.35 },
                { t: 1.0,  r: 160, g: 254, b: 56,  a: 0.60 }
            ];
        } else {
            stops = [
                { t: 0.0,   r: 10,  g: 80,  b: 220, a: 0.70 }, // Rich blue
                { t: 0.49,  r: 40,  g: 120, b: 255, a: 0.75 },
                { t: 0.51,  r: 255, g: 70,  b: 70,  a: 0.75 },
                { t: 1.0,   r: 220, g: 20,  b: 40,  a: 0.70 }  // Rich red
            ];
        }
        
        let i = 0;
        for (; i < stops.length - 1; i++) {
            if (t <= stops[i+1].t) break;
        }
        const s1 = stops[i];
        const s2 = stops[i+1];
        const range = s2.t - s1.t;
        const factor = range > 0 ? (t - s1.t) / range : 0;
        
        const r = Math.round(s1.r + (s2.r - s1.r) * factor);
        const g = Math.round(s1.g + (s2.g - s1.g) * factor);
        const b = Math.round(s1.b + (s2.b - s1.b) * factor);
        const a = s1.a + (s2.a - s1.a) * factor;
        
        return [r, g, b, a];
    }

    formatExtentValue(val) {
        if (val === null || val === undefined || isNaN(val)) return '–';
        if (val >= 100) return val.toFixed(0);
        if (val >= 10) return val.toFixed(1);
        if (val >= 0.1) return val.toFixed(2);
        if (val >= 0.001) return val.toFixed(4);
        return val.toExponential(2);
    }
}
