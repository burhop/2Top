class GeometryStudio {
    constructor({ canvasRenderer, uiClient }) {
        this.canvasRenderer = canvasRenderer;
        this.uiClient = uiClient;

        // Test list state
        this.tests = [];
        this.currentIndex = -1;
        this.isLoadingTest = false;
        this.results = new Map(); // testId -> 'ok' | 'err'

        // Runner state
        this._playTimer = null;
        this._playDelay = 1000;
        this._debouncedRefreshTimeout = null;
        this._pendingAutoFit = false;

        this.elements = {
            testList:            document.getElementById('geometry-test-list'),
            runnerIndex:         document.getElementById('runner-index'),
            runnerPrev:          document.getElementById('runner-prev'),
            runnerPlay:          document.getElementById('runner-play'),
            runnerPause:         document.getElementById('runner-pause'),
            runnerNext:          document.getElementById('runner-next'),
            runnerSpeed:         document.getElementById('runner-speed'),
            mouseLabel:          document.getElementById('mouse-coords'),
            zoomLabel:           document.getElementById('zoom-level'),
            boundsLabel:         document.getElementById('bounds-info'),
            intersectionLabel:   document.getElementById('intersection-count'),
            toggleGrid:          document.getElementById('toggle-grid'),
            toggleAxes:          document.getElementById('toggle-axes'),
            toggleKeypoints:     document.getElementById('toggle-keypoints'),
            toggleIntersections: document.getElementById('toggle-intersections'),
        };

        this._bindRendererEvents();
        this._bindToggles();
        this._bindTransport();
        this.loadTests();
        this.refreshSceneData(true);
    }

    // ── Renderer HUD ──────────────────────────────────────────────────────────

    _bindRendererEvents() {
        if (!this.canvasRenderer) return;
        this.canvasRenderer.on('mouse_move', ({ world }) => {
            if (!this.elements.mouseLabel) return;
            this.elements.mouseLabel.textContent =
                `(${world.x.toFixed(2)}, ${world.y.toFixed(2)})`;
        });
        this.canvasRenderer.on('viewport_changed', ({ bounds, zoom }) => {
            this._updateBounds(bounds);
            this._updateZoom(zoom);
            
            // Debounce reloading curve paths on zoom/pan to avoid flooding the Flask server
            if (this._debouncedRefreshTimeout) {
                clearTimeout(this._debouncedRefreshTimeout);
            }
            this._debouncedRefreshTimeout = setTimeout(() => {
                this.refreshSceneData();
            }, 150); // 150ms debounce
        });
    }

    _bindToggles() {
        const { toggleGrid, toggleAxes, toggleKeypoints, toggleIntersections } = this.elements;
        toggleGrid?.addEventListener('change', (e) => this.canvasRenderer.setGridVisibility(e.target.checked));
        toggleAxes?.addEventListener('change', (e) => this.canvasRenderer.setAxisVisibility(e.target.checked));
        toggleKeypoints?.addEventListener('change', (e) => this.canvasRenderer.setKeyPointVisibility(e.target.checked));
        toggleIntersections?.addEventListener('change', (e) => this.canvasRenderer.setIntersectionVisibility(e.target.checked));
    }

    // ── Transport controls ────────────────────────────────────────────────────

    _bindTransport() {
        this.elements.runnerPrev?.addEventListener('click', () => this.prev());
        this.elements.runnerNext?.addEventListener('click', () => this.next());
        this.elements.runnerPlay?.addEventListener('click', () => this.play());
        this.elements.runnerPause?.addEventListener('click', () => this.pause());
        this.elements.runnerSpeed?.addEventListener('change', (e) => {
            this._playDelay = parseInt(e.target.value, 10);
            if (this._playTimer) {
                this.pause();
                this.play();
            }
        });

        // Keyboard: left/right arrows navigate tests
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
            if (e.key === 'ArrowRight') { e.preventDefault(); this.next(); }
            if (e.key === 'ArrowLeft')  { e.preventDefault(); this.prev(); }
            if (e.key === ' ')          { e.preventDefault(); this._playTimer ? this.pause() : this.play(); }
        });
    }

    play() {
        if (this.tests.length === 0) return;
        // Start from first if nothing selected yet
        if (this.currentIndex < 0) this.currentIndex = 0;
        this._setPlayingUI(true);
        this._scheduleNext();
    }

    pause() {
        clearTimeout(this._playTimer);
        this._playTimer = null;
        this._setPlayingUI(false);
    }

    next() {
        if (this.tests.length === 0) return;
        const next = (this.currentIndex + 1) % this.tests.length;
        this._goTo(next);
    }

    prev() {
        if (this.tests.length === 0) return;
        const prev = (this.currentIndex - 1 + this.tests.length) % this.tests.length;
        this._goTo(prev);
    }

    _scheduleNext() {
        this._playTimer = setTimeout(async () => {
            if (this._playTimer === null) return; // paused
            const idx = this.currentIndex;
            await this._goTo(idx);
            // advance index after run completes, then schedule next
            if (this._playTimer !== null) {
                this.currentIndex = (idx + 1) % this.tests.length;
                this._scheduleNext();
            }
        }, this._playDelay);
    }

    _setPlayingUI(playing) {
        const play  = this.elements.runnerPlay;
        const pause = this.elements.runnerPause;
        if (play)  play.style.display  = playing ? 'none'  : '';
        if (pause) pause.style.display = playing ? ''      : 'none';
    }

    // ── Test loading & running ────────────────────────────────────────────────

    async loadTests() {
        const list = this.elements.testList;
        if (list) list.innerHTML = '<div class="test-list-empty">Loading…</div>';
        try {
            const res = await fetch('/api/geometry-tests');
            const payload = await res.json();
            if (!payload.success) throw new Error(payload.error || 'Failed to load tests');
            this.tests = payload.tests || [];
            this._renderList();
            this._updateIndex();
        } catch (err) {
            console.error('Failed to load geometry tests', err);
            if (list) list.innerHTML = '<div class="test-list-empty">Unable to load tests</div>';
        }
    }

    async _goTo(index) {
        if (index < 0 || index >= this.tests.length) return;
        this.currentIndex = index;
        const test = this.tests[index];
        this._updateIndex();
        this._highlightRow(test.id);
        await this.runTest(test.id);
    }

    async runTest(testId) {
        if (!testId || this.isLoadingTest) return;
        this.isLoadingTest = true;
        this._markResult(testId, 'running');
        try {
            const res = await fetch('/api/geometry-tests/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_id: testId }),
            });
            const payload = await res.json();
            if (!payload.success) throw new Error(payload.error || 'Unknown error');
            this._markResult(testId, 'ok');
            // Small delay so the server finishes writing the scene before we read it
            await new Promise(r => setTimeout(r, 150));
            await this.refreshSceneData(true);
        } catch (err) {
            console.error('Failed to run geometry test', err);
            this._markResult(testId, 'err');
        } finally {
            this.isLoadingTest = false;
        }
    }

    // ── List rendering ────────────────────────────────────────────────────────

    _renderList() {
        const list = this.elements.testList;
        if (!list) return;
        if (this.tests.length === 0) {
            list.innerHTML = '<div class="test-list-empty">No tests found</div>';
            return;
        }
        list.innerHTML = '';
        this.tests.forEach((test, idx) => {
            const row = document.createElement('button');
            row.className = 'test-row';
            row.dataset.testId = test.id;
            row.dataset.idx = idx;
            row.title = test.description || test.name;
            row.innerHTML =
                `<span class="test-row-num">${idx + 1}</span>` +
                `<span class="test-row-name">${test.name}</span>` +
                `<span class="test-row-status" id="trs-${test.id}"></span>`;
            row.addEventListener('click', () => this._goTo(idx));
            list.appendChild(row);
        });
    }

    _highlightRow(testId) {
        const list = this.elements.testList;
        if (!list) return;
        list.querySelectorAll('.test-row').forEach(r => {
            const active = r.dataset.testId === testId;
            r.classList.toggle('active', active);
            if (active) r.scrollIntoView({ block: 'nearest' });
        });
    }

    _markResult(testId, status) {
        this.results.set(testId, status);
        const el = document.getElementById(`trs-${testId}`);
        if (!el) return;
        const icons = { running: '⟳', ok: '✓', err: '✗' };
        el.textContent = icons[status] || '';
        el.className = `test-row-status status-${status}`;
    }

    _updateIndex() {
        const el = this.elements.runnerIndex;
        if (!el) return;
        const total = this.tests.length;
        const cur   = total === 0 ? '–' : this.currentIndex + 1;
        el.textContent = `${cur} / ${total || '–'}`;
    }

    // ── Scene data ────────────────────────────────────────────────────────────

    async refreshSceneData(autoFit = false) {
        if (this._refreshing) {
            this._pendingRefresh = true;
            this._pendingAutoFit = this._pendingAutoFit || autoFit;
            return;
        }
        this._refreshing = true;
        const shouldFit = autoFit || this._pendingAutoFit;
        this._pendingRefresh = false;
        this._pendingAutoFit = false;
        try {
            let url = '/api/geometry-scene';
            if (this.canvasRenderer) {
                const bounds = this.canvasRenderer.getViewBounds();
                if (bounds && Number.isFinite(bounds.minX) && Number.isFinite(bounds.maxX) && Number.isFinite(bounds.minY) && Number.isFinite(bounds.maxY)) {
                    url += `?min_x=${bounds.minX}&max_x=${bounds.maxX}&min_y=${bounds.minY}&max_y=${bounds.maxY}`;
                }
            }
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const payload = await res.json();
            if (!payload.success) throw new Error(payload.error || 'Failed to load scene');
            const data = payload.data;
            this.canvasRenderer.loadGeometryScene(data, shouldFit);
            this._updateBounds(data.scene_bounds);
            this._updateIntersections(data.intersections);
        } catch (err) {
            console.warn('GeometryStudio: failed to refresh scene', err);
        } finally {
            this._refreshing = false;
            if (this._pendingRefresh) this.refreshSceneData();
        }
    }

    _updateBounds(bounds) {
        if (!this.elements.boundsLabel || !bounds) return;
        const values = Array.isArray(bounds)
            ? bounds
            : [bounds.minX, bounds.maxX, bounds.minY, bounds.maxY];
        const [a, b, c, d] = values.map(v => Number.isFinite(v) ? v.toFixed(2) : '∞');
        this.elements.boundsLabel.textContent = `[${a}, ${b}, ${c}, ${d}]`;
    }

    _updateZoom(zoom) {
        if (!this.elements.zoomLabel) return;
        this.elements.zoomLabel.textContent = `${(zoom * 100).toFixed(0)}%`;
    }

    _updateIntersections(points) {
        if (!this.elements.intersectionLabel) return;
        this.elements.intersectionLabel.textContent = `${Array.isArray(points) ? points.length : 0}`;
    }
}

window.GeometryStudio = GeometryStudio;
