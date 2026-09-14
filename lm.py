#!/usr/bin/env python3
"""
LemonPie (lm.py) — lightweight CLI for managing chat sessions with Ollama

Purpose
  Manage chat sessions, send prompts to an Ollama model, and persist session
  history locally. Sessions are stored under the `sessions/` directory as JSON
  files. `config.json` provides the Ollama host, model nickname mappings, and
  a default model nickname.

Usage examples
  # Start a new session with the default model and send a prompt
  lm -n "Hello"

  # Start a new session with a named model nickname and send a prompt
  lm -n -m q2.5-1.5b "Hello"

  # Send a prompt to the current session (creates one automatically if none)
  lm "Tell me about git add"

  # List sessions (shows created/updated dates and marks current session)
  lm -l

  # Print the current session history
  lm -p

  # Load an existing session and make it current
  lm -s 20260911-171931

  # Set or update the title of the current session
  lm -t "My debugging session"

  # Change the model for the current session (prompts for confirmation)
  lm -m q2.5-3b

  # Close the current session (clears the .current pointer)
  lm -c

  # Delete a session by id (prompts for confirmation)
  lm -d 20260911-171931

Behavior and safety
  - Model nicknames are defined in config.json. Passing -m with an unknown
    nickname will print a warning and will not be forwarded to Ollama unless
    the nickname exists in the config.
  - Writes to session files and the .current pointer are atomic (written to a
    .tmp file and then replaced).
  - Timestamps are ISO 8601 with timezone information.
  - Ctrl-C while waiting for a model response is handled gracefully.

Config file (config.json) structure
  {
    "server": "http://127.0.0.1:11434",
    "default": "q2.5-3b",
    "models": {
      "q2.5-3b": "qwen2.5-coder:3b",
      "q2.5-1.5b": "qwen2.5-coder:1.5b-base"
    }
  }

Notes for maintainers
  - The script detects whether -m was explicitly passed by inspecting sys.argv.
  - Use lmConfig.py to manage config.json (host, default, add/remove model
    nicknames) rather than editing config.json by hand.
  - Consider adding file locking if concurrent runs are expected.

"""

import sys, json, argparse, os
from datetime import datetime, timezone
from ollama import Client

# Load config
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "config.json")) as f:
    cfg = json.load(f)

client = Client(host=os.environ.get("OLLAMA_HOST") or cfg.get("server"))

# Expose models and default as before but adapted to new shape
models_list = cfg["models"]            # list of {alias,name}
default_model_name = cfg.get("default")  # canonical model name (full identifier)

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)
CURRENT_FILE = os.path.join(SESSIONS_DIR, ".current")

MAX_TITLE_LEN = 50

def session_path(session_id):
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def now_ts():
    return datetime.now(timezone.utc).astimezone().isoformat()

def short_date(iso_ts):
    if not iso_ts:
        return "<unknown>"
    try:
        dt = datetime.fromisoformat(iso_ts)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_ts

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
            continue
    return sessions

def delete_session(session_id):
    try:
        os.remove(session_path(session_id))
        return True
    except FileNotFoundError:
        return False

def default_title(prompt):
    return prompt if len(prompt) <= MAX_TITLE_LEN else prompt[:MAX_TITLE_LEN].rstrip() + "…"

def set_title(session, new_title):
    if len(new_title) > MAX_TITLE_LEN:
        print(f"title exceeds {MAX_TITLE_LEN} characters. please try again")
        return False
    session["title"] = new_title
    save_session(session["id"], session)
    return True

def print_session(session):
    print(f"Session {session['id']} — {session.get('title') or '<no title>'}")
    for turn in session["history"]:
        role = turn["role"]
        content = turn["content"]
        print(f"{role} [{turn.get('ts','')}] : {content}")

# Helper functions for model lookups
def find_by_alias(cfg, alias):
    for m in cfg.get("models", []):
        if m.get("alias") == alias:
            return m
    return None

