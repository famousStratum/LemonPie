**Status:** Draft

### Implementation plan (high level)

#### Goal
**Native CLI code completion** that behaves like an IDE autocomplete but works from the LemonPie CLI:  
`lm -n "<prefix>" --autocomplete` or an interactive REPL mode.  
The system must be able to **force the model to return only code** when autocomplete is selected and let users set a default autocomplete model via `lmConfig`.

---

#### Prompt and role enforcement
- **Define an autocomplete role** in config (system instruction) that explicitly instructs the model to output only code and no explanations.

**Example system instruction (store in config roles):**
```    
You are a code autocomplete engine.
Only output valid code tokens that continue the given prefix.
Do not include explanations, commentary, or markdown.
If you cannot produce code, output an empty string.
```


- When `--autocomplete` is used, LemonPie selects this role automatically and sends it as the system message so the model is constrained.

---

#### Model selection and config
- **Add a `default_autocomplete_model`** field to `config.json` or `config.yaml`.

**lmConfig commands:**
- `lmConfig --set-default-autocomplete <model>` to set the default.
- `lmConfig --add-model` and the existing state machine should verify the model is available on the Ollama server.

**Behavior:** If `--model` is passed on the CLI it overrides the default; otherwise use `default_autocomplete_model`.

**Example config snippet**
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

#### CLI UX and examples
- **One-shot completion**

    lm -n "def build_client(server_host, timeout):\n    return " --autocomplete

  Output: code continuation only.

- **REPL mode**

    lm --repl --autocomplete

  Press Enter to request completion for the current line or selection.

- **Flags**
  - `--autocomplete` selects role and output filtering.
  - `--model <name>` overrides default autocomplete model.
  - `--stream` enables token streaming for low-latency incremental display.

#### Output filtering and validation
- **Primary enforcement**: rely on the system role to make the model return code-only.
- **Secondary enforcement**: post-process model output:
  - **Syntactic sanity checks**: quick heuristics (starts with `def`, `class`, `{`, `[` or valid indentation for Python).
  - **Strip leading natural language**: if output begins with non-code tokens, discard or retry.
  - **Retry policy**: up to N retries with a stricter system prompt or different temperature.
- **Fail-safe**: if model repeatedly returns non-code, return an empty completion and a short machine-readable error code (not a human explanation) so callers can handle it.

#### Streaming, latency, and model sizing
- **Tradeoffs**:
  - **Small models**: low latency, good for interactive typing; may be less accurate.
  - **Large models**: better completions, higher latency.

- **Suggested defaults**:
  - Use a small/medium autocomplete model for interactive mode (e.g., `smollm:360m`).
  - Allow power users to set a larger model for batch completions.

**Table of tradeoffs**

| **Model Class** | **Latency** | **Accuracy** | **Use Case** |
|-----------------|-------------|--------------|--------------|
| Small (<=500M)  | Low         | Medium       | Interactive REPL, quick suggestions |
| Medium (500M–3B)| Medium      | Good         | Most users, balanced |
| Large (>3B)     | High        | High         | Offline batch completions, complex code |

#### State machine and retries
- Reuse the state-machine style from [model-verification.md](docs/design/model-verification.md) and add a small state machine for completion requests:
  - **Start** → model reachable? → yes: send request; no: fallback to local cache or error.
  - **Receive output** → passes code filter? → yes: return; no: retry with stricter prompt or different model → if still fail, return empty completion with error code.
- Document retry limits and backoff in `code-completion.md`.

#### Testing and rollout
- **Unit tests** for:
  - Role selection when `--autocomplete` is used.
  - Output filtering heuristics.
  - `lmConfig` default model setting and verification.

- **Integration tests**:
  - Simulate streaming completions.
  - Measure latency and retry behavior.

- **Beta flag**: ship behind `--experimental-autocomplete` initially to gather feedback.
