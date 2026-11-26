# (a) Which Combine variable carries the prior? Ablation of the Combine prior (full / weight only / 40 time + 10-yd split only),
#     same players, same LOO code as 12_snaps_equivalent.py.  (b) Player-bootstrap ranges for 'share explained' and n0.
#     (c) Within-position agreement of tracked and official speed.   Outputs: ablation.csv, n0_bootstrap.csv, sensor_agreement_by_position.csv
import sys, io, contextlib, numpy as np, pandas as pd
D, O = sys.argv[1], sys.argv[2]
SRC = globals().get("SRC12") or open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "12_snaps_equivalent.py")).read()   # SRC12 is set by the notebook
SRC = SRC.replace('pd.DataFrame(out).to_csv(f"{O}/snaps_equivalent_results.csv",index=False); print("\\nsaved")', 'pass')
FULL = ["forty", "ten_yd_split", "combine_weight"]
SRC = SRC.replace('T = cr[BASE+["combine_position"]]', 'T = cr[["forty","ten_yd_split","combine_weight","combine_position"]]')
SRC = SRC.replace("dropna(subset=BASE+FEAT)", 'dropna(subset=["forty","ten_yd_split","combine_weight"]+FEAT)')   # keep identical players across arms
def run(base):
    s = SRC.replace('BASE=["forty","ten_yd_split","combine_weight"]', f"BASE={base!r}")
    ns = {"__name__": "__main__"}
    sys.argv = ["x", D, O]
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(s, "12_patched", "exec"), ns)
    return pd.DataFrame(ns["out"])
rng = np.random.default_rng(2027)
arms = {"full (40, 10-yd, weight)": FULL, "weight only": ["combine_weight"], "40 time + 10-yd split only": ["forty", "ten_yd_split"]}
rows = []
for lab, base in arms.items():
    r = run(base)
    r = r[r.k.isin([0, 25])][["outcome", "k", "mse_pos", "mse_comb", "gain_pos_comb", "lo", "hi", "share_explained", "n0_comb"]]; r.insert(0, "prior", lab); rows.append(r)
A = pd.concat(rows); A.to_csv(f"{O}/ablation.csv", index=False)
pd.set_option("display.width", 250)
P = A.pivot_table(index=["outcome", "k"], columns="prior", values="mse_comb"); P["position mean"] = A[A.prior.str.startswith("full")].set_index(["outcome", "k"]).mse_pos
print("MSE vs last-100 mean (lower is better):"); print(P.round(4).to_string())
S = A.pivot_table(index="outcome", columns="prior", values="share_explained"); print("\nshare of true between-player variance explained:"); print((S * 100).round(0).to_string())
# (b) bootstrap of share explained and n0 (player bootstrap over the pool, full prior)
import importlib
ns = {}
src = (globals().get("SRC12") or open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "12_snaps_equivalent.py")).read()).split("out=[]")[0]   # setup + helper functions only
sys.argv = ["x", D, O]
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, "12_setup", "exec"), ns)
T, tabs, fit_prior, BASE_, FEAT_ = ns["T"], ns["tabs"], ns["fit_prior"], ns["BASE"], ns["FEAT"]
brow = []
for name, (Pos, df) in tabs.items():
    df = df.sort_values(["nfl_id", "game_id", "play_id"]); ok = T[(T.combine_position == Pos)].dropna(subset=BASE_ + FEAT_).index; df = df[df.nfl_id.isin(ok)]
    g = df.groupby("nfl_id").y; st = pd.DataFrame({"n": g.size(), "mean": g.mean(), "var": g.var(ddof=1)}); pool = st[st.n >= 30].index.to_numpy()
    if (st.n >= 200).sum() < 15: continue
    sh, n0 = [], []
    for b in range(500):
        ids = pool[rng.integers(0, len(pool), len(pool))]
        # resampled players share one row of T/stats; fit_prior only needs T/stats rows by id, duplicates are fine for .loc
        s2 = ((st.loc[ids, "n"] - 1) * st.loc[ids, "var"]).sum() / (st.loc[ids, "n"] - 1).sum()
        tp = fit_prior(list(ids), st, [], s2)[3]; tb = max(fit_prior(list(ids), st, BASE_, s2)[3], 0.02 * tp)
        sh.append(1 - tb / tp); n0.append(s2 / tb)
    s2 = ((st.loc[pool, "n"] - 1) * st.loc[pool, "var"]).sum() / (st.loc[pool, "n"] - 1).sum()
    brow.append(dict(outcome=name, share_lo=np.percentile(sh, 2.5), share_hi=np.percentile(sh, 97.5), n0_lo=np.percentile(n0, 2.5), n0_hi=np.percentile(n0, 97.5)))
B = pd.DataFrame(brow); B.to_csv(f"{O}/n0_bootstrap.csv", index=False); print("\nplayer-bootstrap 95% ranges (pool resampling):"); print(B.round(2).to_string(index=False))
# (c) sensor vs stopwatch agreement within position
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id"); f = pd.read_csv(f"{O}/forty_run_features.csv").groupby("nfl_id")[["vmax", "v10"]].mean()
X = cr[["forty", "ten_yd_split", "combine_position"]].join(f).dropna(); rows = []
for pos, g in list(X.groupby("combine_position")) + [("ALL", X)]:
    rows.append(dict(position=pos, n=len(g), r_vmax_vs_forty=g.vmax.corr(g.forty), r_v10_vs_ten_yd_split=g.v10.corr(g.ten_yd_split)))
C = pd.DataFrame(rows); C.to_csv(f"{O}/sensor_agreement_by_position.csv", index=False); print("\ntracked vs official, by position:"); print(C.round(2).to_string(index=False))
