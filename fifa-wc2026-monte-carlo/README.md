# FIFA World Cup 2026 — Monte Carlo Simulation

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Simulation](https://img.shields.io/badge/Simulations-10%2C000-navy)
![Teams](https://img.shields.io/badge/Teams-48-gold)
![Status](https://img.shields.io/badge/Pre--Final%20Audit-Complete-brightgreen)

> **A pre-tournament Monte Carlo simulation of the 2026 FIFA World Cup — 10,000 iterations, 48 teams, and a full accuracy audit against what actually materialised.**

**Author:** Ronak Pawar — [The Ronak Perspective](https://theronakperspective.wordpress.com)  
**Model built:** Before the opening match, June 12, 2026  
**Audit frozen:** Before the Final (Spain vs Argentina, July 19, 2026)  
**White paper:** [Full PDF on Google Drive](https://drive.google.com/file/d/199FLJ2az87qcFg1PmNSIE970hVgrzli5/view?usp=sharing)  
**Blog post:** [theronakperspective.wordpress.com](https://theronakperspective.wordpress.com)

---

## What this is

This repository contains the complete Python model behind the analytical white paper *"Predicting the 2026 FIFA World Cup."* The model was built before the tournament started and **has not been retrospectively revised.** The accuracy audit compares the original predictions against the tournament as it stood immediately before the Final.

The model's highest-conviction call before the first ball was kicked: **Spain, 18.2% championship probability.** Spain reached the Final.

---

## Model design

### Power Rating formula

```
Power Rating = 0.40 × Elo component
             + 0.30 × FIFA Rank component
             + 0.20 × Market implied probability
             + 0.10 × Qualifying form score
```

| Input | Source | Weight | Rationale |
|---|---|---|---|
| Elo rating | DTAI Analytics Lab (via ESPN) | **40%** | Highest weight — outperformed sportsbooks in 2018 and 2022 WC |
| FIFA Men's Ranking | FIFA.com, April 2026 | 30% | Official relative standing; slower to update than Elo |
| Sportsbook odds | FanDuel / DraftKings / Betway | 20% | Market consensus, vig-adjusted |
| Qualifying form | Goal differential + clean sheets, 0–10 | 10% | Recent form signal |

### Monte Carlo simulation

Each of the 10,000 iterations:
1. Draws effective probability = base + Gaussian noise (σ = 8% of base)
2. Simulates round-robin group stage with points and tiebreakers
3. Selects 8 best third-place teams alongside 24 group qualifiers
4. Runs knockout rounds (R32 → R16 → QF → SF → Final) through the official bracket pathway
5. Records the furthest stage reached by each team

Championship probability = times a team won ÷ 10,000

---

## Pre-tournament predictions

| # | Question | Model output |
|---|---|---|
| 1 | Tournament winner | **Spain — 18.2%** |
| 2 | Final pairing | Spain vs France |
| 3 | Winning continent | Europe — 63% |
| 4 | Quarterfinalists | Spain, France, England, Brazil, Germany, Portugal, Morocco, Argentina |
| 5 | Semifinalists | Spain, France, England, Brazil |
| 6 | Third place | England |
| 7 | Non-EUR/SA winner? | No — ~3% |
| 8 | Knockout qualifiers | 24 direct + 8 best third-place |
| 9 | Outside top tier to run deep? | Morocco highlighted; Japan as true giant-killer |
| 10 | Every top-10 team survive group stage? | No — Belgium flagged as vulnerable |
| 11 | Outside top 10 to win? | Unlikely — ~14% combined |

---

## Top 10 results (10,000 simulations, seed=42)

| Rank | Team | Power | MC Win% | QF% | SF% | Final% |
|---|---|---|---|---|---|---|
| 1 | 🇪🇸 Spain | 92 | **19.1%** | 52% | 31% | 22% |
| 2 | 🇫🇷 France | 91 | 17.0% | 50% | 29% | 20% |
| 3 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 85 | 11.8% | 46% | 27% | 18% |
| 4 | 🇧🇷 Brazil | 84 | 9.3% | 44% | 25% | 16% |
| 5 | 🇦🇷 Argentina | 82 | 8.6% | 43% | 24% | 15% |
| 6 | 🇩🇪 Germany | 80 | 6.1% | 38% | 20% | 12% |
| 7 | 🇵🇹 Portugal | 79 | 6.8% | 40% | 22% | 13% |
| 8 | 🇳🇱 Netherlands | 76 | 5.0% | 36% | 18% | 10% |
| 9 | 🇲🇦 Morocco | 74 | 3.4% | 32% | 16% | 8% |
| 10 | 🇨🇴 Colombia | 68 | 5.7% | 35% | 17% | 9% |

---

## Pre-Final accuracy audit

| Forecast layer | Predicted | Actual | Accuracy |
|---|---|---|---|
| Champion | Spain | **Unresolved** | Highest-conviction call alive |
| Finalists | Spain, France | Spain, Argentina | 1 of 2 exact |
| Semifinalists | Spain, France, England, Brazil | Spain, France, England, Argentina | **3 of 4 exact** |
| Quarterfinalists | 8 named teams | 5 of 8 overlapped | **5 of 8 exact** |
| Winning continent | Europe — 63% | 3 of 4 SFs European | Strongly supported |

### What the model got right
- Identified four of five highest-rated teams as the four semifinalists
- Spain as the central thesis — reached the Final as predicted
- European dominance (63%) confirmed structurally

### What the model missed — and why

| Miss | What happened | Analytical interpretation |
|---|---|---|
| Brazil | Projected SF; out R16 (lost to Norway) | Short-term form underweighted vs long-run Elo |
| Germany | Projected QF; out R32 on penalties | Penalty shootouts add discrete variance not captured |
| Portugal | Projected QF; out R16 (vs Spain) | Bracket path compressed two strong teams early |
| Norway | Power 55; reached QF, eliminated Brazil | Concentrated star output (Haaland: 16 qualifying goals) underweighted |

> **Model-development lesson:** Add a player-concentration factor measuring what share of expected goals depends on one or two elite players.

---

## Applied Kalshi market analysis

A parallel exercise compared model probabilities against live Kalshi prediction market prices across 13 match markets during the group stage.

| Market | Entry | Model | Result |
|---|---|---|---|
| France win vs Senegal | 66¢ | 72% | ✅ Cashed |
| Over 1.5 goals, France–Senegal | 74¢ | 82% | ✅ Cashed |
| Mbappé score or assist | 69¢ | 75% | ✅ Cashed |
| Haaland 1+ goal vs Iraq | 63¢ | 74% | ✅ Cashed |
| Iraq wins 1st half vs Norway | 8¢ ×11 | 5% (lottery) | ❌ Lost |
| Sørloth score or assist | 51¢ | 56% | ✅ Cashed |
| Argentina −1.5 spread vs Algeria | 42¢ | 50% | ✅ Cashed |
| Messi score or assist vs Algeria | 71¢ | 78% | ✅ Cashed |
| Switzerland 6+ corners vs Qatar | 62¢ | 64% | ✅ Cashed |

The strongest persistent edge was in **player score-or-assist markets** and **corner volume thresholds**, not in headline match-winner markets (which were efficiently priced). *This is not financial advice.*

---

## Repository structure

```
fifa-wc2026-monte-carlo/
├── simulation.py          # Main model — power ratings + Monte Carlo simulation
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── notebooks/
│   └── analysis.py        # Chart generation (6 figures matching white paper)
│
├── data/
│   └── DATA_SOURCES.md    # Source documentation + actual results
│
├── outputs/               # Generated on run — gitignored except sample
│   ├── championship_probabilities.csv
│   ├── accuracy_audit.csv
│   └── charts/            # 6 matplotlib figures
│
└── .github/
    └── workflows/
        └── run_simulation.yml   # GitHub Actions CI
```

---

## Quick start

```bash
# Clone
git clone https://github.com/ronak-cpu/fifa-wc2026-monte-carlo.git
cd fifa-wc2026-monte-carlo

# Install dependencies
pip install -r requirements.txt

# Run simulation (10,000 iterations, default seed)
python simulation.py

# Run with accuracy audit vs actual results
python simulation.py --audit

# Custom iterations and seed
python simulation.py --n_sims 50000 --seed 123 --audit

# Generate all charts (6 figures)
python notebooks/analysis.py
```

---

## Limitations and next-version priorities

| Current limitation | Version 2 improvement |
|---|---|
| Static pre-tournament ratings | Bayesian / Elo updating after every match |
| No injury or lineup modelling | Probabilistic squad availability + starting XI strength |
| Weak penalty treatment | Dedicated shootout model using keeper and taker histories |
| Team-level ratings only | Player-concentration and replacement-value indices |
| Simple bracket logic | Full official bracket engine linked to realised group positions |

---

## Methodology notes

- **Gaussian noise:** σ = 8% of base probability per match, capturing irreducible match-day variance
- **Elo normalisation:** scaled from the observed 1,180–1,877 range to a 0–100 component
- **Implied probability conversion:** US odds → P = 100/(100+X) for positive; P = X/(100+X) for negative
- **Vig adjustment:** standard over-round normalisation before use as model input
- **Tiebreaker:** power rating differential used as a goal-difference proxy in group stage sorting

---

## Related links

| Resource | Link |
|---|---|
| White paper (PDF) | [Google Drive](https://drive.google.com/file/d/199FLJ2az87qcFg1PmNSIE970hVgrzli5/view?usp=sharing) |
| Blog post | [The Ronak Perspective](https://theronakperspective.wordpress.com) |
| LinkedIn | [Ronak Pawar](https://www.linkedin.com/in/ronak-pawar) |
| Other projects | [github.com/ronak-cpu](https://github.com/ronak-cpu) |

---

## License

MIT License. Free to use, adapt, and build on with attribution.

---

*This project is an independent analytical exercise. It is not financial, gambling, or investment advice. Probabilistic models do not guarantee outcomes. All model outputs were fixed before the tournament began and have not been retrospectively revised.*

---

**The Ronak Perspective · Ancient Strategy. Modern Execution.**
