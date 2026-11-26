import sys, os, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D, F = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 200, "display.max_columns", 40)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id")
f = pd.read_csv(F)
f["drill"]=f.drill.replace({"SPEED_OUT_LEFT":"SPEED_OUT_ROUTE_LEFT"})
keep = ["COMEBACK_ROUTE_RIGHT","DAGGER_ROUTE_LEFT","POST_CORNER_ROUTE_LEFT","SLANT_ROUTE_LEFT","SLOT_SAIL_ROUTE_RIGHT","SLOT_STRIKE_ROUTE_LEFT","SPEED_OUT_ROUTE_LEFT","CURL_ROUTE_RIGHT"]
f = f[f.drill.isin(keep) & (f.turn_deg>=40)].copy()
f = f.sort_values("attempt").groupby(["nfl_id","drill"]).head(1)   # one rep per player-drill
f["speed_regain"] = f.exit_speed - f.min_speed
metrics = ["exit_speed","min_speed","peak_turn_rate","turn_dur","speed_regain","reaccel_post"]
z = f.copy()
for m in metrics: z[m] = z.groupby("drill")[m].transform(lambda s:(s-s.mean())/s.std())
cnt = z.groupby("nfl_id").size()
elig = cnt[cnt>=4].index
print("break reps:", len(z), "| players with >=4 break drills:", len(elig), "| median drills per player:", cnt.median())
rng = np.random.default_rng(7)
def sb(r): return 2*r/(1+r)
print("\nsplit-half reliability across routes (200 random splits of each player's drills), Spearman-Brown:")
res={}
for m in metrics:
    rs=[]
    for _ in range(200):
        a=[];b=[]
        for nid,g in z[z.nfl_id.isin(elig)].groupby("nfl_id"):
            v=g[m].dropna().values
            if len(v)<4: continue
            idx=rng.permutation(len(v)); h=len(v)//2
            a.append(v[idx[:h]].mean()); b.append(v[idx[h:2*h]].mean())
        rs.append(np.corrcoef(a,b)[0,1])
    res[m]=(np.mean(rs), sb(np.mean(rs)))
    print(f"  {m:15s} r={res[m][0]:.2f}  SB={res[m][1]:.2f}")
P = z.groupby("nfl_id")[metrics].mean().loc[elig].join(cr[["forty","ten_yd_split","combine_weight","vertical","broad_jump","draft_year"]])
print("\ncorrelation of player-level mean z with conventional measures (n=%d):"%len(P))
print(P[metrics+["forty","ten_yd_split","combine_weight","vertical","broad_jump"]].corr().loc[metrics,["forty","ten_yd_split","combine_weight","vertical","broad_jump"]].round(2))
# how much of each metric is NOT explained by forty+weight (R^2)
import numpy.linalg as la
print("\nR^2 of metric on forty+ten_yd+weight (complete cases):")
Q=P.dropna(subset=["forty","ten_yd_split","combine_weight"])
X=np.c_[np.ones(len(Q)),Q.forty,Q.ten_yd_split,Q.combine_weight]
for m in metrics:
    y=Q[m].values; b=la.lstsq(X,y,rcond=None)[0]; r2=1-((y-X@b)**2).sum()/((y-y.mean())**2).sum(); print(f"  {m:15s} R2={r2:.2f}  (n={len(Q)})")
z.to_csv(os.path.join(os.path.dirname(F),"wr_break_reps_z.csv"), index=False)
P.to_csv(os.path.join(os.path.dirname(F),"wr_player_break_features.csv"))
