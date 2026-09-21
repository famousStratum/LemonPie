import random
import sys
import threading
import time

from lemonpie.sessions.storage import list_sessions

CONNECTING_MSGS = [
    "Connecting",
    "Squeezing the lemons",
    "Knocking on Ollama’s door",
]

WAITING_MSGS = [
    "Waiting for model response",
    "The pie is cooking",
    "Brewing tokens",
]


def confirm(prompt):
    ans = input(f"{prompt} (y/N): ").strip().lower()
    return ans in ("y", "yes")


def print_session(session):
    print(f"Session {session['id']} — {session.get('title') or '<no title>'}")
    for turn in session["history"]:
        role = turn["role"]
        content = turn["content"]
        print(f"{role} [{turn.get('ts', '')}] : {content}")


def print_sessions_list():
    sessions = list_sessions()
    if not sessions:
        print("No sessions found.")
        return
    for sid, title, created, updated, is_current in sessions:
        print(f"{is_current} {sid}  {title} created: {created}, updated: {updated}")


class StatusSpinner:
    def __init__(self, messages, interval=0.5):
        self.messages = messages
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def _animate(self):
        dots = ""
        msg = random.choice(self.messages)
        while self.running:
            dots = (dots + ".") if len(dots) < 3 else ""
            sys.stdout.write("\r" + msg + dots + "   ")
            sys.stdout.flush()
            time.sleep(self.interval)

    def stop(self, clear=True, replace=None):
        self.running = False
        if self.thread:
            self.thread.join()
        if clear:
            clear_len = max(len(m) + 6 for m in self.messages)
            sys.stdout.write("\r" + " " * clear_len + "\r")
            sys.stdout.flush()
        if replace:
            sys.stdout.write(replace + "\n")
            sys.stdout.flush()
