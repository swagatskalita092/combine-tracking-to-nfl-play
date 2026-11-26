# Sensor vs stopwatch prior (EXPLORATORY, not pre-registered; script 13), Nov 27 2026

Coverage: stopwatch-complete 424 of 510 players, sensor-complete 418, sensor-only 0, stopwatch-only 6. Sensors do NOT cover extra players: tracked 40 runs exist where official times exist. Tracked vmax vs official forty r = -0.98; tracked 10-yd speed vs official 10-yd split r = -0.90.
Prior built from tracked (vmax, v10, weight) vs official (forty, ten_yd, weight), same players, LOO, late = last 100 plays:
- DL get-off: share explained 51% both; n0 16 both; MSE k=0 stopwatch .0073 vs sensor .0080 (gain -.0007 [-.0015,+.0001])
- WR adj separation: 45% vs 44%; n0 174 vs 171; gain +.0029 [-.0026,+.0085]
- WR top speed: 34% vs 40%; n0 25 vs 28; gain +.0115 [-.0051,+.0292] at k=0
- DL top speed: 67% both; n0 27 both; gain -.0006 [-.0034,+.0025]
- DB, OL top speed: no Combine signal either way.
Every interval includes 0: sensor prior and stopwatch prior are statistically indistinguishable. Sensor prior vs position mean (point estimates, no CI computed for this arm): DL top speed MSE .284 -> .140, WR top speed .119 -> .066, DL get-off .0110 -> .0080, WR separation .0495 -> .0352.
Reading: tracked sensors reproduce the stopwatch signal (and link to in-game tracking outcomes) but add neither coverage nor incremental accuracy.
