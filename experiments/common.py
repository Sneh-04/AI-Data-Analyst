"""Shared helpers for the experiment scripts: path setup, environment capture, statistics."""
import json
import os
import platform
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ml-service"))
RESULTS_DIR = os.environ.get("AI_DATA_ANALYST_RESULTS_DIR") or tempfile.mkdtemp(
    prefix="ai-data-analyst-research-"
)
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_environment(extra: dict | None = None, name: str = "environment.json") -> None:
    """Record library versions + config so a run can be reproduced and audited."""
    import numpy, pandas, scipy, sklearn, statsmodels
    info = {
        "python": platform.python_version(),
        "numpy": numpy.__version__, "pandas": pandas.__version__, "scipy": scipy.__version__,
        "scikit-learn": sklearn.__version__, "statsmodels": statsmodels.__version__,
    }
    info.update(extra or {})
    with open(os.path.join(RESULTS_DIR, name), "w") as fh:
        json.dump(info, fh, indent=2, sort_keys=True)


def holm_adjust(pvalues):
    """Holm-Bonferroni step-down adjustment of a list of p-values (controls family-wise error)."""
    import numpy as np
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted
