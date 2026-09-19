"""Scoring configuration. Every key is required; there are no defaults."""
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError


class ConfigError(Exception):
    pass


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    record_horizon_mu: float
    judgment_cap_mu: float
    event_threshold_mu: float
    mu_step: float
    min_plot_sources_ranked: int
    board_min_events: int
    board_min_minutes: float
    presence_low_factor: float
    presence_high_factor: float
    presence_central_factor: float
    presence_char_error: float
    runtime_tolerance: float
    mc_draws: int
    mc_seed: int
    tier_break_prob: float


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text())
    try:
        return Config(**raw)
    except ValidationError as e:
        raise ConfigError(f"{path}: {e}") from e
