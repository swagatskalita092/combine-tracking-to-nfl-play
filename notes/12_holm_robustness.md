# 12 - Robustness of the pre-registered claim rule (script 16_robustness.py, outputs/robustness_holm.csv), Nov 27 2026
Rule (note 07): CI for MSE(position mean) - MSE(Combine prior) excludes 0 at BOTH k=0 and k=25. Re-run with 5 other bootstrap seeds (4000 draws), plus intersection-union one-sided bootstrap p = max(p_k0, p_k25), Holm step-down across the 7 pre-registered outcomes (alpha .05).

| outcome | n_test | rule met (of 5 seeds) | p_k0 | p_k25 | p_IU | Holm threshold | survives Holm |
|---|---|---|---|---|---|---|---|
| DL top speed | 51 | 5 | .0000 | .0001 | .0001 | .0071 | YES |
| WR top speed | 48 | 5 | .0128 | .0006 | .0128 | .0083 | no (close) |
| DL get-off | 37 | 0 | .0070 | .0277 | .0277 | .0100 | no |
| WR adj separation | 39 | 0 | .0642 | .1477 | .1477 | .0125 | no |
| OL pressure | 48 | 0 | .7585 | .7713 | .7713 | .0167 | no |
| DB top speed | 55 | 0 | .8419 | .5514 | .8419 | .0250 | no |
| OL top speed | 52 | 0 | .8664 | .7699 | .8664 | .0500 | no |

Reading: the pre-set rule is stable across seeds (WR/DL top speed met 5/5; others 0/5, so DL get-off is NOT met, not "borderline" in a seed-robust sense). After multiplicity correction only DL top speed is a confirmed result; WR top speed is suggestive (p_IU .013 vs Holm .0083). Writeup must say so.
