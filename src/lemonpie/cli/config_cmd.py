#!/usr/bin/env python3
"""
config_cmd.py (alias: lmConfig) — CLI for managing LemonPie configuration.

Usage examples:
  lmConfig --init                                  # Interactive setup wizard
  lmConfig --host http://127.0.0.1:11434           # Set server URL
  lmConfig --add-model qwen qwen2.5-coder:3b       # Map an alias to a model
  lmConfig --add-model qwen qwen2.5:1.5b --force   # Reassign an existing alias
  lmConfig --default-model qwen                    # Set default by alias or name
  lmConfig --remove-model qwen                     # Clear alias or remove model
  lmConfig --list-models                           # View configured models
  lmConfig --api-key                               # Set the API key (hidden prompt)
  lmConfig --remove-api-key                        # Remove the stored API key
"""

import argparse
import getpass
import json
import os
import sys

import httpx2

from lemonpie.cli.ui import confirm
from lemonpie.client import build_client, resolve_error
from lemonpie.config import (
    config_file_path,
    ensure_models_list,
    is_valid_url,
    load_config,
    resolve_api_key,
    save_config,
)
from lemonpie.models import (
    find_by_alias,
    find_by_name,
)

# ---------------------------------------------------------------------------
# lmConfig --init helpers
# ---------------------------------------------------------------------------

KNOWN_BACKENDS = [
    {"name": "llamacpp", "label": "llama.cpp", "port": 9931},
    {"name": "ollama", "label": "Ollama", "port": 11434},
    {"name": "lmstudio", "label": "LM Studio", "port": 1234},
    {"name": None, "label": "Other", "port": None},
]


