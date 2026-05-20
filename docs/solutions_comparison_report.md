# 2Top Geometry - Solutions Comparison Report

This report benchmarks and compares the high-precision **Analytical Solver** against the **Graphics Pipeline** (which extracts intersections from discrete polylines).

## Benchmark Summary Dashboard
| Category | Total Cases | Analytical Pass Rate | Graphics Pass Rate | Avg Anal Time | Avg Graph Time |
|---|:---:|:---:|:---:|:---:|:---:|
| **Periodic Curves** | 152 | 99.34% | 88.16% | 0.0270s | 0.6855s |
| **Database Curves** | 500 | 100.00% | 100.00% | 0.1128s | 0.2325s |

## Table 1: Periodic Curves Detailed Results
| Case ID | Name | Expected | Analytical Found (Time) | Graphics Found (Time) | Status | Notes |
|---|---|:---:|:---:|:---:|:---:|---|
| 1.01 | y - sin(x) = 0 ∩ y = 0.0000 | 5 | 5 (0.0130s) | 5 (0.1531s) | ✅ Pass |  |
| 1.02 | y - sin(x) = 0 ∩ y = 0.5000 | 4 | 4 (0.0130s) | 4 (0.1341s) | ✅ Pass |  |
| 1.03 | y - sin(x) = 0 ∩ y = 1.0000 | 2 | 2 (0.0244s) | 2 (0.1391s) | ✅ Pass |  |
| 1.04 | y - sin(x) = 0 ∩ y = -1.0000 | 2 | 2 (0.0224s) | 2 (0.1265s) | ✅ Pass |  |
| 1.05 | y - sin(x) = 0 ∩ y = 1.5000 | 0 | 0 (0.0103s) | 0 (0.0946s) | ✅ Pass |  |
| 1.06 | y - sin(x) = 0 ∩ y = -0.5000 | 4 | 4 (0.0128s) | 4 (0.1346s) | ✅ Pass |  |
| 1.07 | y - sin(x) = 0 ∩ y = 0.8415 | 4 | 4 (0.0144s) | 4 (0.2713s) | ✅ Pass |  |
| 1.08 | y - cos(x) = 0 ∩ y = 0.0000 | 4 | 4 (0.0314s) | 4 (0.4331s) | ✅ Pass |  |
| 1.09 | y - cos(x) = 0 ∩ y = 1.0000 | 3 | 3 (0.1140s) | 3 (0.4398s) | ✅ Pass |  |
| 1.10 | y - cos(x) = 0 ∩ y = -1.0000 | 2 | 2 (0.0835s) | 2 (0.4697s) | ✅ Pass |  |
| 1.11 | y - cos(x) = 0 ∩ y = 0.5000 | 4 | 4 (0.0326s) | 4 (0.4270s) | ✅ Pass |  |
| 1.12 | y - cos(x) = 0 ∩ y = -0.4161 | 4 | 4 (0.0315s) | 4 (0.4348s) | ✅ Pass |  |
| 1.13 | y - sin(x - pi/4) = 0 ∩ y = 0 | 4 | 4 (0.0332s) | 4 (0.4685s) | ✅ Pass |  |
| 1.14 | y - sin(x + pi/3) = 0 ∩ y - 0.5 = 0 | 4 | 4 (0.0494s) | 4 (0.4762s) | ✅ Pass |  |
| 1.15 | y - cos(x - pi/2) = 0 ∩ y = 0 | 5 | 5 (0.0149s) | 5 (0.1365s) | ✅ Pass |  |
| 1.16 | y - sin(x - 1) = 0 ∩ y = 0 | 4 | 4 (0.0138s) | 4 (0.1422s) | ✅ Pass |  |
| 1.17 | y - 2*sin(x) = 0 ∩ y = 0 | 5 | 5 (0.0115s) | 5 (0.1755s) | ✅ Pass |  |
| 1.18 | y - 2*sin(x) = 0 ∩ y - 1.5 = 0 | 4 | 4 (0.0131s) | 4 (0.1417s) | ✅ Pass |  |
| 1.19 | y - 0.5*sin(x) = 0 ∩ y - 0.3 = 0 | 4 | 4 (0.0168s) | 4 (0.1570s) | ✅ Pass |  |
| 1.20 | y - 3*cos(x) = 0 ∩ y - 2 = 0 | 4 | 4 (0.0121s) | 4 (0.1330s) | ✅ Pass |  |
| 1.21 | y - 2*sin(x) = 0 ∩ y - 2 = 0 | 2 | 2 (0.0213s) | 2 (0.1504s) | ✅ Pass |  |
| 1.22 | y - 2*sin(x) = 0 ∩ y - 3 = 0 | 0 | 0 (0.0118s) | 0 (0.1043s) | ✅ Pass |  |
| 1.23 | y - sin(2*x) = 0 ∩ y = 0 | 9 | 9 (0.0129s) | 9 (0.1954s) | ✅ Pass |  |
| 1.24 | y - sin(3*x) = 0 ∩ y = 0 | 13 | 13 (0.0161s) | 13 (0.2413s) | ✅ Pass |  |
| 1.25 | y - sin(0.5*x) = 0 ∩ y = 0 | 3 | 3 (0.0142s) | 3 (0.1237s) | ✅ Pass |  |
| 1.26 | y - cos(2*x) = 0 ∩ y - 0.5 = 0 | 8 | 8 (0.0134s) | 8 (0.1991s) | ✅ Pass |  |
| 1.27 | y - sin(pi*x) = 0 ∩ y = 0 | 7 | 7 (0.0154s) | 7 (0.1763s) | ✅ Pass |  |
| 1.28 | y - sin(x) = 0 ∩ x - pi/6 = 0 | 1 | 1 (0.0117s) | 1 (0.1060s) | ✅ Pass |  |
| 1.29 | y - sin(x) = 0 ∩ x = 0 | 1 | 1 (0.0117s) | 1 (0.1100s) | ✅ Pass |  |
| 1.30 | y - sin(x) = 0 ∩ y - x = 0 | 1 | 1 (0.0322s) | 1 (0.1773s) | ✅ Pass |  |
| 1.31 | y - sin(x) = 0 ∩ y - x/pi = 0 | 3 | 3 (0.0168s) | 3 (0.1818s) | ✅ Pass |  |
| 1.32 | y - cos(x) = 0 ∩ y + x = 0 | 1 | 1 (0.0114s) | 1 (0.1428s) | ✅ Pass |  |
| 1.33 | ProceduralCurve(y - sin(x)) = 0 ∩ y = 0 | 5 | 5 (0.0134s) | 5 (0.1229s) | ✅ Pass |  |
| 1.34 | ProceduralCurve(y - cos(x)) = 0 ∩ y = 0 | 4 | 4 (0.0117s) | 4 (0.1544s) | ✅ Pass |  |
| 1.35 | ProceduralCurve(y - sin(2*x)) = 0 ∩ y = 0 | 9 | 9 (0.0129s) | 9 (0.1380s) | ✅ Pass |  |
| 1.36 | ProceduralCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y - 0.5) = 0 | 4 | 4 (0.0123s) | 4 (0.1089s) | ✅ Pass |  |
| 1.37 | y - sin(x) = 0 ∩ y - 1.0000000001 = 0 | 2 | 2 (0.0252s) | 2 (0.1403s) | ✅ Pass |  |
| 1.38 | y - sin(x) = 0 ∩ y - 0.999999 = 0 | 4 | 4 (0.0210s) | 2 (0.1304s) | ❌ Graph Fail | 2/4 pts matched |
| 1.39 | y - sin(x) = 0 ∩ y - sin(x) = 0 | 0 | 0 (0.0012s) | 35 (1.8130s) | ❌ Graph Fail | 35 pts found (Overlap Case) |
| 1.40 | y - sin(100*x) = 0 ∩ y = 0 | 63 | 63 (0.0745s) | 33 (0.5117s) | ❌ Graph Fail | 33/63 pts matched |
| 2.01 | y - sin(x) = 0 ∩ x**2 + y**2 - 1 = 0 | 2 | 2 (0.0133s) | 2 (0.2128s) | ✅ Pass |  |
| 2.02 | y - sin(x) = 0 ∩ x**2 + y**2 - 4 = 0 | 2 | 2 (0.0129s) | 2 (0.2530s) | ✅ Pass |  |
| 2.03 | y - sin(x) = 0 ∩ (x-pi)**2 + y**2 - 1 = 0 | 2 | 2 (0.0209s) | 2 (0.2177s) | ✅ Pass |  |
| 2.04 | y - sin(x) = 0 ∩ x**2 + y**2 - 0.01 = 0 | 2 | 2 (0.0332s) | 2 (0.3092s) | ✅ Pass |  |
| 2.05 | y - sin(x) = 0 ∩ (x-10)**2 + y**2 - 1 = 0 | 2 | 2 (0.0168s) | 2 (0.2100s) | ✅ Pass |  |
| 2.06 | y - cos(x) = 0 ∩ x**2 + y**2 - 1 = 0 | 1 | 1 (0.1375s) | 2 (0.4176s) | ❌ Graph Fail | 2/1 pts matched |
| 2.07 | y - sin(2*x) = 0 ∩ x**2 + y**2 - 1 = 0 | 2 | 2 (0.0140s) | 2 (0.2142s) | ✅ Pass |  |
| 2.08 | y - 2*sin(x) = 0 ∩ x**2 + y**2 - 4 = 0 | 2 | 2 (0.0127s) | 2 (0.2103s) | ✅ Pass |  |
| 2.09 | y - sin(x) = 0 ∩ x**2/4 + y**2 - 1 = 0 | 2 | 2 (0.0133s) | 2 (0.2116s) | ✅ Pass |  |
| 2.10 | y - sin(x) = 0 ∩ x**2 + y**2/4 - 1 = 0 | 2 | 2 (0.0138s) | 2 (0.2139s) | ✅ Pass |  |
| 2.11 | y - cos(x) = 0 ∩ x**2/9 + y**2/4 - 1 = 0 | 2 | 2 (0.0178s) | 2 (0.2098s) | ✅ Pass |  |
| 2.12 | y - sin(x) = 0 ∩ (x-1)**2/4 + y**2 - 1 = 0 | 4 | 4 (0.0226s) | 4 (0.2703s) | ✅ Pass |  |
| 2.13 | y - sin(x) = 0 ∩ y - x**2 = 0 | 2 | 2 (0.0165s) | 2 (0.1584s) | ✅ Pass |  |
| 2.14 | y - sin(x) = 0 ∩ y + x**2 = 0 | 2 | 2 (0.0143s) | 2 (0.1529s) | ✅ Pass |  |
| 2.15 | y - sin(x) = 0 ∩ y - x**2/4 = 0 | 2 | 2 (0.0150s) | 2 (0.1655s) | ✅ Pass |  |
| 2.16 | y - cos(x) = 0 ∩ y - x**2 + 1 = 0 | 2 | 2 (0.0139s) | 2 (0.1566s) | ✅ Pass |  |
| 2.17 | y - sin(x) = 0 ∩ x - pi/4 = 0 | 1 | 1 (0.0137s) | 1 (0.1120s) | ✅ Pass |  |
| 2.18 | y - sin(x) = 0 ∩ x - pi = 0 | 1 | 1 (0.0144s) | 1 (0.1233s) | ✅ Pass |  |
| 2.19 | y - cos(x) = 0 ∩ x = 0 | 1 | 1 (0.0114s) | 1 (0.1087s) | ✅ Pass |  |
| 2.20 | y - sin(x) = 0 ∩ x + y = 0 | 1 | 1 (0.0116s) | 1 (0.1399s) | ✅ Pass |  |
| 2.21 | y**2 - sin(x) = 0 ∩ y - 0.5 = 0 | 4 | 4 (0.0135s) | 4 (0.3557s) | ✅ Pass |  |
| 2.22 | y**2 - sin(x) = 0 ∩ y = 0 | 5 | 5 (0.0119s) | 4 (0.3270s) | ❌ Graph Fail | 4/5 pts matched |
| 2.23 | y**2 - sin(x) = 0 ∩ y - 1 = 0 | 2 | 2 (0.0201s) | 2 (0.3084s) | ✅ Pass |  |
| 2.24 | y**2 - 2*sin(x) = 0 ∩ y = 0 | 5 | 5 (0.0117s) | 4 (0.3499s) | ❌ Graph Fail | 4/5 pts matched |
| 2.25 | y**2 - 2*sin(x) = 0 ∩ y - 1 = 0 | 4 | 4 (0.0133s) | 4 (0.3163s) | ✅ Pass |  |
| 2.26 | y**2 - 2*sin(x) = 0 ∩ x**2 + y**2 - 1 = 0 | 2 | 2 (0.0142s) | 2 (0.5292s) | ✅ Pass |  |
| 2.27 | y**2 - 2*sin(x) = 0 ∩ x**2 + y**2 - 4 = 0 | 2 | 2 (0.0130s) | 2 (0.5193s) | ✅ Pass |  |
| 2.28 | y**2 - cos(x) = 0 ∩ y - 0.5 = 0 | 4 | 4 (0.0129s) | 4 (0.3184s) | ✅ Pass |  |
| 2.29 | y - 3*sin(x) = 0 ∩ x**2 + y**2 - 9 = 0 | 6 | 6 (0.0183s) | 6 (0.2837s) | ✅ Pass |  |
| 2.30 | y - sin(3*x) = 0 ∩ x**2 + y**2 - 1 = 0 | 6 | 6 (0.0163s) | 6 (0.2836s) | ✅ Pass |  |
| 2.31 | y**2 - sin(2*x) = 0 ∩ y - 0.5 = 0 | 8 | 8 (0.0149s) | 8 (0.5793s) | ✅ Pass |  |
| 2.32 | y**2 - 3*cos(x) = 0 ∩ y - 1 = 0 | 4 | 4 (0.0123s) | 4 (0.3188s) | ✅ Pass |  |
| 2.33 | y - sin(x) = 0 ∩ x**2 + y**2 - 1e-8 = 0 | 1 | 1 (0.0381s) | 1 (0.0898s) | ✅ Pass |  |
| 2.34 | y**2 - sin(x) = 0 ∩ y**2 - sin(x) = 0 | 0 | 0 (0.0011s) | 13 (3.3457s) | ❌ Graph Fail | 13 pts found (Overlap Case) |
| 2.35 | y - sin(x) = 0 ∩ y - x**2 + 1 = 0 | 2 | 2 (0.0127s) | 2 (0.1472s) | ✅ Pass |  |
| 2.36 | y**2 - sin(x) = 0 ∩ y + 0.5 = 0 | 4 | 4 (0.0130s) | 4 (0.3194s) | ✅ Pass |  |
| 2.37 | y**2 - sin(x) = 0 ∩ y - 1.5 = 0 | 0 | 0 (0.0103s) | 0 (0.2462s) | ✅ Pass |  |
| 2.38 | y - sin(x) = 0 ∩ x**2 - y**2 - 1 = 0 | 2 | 2 (0.0123s) | 2 (0.2275s) | ✅ Pass |  |
| 2.39 | y - sin(x) = 0 ∩ x*y - 1 = 0 | 4 | 4 (0.0134s) | 4 (0.1866s) | ✅ Pass |  |
| 2.40 | y**2 - 2*sin(x) = 0 ∩ y - x = 0 | 2 | 2 (0.0124s) | 2 (0.3776s) | ✅ Pass |  |
| 3.01 | y - sin(x) = 0 ∩ y - cos(x) = 0 | 4 | 4 (0.0152s) | 4 (0.2749s) | ✅ Pass |  |
| 3.02 | y - sin(x) = 0 ∩ y - sin(x + pi/2) = 0 | 4 | 4 (0.0131s) | 4 (0.3100s) | ✅ Pass |  |
| 3.03 | y - sin(x) = 0 ∩ y - sin(x + pi) = 0 | 5 | 5 (0.0137s) | 5 (0.2811s) | ✅ Pass |  |
| 3.04 | y - sin(x) = 0 ∩ y - sin(x + pi/4) = 0 | 4 | 4 (0.0153s) | 4 (0.2966s) | ✅ Pass |  |
| 3.05 | y - cos(x) = 0 ∩ y - cos(x + pi/3) = 0 | 4 | 4 (0.0145s) | 4 (0.2826s) | ✅ Pass |  |
| 3.06 | y - sin(x) = 0 ∩ y - sin(x + pi/6) = 0 | 4 | 4 (0.0179s) | 4 (0.2955s) | ✅ Pass |  |
| 3.07 | y - sin(x) = 0 ∩ y - sin(2*x) = 0 | 9 | 9 (0.0176s) | 9 (0.3965s) | ✅ Pass |  |
| 3.08 | y - sin(x) = 0 ∩ y - sin(3*x) = 0 | 13 | 13 (0.0175s) | 13 (0.5153s) | ✅ Pass |  |
| 3.09 | y - sin(x) = 0 ∩ y - cos(2*x) = 0 | 6 | 6 (0.0230s) | 6 (0.3370s) | ✅ Pass |  |
| 3.10 | y - cos(x) = 0 ∩ y - sin(2*x) = 0 | 8 | 8 (0.0162s) | 8 (0.3909s) | ✅ Pass |  |
| 3.11 | y - sin(2*x) = 0 ∩ y - sin(3*x) = 0 | 13 | 13 (0.0199s) | 13 (0.5243s) | ✅ Pass |  |
| 3.12 | y - sin(x) = 0 ∩ y - sin(0.5*x) = 0 | 5 | 5 (0.0179s) | 5 (0.3321s) | ✅ Pass |  |
| 3.13 | y - sin(2*x) = 0 ∩ y - cos(3*x) = 0 | 12 | 12 (0.0183s) | 12 (0.5153s) | ✅ Pass |  |
| 3.14 | y - sin(x) = 0 ∩ y - 2*sin(x) = 0 | 5 | 5 (0.0177s) | 5 (0.3274s) | ✅ Pass |  |
| 3.15 | y - sin(x) = 0 ∩ y - 0.5*sin(x) = 0 | 5 | 5 (0.0203s) | 5 (0.3480s) | ✅ Pass |  |
| 3.16 | y - 2*sin(x) = 0 ∩ y - 3*cos(x) = 0 | 4 | 4 (0.0138s) | 4 (0.2760s) | ✅ Pass |  |
| 3.17 | y - sin(x) = 0 ∩ y + sin(x) = 0 | 5 | 5 (0.0132s) | 5 (0.2743s) | ✅ Pass |  |
| 3.18 | y - sin(x) = 0 ∩ y + cos(x) = 0 | 4 | 4 (0.0130s) | 4 (0.2863s) | ✅ Pass |  |
| 3.19 | y**2 - sin(x) = 0 ∩ y**2 - cos(x) = 0 | 4 | 4 (0.0132s) | 4 (2.5258s) | ✅ Pass |  |
| 3.20 | y**2 - 2*sin(x) = 0 ∩ y**2 - 2*cos(x) = 0 | 4 | 4 (0.0139s) | 4 (2.4667s) | ✅ Pass |  |
| 3.21 | y**2 - sin(x) = 0 ∩ y**2 - sin(2*x) = 0 | 9 | 9 (0.0763s) | 8 (5.2497s) | ❌ Graph Fail | 8/9 pts matched |
| 3.22 | y**2 - sin(x) = 0 ∩ y**2 - 0.5*sin(x) = 0 | 5 | 5 (0.1246s) | 4 (3.2078s) | ❌ Graph Fail | 4/5 pts matched |
| 3.23 | y**2 - sin(x) = 0 ∩ (y-1)**2 - sin(x) = 0 | 4 | 4 (0.0138s) | 4 (2.4030s) | ✅ Pass |  |
| 3.24 | ImplicitCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y - cos(x)) = 0 | 4 | 4 (0.0137s) | 4 (0.2488s) | ✅ Pass |  |
| 3.25 | ProceduralCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y - cos(x)) = 0 | 4 | 4 (0.0126s) | 4 (0.2170s) | ✅ Pass |  |
| 3.26 | ProceduralCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y - sin(2*x)) = 0 | 9 | 9 (0.0155s) | 9 (0.2722s) | ✅ Pass |  |
| 3.27 | y - sin(x)*cos(x) = 0 ∩ y = 0 | 9 | 9 (0.0158s) | 9 (0.2156s) | ✅ Pass |  |
| 3.28 | y - sin(x)**2 = 0 ∩ y - 0.5 = 0 | 8 | 8 (0.0154s) | 8 (0.2450s) | ✅ Pass |  |
| 3.29 | y - (sin(x)+cos(x)) = 0 ∩ y = 0 | 4 | 4 (0.0132s) | 4 (0.1488s) | ✅ Pass |  |
| 3.30 | y - sin(x)*cos(x) = 0 ∩ y - sin(x) = 0 | 5 | 5 (0.0546s) | 5 (0.3645s) | ✅ Pass |  |
| 3.31 | ProceduralCurve(y - abs(sin(x))) = 0 ∩ y - 0.5 = 0 | 8 | 8 (0.0163s) | 8 (0.1495s) | ✅ Pass |  |
| 3.32 | y - sin(x**2) = 0 ∩ y = 0 | 5 | 5 (0.2750s) | 5 (0.2701s) | ✅ Pass |  |
| 3.33 | y - sin(x) = 0 ∩ y - sin(x) = 0 | 0 | 0 (0.0010s) | 35 (1.8106s) | ❌ Graph Fail | 35 pts found (Overlap Case) |
| 3.34 | y - sin(x) = 0 ∩ y - sin(x) - 1e-10 = 0 | 0 | 0 (0.0011s) | 35 (2.2322s) | ❌ Graph Fail | 35/0 pts matched |
| 3.35 | y - sin(x) = 0 ∩ y - sin(x+1e-8) = 0 | 0 | 0 (0.0010s) | 24 (1.2891s) | ❌ Graph Fail | 24/0 pts matched |
| 3.36 | y**2 - sin(x) = 0 ∩ y = 0 | 2 | 2 (0.0180s) | 2 (0.1784s) | ✅ Pass |  |
| 3.37 | y - sin(x) = 0 ∩ y - cos(x) = 0 | 1 | 1 (0.0252s) | 1 (0.2527s) | ✅ Pass |  |
| 3.38 | y - sin(x) = 0 ∩ y - cos(x) = 0 | 1 | 1 (0.0196s) | 1 (0.2288s) | ✅ Pass |  |
| 3.39 | ProceduralCurve(y - sin(1/x)) = 0 ∩ y = 0 | 23 | 34 (0.0346s) | 4 (0.1808s) | ⚠️ Uncertain | Accumulation case: oracle≈23, anal=34, graph=4 (all estimates) |
| 3.40 | ProceduralCurve(y - x*sin(1/x)) = 0 ∩ y = 0 | 64 | 38 (0.0318s) | 9 (0.3354s) | ❌ Graph Fail | 9/64 pts matched |
| 4.01 | y - sin(x) = 0 ∩ y = 0 | 21 | 21 (0.0244s) | 21 (0.1946s) | ✅ Pass |  |
| 4.02 | y - sin(x) = 0 ∩ y = 0 | 101 | 101 (0.0839s) | 99 (0.4233s) | ✅ Pass |  |
| 4.03 | y - sin(x) = 0 ∩ y = 0 | 63 | 63 (0.0594s) | 63 (0.2777s) | ✅ Pass |  |
| 4.04 | y - sin(x) = 0 ∩ y - 0.5 = 0 | 63 | 63 (0.0666s) | 63 (0.2362s) | ✅ Pass |  |
| 4.05 | y - sin(2*x) = 0 ∩ y = 0 | 127 | 127 (0.0826s) | 127 (0.6271s) | ✅ Pass |  |
| 4.06 | y - sin(10*x) = 0 ∩ y = 0 | 63 | 63 (0.0439s) | 63 (0.5906s) | ✅ Pass |  |
| 4.07 | y - sin(x) = 0 ∩ y - cos(x) = 0 | 64 | 64 (0.0734s) | 64 (0.5334s) | ✅ Pass |  |
| 4.08 | y**2 - 2*sin(x) = 0 ∩ y = 0 | 13 | 13 (0.0139s) | 13 (0.7593s) | ✅ Pass |  |
| 4.09 | y**2 - 2*sin(x) = 0 ∩ y - 1 = 0 | 13 | 13 (0.0178s) | 13 (0.7621s) | ✅ Pass |  |
| 4.10 | y**2 - 2*sin(x) = 0 ∩ x**2 + y**2 - 4 = 0 | 2 | 2 (0.0131s) | 2 (1.6609s) | ✅ Pass |  |
| 4.11 | y**2 - sin(x) = 0 ∩ y**2 - cos(x) = 0 | 14 | 14 (0.0188s) | 14 (19.0722s) | ✅ Pass |  |
| 4.12 | y**2 - 2*sin(x) = 0 ∩ y**2 - 2*cos(x) = 0 | 14 | 14 (0.0147s) | 14 (19.3184s) | ✅ Pass |  |
| 4.13 | ProceduralCurve(y - sin(x)) = 0 ∩ y = 0 | 63 | 63 (0.0585s) | 63 (0.2125s) | ✅ Pass |  |
| 4.14 | ProceduralCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y - cos(x)) = 0 | 64 | 64 (0.0637s) | 64 (0.3853s) | ✅ Pass |  |
| 4.15 | ProceduralCurve(y - sin(x)) = 0 ∩ ProceduralCurve(y) = 0 | 31 | 31 (0.0307s) | 31 (0.1533s) | ✅ Pass |  |
| 4.16 | ProceduralCurve(y - sin(2*x)) = 0 ∩ y = 0 | 63 | 63 (0.0340s) | 63 (0.2839s) | ✅ Pass |  |
| 4.17 | y - sin(x) = 0 ∩ y = 0 (grid_res=100) | 5 | 5 (0.0038s) | 5 (0.1405s) | ✅ Pass |  |
| 4.18 | y - sin(x) = 0 ∩ y = 0 (grid_res=200) | 5 | 5 (0.0045s) | 5 (0.1374s) | ✅ Pass |  |
| 4.19 | y - sin(x) = 0 ∩ y = 0 (grid_res=500) | 5 | 5 (0.0124s) | 5 (0.1424s) | ✅ Pass |  |
| 4.20 | y - sin(x) = 0 ∩ y = 0 (grid_res=1000) | 5 | 5 (0.0516s) | 5 (0.1382s) | ✅ Pass |  |
| 4.21 | y - sin(10*x) = 0 ∩ y = 0 (grid_res=1000) | 41 | 41 (0.0730s) | 41 (0.6439s) | ✅ Pass |  |
| 4.22 | y - sin(10*x) = 0 ∩ y = 0 (grid_res=1500) | 41 | 41 (0.1389s) | 41 (0.6364s) | ✅ Pass |  |
| 4.23 | y - sin(10*x) = 0 ∩ y = 0 (grid_res=2000) | 41 | 41 (0.2141s) | 41 (0.6302s) | ✅ Pass |  |
| 4.24 | y - sin(x) = 0 ∩ y = 0 (Symbolic, 10 runs) | 5 | 5 (0.0128s) | 5 (0.1405s) | ✅ Pass |  |
| 4.25 | Procedural(y - sin(x)) ∩ y = 0 (10 runs) | 5 | 5 (0.0117s) | 5 (0.1125s) | ✅ Pass |  |
| 4.26 | y - sin(x) = 0 ∩ x**2 + y**2 - 1 = 0 (10 runs) | 2 | 2 (0.0123s) | 2 (0.2107s) | ✅ Pass |  |
| 4.27 | y - sin(x) = 0 ∩ y - cos(x) = 0 (10 runs) | 4 | 4 (0.0138s) | 4 (0.2770s) | ✅ Pass |  |
| 4.28 | y**2 - 2*sin(x) = 0 ∩ x**2 + y**2 - 4 = 0 (10 runs) | 2 | 2 (0.0121s) | 2 (0.5539s) | ✅ Pass |  |
| 4.29 | y - sin(x) = 0 ∩ y = 0 (search_range=2.0) | 1 | 1 (0.0184s) | 5 (0.1411s) | ❌ Graph Fail | 5/1 pts matched |
| 4.30 | y - sin(x) = 0 ∩ y = 0 (search_range=5.0) | 3 | 3 (0.0132s) | 5 (0.1449s) | ❌ Graph Fail | 5/3 pts matched |
| 4.31 | y - sin(x) = 0 ∩ y = 0 (search_range=10.0) | 7 | 7 (0.0132s) | 5 (0.1408s) | ❌ Graph Fail | 5/7 pts matched |
| 4.32 | y - sin(x) = 0 ∩ y = 0 (search_range=50.0) | 31 | 31 (0.0348s) | 5 (0.1394s) | ❌ Graph Fail | 5/31 pts matched |

## Table 2: Database Failures & Mismatches
| RowID | Curve Pair (IDs) | Expected | Analytical Found (Time) | Graphics Found (Time) | Status | Details |
|---|---|:---:|:---:|:---:|:---:|---|
| — | No failures | — | — | — | ✅ All Pass | All tested database cases passed perfectly in both systems! |

## System Analysis & Future Context

This suite acts as an exhaustive continuous validation harness for the 2Top Geometry codebase.
Future LLMs and developers can run `python tools/compare_solutions_suite.py --status` to query the current progress, and run `python tools/compare_solutions_suite.py --continuous` to resume the batch pipeline.