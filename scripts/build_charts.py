"""Build chartbook PNGs from the consolidated benchmark CSV."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "outputs/benchmark_runs/consolidated/summary.csv"
OUT = ROOT / "docs/assets"
OUT.mkdir(parents=True, exist_ok=True)

MODES = ["no_loop", "loop_1", "loop_n"]
MODE_COLOR = {"no_loop": "#4C78A8", "loop_1": "#F58518", "loop_n": "#54A24B"}


def load_rows():
    with open(CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if not r.get("total"):
            continue
        out.append(
            {
                "qid": r["question_id"],
                "mode": r["mode"],
                "total": float(r["total"]),
                "iters": int(r["iterations"]) if r.get("iterations") else 0,
            }
        )
    return out


def mode_averages(rows):
    avgs = {}
    iters = {}
    for m in MODES:
        scores = [r["total"] for r in rows if r["mode"] == m]
        it = [r["iters"] for r in rows if r["mode"] == m]
        avgs[m] = sum(scores) / len(scores) if scores else 0
        iters[m] = sum(it) / len(it) if it else 0
    return avgs, iters


def chart_mode_avg(rows):
    avgs, _ = mode_averages(rows)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(MODES, [avgs[m] for m in MODES], color=[MODE_COLOR[m] for m in MODES])
    ax.set_ylabel("Average score (0–10)")
    ax.set_title("Average benchmark score by mode")
    ax.set_ylim(0, 10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, m in zip(bars, MODES):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.15,
            f"{avgs[m]:.2f}",
            ha="center",
            fontsize=10,
        )
    fig.tight_layout()
    fig.savefig(OUT / "mode_averages.png", dpi=150)
    plt.close(fig)


def chart_per_question(rows):
    qids = sorted({r["qid"] for r in rows})
    x = list(range(len(qids)))
    width = 0.27
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, m in enumerate(MODES):
        ys = []
        for q in qids:
            match = next((r for r in rows if r["qid"] == q and r["mode"] == m), None)
            ys.append(match["total"] if match else 0)
        offsets = [xi + (i - 1) * width for xi in x]
        ax.bar(offsets, ys, width=width, color=MODE_COLOR[m], label=m)
    ax.set_xticks(x)
    ax.set_xticklabels(qids)
    ax.set_ylabel("Score (0–10)")
    ax.set_title("Score per question, by mode")
    ax.set_ylim(0, 10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "per_question.png", dpi=150)
    plt.close(fig)


def chart_iters_vs_score(rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    for m in MODES:
        xs = [r["iters"] for r in rows if r["mode"] == m]
        ys = [r["total"] for r in rows if r["mode"] == m]
        ax.scatter(xs, ys, label=m, color=MODE_COLOR[m], s=70, alpha=0.85)
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Score (0–10)")
    ax.set_title("Iterations vs score — more loops, not always more value")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 10)
    ax.grid(linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "iters_vs_score.png", dpi=150)
    plt.close(fig)


def main():
    rows = load_rows()
    chart_mode_avg(rows)
    chart_per_question(rows)
    chart_iters_vs_score(rows)
    print(f"Wrote charts to {OUT}")


if __name__ == "__main__":
    main()
