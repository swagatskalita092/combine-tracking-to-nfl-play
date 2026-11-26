# Combine tracking to NFL play: a prior-weight analysis

Code, decision-rule notes and aggregate results for my entry in the **NFL Big Data Bowl 2027 (Open Track)**.

- Kaggle notebook (reproduces every number and figure): https://www.kaggle.com/code/swagatskalita/combine-tracking-to-nfl-play
- Question: for players drafted 2023-25, does what the Combine tracking system measures predict how they play in NFL regular-season games, and how much weight does a Combine-informed prior deserve relative to a player's own early NFL plays?

## Main findings

- Only **DL in-game top speed** meets the pre-set rule and survives Holm correction (adjusted p = .0007; held-out error .284 to .140 at k = 0).
- WR top speed meets the rule but fails Holm correction (adjusted p = .077). DL get-off, WR separation, DB/OL outcomes do not meet it.
- Tracked 40-yard-dash shape features add no detectable predictive value over the official stopwatch numbers, and the sensor-based prior is not detectably better than the stopwatch-based prior.
- Body weight alone matches or beats the full prior for DL top speed and WR separation, so part of the signal is role and size.

## Layout

| Path | Contents |
|---|---|
| `notebook/` | The Kaggle notebook (no outputs), built from the scripts by `scripts/15_build_notebook.py` |
| `scripts/` | Analysis scripts in run order (00-18) |
| `notes/` | Dated notes: data map, decision rules written before each analysis (05, 07), results, reviews and responses (10-13). These are self-recorded, not registered with a third party |
| `results/` | Aggregate result tables only (no player-level rows) |
| `figures/` | The four Writeup figures |

## Reproducing

The competition data is licensed CC BY-NC 4.0 and **is not included**. Download it from the competition page, then either run the Kaggle notebook (it finds the data under `/kaggle/input`) or run the scripts locally:

```
python scripts/15_build_notebook.py          # rebuilds notebook/combine_tracking_to_nfl_prior.ipynb
# or run the scripts in numeric order; the data directory is the first argument
```

The notebook (`notebook/`) shows the exact argument order for each script.

## Licence

Code and notes: MIT (see `LICENSE`). The competition data is not covered by this licence and is not redistributed here.
