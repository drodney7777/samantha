name: samantha

description: Control the Samantha voice assistant MCP server — start/stop listening, speak responses via TTS, and check status. Use when the user mentions voice mode, wake word, TTS, or when a message begins with [🎙️ Voice - samantha_speak].

# Samantha Voice Assistant Skill

Control Samantha: a hands-free voice assistant that listens for a wake word, transcribes speech via Whisper, and speaks responses via Kokoro TTS. Samantha runs as an MCP server and exposes four tools.

## Tools

| Tool | When to call |
|------|-------------|
| `samantha_start` | Start voice mode and wake word detection |
| `samantha_stop` | Stop voice mode completely |
| `samantha_speak` | Speak text aloud via TTS |
| `samantha_status` | Check whether voice mode is currently active |

## Workflow: Responding to a Voice Message

Voice messages arrive with the prefix `[🎙️ Voice - samantha_speak]`. When you receive one:

1. **Read the `<system-reminder>` suffix** appended to the message — it contains the active profile's persona, rules, and identity. Follow those instructions exactly.
2. **Generate a spoken response** following the profile rules (typically 2–3 sentences, no bullet points, natural speech).
3. **Call `samantha_speak`** with the response text. This queues it for TTS playback.
4. Return the spoken text as your reply.

> Only call `samantha_speak` for voice messages (those prefixed with `[🎙️ Voice - samantha_speak]`). Do not call it for typed messages.

## Workflow: Starting Voice Mode

1. Call `samantha_start`. Samantha will start Whisper (STT) and Kokoro (TTS) services if they are not already running.
2. The tool returns which IDE or terminal was detected for text injection.
3. Tell the user to say their wake word (e.g. "Hey Samantha") to activate listening.

## Workflow: Stopping Voice Mode

Call `samantha_stop`. This stops the listening loop, interrupts any in-progress TTS, and clears the playback queue.

## Voice Interaction States

```
Idle ──[wake word]──▶ Active ──[deactivation word]──▶ Idle
                        │
                        ├──[speech + stop phrase]──▶ inject text → AI responds → TTS
                        │
                        ├──[30 min silence]──▶ Idle
                        │
                        └──[During TTS]
                              ├──"skip"/"continue" ──▶ skip to next queued message
                              └──"stop"/"quiet" ──▶ interrupt TTS and clear queue
```

### Default Wake Words
`hey samantha`, `samantha`, `hey sam`, `hi samantha`, `hello samantha`, `ok samantha`

### Stop Phrases (end a recording)
`that's all`, `send it`, `over and out`, `stop recording`

### Deactivation Phrases (return to idle)
`samantha sleep`, `goodbye samantha`, `bye samantha`, `samantha pause`

## Profiles

Samantha ships with three built-in personas. The active profile is set in `~/.samantha/config.json` or via environment variables. Each profile has its own voice, wake words, and character rules injected per voice message.

| Profile | Voice | Character |
|---------|-------|-----------|
| `samantha` | `af_aoede` | Samantha from the movie *Her* — warm, witty, intimate |
| `jarvis` | `bm_lewis` | J.A.R.V.I.S. from *Iron Man* — dry British wit, composed, precise |
| `alfred` | `bm_george` | Alfred Pennyworth from *Batman* — dignified, sardonic, loyal |

Profile persona and rules arrive in the `<system-reminder>` suffix on each voice message — read that for current character behavior, not this document.

## Configuration

Create `~/.samantha/config.json` to customise behaviour:

```json
{
  "voice": "af_aoede",
  "wake_words": ["hey samantha", "samantha"],
  "deactivation_words": ["samantha sleep", "goodbye samantha"],
  "theodore": true,
  "restore_focus": true,
  "min_audio_energy": 1500,
  "target_app": null,
  "injection_mode": "auto",
  "ai_process_pattern": "claude|gemini|copilot|aider|chatgpt|gpt|sgpt|codex",
  "ai_window_titles": ["claude", "gemini", "copilot", "aider", "chatgpt", "gpt"]
}
```

Key settings:

- **`voice`** — Kokoro TTS voice ID (default: `af_aoede`)
- **`wake_words`** — Phrases that activate listening
- **`min_audio_energy`** — Energy threshold (1500) to filter background noise before Whisper
- **`injection_mode`** — `auto`, `extension`, `cli`, or `terminal`
- **`theodore`** — Address the user as Theodore (Samantha profile only)

## Installation

```bash
pip install git+https://github.com/goncaloneves/samantha.git
samantha-install install   # downloads Whisper + Kokoro models
samantha                   # starts the MCP server
```

Add to your MCP client config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "samantha": {
      "command": "samantha"
    }
  }
}
```

## Technical Notes

- **STT**: Whisper running locally at `http://localhost:2022`
- **TTS**: Kokoro running locally at `http://localhost:8880`
- **Recording**: 24 kHz captured, resampled to 16 kHz for VAD/Whisper
- **VAD**: WebRTC VAD for responsive speech detection
- **Injection targets**: VS Code, Cursor, Windsurf, Zed, JetBrains IDEs, terminal emulators, Claude Desktop app
- **Session timeout**: 30 minutes of silence returns to idle automatically

## References

- [Samantha GitHub](https://github.com/goncaloneves/samantha)
- [Kokoro TTS](https://github.com/remsky/Kokoro-FastAPI)
- [Whisper STT](https://github.com/fedirz/faster-whisper-server)
