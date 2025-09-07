# UI Testing Strategy for 2Top Geometry Visualization

**Sprint Planning Note**: This document outlines the comprehensive testing strategy for the future UI implementation of the 2Top geometry library.

## Testing Pyramid Approach

### 1. Unit Tests (Foundation) ✅
- Individual point containment (`AreaRegion.contains()`)
- Boundary detection (`CompositeCurve.is_closed()`)
- Factory methods (`create_square_from_edges()`)
- **Status**: Already working and reliable

### 2. Integration Tests (Current Focus)
- **Grid evaluation pipeline**: `RegionFactory` → `AreaRegion` → `GridEvaluator` → `PlotManager`
- **End-to-end visual tests**: Generate images and verify inside/boundary point counts
- **Cross-geometry consistency**: Same containment logic across circles, triangles, rectangles
- **Status**: In progress - fixing visual test pipeline

### 3. Visual Regression Tests
- **Reference image generation**: Create "golden" images from corrected visual tests
- **Pixel-level comparison**: Hash-based or structural similarity for detecting changes
- **Boundary visibility checks**: Ensure contours are always visible and correctly positioned
- **Fill pattern validation**: Verify inside points form coherent filled regions
- **Status**: Future implementation after integration tests are stable

### 4. UI Interaction Tests (Future)
- **Browser automation**: Selenium/Playwright for web interface testing
- **Interactive feedback**: Hover tooltips showing containment status
- **Zoom/pan accuracy**: Geometric precision maintained across scale changes
- **Responsive behavior**: Layout adapts without distorting geometry
- **Status**: Future sprint implementation

## Key Challenges to Address

### Cross-platform Rendering
- Matplotlib backends vary (TkAgg, Qt, web canvas)
- Font rendering and DPI differences
- Color space and gamma variations

### Numerical Precision
- Grid resolution vs boundary thickness
- Floating-point errors accumulating in vectorized operations
- Tolerance consistency across zoom levels

### Performance Scaling
- Large grids (1000×1000) with complex composite curves
- Real-time interaction vs batch rendering
- Memory usage with multiple simultaneous plots

## Implementation Plan

### Phase 1: Fix Current Pipeline (Current Sprint)
- Complete `GridEvaluator` and `PlotManager` corrections
- Verify all visual test categories produce meaningful output
- Document expected point counts for each geometry type

### Phase 2: Reference Image Suite (Next Sprint)
- Generate baseline images from corrected visual tests
- Create image comparison utilities (`tests/visual_regression/`)
- Add CI integration to catch visual regressions

### Phase 3: UI Test Framework (Future Sprint)
- Design web interface with interactive geometry viewer
- Implement automated interaction testing
- Add performance benchmarks for real-time rendering

## Success Metrics

- **Visual tests**: All panels show filled regions with visible boundaries
- **Regression detection**: Automated alerts for visual changes
- **Performance**: <100ms response time for interactive operations
- **Cross-platform**: Consistent rendering across Windows/Mac/Linux

## Technical Dependencies

### Required Tools
- **Visual regression**: `pytest-mpl` or custom image comparison
- **Browser testing**: Selenium WebDriver or Playwright
- **Performance monitoring**: `pytest-benchmark`
- **CI/CD**: GitHub Actions with artifact storage for reference images

### Infrastructure Needs
- **Reference image storage**: Git LFS or external storage for baseline images
- **Cross-platform testing**: CI runners for Windows/Mac/Linux
- **Performance baselines**: Benchmark database for tracking performance trends

## Notes for Future Sprints

1. **Start with Phase 2** once current visual test fixes are complete
2. **Prioritize cross-platform consistency** early in UI development
3. **Establish performance baselines** before adding complex interactions
4. **Consider accessibility** in UI interaction test design
5. **Document visual expectations** clearly for each geometry type

---

**Created**: 2025-08-10  
**Last Updated**: 2025-08-10  
**Sprint Context**: Post-visual test fixes, pre-UI implementation
