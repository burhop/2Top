/**
 * 2Top Geometry Library - Canvas Renderer
 * Handles 2D canvas rendering of geometric objects
 */

class CanvasRenderer extends EventEmitter {
    constructor(canvas) {
        super();
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
            
            this.viewport.x -= dx / this.viewport.scale;
            this.viewport.y += dy / this.viewport.scale;
            this.render();
        }

        this.lastMousePos = { x, y };
    }

    handleMouseUp(e) {
        this.isDragging = false;
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const worldPos = this.screenToWorld(x, y);
        this.emit('mouse_up', { screen: { x, y }, world: worldPos });
    }

    handleWheel(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const worldPos = this.screenToWorld(x, y);
        
        this.viewport.scale *= scaleFactor;
        this.viewport.scale = Math.max(0.1, Math.min(10, this.viewport.scale));
        
        const newScreenPos = this.worldToScreen(worldPos.x, worldPos.y);
        this.viewport.x += (x - newScreenPos.x) / this.viewport.scale;
        this.viewport.y -= (y - newScreenPos.y) / this.viewport.scale;
        
        this.render();
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

    addObject(id, objectData) {
        this.objects.set(id, objectData);
        this.render();
    }

    removeObject(id) {
        this.objects.delete(id);
        this.selectedObjects.delete(id);
        this.render();
    }

    updateObject(id, objectData) {
        if (this.objects.has(id)) {
            this.objects.set(id, { ...this.objects.get(id), ...objectData });
            this.render();
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.save();
        this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.scale(this.viewport.scale, -this.viewport.scale);
        this.ctx.translate(-this.viewport.x, -this.viewport.y);

        if (this.showGrid) {
            this.renderGrid();
        }

        for (const [id, obj] of this.objects) {
            this.renderObject(id, obj);
        }

        this.ctx.restore();
    }

    renderGrid() {
        const gridSize = this.getGridSize();
        const bounds = this.getViewBounds();
        
        this.ctx.strokeStyle = '#e0e0e0';
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

    getGridSize() {
        const scale = this.viewport.scale;
        if (scale > 2) return 0.5;
        if (scale > 0.5) return 1;
        if (scale > 0.1) return 5;
        return 10;
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
        if (!obj.data) return;

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

        if (this.selectedObjects.has(id)) {
            this.renderSelection(obj);
        }

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
        this.render();
    }
}
