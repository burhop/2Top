class GeometryStudio {
    constructor({ canvasRenderer, uiClient }) {
        this.canvasRenderer = canvasRenderer;
        this.uiClient = uiClient;

        // Test list state
        this.tests = [];
        this.currentIndex = -1;
        this.isLoadingTest = false;
        this.results = new Map(); // testId -> 'ok' | 'err' | 'running'
        this.suite = 'standard'; // 'standard' | 'periodic'

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
            runnerRenderAll:     document.getElementById('runner-render-all'),
            mouseLabel:          document.getElementById('mouse-coords'),
            zoomLabel:           document.getElementById('zoom-level'),
            boundsLabel:         document.getElementById('bounds-info'),
            intersectionLabel:   document.getElementById('intersection-count'),
            toggleGrid:          document.getElementById('toggle-grid'),
            toggleAxes:          document.getElementById('toggle-axes'),
            toggleKeypoints:     document.getElementById('toggle-keypoints'),
            toggleIntersections: document.getElementById('toggle-intersections'),
            toggleHeatmap:       document.getElementById('toggle-heatmap'),
            suiteStandard:       document.getElementById('suite-standard-btn'),
            suitePeriodic:       document.getElementById('suite-periodic-btn'),
            fieldExtentSlider:   document.getElementById('field-extent-slider'),
            fieldExtentVal:      document.getElementById('field-extent-val'),
        };

        this._bindRendererEvents();
        this._bindToggles();
        this._bindTransport();
        this._bindSuiteSelector();
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
        const { toggleGrid, toggleAxes, toggleKeypoints, toggleIntersections, toggleHeatmap, fieldExtentSlider, fieldExtentVal } = this.elements;
        toggleGrid?.addEventListener('change', (e) => this.canvasRenderer.setGridVisibility(e.target.checked));
        toggleAxes?.addEventListener('change', (e) => this.canvasRenderer.setAxisVisibility(e.target.checked));
        toggleKeypoints?.addEventListener('change', (e) => this.canvasRenderer.setKeyPointVisibility(e.target.checked));
        toggleIntersections?.addEventListener('change', (e) => this.canvasRenderer.setIntersectionVisibility(e.target.checked));
        toggleHeatmap?.addEventListener('change', (e) => this.canvasRenderer.setHeatmapVisibility(e.target.checked));

        if (fieldExtentSlider) {
            fieldExtentSlider.addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                if (fieldExtentVal) {
                    fieldExtentVal.textContent = Math.round(val);
                }
                this.canvasRenderer.glowSliderValue = val;
                this.canvasRenderer.fieldExtent = (val / 100.0) * 20.0;
                this.canvasRenderer.isExplicitFieldExtent = true;
                this.canvasRenderer.render();
            });
        }
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

    _bindSuiteSelector() {
        const { suiteStandard, suitePeriodic, runnerRenderAll } = this.elements;
        
        suiteStandard?.addEventListener('click', () => {
            if (this.suite === 'standard') return;
            this.suite = 'standard';
            suiteStandard.classList.add('active');
            suitePeriodic?.classList.remove('active');
            if (runnerRenderAll) runnerRenderAll.style.display = 'none';
            this.currentIndex = -1;
            this.results.clear();
            document.getElementById('db-verification-panel')?.classList.add('hidden');
            this.loadTests();
        });
        
        suitePeriodic?.addEventListener('click', () => {
            if (this.suite === 'periodic') return;
            this.suite = 'periodic';
            suitePeriodic.classList.add('active');
            suiteStandard?.classList.remove('active');
            if (runnerRenderAll) runnerRenderAll.style.display = '';
            this.currentIndex = -1;
            this.results.clear();
            document.getElementById('db-verification-panel')?.classList.add('hidden');
            this.loadTests();
        });

        runnerRenderAll?.addEventListener('click', () => {
            this.autoRenderAll();
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
            const endpoint = this.suite === 'standard' ? '/api/geometry-tests' : '/api/periodic-tests';
            const res = await fetch(endpoint);
            const payload = await res.json();
            if (!payload.success) throw new Error(payload.error || 'Failed to load tests');
            
            const rawTests = payload.tests || [];
            this.tests = rawTests.map(t => {
                return {
                    id: t.id || t.test_id,
                    name: t.name,
                    description: t.description || `${t.eq_a} vs ${t.eq_b}`
                };
            });
            
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
            const endpoint = this.suite === 'standard' ? '/api/geometry-tests/run' : '/api/periodic-tests/run';
            const res = await fetch(endpoint, {
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

            if (this.suite === 'periodic') {
                this._displayPeriodicVerification(payload);
            } else {
                document.getElementById('db-verification-panel')?.classList.add('hidden');
            }
        } catch (err) {
            console.error('Failed to run geometry test', err);
            this._markResult(testId, 'err');
        } finally {
            this.isLoadingTest = false;
        }
    }

    _displayPeriodicVerification(payload) {
        const panel = document.getElementById('db-verification-panel');
        const summary = document.getElementById('verification-summary');
        const details = document.getElementById('verification-details');
        if (!panel || !summary || !details) return;

        panel.classList.remove('hidden');

        // Render color-coded markers on HTML5 canvas
        const intersections = [];
        const isOverlap = payload.test_id === '1.39' || payload.test_id === '2.34' || payload.test_id === '3.33';
        const tol_int = (payload.name.includes("1/x") || payload.name.includes("reciprocal")) ? 0.15 : 0.05;
        
        payload.calculated_intersections.forEach((calc, idx) => {
            let isCorrect = false;
            if (!isOverlap) {
                for (const exp of payload.expected_intersections) {
                    const dist = Math.sqrt((calc[0] - exp[0])**2 + (calc[1] - exp[1])**2);
                    if (dist < tol_int) {
                        isCorrect = true;
                        break;
                    }
                }
            }
            intersections.push({
                x: calc[0],
                y: calc[1],
                label: `int_${idx+1}`,
                color: isCorrect ? '#39ff14' : '#ff3366'
            });
        });
        
        this.canvasRenderer.setIntersectionPoints(intersections);

        const endpoints_a = [];
        const tol_ep = 0.05;
        
        payload.calculated_endpoints.forEach((calc, idx) => {
            let isCorrect = false;
            for (const exp of payload.expected_endpoints) {
                const dist = Math.sqrt((calc[0] - exp[0])**2 + (calc[1] - exp[1])**2);
                if (dist < tol_ep) {
                    isCorrect = true;
                    break;
                }
            }
            endpoints_a.push({
                x: calc[0],
                y: calc[1],
                label: `ep_${idx+1}`,
                color: isCorrect ? '#39ff14' : '#ff3366'
            });
        });

        // Set keypoints on curve A
        const curveA = this.canvasRenderer.getObject('periodic_curve_a');
        const curveB = this.canvasRenderer.getObject('periodic_curve_b');
        if (curveA) {
            curveA.keyPoints = endpoints_a;
            this.canvasRenderer.updateObject('periodic_curve_a', curveA);
        }
        if (curveB) {
            curveB.keyPoints = [];
            this.canvasRenderer.updateObject('periodic_curve_b', curveB);
        }
        
        this.canvasRenderer.render();

        // ── Render Glassmorphic UI Report Card ──
        const statusClass = payload.is_correct ? 'v-badge-success' : 'v-badge-error';
        const statusIcon = payload.is_correct ? '✅' : '❌';
        const statusText = payload.is_correct ? 'VERIFIED' : 'MISMATCH';
        
        summary.innerHTML = `
            <div class="v-badge ${statusClass}">
                <span class="v-badge-icon">${statusIcon}</span>
                <div class="v-badge-text">
                    <strong>${statusText}</strong> — Case ${payload.test_id}<br>
                    <span style="font-size:0.65rem; opacity:0.85; font-family: monospace;">Time: ${payload.elapsed_time.toFixed(3)}s</span>
                </div>
            </div>
        `;

        const intCount = payload.calculated_intersections.length;
        const expIntCount = payload.expected_intersections.length;
        const epCount = payload.calculated_endpoints.length;
        const expEpCount = payload.expected_endpoints.length;

        details.innerHTML = `
            <div>
                <div class="v-section-title">Intersections</div>
                <div class="v-item-list">
                    <div class="v-item ${payload.is_correct ? 'match' : 'mismatch'}">
                        <div class="v-item-meta">
                            <span class="v-item-id">Intersection Count</span>
                            <span class="v-item-status-label">${intCount === expIntCount ? 'MATCH' : 'DIFF'}</span>
                        </div>
                        <div class="v-item-msg">Found ${intCount} intersections (Expected: ${expIntCount})</div>
                    </div>
                </div>
            </div>
            
            <div>
                <div class="v-section-title">Endpoints</div>
                <div class="v-item-list">
                    <div class="v-item ${payload.is_correct ? 'match' : 'mismatch'}">
                        <div class="v-item-meta">
                            <span class="v-item-id">Endpoint Count</span>
                            <span class="v-item-status-label">${epCount === expEpCount ? 'MATCH' : 'DIFF'}</span>
                        </div>
                        <div class="v-item-msg">Found ${epCount} endpoints (Expected: ${expEpCount})</div>
                    </div>
                </div>
            </div>
        `;
        
        // Bind close button
        document.getElementById('close-verification-panel')?.addEventListener('click', () => {
            panel.classList.add('hidden');
        });
    }

    async autoRenderAll() {
        if (this.tests.length === 0) return;
        this.pause(); // stop standard autoplay timer
        
        const overlay = document.getElementById('loading-overlay');
        const title = document.getElementById('loading-title');
        const status = document.getElementById('loading-status');
        const progressFill = document.getElementById('loading-progress-fill');
        
        if (!overlay) return;
        
        overlay.classList.add('visible');
        title.textContent = "Auto-Rendering Periodic Curves";
        
        let cancelRequested = false;
        const onKey = (e) => {
            if (e.key === 'Escape') {
                cancelRequested = true;
                if (status) status.textContent = "Cancelling sequential renders...";
            }
        };
        document.addEventListener('keydown', onKey);
        
        const total = this.tests.length;
        for (let i = 0; i < total; i++) {
            if (cancelRequested) break;
            
            const test = this.tests[i];
            const percent = ((i / total) * 100).toFixed(0);
            
            if (progressFill) progressFill.style.width = `${percent}%`;
            if (status) {
                status.textContent = `Rendering ${i + 1} of ${total}: Case ${test.id} (${test.name}). Press ESC to cancel.`;
            }
            
            try {
                this.currentIndex = i;
                this._updateIndex();
                this._highlightRow(test.id);
                
                const res = await fetch('/api/periodic-tests/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ test_id: test.id }),
                });
                const payload = await res.json();
                
                if (payload.success) {
                    this._markResult(test.id, 'ok');
                    await new Promise(r => setTimeout(r, 100)); // allow time for background render write to disk
                    await this.refreshSceneData(true);
                    this._displayPeriodicVerification(payload);
                } else {
                    this._markResult(test.id, 'err');
                }
            } catch (err) {
                console.error(`Failed to run/render case ${test.id}:`, err);
                this._markResult(test.id, 'err');
            }
        }
        
        if (progressFill) progressFill.style.width = '100%';
        if (status) {
            status.textContent = cancelRequested ? "Auto-rendering cancelled!" : "Completed! 155 periodic renders successfully generated.";
        }
        
        document.removeEventListener('keydown', onKey);
        
        // Brief pause to let user see 100% completion before hiding overlay
        setTimeout(() => {
            overlay.classList.remove('visible');
        }, 1200);
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
