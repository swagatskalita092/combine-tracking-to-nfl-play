import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D=sys.argv[1]; pd.set_option("display.width",200,"display.max_columns",40)
cr=pd.read_csv(f"{D}/combine_results.csv",na_values=["NA"]).set_index("nfl_id")
ct=pd.read_csv(f"{D}/combine_tracking.csv")
ct["t"]=pd.to_datetime(ct.time,format="mixed")
d=ct[ct.drill_name=="PASS_RUSH_DRILL"]
dl=d[(d.entity_type=="PLAYER")&(d.nfl_id.map(cr.combine_position)=="DL")]
print("DL PASS_RUSH_DRILL events:",dl.event_id.nunique(),"players:",dl.nfl_id.nunique())
ents=d[d.event_id.isin(dl.event_id.unique())].groupby("event_id").entity_type.agg(lambda s:",".join(sorted(set(s))))
print("entity types in these events:",ents.value_counts().to_dict())
print("BALL rows by drill (top):",ct[ct.entity_type=="BALL"].groupby("drill_name").size().sort_values(ascending=False).head(8).to_dict())
g=dl.sort_values("t").groupby(["event_id","nfl_id"])
st=g.agg(n=("x","size"),x0=("x","first"),y0=("y","first"),x1=("x","last"),y1=("y","last"),smax=("s","max"),s0=("s","first"))
print(st.describe().round(2).to_string())
ev=list(g)[:2]
for (eid,nid),e in ev:
    e=e.reset_index(drop=True); print(f"\n-- {eid} {nid} attempt {e.attempt.iloc[0]} rows {len(e)}"); print(e.iloc[::4][["time","x","y","s","a","dir"]].round(2).head(12).to_string(index=False))
# onset: first frame with s>1; start-of-tracking speed
on=g.apply(lambda e:(np.argmax(e.s.values>1.0) if (e.s.values>1).any() else np.nan)*0.1)
print("\nonset time of motion (s from first frame): ",on.describe().round(2).to_dict())
