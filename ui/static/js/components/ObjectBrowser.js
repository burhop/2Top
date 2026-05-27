/**
 * 2Top Geometry Library - Object Browser Component
 * Manages the object list and selection in the left panel
 */

class ObjectBrowser extends EventEmitter {
    constructor(container) {
        super();
        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (!container) {
            throw new Error('ObjectBrowser requires a valid container element');
        }
        this.container = container;
        this.objects = new Map();
        this.selectedObject = null;
        
        this.render();
    }

    updateObjects(objectList) {
        // Update internal object list
        const newObjects = new Map();
        
        for (const objId of objectList) {
            if (this.objects.has(objId)) {
                newObjects.set(objId, this.objects.get(objId));
            } else {
                // New object - determine type from ID
                const type = this.getObjectTypeFromId(objId);
                newObjects.set(objId, {
                    id: objId,
                    type: type,
                    visible: true,
                    name: objId
                });
            }
        }
        
        this.objects = newObjects;
        this.render();
    }

    getObjectTypeFromId(objId) {
        const idLower = objId.toLowerCase();
        if (idLower.includes('circle')) return 'circle';
        if (idLower.includes('rectangle')) return 'rectangle';
        if (idLower.includes('triangle')) return 'triangle';
        if (idLower.includes('ellipse')) return 'ellipse';
        if (idLower.includes('line')) return 'line';
        if (idLower.includes('parabola')) return 'parabola';
        if (idLower.includes('hyperbola')) return 'hyperbola';
        if (idLower.includes('cubic')) return 'cubic';
        if (idLower.includes('periodic')) return 'periodic';
        if (idLower.includes('curvefield')) return 'curvefield';
        if (idLower.includes('signeddistancefield') || idLower.includes('sdf')) return 'sdf';
        if (idLower.includes('occupancyfield') || idLower.includes('occupancy')) return 'occupancy';
        if (idLower.includes('db_curve')) return 'db_curve';
        return 'unknown';
    }

    getAssociatedFields(objId) {
        const fields = [];
        const targetIdClean = objId.replace(/[^a-zA-Z0-9_]/g, '').toLowerCase();
        for (const [key, val] of this.objects.entries()) {
            const keyLower = key.toLowerCase();
            const isField = keyLower.includes('curvefield') || 
                            keyLower.includes('signeddistancefield') || 
                            keyLower.includes('occupancyfield') ||
                            keyLower.includes('sdf') ||
                            keyLower.includes('occupancy');
            if (isField) {
                // Match either strict _for_sourceId_ format or a simpler _sourceId match
                if (keyLower.includes(`_for_${targetIdClean}_`) || 
                    keyLower.includes(`_${targetIdClean}_`) || 
                    keyLower.endsWith(`_${targetIdClean}`)) {
                    fields.push(key);
                }
            }
        }
        return fields;
    }

