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
        if (objId.includes('circle')) return 'circle';
        if (objId.includes('rectangle')) return 'rectangle';
        if (objId.includes('triangle')) return 'triangle';
        if (objId.includes('ellipse')) return 'ellipse';
        if (objId.includes('line')) return 'line';
        return 'unknown';
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

        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.left = event.pageX + 'px';
        menu.style.top = event.pageY + 'px';
        
        menu.innerHTML = `
            <button class="context-menu-item" data-action="rename">Rename</button>
            <button class="context-menu-item" data-action="duplicate">Duplicate</button>
            <div class="context-menu-separator"></div>
            <button class="context-menu-item" data-action="delete">Delete</button>
        `;

        document.body.appendChild(menu);

        // Handle menu actions
        menu.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action) {
                this.handleContextAction(action, objId);
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

    handleContextAction(action, objId) {
        switch (action) {
            case 'rename':
                this.renameObject(objId);
                break;
            case 'duplicate':
                this.emit('object_duplicate', objId);
                break;
            case 'delete':
                if (confirm(`Delete object ${objId}?`)) {
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
