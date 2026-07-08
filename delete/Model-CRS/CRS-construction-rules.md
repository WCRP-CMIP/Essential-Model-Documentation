# CRS Construction Rules

**Canonical Realm String** — a compact, deterministic string encoding the
embedding and coupling structure of an earth system model.

---

## Realm order

All sorting uses this fixed sequence:

```
A   Ac   Ae   L   Li   O   Ob   Si
```

atmosphere · atmos-chem · aerosol · land · land-ice · ocean · ocean-biogeo · sea-ice

---

## Definitions

| Term | Meaning |
|---|---|
| **Embedded realm** | Has a parent host. Written in `[brackets]` on the host. Cannot couple. |
| **Superior host** | Not embedded in anything. Forms the coupling graph. |
| **Coupling graph** | Graph of superior hosts connected by coupling edges. |

---

## Step 1 — Build the embedding string for each superior host

For each superior host, write its code followed by each embedded child in
`[brackets]`, children sorted by realm order. Each child expands recursively.

```
Host A, with Ac embedded in A, and Ae embedded in Ac:

  A[Ac[Ae]]

Host O, with Ob and Si both embedded directly in O:

  O[Ob][Si]
```

This embedding string is what gets placed into the coupling string below.

---

## Step 2 — Identify the coupling graph topology

Apply the first matching rule:

### Rule A — Single host (no couplings)

Write the embedding string. Done.

```
A[Ac[Ae]]
```

---

### Rule B — Full clique, 4 or more hosts

Every host couples with every other host. Write `*{` + hosts in realm order + `}`.

```
*{A[Ac[Ae]]  L  Li  O[Ob][Si]}

Means: A, L, Li, O all coupled to each other (6 pairs)
* signals fully connected
```

> Note: `*{}` is only used for 4+ node cliques. A 3-node clique is just a cycle (Rule C).

---

### Rule C — A cycle exists

Find the **longest simple cycle**. If there is a tie in length, pick the
lexicographically earliest sequence (start at the lowest realm-order node,
then take nodes in the order that reads earliest left-to-right by realm index).

Write the cycle nodes in order, wrapped in `{ }`.

```
Three hosts A, L, O all coupled:

  {A[Ac]  L  O[Ob][Si]}

Four hosts A, L, O, Li forming a ring A–L–O–Li–A:

  {A  L  O[Ob][Si]  Li}
```

**Chords** — a coupling edge between two cycle nodes that is *not* a cycle
edge (a "shortcut" across the ring). Write `(X)` immediately after the
**earlier** of the two nodes in the cycle order. `X` is bare code only — no
re-expansion, because X already appears in full elsewhere in the string.

```
Cycle A–L–O–Li plus extra edge A–O:

  {A(O)  L  O[Ob][Si]  Li}
       ^
       chord: A also links directly to O
```

**Off-cycle branches** — a host not in the cycle. Write `(embStr)` after the
first cycle node it connects to. Full expansion because this is the only place
it appears.

```
Cycle {A L O} plus extra host Si coupled only to O:

  {A  L  O(Si)}
```

---

### Rule D — No cycle (chain)

Find the **longest canonical chain** (same lex tiebreak as above). Write nodes
in chain order.

**Off-chain branches** — same as off-cycle branches: `(embStr)` after the
chain node they connect to.

```
Chain A–L–O, plus Li coupled only to A:

  A(Li)  L  O[Ob][Si]

Chain A–L, O branches off L:

  A  L(O[Ob][Si])
```

---

## Summary table

| Situation | Notation | Example |
|---|---|---|
| Single host | bare embedding | `A[Ac[Ae]]` |
| Full clique 4+ | `*{...}` | `*{A[Ac]LLiO}` |
| Cycle (3+ nodes) | `{...}` | `{A[Ac]LO[Ob][Si]}` |
| Chord on cycle | `(X)` at earlier node | `{A(O)LO[Ob]Li}` |
| Branch off cycle/chain | `(embStr)` at host | `{ALO(Li)}` |
| Chain (no cycle) | bare sequence | `A[Ac]LO[Ob]` |

---

## Real model examples

| Model | Compact CRS |
|---|---|
| CNRM-ESM2-1e | `{A[Ac][Ae]LO[Ob][Si]}` |
| UKESM1 (K4 coupling) | `*{A[Ac[Ae]]LLiO[Ob][Si]}` |
| HadGEM3-GC31 | `{A L O[Si]}` |
| Atmosphere only | `A[Ac[Ae]]` |
| 4-cycle A–L–O–Li | `{A[Ac]LO[Ob][Si]Li}` |
| K4 minus L–Li | `{A(O)LO[Ob][Si]Li}` |

---

## Canonicality guarantee

Because every step uses the fixed realm order for all tie-breaking, the same
coupling graph always produces the same string regardless of the order in which
embeddings and couplings are supplied.
