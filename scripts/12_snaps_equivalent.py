import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
D, O = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(2027)
BASE=["forty","ten_yd_split","combine_weight"]; FEAT=["maint","peak_acc","d95"]; KS=[0,10,25,50,100]; LATE=100
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id")
f = pd.read_csv(f"{O}/forty_run_features.csv"); F = f.groupby("nfl_id")[FEAT].mean()
T = cr[BASE+["combine_position"]].join(F)
games = pd.read_csv(f"{D}/games.csv")
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False).merge(games[["game_id","season_type"]], on="game_id")
pp = pp[pp.season_type=="REG"].copy(); pp["pos"]=pp.nfl_id.map(cr.combine_position)
tabs={}
d=pp[pp.pos=="DL"].copy(); d["y"]=pd.to_numeric(d.player_get_off,errors="coerce"); tabs["DL get-off (lower=faster)"]=("DL",d[d.y.notna()])
w=pp[(pp.pos=="WR")&pp.route_ran.notna()&pp.separation_at_pass_forward.notna()&pp.cushion.notna()].copy()
Xd=pd.get_dummies(w[["route_ran","team_coverage_man_zone","lined_up_position"]].fillna("NA"),drop_first=True).astype(float); Xd["cushion"]=w.cushion.values
A=np.c_[np.ones(len(Xd)),Xd.values]; w["y"]=w.separation_at_pass_forward.values-A@np.linalg.lstsq(A,w.separation_at_pass_forward.values,rcond=None)[0]
tabs["WR adjusted separation"]=("WR",w)
o=pp[(pp.pos=="OL")&pp.pressure_allowed.notna()].copy(); o["y"]=o.pressure_allowed.astype(str).str.upper().isin(["TRUE","1","1.0"]).astype(float); tabs["OL pressure allowed"]=("OL",o)
sp=pd.read_csv(f"{O}/ingame_speed_play.csv"); sp=sp[sp.n>=20].copy(); sp["pos"]=sp.nfl_id.map(cr.combine_position); sp["y"]=sp.smax
for P in ["WR","DL","DB","OL"]: tabs[f"{P} in-game top speed"]=(P,sp[sp.pos==P])
def zs(M,mu,sd): return (M-mu)/sd
def fit_prior(ids, stats, cols, sig2):
    s=stats.loc[ids]; m=s["mean"].values; n=s["n"].values
    if cols:
        X=T.loc[ids,cols].values.astype(float); mu,sd=X.mean(0),X.std(0)+1e-9; X=np.c_[np.ones(len(ids)),zs(X,mu,sd)]
    else: X=np.ones((len(ids),1)); mu=sd=None
    tt=max(np.var(m)-np.mean(sig2/n),1e-9); wts=1/(0.5*tt+sig2/n)
    sw=np.sqrt(wts); b=np.linalg.lstsq(X*sw[:,None],m*sw,rcond=None)[0]
    r=m-X@b; p=X.shape[1]; N=len(ids)
    tau2=max((wts*(r**2*N/max(N-p,1)-sig2/n)).sum()/wts.sum(),1e-9)
    return b,mu,sd,tau2
def predict(b,mu,sd,pid,cols):
    if cols: x=np.r_[1,zs(T.loc[pid,cols].values.astype(float),mu,sd)]
    else: x=np.array([1.0])
    return float(x@b)
