#!/usr/bin/env python3
"""
LemonPie (lm.py) — lightweight CLI for managing chat sessions with Ollama

Purpose
  Manage chat sessions, send prompts to Ollama models, and persist session
  history locally under `sessions/`. Configuration (host, default model, aliases)
  is stored in `config.json`.

Quick usage
  lm -n "Hello"        # start a new session
  lm "Hello"           # send prompt (auto-creates if none)
  lm -l                # list sessions
  lm -p                # print current session
  lm -h                # full help and options

See README.md for details and maintainer notes.
"""

import argparse, errno, httpx, json, os, sys
from datetime import datetime, timezone
from ollama import Client

from lemonpie.paths import CURRENT_FILE, SESSIONS_DIR

from lemonpie.config import (
    load_config,
    resolve_server_host,
    build_timeout,
)

from lemonpie.cli_utils import (
    build_parser,
    list_sessions,
    print_session,
    print_sessions_list,
)

from lemonpie.model_utils import (
    find_by_alias,
    find_by_name,
    handle_model_switch,
    resolve_model,
)

from lemonpie.session_utils import (
    create_session,
    load_session_by_id,
    delete_session_by_id,
    delete_all_sessions,
    resolve_session,
    close_session,
    load_session,
    save_session,
    delete_session,
    read_current,
    write_current,
    clear_current,
    default_title,
    set_title,
    update_title,
)

from lemonpie.spinner import (
    StatusSpinner,
    CONNECTING_MSGS,
    WAITING_MSGS,
)

from lemonpie.time_utils import now_ts

cfg = load_config()
server_host = resolve_server_host(cfg)
timeout = build_timeout()
client = Client(host=server_host, timeout=timeout)

models_list = cfg["models"]
default_model_name = cfg.get("default") or None

def main():
    parser = build_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    model_flag = any(a in ("-m", "--model") for a in sys.argv[1:])
    resolve_model(cfg, args.model, default_model_name)

    model = default_model_name
    if model is None:
        print("No default model configured.")
        print("Use lmConfig to add one or pass a known alias with -m.")
        sys.exit(1)

    current_id = read_current()

    # Direct CLI actions

    if args.list:
        print_sessions_list(); sys.exit(0)

    if args.print:
        if not current_id:
            print("No active session.")
            sys.exit(0)
        session = load_session(current_id)
        if not session:
            print(f"Session {current_id} not found.")
            sys.exit(0)
        print_session(session)
        sys.exit(0)

    if args.delete:
        delete_session_by_id(args.delete); sys.exit(0)

    if args.close:
        close_session(); sys.exit(0)

    if args.delete_all:
        confirm = input("Are you sure you want to delete ALL sessions? (y/N): ")
        if confirm.lower() in ("y", "yes"):
            count = delete_all_sessions()
            print(f"Deleted {count} session(s).")
        else:
            print("Aborted."); sys.exit(0)

    if model_flag and not current_id and not args.new and not args.session and not args.prompt:
        print(f'No current session.\n'
              f'To create a new session with "{args.model}" use: lm -n -m {args.model}\n'
              f'To change the model of a specific session: lm -s <id> -m {args.model}\n'
              f'To change the default model use lmConfig.')
        sys.exit(0)

    session = resolve_session(args, model, current_id)
    session_id = session["id"]

    if model_flag and session:
        session = handle_model_switch(cfg, session, args.model)

    if args.title:
        session = update_title(session, model, args.title, args.prompt)

    if args.prompt:
        user_prompt = " ".join(args.prompt)
        turn_ts = now_ts()
        if session:
            session["history"].append({"role": "user", "content": user_prompt, "ts": turn_ts})
            session["updated_at"] = turn_ts
            save_session(session_id, session)
        else:
            session = create_session(user_prompt, model)
            session_id = session["id"]

        if not find_by_name(cfg, model):
            print(f'Configured models do not include "{model}". Use lmConfig to add it or pass a known alias.')
            sys.exit(1)

        spinner = StatusSpinner(CONNECTING_MSGS)
        spinner.start()

        assistant_reply = ""
        reply_ts = None
        first_chunk_seen = False

        try:
            stream = client.chat(model=model, messages=session["history"], stream=True)
            spinner.stop()

            spinner = StatusSpinner(WAITING_MSGS)
            spinner.start()

            for chunk in stream:
                if not first_chunk_seen:
                    spinner.stop()
                    first_chunk_seen = True

                # Standard Ollama client attribute access
                content = getattr(getattr(chunk, "message", None), "content", None)
                if content is None and isinstance(chunk, dict):
                    content = chunk.get("message", {}).get("content", "")

                if content:
                    print(content, end="", flush=True)
                    assistant_reply += content
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
            msg = str(e)
            if "[Errno 111]" in msg or "Connection refused" in msg:
                print("\nOllama server did not respond: Connection refused.")
                print("Hint: Ollama may not be running, or it may not be listening on:", server_host)
                print("Check that the server is started with `ollama serve` and bound to the correct interface.")
            elif "[Errno 110]" in msg or "timed out" in msg.lower():
                print("\nFailed to contact Ollama server: Connection timed out.")
                print("Hint: The server at", server_host, "is unreachable. Verify IP/port and network.")
            else:
                print("\nFailed to contact Ollama server:", msg)
            sys.exit(1)

        finally:
            spinner.stop()

        if assistant_reply:
            session["history"].append({"role": "assistant", "content": assistant_reply, "ts": reply_ts or now_ts()})
            session["updated_at"] = reply_ts or now_ts()
            save_session(session_id, session)
        else:
            print("No response from model.")

if __name__ == "__main__":
    main()
