# GL-MT6000 custom OpenWrt firmware builder

This repository automates the process of building OpenWrt custom firmware images for **MY** Flint 2 (GL-MT6000) router, based on **MY PREFERENCES** and [pesa1234](https://github.com/pesa1234)'s work.

You should **not use** the firmwares released in this repository unless you have the same preferences/needs.
Instead, **make a fork and adapt to your needs**.

Read [this topic](https://forum.openwrt.org/t/mt6000-custom-build-with-luci-and-some-optimization-kernel-6-12-x/185241) in OpenWrt's forum to learn the details about pesa1234's customizations.

Compared to his custom firmware, this firmware adds:
- **WiFi UCODE scripts** (faster boot)
- **Wireguard VPN**
- **Policy Based Routing** (select what goes through VPN and what not)
- **AdBlock Fast** (ads and malware blocking at DNS level)
- **PPPoE-ready WAN defaults with IPv6 enabled** (pre-tagged VLAN 40, MTU 1492; set your ISP credentials after flashing)
- **Cake SQM preconfigured for gigabit fiber** (1492 MTU, PPPoE overhead, 950/950 Mbps)
- **Wake-on-LAN helper script** to power on the homelab server after SSHing into the router
- **Cloudflare DDNS template** that keeps your public DNS records updated directly from the router

And also:
- **REMOVED:** upnp, iptables, avahi, samba, usb storage and probably more stuff I forgot to mention (odhcp packages are back to support IPv6 on PPPoE).
- Added the needed packages to use QoS script [cake-wg-pbr](https://github.com/lynxthecat/cake-wg-pbr)
- Some compiler optimizations and build hardening options (cortex-a53+crc+crypto; LTO, MOLD, and more).
- SSH configuration with strong algorithms and key exchange methods. Check the content of [`ssh_hardening.config`](files/etc/ssh/sshd_config.d/ssh_hardening.conf) and [`sshd_config`](files/etc/ssh/sshd_config).
- Quality-of-life enhancements through UCI configuration. Check the content of [`999-QOL_config`](files/etc/uci-defaults/999-QOL_config).
- Some debug and kernel stuff removed.
- [`upgrade_custom_openwrt`](files/usr/bin/upgrade_custom_openwrt) script
- Pre-enabled [OpenWrt SQM](https://openwrt.org/docs/guide-user/network/traffic-shaping/sqm) with Cake tuned for PPPoE fiber connections.
- [`wake_homelab`](files/usr/bin/wake_homelab) helper that calls `etherwake` with your server MAC.
- [`020-ddns-cloudflare`](files/etc/uci-defaults/020-ddns-cloudflare) template for Cloudflare DNS updates (disabled until configured).

## Getting started after flashing

1. **Set PPPoE credentials and confirm IPv6 is live**
   - Log into LuCI at `http://192.168.8.1` (or whichever LAN address you use).
   - Navigate to: *Network → Interfaces → WAN* and fill in the username/password provided by your ISP. The WAN device is already tagged as **`wan.40`** so the fiber handoff on VLAN 40 syncs without extra changes.
   - Under *Network → Interfaces → WAN6* leave protocol on DHCPv6; the defaults in [`010-network-pppoe`](files/etc/uci-defaults/010-network-pppoe) request both an IPv4 address and a delegated IPv6 prefix. The LAN bridge advertises IPv6 using SLAAC + DHCPv6 so your Arch Linux desktop and Debian 12 homelab will both pick up global addresses automatically.
   - If your ISP expects a different VLAN or MTU, adjust **Device** and **MTU** in the WAN interface accordingly. The profile ships with VLAN **40** and MTU **1492** to match your fiber PPPoE service.
   - If your ISP hands out a different prefix length, adjust **IPv6 assignment length** on the LAN interface accordingly (default is `/64`).

2. **Verify Cake SQM**
   - Go to *Network → SQM QoS* and confirm the Cake instance is enabled on `pppoe-wan` with 950/950 Mbps limits and PPPoE overhead. Tweak the bandwidth values if your line rate differs.

3. **Wake your homelab on demand**
   - Edit [`/usr/bin/wake_homelab`](files/usr/bin/wake_homelab) to replace `TARGET_MAC` with the MAC address of your Debian server's onboard NIC. You can grab it with `ip link` on the server before it powers down.
   - From outside your network, SSH into the router (port 22 is already opened on the WAN) using your key and run `wake_homelab`. The script sends the magic packet over `br-lan`, so the server will boot even if everything else is asleep.

4. **Keep Cloudflare DNS records updated**
   - Create a Cloudflare API token with DNS edit permissions for the zone hosting your homelab domain.
   - Open `/etc/config/ddns` and replace every `CHANGE_ME` placeholder created by [`020-ddns-cloudflare`](files/etc/uci-defaults/020-ddns-cloudflare) with your real hostname and token. There are two entries: one for IPv4 and one for IPv6.
   - Flip **Enabled** to *on* for both services in LuCI (*Services → Dynamic DNS*) or by setting `option enabled '1'` for each section and running `service ddns restart`.
   - Once enabled, the router—not your Docker host—will push the current public IPv4/IPv6 to Cloudflare, keeping your domain reachable for port forwarding and Cloudflare Tunnel fallbacks.

5. **Build images the usual way**
   - GitHub Actions continues to work exactly like the upstream project; triggering a build via the `Build OpenWrt` workflow or running `./build.sh` locally still uses `mt6000.config`. No extra steps are required beyond committing your customisations.

Check the content of [`mt6000.config`](mt6000.config) for details.



## About upgrade_custom_openwrt script

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
