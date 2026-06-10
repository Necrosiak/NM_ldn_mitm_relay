# NM-LanPlay — Desktop Client

GUI client for **NetworkMemories LAN Play**, pre-configured to connect to the NM relay server.

## For who?

| | NM-LanPlay (this) | ldn_mitm sysmodule |
|---|---|---|
| Switch non moddée (LAN mode games) | ✅ | ❌ |
| Ryujinx / Yuzu / Sudachi / Citron | ✅ | ❌ |
| Switch moddée CFW | ✅ (fallback) | ✅ **Recommended** |

**If you have a modded Switch, use the sysmodule instead — no PC needed at all.**

## Requirements

### Windows
- [Npcap](https://npcap.com/) — required by lan-play
- Run NM-LanPlay **as Administrator**
- Place `lan-play.exe` in `bin/` (from [switch-lan-play releases](https://github.com/spacemeowx2/switch-lan-play/releases))

### Linux / macOS
- `libpcap` installed
- Place `lan-play` binary in `bin/`

## Switch IP Configuration

Settings → Internet → Your network → Change Settings → IP Address Settings: Manual
- IP: `10.13.1.X` (unique per player)
- Subnet Mask: `255.255.0.0`
- Gateway: `10.13.37.1`

## Build from source

```bash
pip install pyinstaller
pyinstaller nm-lanplay.spec
```

## Credits
- [spacemeowx2/switch-lan-play](https://github.com/spacemeowx2/switch-lan-play) — Core protocol
- NetworkMemories — GUI & relay server
