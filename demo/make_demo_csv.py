#!/usr/bin/env python3
"""Write a reproducible 800-row CSV with x2 missing under an x1-dependent MAR mask."""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


SEED = 20261101
ROW_COUNT = 800
OUTPUT = Path(__file__).with_name("demo_missing.csv")


def main() -> None:
    rng = random.Random(SEED)
    categories = ("alpha", "beta", "gamma", "delta")
    start_date = date(2024, 1, 1)

    with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("x1", "x2", "x3", "category", "date"))
        writer.writeheader()
        for index in range(ROW_COUNT):
            x1 = rng.gauss(0, 1)
            x2 = 4.0 + 1.25 * x1 + rng.gauss(0, 1.5)
            x3 = 2.0 - 0.4 * x1 + rng.gauss(0, 1.0)
            missing_probability = 1 / (1 + math.exp(-(-1.05 + 0.85 * x1)))
            x2_value = "" if rng.random() < missing_probability else f"{x2:.4f}"
            writer.writerow(
                {
                    "x1": f"{x1:.4f}",
                    "x2": x2_value,
                    "x3": f"{x3:.4f}",
                    "category": rng.choice(categories),
                    "date": (start_date + timedelta(days=index)).isoformat(),
                }
            )

    print(f"Wrote {ROW_COUNT} rows to {OUTPUT} (seed={SEED})")


if __name__ == "__main__":
    main()
