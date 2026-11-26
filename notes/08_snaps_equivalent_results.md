# Snaps-equivalent results (pre-registered in 07; script 12; outputs/snaps_equivalent_results.csv), Nov 26 2026

Prior = Combine baseline (forty, ten_yd_split, weight). n0 = sigma^2/tau^2 = snaps of data the prior is worth. Test = players with >=200 plays; late = last 100 plays; early = first k.

| Outcome | Test n | Combine explains (true between-player var) | n0 position-mean -> Combine | Pre-reg criterion (CI of MSE gain excludes 0 at k=0 and k=25) |
|---|---|---|---|---|
| DL get-off | 37 | 51% | 8 -> 16 snaps | k=0 yes [+.0009,+.0067]; k=25 [-.0000,+.0026] touches 0: NOT met strictly; gain gone by k=50 |
| WR adjusted separation | 39 | 45% | 95 -> 174 routes | CIs include 0 at every k (point gain ~23% of MSE at k=0): NOT met |
| OL pressure allowed | 48 | -5% | 250 -> 239 | No |
| WR in-game top speed | 48 | 34% | 16 -> 25 | Met (k=0 [+.0041,+.0838], k=25 [+.0080,+.0425]); fades by k=100 |
| DL in-game top speed | 51 | 67% | 9 -> 27 | Met (k=0 [+.0897,+.2023], k=25 [+.0225,+.0732]); CI touches 0 at k=50 |
| DB in-game top speed | 55 | 0% | 64 | No |
| OL in-game top speed | 52 | -4% | 36 | No |

Shape features (secondary arm): never beat the baseline prior; for DL get-off adding them was worse (gain -.0009 [-.0021,-.0002] at k=0). Consistent with the first pre-registered test: no added value.
Raw early means are far worse than shrunk estimates: WR separation MSE at k=10 raw .356 vs shrunk .040; at k=100 raw .075 vs Combine-prior .038 (prior still beats the data at 100 routes).
Caveats: 37 to 55 test players; late-window truth is itself noisy (100 plays); tau from method of moments; Combine arm uses official stopwatch numbers, so the tracking-specific contribution is only via the shape arm (null). Need an arm showing tracked sensor speed vs stopwatch (exploratory, not pre-registered) to tie the story to sensor data.
