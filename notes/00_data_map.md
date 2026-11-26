# BDB 2027: data map (generated from local files, Nov 26 2026)

Data dir: D:\Big Data Bowl\nfl-big-data-bowl-2027\nfl-big-data-bowl-2027\

## Files
- combine_results.csv: 510 players, one row each (2023: 160, 2024: 177, 2025: 173). Measurables, drill times, NGS scores.
- combine_tracking.csv: 463k rows, 10 Hz (0.1 s), 510 players + BALL rows. Columns: draft_year, event_id, nfl_id, entity_type, time, drill_type, drill_name, attempt, x, y, s, a, dis, dir.
- game_tracking_2023/24/25.csv: 10 Hz in-game tracking, ONLY the combine players (156 / ? / 448 ids). Columns: game_id, play_id, nfl_id, time, x, y, s, a, dis, o, dir, event.
- player_play.csv: 314k player-play rows, 497 players, 1001 games, 115k plays. Outcomes and context (EPA, coverage, formation, route_ran, separation_at_pass_forward, cushion, pressure/sack allowed, get_off, blitzing, tackles).
- player_career_successes.csv: career snaps, games, All-Pro, Pro Bowl.
- players.csv: nfl_position, college, draft round and pick.
- games.csv: 1002 games (REG 272 per season, plus PRE and POST).

## Counts by combine position
DB 122, DL 118, OL 121, TE 42, WR 107.

## Position-level facts that constrain ideas
- three_cone and short_shuttle are missing for most players (20 to 53 percent present). 40, 10-yd, vertical, broad are 79 to 91 percent present.
- Tracked drills are position-specific. WR route drills: ~100 players each (comebacks, curls, daggers, gos, slants, slot routes). DL: body control, four-bag agility, pass rush, run the hoop, ~110 each. OL: pass rush drop, screen, pull drills, wave drill, ~120 each. DB: W drill, box drill, gauntlet, back pedal drills, ~122 each. TE: only 30 to 42 per drill.
- Drill name inconsistencies to clean: OVER_SHOULDER_ADJUST vs OVER_THE_SHOULDER_ADJUST, PASS_PRO-MIRROR vs PASS_PRO_MIRROR, LINE vs LINE_DRILL, SHORT_ZONE_BREAKS variants.
- 2023 LB tracking exists for 4 players only: ignore.
- player_play outcome columns are conditional: route_ran 17 percent non-null, separation_at_pass_forward 15, cushion 33, pressure/sack allowed 19, player_get_off 14. Always check the denominator.
- Career success columns are rare events (All-Pro mean 0.01): too sparse as a target. Use snaps, starts, and play-level outcomes.
