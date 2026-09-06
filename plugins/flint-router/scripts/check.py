"""Run with: uv run --with mcp==1.29.1 python scripts/check.py [--live]."""
import asyncio
import json
import subprocess
from pathlib import Path
import sys
import uuid

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(command=sys.executable,
                                  args=[str(Path(__file__).with_name('server.py'))])
    if '--installed' in sys.argv:
        servers = json.loads(subprocess.check_output(['codex', 'mcp', 'list', '--json']))
        config = next(s['transport'] for s in servers if s['name'] == 'flint_router')
        server = StdioServerParameters(command=config['command'], args=config['args'],
                                      cwd=config['cwd'], env=config.get('env'))
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            tools = {t.name: t for t in (await client.list_tools()).tools}
            assert set(tools) == {'router_status', 'router_exec'}
            assert tools['router_status'].annotations.readOnlyHint
            assert not tools['router_exec'].annotations.readOnlyHint
            for args in ({'command': ''}, {'command': 'true', 'timeout_seconds': 0},
                         {'command': 'true', 'output_bytes': 0}, {'command': '\0'}):
                assert (await client.call_tool('router_exec', args)).isError
            print('PASS: MCP initialization, discovery, annotations and invalid input')
            if '--live' not in sys.argv:
                return

            async def run(command, **kwargs):
                result = await client.call_tool('router_exec', {'command': command, **kwargs})
                assert not result.isError, result
                return result.structuredContent

            result = await client.call_tool('router_status', {})
            assert not result.isError, result
            assert 'GL-MT6000' in result.structuredContent['stdout']
            print('PASS: live router status')
            path = '/tmp/flint-mcp-check-' + uuid.uuid4().hex
            payload = "quotes ' \" $() ` ; \\ and unicode café\n" * 2048
            try:
                result = await run(f"umask 077; cat > {path}", stdin=payload)
                assert result['exit_code'] == 0, result
                result = await run(f'cat {path}', output_bytes=131072)
                assert result['stdout'] == payload and not result['stdout_truncated'], result
                result = await run(f'cat {path}; cat {path} >&2', output_bytes=1024)
                assert result['stdout_truncated'] and result['stderr_truncated'], result
                assert len(result['stdout'].encode()) <= 1027
                result = await run("printf '%s' \"a'b\"; printf problem >&2; exit 7")
                assert (result['exit_code'], result['stdout'], result['stderr']) == (7, "a'b", 'problem'), result
                result = await run('sleep 4; printf should-not-run', timeout_seconds=1)
                assert result['exit_code'] != 0 and 'should-not-run' not in result['stdout'], result
                print('PASS: root file write/read, literal stdin, bounded output, quoting, exit status and remote timeout')
            finally:
                result = await run(f'rm -f {path}; test ! -e {path}')
                assert result['exit_code'] == 0, result
                print('PASS: temporary test file removed')


asyncio.run(main())
