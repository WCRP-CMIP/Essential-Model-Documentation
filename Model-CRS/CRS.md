# Canonical Realm String (CRS)

## What is Model-CRS?

A **compact, deterministic string** that uniquely represents how realms in your earth system model are connected via embeddings and couplings.

- **Fingerprint**: Two identical models always produce identical CRS strings
- **Minimal**: Represents complex graphs in 20-50 characters
- **Deterministic**: Same structure → same string, regardless of construction order
- **Reversible**: Can parse back to get embeddings and couplings

Example: `A[Ac[Ae]](O,L)O[Ob](L)L[Li]`

---

## Why Use CRS?

1. **Model Comparison**: Instantly check if two configurations are equivalent
2. **Version Control**: Track model structure changes as strings
3. **Database Keys**: Use CRS as unique identifier for model configurations
4. **Communication**: Share model topology as a single string
5. **Validation**: Ensure models follow constraints (single parent, no cycles, etc.)
6. **Compression**: Encode complex graphs efficiently

---

## Realm Codes

Your 8 realms have standardized 2-character codes:

```
A   atmosphere
O   ocean
L   land-surface
Ac  atmospheric-chemistry
Ae  aerosol
Li  land-ice
Ob  ocean-biogeochemistry
Si  sea-ice
```

These are always in **alphabetical order**: A, Ac, Ae, Li, L, O, Ob, Si

---

## CRS Construction Rules

### Rule 1: Embeddings Use `[child]` Notation

**One realm can be embedded in another** - always linear chains, never branching.

- `A[Ac]` means Ac is embedded in A
- `A[Ac[Ae]]` means Ae embedded in Ac, Ac embedded in A
- Forms a hierarchy: Ae ← Ac ← A

**Chain Example:**
```
Aerosol embedded in Atmospheric-chemistry
Atmospheric-chemistry embedded in Atmosphere
```

Represents as: `A[Ac[Ae]]`

### Rule 2: Couplings Use `(realm1,realm2,...)` Notation

**Realms can couple with each other** - bidirectional relationships.

- `A(O,L)` means A coupled with both O and L
- Lists are comma-separated
- Order: Always alphabetical within parentheses

**Coupling Example:**
```
Atmosphere coupled with Ocean
Atmosphere coupled with Land-surface
```

Represents as: `A(L,O)` (alphabetical order)

### Rule 3: Forward-Only Listing

**Each realm lists couplings only to realms that come AFTER it alphabetically.**

This eliminates duplication:

```
✓ Correct:    A(B,C,D)B(C)
✗ Redundant:  A(B,C,D)B(C)C()D()
```

Why? A-C is already listed under A, so C doesn't need to re-list it.

For complete graph K₄ (all 6 pairs):
```
A(B,C,D)B(C,D)C(D)
```

Expands to: A-B, A-C, A-D, B-C, B-D, C-D ✓

### Rule 4: Nested Parentheses for Dense Couplings

Use nesting to show transitive couplings:

```
A(B(C(D)))
```

Means:
- A coupled with B
- B coupled with C (nested)
- C coupled with D (nested)

**Expands to all K₅ pairs:**
- A-B, A-C, A-D (A to everyone)
- B-C, B-D (B to downstream)
- C-D (C to downstream)

Result: 10 pairs from just 13 characters!

### Rule 5: Constraints

1. **Single Parent**: Each realm has at most ONE parent (one embedding relationship)
2. **No Cycles**: Embedding forms a forest (tree structure with multiple roots)
3. **No Cross-Coupling**: Embedded realms cannot couple (e.g., if Ae→Ac, then Ae cannot couple with anything)
4. **Bidirectional**: If A~B, then B~A (both listed in forward-only form)

---

## CRS Syntax

### Full Format

```
REALM[embedded_chain](coupled_realms)...other_realms...
```

### Simple Examples

```
A[Ac]                 → Ac embedded in A
A[Ac[Ae]]             → Hierarchy: Ae in Ac in A
A(O)                  → A coupled with O
A(O,L)                → A coupled with O and L
A[Ac](O,L)            → Ac in A; A couples O,L
A(B(C(D)))            → Complete K₄ graph
```

### Complex Example

```
A[Ac[Ae]](O,L)O[Ob](L)L[Li]Si
```

**Breakdown:**
- `A[Ac[Ae]]` - A contains Ac which contains Ae
- `(O,L)` - A couples with O and L
- `O[Ob]` - O contains Ob
- `(L)` - O couples with L (O-L pair)
- `L[Li]` - L contains Li
- `Si` - Sea-ice standalone (no embeddings, no couplings)

---

## How to Construct a CRS String

### Step 1: List Embeddings

Identify parent-child relationships:
```
Ae → Ac → A
Li → A
Ob → O
Si → O
```

### Step 2: List Couplings

Identify bidirectional relationships:
```
A ↔ O
A ↔ L
O ↔ L
```

### Step 3: Identify Roots

Realms not embedded in anything: **A, L, O, Si**

