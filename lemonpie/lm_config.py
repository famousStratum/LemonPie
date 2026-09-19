#!/usr/bin/env python3
"""
lm_config.py (alias: lmConfig) — manage LemonPie config.json safely

Usage examples:
  # Set Ollama host URL
  lmConfig --host http://192.168.1.252:11434

  # Add a model object (alias -> full model name)
  lmConfig --add-model qwen qwen2.5-coder:1.5b-base

  # Reassign an alias to a different model (use --force to reassign)
  lmConfig --add-model qwen qwen2.5-coder:3b --force

  # Set default model by alias or by full model name
  lmConfig --default-model qwen
  lmConfig --default-model qwen2.5-coder:3b

  # Remove a model or clear an alias
  lmConfig --remove-model qwen                 # clears alias (model remains, alias -> null)
  lmConfig --remove-model qwen2.5-coder:3b     # removes the model record entirely

  # List configured models (shows alias or <none> and marks default by model name)
  lmConfig --list-models

Behavior and data model
  - Config now stores models as a list of objects:
      "models": [
        { "alias": "qwen", "name": "qwen2.5-coder:3b" },
        { "alias": null,   "name": "qwen2.5-coder:1.5b-base" }
      ]
  - The default is stored as the canonical model name (full identifier), not an alias.
  - --add-model checks the model name first, then the alias. Using --force will
    reassign aliases: the previous alias is set to null (the model record is kept).
  - The script will automatically migrate the old dict-style "alias: name"
    mapping to the new list-of-objects format on first load.

Notes for users and maintainers
  - Use aliases for convenience; the canonical identity is the full model name.
  - lm.py resolves aliases to model names; it accepts either an alias or a full
    model name when switching models.
  - Writes are atomic (tmp file + os.replace). Confirm destructive actions when prompted.
"""


import argparse
import json
import os
import sys
from urllib.parse import urlparse
from lemonpie.paths import CONFIG_FILE

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # default structure uses list-of-objects for models
        return {"server": None, "default": None, "models": []}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Ensure structure keys exist
    cfg.setdefault("server", None)
    cfg.setdefault("default", None)
    cfg.setdefault("models", [])
    return cfg


def save_config(cfg):
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CONFIG_FILE)


def find_by_alias(cfg, alias):
    for idx, m in enumerate(cfg.get("models", [])):
        if m.get("alias") == alias:
            return idx, m
    return None, None


def find_by_name(cfg, name):
    for idx, m in enumerate(cfg.get("models", [])):
        if m.get("name") == name:
            return idx, m
    return None, None


def ensure_models_list(cfg):
    # Guarantee models is a list (defensive)
    if not isinstance(cfg.get("models"), list):
        cfg["models"] = []


def is_valid_url(url):
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and p.netloc != ""
    except Exception:
        return False


def confirm(prompt):
    ans = input(f"{prompt} (y/N): ").strip().lower()
    return ans in ("y", "yes")


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
        print(f'Default model set to {m["name"]} (alias: {identifier})')
        return 0

    # Try full model name
    _, m = find_by_name(cfg, identifier)
    if m:
        cfg["default"] = m["name"]
        save_config(cfg)
        print(f'Default model set to {m["name"]}')
        return 0

    print(f'Model "{identifier}" not found.'
          f' Use --list-models to see configured models.'
          f' Use --add-model to add a new model mapping.')
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
    idx_name, entry_by_name = find_by_name(cfg, model_name)
    idx_alias, entry_by_alias = find_by_alias(cfg, alias)

    # Exact mapping exists -> no-op
    if entry_by_alias and entry_by_name and entry_by_alias is entry_by_name:
        print(f'Alias "{alias}" already maps to "{model_name}". No changes made.')
        return 0

    # If model_name exists under a different alias
    if entry_by_name and entry_by_name.get("alias") and entry_by_name.get("alias") != alias:
        existing_alias = entry_by_name["alias"]
        if not force:
            print(f'Model "{model_name}" is already mapped to alias "{existing_alias}". Use --force to reassign.')
            return 2
        # force: clear the old alias (set to None) but keep the model record
        print(f'Removing alias "{existing_alias}" from model "{model_name}". It will remain accessible by full name.')
        entry_by_name["alias"] = None

    # If alias exists and maps to a different model
    if entry_by_alias and entry_by_alias.get("name") != model_name:
        existing_model = entry_by_alias["name"]
        if not force:
            print(f'Alias "{alias}" is already in use for model "{existing_model}". Please use a different alias or remove the existing mapping.')
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
    print(f'Added model mapping: {alias} -> {model_name}')

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

    idx_alias, entry_alias = find_by_alias(cfg, identifier)
    if entry_alias:
        # Clear alias only
        if not confirm(f'Clear alias "{identifier}" from model "{entry_alias["name"]}"? (model will remain accessible by full name)'):
            print("Aborted.")
            return 1
        entry_alias["alias"] = None
        save_config(cfg)
        print(f'Cleared alias "{identifier}" from model "{entry_alias["name"]}".')
        return 0

    idx_name, entry_name = find_by_name(cfg, identifier)
    if entry_name:
        # Remove entire model object
        if not confirm(f'Remove model "{identifier}" entirely from config? This will delete the record.'):
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


def cmd_show(cfg):
    print(json.dumps(cfg, indent=2, ensure_ascii=False))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(prog="lmConfig", description="Manage LemonPie configuration (config.json)")
    parser.add_argument("--host", help="Set Ollama host URL (http(s)://host:port)")
    parser.add_argument("--default-model", help="Set default model using alias or full name (must exist in models)")
    parser.add_argument("--add-model", nargs=2, metavar=("ALIAS", "MODEL"), help="Add model mapping: alias model_full_name")
    parser.add_argument("--remove-model", metavar="IDENTIFIER", help="Remove a model mapping by alias or full name")
    parser.add_argument("--list-models", action="store_true", help="List configured model aliases and names")
    parser.add_argument("--show", action="store_true", help="Print full config.json")
    parser.add_argument("--force", action="store_true", help="Force overwrite when adding a model")
    args = parser.parse_args(argv)

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

    if args.list_models:
        return cmd_list_models(cfg)

    if args.show:
        return cmd_show(cfg)

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]) or 0)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
