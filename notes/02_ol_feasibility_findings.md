# OL feasibility audit (script 02_ol_feasibility.py, Nov 26 2026)

- Combine OL: 121 players. With regular-season rows: 91. With pressure data: 89. With >=100 pass-block snaps: 66. With >=200: 60. With >=400: 47. Effective n is about 60 to 66, not 120.
- Pass-block snaps by draft class (players with data): 2023 median 786, 2024 median 406, 2025 median 263. Exposure is very unequal. Compare on matched exposure (first season) or model exposure explicitly.
- Missingness within eligible rows (OL pass plays): pressure_allowed, sack_allowed, dropback_duration, pass_rushers_encountered about 93% filled. time_to_pressure_allowed 7.9% (only on pressure events, use competing-risks design or skip). unblocked_pressure and quick_pressure are 0% for OL. Earlier "19% thin coverage" claim was an all-rows denominator and was misleading.
- Pressure allowed rate overall: 8.5% of 48.5k snaps. Player-level SD of rate (>=100 snaps) 0.027 vs pure binomial noise 0.013, so real between-player spread exists (about 2.4 points), but it includes team, scheme and QB effects.
- Combine drill repeatability: PASS_RUSH_DROP has 2 attempts for 118 of 120 OL. PASS_PRO_MIRROR_DRILL has exactly 1 attempt per player (121 players). Wave drill, pull drills, screen drill: 1 attempt. So split-half reliability is only testable on PASS_RUSH_DROP. Direction-specific mirror hypothesis cannot be validated for reliability from this data.
- Open: do the two PASS_RUSH_DROP attempts differ in direction/side? Not yet checked.
