"""Standard empirical curves used in component reasoning. Each returns MU (= -log10 P(outcome)).
Every curve notes its validated range; values outside it are extrapolations and must be flagged."""
import math

# NHTSA DOT HS 813 219 (Wang 2022), logit = a + b*D, D = delta-V in mph. Fit range: D <= 60 mph.
NHTSA = {
    ("frontal", "fatal"): (-9.0422, 0.1571),
    ("frontal", "mais2"): (-4.9429, 0.1425),
    ("all", "fatal"): (-8.9819, 0.1603),
    ("all", "mais2"): (-5.1331, 0.1479),
}
NHTSA_FIT_MAX_MPH = 60


def _logistic(x):
    return 1 / (1 + math.exp(-x))


def crash_survive_mu(dv_mph: float, mode: str = "all") -> float:
    """MU of surviving a crash with this delta-V (restrained occupant, modern car)."""
    a, b = NHTSA[(mode, "fatal")]
    return -math.log10(1 - _logistic(a + b * dv_mph))


def crash_walkaway_mu(dv_mph: float, mode: str = "all") -> float:
    """MU of walking away with at most minor injury (MAIS 0-1)."""
    a, b = NHTSA[(mode, "mais2")]
    return -math.log10(1 - _logistic(a + b * dv_mph))


if __name__ == "__main__":
    for d in (30, 40, 50, 60, 80, 100):
        flag = " (extrapolated)" if d > NHTSA_FIT_MAX_MPH else ""
        print(f"dv {d:>3} mph: survive {crash_survive_mu(d):.2f} MU, walk away {crash_walkaway_mu(d):.2f} MU{flag}")
