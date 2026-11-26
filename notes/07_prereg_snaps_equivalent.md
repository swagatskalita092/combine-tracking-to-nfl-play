# Pre-registration 2: "How many NFL snaps is a Combine number worth?" (written before running, Nov 26 2026 ~23:15 IST)

Design is fixed here. No grid, threshold or outcome will be changed after seeing results.

Outcome-position pairs (all reported, none dropped): DL get-off; WR adjusted separation (route, cushion, man/zone, alignment removed by global OLS); OL pressure allowed; in-game per-play top speed for WR, DL, DB, OL. Regular season only, chronological by game_id then play_id.

Per outcome estimate (pool = players with >=30 qualifying plays and complete baseline + shape features):
 sigma^2 = pooled within-player play-level variance; tau_tot^2 = true between-player variance; tau_r^2 = true between-player variance left after the Combine baseline (forty, ten_yd_split, combine_weight); method-of-moments, floor 2% of tau_tot^2.
 Snaps-equivalent n0 = sigma^2 / tau^2 (position-mean prior vs Combine prior). Share explained = 1 - tau_r^2/tau_tot^2.

Out-of-time validation (test players need >=200 qualifying plays): "late" = last 100 plays; "early" = first k plays, k in {0,10,25,50,100}. Predict the late mean using:
 (a) raw early mean (k>0), (b) normal-normal shrinkage to the position mean, (c) shrinkage to the Combine-baseline prior, (d) shrinkage to baseline + shape features (F1 maint, F2 peak_acc, F3 d95) as secondary arm.
 Prior is refit leaving the test player out (leave-one-player-out). Metric: MSE against the late mean, player-bootstrap 95% CI (2000 resamples) for MSE(b) - MSE(c).
Claims: the Combine baseline "helps" for an outcome only if the CI for MSE(b) - MSE(c) excludes 0 at k=0 and at k=25. The shape arm is secondary; claim added value only if (d) beats (c) with CI excluding 0. Nulls and wide intervals reported as inconclusive.
Common sample for all arms (complete baseline and shape features).

## Addendum (Nov 27 2026 ~00:05 IST): EXPLORATORY arm, NOT pre-registered
Sensor-vs-stopwatch prior: replace (forty, ten_yd_split) by tracked (vmax, v10 = speed at 10 yd from the 40-yard-dash tracking) plus weight; compare MSE with the stopwatch prior on the same players and outcomes. Also count coverage: players with a usable sensor prior but no complete stopwatch prior. Reported as exploratory.
