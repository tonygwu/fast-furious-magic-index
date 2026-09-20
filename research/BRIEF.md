# Research brief: per-film inventory for the Fast & Furious Magic Index

> **Provenance.** The brief every per-film research pass followed. It sets the sourcing bar (two independent
> sources per candidate), the separation of what is depicted from what is inferred, and the rule that researchers
> gather facts while a single analyst assigns every score, so the scale stays consistent across films.

You research ONE film. You gather facts and sources. You do NOT assign probabilities or Magic Units.
One analyst scores all films later, so consistency depends on you not scoring.

## Project in one paragraph

We rank the most physically improbable events in the Fast & Furious franchise. The unit is the
Magic Unit (MU = -log10 P), where P is the chance the depicted outcome happens if an elite real-world
professional attempts it with the equipment shown. Your job is the factual base: what the film
actually shows, who takes part, and the real-world numbers an analyst needs to do physics.

## Rules

- Walk the WHOLE film in order, not only the famous scenes. Selection bias toward memorable scenes is
  the risk we most need to avoid. List every action set piece and every survival, stunt, or
  coincidence that a sceptical viewer would call implausible, even mild ones. Also list items you
  considered and think are ordinary (they go to a rejected log), with one line why.
- Theatrical cut only. Include mid- and post-credit scenes and mark them. Exclude deleted scenes.
- Separate DEPICTED (what the film visibly shows) from INFERRED (what you or sources deduce).
  If sources disagree about who is in a car, who survives, or what happens, say so explicitly.
- Every candidate needs at least 2 independent sources for what happens (Wikipedia plot, the
  Fast & Furious Fandom wiki, reputable reviews or recaps, screenplay/transcript where legally
  accessible, official Universal clip titles/descriptions, stunt/VFX interviews). Give URLs.
  If you only have 1 source, mark `sources_ok: false`.
- Collect real-world parameters the analyst will need, with URLs: distances (e.g. tower
  separation), vehicle masses/power/top speed, heights of falls, speeds shown or stated, runway or
  bridge lengths, and any published fan/physicist analyses of the stunt (e.g. "how long is the
  runway" analyses). Say whether a number comes from the film, the real location, or an analysis.
- Note behind-the-scenes facts only when they constrain what is depicted (for example the real cars
  used, a real drop height).
- Do not invent numbers. If you cannot find a figure, write `unknown` and what search you tried.
- Plot/continuity items (resurrections, amnesia, retcons, magic surveillance, pardons, implausible
  access or knowledge) go in a separate `plot_armor` list.
- Screen presence: build a scene-by-scene presence log for the whole runtime. For each scene give
  approximate start and end minutes, and which named characters are on screen. Blu-ray/DVD chapter
  lists with timestamps (e.g. dvdcompare.net, chapter databases), timestamped recaps, or official
  runtime are good anchors; say what anchors you used. The scene durations should add up to the
  runtime (including credits). Mark durations as estimates. Also record any published screen-time
  measurement for any character in this film (these are rare; say if you found none).

## Output

Write exactly one file: `research/<film_id>.md` (path given in your task). Use this structure:

```markdown
# <Title> (<year>) — film_id <id>
Runtime: <minutes> (source URL). Credits start approx <min>.
Sources consulted: <list of URLs with one-line description>

## Candidates
### <film_id>-c01 <short title>
- sequence: <which set piece it belongs to>
- approx_time: <minutes into film, or unknown>
- characters: <name (role: driver/occupant/performer/survivor/beneficiary)>, ...
- depicted: <what the film shows, concrete>
- inferred: <what is deduced, and by whom>
- real_world_params: <param = value (source URL, film|location|analysis)>; ...
- sources: <URL>, <URL>
- sources_ok: true|false
- post_credit: false
- notes / disagreements:

## Rejected (considered, ordinary)
- <short title> — <why ordinary>

## Plot armor
### <film_id>-p01 <short title>
- characters:
- what: <resurrection / retcon / info magic / institutional / amnesia ...>
- explained_in_film: yes|no|partly — how
- contradicts_prior_canon: yes|no — what
- sources:

## Presence log
| # | start | end | scene | characters on screen |
Anchors used: ...
Published screen-time measurements found: ...

## Open questions for the analyst
```

Keep descriptions concrete and short. Accuracy beats volume, but completeness of the walk-through
matters. Close with a five-line summary: number of candidates, number with sources_ok false,
the 3 most extreme candidates, and anything you could not verify.