def _prompt_backend():
    """Ask which backend the user is using.

    Returns (backend_name, default_port). Both are None for 'Other'.
    """
    print("Which backend are you using?")
    for i, b in enumerate(KNOWN_BACKENDS, 1):
        print(f"  {i}. {b['label']}")

    while True:
        raw = input(f"  Enter number (1-{len(KNOWN_BACKENDS)}): ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(KNOWN_BACKENDS):
                b = KNOWN_BACKENDS[idx]
                return b["name"], b["port"]
        except ValueError:
            pass
        print(f"  Invalid choice, enter 1-{len(KNOWN_BACKENDS)}.")


def _prompt_custom_url(hint=None):
    """Prompt for a custom server URL with an optional example hint."""
    prompt = f"  Server URL ({hint}): " if hint else "  Server URL: "
    while True:
        raw = input(prompt).strip()
        if is_valid_url(raw):
            return raw
        print("  Invalid URL. Must start with http:// or https://.")


def _prompt_server(default_port):
    """Ask if the server is local or remote, return server URL."""
    is_local = confirm("Is your server running on this machine?")

    if is_local:
        if default_port:
            default_url = f"http://localhost:{default_port}"
            print(f"\n  1. Default  ({default_url})")
            print("  2. Custom")
            while True:
                raw = input("  Enter number (1-2): ").strip()
                if raw == "1":
                    return default_url
                if raw == "2":
                    return _prompt_custom_url()
                print("  Invalid choice, enter 1 or 2.")
        else:
            return _prompt_custom_url()
    else:
        hint = (
            f"e.g. http://192.168.1.1:{default_port}"
            if default_port
            else "e.g. http://192.168.1.1:<port>"
        )
        return _prompt_custom_url(hint=hint)


def _prompt_model_selection(available_models):
    """Show a numbered list of server-installed models; return selected entries.

    The user enters space-separated numbers (e.g. ``1 3``).  For each chosen
    model an optional alias is collected.  Pressing Enter without typing
    anything skips model registration entirely.
    """
    print("\n  Available models:")
    for i, name in enumerate(available_models, 1):
        print(f"    {i}. {name}")

    raw = input("\n  Select models to add (e.g. 1 3), Enter to skip: ").strip()
    if not raw:
        return []

    selected = []
    seen: set[str] = set()
    for token in raw.split():
        try:
            idx = int(token) - 1
        except ValueError:
            print(f"  Skipping invalid token: {token!r}")
            continue
        if not (0 <= idx < len(available_models)):
            print(f"  Out of range, skipping: {token!r}")
            continue
        name = available_models[idx]
        if name in seen:
            continue
        seen.add(name)
        alias_raw = input(f"  Alias for {name!r} (optional, Enter to skip): ").strip()
        selected.append({"alias": alias_raw or None, "name": name})

    return selected


def _prompt_model_manual():
    """Collect one or more model entries by hand (name + optional alias)."""
    models = []
    while True:
        while True:
            name = input("  Model name (e.g. qwen2.5-coder:3b): ").strip()
            if name:
                break
            print("  Model name cannot be empty.")
        alias_raw = input("  Alias (optional, Enter to skip): ").strip()
        models.append({"alias": alias_raw or None, "name": name})
        if not confirm("  Add another model?"):
            break
    return models


def _prompt_default(models):
    """Ask which of the configured models should be the default.

    Returns the chosen model name, or None if the user declines / there are
    no models to choose from.
    """
    if not models:
        return None

    if len(models) == 1:
        if confirm(f'  Set "{models[0]["name"]}" as the default model?'):
            return models[0]["name"]
        return None

    # Multiple models — let the user pick by number.
    if not confirm("  Set a default model?"):
        return None

    for i, m in enumerate(models, 1):
        alias_disp = m.get("alias") or "<no alias>"
        print(f"    {i}. {alias_disp} -> {m['name']}")

    while True:
        raw = input(f"  Enter number (1-{len(models)}): ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(models):
                return models[idx]["name"]
        except ValueError:
            pass
        print(f"  Invalid choice, enter 1-{len(models)}.")


# ---------------------------------------------------------------------------
# Server discovery
# ---------------------------------------------------------------------------


def _fetch_with_key(server, api_key=None):
    """GET /v1/models with an optional API key.

    Returns (models, err, auth_err) where ``err`` is a human-readable
    error message (or ``None`` on success) and ``auth_err`` is ``True``
    when the server returned 401/403 — letting the caller prompt for an
    API key without relying on string parsing.
    """
    try:
        with build_client(server, timeout=5.0, api_key=api_key) as client:
            resp = client.get("/v1/models")
            resp.raise_for_status()
            data = resp.json()
        return [m["id"] for m in data.get("data", [])], None, False
    except httpx2.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (401, 403):
            return [], "Server requires authentication", True
        return [], f"Server returned HTTP {status}", False
    except (httpx2.HTTPError, httpx2.InvalidURL) as exc:
        # Connection, timeout, DNS, TLS and protocol failures. HTTPStatusError
        # is handled above because it is a subclass of HTTPError.
        message, _hint = resolve_error(exc, server)
        return [], message, False
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        # Bad JSON (JSONDecodeError is a ValueError) or an unexpected shape.
        return [], f"Invalid response format from server ({exc!r})", False


def _print_probe_result(models, err):
    """Finish the 'Connecting ...' status line that the caller started."""
    if err:
        print(f" failed.\n  {err}")
        return
    count = len(models)
    label = f"{count} model(s) available" if count else "no models installed"
    print(f" OK ({label})")


# ---------------------------------------------------------------------------
# lmConfig --init
# ---------------------------------------------------------------------------


def cmd_init(force=False):
    """Interactive wizard: create or reset config.json from scratch.

    Steps
    -----
    1. Warn if a config already exists; ask for confirmation to overwrite.
    2. Prompt for backend selection.
    3. Prompt for server URL — local (default or custom) or remote.
    4. Unless ``--force``, verify server reachability via ``GET /v1/models``.
       - If reachable: present the installed-model list for selection.
       - If the server answers 401/403: prompt for an API key and retry
         (a key from LEMONPIE_API_KEY is tried first and never saved).
       - If unreachable or the key is rejected: offer to continue without
         verification.
    5. If no server models are available, offer manual model entry.
    6. Optionally set a default model.
    7. Save and print a summary.

    ``--force`` skips step 4 entirely (useful when the server is offline
    during setup).
    """
    path = config_file_path()
    if os.path.exists(path):
        print(f"Config already exists: {path}")
        if not confirm("Reinitialize from scratch?"):
            print("Aborted.")
            return 1

    print("\nLemonPie setup\n")

    # ------------------------------------------------------------------
    # Step 1: Backend
    # ------------------------------------------------------------------
    backend, default_port = _prompt_backend()

    # ------------------------------------------------------------------
    # Step 2: Server URL
    # ------------------------------------------------------------------
    print()
    server = _prompt_server(default_port)

    # ------------------------------------------------------------------
    # Step 3: Verify server & discover models
    # ------------------------------------------------------------------
    available_models: list[str] = []
    server_ok = False
    api_key: str | None = None

    if force:
        print(
            "  Skipping server verification (--force).\n"
            "  Use `lmConfig --api-key` later if your server needs a key."
        )
    else:
        # A key from LEMONPIE_API_KEY is used for the probe only; it is never
        # written to the config file.
        print(f"  Connecting to {server} ...", end="", flush=True)
        available_models, err, auth_err = _fetch_with_key(server, resolve_api_key({}))
        if auth_err:
            print(" authentication required.")
            raw_key = getpass.getpass(
                "  Enter API key (or press Enter to skip): "
            ).strip()
            if raw_key:
                print("  Retrying with API key ...", end="", flush=True)
                available_models, err, auth_err = _fetch_with_key(server, raw_key)
                if auth_err:
                    err = "Server rejected the API key"
                if not err:
                    api_key = raw_key
                _print_probe_result(available_models, err)
            # Key skipped: err is still set, so the prompt below applies.
        else:
            _print_probe_result(available_models, err)

        if err:
            if not confirm("  Continue without verification?"):
                print("Aborted.")
                return 1
        else:
            server_ok = True

    # ------------------------------------------------------------------
    # Step 4: Select / add models
    # ------------------------------------------------------------------
    models: list[dict] = []

    if available_models:
        models = _prompt_model_selection(available_models)
    else:
        if server_ok:
            print("  No models are installed on this server.")
        if confirm("  Add a model manually?"):
            models = _prompt_model_manual()

    # ------------------------------------------------------------------
    # Step 5: Default model
    # ------------------------------------------------------------------
    default = _prompt_default(models)

    # ------------------------------------------------------------------
    # Step 6: Save & summarise
    # ------------------------------------------------------------------
    cfg = {
        "backend": backend,
        "server": server,
        "api_key": api_key,
        "default": default,
        "models": models,
    }
    save_config(cfg)

    print("\nConfig saved.")
    print(f"  Backend: {backend or 'other'}")
    print(f"  Server : {server}")
    print(f"  Default: {default or '<none>'}")
    if models:
        for m in models:
            mark = "*" if m.get("name") == default else " "
            alias_disp = m.get("alias") or "<no alias>"
            print(f"  {mark} {alias_disp} -> {m['name']}")
    else:
        print("  No models configured yet.")
        print("  Use `lmConfig --add-model <alias> <name>` to add models later.")

    return 0


# ---------------------------------------------------------------------------
# Existing lmConfig sub-commands
# ---------------------------------------------------------------------------


def cmd_set_host(cfg, host):
    if not is_valid_url(host):
        print(f"Invalid URL: {host}")
        return 2
    cfg["server"] = host
    save_config(cfg)
    print(f"Host set to {host}")
    return 0


def cmd_set_default(cfg, identifier):
    """
    Set default by alias or full model name. Default stores the model 'name'.
    """
    ensure_models_list(cfg)

    # Try alias first
    _, m = find_by_alias(cfg, identifier)
    if m:
        cfg["default"] = m["name"]
        save_config(cfg)
        print(f"Default model set to {m['name']} (alias: {identifier})")
        return 0

    # Try full model name
    _, m = find_by_name(cfg, identifier)
    if m:
        cfg["default"] = m["name"]
        save_config(cfg)
        print(f"Default model set to {m['name']}")
        return 0

    print(
        f'Model "{identifier}" not found.'
        f" Use --list-models to see configured models."
        f" Use --add-model to add a new model mapping."
    )
    return 2


def cmd_add_model(cfg, alias, model_name, force=False):
    """
    Add or update a model object: { "alias": <nullable>, "name": <model_name> }.
    - Check model_name first, then alias.
    - With --force: reassign alias to model_name and set previous alias to None.
    - If models list is empty before adding, set the added model as the default.
    """
    ensure_models_list(cfg)
    models = cfg["models"]

    # Remember whether models list was empty before changes (for default assignment)
    was_empty = len(models) == 0

    # Find existing entries
    _idx_name, entry_by_name = find_by_name(cfg, model_name)
    _idx_alias, entry_by_alias = find_by_alias(cfg, alias)

    # Exact mapping exists -> no-op
    if entry_by_alias and entry_by_name and entry_by_alias is entry_by_name:
        print(f'Alias "{alias}" already maps to "{model_name}". No changes made.')
        return 0

    # If model_name exists under a different alias
    if (
        entry_by_name
        and entry_by_name.get("alias")
        and entry_by_name.get("alias") != alias
    ):
        existing_alias = entry_by_name["alias"]
        if not force:
            print(
                f'Model "{model_name}" is already mapped to alias "{existing_alias}". Use --force to reassign.'
            )
            return 2
        # force: clear the old alias (set to None) but keep the model record
        print(
            f'Removing alias "{existing_alias}" from model "{model_name}". It will remain accessible by full name.'
        )
        entry_by_name["alias"] = None

    # If alias exists and maps to a different model
    if entry_by_alias and entry_by_alias.get("name") != model_name:
        existing_model = entry_by_alias["name"]
        if not force:
            print(
                f'Alias "{alias}" is already in use for model "{existing_model}". Please use a different alias or remove the existing mapping.'
            )
            return 2
        # force: clear the alias on the existing model object (set to None),
        # but keep the model object (do not delete it).
        print(f'Clearing alias "{alias}" from model "{existing_model}" to reassign it.')
        entry_by_alias["alias"] = None

    # At this point:
    # - if entry_by_name exists, it may have alias None (cleared above) or already equal to alias
    # - if entry_by_alias existed and was for a different model, its alias is now None
    # Assign alias to existing model object if present
    if entry_by_name:
        entry_by_name["alias"] = alias
        save_config(cfg)
        print(f'Assigned alias "{alias}" to existing model "{model_name}".')
        # If models list was empty before, set default to this model name
        if was_empty:
            cfg["default"] = model_name
            save_config(cfg)
            print(f'Set default model to "{model_name}" (first configured model).')
        return 0

    # Otherwise, alias is free and model_name is new -> create new object
    models.append({"alias": alias, "name": model_name})
    save_config(cfg)
    print(f"Added model mapping: {alias} -> {model_name}")

    # If this was the first model added, make it the default
    if was_empty:
        cfg["default"] = model_name
        save_config(cfg)
        print(f'Set default model to "{model_name}" (first configured model).')

    return 0


def cmd_remove_model(cfg, identifier):
    """
    Remove mapping by alias or by full model name.
    - If identifier matches an alias: clear the alias (set to None).
    - If identifier matches a model name: confirm and remove the model object entirely.
    """
    ensure_models_list(cfg)

    _idx_alias, entry_alias = find_by_alias(cfg, identifier)
    if entry_alias:
        # Clear alias only
        if not confirm(
            f'Clear alias "{identifier}" from model "{entry_alias["name"]}"? (model will remain accessible by full name)'
        ):
            print("Aborted.")
            return 1
        entry_alias["alias"] = None
        save_config(cfg)
        print(f'Cleared alias "{identifier}" from model "{entry_alias["name"]}".')
        return 0

    idx_name, entry_name = find_by_name(cfg, identifier)
    if entry_name:
        # Remove entire model object
        if not confirm(
            f'Remove model "{identifier}" entirely from config? This will delete the record.'
        ):
            print("Aborted.")
            return 1
        del cfg["models"][idx_name]
        # If default pointed to this model name, clear it
        if cfg.get("default") == identifier:
            cfg["default"] = None
            print("Removed default model because it referenced the deleted model.")
        save_config(cfg)
        print(f'Removed model "{identifier}".')
        return 0

    print(f'No model or alias matching "{identifier}" found.')
    return 2


def cmd_list_models(cfg):
    ensure_models_list(cfg)
    models = cfg.get("models", [])
    if not models:
        print("No models configured.")
        return 0
    default_name = cfg.get("default")
    print("Configured models:")
    for m in sorted(models, key=lambda x: (x.get("alias") or "", x.get("name"))):
        alias = m.get("alias") if m.get("alias") is not None else "<none>"
        mark = "*" if m.get("name") == default_name else " "
        print(f"{mark} {alias} -> {m.get('name')}")
    return 0


# Sentinel: ``--api-key`` was given without a value, so ask for it without echo.
_PROMPT_FOR_KEY = object()


def _warn_if_env_key():
    if os.environ.get("LEMONPIE_API_KEY"):
        print(
            "Note: LEMONPIE_API_KEY is set and takes precedence over the "
            "config value at runtime."
        )


def cmd_set_api_key(cfg, api_key):
    """Set or update the API key in the config.

    Pass ``_PROMPT_FOR_KEY`` to read the key from a hidden prompt, which keeps
    it out of shell history and the process list.
    """
    if api_key is _PROMPT_FOR_KEY:
        api_key = getpass.getpass("Enter API key: ")
    api_key = api_key.strip()
    if not api_key:
        print("No API key provided.")
        return 2
    cfg["api_key"] = api_key
    save_config(cfg)
    print("API key set.")
    _warn_if_env_key()
    return 0


def cmd_clear_api_key(cfg):
    """Remove the API key from the config."""
    cfg["api_key"] = None
    save_config(cfg)
    print("API key removed.")
    _warn_if_env_key()
    return 0


def cmd_show(cfg):
    shown = dict(cfg)
    key = shown.get("api_key")
    if key:
        shown["api_key"] = f"****{key[-4:]}" if len(key) >= 12 else "****"
    print(json.dumps(shown, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Parser & entry-point
# ---------------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        prog="lmConfig",
        description="Manage LemonPie configuration (config.json)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Interactive setup wizard: create or reinitialize config.json",
    )
    parser.add_argument("--host", help="Set server host URL (http(s)://host:port)")
    parser.add_argument(
        "--default-model",
        help="Set default model using alias or full name (must exist in models)",
    )
    parser.add_argument(
        "--add-model",
        nargs=2,
        metavar=("ALIAS", "MODEL"),
        help="Add model mapping: alias model_full_name",
    )
    parser.add_argument(
        "--remove-model",
        metavar="IDENTIFIER",
        help="Remove a model mapping by alias or full name",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List configured model aliases and names",
    )
    parser.add_argument(
        "--api-key",
        nargs="?",
        const=_PROMPT_FOR_KEY,
        metavar="KEY",
        help="Set or update the API key (omit KEY to be prompted without echo)",
    )
    parser.add_argument(
        "--remove-api-key",
        action="store_true",
        help="Remove the API key from config",
    )
    parser.add_argument("--show", action="store_true", help="Print full config.json")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite when adding a model; skip server verification with --init",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --init is handled before load_config() so it can decide for itself
    # whether the file already exists without triggering auto-creation.
    if args.init:
        return cmd_init(force=args.force)

    cfg = load_config()

    # Dispatch
    if args.host:
        return cmd_set_host(cfg, args.host)

    if args.default_model:
        return cmd_set_default(cfg, args.default_model)

    if args.add_model:
        alias, model_name = args.add_model
        return cmd_add_model(cfg, alias, model_name, force=args.force)

    if args.remove_model:
        return cmd_remove_model(cfg, args.remove_model)

    if args.api_key is not None:
        return cmd_set_api_key(cfg, args.api_key)

    if args.remove_api_key:
        return cmd_clear_api_key(cfg)

    if args.list_models:
        return cmd_list_models(cfg)

    if args.show:
        return cmd_show(cfg)

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
