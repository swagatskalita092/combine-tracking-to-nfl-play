# Pre-registration (written before looking at any game outcomes), Nov 26 2026 ~22:35 IST

Question: do tracking-derived shape features of the 40-yard dash predict in-game performance BEYOND the conventional numbers?

Features (run-averaged over the player's 40-yard dash runs, from combine_tracking, downfield position and s):
 F1 maint     = speed at 38 yd / max speed (speed maintenance)
 F2 peak_acc  = peak smoothed acceleration in first 2.0 s
 F3 d95       = yards needed to reach 95% of max speed
Baseline (conventional): official forty, ten_yd_split, combine_weight (+ position dummies when pooling positions).
No other features will be tested. Max speed and split times are excluded because they are 89 to 97% redundant with the baseline (script 08).

Outcomes:
 O1 in-game top speed: player p95 of per-play max speed (regular season, plays >= 2 s of tracking); all positions, z-scored within position
 O2 WR adjusted separation: mean separation_at_pass_forward after removing route, cushion, man/zone, alignment effects (WR only)
 O3 DL get-off (DL only)
 O4 secondary: OL pressure-allowed rate (binary, noisy)

Analysis: player is the unit. Outcomes weighted by exposure (inverse-variance with shrinkage). Compare baseline vs baseline+F1..F3 by repeated 5-fold CV across players (R^2 gain), plus player-bootstrap 95% CI for the gain and for each feature's partial correlation controlling for the baseline.
Decision rule: claim added signal only if the bootstrap CI for the gain/partial correlation excludes 0 for a primary outcome. Otherwise report as no detectable gain (wide interval = inconclusive, not proof of absence). All four outcomes are reported, none dropped. Multiple outcomes noted as a limitation.
Complete-case on baseline variables; n reported each time.
