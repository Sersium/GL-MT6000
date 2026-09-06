# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp==1.29.1"]
# ///
"""Local stdio MCP bridge to the home Flint 2, using its existing SSH server."""
import asyncio
import os
from pathlib import Path
import shlex
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

mcp = FastMCP(
    "flint-router",
    instructions="Manage the user's home GL-MT6000 OpenWrt router with router_status and "
    "router_exec. SSH authentication is already configured; no password is needed. "
    "Commands run as root on the router. Use the flint-router skill for router workflows. "
    "Read current state, make changes within the user's request, then verify live state. "
    "A timeout does not prove a write failed; inspect before retrying.",
)


async def drain(stream, limit):
    kept = bytearray()
    size = 0
    while chunk := await stream.read(65536):
        kept.extend(chunk[:max(0, limit - len(kept))])
        size += len(chunk)
    return kept.decode("utf-8", errors="replace"), size > limit


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True))
async def router_exec(
    command: Annotated[str, Field(min_length=1, max_length=65536)],
    stdin: Annotated[str, Field(max_length=1048576)] = "",
    timeout_seconds: Annotated[int, Field(ge=1, le=300)] = 60,
    output_bytes: Annotated[int, Field(ge=1024, le=131072)] = 20000,
) -> dict[str, str | int | bool]:
    """Execute a BusyBox ash command as root on the home OpenWrt Flint 2 router.

    Full read/write access: use ubus, UCI, logs, service commands, cat, and shell tools.
    For file contents pass stdin, e.g. command='cat > /tmp/example', stdin='contents'.
    Back up existing configuration before replacing it. Output is UTF-8; use hex for
    binary data. stdout/stderr are bounded independently and report truncation.
    The remote timeout also applies if the local client disconnects. Commands that
    detach themselves can outlive it. Nonzero exit codes must be checked by the caller.
    """
    if "\0" in command:
        raise ValueError("command cannot contain NUL")
    config = str(Path(os.environ.get("FLINT_SSH_CONFIG", "~/.ssh/flint-router.conf")).expanduser())
    remote = f"timeout -k 2 {timeout_seconds} sh -c {shlex.quote(command)}"
    proc = await asyncio.create_subprocess_exec(
        "ssh", "-F", config, "-T", "flint-router", remote,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async def feed():
        try:
            proc.stdin.write(stdin.encode())
            await proc.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            proc.stdin.close()

    try:
        _, out, err, code = await asyncio.wait_for(
            asyncio.gather(feed(), drain(proc.stdout, output_bytes),
                           drain(proc.stderr, output_bytes), proc.wait()),
            timeout=timeout_seconds + 15,
        )
    except BaseException:
        if proc.returncode is None:
            proc.kill()
        await proc.wait()
        raise
    return {"exit_code": code, "stdout": out[0], "stderr": err[0],
            "stdout_truncated": out[1], "stderr_truncated": err[1]}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
async def router_status() -> dict[str, str | int | bool]:
    """Read home Flint 2 model/firmware, uptime, storage, WAN state and pending UCI changes."""
    return await router_exec("ubus call system board; uptime; df -h /overlay; ifstatus wan; uci changes")


if __name__ == "__main__":
    mcp.run(transport="stdio")
