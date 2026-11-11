import sys

from lemonpie.sessions.storage import save_session


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


def resolve_model(cfg, args_model, default_model_name):
    if args_model:
        _, alias_entry = find_by_alias(cfg, args_model)
        if alias_entry:
            return alias_entry["name"]
        _, name_entry = find_by_name(cfg, args_model)
        if name_entry:
            return name_entry["name"]
        return args_model
    return default_model_name


def handle_model_switch(cfg, session, requested_model):
    """
    Handles validating a requested model/alias and updates the active session
    if confirmed by the user.
    """
    if not session or not requested_model:
        return session

    _, alias_entry = find_by_alias(cfg, requested_model)
    _, name_entry = find_by_name(cfg, requested_model)

    if alias_entry:
        new_model = alias_entry["name"]
    elif name_entry:
        new_model = name_entry["name"]
    else:
        print(f'Warning: "{requested_model}" is not a known alias or configured model.')
        print('To add it, use lmConfig --add-model <alias> <model_name>')
        sys.exit(0)

    if new_model != session.get("model"):
        confirm = input(f'Change session {session["id"]} model to "{new_model}"? (Y/n): ')
        if confirm.lower() in ("y", "yes", ""):
            session["model"] = new_model
            save_session(session["id"], session)
            print(f'Session model updated to {new_model}.')
        else:
            print("Aborted model change.")

    return session
