# WR adjusted separation with the route/coverage/alignment/cushion adjustment refit WITHOUT each held-out player (closes the
# leakage noted in review: in 12_snaps_equivalent.py the adjustment is fit once on all WR plays).  Compares to the original errors.
import sys, io, contextlib, numpy as np, pandas as pd
D, O = sys.argv[1], sys.argv[2]
SRC = globals().get("SRC12") or open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "12_snaps_equivalent.py")).read()
ns = {}; sys.argv = ["x", D, O]
with contextlib.redirect_stdout(io.StringIO()): exec(compile(SRC.split("out=[]")[0], "12_setup", "exec"), ns)
T, tabs, fit_prior, predict, BASE, FEAT, KS, LATE = (ns[k] for k in ("T", "tabs", "fit_prior", "predict", "BASE", "FEAT", "KS", "LATE"))
P, w = tabs["WR adjusted separation"]
w = w.sort_values(["nfl_id", "game_id", "play_id"]).reset_index(drop=True)
Xd = pd.get_dummies(w[["route_ran", "team_coverage_man_zone", "lined_up_position"]].fillna("NA"), drop_first=True).astype(float); Xd["cushion"] = w.cushion.values
A = np.c_[np.ones(len(Xd)), Xd.values]; sep = w.separation_at_pass_forward.values; ids_all = w.nfl_id.values
ok = T[(T.combine_position == P)].dropna(subset=BASE + FEAT).index
keep = np.isin(ids_all, ok)
st0 = w[keep].groupby("nfl_id").y.agg(n="size"); pool = st0[st0.n >= 30].index.tolist(); test = st0[st0.n >= KS[-1] + LATE].index.tolist()
rng = np.random.default_rng(2027); E = {k: {"pos": [], "base": []} for k in KS}
for pid in test:
    beta = np.linalg.lstsq(A[ids_all != pid], sep[ids_all != pid], rcond=None)[0]
    y = sep - A @ beta; df = pd.DataFrame({"nfl_id": ids_all, "y": y})[keep]
    g = df.groupby("nfl_id").y; st = pd.DataFrame({"n": g.size(), "mean": g.mean(), "var": g.var(ddof=1)})
    rest = [i for i in pool if i != pid]; rs = st.loc[rest]; sig2 = ((rs.n - 1) * rs["var"]).sum() / (rs.n - 1).sum()
    pri = {}
    for arm, cols in (("pos", []), ("base", BASE)):
        b, mu, sd, t2 = fit_prior(rest, st, cols, sig2)
        if arm != "pos": t2 = max(t2, 0.02 * fit_prior(rest, st, [], sig2)[3])
        pri[arm] = (predict(b, mu, sd, pid, cols), t2)
    yy = df[df.nfl_id == pid].y.values; late = yy[-LATE:].mean()
    for k in KS:
        for arm in pri:
            mu0, t2 = pri[arm]; post = mu0 if k == 0 else (k / sig2 * yy[:k].mean() + mu0 / t2) / (k / sig2 + 1 / t2)
            E[k][arm].append((post - late) ** 2)
orig = pd.read_csv(f"{O}/snaps_equivalent_results.csv"); orig = orig[orig.outcome == "WR adjusted separation"].set_index("k")
rows = []
for k in KS:
    a, b = np.array(E[k]["pos"]), np.array(E[k]["base"]); d = a - b; n = len(d)
    bs = [d[rng.integers(0, n, n)].mean() for _ in range(2000)]
    rows.append(dict(k=k, n_test=n, mse_pos_holdout=a.mean(), mse_comb_holdout=b.mean(), gain_holdout=d.mean(), lo_holdout=np.percentile(bs, 2.5), hi_holdout=np.percentile(bs, 97.5),
                     mse_pos_orig=orig.loc[k, "mse_pos"], mse_comb_orig=orig.loc[k, "mse_comb"], gain_orig=orig.loc[k, "gain_pos_comb"], lo_orig=orig.loc[k, "lo"], hi_orig=orig.loc[k, "hi"]))
R = pd.DataFrame(rows); R.to_csv(f"{O}/wr_adjustment_holdout.csv", index=False)
pd.set_option("display.width", 250); print("WR separation: adjustment refit without the held-out player vs original (adjustment fit on all WR plays)"); print(R.round(4).to_string(index=False))
