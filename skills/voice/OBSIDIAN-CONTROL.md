---
name: obsidian-control
description: Obsidian control panel note for Samantha voice assistant. Copy this file into your Obsidian vault to get a one-click dashboard for turning voice mode on/off and switching between Samantha, Jarvis, and Alfred profiles.
---

# Samantha Control Panel

Copy this file into your Obsidian vault. Open it to control your voice assistant.

## Quick Start

1. Start the dashboard server (run once, leave it running):
   ```bash
   samantha-install dashboard
   ```

2. Open the control panel:
   [Open Samantha Control Panel](http://localhost:7780)

> Click the link above to open the dashboard in your browser. Use it to toggle voice mode and switch profiles.

---

## Controls

The dashboard at `http://localhost:7780` provides:

| Control | What it does |
|---------|-------------|
| **Listening toggle** | Start / stop voice mode |
| **Samantha** 🌸 | Switch to Samantha (warm, intimate — *af_aoede* voice) |
| **Jarvis** 🤖 | Switch to J.A.R.V.I.S. (dry wit, composed — *bm_lewis* voice) |
| **Alfred** 🎩 | Switch to Alfred (dignified butler — *bm_george* voice) |

Status updates every 3 seconds automatically.

---

## Wake Words

| Profile | Say to activate | Say to sleep |
|---------|----------------|-------------|
| Samantha | `hey samantha` | `samantha sleep` |
| Jarvis | `hey jarvis` | `jarvis sleep` |
| Alfred | `hey alfred` | `alfred sleep` |

---

## MCP Tools (for AI agents)

If you're using this via Claude Code or another MCP client:

```
samantha_start          — start voice mode
samantha_stop           — stop voice mode
samantha_speak "text"   — speak text via TTS
samantha_status         — check current status + profile
samantha_set_profile    — switch profile (samantha / jarvis / alfred)
```

---

## Installation

```bash
# Install Samantha
pip install git+https://github.com/goncaloneves/samantha.git

# Install voice services (Whisper + Kokoro)
samantha-install install

# Start the control dashboard
samantha-install dashboard

# Start the MCP server (for Claude Code / AI tools)
samantha
```

## Configuration

Edit `~/.samantha/config.json` to set your default profile and other preferences:

```json
{
  "profile": "samantha",
  "voice": "af_aoede",
  "wake_words": ["hey samantha", "samantha"],
  "min_audio_energy": 1500
}
```