### Step 4: Build Embedding Chains

For each root, follow the chain:
- A: has child Ac, which has child Ae → `A[Ac[Ae]]`
- L: has child Li → `L[Li]`
- O: has child Ob → `O[Ob]`
- Si: no children → `Si`

### Step 5: Add Couplings (Forward-Only)

For each realm in alphabetical order, list couplings to realms AFTER it:
- A couples with L, O → `A(L,O)`
- L couples with O → `L(O)`
- O, Si: nothing after them → no couplings

### Step 6: Assemble

```
A[Ac[Ae]](L,O)L[Li](O)O[Ob]Si
```

---

## Canonical Ordering

Realms are **always processed in alphabetical order**: A, Ac, Ae, Li, L, O, Ob, Si

This ensures:
- ✓ Deterministic output
- ✓ Easy comparison (string equality = same structure)
- ✓ Consistent representation

**Two different constructions of the same system:**

Construction 1:
```
[Ae in Ac, Ac in A, Li in A, Ob in O]
[A-O, A-L, O-L]
```

Construction 2:
```
[Li in A, Ob in O, Ae in Ac, Ac in A]
[O-A, L-A, L-O]
```

**Both produce identical CRS:** `A[Ac[Ae]](L,O)L(O)O[Ob]Si`

---

## Realm Codes Table

| Code | Realm | Notes |
|------|-------|-------|
| A | atmosphere | Single char (most fundamental) |
| O | ocean | Single char (most fundamental) |
| L | land-surface | Single char (most fundamental) |
| Ac | atmospheric-chemistry | Embedded in A |
| Ae | aerosol | Can embed in Ac or A |
| Li | land-ice | Embedded in L |
| Ob | ocean-biogeochemistry | Embedded in O |
| Si | sea-ice | Embedded in O |

---

## Validation Rules

A valid CRS must satisfy:

1. **Single Parent**: No realm appears as a child more than once
   - ✓ `A[Ac[Ae]]` - each realm has one parent
   - ✗ `A[Ac]B[Ac]` - Ac has two parents

2. **No Cycles**: Embedding forms a forest
   - ✓ `A[Ac[Ae]]` - linear chain
   - ✗ `A[Ac[A]]` - creates cycle

3. **Embedded ≠ Coupled**: If X is embedded (anywhere), it cannot couple
   - ✓ `A[Ac](O,L)` - Ac is embedded, doesn't couple
   - ✗ `A[Ac](Ac,O)` - violates rule (Ac is embedded)

4. **Bidirectional**: Couplings listed forward-only but represent undirected edges
   - ✓ `A(B(C))` - A-B, B-C, A-C all exist
   - ✓ Both `A(B)B(C)` and `A(B(C))` valid representations of same graph

---

## Real-World Examples

### Example 1: Simple System

```
A[Ac](O)
```

- Atmospheric-chemistry embedded in Atmosphere
- Atmosphere coupled with Ocean

### Example 2: Complex Hierarchy

```
A[Ac[Ae],Li](O,L)O[Ob,Si](L)L
```

Wait - this violates single parent! Let me fix:

```
A[Ac[Ae]](O,L)O[Ob](L)L[Li]Si
```

- A contains Ac which contains Ae
- A couples with O and L
- O contains Ob and couples with L
- L contains Li
- Si standalone

### Example 3: Complete K₅ Graph

```
A(B(C(D(E))))
```

All 10 pairs: A-B, A-C, A-D, A-E, B-C, B-D, B-E, C-D, C-E, D-E

---

## Use Cases

### 1. Model Fingerprinting

```python
crs1 = generate(embeddings1, couplings1)
crs2 = generate(embeddings2, couplings2)

if crs1 == crs2:
    print("Models are identical!")
```

### 2. Configuration Versioning

```
v1.0: A[Ac](O,L)
v1.1: A[Ac[Ae]](O,L)    # Added aerosol
v2.0: A[Ac[Ae]](O,L,Li) # Added land-ice
```

### 3. Database Storage

Use CRS as unique key for model configuration table:

```
id | crs | version | description
---|-----|---------|------------
1  | A[Ac](O,L) | 1.0 | Basic atmosphere-ocean
2  | A[Ac[Ae]](O,L) | 1.1 | With aerosol
```

### 4. Validation Checklists

```
✓ Single parent per realm
✓ No cycles in embeddings
✓ Embedded realms not coupled
✓ Couplings bidirectional
✓ Alphabetical ordering
```

---

## Summary

| Concept | Notation | Example |
|---------|----------|---------|
| Embedding chain | `[child]` | `A[Ac[Ae]]` |
| Coupling list | `(realm1,realm2)` | `A(O,L)` |
| Both | Combined | `A[Ac](O,L)` |
| Dense coupling | Nested parens | `A(B(C(D)))` |
| Full system | Multiple roots | `A[Ac](O)O[Ob]L[Li]` |

**CRS is:** Minimal, Deterministic, Reversible, Hierarchical, Order-Independent

Done.
