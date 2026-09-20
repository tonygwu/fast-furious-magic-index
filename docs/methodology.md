# Standard FF-MU-1 — how a Magic Unit is assigned

One **Magic Unit (MU)** is one order of magnitude of improbability.

```
MU = −log10(P)
```

P is the chance the depicted outcome happens **given that the attempt begins**, under real-world physics, biology and
institutions, with the best real professional for the job and the equipment the film shows. Under that reference
class ordinary movie driving scores about 0 MU. Only the impossible part scores.

| Odds | MU |
|---|---|
| 1 in 10 | 1 |
| 1 in 1,000 | 3 |
| 1 in a million | 6 |
| 1 in a trillion | 12 (the cap) |

## Events and components

An **event** is one continuous attempt with one success condition, scoring at least 2 MU. Inside it, each separate
way the attempt could fail is a **component**. Components chain as conditional probabilities, so their MU values add.
Each one carries a low, a central and a high estimate; the event's range is the sum of the parts.

## Evidence types

Every component declares where its number comes from.

| Type | Meaning | Example |
|---|---|---|
| **E1** | Empirical frequency | NHTSA injury-risk curves by delta-V; Golden Gate survival rates |
| **E2** | Physics model plus a measured tolerance | the rocket equation; tyre grip against required towing force |
| **E3** | Geometry or timing | a landing window divided by the plausible spread |
| **E4** | Judgment prior | no usable data exists, so the estimate is explicitly a judgment |

## The two caps, and which one usually binds

**The Record Horizon: 12 MU per component.** One in a trillion is roughly one year of every car trip on Earth
(the US alone made 220 billion vehicle trips in 2017). Beyond that, no dataset in any of these domains supports a
number, so a component that breaks a hard limit stops here and is displayed as a lower bound, "≥". An event can
exceed 12 MU only by stacking separate failure modes, never by inventing a smaller probability.

**The judgment cap: 3 MU per component.** A component resting on judgment alone (E4) cannot exceed 1 in 1,000.
This is the binding constraint on most of the dataset: about half of all components are E4. It exists so that
guesswork cannot inflate a score.

**When a component is capped.** A cap asserts a measured hard limit, so it requires a comparison of **sourced**
quantities giving required over available of 3 or more, under the assumptions most favourable to the stunt. If a
quantity that comparison needs is unknown — the mechanism, a magnet's field strength, an unpublished mass — the
component cannot claim a hard limit and is held at the judgment cap instead. Two validator rules enforce this: a
capped component must cite at least one reference, and an uncapped component may not argue a hard limit in its
reasoning.

Worked examples:

- **Capped.** The Fast Five vault: sliding 20 t of steel needs about 59 kN; two Chargers can apply about 17 kN
  before their tyres spin. Both figures are sourced, and the ratio is 3–7x.
- **Not capped.** The F&F6 tank flip and the F9 magnet feats: no source describes the mechanism, so no ratio can be
  computed, and they are held at 3 MU.
- **Not capped.** The Fate torpedo: its gentlest corner needs 1.5x the plausible human force, which is under the
  threshold, so it keeps a wide 3–12 MU range instead of a cap.

## Attribution

Everyone in a stunt receives the full score of the components they are credited with. Two people in one car both get
the full value. Character totals therefore add up to **more** than scene totals: they are an additive index of
absurdity, not the probability of a life. Credits follow roles: physics goes to whoever controls or rides the object,
survival to each survivor, skill only to the performer, coincidence to whoever it benefits.

## Uncertainty

Each component's low, central and high values are summed to give an event's plausibility envelope. A seeded Monte
Carlo (10,000 draws) then draws each component from a triangular distribution and ranks every scene and character in
every draw, which is what the tie statements on the site are based on. Capped components are held fixed, because they
are lower bounds rather than estimates.

## Plot armor

Resurrections, retcons, magic surveillance and vanishing legal consequences are counted on a separate ordinal track
(1 = convenient but explained, 2 = unexplained, 3 = contradicts canon or reverses a death). Plot armor is **never**
converted into Magic Units, because narrative convenience and physical improbability do not share a scale.

## What this cannot do

- Screen time is estimated from scene-by-scene presence logs, not measured frame by frame, so the per-minute board
  is a band rather than a ranking.
- A scene with only one source is not scored at all, which holds some films below their true total. Fast X is the
  most affected.
- Above the cap, scores are lower bounds, so a larger gap between two capped scenes is not a real difference.
- The scores rest on written descriptions of the films, plus a few confirmations from the project owner's own
  viewing. Details that exist only on screen are flagged per event as "visually unverified".
