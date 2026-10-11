"""
Does the health-score "MNAR signal" detector (health_service.detect_mnar_signals) actually
discriminate missingness mechanisms?  Uses the same real datasets and masks as the imputation
benchmark. For each (dataset, mechanism, rate, trial) the detector is run on the masked table and we
record whether it raised any signal.

Expected, and worth stating plainly: MNAR is *not identifiable* from the observed data alone, and the
detector only looks for correlation between a column's missingness and OTHER observed columns -- so
it can flag MAR (missingness driven by an observed column) as well as MNAR (when the hidden value is
correlated with observed columns), and cannot flag pure MNAR on an uncorrelated column. This script
measures how it behaves in practice rather than assuming.

Run: python3 mnar_detector_benchmark.py
"""
import itertools
import warnings

import numpy as np
import pandas as pd

from common import RESULTS_DIR
from imputation_research_benchmark import MECHANISMS, RATES, SEED, load_datasets, make_mask
from app.services.health_service import detect_mnar_signals

warnings.filterwarnings("ignore")
N_TRIALS = 12


def main():
    rows = []
    for (name, df), mech, rate, trial in itertools.product(load_datasets().items(), MECHANISMS, RATES, range(N_TRIALS)):
        rng = np.random.RandomState(SEED + 1000 * trial + int(rate * 100) + MECHANISMS.index(mech))
        masked = df.mask(make_mask(df, mech, rate, rng))
        signals = detect_mnar_signals(masked)
        rows.append({"dataset": name, "mechanism": mech, "rate": rate, "trial": trial,
                     "flagged": len(signals) > 0, "n_signals": len(signals)})
    raw = pd.DataFrame(rows)
    raw.to_csv(f"{RESULTS_DIR}/mnar_detector_raw.csv", index=False)
    table = raw.groupby(["mechanism", "rate"]).flagged.mean().unstack("rate").round(3)
    by_dataset = raw.groupby(["dataset", "mechanism"]).flagged.mean().unstack("mechanism").round(3)
    table.to_csv(f"{RESULTS_DIR}/mnar_detector_summary.csv")
    print("Fraction of masked tables for which the detector raised >=1 signal:")
    print(table.to_markdown())
    print("\nBy dataset:")
    print(by_dataset.to_markdown())


if __name__ == "__main__":
    main()
