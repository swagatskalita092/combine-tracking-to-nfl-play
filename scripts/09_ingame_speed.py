import sys, pandas as pd, numpy as np, warnings, time
warnings.filterwarnings("ignore")
D, OUT = sys.argv[1], sys.argv[2]
t0=time.time()
g = pd.read_csv(f"{D}/games.csv"); reg=set(g[g.season_type=="REG"].game_id)
parts=[]
for y in (2023,2024,2025):
    for ch in pd.read_csv(f"{D}/game_tracking_{y}.csv", usecols=["game_id","play_id","nfl_id","s","a"], chunksize=3_000_000):
        ch=ch[ch.game_id.isin(reg)]
        parts.append(ch.groupby(["game_id","play_id","nfl_id"]).agg(smax=("s","max"),amax=("a","max"),n=("s","size")).reset_index())
    print(y,"done",round(time.time()-t0),"s",flush=True)
p=pd.concat(parts).groupby(["game_id","play_id","nfl_id"]).agg(smax=("smax","max"),amax=("amax","max"),n=("n","sum")).reset_index()
p.to_csv(OUT.replace(".csv","_play.csv"),index=False)
p=p[p.n>=20]
print("player-plays:",len(p),"| players:",p.nfl_id.nunique(),flush=True)
def summ(d): return pd.Series({"n_plays":len(d),"s_p95":d.smax.quantile(.95),"s_p99":d.smax.quantile(.99),"a_p95":d.amax.quantile(.95)})
P=p.groupby("nfl_id").apply(summ)
for nm,mask in (("odd",p.game_id%2==1),("even",p.game_id%2==0)):
    Q=p[mask].groupby("nfl_id").apply(summ); P[f"s_p95_{nm}"]=Q.s_p95; P[f"a_p95_{nm}"]=Q.a_p95
P.to_csv(OUT)
print(P.describe().round(2).to_string())
ok=P[P.n_plays>=100].dropna(subset=["s_p95_odd","s_p95_even"])
print("split-half (odd/even games) corr, players>=100 plays (n=%d): s_p95 r=%.2f | a_p95 r=%.2f"%(len(ok),ok.s_p95_odd.corr(ok.s_p95_even),ok.a_p95_odd.corr(ok.a_p95_even)))
print("done",round(time.time()-t0),"s",flush=True)
