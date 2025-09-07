/**
 * 2Top Geometry Library - UI Client
 * Handles direct communication with the backend UI server via WebSocket
 */

class UIClient extends EventEmitter {
    constructor() {
        super();
        this.socket = null;
        this.connected = false;
        this.commandIdCounter = 0;
        this.pendingCommands = new Map();
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        try {
            this.socket = io();
            this.setupEventHandlers();
        } catch (error) {
            console.error('Failed to connect to server:', error);
            this.emit('connection_error', error);
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.connected = true;
            this.emit('connected');
            this.processCommandQueue();
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.connected = false;
            this.emit('disconnected');
        });

        this.socket.on('connection_response', (data) => {
            console.log('Connection confirmed:', data);
        });

        this.socket.on('ui_response', (data) => {
            this.handleUIResponse(data);
        });

        this.socket.on('scene_updated', (data) => {
            this.emit('scene_updated', data);
        });

        this.socket.on('object_data_response', (data) => {
            this.emit('object_data_response', data);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.emit('connection_error', error);
        });
    }

    /**
     * Send MCP command to server
     */
    async sendCommand(command, params = {}) {
        if (!this.connected) {
            return Promise.reject(new Error('Not connected to UI server'));
        }
        
        const commandId = ++this.commandIdCounter;
        const commandData = {
            command: command,
            ...params
        };
        
        return new Promise((resolve, reject) => {
            this.pendingCommands.set(commandId, { resolve, reject });
            
            this.socket.emit('ui_command', {
                command_id: commandId,
                command: commandData
            });
            
            // Set timeout for command
            setTimeout(() => {
                if (this.pendingCommands.has(commandId)) {
                    this.pendingCommands.delete(commandId);
                    reject(new Error('Command timeout'));
                }
            }, 30000);
        });
    }

    /**
     * Handle UI response from server
     */
    handleUIResponse(data) {
        const commandId = data.command_id;
        const pending = this.pendingCommands.get(commandId);

        if (pending) {
            clearTimeout(pending.timeout);
            this.pendingCommands.delete(commandId);

            if (data.success) {
                pending.resolve(data.result);
            } else {
                pending.reject(new Error(data.error));
            }
        }
    }

    /**
     * Process queued commands when connection is established
     */
    processCommandQueue() {
        // Command queue processing no longer needed with direct UI commands
    }

    /**
     * Request object data for visualization
     */
    requestObjectData(objId, type = 'curve', resolution = 100) {
        if (this.connected) {
            this.socket.emit('get_object_data', {
                obj_id: objId,
                type: type,
                resolution: resolution
            });
        }
    }

    // Convenience methods for common UI commands

    /**
     * Create a circle
     */
    createCircle(objId, centerX, centerY, radius, style = {}) {
        return this.sendCommand('create_circle', {
            obj_id: objId,
            center_x: centerX,
            center_y: centerY,
            radius: radius,
            style: style
        });
    }
    
    /**
     * Create a rectangle
     */
    createRectangle(objId, x, y, width, height, style = {}) {
        return this.sendCommand('create_rectangle', {
            obj_id: objId,
            x: x,
            y: y,
            width: width,
            height: height,
            style: style
        });
    }
    
    /**
     * Create a triangle
     */
    createTriangle(objId, x1, y1, x2, y2, x3, y3, style = {}) {
        return this.sendCommand('create_triangle', {
            obj_id: objId,
            x1: x1, y1: y1,
            x2: x2, y2: y2,
            x3: x3, y3: y3,
            style: style
        });
    }
    
    /**
     * Create an ellipse
     */
    createEllipse(objId, centerX, centerY, radiusX, radiusY, style = {}) {
        return this.sendCommand('create_ellipse', {
            obj_id: objId,
            center_x: centerX,
            center_y: centerY,
            radius_x: radiusX,
            radius_y: radiusY,
            style: style
        });
    }
    
    /**
     * Create a line
     */
    createLine(objId, x1, y1, x2, y2, style = {}) {
        return this.sendCommand('create_line', {
            obj_id: objId,
            x1: x1, y1: y1,
            x2: x2, y2: y2,
            style: style
        });
    }
    
    /**
     * Delete an object
     */
    deleteObject(objId) {
        return this.sendCommand('delete_object', {
            obj_id: objId
        });
    }
    
    /**
     * Update object parameter
     */
    updateParameter(objId, parameter, value) {
        return this.sendCommand('update_parameter', {
            obj_id: objId,
            parameter: parameter,
            value: value
        });
    }
    
    /**
     * Set object style
     */
    setStyle(objId, style) {
        return this.sendCommand('set_style', {
            obj_id: objId,
            style: style
        });
    }
    
    /**
     * Save scene
     */
    saveScene(filename) {
        return this.sendCommand('save_scene', {
            filename: filename
        });
    }
    
    /**
     * Load scene
     */
    loadScene(filename) {
        return this.sendCommand('load_scene', {
            filename: filename
        });
    }
    
    /**
     * Clear scene
     */
    clearScene() {
        return this.sendCommand('clear_scene', {});
    }
    
    /**
     * Get object data
     */
    getObjectData(objId, bounds, resolution = 100) {
        return this.sendCommand('get_object_data', {
            obj_id: objId,
            bounds: bounds,
            resolution: resolution
        });
    }
    
    /**
     * Get scene bounds
     */
    getSceneBounds() {
        return this.sendCommand('get_scene_bounds', {});
    }
    
    /**
     * Group objects
     */
    async groupObjects(groupId, objectIds) {
        return this.sendCommand({
            command: 'group_objects',
            group_id: groupId,
            object_ids: objectIds
        });
    }

    /**
     * Create parameter animation
     */
    async createParameterAnimation(objId, parameter, values, filename, options = {}) {
        return this.sendCommand({
            command: 'animate_parameter',
            obj_id: objId,
            parameter: parameter,
            values: values,
            filename: filename,
            ...options
        });
    }

    /**
     * Create multi-parameter animation
     */
    async createMultiParameterAnimation(animations, filename, options = {}) {
        return this.sendCommand({
            command: 'animate_multi_parameter',
            animations: animations,
            filename: filename,
            ...options
        });
    }

    /**
     * Save scene
     */
    async saveScene(filename) {
        return this.sendCommand({
            command: 'save_scene',
            filename: filename
        });
    }

    /**
     * Load scene
     */
    async loadScene(filename) {
        return this.sendCommand({
            command: 'load_scene',
            filename: filename
        });
    }

    /**
     * Clear scene
     */
    async clearScene() {
        return this.sendCommand({
            command: 'clear_scene'
        });
    }

    /**
     * Get scene bounds
     */
    async getSceneBounds() {
        return this.sendCommand({
            command: 'get_scene_bounds'
        });
    }

    /**
     * List all objects in scene
     */
    async listObjects() {
        return this.sendCommand({
            command: 'list_objects'
        });
    }

    /**
     * Get object information
     */
    async getObjectInfo(objId) {
        return this.sendCommand({
            command: 'get_object_info',
            obj_id: objId
        });
    }

    /**
     * Render scene to image
     */
    async renderImage(filename, resolution = [800, 600], bbox = null) {
        return this.sendCommand({
            command: 'render_image',
            filename: filename,
            resolution: resolution,
            bbox: bbox
        });
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.connected = false;
        this.commandQueue = [];
        this.pendingCommands.clear();
    }
}
