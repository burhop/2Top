/**
 * 2Top Geometry Library - Property Panel Component
 * Handles object property editing and styling
 */

class PropertyPanel extends EventEmitter {
    constructor(container) {
        super();
        this.container = container;
        this.currentObject = null;
        this.currentObjectData = null;
        this.parameters = {};
        
        this.render();
    }

    setObject(objId, objectData) {
        this.currentObject = objId;
        this.currentObjectData = objectData;
        this.loadParameters();
    }

    async loadParameters() {
        if (!this.currentObject) {
            this.render();
            return;
        }

        try {
            // In a real implementation, we'd fetch parameters from the backend
            // For now, we'll use default parameters based on object type
            this.parameters = this.getDefaultParameters();
            this.render();
        } catch (error) {
            console.error('Failed to load parameters:', error);
            this.render();
        }
    }

    getDefaultParameters() {
        if (!this.currentObject) return {};

        const type = this.getObjectType();
        
        switch (type) {
            case 'circle':
                return {
                    center_x: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    center_y: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    radius: { value: 1, min: 0.1, max: 10, step: 0.1, type: 'number' }
                };
            case 'rectangle':
                return {
                    x: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    y: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    width: { value: 2, min: 0.1, max: 10, step: 0.1, type: 'number' },
                    height: { value: 1.5, min: 0.1, max: 10, step: 0.1, type: 'number' }
                };
            case 'triangle':
                return {
                    x1: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    y1: { value: 1, min: -10, max: 10, step: 0.1, type: 'number' },
                    x2: { value: -1, min: -10, max: 10, step: 0.1, type: 'number' },
                    y2: { value: -1, min: -10, max: 10, step: 0.1, type: 'number' },
                    x3: { value: 1, min: -10, max: 10, step: 0.1, type: 'number' },
                    y3: { value: -1, min: -10, max: 10, step: 0.1, type: 'number' }
                };
            case 'ellipse':
                return {
                    center_x: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    center_y: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    radius_x: { value: 1.5, min: 0.1, max: 10, step: 0.1, type: 'number' },
                    radius_y: { value: 1, min: 0.1, max: 10, step: 0.1, type: 'number' }
                };
            case 'line':
                return {
                    x1: { value: -1, min: -10, max: 10, step: 0.1, type: 'number' },
                    y1: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' },
                    x2: { value: 1, min: -10, max: 10, step: 0.1, type: 'number' },
                    y2: { value: 0, min: -10, max: 10, step: 0.1, type: 'number' }
                };
            default:
                return {};
        }
    }

    getObjectType() {
        if (!this.currentObject) return 'unknown';
        
        if (this.currentObject.includes('circle')) return 'circle';
        if (this.currentObject.includes('rectangle')) return 'rectangle';
        if (this.currentObject.includes('triangle')) return 'triangle';
        if (this.currentObject.includes('ellipse')) return 'ellipse';
        if (this.currentObject.includes('line')) return 'line';
        return 'unknown';
    }

    render() {
        if (!this.currentObject) {
            this.container.innerHTML = '<div class="empty-state">Select an object to edit properties</div>';
            return;
        }

        const type = this.getObjectType();
        const parametersHtml = this.renderParameters();
        const styleHtml = this.renderStyleControls();

        this.container.innerHTML = `
            <div class="property-section">
                <h4>Object: ${this.currentObject}</h4>
                <div class="object-type-badge">${type.toUpperCase()}</div>
            </div>
            
            <div class="property-section">
                <h4>Parameters</h4>
                ${parametersHtml}
            </div>
            
            <div class="property-section">
                <h4>Style</h4>
                ${styleHtml}
            </div>
            
            <div class="property-section">
                <h4>Animation</h4>
                <button class="btn btn-secondary animate-btn">Create Animation</button>
            </div>
        `;

        this.setupEventHandlers();
    }

