import glob, json, os, sys
from datetime import datetime, timezone

from lemonpie.paths import CURRENT_FILE, SESSIONS_DIR
from lemonpie.time_utils import now_ts, short_date

MAX_TITLE_LEN = 50

def session_path(session_id):
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def read_current():
    try:
        with open(CURRENT_FILE, "r", encoding="utf-8") as f:
            sid = f.read().strip()
            return sid if sid else None
    except FileNotFoundError:
        return None

def write_current(session_id):
    tmp = CURRENT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(session_id)
    os.replace(tmp, CURRENT_FILE)

def clear_current():
    try:
        os.remove(CURRENT_FILE)
    except FileNotFoundError:
        pass

def resolve_session(args, model, current_id):
    if args.new:
        return create_session(args.prompt, model)
    if args.session:
        return load_session_by_id(args.session, model)
    if current_id:
        return load_session(current_id)
    return create_session(args.prompt, model)

def load_session(session_id):
    try:
        with open(session_path(session_id), "r", encoding="utf-8") as f:
            return json.load(f)
        # Backfill created_at/updated_at from history if missing
        if "created_at" not in s or not s.get("created_at"):
            if s.get("history"):
                s["created_at"] = s["history"][0].get("ts")
            else:
                # fallback to file mtime
                s["created_at"] = datetime.fromtimestamp(
                    os.path.getmtime(session_path(session_id))
                ).astimezone().isoformat()
        if "updated_at" not in s or not s.get("updated_at"):
            if s.get("history"):
                s["updated_at"] = s["history"][-1].get("ts")
            else:
                s["updated_at"] = s["created_at"]
        return s
    except FileNotFoundError:
        return {"id": session_id, "title": None, "history": [], "created_at": None, "updated_at": None}

def save_session(session_id, session):
    tmp = session_path(session_id) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
    os.replace(tmp, session_path(session_id))

def delete_session(session_id):
    try:
        os.remove(session_path(session_id))
        return True
    except FileNotFoundError:
        return False

def delete_all_sessions():
    """Deletes all session files in SESSIONS_DIR and clears current session marker."""
    deleted_count = 0

    if os.path.exists(SESSIONS_DIR):
        for filepath in glob.glob(os.path.join(SESSIONS_DIR, "*.json")):
            try:
                os.remove(filepath)
                deleted_count += 1
            except OSError:
                pass

    clear_current()
    return deleted_count

def default_title(prompt):
    return prompt if len(prompt) <= MAX_TITLE_LEN else prompt[:MAX_TITLE_LEN].rstrip() + "…"

def set_title(session, new_title):
    if len(new_title) > MAX_TITLE_LEN:
        print(f"title exceeds {MAX_TITLE_LEN} characters. please try again")
        return False
    session["title"] = new_title
    save_session(session["id"], session)
    return True

def create_session(prompt, model):
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    title = default_title(" ".join(prompt)) if prompt else "<no title>"
    session = {"id": session_id, "model": model, "title": title, "history": [], "created_at": now_ts(), "updated_at": now_ts()}
    save_session(session_id, session)
    write_current(session_id)
    return session

def load_session_by_id(session_id, model=None):
    """Load a session by ID and set it as current."""
    session = load_session(session_id)
    if model:
        session["model"] = model
    write_current(session_id)
    return session

def delete_session_by_id(session_id):
    """Delete a session after user confirmation."""
    confirm = input(f'Delete session {session_id}? (Y/n): ')
    if confirm.lower() in ("y", "yes", ""):
        if delete_session(session_id):
            print(f"Deleted session {session_id}")
            if read_current() == session_id:
                clear_current()
        else:
            print(f"No session found with id {session_id}")
    else:
        print("Aborted deletion.")

def close_session():
    """Close the current session pointer."""
    clear_current()
    print("Current session closed.")

def update_title(session, model, new_title, prompt=None):
    """Update or create a session with a new title."""
    if not session:
        confirm = input(f'No current session. Create a new session with title "{new_title}"? (Y/n): ')
        if confirm.lower() in ("y", "yes", ""):
            session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            session = {
                "id": session_id,
                "model": model,
                "title": new_title,
                "history": [],
                "created_at": now_ts(),
                "updated_at": now_ts()
            }
            save_session(session_id, session)
            write_current(session_id)
            print(f'Created new session {session_id} with title "{new_title}".')
        else:
            print("Aborted creating new session.")
            sys.exit(0)
    else:
        set_title(session, new_title)
        print(f'Updated title for session {session["id"]} to "{new_title}".')

    # If no prompt was passed, exit after title update
    if not prompt:
        sys.exit(0)

    return session

def list_sessions():
    sessions = []
    current = read_current()
    for fname in os.listdir(SESSIONS_DIR):
        if not fname.endswith(".json"):
          continue
        try:
            with open(os.path.join(SESSIONS_DIR, fname), encoding="utf-8") as f:
                data = json.load(f)
            if "id" in data:
                created = short_date(data.get("created_at"))
                updated = short_date(data.get("updated_at"))
                is_current = "*" if data["id"] == current else " "
                sessions.append((data["id"], data.get("title") or "<no title>", created, updated, is_current))
        except Exception:
            # skip invalid JSON files
            print("DEBUG: loaded", fname, "->", data.get("id"))
            continue
    return sessions
