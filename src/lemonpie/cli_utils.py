import argparse

from lemonpie.session_utils import list_sessions, read_current

try:
    from lemonpie._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

def build_parser():
    parser = argparse.ArgumentParser(prog="lm", description="Run LemonPie with a given model or prompt")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-m", "--model", help="Model alias or full name", default=None)
    parser.add_argument("-n", "--new", action="store_true", help="Start a new chat session")
    parser.add_argument("-s", "--session", help="Load an existing session by ID")
    parser.add_argument("-l", "--list", action="store_true", help="List chat sessions")
    parser.add_argument("-d", "--delete", help="Delete a session by ID")
    parser.add_argument("-t", "--title", help="Set or update session title")
    parser.add_argument("-c", "--close", action="store_true", help="Close current session")
    parser.add_argument("-p", "--print", action="store_true", help="Print current session history")
    parser.add_argument("--delete-all", action="store_true", help="Delete all stored sessions")
    parser.add_argument("prompt", nargs="*", help="Prompt text")
    return parser

def confirm(prompt):
    ans = input(f"{prompt} (y/N): ").strip().lower()
    return ans in ("y", "yes")

def print_session(session):
    print(f"Session {session['id']} — {session.get('title') or '<no title>'}")
    for turn in session["history"]:
        role = turn["role"]
        content = turn["content"]
        print(f"{role} [{turn.get('ts','')}] : {content}")

def print_sessions_list():
    sessions = list_sessions()
    if not sessions:
        print("No sessions found.")
        return
    for sid, title, created, updated, is_current in sessions:
        print(f"{is_current} {sid}  {title} created: {created}, updated: {updated}")
