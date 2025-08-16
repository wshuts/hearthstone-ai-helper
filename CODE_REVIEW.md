# Clean Code Review – Multiplicity Slice (Step-by-Step)

> Scope: **Multiplicity** only (resolver, deck-code path, and their tests). No behavior changes; refactor for clarity and testability.

---

## 0) Prep
- [ ] Tag current state (e.g., `multiplicity-pre-refactor`).
- [ ] Ensure all tests are green (baseline).

---

## 1) Characterize Current Behavior (Tests First)
- [ ] Add/finish **characterization tests** that pin today’s behavior:
  - [ ] With/without `deckCode`
  - [ ] Empty/invalid `deckCode` paths
  - [ ] Union/dedupe scenarios (as relevant)
- [ ] Prefer **AAA style** (Arrange–Act–Assert).
- [ ] Use **parametrization** for input→output tables.
- [ ] Assert **observables** (return values / emitted lines), not internals.

---

## 2) Introduce Minimal DI Seams (No Behavior Change)
- [ ] **Multiplicity strategy seam**
  - [ ] Function accepts `multiplicity_resolver` with default `_no_augmentation`.
  - [ ] Resolver is **pure**: `(items, deck_code) -> Dict[str,int]`.
  - [ ] Name is intention-revealing (`_no_augmentation`, not “default”).
- [ ] **Deck code decode seam**
  - [ ] Accept `decode_deck: (str) -> Dict[int,int]` (dbfId→count).
  - [ ] Provide a real default that uses the library; tests inject fakes.
- [ ] **I/O boundaries** are explicit: parsing/loading/writing are at edges; core funcs are pure.

---

## 3) Refactor for Clarity (Small, Intentional Steps)
- [ ] **Naming communicates intent** (replace comments with good names).
- [ ] **Tiny functions**, single responsibility, early exits over deep nesting.
- [ ] **No hidden globals**; pass collaborators (DI) explicitly.
- [ ] Consolidate duplicate logic; keep CLI orchestration thin.
- [ ] Keep error messages **actionable** (e.g., “install `hearthstone` …”).

---

## 4) Test Hygiene Pass
- [ ] Test names follow `test_<behavior>_<condition>_<expected>()`.
- [ ] Shared builders/fixtures are **obvious** and minimal.
- [ ] Fakes replace heavy deps:
  - [ ] `decode_deck` fake avoids real library in most tests.
  - [ ] `multiplicity_resolver` fakes cover spike behaviors.
- [ ] Avoid time/fs randomness unless explicitly faked.

---

## 5) Style & Quality Gates
- [ ] Format with **black**; lint with **ruff/flake8** (no functional edits).
- [ ] Keep public surface area stable; DI is **optional** via defaults.
- [ ] Diff reads clearly: small, behavior-preserving commits.

---

## 6) Exit Criteria (“Done” for this Review)
- [ ] Characterization tests pass before & after refactor.
- [ ] Spike behavior is covered by tests (via injected resolver).
- [ ] Resolver is pure/injected; deck decode seam injected.
- [ ] Core logic is self-documenting (very few comments needed).
- [ ] Commit history is a tutorial of intent, not a monolith.

---

## Quick Reference – Minimal Shapes

```py
from typing import Protocol, Dict, List, Callable

class MultiplicityResolver(Protocol):
    def __call__(self, items: List[dict], deck_code: str) -> Dict[str, int]: ...

DecodeDeck = Callable[[str], Dict[int, int]]  # dbfId -> count
```

```py
def resolve_multiplicity(
    items: List[dict],
    deck_code: str | None,
    resolver: MultiplicityResolver = _no_augmentation,
) -> Dict[str, int]:
    return {} if not deck_code else resolver(items, deck_code)
```

---

## Anti-Patterns to Catch (and Remove)
- [ ] Hidden state or surprise imports inside core logic.
- [ ] Commented-out code; comments that explain *what* instead of *why*.
- [ ] Tests that rely on real filesystem or external libs unnecessarily.
- [ ] Over-parameterized functions with unclear names.

---

## Commit Discipline (suggested)
1. Add characterization tests (red/green on baseline).
2. Introduce DI seams with defaults (no behavior change).
3. Pure refactors: naming, extraction, early returns.
4. Test hygiene & parametrization.
5. Style pass (formatter/linter), no logic changes.

> Goal: New readers can understand the module without opening tests or comments; tests read like a truth table of behavior.

