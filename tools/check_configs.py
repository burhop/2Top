import sys, math
sys.path.append('.')
from tests.test_periodic_curves import TEST_CONFIGS
import sympy as sp

for pid in ['4.01', '4.02', '4.21', '4.22', '4.23']:
    cfg = TEST_CONFIGS.get(pid)
    if not cfg:
        print(f'{pid}: not found')
        continue
    dom = cfg['domain']
    sr = cfg.get('search_range', (dom[1] - dom[0]) / 2.0)
    ec = cfg.get('expected_count', 'NOT SET')
    grid_res = cfg.get('grid_res', 500)
    print(f'{pid}: domain=({dom[0]:.2f},{dom[1]:.2f}), search_range={sr:.4f}, grid_res={grid_res}, expected_count={ec}')
