---
name: flint-router
description: Inspect and configure the user's home Flint 2 (GL-MT6000) OpenWrt router, including home internet, Wi-Fi, DNS, firewall, SQM, WireGuard, packages, logs, and firmware. Use for requests about the home router; its SSH connection is already configured.
---

# Home Flint 2

Use this plugin's `router_status` and `router_exec` MCP tools. They connect as root
through a dedicated SSH key; the user does not need to provide SSH instructions or
a password. Full filesystem and command access is available. Read-only status is a
useful starting point; follow the scope of the current user request for writes.

- Router: GL.iNet GL-MT6000, OpenWrt, LAN `192.168.1.1`.
- Firmware source: https://github.com/Sersium/GL-MT6000 (upstream cjom/GL-MT6000).
- Shell: BusyBox ash. Use UCI for configuration and ubus/ifstatus for live state.
- MCP runs on the agent computer; no router daemon or additional network port.
- SSH fallback: `ssh -F ~/.ssh/flint-router.conf flint-router 'COMMAND'`.
  An SSH sandbox/network permission failure needs the client's normal permission
  mechanism. Do not change host verification or ask for the router password.

Use `router_exec(command=..., stdin=...)` to send file contents without embedding
them in shell syntax. For an existing file, inspect and back it up first, preserve
its permissions, and prefer a same-directory temporary file followed by `mv`.
Check `exit_code` and both truncation flags. Narrow reads of large logs/files.
Timeouts/disconnects leave the write outcome uncertain: inspect before retrying.
Do not silently repeat a timed-out mutation.

For network/firewall/SSH changes that could drop access, prepare a timed rollback
before applying, retain the SSH session where practical, then verify reconnection
and WAN/DNS service before canceling rollback. UCI firewall changes need
`/etc/init.d/firewall reload`; network reload alone is insufficient. Read the
current configuration instead of assuming interface names or DNS addresses.

For firmware work, preserve the fork's customizations and SSH authorization.
`sysupgrade -l` should include `/root/.ssh/authorized_keys` and SSH host keys.
Keep private keys and passwords out of the repository and generated firmware.
Flashing/rebooting is a separate disruptive operation; do it when requested.
