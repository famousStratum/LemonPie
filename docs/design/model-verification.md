# Model Verification

**Status:** Ready

This document outlines the planned state machine for `lmConfig --add-model`.  
It defines how LemonPie should handle server reachability, model installation, and user choices when adding models.

---

## 🎯 Goals
- Ensure models are verified against the Ollama server before being added.
- Provide clear user feedback for success/failure cases.
- Support `--force` as a broad override mechanism (alias conflicts, skipping verification).
- Keep logic predictable and extensible for future improvements.

---

## 🔄 State Machine Flow

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
