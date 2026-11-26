import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
pd.set_option("display.width", 220, "display.max_columns", 60, "display.max_rows", 120)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"])
pos = cr.set_index("nfl_id").combine_position
ct = pd.read_csv(f"{D}/combine_tracking.csv", usecols=["event_id","nfl_id","entity_type","drill_type","drill_name","attempt","time","x","y"])
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False)
g = pd.read_csv(f"{D}/games.csv")
pp = pp.merge(g[["game_id","season_type"]], on="game_id")
pp = pp[pp.season_type=="REG"].copy()
pp["pos"] = pp.nfl_id.map(pos)
pp["is_pass"] = pp.pass_result.notna() & (pp.pass_result.astype(str)!="")
cols = ["route_ran","separation_at_pass_forward","cushion","target","expected_yards_after_catch","yards_after_catch","rec_yards","player_get_off","sack","time_to_qb_hurry","time_to_pressure","pressure_allowed","coverage_assignment","tackle","tackle_for_loss","blitzing"]
for P in ["DL","WR","DB","TE"]:
    d = pp[pp.pos==P]; dp = d[d.is_pass]
    print(f"\n===== {P}: REG rows {len(d)}, players {d.nfl_id.nunique()} of {(pos==P).sum()}; pass-play rows {len(dp)}")
    print("non-null % within pass-play rows:", {c: round(dp[c].notna().mean()*100) for c in cols if dp[c].notna().mean()>0.005})
    key = {"WR":"separation_at_pass_forward","TE":"separation_at_pass_forward","DL":"player_get_off","DB":"cushion"}[P]
    k = dp[dp[key].notna()].groupby("nfl_id").size()
    print(f"key outcome {key}: rows {int(k.sum())}, players with data {len(k)}; >=20: {(k>=20).sum()}, >=50: {(k>=50).sum()}, >=100: {(k>=100).sum()}, median {k.median():.0f}")
    if P in ("WR","TE"):
        r = dp[dp.route_ran.notna()].groupby("nfl_id").size()
        print(f"route_ran rows: players {len(r)}, >=50: {(r>=50).sum()}, >=100: {(r>=100).sum()}, >=200: {(r>=200).sum()}")
    if P=="DL":
        for c in ["sack","time_to_qb_hurry","time_to_pressure"]:
            s = dp.groupby("nfl_id")[c].apply(lambda x: x.notna().sum()); print(f"  {c}: non-null events total {int(s.sum())}, players with >=5: {(s>=5).sum()}")
        pr = dp.groupby("nfl_id").size(); print(f"  DL pass-play snaps per player: median {pr.median():.0f}, >=200: {(pr>=200).sum()}, >=400: {(pr>=400).sum()}")
    # drill repeatability
    c = ct[(ct.entity_type=="PLAYER")&(ct.nfl_id.map(pos)==P)].copy()
    c["drill"]=c.drill_name.replace({"PASS_PRO-MIRROR_DRILL":"PASS_PRO_MIRROR_DRILL","OVER_THE_SHOULDER_ADJUST":"OVER_SHOULDER_ADJUST"})
    c = c[c.drill_type.str.startswith("SKILL")]
    a = c.groupby(["drill","nfl_id"]).event_id.nunique().reset_index(name="n")
    s = a.groupby("drill").n.agg(players="size", ge2=lambda x:(x>=2).sum(), ge3=lambda x:(x>=3).sum())
    print(s[s.players>=60].to_string())

# OL PASS_RUSH_DROP: do the two attempts differ in direction?
c = ct[(ct.entity_type=="PLAYER")&(ct.drill_name=="PASS_RUSH_DROP")&(ct.nfl_id.map(pos)=="OL")].sort_values(["nfl_id","event_id","time"])
disp = c.groupby(["nfl_id","event_id"]).apply(lambda e: pd.Series({"dx":e.x.iloc[-1]-e.x.iloc[0],"dy":e.y.iloc[-1]-e.y.iloc[0]})).reset_index()
rows=[]
for nid, e in disp.groupby("nfl_id"):
    if len(e)>=2:
        a,b = e.iloc[0], e.iloc[1]
        n1=np.hypot(a.dx,a.dy); n2=np.hypot(b.dx,b.dy)
        rows.append(((a.dx*b.dx+a.dy*b.dy)/(n1*n2+1e-9), n1, n2))
cs = pd.DataFrame(rows, columns=["cos","len1","len2"])
print("\nOL PASS_RUSH_DROP attempt1 vs attempt2 displacement cosine: n=",len(cs)); print(cs.cos.describe().round(2).to_dict())
print("share cos>0.8:", round((cs.cos>0.8).mean(),2), "| cos<0:", round((cs.cos<0).mean(),2), "| median path length (yd):", round(cs.len1.median(),1))
