# Translation test results (pre-registered in 05_preregistration.md), Nov 26 2026

Do 40-yard-dash shape features (maint, peak_acc, d95) add to forty + ten_yd + weight? Repeated 5-fold CV across players (R2 gain), permutation p for the 3 features jointly, bootstrap CIs for partial correlations.

| Outcome | n | Baseline CV R2 | CV gain | Perm p |
|---|---|---|---|---|
| O1 in-game top speed, pooled | 253 | .20 | -.002 | .086 |
| O1 WR | 57 | .39 | +.002 | .065 |
| O1 DB | 62 | .13 | -.079 | .962 |
| O1 DL | 60 | .41 | +.002 | .038 |
| O1 OL | 56 | .03 | -.107 | .587 |
| O2 WR adjusted separation | 63 | .27 | -.035 | .249 |
| O3 DL get-off | 65 | .44 | -.078 | .959 |
| O4 OL pressure allowed | 53 | -.11 | -.156 | .714 |

Verdict: no detectable added signal. CV gains are zero or negative everywhere. One nominal p<0.05 (DL top speed) among 8 tests has CV gain +0.002: treat as chance. Partial-correlation CIs excluding 0: pooled d95 [0.00,.27], DL peak_acc +.35 [.03,.61], WR separation peak_acc -.20 [-.42,0.00] (opposite sign to DL, uncorroborated). About 2 to 3 of 24 expected by chance.
CIs are wide (half-width about 0.25 at n about 60): inconclusive, not proof of absence.

Outcome reliability (odd/even game split-half): in-game top speed .98 (pooled), DL get-off .83, OL pressure .40, WR adjusted separation .37. WR separation: between-player SD only 0.20 yd vs 1.80 yd play-level.
Sanity: in-game top speed vs tracked 40 vmax within position: WR .60, DL .62, TE .33, DB .24, OL .12.
Baseline (conventional) numbers already predict: DL get-off CV R2 .44, WR in-game speed .39, DL speed .41, WR separation .27. Not novel (DL get-off likely tracks edge vs interior role via weight).

Next candidate (not yet pre-registered): DL PASS_RUSH_DRILL (2 reps for 106 DL) first-step features vs DL get-off (outcome reliability .83).
