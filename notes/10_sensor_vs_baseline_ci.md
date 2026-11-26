# 10 - CI for sensor/stopwatch prior vs position-mean (EXPLORATORY, not pre-registered)
Script: scripts/13_sensor_vs_stopwatch.py (player bootstrap, 2000 draws). Same players for all arms (complete-case: n_test 37-55).
Gain = MSE(position mean) - MSE(prior); positive = prior helps. 95% CI.

| outcome | k | stopwatch gain [CI] | sensor gain [CI] |
|---|---|---|---|
| DL get-off | 0 | .0037 [.0007,.0063] | .0030 [-.0003,.0059] |
| DL get-off | 25 | .0012 [-.0001,.0025] | .0010 [-.0003,.0024] |
| WR adj separation | 0 | .0115 [-.0032,.0276] | .0144 [-.0002,.0299] |
| WR adj separation | 100 | .0066 [-.0001,.0135] | .0093 [.0018,.0172] |
| WR top speed | 0 | .0416 [.0033,.0820] | .0531 [.0178,.0935] |
| WR top speed | 25 | .0248 [.0082,.0430] | .0285 [.0107,.0500] |
| DL top speed | 0 | .1438 [.0881,.2043] | .1432 [.0879,.2031] |
| DL top speed | 25 | .0490 [.0232,.0740] | .0492 [.0235,.0738] |
| DB, OL top speed | all k | CIs include 0 | CIs include 0 |

Reading: sensor prior beats position mean with CI excluding 0 for WR/DL top speed (k=0,25) - same as stopwatch. Sensor never beats stopwatch (see 09). 
Caveats: 6 outcomes x 3 k x 2 arms = many looks, no multiplicity correction; small test n; WR separation k=100 sensor-only significance is not robust evidence of anything (stopwatch CI just touches 0).
