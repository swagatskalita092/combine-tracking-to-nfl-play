import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
D, O = sys.argv[1], sys.argv[2]
rng=np.random.default_rng(2027)
STOP=["forty","ten_yd_split","combine_weight"]; SENS=["vmax","v10","combine_weight"]; KS=[0,10,25,50,100]; LATE=100
cr=pd.read_csv(f"{D}/combine_results.csv",na_values=["NA"]).set_index("nfl_id")
f=pd.read_csv(f"{O}/forty_run_features.csv"); F=f.groupby("nfl_id")[["vmax","v10"]].mean()
T=cr[["forty","ten_yd_split","combine_weight","combine_position"]].join(F)
print("COVERAGE by position (n players): stopwatch-complete | sensor-complete | either | sensor only (no complete stopwatch) | stopwatch only")
for P,g in T.groupby("combine_position"):
    s=g[STOP].notna().all(axis=1); e=g[SENS].notna().all(axis=1)
    print(f"  {P}: total {len(g)} | {s.sum()} | {e.sum()} | {(s|e).sum()} | {(e&~s).sum()} | {(s&~e).sum()}")
s=T[STOP].notna().all(axis=1); e=T[SENS].notna().all(axis=1)
print(f"  ALL: total {len(T)} | {s.sum()} | {e.sum()} | {(s|e).sum()} | sensor-only {(e&~s).sum()} | stopwatch-only {(s&~e).sum()}")
print("corr tracked vmax vs official forty (all):", round(T.vmax.corr(T.forty),2), "| tracked v10 vs official ten_yd:", round(T.v10.corr(T.ten_yd_split),2))
games=pd.read_csv(f"{D}/games.csv")
pp=pd.read_csv(f"{D}/player_play.csv",low_memory=False).merge(games[["game_id","season_type"]],on="game_id")
pp=pp[pp.season_type=="REG"].copy(); pp["pos"]=pp.nfl_id.map(cr.combine_position)
tabs={}
d=pp[pp.pos=="DL"].copy(); d["y"]=pd.to_numeric(d.player_get_off,errors="coerce"); tabs["DL get-off"]=("DL",d[d.y.notna()])
w=pp[(pp.pos=="WR")&pp.route_ran.notna()&pp.separation_at_pass_forward.notna()&pp.cushion.notna()].copy()
Xd=pd.get_dummies(w[["route_ran","team_coverage_man_zone","lined_up_position"]].fillna("NA"),drop_first=True).astype(float); Xd["cushion"]=w.cushion.values
A=np.c_[np.ones(len(Xd)),Xd.values]; w["y"]=w.separation_at_pass_forward.values-A@np.linalg.lstsq(A,w.separation_at_pass_forward.values,rcond=None)[0]; tabs["WR adj separation"]=("WR",w)
sp=pd.read_csv(f"{O}/ingame_speed_play.csv"); sp=sp[sp.n>=20].copy(); sp["pos"]=sp.nfl_id.map(cr.combine_position); sp["y"]=sp.smax
for P in ["WR","DL","DB","OL"]: tabs[f"{P} top speed"]=(P,sp[sp.pos==P])
def fit_prior(ids,stats,cols,sig2):
    s=stats.loc[ids]; m=s["mean"].values; n=s["n"].values
    if cols: X=T.loc[ids,cols].values.astype(float); mu,sd=X.mean(0),X.std(0)+1e-9; X=np.c_[np.ones(len(ids)),(X-mu)/sd]
    else: X=np.ones((len(ids),1)); mu=sd=None
    tt=max(np.var(m)-np.mean(sig2/n),1e-9); wts=1/(0.5*tt+sig2/n); sw=np.sqrt(wts); b=np.linalg.lstsq(X*sw[:,None],m*sw,rcond=None)[0]
    r=m-X@b; N=len(ids); p=X.shape[1]; tau2=max((wts*(r**2*N/max(N-p,1)-sig2/n)).sum()/wts.sum(),1e-9); return b,mu,sd,tau2
def pred(b,mu,sd,pid,cols):
    x=np.r_[1,(T.loc[pid,cols].values.astype(float)-mu)/sd] if cols else np.array([1.0]); return float(x@b)
