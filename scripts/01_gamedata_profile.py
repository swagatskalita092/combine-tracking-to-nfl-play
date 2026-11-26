import sys, pandas as pd, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
pd.set_option("display.width", 220, "display.max_columns", 80, "display.max_rows", 200)
pp = pd.read_csv(f"{D}/player_play.csv", low_memory=False)
print("player_play", pp.shape, "| players", pp.nfl_id.nunique(), "| games", pp.game_id.nunique(), "| plays", pp.groupby(["game_id","play_id"]).ngroups)
print("\nCOLUMNS with non-null %:")
nn = (pp.notna().mean()*100).round(0).astype(int)
print(", ".join(f"{c}({v})" for c,v in nn.items()))
print("\nlined_up_position counts:"); print(pp.lined_up_position.value_counts().to_dict())
g = pd.read_csv(f"{D}/games.csv"); print("\ngames", g.shape, g.groupby(["season","season_type"]).size().to_dict())
