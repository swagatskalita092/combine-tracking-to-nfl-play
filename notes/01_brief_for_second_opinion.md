# Brief: NFL Big Data Bowl 2027 (second opinion wanted)

## Competition
Kaggle analytics competition. Link 10 Hz NFL Combine sensor tracking to regular-season NFL performance. Judged on Football (30%), Data Science (30%), Writeup (20%), Visualization (20%). Max 2,000 words, fewer than 10 figures/tables, public Kaggle notebook required, must use the tracking data. Deadline Jan 6 2027 (about 6 weeks). Organizers advise going deep on one position group or drill; null results are acceptable. Judges are NFL team analytics staff.

## Team
One person: M.Sc. computer science student, strong in Python, data engineering and ML, no football scouting background.

## Data (already local)
- 510 drafted players (2023 to 2025 classes): DB 122, DL 118, OL 121, WR 107, TE 42.
- combine_tracking: 10 Hz x, y, speed, acceleration, direction, by drill and attempt, position-specific drills (WR routes, OL pass-pro and pull drills, DL pass rush and agility, DB back-pedal and W drill, plus 40, 3-cone, shuttle).
- game_tracking 2023 to 2025: 10 Hz, only these players.
- player_play: per-player-per-play outcomes (EPA, route_ran, separation_at_pass_forward, cushion, pressure/sack allowed, time_to_pressure, player_get_off, coverage type, formation).
- combine_results: measurables, 40, vertical, broad, etc. Three-cone and shuttle missing for 50 to 80 percent of players.
- Outcome columns are sparse and role-specific (separation about 15 percent of rows, get_off about 14 percent, pressure allowed about 19 percent). All-Pro/Pro Bowl too rare to use.

## Candidate ideas
1. OL pass protection: pass-rush-drop and mirror drill footwork vs pressure allowed and time to pressure (most snaps per player).
2. WR separation: deceleration and break sharpness in route drills vs separation at pass forward (clearest story, thin outcome data).
3. DL get-off: first-step metrics in pass-rush and four-bag drills vs get-off and pressure.

## Constraints
About 120 players per position, short careers, outcomes depend on opponent, scheme and play type. Needs shrinkage or mixed-effects, not raw correlations.

## Questions
1. Which idea would NFL analytics judges find most novel and usable, and why?
2. What confounders would they expect us to control for?
3. Which model design is defensible at n of about 120?
4. What is the most likely way this entry fails to score well?
5. Is there a stronger idea we are missing?
