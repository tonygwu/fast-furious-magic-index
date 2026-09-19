"""Strict loaders for the hand-authored YAML data. Unknown or missing fields raise."""
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .config import Config, load_config


class DataError(Exception):
    pass


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


Category = Literal["physics", "survival", "skill", "coincidence"]
CATEGORIES: tuple[str, ...] = ("physics", "survival", "skill", "coincidence")
Role = Literal["controller", "occupant", "performer", "survivor", "beneficiary"]


class Film(Strict):
    id: str
    title: str
    year: int
    runtime_min: float
    release_order: int
    spinoff: bool


class Character(Strict):
    id: str
    name: str
    aliases: list[str]


class Source(Strict):
    id: str
    kind: Literal["plot", "physics", "empirical", "analysis", "bts", "literature", "spec", "screenplay"]
    title: str
    url: str


class Reference(Strict):
    id: str
    quantity: str
    value: float | str
    unit: str
    basis: Literal["film", "location", "analysis", "spec", "literature", "estimate"]
    source: str
    note: str


class MU(Strict):
    low: float
    central: float
    high: float


class Credit(Strict):
    character: str
    role: Role


class Component(Strict):
    id: str
    category: Category
    subtype: str
    claim: str
    evidence: Literal["E1", "E2", "E3", "E4"]
    mu: MU
    capped: bool
    reasoning: str
    dependence: str
    references: list[str]
    credits: list[Credit]


class Event(Strict):
    id: str
    title: str
    sequence: str
    depicted: str
    inferred: str
    post_credit: bool
    in_universe_excuse: Optional[str]
    visually_unverified: list[str]
    confidence: Literal["low", "medium", "high"]
    participants: list[str]
    plot_sources: list[str]
    components: list[Component] = Field(min_length=1)


class EventFile(Strict):
    film: str
    events: list[Event]


class PlotArmor(Strict):
    id: str
    film: str
    title: str
    characters: list[str]
    kind: Literal["resurrection", "retcon", "information", "institutional", "amnesia", "other"]
    level: Literal[1, 2, 3]
    justification: str
    sources: list[str]


class Rejected(Strict):
    id: str
    film: str
    title: str
    reason: Literal["below_threshold", "not_depicted", "merged", "plot_armor", "ordinary", "insufficient_sources"]
    merged_into: Optional[str]
    note: str


class Scene(Strict):
    n: int
    start: float
    end: float
    title: str
    characters: list[str]


class PresenceLog(Strict):
    film: str
    anchors: list[str]
    scenes: list[Scene] = Field(min_length=1)


class Dataset(Strict):
    config: Config
    films: list[Film]
    characters: list[Character]
    sources: list[Source]
    references: list[Reference]
    event_files: list[EventFile]
    plot_armor: list[PlotArmor]
    rejected: list[Rejected]
    presence: list[PresenceLog]

    @property
    def events(self) -> list[tuple[str, Event]]:
        return [(f.film, e) for f in self.event_files for e in f.events]

    def film(self, fid: str) -> Film:
        return next(f for f in self.films if f.id == fid)


def _yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise DataError(f"{path}: {e}") from e


def _parse(model, raw, where):
    try:
        return model(**raw)
    except (ValidationError, TypeError) as e:
        raise DataError(f"{where}: {e}") from e


def load_dataset(data_dir: Path) -> Dataset:
    d = Path(data_dir)
    lst = lambda name, model: [_parse(model, r, f"{name}[{i}]") for i, r in enumerate(_yaml(d / name) or [])]
    return Dataset(
        config=load_config(d / "config.yaml"),
        films=lst("films.yaml", Film),
        characters=lst("characters.yaml", Character),
        sources=lst("sources.yaml", Source),
        references=lst("references.yaml", Reference),
        event_files=[_parse(EventFile, _yaml(p), str(p)) for p in sorted((d / "events").glob("*.yaml"))],
        plot_armor=lst("plot_armor.yaml", PlotArmor),
        rejected=lst("rejected.yaml", Rejected),
        presence=[_parse(PresenceLog, _yaml(p), str(p)) for p in sorted((d / "screen_time").glob("*.yaml"))],
    )
