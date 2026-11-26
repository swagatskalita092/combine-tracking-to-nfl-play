# Builds the public Kaggle notebook (notebook/combine_tracking_to_nfl_prior.ipynb) from the analysis scripts.
import json, os, sys
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.dirname(here)
def md(t): return {"cell_type":"markdown","metadata":{},"source":t.strip("\n").splitlines(True)}
def code(t): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":t.strip("\n").splitlines(True)}
def script(name,argv_expr,skip_head=0):
    s=open(os.path.join(here,name)).read()
    return code(f"import sys\nsys.argv = {argv_expr}\n# --- {name} ---\n"+s)
cells=[]
cells.append(md("""
# Do Combine tracking measures carry information about NFL play? A prior-weight analysis
**NFL Big Data Bowl 2027, Open Track.** This notebook reproduces every number and figure in the Writeup.

**Question.** For players drafted 2023-25, does what the Combine tracking system measures (position-specific drills at 10 Hz) predict how those players play in NFL regular-season games (player tracking, 2023-25), and how much weight does a Combine-informed prior deserve relative to a player's own early NFL plays?

**Design (decision rules written down in dated notes before the analyses they govern; self-recorded, not registered with a third party, see Writeup).**
1. *Unit of analysis is the player*, not the play. About 60-66 players per position have at least 100 usable snaps, so claims are sized to that.
2. *Combine tracking → NFL linkage.* Combine tracking features (tracked 40-yard-dash speed profile) are joined by `nfl_id` to NFL tracking outcomes: in-game top speed (from `game_tracking_*`), and NGS-style outcomes in `player_play` (DL get-off time, WR route separation, OL pressure allowed).
3. *Value of a Combine prior* is expressed as a **model-implied prior weight** (in independent-play equivalents): an empirical-Bayes prior built from Combine numbers is compared with a position-average prior, evaluated leave-one-player-out on each player's *later* 100 plays.
4. *Sensor vs stopwatch* (exploratory, added after the main analysis): is the tracked speed profile a better prior than the official stopwatch numbers?

Data are used under the competition's CC BY-NC 4.0 terms; nothing is redistributed.
"""))
cells.append(code("""
import os, glob, sys, subprocess
# Locate the competition data (Kaggle) or fall back to a local path.
cands = glob.glob("/kaggle/input/**/combine_results.csv", recursive=True)
DATA = os.path.dirname(cands[0]) if cands else os.environ.get("BDB_DATA", ".")
ON_KAGGLE = os.path.isdir("/kaggle/working")
# Player/play-level intermediates (derived from the competition data) go to temp storage and are NOT published
# with the notebook; only figures and aggregate result tables are copied to the public output folder below.
OUTDIR = os.environ.get("BDB_OUT") or ("/kaggle/temp/work" if ON_KAGGLE else "outputs")
try: os.makedirs(OUTDIR, exist_ok=True)
except OSError: OUTDIR = "/tmp/bdb_work"; os.makedirs(OUTDIR, exist_ok=True)
print("data:", DATA); print("outputs:", OUTDIR)
print(sorted(os.listdir(DATA)))
"""))
cells.append(md("## 1. Which positions have enough data? (position audit)"))
cells.append(script("03_position_audit.py",'["x", DATA]'))
cells.append(md("The audit above covers DL, DB, WR and TE; the next cell covers OL pass-protection coverage and the spread of pressure rates."))
cells.append(script("02_ol_feasibility.py",'["x", DATA]'))
cells.append(md("## 2. Sanity check: is the Combine sensor pipeline measuring speed correctly?\nTracked top speed in the 40-yard dash should track the official time. (Tracked 40 times are not comparable to official times because the clips start with the player already in motion, so we use speed levels, not times.)"))
cells.append(script("07_sanity_speed.py",'["x", DATA]'))
cells.append(md("## 3. Combine tracking features from the 40-yard dash\nDownfield position (not the `dis` column, which undercounts distance) gives speed levels (10/20/30 yd, top speed) and shape features (peak acceleration, yards to 95% of top speed, time of top speed, speed maintenance)."))
cells.append(script("08_forty_profile.py",'["x", DATA, OUTDIR + "/forty_run_features.csv"]'))
cells.append(md("## 4. Negative result worth stating: route-break features at the Combine have no cross-route reliability\nEach receiver runs each route once, so a 'route-break' feature would have to repeat across *different* routes. It does not, so it cannot be a stable player trait."))
cells.append(script("05_wr_rep_features.py",'["x", DATA, OUTDIR + "/wr_rep_features.csv"]'))
cells.append(script("06_wr_reliability.py",'["x", DATA, OUTDIR + "/wr_rep_features.csv"]'))
cells.append(md("## 5. NFL outcomes: in-game top speed per play\nMax tracked speed on each regular-season play for the drafted players (split-half reliability of the per-player figure is ~0.98)."))
cells.append(script("09_ingame_speed.py",'["x", DATA, OUTDIR + "/ingame_speed.csv"]'))
cells.append(md("## 6. Test 1 (pre-set): do tracking *shape* features add predictive value beyond the stopwatch?\nCross-validated R² gain over a baseline of official 40 time, 10-yd split and weight. Expectation recorded beforehand: small. Result: no detectable gain."))
cells.append(script("10_translation_test.py",'["x", DATA, OUTDIR]'))
cells.append(md("## 7. Test 2 (pre-set rule): how much prior weight does a Combine-informed prior get?\nLeave-one-player-out empirical-Bayes shrinkage. Pre-set claim rule (written down in a dated note before this analysis): the CI for MSE(position mean) − MSE(Combine prior) must exclude 0 at both k = 0 and k = 25 early snaps."))
cells.append(script("12_snaps_equivalent.py",'["x", DATA, OUTDIR]'))
cells.append(md("## 8. Exploratory (post hoc): tracked-sensor prior vs official-stopwatch prior\nSame players, same outcomes. Also reports CIs for each prior against the position average."))
cells.append(script("13_sensor_vs_stopwatch.py",'["x", DATA, OUTDIR]'))
cells.append(md("## 9. Robustness: multiplicity, seeds, and which Combine variable carries the prior\nHolm correction across the seven outcomes (added after the fact), single-player influence on the gains, the claim rule under five other bootstrap seeds, an ablation of the prior (full / body weight only / 40 time + 10-yd split only), player-bootstrap ranges for the prior weights, and tracked-vs-official agreement within position."))
cells.append(code("# Source of step 7 (12_snaps_equivalent.py), reused by the robustness checks below\nSRC12 = " + repr(open(os.path.join(here, "12_snaps_equivalent.py")).read())))
cells.append(script("16_robustness.py",'["x", DATA, OUTDIR]'))
cells.append(script("17_ablation_and_uncertainty.py",'["x", DATA, OUTDIR]'))
cells.append(md("Sensitivity: the WR separation adjustment (route, coverage, alignment, cushion) refit without each held-out player."))
cells.append(script("18_wr_adjustment_holdout.py",'["x", DATA, OUTDIR]'))
cells.append(md("## 10. Figures"))
cells.append(script("14_figures.py",'["x", DATA, OUTDIR]'))
cells.append(code("""
import shutil
from IPython.display import Image, display
RESULTS = "/kaggle/working/results" if ON_KAGGLE else OUTDIR + "/results"
os.makedirs(RESULTS, exist_ok=True)
for f in ("translation_results.csv", "snaps_equivalent_results.csv", "sensor_vs_stopwatch.csv", "robustness_holm.csv", "ablation.csv", "n0_bootstrap.csv", "sensor_agreement_by_position.csv", "influence.csv", "wr_adjustment_holdout.csv"):   # aggregate tables only
    shutil.copy(f"{OUTDIR}/{f}", RESULTS)
for f in sorted(os.listdir(f"{OUTDIR}/figures")):
    shutil.copy(f"{OUTDIR}/figures/{f}", RESULTS); display(Image(f"{RESULTS}/{f}"))
print("published to", RESULTS, ":", sorted(os.listdir(RESULTS)))
"""))
nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
os.makedirs(os.path.join(root,"notebook"),exist_ok=True)
out=os.path.join(root,"notebook","combine_tracking_to_nfl_prior.ipynb"); json.dump(nb,open(out,"w"),indent=1)
# also a flat .py for verification runs
py=["# auto-generated from the notebook for verification"]+["".join(c["source"]) for c in cells if c["cell_type"]=="code"]
open(os.path.join(root,"notebook","_flat_check.py"),"w").write("\n\n".join(py))
print("wrote",out,len(cells),"cells")
