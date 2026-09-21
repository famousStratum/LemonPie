"""Ollama API interaction abstractions: client construction and streaming chat."""

from ollama import Client


def build_client(server_host, timeout):
    return Client(host=server_host, timeout=timeout)


def stream_chat(client, model, messages):
    """
    Stream a chat completion from Ollama, yielding text content chunks.

    The underlying stream is closed automatically when this generator is
    closed (e.g. via a `for` loop finishing, an exception propagating, or an
    explicit `.close()` call on the generator by the caller).
    """
    stream = client.chat(model=model, messages=messages, stream=True)
    try:
        for chunk in stream:
            # Standard Ollama client attribute access
            content = getattr(getattr(chunk, "message", None), "content", None)
            if content is None and isinstance(chunk, dict):
                content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
    finally:
        if hasattr(stream, "close"):
            stream.close()


def resolve_ollama_error(exc, server_host):
    """
    Map an exception raised during an Ollama request to a (message, hint)
    pair suitable for printing to the user. `hint` may be None.
    """
    msg = str(exc)
    if "[Errno 111]" in msg or "Connection refused" in msg:
        return (
            "Ollama server did not respond: Connection refused.",
            f"Hint: Ollama may not be running, or it may not be listening on: {server_host}\n"
            "Check that the server is started with `ollama serve` and bound to the correct interface.",
        )
    if "[Errno 110]" in msg or "timed out" in msg.lower():
        return (
            "Failed to contact Ollama server: Connection timed out.",
            f"Hint: The server at {server_host} is unreachable. Verify IP/port and network.",
        )
    return (f"Failed to contact Ollama server: {msg}", None)
