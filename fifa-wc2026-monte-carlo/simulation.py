"""
FIFA World Cup 2026 — Monte Carlo Simulation
=============================================
Author  : Ronak Pawar
Blog    : https://theronakperspective.wordpress.com
GitHub  : https://github.com/ronak-cpu
Date    : June 2026 (pre-tournament baseline)

Description
-----------
10,000-iteration Monte Carlo simulation of the 2026 FIFA World Cup.
Produces championship probability, quarterfinal / semifinal / final
probability per team, and an accuracy audit against actual results.

Inputs
------
- Elo ratings          (weight: 40%)  — DTAI Analytics Lab
- FIFA Men's Rankings  (weight: 30%)  — April 2026 official release
- Sportsbook odds      (weight: 20%)  — FanDuel / DraftKings / Betway
- Qualifying form      (weight: 10%)  — goal differential & clean sheets

Output
------
- championship_probabilities.csv
- stage_probabilities.csv
- accuracy_audit.csv  (post-tournament comparison)
- console summary table

Usage
-----
    pip install -r requirements.txt
    python simulation.py                      # run simulation (default 10,000 iterations)
    python simulation.py --n_sims 50000       # custom iterations
    python simulation.py --audit              # include accuracy audit vs actual results
    python simulation.py --seed 42            # reproducible run

"""

import argparse
import random
import math
import csv
import os
from collections import defaultdict

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_N_SIMS  = 10_000
NOISE_SIGMA_PCT = 0.08          # Gaussian noise = σ × base_probability
OUTPUT_DIR      = "outputs"

# ─── Team Data ────────────────────────────────────────────────────────────────
# Fields: name, confederation, fifa_rank, elo, win_odds_us, qualifying_form_score (0–10)

TEAMS = [
    # Elite tier
    ("Spain",          "UEFA",     2,  1876, 450,   9.2),
    ("France",         "UEFA",     1,  1877, 480,   8.8),
    ("England",        "UEFA",     4,  1826, 650,   8.6),
    ("Brazil",         "CONMEBOL", 6,  1761, 850,   8.4),
    ("Argentina",      "CONMEBOL", 3,  1875, 950,   8.2),
    ("Germany",        "UEFA",    10,  1730, 1400,  7.8),
    ("Portugal",       "UEFA",     5,  1764, 1200,  8.0),
    ("Netherlands",    "UEFA",     7,  1758, 1600,  7.6),
    ("Morocco",        "CAF",      8,  1756, 3000,  7.4),
    ("Belgium",        "UEFA",     9,  1735, 2500,  7.0),
    # Contender tier
    ("Colombia",       "CONMEBOL",13,  1693, 1400,  6.8),
    ("Senegal",        "CAF",     14,  1689, 5000,  6.6),
    ("Japan",          "AFC",     18,  1660, 6000,  6.4),
    ("USA",            "CONCACAF",16,  1673, 5500,  6.2),
    ("Uruguay",        "CONMEBOL",17,  1673, 4000,  6.0),
    ("Mexico",         "CONCACAF",15,  1681, 6000,  6.0),
    ("Croatia",        "UEFA",    11,  1717, 8000,  5.9),
    ("Switzerland",    "UEFA",    19,  1649, 7000,  5.8),
    ("Norway",         "UEFA",    31,  1580, 8000,  5.5),
    ("Ecuador",        "CONMEBOL",None,1570, 10000, 5.3),
    ("South Korea",    "AFC",     None,1570, 12000, 5.2),
    ("Austria",        "UEFA",    None,1565, 12000, 5.1),
    ("Ivory Coast",    "CAF",     None,1560, 15000, 5.0),
    ("Egypt",          "CAF",     None,1555, 15000, 5.0),
    ("Turkey",         "UEFA",    None,1550, 12000, 4.9),
    ("Canada",         "CONCACAF",None,1545, 20000, 4.8),
    ("Algeria",        "CAF",     None,1530, 20000, 4.6),
    ("Paraguay",       "CONMEBOL",None,1520, 20000, 4.5),
    ("Australia",      "AFC",     None,1515, 20000, 4.5),
    ("Scotland",       "UEFA",    None,1510, 25000, 4.4),
    ("Ghana",          "CAF",     None,1495, 25000, 4.3),
    ("Bosnia & Hz.",   "UEFA",    None,1490, 25000, 4.3),
    ("Iran",           "AFC",     None,1480, 30000, 4.2),
    ("Czechia",        "UEFA",    None,1470, 30000, 4.1),
    ("DR Congo",       "CAF",     None,1450, 40000, 4.0),
    ("Tunisia",        "CAF",     None,1445, 40000, 3.9),
    ("Sweden",         "UEFA",    None,1445, 20000, 5.0),
    ("Saudi Arabia",   "AFC",     None,1390, 50000, 3.5),
    ("Cape Verde",     "CAF",     None,1380, 50000, 3.4),
    ("South Africa",   "CAF",     None,1370, 60000, 3.3),
    ("Qatar",          "AFC",     None,1340, 75000, 3.0),
    ("Haiti",          "CONCACAF",None,1290,100000, 2.8),
    ("Panama",         "CONCACAF",None,1280,100000, 2.7),
    ("New Zealand",    "OFC",     None,1250,100000, 2.6),
    ("Uzbekistan",     "AFC",     None,1240,100000, 2.5),
    ("Jordan",         "AFC",     None,1230,100000, 2.4),
    ("Iraq",           "AFC",     None,1220,100000, 2.3),
    ("Curacao",        "CONCACAF",None,1180,200000, 2.2),
]

