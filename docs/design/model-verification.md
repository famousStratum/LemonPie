# Model Verification

**Status:** Ready

This document outlines the state machine for `lmConfig --add-model`.
It defines how LemonPie handles server reachability, model installation, and user choices when adding models.

---

## Goals

- Ensure models are verified against the server before being added.
- Provide clear user feedback for success/failure cases.
- Support `--force` as a broad override mechanism.
- Keep logic predictable and extensible.

---

## State machine

```text
lmConfig --add-model sm smollm:360m
             │
             ▼
       Can contact server?
        /              \
      NO                YES
      │                  │
      │             model installed?
      │              /          \
      │            YES           NO
      │             │             │
      │             ▼             ▼
      │            ADD         offer pull
      │                           │
      │                      ┌────┴────┐
      │                      │         │
      │                     YES        NO
      │                      │          │
      │                    pull       abort
      │                      │
      │                 success?
      │                 /      \
      │               YES       NO
      │                │         │
      │               ADD      abort
      │
      ▼
   abort
   "use --force to add without verification"
```

---

## --force override

`--force` is a broad override that bypasses verification steps:

- Skip server reachability check.
- Skip model installation check.
- Overwrite existing alias conflicts without prompting.

Use `--force` when the server is temporarily unreachable, the model is known to be installed,
or an alias conflict needs to be resolved non-interactively.
