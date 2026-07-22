# Data Sources

All model inputs were collected between May–June 2026 before the opening match on June 13, 2026.
No data has been retrospectively revised.

| Input | Source | Date | Weight in model |
|---|---|---|---|
| Elo ratings | DTAI Analytics Lab (via ESPN) | June 2026 | 40% |
| FIFA Men's Rankings | FIFA.com (official April 2026 release) | April 2026 | 30% |
| Win odds (American) | FanDuel / DraftKings / Betway | June 2026 | 20% |
| Qualifying form score | Goal differential + clean sheets, normalised 0–10 | June 2026 | 10% |

## Notes

- Elo values are approximated from the DTAI Analytics Lab model as published by ESPN prior to the tournament.
- American odds are the pre-tournament consensus across FanDuel, DraftKings, and Betway.
- Implied probability conversion: for +X odds → P = 100/(100+X); for −X odds → P = X/(100+X).
- All probabilities are vig-adjusted using standard over-round normalisation before use.
- Qualifying form score: 10-point scale where 10 = perfect qualifying record (all wins, no goals conceded).

## Actual Results (for accuracy audit)

| Team | Furthest stage reached |
|---|---|
| Spain | Final (champion — result intentionally excluded from white paper) |
| Argentina | Final |
| France | Semifinal |
| England | Semifinal |
| Morocco | Quarterfinal |
| Belgium | Quarterfinal |
| Norway | Quarterfinal |
| Switzerland | Quarterfinal |
| Brazil | Round of 16 |
| Portugal | Round of 16 |
| Germany | Round of 32 |