out=[]
for name,(P,df) in tabs.items():
    df=df.sort_values(["nfl_id","game_id","play_id"])
    ok=T[(T.combine_position==P)].dropna(subset=BASE+FEAT).index
    df=df[df.nfl_id.isin(ok)]
    g=df.groupby("nfl_id").y
    stats=pd.DataFrame({"n":g.size(),"mean":g.mean(),"var":g.var(ddof=1)})
    pool=stats[stats.n>=30].index.tolist(); test=stats[stats.n>=KS[-1]+LATE].index.tolist()
    if len(test)<15: print(f"[{name}] too few test players ({len(test)})"); continue
    ys={i:df[df.nfl_id==i].y.values for i in test}
    sig2_all=((stats.loc[pool,"n"]-1)*stats.loc[pool,"var"]).sum()/(stats.loc[pool,"n"]-1).sum()
    # full-pool parameters
    _,_,_,t_pos=fit_prior(pool,stats,[],sig2_all); _,_,_,t_base=fit_prior(pool,stats,BASE,sig2_all); _,_,_,t_shape=fit_prior(pool,stats,BASE+FEAT,sig2_all)
    t_base=max(t_base,0.02*t_pos); t_shape=max(t_shape,0.02*t_pos)
    E={k:{m:[] for m in ("raw","pos","base","shape")} for k in KS}; truth=[]
    for pid in test:
        rest=[i for i in pool if i!=pid]
        rs=stats.loc[rest]; sig2=((rs.n-1)*rs["var"]).sum()/(rs.n-1).sum()
        pri={}
        for arm,cols in (("pos",[]),("base",BASE),("shape",BASE+FEAT)):
            b,mu,sd,t2=fit_prior(rest,stats,cols,sig2); t2=max(t2,0.02*fit_prior(rest,stats,[],sig2)[3]) if arm!="pos" else t2
            pri[arm]=(predict(b,mu,sd,pid,cols),t2)
        y=ys[pid]; late=y[-LATE:].mean(); truth.append(late)
        for k in KS:
            ek=y[:k]
            for arm in ("pos","base","shape"):
                mu0,t2=pri[arm]
                post=mu0 if k==0 else (k/sig2*ek.mean()+mu0/t2)/(k/sig2+1/t2)
                E[k][arm].append((post-late)**2)
            E[k]["raw"].append(np.nan if k==0 else (ek.mean()-late)**2)
    n_t=len(test)
    print(f"\n[{name}] pool {len(pool)}, test {n_t} | sigma {np.sqrt(sig2_all):.3f}, tau_tot {np.sqrt(t_pos):.3f}, tau_after_combine {np.sqrt(t_base):.3f} | Combine explains {100*(1-t_base/t_pos):.0f}% of true between-player variance | n0 position-mean {sig2_all/t_pos:.0f} snaps, n0 Combine prior {sig2_all/t_base:.0f} snaps, with shape {sig2_all/t_shape:.0f}")
    print("   k   MSEraw   MSEpos   MSEcomb  MSEshape | pos-comb gain [95% CI]   | comb-shape gain [95% CI]")
    for k in KS:
        a={m:np.array(E[k][m]) for m in E[k]}
        def ci(x,y):
            d=x-y; bs=[d[rng.integers(0,n_t,n_t)].mean() for _ in range(2000)]; return d.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5)
        g1=ci(a["pos"],a["base"]); g2=ci(a["base"],a["shape"])
        raw=np.nanmean(a["raw"]) if k>0 else np.nan
        print(f"  {k:3d}  {raw:7.4f}  {a['pos'].mean():7.4f}  {a['base'].mean():7.4f}  {a['shape'].mean():7.4f} | {g1[0]:+.4f} [{g1[1]:+.4f},{g1[2]:+.4f}] | {g2[0]:+.4f} [{g2[1]:+.4f},{g2[2]:+.4f}]")
        out.append(dict(outcome=name,k=k,n_test=n_t,pool=len(pool),sigma=np.sqrt(sig2_all),tau_tot=np.sqrt(t_pos),tau_comb=np.sqrt(t_base),share_explained=1-t_base/t_pos,n0_pos=sig2_all/t_pos,n0_comb=sig2_all/t_base,mse_raw=raw,mse_pos=a['pos'].mean(),mse_comb=a['base'].mean(),mse_shape=a['shape'].mean(),gain_pos_comb=g1[0],lo=g1[1],hi=g1[2],gain_comb_shape=g2[0],lo2=g2[1],hi2=g2[2]))
pd.DataFrame(out).to_csv(f"{O}/snaps_equivalent_results.csv",index=False); print("\nsaved")
