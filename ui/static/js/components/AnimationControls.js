/**
 * 2Top Geometry Library - Animation Controls Component
 */

class AnimationControls extends EventEmitter {
    constructor(container) {
        super();
        this.container = container;
        this.animations = new Map();
        this.isPlaying = false;
        this.currentFrame = 0;
        this.totalFrames = 100;
        this.fps = 10;
        this.playbackTimer = null;
        
        this.setupControls();
    }

    setupControls() {
        this.playBtn = this.container.querySelector('#play-btn');
        this.pauseBtn = this.container.querySelector('#pause-btn');
        this.stopBtn = this.container.querySelector('#stop-btn');
        this.frameSlider = this.container.querySelector('#frame-slider');
        this.timeline = this.container.querySelector('#timeline');
        
        this.setupEventHandlers();
        this.updateUI();
    }

    setupEventHandlers() {
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.play());
        }
        
        if (this.pauseBtn) {
            this.pauseBtn.addEventListener('click', () => this.pause());
        }
        
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stop());
        }
        
        if (this.frameSlider) {
            this.frameSlider.addEventListener('input', (e) => {
                this.setFrame(parseInt(e.target.value));
            });
        }
    }

    play() {
        if (this.isPlaying) return;
        
        this.isPlaying = true;
        this.playbackTimer = setInterval(() => {
            this.nextFrame();
        }, 1000 / this.fps);
        
        this.updateUI();
        this.emit('playback_started');
    }

    pause() {
        if (!this.isPlaying) return;
        
        this.isPlaying = false;
        if (this.playbackTimer) {
            clearInterval(this.playbackTimer);
            this.playbackTimer = null;
        }
        
        this.updateUI();
        this.emit('playback_paused');
    }

    stop() {
        this.pause();
        this.setFrame(0);
        this.emit('playback_stopped');
    }

    nextFrame() {
        if (this.currentFrame >= this.totalFrames - 1) {
            this.stop();
        } else {
            this.setFrame(this.currentFrame + 1);
        }
    }

    setFrame(frame) {
        this.currentFrame = Math.max(0, Math.min(frame, this.totalFrames - 1));
        
        if (this.frameSlider) {
            this.frameSlider.value = this.currentFrame;
        }
        
        this.updateTimeline();
        this.emit('frame_changed', this.currentFrame);
    }

    updateUI() {
        if (this.playBtn) {
            this.playBtn.disabled = this.isPlaying;
        }
        
        if (this.pauseBtn) {
            this.pauseBtn.disabled = !this.isPlaying;
        }
        
        if (this.frameSlider) {
            this.frameSlider.max = this.totalFrames - 1;
            this.frameSlider.value = this.currentFrame;
        }
    }

    updateTimeline() {
        if (!this.timeline) return;
        
        this.timeline.innerHTML = '';
        
        const ruler = document.createElement('div');
        ruler.className = 'timeline-ruler';
        this.timeline.appendChild(ruler);
        
        const playhead = document.createElement('div');
        playhead.className = 'timeline-playhead';
        playhead.style.left = `${(this.currentFrame / this.totalFrames) * 100}%`;
        this.timeline.appendChild(playhead);
    }

    addAnimation(animId, config) {
        const animation = {
            id: animId,
            objId: config.objId,
            parameter: config.parameter,
            values: config.values || [],
            duration: config.duration || this.totalFrames
        };
        
        this.animations.set(animId, animation);
        this.updateTimeline();
        
        return animation;
    }

    removeAnimation(animId) {
        this.animations.delete(animId);
        this.updateTimeline();
    }

    clearAnimations() {
        this.animations.clear();
        this.updateTimeline();
    }
}
