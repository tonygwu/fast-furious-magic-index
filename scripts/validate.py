"""Validate data/. Prints PASS/FAIL with the check count and every failure. Exit 1 on failure."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ff_magic.dataset import load_dataset  # noqa: E402
from ff_magic.validate import validate  # noqa: E402

data = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data"
ds = load_dataset(data)
rep = validate(ds)
n_ev = len(ds.events)
n_comp = sum(len(e.components) for _, e in ds.events)
for f in rep.failures:
    print("FAIL:", f)
status = "PASS" if not rep.failures else "FAIL"
print(f"{status}: {rep.n_checks} checks; {n_ev} events; {n_comp} components; {len(ds.rejected)} rejected; "
      f"{len(ds.plot_armor)} plot-armor items; {len(rep.failures)} failures")
sys.exit(0 if not rep.failures else 1)
