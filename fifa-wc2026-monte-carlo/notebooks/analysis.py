"""
FIFA World Cup 2026 — Analysis & Visualisation Script
======================================================
Run this after simulation.py to generate all charts.
Outputs saved to outputs/charts/

Usage:
    python notebooks/analysis.py

Or open as a Jupyter notebook by copying cells into a .ipynb file.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict
from simulation import run_simulation, TEAMS, compute_power_ratings

# ─── Setup ────────────────────────────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NAVY   = "#1A3A5C"
GOLD   = "#C9A84C"
BLUE   = "#5B9BD5"
LTBLUE = "#D6E8F5"
GREEN  = "#217346"
GRAY   = "#888888"

plt.rcParams.update({
    "font.family":     "Arial",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "grid.alpha":         0.3,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
})


def save_fig(name):
    path = os.path.join(OUTPUT_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ─── Run simulation ───────────────────────────────────────────────────────────

print("Running 10,000 simulations…")
probs = run_simulation(10_000, seed=42)
sorted_teams = sorted(probs.items(), key=lambda x: x[1]["champion_pct"], reverse=True)

# ─── Chart 1: Top 10 Championship Probability (horizontal bar) ────────────────

fig, ax = plt.subplots(figsize=(10, 6))

top10 = sorted_teams[:10]
names  = [t[0] for t in top10]
champs = [t[1]["champion_pct"] for t in top10]
colors = [NAVY if i == 0 else BLUE if i < 3 else LTBLUE for i in range(10)]

bars = ax.barh(names[::-1], champs[::-1], color=colors[::-1], height=0.65, edgecolor="none")

for bar, val in zip(bars, champs[::-1]):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", ha="left", fontsize=10, color=NAVY, fontweight="bold")

ax.set_xlabel("Monte Carlo Championship Probability (%)", fontsize=11, color=GRAY)
ax.set_title("Pre-tournament Monte Carlo championship probability",
             fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax.tick_params(axis="y", labelsize=10)
ax.set_xlim(0, max(champs) * 1.25)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig1_championship_probabilities.png")


# ─── Chart 2: Power Rating vs Win% scatter ────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 7))

ratings = compute_power_ratings(TEAMS)
powers  = [probs[n]["power_rating"]  for n, _ in sorted_teams[:20]]
wins    = [probs[n]["champion_pct"]  for n, _ in sorted_teams[:20]]
names20 = [n for n, _ in sorted_teams[:20]]

ax.scatter(powers, wins, color=NAVY, s=80, zorder=3, alpha=0.85)

# Trend line
z = np.polyfit(powers, wins, 1)
p_line = np.poly1d(z)
x_range = np.linspace(min(powers) - 2, max(powers) + 2, 100)
ax.plot(x_range, p_line(x_range), color=BLUE, linewidth=1.5, linestyle="--", alpha=0.7)

for name, x, y in zip(names20, powers, wins):
    ax.annotate(name, (x, y), textcoords="offset points",
                xytext=(5, 3), fontsize=7.5, color=NAVY)

ax.set_xlabel("Composite Power Rating (0–100)", fontsize=11, color=GRAY)
ax.set_ylabel("Monte Carlo Win Probability (%)", fontsize=11, color=GRAY)
ax.set_title("Composite power rating vs. simulated title probability",
             fontsize=13, fontweight="bold", color=NAVY, pad=14)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig2_power_vs_winpct.png")


# ─── Chart 3: Continental probability ────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))

cont = defaultdict(float)
for name, p in probs.items():
    cont[p["confederation"]] += p["champion_pct"]

conf_order  = ["UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"]
conf_labels = ["Europe (UEFA)", "South America", "Africa", "North America", "Asia", "Oceania"]
conf_vals   = [cont.get(c, 0) for c in conf_order]
conf_colors = [NAVY, BLUE, LTBLUE, "#B5D4F4", "#D6E8F5", "#EBF3FB"]

bars = ax.bar(conf_labels, conf_vals, color=conf_colors, edgecolor="none", width=0.6)

for bar, val in zip(bars, conf_vals):
    if val > 0.5:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.0f}%", ha="center", fontsize=11, fontweight="bold", color=NAVY)

ax.set_ylabel("Combined championship probability (%)", fontsize=11, color=GRAY)
ax.set_title("Pre-tournament championship probability by confederation",
             fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax.tick_params(axis="x", labelsize=9)
ax.set_ylim(0, max(conf_vals) * 1.2)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig3_continental_probability.png")


# ─── Chart 4: Projected vs Actual depth (pre-Final audit) ────────────────────

STAGE_NUM = {"group": 0, "r32": 1, "r16": 2, "qf": 3, "sf": 4, "final": 5, "champion": 6}
STAGE_LABELS = ["Not proj.", "R32", "R16", "QF", "SF", "Final", "Champion"]

ACTUAL = {
    "Spain": "final", "Argentina": "final", "France": "sf", "England": "sf",
    "Morocco": "qf", "Belgium": "qf", "Norway": "qf", "Switzerland": "qf",
    "Brazil": "r16", "Germany": "r32", "Portugal": "r16",
}

THRESHOLD = {"r32": 70, "r16": 40, "qf": 20, "sf": 10, "final": 8, "champion": 5}

def model_predicted_stage(p):
    stage_probs = {
        "r32": p["r32_pct"], "r16": p["r16_pct"], "qf": p["qf_pct"],
        "sf": p["sf_pct"], "final": p["final_pct"], "champion": p["champion_pct"]
    }
    result = "r32"
    for stage, thr in THRESHOLD.items():
        if stage_probs.get(stage, 0) >= thr:
            result = stage
    return result

teams_audit = list(ACTUAL.keys())
model_nums  = [STAGE_NUM[model_predicted_stage(probs[t])] for t in teams_audit]
actual_nums = [STAGE_NUM[ACTUAL[t]] for t in teams_audit]

x = np.arange(len(teams_audit))
width = 0.35

fig, ax = plt.subplots(figsize=(13, 6))
b1 = ax.bar(x - width/2, model_nums,  width, label="Pre-tournament projection", color=NAVY,  alpha=0.85)
b2 = ax.bar(x + width/2, actual_nums, width, label="Actual stage before Final",  color=GOLD,  alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels(teams_audit, rotation=25, ha="right", fontsize=9)
ax.set_yticks(range(7))
ax.set_yticklabels(STAGE_LABELS, fontsize=9)
ax.set_title("Projected depth vs. actual tournament depth",
             fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax.legend(fontsize=9)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig4_projected_vs_actual.png")


# ─── Chart 5: Knockout forecast accuracy (5/8, 3/4, 1/2) ─────────────────────

fig, ax = plt.subplots(figsize=(8, 5))

stages     = ["Quarterfinalists", "Semifinalists", "Finalists"]
numerators = [5, 3, 1]
denominators = [8, 4, 2]
pcts = [n / d * 100 for n, d in zip(numerators, denominators)]
labels = [f"{n}/{d}" for n, d in zip(numerators, denominators)]

bars = ax.bar(stages, pcts, color=[NAVY, BLUE, LTBLUE], edgecolor="none", width=0.5)

for bar, label, pct in zip(bars, labels, pcts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            label, ha="center", fontsize=14, fontweight="bold", color=NAVY)

ax.set_ylabel("Exact team overlap (%)", fontsize=11, color=GRAY)
ax.set_title("How much of the projected knockout field materialised?",
             fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax.set_ylim(0, 110)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig5_knockout_accuracy.png")


# ─── Chart 6: Spain probability journey ──────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))

milestones  = ["Pre-tournament\nfavourite", "Quarterfinal\nreached", "Semifinal\nwon", "Final\nreached", "Champion"]
spain_probs = [19.1, 51.0, 30.5, 22.0, None]
x_pts = list(range(len(milestones)))

solid_x = [i for i, v in enumerate(spain_probs) if v is not None]
solid_y = [v for v in spain_probs if v is not None]

ax.plot(solid_x, solid_y, color=NAVY, linewidth=2.5, marker="o", markersize=8, zorder=3)
ax.plot([solid_x[-1], len(milestones) - 1], [solid_y[-1], solid_y[-1]],
        color=NAVY, linewidth=2, linestyle="--", alpha=0.5)

open_circle = plt.Circle((len(milestones) - 1, solid_y[-1]), 0.15,
                          color="white", ec=NAVY, linewidth=2, zorder=4)
ax.add_patch(open_circle)

ax.annotate("Final outcome\nintentionally left open",
            xy=(len(milestones) - 1, solid_y[-1]),
            xytext=(len(milestones) - 1.2, solid_y[-1] + 8),
            arrowprops=dict(arrowstyle="-", color=GRAY, lw=1),
            fontsize=8, color=GRAY, ha="center")

ax.set_xticks(x_pts)
ax.set_xticklabels(milestones, fontsize=9)
ax.set_ylabel("Pre-tournament modelled probability (%)", fontsize=10, color=GRAY)
ax.set_title("Spain: the model's highest-conviction call remains unresolved",
             fontsize=12, fontweight="bold", color=NAVY, pad=14)
ax.set_ylim(0, 65)

fig.text(0.99, 0.01, "The Ronak Perspective  ·  theronakperspective.wordpress.com",
         ha="right", fontsize=7, color=GRAY, style="italic")

save_fig("fig6_spain_probability_journey.png")

print("\n  All 6 charts saved to outputs/charts/")
print("  Done.\n")
