# NM_ldn_mitm_relay

> **Nintendo Switch LAN Play — Direct Relay without PC**  
> A fork of [ldn_mitm](https://github.com/spacemeowx2/ldn_mitm) with an integrated SLP relay client.  
> Part of the [NetworkMemories](https://networkmemories.com) project.

## What is this?

Standard Switch LAN play requires a PC client. This removes it entirely:
Switch (this sysmodule) → Internet → Relay server

## Repository Structure
NM_ldn_mitm_relay/
├── client/     # Modified ldn_mitm sysmodule
├── server/     # Self-hosted relay (Docker)
└── sd_card/    # Files to copy to SD card

## Quick Start — Server

```bash
cd server && docker compose up -d
```

Ports: 11451 UDP+TCP (Switch), 27312 TCP (PSP), 27313 UDP+TCP (PSP)

## Quick Start — Switch

1. Copy `sd_card/` to root of SD card
2. Edit `atmosphere/config/ldn_mitm_relay.ini`
3. Enable ldn_mitm via ldnmitm_config overlay (Y + X LOGIN)
4. Launch any game with LAN mode

## Credits

- spacemeowx2 — ldn_mitm & switch-lan-play
- DefenderOfHyrule — ldn_mitm maintenance  
- Atmosphere-NX — CFW & libs
- WerWolv — libtesla & ldnmitm_config
- Souler — ppsspp-adhoc Docker
- Kethen — aemu_postoffice PSP relay
- Nekyron / NetworkMemories — integration & deployment

## Public Server

`193.70.35.100:11451` — NetworkMemories public relay, no account needed.

## License

GPLv2 — based on ldn_mitm
