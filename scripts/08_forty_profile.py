import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D, OUT = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 200, "display.max_columns", 40)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"]).set_index("nfl_id")
ct = pd.read_csv(f"{D}/combine_tracking.csv")
p = ct[(ct.entity_type=="PLAYER")&(ct.drill_name=="FORTY_YARD_DASH")].copy()
p["t"] = pd.to_datetime(p.time, format="mixed")
def sm(v,k=3): return pd.Series(v).rolling(k,center=True,min_periods=1).mean().values
rows=[]
for (eid,nid),g in p.sort_values("t").groupby(["event_id","nfl_id"]):
    s=sm(g.s.values); n=len(s)
    if n<30: continue
    d=g.x.values-g.x.values[0]               # downfield yards (dis column undercounts)
    on = np.argmax(s>0.8) if (s>0.8).any() else None
    if on is None: continue
    d=d-d[on]; i40=np.argmax(d>=38) if (d>=38).any() else None
    if i40 is None or i40<=on: continue
    S=s[on:i40+1]; Dd=d[on:i40+1]-d[on]; T=np.arange(len(S))*0.1
    vmax=S.max(); acc=np.gradient(S)/0.1
    at=lambda yd: S[np.argmax(Dd>=yd)] if (Dd>=yd).any() else np.nan
    tt=lambda yd: T[np.argmax(Dd>=yd)] if (Dd>=yd).any() else np.nan
    rows.append(dict(nfl_id=nid,event_id=eid,t_event=g.t.iloc[0],t10=tt(10),t20=tt(20),t40=T[-1],v10=at(10),v20=at(20),v30=at(30),v40=S[-1],vmax=vmax,
        peak_acc=acc[:20].max(), d95=Dd[np.argmax(S>=0.95*vmax)], t_vmax=T[np.argmax(S)], maint=S[-1]/vmax))
f=pd.DataFrame(rows).sort_values("t_event")
f["run"]=f.groupby("nfl_id").cumcount()+1
f.to_csv(OUT,index=False)
print("runs:",len(f),"| players:",f.nfl_id.nunique(),"| runs per player:",f.groupby("nfl_id").size().value_counts().to_dict())
print("tracked t40 vs official forty corr:", round(f.groupby("nfl_id").t40.min().to_frame().join(cr.forty).dropna().corr().iloc[0,1],2))
feats=["t10","t40","v10","v20","v30","vmax","peak_acc","d95","t_vmax","maint"]
two=f[f.run<=2].pivot(index="nfl_id",columns="run",values=feats).dropna()
print("\ntest-retest (run1 vs run2) r, n=%d:"%len(two))
for m in feats: print(f"  {m:9s} r={np.corrcoef(two[(m,1)],two[(m,2)])[0,1]:.2f}")
P=f.groupby("nfl_id")[feats].mean().join(cr[["forty","ten_yd_split","combine_weight","combine_position"]]).dropna(subset=["forty","ten_yd_split","combine_weight"])
X=np.c_[np.ones(len(P)),P.forty,P.ten_yd_split,P.combine_weight]
print("\nR^2 of tracked feature on official forty+ten_yd+weight (n=%d), i.e. share already explained by conventional numbers:"%len(P))
for m in feats:
    y=P[m].values; b=np.linalg.lstsq(X,y,rcond=None)[0]; print(f"  {m:9s} R2={1-((y-X@b)**2).sum()/((y-y.mean())**2).sum():.2f}")
