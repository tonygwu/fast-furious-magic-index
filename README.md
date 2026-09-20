# The Fast & Furious Magic Index

**Live: https://fast-furious.tonygwu.com**

How impossible are the Fast & Furious movies? This project scores every major stunt in the franchise with an
over-serious probability method.

**One Magic Unit (MU) = one order of magnitude of improbability.** MU = −log10(P), where P is the chance that the
depicted outcome happens if the best real-world professional attempts it with the equipment the film shows.
1 in 10 is 1 MU; 1 in a million is 6 MU.

- Each scene is split into separate failure modes (components), each with its own evidence, reasoning and
  low / central / high estimate.
- One component can score at most 12 MU (1 in a trillion, roughly every car trip on Earth in a year). A component
  that breaks a hard physical limit sits at that cap and is shown as a lower bound ("≥").
- Character totals give full credit to everyone in a stunt, so they add up to more than the scene totals. They are an
  additive absurdity index, not a joint probability.
- Plot armor (resurrections, retcons, magic surveillance) is scored separately and never converted to MU.

Methodology details: `docs/scene-notes.md` (every worksheet, generated) and `docs/DECISIONS.md`.

## Layout

| Path | What it is |
|---|---|
| `data/` | Hand-authored scores, sources, references and presence logs (YAML) |
| `ff_magic/` | Scoring engine: schema, validation, aggregation, rank-stability simulation |
| `scripts/` | `validate.py`, `build.py`, `import_presence.py` |
| `build/`, `web/data.js`, `docs/scene-notes.md` | Generated from `data/`; a test fails if they are stale |
| `research/*.md` | Raw per-film research notes written by AI research agents from `research/BRIEF.md`, addressed to a human analyst. Kept for provenance; the scores in `data/` were assigned separately. |

## Deploy

The site is a static page served from `web/` by Cloudflare (Workers static assets).

```sh
scripts/render_cards.sh      # regenerate the social cards from the page
npx wrangler deploy          # publish web/ to fast-furious.tonygwu.com
```

## Build and test

```sh
uv run python scripts/validate.py
uv run python scripts/build.py
uv run pytest -q
```

## Sources

Every source is listed with its URL in `data/sources.yaml`; physical quantities are in `data/references.yaml`.
Third-party pages and PDFs were consulted but are not redistributed here. A few scenes rely on the project owner's
own viewing (sources marked "Project owner's viewing confirmation").

## Disclaimer

Unofficial fan commentary and parody. Not affiliated with or endorsed by Universal Pictures. "Fast & Furious" is a
trademark of its owner. No film stills or studio artwork are included.

## Licensing

- **Code** (`ff_magic/`, `scripts/`, `tests/`): MIT, see `LICENSE`.
- **Data and write-ups** (`data/`, `docs/`, `research/`, `build/`, `web/data.js`): Creative Commons Attribution 4.0
  (CC BY 4.0), see `LICENSE-CONTENT`. Credit "The Fast & Furious Magic Index, Tony Wu".
