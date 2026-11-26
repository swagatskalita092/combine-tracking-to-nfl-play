import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
pd.set_option("display.width", 220, "display.max_columns", 60, "display.max_rows", 120)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"])
wr = set(cr[cr.combine_position=="WR"].nfl_id)
ct = pd.read_csv(f"{D}/combine_tracking.csv")
ct = ct[ct.nfl_id.isin(wr) | (ct.entity_type=="BALL")]
w = ct[(ct.entity_type=="PLAYER")&(ct.drill_name=="SLANT_ROUTE_LEFT")]
print("SLANT_ROUTE_LEFT events:", w.event_id.nunique(), "| attempt values:", sorted(w.attempt.unique()))
print("rows per event: ", w.groupby("event_id").size().describe().round(1).to_dict())
print("attempts per player-event:", w.groupby(["nfl_id","event_id"]).attempt.nunique().value_counts().to_dict())
e = w.sort_values("time").groupby(["event_id","nfl_id"])
ev = list(e)[:3]
for (eid,nid), g in ev:
    g = g.reset_index(drop=True)
    print(f"\n-- {eid} nfl_id {nid} attempt {g.attempt.iloc[0]} rows {len(g)}")
    print(g.iloc[::6][["time","x","y","s","a","dir"]].round(2).head(14).to_string(index=False))
# other entities in same event?
sample_eid = ev[0][0][0]
print("\nentities in that event:", ct[ct.event_id==sample_eid].groupby(["entity_type","nfl_id"]).size().to_dict())
# start/end geometry across all slant events
st = w.sort_values("time").groupby(["event_id","nfl_id"]).agg(x0=("x","first"),y0=("y","first"),x1=("x","last"),y1=("y","last"),n=("x","size"),smax=("s","max"))
print("\nstart/end geometry summary (slant left):"); print(st.describe().round(1))
# game-side
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False)
pw = pp[pp.nfl_id.isin(wr)]
print("\nroute_ran values:", pw.route_ran.value_counts(dropna=False).to_dict())
print("separation_at_pass_forward:", pw.separation_at_pass_forward.describe().round(2).to_dict())
print("cushion:", pw.cushion.describe().round(2).to_dict())
print("team_coverage_man_zone:", pw.team_coverage_man_zone.value_counts(dropna=False).to_dict())
print("target:", pw.target.value_counts(dropna=False).to_dict())
print("pass_result:", pw.pass_result.value_counts(dropna=False).to_dict())
print("lined_up_position:", pw.lined_up_position.value_counts().to_dict())
print("sep by route (mean, n):"); print(pw.groupby("route_ran").separation_at_pass_forward.agg(["mean","std","count"]).round(2))
gt = pd.read_csv(f"{D}/game_tracking_2025.csv", nrows=0); print("\ngame tracking cols:", list(gt.columns))
