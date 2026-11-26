import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
D, O = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(2027)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id")
f = pd.read_csv(f"{O}/forty_run_features.csv")
F = f.groupby("nfl_id")[["maint","peak_acc","d95","vmax"]].mean()
sp = pd.read_csv(f"{O}/ingame_speed.csv").set_index("nfl_id")
games = pd.read_csv(f"{D}/games.csv")
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False).merge(games[["game_id","season_type"]], on="game_id")
pp = pp[pp.season_type=="REG"].copy(); pp["pos"] = pp.nfl_id.map(cr.combine_position)
BASE=["forty","ten_yd_split","combine_weight"]; FEAT=["maint","peak_acc","d95"]
T = cr[BASE+["combine_position"]].join(F).dropna(subset=BASE+FEAT)
print("players with baseline + 40-dash shape features:", len(T), T.combine_position.value_counts().to_dict())

def wls(X,y,w):
    sw=np.sqrt(w); return np.linalg.lstsq(X*sw[:,None], y*sw, rcond=None)[0]
def wr2(y,yh,w,ybar): return 1-(w*(y-yh)**2).sum()/(w*(y-ybar)**2).sum()
def zs(M): return (M-M.mean(0))/M.std(0)
def design(df, pooled):
    B=zs(df[BASE].values); Fm=zs(df[FEAT].values)
    if pooled: B=np.c_[B, pd.get_dummies(df.combine_position,drop_first=True).values.astype(float)]
    one=np.ones((len(df),1)); return np.c_[one,B], Fm
def pcorr(Xb,Fm,y,w):
    out=[]
    ry=y-Xb@wls(Xb,y,w)
    for j in range(Fm.shape[1]):
        rf=Fm[:,j]-Xb@wls(Xb,Fm[:,j],w)
        a=np.average(rf,weights=w); b=np.average(ry,weights=w)
        out.append(((w*(rf-a)*(ry-b)).sum())/np.sqrt((w*(rf-a)**2).sum()*(w*(ry-b)**2).sum()))
    return np.array(out)
def analyze(name, df, y, w, pooled=False, B=1000):
    Xb,Fm=design(df,pooled); Xf=np.c_[Xb,Fm]; n=len(df); y=np.asarray(y,float); w=np.asarray(w,float)
    yb=np.average(y,weights=w)
    r2b=wr2(y,Xb@wls(Xb,y,w),w,yb); r2f=wr2(y,Xf@wls(Xf,y,w),w,yb); d_in=r2f-r2b
    cvb=[];cvf=[]
    for rep in range(20):
        idx=rng.permutation(n); folds=np.array_split(idx,5); sb=sf=sst=0
        for k in range(5):
            te=folds[k]; tr=np.setdiff1d(idx,te); ybar=np.average(y[tr],weights=w[tr])
            pb=Xb[te]@wls(Xb[tr],y[tr],w[tr]); pf=Xf[te]@wls(Xf[tr],y[tr],w[tr])
            sb+=(w[te]*(y[te]-pb)**2).sum(); sf+=(w[te]*(y[te]-pf)**2).sum(); sst+=(w[te]*(y[te]-ybar)**2).sum()
        cvb.append(1-sb/sst); cvf.append(1-sf/sst)
    cvb,cvf=np.mean(cvb),np.mean(cvf)
    cnt=0
    for _ in range(1000):
        Fp=Fm[rng.permutation(n)]; Xp=np.c_[Xb,Fp]
        dp=wr2(y,Xp@wls(Xp,y,w),w,yb)-r2b; cnt+= dp>=d_in
    pval=(1+cnt)/1001
    pc=pcorr(Xb,Fm,y,w); bs=[]
    for _ in range(B):
        i=rng.integers(0,n,n); bs.append(pcorr(Xb[i],Fm[i],y[i],w[i]))
    lo,hi=np.nanpercentile(bs,[2.5,97.5],axis=0)
    print(f"\n[{name}] n={n}  baseline R2(in-sample)={r2b:.3f}  +shape: in-sample gain={d_in:.3f}  CV R2 base={cvb:.3f} full={cvf:.3f} CV gain={cvf-cvb:+.3f}  permutation p={pval:.3f}")
    print("   partial corr (controlling baseline), 95% player-bootstrap CI: "+" | ".join(f"{FEAT[j]} {pc[j]:+.2f} [{lo[j]:+.2f},{hi[j]:+.2f}]" for j in range(3)))
    return dict(outcome=name,n=n,base_r2=r2b,gain_in=d_in,cv_base=cvb,cv_full=cvf,cv_gain=cvf-cvb,perm_p=pval,**{f"pc_{FEAT[j]}":pc[j] for j in range(3)})
