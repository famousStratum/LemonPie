import argparse

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
