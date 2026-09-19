import math

import pytest

from ff_magic.magic import mu_from_p, p_from_mu, on_grid, odds_label


def test_mu_definition():
    assert mu_from_p(0.1) == pytest.approx(1)
    assert mu_from_p(1e-3) == pytest.approx(3)
    assert mu_from_p(1e-6) == pytest.approx(6)
    assert mu_from_p(1e-30) == pytest.approx(30)


def test_round_trip():
    for mu in [0, 0.5, 2, 7.5, 12]:
        assert mu_from_p(p_from_mu(mu)) == pytest.approx(mu)


@pytest.mark.parametrize("p", [0, -0.1, 1.5, math.nan])
def test_mu_rejects_invalid_probability(p):
    with pytest.raises(ValueError):
        mu_from_p(p)


def test_on_grid():
    assert on_grid(2.5, 0.5)
    assert not on_grid(2.3, 0.5)


def test_odds_label():
    assert odds_label(6) == "1 in 10^6"
    assert odds_label(2) == "1 in 100"
    assert odds_label(1) == "1 in 10"
    assert odds_label(2.5) == "1 in 300"
    assert odds_label(14, lower_bound=True) == "< 1 in 10^14"
