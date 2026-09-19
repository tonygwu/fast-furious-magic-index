"""Magic Unit arithmetic. MU = -log10(P)."""
import math


def mu_from_p(p: float) -> float:
    if not (isinstance(p, (int, float)) and 0 < p <= 1):
        raise ValueError(f"probability must be in (0, 1], got {p!r}")
    return -math.log10(p)


def p_from_mu(mu: float) -> float:
    if mu < 0:
        raise ValueError(f"MU must be >= 0, got {mu!r}")
    return 10.0 ** (-mu)


def on_grid(x: float, step: float) -> bool:
    q = x / step
    return abs(q - round(q)) < 1e-9


def odds_label(mu: float, lower_bound: bool = False) -> str:
    """Human odds for an MU value, with one significant figure. 2.5 MU -> '1 in 300'."""
    whole = math.floor(mu + 1e-9)
    frac = mu - whole
    lead = round(10**frac)  # 1 for integer MU, 3 for a half step
    if lead == 10:
        lead, whole = 1, whole + 1
    if whole < 6:
        body = f"1 in {lead * 10**whole:,}"
    elif lead == 1:
        body = f"1 in 10^{whole}"
    else:
        body = f"1 in {lead}×10^{whole}"
    return ("< " if lower_bound else "") + body
