import sys; sys.path.append('.')
from tests.test_periodic_curves import TEST_CONFIGS
for pid in ['4.21', '4.22', '4.23']:
    cfg = TEST_CONFIGS[pid]
    eq_a = cfg["eq_a"]
    eq_b = cfg["eq_b"]
    grid_res = cfg.get("grid_res", 500)
    print(f'{pid}: eq_a={eq_a}, eq_b={eq_b}, grid_res={grid_res}')
