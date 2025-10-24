# TODO: Main Branch Workflow Updates

This PR fixes the dev branch workflow. The main branch also needs similar updates.

## Current Issue on Main Branch

The main branch workflow currently:
- Triggers on BOTH `main` AND `dev` branches (lines 11-12)
- Uses generic "Main Repository" label in release messages
- Uses `--latest` flag (which is correct for stable releases)

## Required Changes for Main Branch

Apply these changes to `.github/workflows/build-openwrt.yaml` on the **main** branch:

### 1. Remove `dev` from trigger branches (lines 10-12)

**Current:**
```yaml
  push:
    branches:
      - main
      - dev
```

**Should be:**
```yaml
  push:
    branches:
      - main
```

### 2. Update release message to "Stable Release" (line 109)

**Current:**
```yaml
--notes "### 🔄 Main Repository
```

**Should be:**
```yaml
--notes "### 🔄 Stable Release
```

### 3. Update release title (line 121)

**Current:**
```yaml
--title "OpenWrt Custom Release for Flint 2 (${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE})"
```

**Should be:**
```yaml
--title "OpenWrt Stable Release for Flint 2 (${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE})"
```

**NOTE:** Keep the `--latest` flag on main branch - only dev builds should use `--prerelease`.

## Complete Diff for Main Branch

```diff
@@ -9,7 +9,6 @@ on:
   push:
     branches:
       - main
-      - dev
   schedule:
     - cron: "38 1 * * *"

@@ -107,7 +106,7 @@ jobs:
         run: |
           RELEASE_DATE=$(date +%F)
           gh release delete "${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE}" --cleanup-tag -y --repo "${{ github.repository }}" ||:
-          gh release create "${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE}" --repo "${{ github.repository }}" --latest --notes "### 🔄 Main Repository
+          gh release create "${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE}" --repo "${{ github.repository }}" --latest --notes "### 🔄 Stable Release
           - **Repository:** [${{ env.REMOTE_REPOSITORY }}](https://github.com/${{ env.REMOTE_REPOSITORY }})
           - **Branch:** ${{ needs.check_commits.outputs.remote_branch }}
           - **Commit:** ${{ needs.check_commits.outputs.latest_commit_sha }}
@@ -119,7 +118,7 @@ jobs:
           - **Wireguard VPN**
           - **Policy Based Routing**
           - **Ad Block Fast**
-          - **REMOVED:** odhcp, upnp, iptables, avahi, samba, usb storage..." --title "OpenWrt Custom Release for Flint 2 (${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE})" firmware/*
+          - **REMOVED:** odhcp, upnp, iptables, avahi, samba, usb storage..." --title "OpenWrt Stable Release for Flint 2 (${{ needs.check_commits.outputs.release_prefix }}-${RELEASE_DATE})" firmware/*
```

## Summary

After both branches are updated:
- ✅ Dev branch workflow triggers only on `dev` branch, creates prereleases labeled "Dev Build"
- 🔲 Main branch workflow triggers only on `main` branch, creates latest releases labeled "Stable Release"
- ✅ Users will only see dev builds in the dev branch releases
- 🔲 Users will only see stable builds in the main branch releases

## How to Apply

Create a PR or direct commit to the main branch with these changes.
