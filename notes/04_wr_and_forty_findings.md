# WR route breaks and 40-yard dash profile: findings (Nov 26 2026)

## WR route-break features (scripts 04 to 07)
- Route drills: one event (rep) per player per route, ~15 route types, game-like effort, 4 to 8 attempt index values across the group.
- Break detector (peak turn rate, +/- 0.8 s window) run on 8 break routes, z-scored within drill, pooled per player (106 WRs, median 7 drills each).
- Cross-route split-half reliability (Spearman-Brown): exit_speed -0.05, min_speed 0.08, peak_turn_rate 0.09, turn_dur 0.17, speed_regain -0.12, reaccel 0.03. No player-level trait detected.
- Even plain top speed across route drills: SB 0.46, corr with official forty only -0.22. Route reps are not maximal sprints.
- Pipeline validated: tracked max speed in 40-yard dash vs official forty r = -0.80 (WR), -0.98 (DL). IDs and merges are sound.
- Caveat: detector is generic and could be noisy; this does not prove WR break skill does not exist, only that these single-rep metrics do not show a stable player trait.
- Data quirk: `dis` column undercounts distance relative to s and to x displacement (about 8% low). Use position or s, not dis.

## 40-yard dash tracking (script 08)
- 793 runs, 418 players, 375 with two runs. Every run spans ~40.4 yd downfield. Tracked time to 38 yd vs official forty r = 0.92.
- Test-retest r: v10 .92, v20 .98, v30 .99, vmax .99 (speed metrics); peak_acc .46, d95 .49, t_vmax .40, maint (speed at 38yd / vmax) .50, t10 .24.
- R^2 of each feature on official forty + 10yd split + weight: speeds .89 to .97 (redundant); peak_acc .38, d95 .29, t_vmax .27, maint .17, t10 .17.
- Reading: speed levels add nothing beyond conventional numbers. Shape features (maintenance, acceleration, distance to 95% top speed) are less redundant but only moderately reliable. Unique reliable signal may exist but is small.

## Next test
Do 40-yard-dash shape features predict in-game outcomes beyond forty/10yd/weight? Candidate outcomes: in-game top speed and burst from game tracking (large n, reliable), WR separation on vertical routes, DL get-off. Prespecify 2 to 3 features. A null is acceptable.