res=[]
print("\nEXPLORATORY: stopwatch prior vs sensor prior, same players (LOO, late=last 100 plays). gain = MSE(stop)-MSE(sensor); positive favours sensor")
for name,(P,df) in tabs.items():
    df=df.sort_values(["nfl_id","game_id","play_id"])
    ok=T[(T.combine_position==P)].dropna(subset=STOP+SENS).index; df=df[df.nfl_id.isin(ok)]
    g=df.groupby("nfl_id").y; st=pd.DataFrame({"n":g.size(),"mean":g.mean(),"var":g.var(ddof=1)})
    pool=st[st.n>=30].index.tolist(); test=st[st.n>=KS[-1]+LATE].index.tolist()
    if len(test)<15: continue
    ys={i:df[df.nfl_id==i].y.values for i in test}
    sig2_all=((st.loc[pool,"n"]-1)*st.loc[pool,"var"]).sum()/(st.loc[pool,"n"]-1).sum()
    tp=fit_prior(pool,st,[],sig2_all)[3]; ts=max(fit_prior(pool,st,STOP,sig2_all)[3],0.02*tp); te=max(fit_prior(pool,st,SENS,sig2_all)[3],0.02*tp)
    E={k:{a:[] for a in ("pos","stop","sens")} for k in KS}
    for pid in test:
        rest=[i for i in pool if i!=pid]; rs=st.loc[rest]; sig2=((rs.n-1)*rs["var"]).sum()/(rs.n-1).sum(); tpos=fit_prior(rest,st,[],sig2)[3]
        pri={}
        for arm,cols in (("pos",[]),("stop",STOP),("sens",SENS)):
            b,mu,sd,t2=fit_prior(rest,st,cols,sig2); t2=max(t2,0.02*tpos) if arm!="pos" else t2; pri[arm]=(pred(b,mu,sd,pid,cols),t2)
        y=ys[pid]; late=y[-LATE:].mean()
        for k in KS:
            for arm in pri:
                mu0,t2=pri[arm]; post=mu0 if k==0 else (k/sig2*y[:k].mean()+mu0/t2)/(k/sig2+1/t2); E[k][arm].append((post-late)**2)
    n=len(test)
    print(f"\n[{name}] pool {len(pool)}, test {n} | Combine-explained true variance: stopwatch {100*(1-ts/tp):.0f}%, sensor {100*(1-te/tp):.0f}% | n0: stopwatch {sig2_all/ts:.0f}, sensor {sig2_all/te:.0f}")
    for k in (0,25,100):
        a={m:np.array(E[k][m]) for m in E[k]}; d=a["stop"]-a["sens"]; bs=[d[rng.integers(0,n,n)].mean() for _ in range(2000)]
        print(f"   k={k:3d}  MSE pos {a['pos'].mean():.4f} | stopwatch {a['stop'].mean():.4f} | sensor {a['sens'].mean():.4f} | gain {d.mean():+.4f} [{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}]")
    for k in KS:
        a={m:np.array(E[k][m]) for m in E[k]}; d=a["stop"]-a["sens"]; bs=[d[rng.integers(0,n,n)].mean() for _ in range(1000)]
        d2=a["pos"]-a["sens"]; d3=a["pos"]-a["stop"]; ix=[rng.integers(0,n,n) for _ in range(2000)]
        b2=[d2[j].mean() for j in ix]; b3=[d3[j].mean() for j in ix]
        res.append(dict(outcome=name,k=k,n_test=n,mse_pos=a["pos"].mean(),mse_stop=a["stop"].mean(),mse_sens=a["sens"].mean(),gain=d.mean(),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5),
            gain_sens_vs_pos=d2.mean(),lo_sens_vs_pos=np.percentile(b2,2.5),hi_sens_vs_pos=np.percentile(b2,97.5),gain_stop_vs_pos=d3.mean(),lo_stop_vs_pos=np.percentile(b3,2.5),hi_stop_vs_pos=np.percentile(b3,97.5),share_stop=1-ts/tp,share_sens=1-te/tp,n0_stop=sig2_all/ts,n0_sens=sig2_all/te))
pd.DataFrame(res).to_csv(f"{O}/sensor_vs_stopwatch.csv",index=False); print("\nsaved")