    renderParameters() {
        if (Object.keys(this.parameters).length === 0) {
            return '<div class="empty-state">No parameters available</div>';
        }

        return Object.entries(this.parameters).map(([name, param]) => `
            <div class="property-row">
                <label class="property-label">${name.replace('_', ' ')}</label>
                <div class="property-value">
                    <div class="property-slider-container">
                        <input type="range" 
                               class="property-slider" 
                               data-parameter="${name}"
                               min="${param.min}" 
                               max="${param.max}" 
                               step="${param.step}" 
                               value="${param.value}">
                        <input type="number" 
                               class="property-number-input" 
                               data-parameter="${name}"
                               min="${param.min}" 
                               max="${param.max}" 
                               step="${param.step}" 
                               value="${param.value}">
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderStyleControls() {
        const currentStyle = this.currentObjectData?.style || {};
        
        return `
            <div class="property-row">
                <label class="property-label">Color</label>
                <div class="property-value">
                    <div class="color-picker-container">
                        <input type="color" 
                               class="color-picker" 
                               data-style="color"
                               value="${currentStyle.color || '#667eea'}">
                        <span class="color-value">${currentStyle.color || '#667eea'}</span>
                    </div>
                </div>
            </div>
            
            <div class="property-row">
                <label class="property-label">Fill Color</label>
                <div class="property-value">
                    <div class="color-picker-container">
                        <input type="color" 
                               class="color-picker" 
                               data-style="fillColor"
                               value="${currentStyle.fillColor || '#667eea'}">
                        <span class="color-value">${currentStyle.fillColor || '#667eea'}</span>
                    </div>
                </div>
            </div>
            
            <div class="property-row">
                <label class="property-label">Line Width</label>
                <div class="property-value">
                    <div class="property-slider-container">
                        <input type="range" 
                               class="property-slider" 
                               data-style="lineWidth"
                               min="0.5" 
                               max="10" 
                               step="0.5" 
                               value="${currentStyle.lineWidth || 2}">
                        <input type="number" 
                               class="property-number-input" 
                               data-style="lineWidth"
                               min="0.5" 
                               max="10" 
                               step="0.5" 
                               value="${currentStyle.lineWidth || 2}">
                    </div>
                </div>
            </div>
            
            <div class="property-row">
                <label class="property-label">Opacity</label>
                <div class="property-value">
                    <div class="property-slider-container">
                        <input type="range" 
                               class="property-slider" 
                               data-style="opacity"
                               min="0" 
                               max="1" 
                               step="0.1" 
                               value="${currentStyle.opacity || 1}">
                        <input type="number" 
                               class="property-number-input" 
                               data-style="opacity"
                               min="0" 
                               max="1" 
                               step="0.1" 
                               value="${currentStyle.opacity || 1}">
                    </div>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        // Parameter sliders
        this.container.querySelectorAll('.property-slider[data-parameter]').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const parameter = e.target.dataset.parameter;
                const value = parseFloat(e.target.value);
                
                // Update corresponding number input
                const numberInput = this.container.querySelector(`input[type="number"][data-parameter="${parameter}"]`);
                if (numberInput) {
                    numberInput.value = value;
                }
                
                // Update parameter and emit change
                this.parameters[parameter].value = value;
                this.emit('parameter_changed', this.currentObject, parameter, value);
            });
        });

        // Parameter number inputs
        this.container.querySelectorAll('input[type="number"][data-parameter]').forEach(input => {
            input.addEventListener('change', (e) => {
                const parameter = e.target.dataset.parameter;
                const value = parseFloat(e.target.value);
                
                // Update corresponding slider
                const slider = this.container.querySelector(`.property-slider[data-parameter="${parameter}"]`);
                if (slider) {
                    slider.value = value;
                }
                
                // Update parameter and emit change
                this.parameters[parameter].value = value;
                this.emit('parameter_changed', this.currentObject, parameter, value);
            });
        });

        // Style controls
        this.container.querySelectorAll('[data-style]').forEach(control => {
            control.addEventListener('input', (e) => {
                const styleProperty = e.target.dataset.style;
                let value = e.target.value;
                
                // Convert to appropriate type
                if (styleProperty === 'lineWidth' || styleProperty === 'opacity') {
                    value = parseFloat(value);
                }
                
                // Update color value display
                if (e.target.type === 'color') {
                    const colorValue = this.container.querySelector(`.color-value`);
                    if (colorValue && e.target.closest('.color-picker-container').contains(colorValue)) {
                        colorValue.textContent = value;
                    }
                }
                
                // Update corresponding controls
                if (styleProperty === 'lineWidth' || styleProperty === 'opacity') {
                    const slider = this.container.querySelector(`.property-slider[data-style="${styleProperty}"]`);
                    const numberInput = this.container.querySelector(`input[type="number"][data-style="${styleProperty}"]`);
                    
                    if (e.target.type === 'range' && numberInput) {
                        numberInput.value = value;
                    } else if (e.target.type === 'number' && slider) {
                        slider.value = value;
                    }
                }
                
                // Emit style change
                const style = {};
                style[styleProperty] = value;
                this.emit('style_changed', this.currentObject, style);
            });
        });

        // Animation button
        const animateBtn = this.container.querySelector('.animate-btn');
        if (animateBtn) {
            animateBtn.addEventListener('click', () => {
                this.showAnimationDialog();
            });
        }
    }

    showAnimationDialog() {
        // Simple animation dialog
        const parameter = prompt('Enter parameter to animate:', Object.keys(this.parameters)[0] || '');
        if (parameter && this.parameters[parameter]) {
            const param = this.parameters[parameter];
            const startValue = prompt('Start value:', param.min);
            const endValue = prompt('End value:', param.max);
            const steps = prompt('Number of steps:', '10');
            
            if (startValue && endValue && steps) {
                const values = [];
                const start = parseFloat(startValue);
                const end = parseFloat(endValue);
                const stepCount = parseInt(steps);
                
                for (let i = 0; i <= stepCount; i++) {
                    const value = start + (end - start) * (i / stepCount);
                    values.push(value);
                }
                
                this.emit('animation_requested', {
                    objId: this.currentObject,
                    parameter: parameter,
                    values: values
                });
            }
        }
    }

    clear() {
        this.currentObject = null;
        this.currentObjectData = null;
        this.parameters = {};
        this.render();
    }
}