res=[]
# ---- O1 in-game top speed (z within position)
S=sp[sp.n_plays>=100].join(T,how="inner")
S["y"]=S.groupby("combine_position").s_p95.transform(lambda s:(s-s.mean())/s.std())
print("\nSANITY: corr(in-game p95 top speed, combine tracked vmax) within position:", S.groupby("combine_position").apply(lambda g: round(g.s_p95.corr(g.vmax),2)).to_dict())
print("SANITY: corr(in-game top speed, official forty) within position:", S.groupby("combine_position").apply(lambda g: round(g.s_p95.corr(g.forty),2)).to_dict())
res.append(analyze("O1 in-game top speed (all positions, pooled)", S, S.y, np.ones(len(S)), pooled=True))
for P in ["WR","DB","DL","OL"]:
    Q=S[S.combine_position==P]
    if len(Q)>=40: res.append(analyze(f"O1 in-game top speed ({P})", Q, Q.y, np.ones(len(Q)), pooled=False, B=500))
# ---- O2 WR adjusted separation
w_=pp[(pp.pos=="WR")&pp.route_ran.notna()&pp.separation_at_pass_forward.notna()&pp.cushion.notna()].copy()
Xd=pd.get_dummies(w_[["route_ran","team_coverage_man_zone","lined_up_position"]].fillna("NA"),drop_first=True).astype(float); Xd["cushion"]=w_.cushion.values
A=np.c_[np.ones(len(Xd)),Xd.values]; bb=np.linalg.lstsq(A,w_.separation_at_pass_forward.values,rcond=None)[0]
w_["res"]=w_.separation_at_pass_forward.values-A@bb
def eb(df,col,minn,sig2=None):
    g=df.groupby("nfl_id")[col].agg(["mean","size"]); g=g[g["size"]>=minn]
    s2=df[col].var() if sig2 is None else sig2
    tau2=max(g["mean"].var()-(s2/g["size"]).mean(),1e-4); g["w"]=1/(tau2+s2/g["size"]); return g,tau2,s2
g2,tau2,s2=eb(w_,"res",50)
for nm,mk in (("odd",w_.game_id%2==1),("even",w_.game_id%2==0)): g2[nm]=w_[mk].groupby("nfl_id").res.mean()
print(f"\nO2 WR separation residual: players>=50 routes {len(g2)}, between-player SD {np.sqrt(tau2):.2f} yd, play-level SD {np.sqrt(s2):.2f} yd, odd/even-game split-half r={g2.odd.corr(g2.even):.2f}")
Q=g2.join(T,how="inner"); Q=Q[Q.combine_position=="WR"]
res.append(analyze("O2 WR adjusted separation", Q, Q["mean"], Q.w, pooled=False))
# ---- O3 DL get-off
d_=pp[(pp.pos=="DL")].copy(); d_["go"]=pd.to_numeric(d_.player_get_off,errors="coerce"); d_=d_[d_.go.notna()]
print("\nO3 DL player_get_off distribution:", d_.go.describe().round(3).to_dict())
g3,tau3,s3=eb(d_,"go",50)
for nm,mk in (("odd",d_.game_id%2==1),("even",d_.game_id%2==0)): g3[nm]=d_[mk].groupby("nfl_id").go.mean()
print(f"O3 players>=50 snaps {len(g3)}, between SD {np.sqrt(tau3):.3f}, play SD {np.sqrt(s3):.3f}, split-half r={g3.odd.corr(g3.even):.2f}")
Q=g3.join(T,how="inner"); Q=Q[Q.combine_position=="DL"]
res.append(analyze("O3 DL get-off", Q, Q["mean"], Q.w, pooled=False))
# ---- O4 OL pressure allowed (secondary)
o_=pp[(pp.pos=="OL")&pp.pressure_allowed.notna()].copy(); o_["pr"]=o_.pressure_allowed.astype(str).str.upper().isin(["TRUE","1","1.0"]).astype(float)
p0=o_.pr.mean(); g4,tau4,s4=eb(o_,"pr",100,sig2=p0*(1-p0))
for nm,mk in (("odd",o_.game_id%2==1),("even",o_.game_id%2==0)): g4[nm]=o_[mk].groupby("nfl_id").pr.mean()
print(f"\nO4 OL pressure rate {p0:.3f}: players>=100 snaps {len(g4)}, between SD {np.sqrt(tau4):.3f}, split-half r={g4.odd.corr(g4.even):.2f}")
Q=g4.join(T,how="inner"); Q=Q[Q.combine_position=="OL"]
res.append(analyze("O4 OL pressure allowed (secondary)", Q, Q["mean"], Q.w, pooled=False))
pd.DataFrame(res).to_csv(f"{O}/translation_results.csv",index=False)
print("\nsaved translation_results.csv")
