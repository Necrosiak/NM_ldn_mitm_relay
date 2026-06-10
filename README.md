# NM_ldn_mitm_relay

> **Nintendo Switch LAN Play — Direct Relay without PC**
> A fork of [ldn_mitm](https://github.com/spacemeowx2/ldn_mitm) with an integrated SLP relay client.
> Part of the [NetworkMemories](https://networkmemories.com) project.

## What is this?

Standard Switch LAN play requires a PC client. This removes it entirely:
Switch (this sysmodule) → Internet → Relay server

## Repository Structure
NM_ldn_mitm_relay/
├── client/          # Modified ldn_mitm sysmodule (Switch CFW — no PC needed)
├── server/          # Self-hosted relay server (Docker)
├── desktop-client/  # GUI client (emulators & unmodded Switch)
└── sd_card/         # Files to copy to SD card

## Quick Start — Server

```bash
cd server && docker compose up -d
```

Port: `11451 UDP+TCP` (Switch LAN relay)

## Quick Start — Switch (CFW)

1. Copy `sd_card/` to root of SD card
2. Edit `atmosphere/config/ldn_mitm_relay.ini` (optional — defaults to NM public server)
3. Enable ldn_mitm via ldnmitm_config overlay (Y to enable, X to toggle LOGIN)
4. Launch any game in LAN mode

## Quick Start — Emulators & Unmodded Switch

Use the **NM-LanPlay** desktop client (Windows/Linux/macOS):

1. Go to `desktop-client/`
2. Install [Npcap](https://npcap.com/) (Windows only)
3. Run `python nm-lanplay.py` (as Administrator on Windows)
4. Click **SE CONNECTER**

`lan-play` binaries are included in `desktop-client/bin/`.

## Compatibility

| Platform | Solution | PC required |
|---|---|---|
| Switch CFW (Atmosphere) | Sysmodule client/ | No |
| Switch unmodded (LAN mode games) | NM-LanPlay desktop-client/ | Yes |
| Ryujinx / Yuzu / Sudachi / Citron | NM-LanPlay desktop-client/ | Yes |

## Public Relay

NetworkMemories public relay: `193.70.35.100:11451` — no account needed.

## Credits

| Who | What |
|-----|------|
| [spacemeowx2](https://github.com/spacemeowx2) | Original ldn_mitm & switch-lan-play protocol |
| [DefenderOfHyrule](https://github.com/DefenderOfHyrule) | ldn_mitm maintenance |
| [Atmosphere-NX](https://github.com/Atmosphere-NX) | Atmosphere CFW & libs |
| [WerWolv](https://github.com/WerWolv) | libtesla & ldnmitm_config overlay |
| **Nekyron / NetworkMemories** | Integration, relay, deployment & GUI |

## License

GPLv2 — based on ldn_mitm
