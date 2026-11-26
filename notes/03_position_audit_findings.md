# Position audit (script 03_position_audit.py, Nov 26 2026)

Players with game data / with >=100 snaps that carry the key outcome:
- OL: 89 / 66, pressure_allowed (binary, 8.5% rate, 93% filled in OL pass rows)
- WR: 83 / 63, separation_at_pass_forward (continuous, 88% filled in WR rows), median 250 routes. cushion 95%, route_ran 100% filled. Context controls exist in the data.
- DL: 98 / 63, player_get_off (82% filled). time_to_qb_hurry and time_to_pressure only 9% (event-conditional). Median 160 DL pass snaps per player, only 45 with >=200.
- DB: 96 / 54, only cushion (61% filled) is a clear outcome. No separation-allowed field. Weakest.
- TE: 33 / 21. Too small.
Earlier claims that separation (15%), get_off (14%) and pressure (19%) were thin used an all-rows denominator and were wrong.

Combine drill repeats (distinct event_id per player per drill):
- OL PASS_RUSH_DROP: 2 events for 118 of 120. Both attempts head the same direction (cosine 0.93 median, none negative), so no left/right contrast. Direction-specific OL idea is dead.
- DL PASS_RUSH_DRILL: 2 events for 106 of 118. Other DL drills 1 event.
- WR route drills: ~1 event per player per route (about 15 route types, 70 to 107 players each). GAUNTLET_DRILL has 2 events for 93 of 107. Reliability must come from consistency across routes, not test-retest.
- DB BACK_PEDAL_AND_TRANSITION_45: 2 events for 119 of 122. LINE_DRILL 82 of 85.
