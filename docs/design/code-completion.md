# Code Completion

**Status:** Draft

Native CLI code completion that behaves like an IDE autocomplete but works from the terminal:
`lm -n "<prefix>" --autocomplete` for one-shot mode, or `lm --repl --autocomplete` for interactive.
The system must force the model to return only code when autocomplete is selected, and let users
set a default autocomplete model via `lmConfig`.

---

## Prompt and role enforcement

Define an **autocomplete role** in config — a system instruction that explicitly constrains
the model to output only code and no explanations.

**Example system instruction (stored in config roles):**

```
You are a code autocomplete engine.
Only output valid code tokens that continue the given prefix.
Do not include explanations, commentary, or markdown.
If you cannot produce code, output an empty string.
```

When `--autocomplete` is used, LemonPie selects this role automatically and sends it as the
system message.

---

## Model selection and config

Add a `default_autocomplete_model` field to `config.json`.

**lmConfig commands:**
- `lmConfig --set-default-autocomplete <model>` — set the default autocomplete model.
- `lmConfig --add-model` and the existing state machine verify the model is available on the server.

**Behaviour:** If `--model` is passed on the CLI it overrides the default; otherwise
`default_autocomplete_model` is used.

**Config snippet:**

```json
{
  "default_autocomplete_model": "smollm:360m",
  "roles": {
    "autocomplete": {
      "system": "You are a code autocomplete engine. Only output valid code tokens..."
    }
  }
}
```

---

## CLI UX

**One-shot completion:**

```bash
lm -n "def build_client(server_host, timeout):\n    return " --autocomplete
```

Output: code continuation only.

**REPL mode:**

```bash
lm --repl --autocomplete
```

Press Enter to request completion for the current line or selection.

**Flags:**

| Flag | Description |
|---|---|
| `--autocomplete` | Select autocomplete role and enable output filtering |
| `--model <name>` | Override default autocomplete model for this invocation |
| `--stream` | Token streaming for low-latency incremental display |

---

## Output filtering and validation

- **Primary enforcement** — the system role constrains the model to code-only output.
- **Secondary enforcement** — post-process the model output:
  - Syntactic sanity checks (output starts with `def`, `class`, `{`, `[`, or valid indentation).
  - Strip leading natural language; if output begins with non-code tokens, discard or retry.
  - Retry policy: up to N retries with a stricter system prompt or adjusted temperature.
- **Fail-safe** — if the model repeatedly returns non-code, return an empty completion and a
  machine-readable error code (not a human explanation) so callers can handle it gracefully.

---

## Streaming, latency, and model sizing

| Model class | Latency | Accuracy | Use case |
|---|---|---|---|
| Small (≤500M) | Low | Medium | Interactive REPL, quick suggestions |
| Medium (500M–3B) | Medium | Good | Most users, balanced |
| Large (>3B) | High | High | Offline batch, complex code |

**Suggested defaults:**
- Small model for interactive mode (e.g. `smollm:360m`).
- Allow users to configure a larger model for batch completions.

---

## State machine and retries

Reuses the state-machine approach from [model-verification.md](model-verification.md).
Adds a small state machine for completion requests:

```text
Send completion request
         │
         ▼
   model reachable?
    /           \
  NO            YES
   │              │
fallback /      receive output
  error            │
                   ▼
            passes code filter?
             /           \
           YES             NO
            │               │
          return        retry (stricter prompt)
                              │
                         still failing?
                          /        \
                        YES         NO
                         │           │
                  return empty     return output
                  completion +
                  error code
```

Retry limits and backoff to be documented during implementation.

---

## Testing and rollout

**Unit tests:**
- Role selection when `--autocomplete` is active.
- Output filtering heuristics.
- `lmConfig --set-default-autocomplete` and model verification.

**Integration tests:**
- Simulate streaming completions.
- Measure latency and retry behaviour under load.

**Rollout:** Ship behind `--experimental-autocomplete` initially to gather feedback,
then promote once stable.
