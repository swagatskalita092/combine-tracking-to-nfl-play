import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D, OUT = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 220, "display.max_columns", 60, "display.max_rows", 120)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"])
wr = set(cr[cr.combine_position=="WR"].nfl_id)
ct = pd.read_csv(f"{D}/combine_tracking.csv")
ct = ct[(ct.entity_type=="PLAYER") & ct.nfl_id.isin(wr) & (ct.drill_type=="SKILL_DRILLS_WR")].copy()
ct["drill"] = ct.drill_name.replace({"OVER_THE_SHOULDER_ADJUST":"OVER_SHOULDER_ADJUST"})
ct = ct[~ct.drill.isin(["GAUNTLET_DRILL","OVER_SHOULDER_ADJUST"])]
ct["t"] = pd.to_datetime(ct.time, format="mixed")
def smooth(v, k=3): return pd.Series(v).rolling(k, center=True, min_periods=1).mean().values
rows=[]
for (eid,nid), g in ct.sort_values("t").groupby(["event_id","nfl_id"]):
    s = g.s.values; n=len(s)
    if n < 20: continue
    on = np.argmax(s>1.0) if (s>1.0).any() else None
    if on is None or on > n-15: continue
    th = np.degrees(np.unwrap(np.radians(smooth(g.dir.values))))
    om = np.gradient(th)/0.1                      # deg/s
    om_s = smooth(om)
    acc = smooth(np.gradient(smooth(s))/0.1)      # yd/s^2 from speed
    lo, hi = on+4, n-4
    if hi<=lo: continue
    c = lo + int(np.argmax(np.abs(om_s[lo:hi])))
    a0, a1 = max(on, c-8), min(n-1, c+8)
    turn = abs(th[a1]-th[a0])
    pre = s[max(on,c-10):max(on+1,c-4)].mean()
    smin = s[max(on,c-6):min(n,c+7)].min()
    dec = -acc[max(on,c-10):c+1].min()
    rea = acc[c:min(n,c+11)].max()
    exitv = s[min(n-1,c+10)]
    half = np.abs(om_s) >= 0.5*np.abs(om_s[c])
    dur = half[max(0,c-8):min(n,c+9)].sum()*0.1
    rows.append(dict(drill=g.drill.iloc[0], nfl_id=nid, event_id=eid, attempt=g.attempt.iloc[0], draft_year=g.draft_year.iloc[0],
        n=n, onset=on, c_idx=c, t_break=(c-on)*0.1, turn_deg=turn, peak_turn_rate=abs(om_s[c]), stem_speed=pre, min_speed=smin,
        retention=smin/pre if pre>0 else np.nan, decel_pre=dec, reaccel_post=rea, exit_speed=exitv, turn_dur=dur, top_speed=s.max(),
        x_break=g.x.values[c], y_break=g.y.values[c]))
f = pd.DataFrame(rows); f.to_csv(OUT, index=False)
print("reps:", len(f), "| players:", f.nfl_id.nunique())
sm = f.groupby("drill").agg(reps=("nfl_id","size"), turn=("turn_deg","median"), t_break=("t_break","median"), stem=("stem_speed","median"),
    retention=("retention","median"), decel=("decel_pre","median"), reaccel=("reaccel_post","median"), exitv=("exit_speed","median"), top=("top_speed","median"))
print(sm.round(2))
print("\nshare of reps with turn>=40 deg by drill:"); print((f.assign(b=f.turn_deg>=40).groupby("drill").b.mean()).round(2).to_dict())
