import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id")
ct = pd.read_csv(f"{D}/combine_tracking.csv")
p = ct[ct.entity_type=="PLAYER"]
# 1) forty-yard dash: tracked max speed vs official forty
fd = p[p.drill_name=="FORTY_YARD_DASH"].groupby(["nfl_id","event_id"]).agg(vmax=("s","max"), n=("s","size"), dur=("time","size")).reset_index()
fd = fd.groupby("nfl_id").vmax.max().to_frame().join(cr[["forty","ten_yd_split","combine_position"]]).dropna()
print("FORTY tracked max speed vs official forty, corr by position:")
print(fd.groupby("combine_position").apply(lambda g: pd.Series({"n":len(g),"r_vmax_forty":g.vmax.corr(g.forty),"mean_vmax":g.vmax.mean()})).round(2))
# 2) WR route drills: top speed per player-drill
wr = set(cr[cr.combine_position=="WR"].index)
w = p[p.nfl_id.isin(wr)&(p.drill_type=="SKILL_DRILLS_WR")&(~p.drill_name.isin(["GAUNTLET_DRILL"]))]
t = w.groupby(["nfl_id","drill_name","event_id"]).s.max().reset_index().sort_values("event_id").groupby(["nfl_id","drill_name"]).head(1)
t["z"] = t.groupby("drill_name").s.transform(lambda s:(s-s.mean())/s.std())
cnt=t.groupby("nfl_id").size(); el=cnt[cnt>=6].index
rng=np.random.default_rng(1); rs=[]
for _ in range(200):
    a=[];b=[]
    for nid,g in t[t.nfl_id.isin(el)].groupby("nfl_id"):
        v=g.z.values; i=rng.permutation(len(v)); h=len(v)//2; a.append(v[i[:h]].mean()); b.append(v[i[h:2*h]].mean())
    rs.append(np.corrcoef(a,b)[0,1])
r=np.mean(rs); print(f"\nWR route top-speed split-half r={r:.2f}, SB={2*r/(1+r):.2f} (n players={len(el)})")
pm = t.groupby("nfl_id").z.mean().to_frame("topspeed_z").join(cr[["forty","ten_yd_split"]]).dropna()
print("corr(top speed in routes, forty) =", round(pm.topspeed_z.corr(pm.forty),2), "| n", len(pm))
# 3) timestamps/sampling sanity: dt distribution in a route event
g = w[w.event_id==w.event_id.iloc[0]]
print("\nrows in first route event:", len(g), "| dt:", pd.to_datetime(g.time, format="mixed").diff().dt.total_seconds().round(2).value_counts().head(3).to_dict())
print("s vs dis*10 check (corr):", round(np.corrcoef(g.s, g.dis*10)[0,1],3), "| mean s", round(g.s.mean(),2), "mean dis*10", round((g.dis*10).mean(),2))
