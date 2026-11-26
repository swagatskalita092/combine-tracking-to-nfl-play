import sys, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
pd.set_option("display.width", 220, "display.max_columns", 60, "display.max_rows", 100)
cr = pd.read_csv(f"{D}/combine_results.csv", na_values=["NA"])
ct = pd.read_csv(f"{D}/combine_tracking.csv", usecols=["draft_year","event_id","nfl_id","entity_type","drill_type","drill_name","attempt","time"])
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False)
games = pd.read_csv(f"{D}/games.csv")
ol = set(cr[cr.combine_position=="OL"].nfl_id)

# 1. drill repeatability for OL
c = ct[(ct.nfl_id.isin(ol)) & (ct.entity_type=="PLAYER") & (ct.drill_type=="SKILL_DRILLS_OL")]
c["drill"] = c.drill_name.replace({"PASS_PRO-MIRROR_DRILL":"PASS_PRO_MIRROR_DRILL"})
a = c.groupby(["drill","nfl_id"]).event_id.nunique().rename("n_events").reset_index()
print("OL drill coverage: players with >=1 and >=2 recorded attempts (events)")
print(a.groupby("drill").n_events.agg(players="size", ge2=lambda s:(s>=2).sum(), median="median"))
print("\nOL players with BOTH pass_rush_drop and mirror:", len(set(a[a.drill=="PASS_RUSH_DROP"].nfl_id) & set(a[a.drill=="PASS_PRO_MIRROR_DRILL"].nfl_id)))

# 2. game exposure and eligible-role missingness
ppo = pp[pp.nfl_id.isin(ol)].merge(games[["game_id","season","season_type"]], on="game_id", how="left")
reg = ppo[ppo.season_type=="REG"]
print("\nOL player-play rows (REG):", len(reg), "| players:", reg.nfl_id.nunique())
print("lined_up_position:", reg.lined_up_position.value_counts().to_dict())
passes = reg[reg.pass_result.notna() & (reg.pass_result!="")]
print("\nOL rows on pass plays:", len(passes))
cols = ["pressure_allowed","sack_allowed","time_to_pressure_allowed","dropback_duration","pass_rushers_encountered","peak_pressure_probability_allowed","unblocked_pressure","quick_pressure"]
print("non-null % WITHIN OL pass-play rows:"); print((passes[cols].notna().mean()*100).round(1).to_dict())
pa = passes[passes.pressure_allowed.notna()]
pa["pressure_allowed"] = pa.pressure_allowed.astype(str).str.upper().isin(["TRUE","1","1.0"])
print("\npressure_allowed value counts (raw):", passes.pressure_allowed.value_counts(dropna=False).to_dict())
per = pa.groupby("nfl_id").agg(snaps=("pressure_allowed","size"), press=("pressure_allowed","mean"))
print("\npass-block snaps per OL player:", per.snaps.describe().round(0).to_dict())
for k in (50,100,200,400): print(f" players with >= {k} pass-block snaps: {(per.snaps>=k).sum()} of {len(ol)}")
print("overall pressure-allowed rate:", round(pa.pressure_allowed.mean(),3))
# between-player signal: expected binomial sd vs observed
p=pa.pressure_allowed.mean(); big=per[per.snaps>=100]
print(f"observed sd of player rate (>=100 snaps): {big.press.std():.3f} | pure-noise binomial sd: {np.sqrt((p*(1-p)/big.snaps).mean()):.3f}")
print("\nseason split of pass-block snaps:"); print(pa.merge(games[['game_id','season']],on='game_id').season_x.value_counts().to_dict() if 'season_x' in pa.merge(games[['game_id','season']],on='game_id').columns else pa.season.value_counts().to_dict())
print("\nOL pass-block snaps by draft class:")
dy = cr.set_index("nfl_id").draft_year
print(per.join(dy).groupby("draft_year").snaps.agg(["size","median","sum"]))