    render() {
        if (!this.container) return;
        if (this.objects.size === 0) {
            this.container.innerHTML = '';
            return;
        }
        const objectsHtml = Array.from(this.objects.values()).map(obj => {
            const label = (obj.name || obj.id).slice(0, 3).toUpperCase();
            const sel = obj.id === this.selectedObject ? ' selected' : '';
            return `<button class="obj-pill${sel}" data-object-id="${obj.id}" title="${obj.name || obj.id} (${obj.type})">${label}</button>`;
        }).join('');
        this.container.innerHTML = objectsHtml;
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.container.querySelectorAll('.obj-pill').forEach(item => {
            item.addEventListener('click', () => {
                const objId = item.dataset.objectId;
                this.selectObject(objId);
            });
            item.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                const objId = item.dataset.objectId;
                this.showContextMenu(e, objId);
            });
        });
    }

    selectObject(objId) {
        this.selectedObject = objId;
        this.render();
        this.emit('object_selected', objId);
    }

    toggleVisibility(objId) {
        const obj = this.objects.get(objId);
        if (obj) {
            obj.visible = !obj.visible;
            this.render();
            this.emit('object_visibility_changed', objId, obj.visible);
        }
    }

    showContextMenu(event, objId) {
        // Remove existing context menu
        const existingMenu = document.querySelector('.context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        const type = this.getObjectTypeFromId(objId);
        const isField = type === 'curvefield' || type === 'sdf' || type === 'occupancy';
        const associatedFields = this.getAssociatedFields(objId);

        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.visibility = 'hidden';
        menu.style.position = 'absolute';
        
        let menuHtml = '';
        if (isField) {
            menuHtml = `
                <button class="context-menu-item" data-action="rename">Rename</button>
                <div class="context-menu-separator"></div>
                <button class="context-menu-item danger" data-action="delete">Delete Field</button>
            `;
        } else {
            // It's a curve / database curve / etc.
            menuHtml = `
                <button class="context-menu-item" data-action="rename">Rename</button>
                <button class="context-menu-item" data-action="duplicate">Duplicate</button>
                <div class="context-menu-separator"></div>
                <button class="context-menu-item" data-action="create_curve_field">Add CurveField</button>
                <button class="context-menu-item" data-action="create_sdf">Add SignedDistanceField (SDF)</button>
                <button class="context-menu-item" data-action="create_occupancy">Add OccupancyField</button>
            `;
            
            if (associatedFields.length > 0) {
                menuHtml += `
                    <div class="context-menu-separator"></div>
                    <button class="context-menu-item danger" data-action="delete_associated_fields">Delete Applied Fields (${associatedFields.length})</button>
                `;
            }
            
            menuHtml += `
                <div class="context-menu-separator"></div>
                <button class="context-menu-item danger" data-action="delete">Delete Curve</button>
            `;
        }

        menu.innerHTML = menuHtml;
        document.body.appendChild(menu);

        // Adjust position dynamically to fit completely within the viewport bounds
        const rect = menu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        let left = event.pageX;
        let top = event.pageY;
        
        // If the menu overflows the right edge, shift it left by its width
        if (left + rect.width > viewportWidth) {
            left = Math.max(10, left - rect.width);
        }
        // If the menu overflows the bottom edge, shift it up to stay visible
        if (top + rect.height > viewportHeight) {
            top = Math.max(10, viewportHeight - rect.height - 15);
        }
        
        menu.style.left = left + 'px';
        menu.style.top = top + 'px';
        menu.style.visibility = 'visible';

        // Handle menu actions
        menu.addEventListener('click', (e) => {
            const button = e.target.closest('.context-menu-item');
            if (!button) return;
            const action = button.dataset.action;
            if (action) {
                this.handleContextAction(action, objId, associatedFields);
                menu.remove();
            }
        });

        // Remove menu when clicking elsewhere
        const removeMenu = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }
        };
        setTimeout(() => document.addEventListener('click', removeMenu), 0);
    }

    handleContextAction(action, objId, associatedFields = []) {
        switch (action) {
            case 'rename':
                this.renameObject(objId);
                break;
            case 'duplicate':
                this.emit('object_duplicate', objId);
                break;
            case 'create_curve_field':
                this.emit('create_field_from_curve', { sourceId: objId, type: 'CurveField' });
                break;
            case 'create_sdf':
                this.emit('create_field_from_curve', { sourceId: objId, type: 'SignedDistanceField' });
                break;
            case 'create_occupancy':
                this.emit('create_field_from_curve', { sourceId: objId, type: 'OccupancyField' });
                break;
            case 'delete_associated_fields':
                if (confirm(`Delete all ${associatedFields.length} field(s) applied to curve ${objId}?`)) {
                    this.emit('delete_multiple_objects', associatedFields);
                }
                break;
            case 'delete':
                const type = this.getObjectTypeFromId(objId);
                const isField = type === 'curvefield' || type === 'sdf' || type === 'occupancy';
                const label = isField ? 'field' : 'object';
                if (confirm(`Delete ${label} ${objId}?`)) {
                    this.emit('object_deleted', objId);
                }
                break;
        }
    }

    renameObject(objId) {
        const obj = this.objects.get(objId);
        if (obj) {
            const newName = prompt('Enter new name:', obj.name);
            if (newName && newName !== obj.name) {
                obj.name = newName;
                this.render();
                this.emit('object_renamed', objId, newName);
            }
        }
    }

    clear() {
        this.objects.clear();
        this.selectedObject = null;
        this.render();
    }

    getSelectedObject() {
        return this.selectedObject;
    }

    setSelectedObject(objId) {
        this.selectedObject = objId;
        this.render();
    }
}