def find_by_name(cfg, name):
    for m in cfg.get("models", []):
        if m.get("name") == name:
            return m
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Model alias or full name", default=None)
    parser.add_argument("-n", "--new", action="store_true", help="Start a new chat session")
    parser.add_argument("-s", "--session", help="Load an existing session by ID")
    parser.add_argument("-l", "--list", action="store_true", help="List chat sessions")
    parser.add_argument("-d", "--delete", help="Delete a session by ID")
    parser.add_argument("-t", "--title", help="Set or update session title")
    parser.add_argument("-c", "--close", action="store_true", help="Close current session")
    parser.add_argument("-p", "--print", action="store_true", help="Print current session history")
    parser.add_argument("prompt", nargs="*", help="Prompt text")
    args = parser.parse_args()

    # detect whether -m/--model was explicitly passed on the command line
    model_flag = any(a in ("-m", "--model") for a in sys.argv[1:])

    # Resolve model input: accept alias or full model name
    # model_flag indicates user explicitly passed -m
    if model_flag:
        # Try alias first
        entry = find_by_alias(cfg, args.model)
        if entry:
            model = entry["name"]
        else:
            # If not a known alias, treat args.model as a full model name but do NOT forward unknown names
            # We will warn later if the name is not configured.
            model = args.model
    else:
        # No explicit -m: use configured default model name (may be None)
        model = default_model_name

    # Resolve current session id from file
    current_id = read_current()

    # If user only passed -m and there is no current session and they didn't ask to create/load or send a prompt, print instructions and exit
    if model_flag and not current_id and not args.new and not args.session and not args.prompt:
        print(f'No current session.\n'
              f'To create a new session with "{args.model}" use: lm -n -m {args.model}\n'
              f'To change the model of a specific session: lm -s <id> -m {args.model}\n'
              f'To change the default model use lmConfig.')
        sys.exit(0)

    # Handle listing
    if args.list:
        for sid, title, created, updated, is_current in list_sessions():
            print(f"{is_current} {sid}  {title} created: {created}, updated: {updated}")
        sys.exit(0)

    # Handle printing current session
    if args.print:
        if not current_id:
            print("No current session.")
            sys.exit(0)
        session = load_session(current_id)
        for turn in session["history"]:
            print(f"{turn['role']} [{turn.get('ts','')}] : {turn['content']}")
        sys.exit(0)

    # Handle deletion
    if args.delete:
        confirm = input(f'Delete session {args.delete}? (Y/n): ')
        if confirm.lower() in ("y", "yes", ""):
            if delete_session(args.delete):
                print(f"Deleted session {args.delete}")
                # If it was current, clear pointer
                if read_current() == args.delete:
                    clear_current()
            else:
                print(f"No session found with id {args.delete}")
        else:
            print("Aborted deletion.")
        sys.exit(0)

    # Handle close current session
    if args.close:
        clear_current()
        print("Current session closed.")
        sys.exit(0)

    # Create new session
    if args.new:
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        title = default_title(" ".join(args.prompt)) if args.prompt else "<no title>"
        session = {"id": session_id, "model": model, "title": title, "history": [], "created_at": now_ts(), "updated_at": now_ts()}
        save_session(session_id, session)
        write_current(session_id)

    # Explicitly load a session and make it current
    elif args.session:
        session_id = args.session
        session = load_session(session_id)
        model = session.get("model", model)
        write_current(session_id)

    # If a current session exists, load it
    elif current_id:
        session_id = current_id
        session = load_session(session_id)
        model = session.get("model", model)

    # No current session and no -n/-s: create a new session automatically
    else:
        from datetime import datetime
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        title = default_title(" ".join(args.prompt)) if args.prompt else "<no title>"
        session = {"id": session_id, "model": model, "title": title, "history": [], "created_at": now_ts(), "updated_at": now_ts()}
        save_session(session_id, session)
        write_current(session_id)

    # Handle model update for an active session
    if model_flag and session:
        # Resolve the requested model: prefer alias, then full name if present in config
        alias_entry = find_by_alias(cfg, args.model)
        name_entry = find_by_name(cfg, args.model)

        if alias_entry:
            new_model = alias_entry["name"]
        elif name_entry:
            new_model = name_entry["name"]
        else:
            # Unknown alias/name — inform user and do not forward to Ollama
            print(f'Warning: "{args.model}" is not a known alias or configured model.')
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


    # Handle title update
    if args.title:
        if not session:
            confirm = input(f'No current session. Create a new session with title "{args.title}"? (Y/n): ')
            if confirm.lower() in ("y", "yes", ""):
                from datetime import datetime
                session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
                session = {"id": session_id, "model": model, "title": args.title, "history": [], "created_at": now_ts(), "updated_at": now_ts()}
                save_session(session_id, session)
                write_current(session_id)
                print(f'Created new session {session_id} with title "{args.title}".')
            else:
                print("Aborted creating new session.")
                sys.exit(0)
        else:
            set_title(session, args.title)
            print(f'Updated title for session {session["id"]} to "{args.title}".')
        if not args.prompt:
            sys.exit(0)

    # Handle prompt
    if args.prompt:
        user_prompt = " ".join(args.prompt)
        turn_ts = now_ts()
        session["history"].append({"role": "user", "content": user_prompt, "ts": turn_ts})
        session["updated_at"] = turn_ts
        save_session(session_id, session)

        # Final validation: ensure model is a configured model name
        if not find_by_name(cfg, model):
            print(f'Configured models do not include "{model}". Use lmConfig to add it or pass a known alias.')
            sys.exit(1)

        # Streamed chat response from Ollama (robust extraction of text parts)
        assistant_reply = ""
        reply_ts = None
        try:
            stream = client.chat(model=model, messages=session["history"], stream=True)

            for chunk in stream:
                # Extract text part from common chunk shapes
                part = ""

                # 1) dict-like chunk: {"message": {"content": "..."}} or {"content": "..."}
                if isinstance(chunk, dict):
                    part = chunk.get("message", {}).get("content", "") or chunk.get("content", "") or ""

                # 2) plain string chunk
                elif isinstance(chunk, str):
                    part = chunk

                # 3) object with .message (dataclass-like)
                else:
                    # try common attributes safely
                    msg = getattr(chunk, "message", None)
                    if msg is not None:
                        # msg might be an object or dict
                        if isinstance(msg, dict):
                            part = msg.get("content", "") or ""
                        else:
                            part = getattr(msg, "content", "") or ""
                    else:
                        # fallback: direct content attribute
                        part = getattr(chunk, "content", "") or getattr(chunk, "text", "") or ""

                if not part:
                    # nothing useful in this chunk; skip printing
                    continue

                # Print chunk immediately (streaming) and accumulate
                print(part, end="", flush=True)
                assistant_reply += part

            # tidy newline after stream completes
            print()
            reply_ts = now_ts()

        except KeyboardInterrupt:
            try:
                if 'stream' in locals() and hasattr(stream, "close"):
                    stream.close()
            except Exception:
                pass
            print("\nInterrupted by user.")
            sys.exit(1)

        except Exception as e:
            print("\nFailed to contact Ollama server:", e)
            sys.exit(1)

        # Save the final assistant reply
        if assistant_reply:
            session["history"].append({"role": "assistant", "content": assistant_reply, "ts": reply_ts or now_ts()})
            session["updated_at"] = reply_ts or now_ts()
            save_session(session_id, session)
        else:
            print("No response from model.")
