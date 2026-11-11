"""API interaction abstractions: client construction and streaming chat."""

import json

import httpx


def build_client(server_host, timeout, api_key=None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return httpx.Client(base_url=server_host, timeout=timeout, headers=headers)


def stream_chat(client, model, messages):
    """
    Stream a chat completion from an OpenAI-compatible endpoint,
    yielding text content chunks.
    """
    payload = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        "stream": True,
    }

    with client.stream("POST", "/v1/chat/completions", json=payload) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                continue


def resolve_error(exc: Exception, server_host: str) -> tuple[str, str | None]:
    """
    Map an exception raised during an httpx request to a (message, hint)
    pair suitable for printing to the user. `hint` may be None.
    """
    msg = str(exc)
    msg_lower = msg.lower()

    if isinstance(exc, httpx.TimeoutException):
        if isinstance(exc, httpx.ConnectTimeout):
            return (
                "Failed to contact server: Connection timed out.",
                f"Hint: The server at '{server_host}' is unreachable. Verify the network and IP/port settings.",
            )
        return (
            "Server did not respond in time: Request timed out.",
            f"Hint: The server at '{server_host}' accepted the connection, but took too long to respond.",
        )

    if isinstance(exc, httpx.ConnectError):
        refused_errors = (
            "errno 111",
            "errno 61",
            "errno 10061",
            "connection refused",
            "actively refused it",
        )
        if any(err in msg_lower for err in refused_errors):
            return (
                "Server did not respond: Connection refused.",
                (
                    f"Hint: The server may not be running, or it may not be listening on '{server_host}'.\n"
                    "Check that the server is started and bound to the correct interface."
                ),
            )

        dns_errors = (
            "errno -2",
            "errno -3",
            "errno 8",
            "errno 11001",
            "name or service not known",
            "no such host is known",
            "getaddrinfo failed",
            "temporary failure in name resolution",
            "nodename nor servname provided",
        )
        if any(err in msg_lower for err in dns_errors):
            return (
                "Failed to contact server: Could not resolve hostname.",
                f"Hint: '{server_host}' could not be found. Check the server URL in your config.",
            )

        ssl_errors = ("certificate_verify_failed", "ssl:")
        if any(err in msg_lower for err in ssl_errors):
            return (
                "Failed to contact server: SSL/TLS verification failed.",
                f"Hint: Check if '{server_host}' uses a self-signed certificate or if your system clock is incorrect.",
            )

        return (
            f"Failed to contact server: {msg}",
            f"Hint: Check your network connection and verify '{server_host}' is reachable.",
        )

    if isinstance(exc, httpx.ProtocolError):
        return (
            f"Failed to contact server: Invalid protocol response ({msg}).",
            f"Hint: Ensure '{server_host}' is speaking HTTP/HTTPS and not another protocol (like SSH or raw TCP).",
        )

    if isinstance(exc, httpx.InvalidURL):
        return (
            f"Invalid server URL: '{server_host}'.",
            "Hint: Ensure the URL includes the scheme (e.g., 'http://' or 'https://').",
        )

    return f"Failed to contact server: {msg}", None
