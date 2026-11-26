# Robustness for the pre-set claim rule: (a) different bootstrap seeds, (b) intersection-union p-values with Holm correction.
# Re-runs the exact logic of 12_snaps_equivalent.py, but keeps per-player squared-error differences (position-mean minus Combine prior).
import sys, io, contextlib, numpy as np, pandas as pd
D, O = sys.argv[1], sys.argv[2]
src = globals().get("SRC12") or open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "12_snaps_equivalent.py")).read()   # SRC12 is set by the notebook
src = src.replace('pd.DataFrame(out).to_csv(f"{O}/snaps_equivalent_results.csv",index=False); print("\\nsaved")', 'pass')
src = src.replace("g1=ci(a[\"pos\"],a[\"base\"]);", "g1=ci(a[\"pos\"],a[\"base\"]); DIFFS[(name,k)]=a[\"pos\"]-a[\"base\"];")
DIFFS = {}
sys.argv = ["x", D, O]
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "12_patched", "exec"), {"DIFFS": DIFFS, "__name__": "__main__"})
names = sorted({n for n, _ in DIFFS})
def boot(d, seed, B=20000):
    r = np.random.default_rng(seed); n = len(d); m = np.array([d[r.integers(0, n, n)].mean() for _ in range(B)])
    return m
rows = []
for nm in names:
    row = {"outcome": nm, "n_test": len(DIFFS[(nm, 0)])}
    met = []
    for seed in (1, 2, 3, 4, 5):
        ok = True
        for k in (0, 25):
            m = boot(DIFFS[(nm, k)], seed, 4000); ok &= np.percentile(m, 2.5) > 0
        met.append(ok)
    row["rule_met_in_seeds_of_5"] = sum(met)
    # one-sided bootstrap p for gain > 0 at k=0 and k=25; intersection-union p = max of the two
    p = {}
    for k in (0, 25):
        m = boot(DIFFS[(nm, k)], 11, 20000); p[k] = (np.sum(m <= 0) + 1) / (len(m) + 1)
    row.update(p_k0=p[0], p_k25=p[25], p_iu=max(p[0], p[25])); rows.append(row)
R = pd.DataFrame(rows).sort_values("p_iu").reset_index(drop=True); m = len(R)
R["holm_threshold"] = [0.05 / (m - i) for i in range(m)]
# Holm step-down
rej = []; stop = False
for i, r in R.iterrows():
    if not stop and r.p_iu <= r.holm_threshold: rej.append(True)
    else: stop = True; rej.append(False)
R["holm_reject_at_.05"] = rej
# Holm-adjusted p-values (step-down, monotone)
adj = []; run = 0.0
for i, r in R.iterrows():
    run = max(run, min(1.0, (m - i) * r.p_iu)); adj.append(run)
R["holm_adjusted_p"] = adj
pd.set_option("display.width", 220); print(R.round(4).to_string(index=False)); R.to_csv(f"{O}/robustness_holm.csv", index=False)
# Influence: does a single test player drive the gain? (drop-one means, and share of the total gain from the 3 largest contributors)
inf = []
for nm in names:
    for k in (0, 25):
        d = DIFFS[(nm, k)]; n = len(d); tot = d.sum(); loo = (tot - d) / (n - 1)
        top3 = np.sort(d)[::-1][:3].sum() / tot if tot > 0 else np.nan
        inf.append(dict(outcome=nm, k=k, n_test=n, mean_gain=d.mean(), min_dropone_gain=loo.min(), max_dropone_gain=loo.max(), top3_share_of_total=top3))
I = pd.DataFrame(inf); I.to_csv(f"{O}/influence.csv", index=False); print("\ninfluence of single test players on the gain (position mean minus Combine prior):"); print(I.round(4).to_string(index=False))
