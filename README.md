# GL-MT6000 custom OpenWrt firmware builder

This repository automates the process of building OpenWrt custom firmware images for **MY** Flint 2 (GL-MT6000) router, based on **MY PREFERENCES** and [pesa1234](https://github.com/pesa1234)'s work.

You should **not use** the firmwares released in this repository unless you have the same preferences/needs.
Instead, **make a fork and adapt to your needs**.

Read [this topic](https://forum.openwrt.org/t/mt6000-custom-build-with-luci-and-some-optimization-kernel-6-12-x/185241) in OpenWrt's forum to learn the details about pesa1234's customizations.

Compared to his custom firmware, this firmware adds:
- **WiFi UCODE scripts** (faster boot)
- **Wireguard VPN server**, auto-provisioned on first boot by [`98_wireguard_server`](files/etc/uci-defaults/98_wireguard_server): interface `wg0` (10.100.0.1/24) listening on UDP 51820, WAN firewall rule included, private key generated on-device. Add peers in LuCI (Network → Interfaces → wg0 → Peers) — `qrencode` is included so client configs can be exported as QR codes. Existing configuration is never overwritten.
- **Policy Based Routing** (select what goes through VPN and what not)
- **Measured SQM profile for this 1 Gbps PPPoE link**: CAKE `diffserv4` at 945 Mbps on upload, with per-host fairness, ACK filtering, correct PPPoE/VLAN overhead, and wired LAN ports promoted over WiFi during contention. Download remains unshaped because this MT7986 build measured 934 Mbps with under 1 ms additional loaded latency natively, while IFB ingress shaping reduced throughput to roughly 740 Mbps.
- **AdBlock Fast** (ads and malware blocking at DNS level)
- **Custom Attended Sysupgrade** (install custom firmware from GitHub)
- **NordVPN Lite installer** (optional: nothing is downloaded until you run it)

And also:
- **REMOVED:** odhcp, upnp, iptables, avahi, samba, usb storage and probably more stuff I forgot to mention.
- Added the needed packages to use QoS script [cake-wg-pbr](https://github.com/lynxthecat/cake-wg-pbr)
- Some compiler optimizations and build hardening options (cortex-a53+crc+crypto; LTO, MOLD, and more).
- SSH configuration with strong algorithms and key exchange methods. Check the content of [`ssh_hardening.config`](files/etc/ssh/sshd_config.d/ssh_hardening.conf) and [`sshd_config`](files/etc/ssh/sshd_config).
- Quality-of-life enhancements through UCI configuration. Check the content of [`99-QOL_config`](files/etc/uci-defaults/99-QOL_config).
- Some debug and kernel stuff removed.
- [`upgrade_custom_openwrt`](files/usr/bin/upgrade_custom_openwrt) script

Check the content of [`mt6000.config`](mt6000.config) for details.



## About Custom Attended Sysupgrade

Using Luci's menu "System" --> "Attended Sysupgrade" it is now possible to select and install custom firmware from GitHub.
  
<sub>Custom Attended Sysupgrade</sub>  
![Custom Attended Sysupgrade](attended-sysupgrade-custom.png)
  
<sub>Dropdown list</sub>  
![Dropdown list](attended-sysupgrade-releases.png)
  
<sub>Installing Custom Firmware</sub>  
![Installing Custom Firmware](attended-sysupgrade-installing.png)
  
<sub>GitHub repository</sub>  
![GitHub repository used](attended-sysupgrade-server.png)
  
Notes:
- if you fork this repository, this will be adapted to look for upgrades in your repository by default.



## About NordVPN Lite

The firmware does not include NordVPN Lite itself, only the packages it needs and an installer. Nothing is downloaded until you run, from a SSH terminal:
- `nordvpnlite-install --install` to install the latest release and enable a daily update check (at 04:38).
- `nordvpnlite-install --check` to compare the installed and latest versions.
- `nordvpnlite-install --uninstall` to remove it (the configuration and login are kept).

After installing, log in with `nordvpnlite login <token>` or in Luci's menu "Services" --> "NordVPN Lite", then start it with `/etc/init.d/nordvpnlite start`. When an update is installed, a running NordVPN Lite is restarted.

Notes:
- The binary comes from the releases of [cjom/libtelio](https://github.com/cjom/libtelio/releases), a fork of NordSecurity's libtelio that adds a tunnel health check and an option to leave dnsmasq untouched. To use another fork, change `REPOSITORY` in [`nordvpnlite-install`](files/usr/sbin/nordvpnlite-install).
- The installed files survive firmware upgrades.
- The text output of the installer will show both in terminal and system logs.



## About upgrade_custom_openwrt script

```
THIS IS NOW DEPRECATED, ALTHOUGHT THE SCRIPT IS STILL INCLUDED
```

I added a script to make upgrading OpenWRT super easy. Just run from a SSH terminal:
- `upgrade_custom_openwrt --now` to check if a newer firmware is available and upgrade if so.
- `upgrade_custom_openwrt --wait` to wait for clients activity to stop before upgrading.
- `upgrade_custom_openwrt --check` to check for new versions but not upgrade the router.

**IT IS NOT RECOMMENDED** to schedule the script to be executed automatically, although the script is very careful and checks sha256sums before trying to upgrade. Don't blame me if something goes wrong with scripts that **YOU** run in your router!

Notes:
- if you fork this repository, the script will be adapted to look for upgrades in your repository.
- The text output of upgrade_custom_openwrt script will show both in terminal and system logs.



## About SSH Hardening

To enhance the security of SSH connections, this firmware includes a hardened SSH configuration. The configuration is derived from recommendations by [SSH-Audit](https://github.com/jtesta/ssh-audit) and the [BSI](https://www.bsi.bund.de/), it specifies strong key exchange algorithms, ciphers, message authentication codes (MACs), host key algorithms, and public key algorithms. This ensures that only secure and up-to-date algorithms are used for SSH communication.



## Contributing

Contributions to this project are welcome. If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.



## Acknowledgements

- The OpenWrt project for providing the foundation for this firmware build and support of [GL.iNet GL-MT6000](https://openwrt.org/toh/gl.inet/gl-mt6000) router.
- The community over at the [OpenWrt forum](https://forum.openwrt.org/t/mt6000-custom-build-with-luci-and-some-optimization-kernel-6-12-x/185241) for their valuable contributions and resources. 
- [pesa1234](https://github.com/pesa1234) for his [MT6000 custom builds](https://github.com/pesa1234/MT6000_cust_build).
- [Julius Bairaktaris](https://github.com/JuliusBairaktaris/Qualcommax_NSS_Builder) from whom I "borrowed" much of this project (his repository is about custom builds for Xiaomi AX3600).
## AI agent access (MCP + Codex skill)

[`plugins/flint-router`](plugins/flint-router) exposes this home router to local AI
clients through standard MCP over stdio. It provides `router_status` and
`router_exec` (full root command and filesystem access), plus a discoverable Codex
skill. The MCP process runs on the agent computer and connects to OpenWrt using
SSH keys. There is no extra listener, firewall opening, or router runtime package;
this firmware already includes OpenSSH, SFTP, and BusyBox `timeout`.

The personal `flint-router` Codex plugin bundles both tools and the skill. Once
installed, start a new Codex task and ask, for example, “check my home router” or
“inspect my Wi-Fi settings.” The connection is configured once per agent computer.
Other stdio MCP clients can use the same server.

### Connection setup on another computer

Requires OpenSSH, Python 3.11+, and [uv](https://docs.astral.sh/uv/). Generate a
separate key for each computer; never commit keys, passwords, or credentials:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/flint_router_agent -C flint-router-agent
ssh-copy-id -i ~/.ssh/flint_router_agent.pub root@192.168.1.1
```

Verify the router host fingerprint when first connecting. For unattended access,
use a key loaded in ssh-agent or a dedicated key protected by local filesystem
permissions. Save this as `~/.ssh/flint-router.conf` (mode 600):

```sshconfig
Host flint-router
    HostName 192.168.1.1
    User root
    IdentityFile ~/.ssh/flint_router_agent
    IdentitiesOnly yes
    BatchMode yes
    StrictHostKeyChecking yes
    ConnectTimeout 10
    ServerAliveInterval 10
    ServerAliveCountMax 2
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes
```

Verify with `ssh -F ~/.ssh/flint-router.conf flint-router 'ubus call system board'`.
For a different address, change `HostName`. The server accepts `FLINT_SSH_CONFIG`
for a different SSH configuration file. The host alias remains `flint-router`.
OpenWrt's `sysupgrade -l` must include `/root/.ssh/authorized_keys` and the SSH host
keys before upgrading with settings retained. A factory reset requires enrollment
again. No credentials are embedded in firmware.

### Direct MCP installation (without the packaged Codex plugin)

From this repository's root:

```sh
uv run --frozen --script plugins/flint-router/scripts/server.py </dev/null
codex mcp add flint-router -- uv run --frozen --script "$PWD/plugins/flint-router/scripts/server.py"
mkdir -p ~/.codex/skills
cp -R plugins/flint-router/skills/flint-router ~/.codex/skills/
```

This registers a global MCP and skill for Codex. Use either the packaged plugin
or direct registration to avoid duplicate tools. For other MCP clients, configure
command `uv` with arguments `run`, `--frozen`, `--script`, and the absolute path to
`server.py`. Set the client's tool timeout to 330 seconds if commands may use the
server's maximum 300-second timeout. The default command timeout is 60 seconds.
The lockfile pins the SDK and dependencies. Warm the uv cache before offline use.

`router_exec` accepts `command`, optional `stdin`, `timeout_seconds` (1–300), and
`output_bytes` (1024–131072 per output stream). Example: command
`cat > /tmp/example`, stdin `hello\n`. Read with `cat /tmp/example`. For real
configuration, back up first and use UCI or an atomic replacement preserving file
permissions. Inspect the returned exit code and truncation flags. Timeouts can
leave completed writes; inspect state before retrying. Detached processes can
outlive the timeout. Network changes should have a timed rollback and reconnect
check. Root access is intentionally unrestricted; clients retain their own tool
approval policies.

### Verification and removal

```sh
uv run --with mcp==1.29.1 python plugins/flint-router/scripts/check.py
# Also verify live root read/write using a temporary /tmp file, then remove it:
uv run --with mcp==1.29.1 python plugins/flint-router/scripts/check.py --live
```

The check covers protocol initialization, tool discovery, input rejection, live
status, file round trips, shell quoting, output limits, nonzero exits, and timeout.

Remove a packaged install with `codex plugin remove flint-router@personal`.
For direct installation, use `codex mcp remove flint-router` and remove the copied
skill directory. Revoke a computer's access by deleting its public-key line from
`/root/.ssh/authorized_keys` using another working login. Removing a client plugin
alone does not revoke its SSH key.

References: [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli),
[official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x).