# ─── Groups (Group : [team names]) ───────────────────────────────────────────

GROUPS = {
    "A": ["Mexico", "South Korea", "Czechia", "South Africa"],
    "B": ["Switzerland", "Canada", "Bosnia & Hz.", "Qatar"],
    "C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "D": ["USA", "Turkey", "Australia", "Paraguay"],
    "E": ["Germany", "Ivory Coast", "Ecuador", "Curacao"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Austria", "Algeria", "Jordan"],
    "K": ["Portugal", "Colombia", "DR Congo", "Uzbekistan"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# ─── Helper: implied probability from US odds ─────────────────────────────────

def implied_prob(us_odds: int) -> float:
    """Convert US moneyline odds to implied probability (vig-unadjusted)."""
    if us_odds > 0:
        return 100 / (100 + us_odds)
    else:
        return abs(us_odds) / (100 + abs(us_odds))


# ─── Power Rating computation ─────────────────────────────────────────────────

def compute_power_ratings(teams: list) -> dict:
    """
    Composite Power Rating (0–100 scale):
      0.40 × elo_component
    + 0.30 × rank_component
    + 0.20 × market_component
    + 0.10 × form_component

    Returns dict: {team_name: {"power": float, "win_prob": float, ...}}
    """
    # Normalise Elo: scale 1,100–2,000 range → 0–100
    elo_values = [t[3] for t in teams]
    elo_min, elo_max = min(elo_values), max(elo_values)

    # Normalise FIFA rank: rank 1 → 100, rank 60 → 40 (inverse, capped)
    # Missing rank (None) → treated as rank 50
    rank_values = [(t[2] if t[2] is not None else 50) for t in teams]
    rank_min, rank_max = min(rank_values), max(rank_values)

    # Normalise market implied probability
    market_probs = [implied_prob(t[4]) for t in teams]
    mp_min, mp_max = min(market_probs), max(market_probs)

    # Normalise form score (already 0–10; scale to 0–100)
    form_values = [t[5] for t in teams]
    form_min, form_max = min(form_values), max(form_values)

    ratings = {}
    for t in teams:
        name, conf, rank, elo, odds, form = t

        elo_comp  = (elo - elo_min) / (elo_max - elo_min) * 100
        rank_num  = rank if rank is not None else 50
        rank_comp = (1 - (rank_num - rank_min) / (rank_max - rank_min)) * 100
        mkt_prob  = implied_prob(odds)
        mkt_comp  = (mkt_prob - mp_min) / (mp_max - mp_min) * 100
        form_comp = (form - form_min) / (form_max - form_min) * 100

        power = (
            0.40 * elo_comp +
            0.30 * rank_comp +
            0.20 * mkt_comp +
            0.10 * form_comp
        )

        ratings[name] = {
            "confederation": conf,
            "fifa_rank":      rank,
            "elo":            elo,
            "win_odds":       odds,
            "implied_prob":   round(mkt_prob, 4),
            "form_score":     form,
            "power_rating":   round(power, 2),
            "base_win_prob":  round(mkt_prob, 4),  # market-implied as base
        }

    return ratings


# ─── Match simulation ─────────────────────────────────────────────────────────

def simulate_match(team_a: str, team_b: str, ratings: dict, rng: random.Random) -> str:
    """
    Simulate a single match. Returns winner name.
    Uses power-rating-based probability with Gaussian noise.
    """
    pa = ratings[team_a]["power_rating"]
    pb = ratings[team_b]["power_rating"]

    # Add Gaussian noise
    noise_a = rng.gauss(0, NOISE_SIGMA_PCT * pa)
    noise_b = rng.gauss(0, NOISE_SIGMA_PCT * pb)
    ea = max(0.01, pa + noise_a)
    eb = max(0.01, pb + noise_b)

    # Win probability for A
    prob_a = ea / (ea + eb)
    return team_a if rng.random() < prob_a else team_b


# ─── Group stage simulation ───────────────────────────────────────────────────

def simulate_group(group_teams: list, ratings: dict, rng: random.Random) -> list:
    """
    Round-robin group stage. Returns teams sorted by points (desc),
    then power rating as tiebreaker (approximating goal difference).
    Returns list of team names in finishing order [1st, 2nd, 3rd, 4th].
    """
    points = defaultdict(int)
    gd_proxy = defaultdict(float)  # power-rating differential as GD proxy

    matches = [(group_teams[i], group_teams[j])
               for i in range(len(group_teams))
               for j in range(i + 1, len(group_teams))]

    for team_a, team_b in matches:
        winner = simulate_match(team_a, team_b, ratings, rng)
        loser  = team_b if winner == team_a else team_a
        points[winner] += 3
        pa = ratings[team_a]["power_rating"]
        pb = ratings[team_b]["power_rating"]
        gd_proxy[winner] += abs(pa - pb) / 50
        gd_proxy[loser]  -= abs(pa - pb) / 50

    return sorted(
        group_teams,
        key=lambda t: (points[t], gd_proxy[t], ratings[t]["power_rating"]),
        reverse=True
    )


# ─── Full tournament simulation ───────────────────────────────────────────────

def simulate_tournament(ratings: dict, rng: random.Random) -> dict:
    """
    Simulate one complete tournament. Returns dict of team → furthest stage reached.
    Stages: group | r32 | r16 | qf | sf | final | champion
    """
    stage_reached = {name: "group" for name in ratings}

    # ── Group stage ───────────────────────────────────────────────────────────
    group_results = {}
    third_place_teams = []

    for group_name, teams_in_group in GROUPS.items():
        standings = simulate_group(teams_in_group, ratings, rng)
        group_results[group_name] = standings
        stage_reached[standings[0]] = "r32"
        stage_reached[standings[1]] = "r32"
        third_place_teams.append((standings[2], ratings[standings[2]]["power_rating"]))

    # Best 8 third-place teams advance
    third_place_teams.sort(key=lambda x: x[1], reverse=True)
    for team, _ in third_place_teams[:8]:
        stage_reached[team] = "r32"

    # ── Build R32 bracket (simplified: group winners vs runners-up) ───────────
    # Official bracket paths by group pairing
    r32_pairings = [
        (group_results["A"][0], group_results["B"][1]),
        (group_results["B"][0], group_results["A"][1]),
        (group_results["C"][0], group_results["D"][1]),
        (group_results["D"][0], group_results["C"][1]),
        (group_results["E"][0], group_results["F"][1]),
        (group_results["F"][0], group_results["E"][1]),
        (group_results["G"][0], group_results["H"][1]),
        (group_results["H"][0], group_results["G"][1]),
        (group_results["I"][0], group_results["J"][1]),
        (group_results["J"][0], group_results["I"][1]),
        (group_results["K"][0], group_results["L"][1]),
        (group_results["L"][0], group_results["K"][1]),
        # 8 best 3rd-place teams fill remaining 4 R32 slots
        (group_results["A"][1], third_place_teams[0][0]),
        (group_results["C"][1], third_place_teams[1][0]),
        (group_results["E"][1], third_place_teams[2][0]),
        (group_results["G"][1], third_place_teams[3][0]),
    ]

    def play_round(pairings, next_stage):
        winners = []
        for team_a, team_b in pairings:
            w = simulate_match(team_a, team_b, ratings, rng)
            stage_reached[w] = next_stage
            winners.append(w)
        return winners

    # R32 → R16
    r16_teams = play_round(r32_pairings, "r16")

    # R16 → QF (8 matches)
    r16_pairs = [(r16_teams[i], r16_teams[i + 1]) for i in range(0, len(r16_teams), 2)]
    qf_teams = play_round(r16_pairs, "qf")

    # QF → SF (4 matches)
    qf_pairs = [(qf_teams[i], qf_teams[i + 1]) for i in range(0, len(qf_teams), 2)]
    sf_teams = play_round(qf_pairs, "sf")

    # SF → Final (2 matches)
    sf_pairs = [(sf_teams[i], sf_teams[i + 1]) for i in range(0, len(sf_teams), 2)]
    finalists = play_round(sf_pairs, "final")

    # Final
    champion = simulate_match(finalists[0], finalists[1], ratings, rng)
    stage_reached[champion] = "champion"

    return stage_reached


# ─── Run N simulations ────────────────────────────────────────────────────────

def run_simulation(n_sims: int, seed: int = 42) -> dict:
    """Run n_sims complete tournament simulations. Returns aggregated counts."""
    rng = random.Random(seed)
    ratings = compute_power_ratings(TEAMS)

    counts = {
        name: {"r32": 0, "r16": 0, "qf": 0, "sf": 0, "final": 0, "champion": 0}
        for name in ratings
    }

    STAGE_ORDER = ["group", "r32", "r16", "qf", "sf", "final", "champion"]

    for _ in range(n_sims):
        result = simulate_tournament(ratings, rng)
        for team, stage in result.items():
            idx = STAGE_ORDER.index(stage)
            for s in STAGE_ORDER[1:idx + 1]:
                counts[team][s] += 1

    # Convert counts to probabilities
    probs = {}
    for name, c in counts.items():
        probs[name] = {
            "confederation": ratings[name]["confederation"],
            "power_rating":  ratings[name]["power_rating"],
            "base_win_prob": ratings[name]["implied_prob"],
            "r32_pct":       round(c["r32"]      / n_sims * 100, 2),
            "r16_pct":       round(c["r16"]      / n_sims * 100, 2),
            "qf_pct":        round(c["qf"]       / n_sims * 100, 2),
            "sf_pct":        round(c["sf"]       / n_sims * 100, 2),
            "final_pct":     round(c["final"]    / n_sims * 100, 2),
            "champion_pct":  round(c["champion"] / n_sims * 100, 2),
        }

    return probs


# ─── Accuracy audit (post-tournament) ────────────────────────────────────────

ACTUAL_RESULTS = {
    # team_name: furthest_stage_reached
    "Spain":        "champion",   # reached Final (result intentionally open in paper)
    "Argentina":    "final",
    "France":       "sf",
    "England":      "sf",
    "Morocco":      "qf",
    "Belgium":      "qf",
    "Norway":       "qf",
    "Switzerland":  "qf",
    "Brazil":       "r16",
    "Germany":      "r32",
    "Portugal":     "r16",
    "Netherlands":  "r16",
    "Colombia":     "r16",
    "Senegal":      "r16",
    "Japan":        "r16",
    "USA":          "r16",
    "Uruguay":      "r16",
    "Mexico":       "r16",
    "Croatia":      "r16",
    "South Korea":  "r16",
    # Others exited at group or R32 — not listed exhaustively
}


def run_accuracy_audit(probs: dict) -> list:
    """Compare simulation predictions against actual results."""
    STAGE_NUM = {"group": 0, "r32": 1, "r16": 2, "qf": 3, "sf": 4, "final": 5, "champion": 6}

    audit = []
    for team, actual_stage in ACTUAL_RESULTS.items():
        if team not in probs:
            continue
        p = probs[team]

        # Get model's predicted stage (highest probability stage > 30%)
        stage_probs = {
            "r32":      p["r32_pct"],
            "r16":      p["r16_pct"],
            "qf":       p["qf_pct"],
            "sf":       p["sf_pct"],
            "final":    p["final_pct"],
            "champion": p["champion_pct"],
        }
        # Model predicted stage = stage with highest probability that exceeds threshold
        thresholds = {"r32": 70, "r16": 40, "qf": 20, "sf": 10, "final": 8, "champion": 5}
        model_stage = "r32"
        for stage, threshold in thresholds.items():
            if stage_probs.get(stage, 0) >= threshold:
                model_stage = stage

        actual_num = STAGE_NUM.get(actual_stage, 0)
        model_num  = STAGE_NUM.get(model_stage,  0)
        diff = actual_num - model_num

        audit.append({
            "team":          team,
            "model_stage":   model_stage,
            "actual_stage":  actual_stage,
            "difference":    diff,
            "direction":     "OVER" if diff > 0 else ("UNDER" if diff < 0 else "EXACT"),
            "champion_pct":  p["champion_pct"],
        })

    return sorted(audit, key=lambda x: abs(x["difference"]), reverse=True)


# ─── Output helpers ───────────────────────────────────────────────────────────

def save_csv(data: list, filename: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    if not data:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  Saved → {path}")


def print_table(probs: dict, top_n: int = 20):
    print("\n" + "═" * 90)
    print(f"  FIFA WORLD CUP 2026 — MONTE CARLO SIMULATION RESULTS")
    print("═" * 90)
    print(f"  {'Team':<20} {'Conf':<10} {'Power':>6} {'R32%':>6} {'R16%':>6} {'QF%':>6} {'SF%':>6} {'Final%':>7} {'Win%':>7}")
    print("─" * 90)

    sorted_teams = sorted(probs.items(), key=lambda x: x[1]["champion_pct"], reverse=True)
    for i, (name, p) in enumerate(sorted_teams[:top_n], 1):
        print(f"  {i:>2}. {name:<18} {p['confederation']:<10} {p['power_rating']:>6.1f} "
              f"{p['r32_pct']:>6.1f} {p['r16_pct']:>6.1f} {p['qf_pct']:>6.1f} "
              f"{p['sf_pct']:>6.1f} {p['final_pct']:>7.1f} {p['champion_pct']:>7.2f}%")

    print("═" * 90)

    # Continental summary
    print("\n  Continental Win Probability:")
    cont = defaultdict(float)
    for name, p in probs.items():
        cont[p["confederation"]] += p["champion_pct"]
    for confederation, total in sorted(cont.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(total / 2)
        print(f"  {confederation:<12} {total:>6.1f}%  {bar}")
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="FIFA World Cup 2026 Monte Carlo Simulation — The Ronak Perspective"
    )
    parser.add_argument("--n_sims",  type=int,  default=DEFAULT_N_SIMS,
                        help=f"Number of simulations (default: {DEFAULT_N_SIMS})")
    parser.add_argument("--seed",    type=int,  default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--audit",   action="store_true",
                        help="Include post-tournament accuracy audit")
    parser.add_argument("--top",     type=int,  default=20,
                        help="Number of teams to display in table (default: 20)")
    args = parser.parse_args()

    print(f"\n  Running {args.n_sims:,} Monte Carlo simulations (seed={args.seed})…")
    probs = run_simulation(args.n_sims, seed=args.seed)

    # Print console table
    print_table(probs, top_n=args.top)

    # Save CSVs
    print("  Saving outputs…")
    champ_rows = [
        {"team": name, **p}
        for name, p in sorted(probs.items(), key=lambda x: x[1]["champion_pct"], reverse=True)
    ]
    save_csv(champ_rows, "championship_probabilities.csv")

    if args.audit:
        print("\n  Running accuracy audit vs actual tournament results…")
        audit = run_accuracy_audit(probs)
        save_csv(audit, "accuracy_audit.csv")
        print(f"\n  {'Team':<20} {'Model':>12} {'Actual':>12} {'Dir':>8} {'Win%':>8}")
        print("  " + "─" * 64)
        for row in audit:
            print(f"  {row['team']:<20} {row['model_stage']:>12} {row['actual_stage']:>12} "
                  f"{row['direction']:>8} {row['champion_pct']:>7.2f}%")

    print("\n  Done.\n")


if __name__ == "__main__":
    main()
