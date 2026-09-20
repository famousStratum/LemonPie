import sys, time, random, threading

CONNECTING_MSGS = [
    "Connecting",
    "Squeezing the lemons",
    "Knocking on Ollama’s door"
]

WAITING_MSGS = [
    "Waiting for model response",
    "The pie is cooking",
    "Brewing tokens"
]

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
