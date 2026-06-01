"""Samantha web control dashboard — served at http://localhost:7780."""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("samantha")

_DASHBOARD_PORT = int(os.getenv("SAMANTHA_DASHBOARD_PORT", "7780"))

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Samantha</title>
<style>
  :root {
    --bg: #1e1e2e;
    --surface: #2a2a3c;
    --surface2: #313145;
    --accent: #cba6f7;
    --green: #a6e3a1;
    --red: #f38ba8;
    --yellow: #f9e2af;
    --blue: #89b4fa;
    --text: #cdd6f4;
    --subtext: #a6adc8;
    --border: #45475a;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
  }
  .status-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    background: var(--red);
    flex-shrink: 0;
    transition: background 0.3s;
  }
  .status-dot.active {
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 4px var(--green); }
    50% { box-shadow: 0 0 12px var(--green); }
  }
  h1 { font-size: 20px; font-weight: 600; }
  .status-label {
    margin-left: auto;
    font-size: 12px;
    color: var(--subtext);
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--subtext);
    margin-bottom: 12px;
  }
  /* Voice toggle */
  .voice-section { margin-bottom: 28px; }
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
  }
  .toggle-label { font-size: 15px; font-weight: 500; }
  .toggle-sub { font-size: 12px; color: var(--subtext); margin-top: 2px; }
  .toggle {
    position: relative;
    width: 52px; height: 28px;
    flex-shrink: 0;
  }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .slider {
    position: absolute; inset: 0;
    background: var(--border);
    border-radius: 28px;
    cursor: pointer;
    transition: background 0.25s;
  }
  .slider::before {
    content: "";
    position: absolute;
    width: 22px; height: 22px;
    left: 3px; top: 3px;
    background: white;
    border-radius: 50%;
    transition: transform 0.25s;
  }
  input:checked + .slider { background: var(--accent); }
  input:checked + .slider::before { transform: translateX(24px); }
  /* Profile cards */
  .profiles-section { margin-bottom: 28px; }
  .profiles-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .profile-card {
    background: var(--surface2);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 16px 8px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    user-select: none;
  }
  .profile-card:hover { border-color: var(--accent); }
  .profile-card.active {
    border-color: var(--accent);
    background: rgba(203,166,247,0.12);
  }
  .profile-card.jarvis.active {
    border-color: var(--blue);
    background: rgba(137,180,250,0.12);
  }
  .profile-card.alfred.active {
    border-color: var(--yellow);
    background: rgba(249,226,175,0.12);
  }
  .profile-icon { font-size: 28px; margin-bottom: 6px; }
  .profile-name {
    font-size: 13px;
    font-weight: 600;
    text-transform: capitalize;
  }
  .profile-voice { font-size: 10px; color: var(--subtext); margin-top: 2px; }
  /* Wake word badge */
  .wake-section { }
  .wake-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: var(--subtext);
  }
  .wake-badge span { color: var(--text); font-weight: 500; }
  /* Toast */
  #toast {
    position: fixed;
    bottom: 24px; left: 50%;
    transform: translateX(-50%) translateY(60px);
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
    transition: transform 0.3s;
    pointer-events: none;
    white-space: nowrap;
  }
  #toast.show { transform: translateX(-50%) translateY(0); }
</style>
</head>
<body>
<div class="panel">
  <div class="header">
    <div class="status-dot" id="dot"></div>
    <h1>Samantha</h1>
    <div class="status-label" id="statusLabel">Offline</div>
  </div>

  <div class="voice-section">
    <div class="section-title">Voice Mode</div>
    <div class="toggle-row">
      <div>
        <div class="toggle-label">Listening</div>
        <div class="toggle-sub" id="toggleSub">Start voice mode</div>
      </div>
      <label class="toggle">
        <input type="checkbox" id="voiceToggle" onchange="onVoiceToggle(this)">
        <span class="slider"></span>
      </label>
    </div>
  </div>

  <div class="profiles-section">
    <div class="section-title">Profile</div>
    <div class="profiles-grid">
      <div class="profile-card samantha" id="card-samantha" onclick="setProfile('samantha')">
        <div class="profile-icon">🌸</div>
        <div class="profile-name">Samantha</div>
        <div class="profile-voice">af_aoede</div>
      </div>
      <div class="profile-card jarvis" id="card-jarvis" onclick="setProfile('jarvis')">
        <div class="profile-icon">🤖</div>
        <div class="profile-name">Jarvis</div>
        <div class="profile-voice">bm_lewis</div>
      </div>
      <div class="profile-card alfred" id="card-alfred" onclick="setProfile('alfred')">
        <div class="profile-icon">🎩</div>
        <div class="profile-name">Alfred</div>
        <div class="profile-voice">bm_george</div>
      </div>
    </div>
  </div>

  <div class="wake-section">
    <div class="section-title">Wake Word</div>
    <div class="wake-badge">🎙️ Say <span id="wakeWord">hey samantha</span> to activate</div>
  </div>
</div>

<div id="toast"></div>

<script>
const API = '';  // same origin

const WAKE_WORDS = {
  samantha: 'hey samantha',
  jarvis: 'hey jarvis',
  alfred: 'hey alfred',
};

async function fetchStatus() {
  try {
    const r = await fetch(API + '/api/status');
    if (!r.ok) return;
    const d = await r.json();

    const dot = document.getElementById('dot');
    const label = document.getElementById('statusLabel');
    const toggle = document.getElementById('voiceToggle');
    const sub = document.getElementById('toggleSub');
    const wake = document.getElementById('wakeWord');

    dot.className = 'status-dot' + (d.active ? ' active' : '');
    label.textContent = d.active ? 'Active' : 'Offline';
    toggle.checked = d.active;
    sub.textContent = d.active ? 'Listening for wake word' : 'Start voice mode';
    wake.textContent = WAKE_WORDS[d.profile] || ('hey ' + d.profile);

    document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('active'));
    const active = document.getElementById('card-' + d.profile);
    if (active) active.classList.add('active');
  } catch(e) {}
}

async function onVoiceToggle(el) {
  try {
    const r = await fetch(API + (el.checked ? '/api/start' : '/api/stop'), {method:'POST'});
    const d = await r.json();
    toast(d.message || (el.checked ? '🎧 Started' : '🛑 Stopped'));
    setTimeout(fetchStatus, 800);
  } catch(e) {
    el.checked = !el.checked;
    toast('❌ Could not reach Samantha');
  }
}

async function setProfile(name) {
  try {
    const r = await fetch(API + '/api/profile', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({profile: name}),
    });
    const d = await r.json();
    toast(d.message || '✅ Profile: ' + name);
    fetchStatus();
  } catch(e) {
    toast('❌ Could not switch profile');
  }
}

function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 2500);
}

fetchStatus();
setInterval(fetchStatus, 3000);
</script>
</body>
</html>
"""


def _write_config(key: str, value) -> None:
    from samantha.config.constants import CONFIG_FILE, SAMANTHA_DIR
    config: dict = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except Exception:
            config = {}
    config[key] = value
    SAMANTHA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


async def _start_voice():
    """Start voice mode programmatically (same logic as samantha_start tool)."""
    import samantha.core.state as state
    import samantha.audio.playback as playback
    import threading
    from samantha.config.constants import SAMANTHA_ACTIVE_FILE, SAMANTHA_DIR
    from samantha.injection.detection import kill_orphaned_processes, is_samantha_running_elsewhere
    from samantha.services.health import ensure_kokoro_running, ensure_whisper_running
    from samantha.core.loop import samantha_loop_thread
    import os

    kill_orphaned_processes()
    if (state._samantha_thread and state._samantha_thread.is_alive()) or is_samantha_running_elsewhere():
        return "Already running"

    if SAMANTHA_ACTIVE_FILE.exists():
        SAMANTHA_ACTIVE_FILE.unlink(missing_ok=True)

    SAMANTHA_DIR.mkdir(parents=True, exist_ok=True)
    SAMANTHA_ACTIVE_FILE.write_text(str(os.getpid()))

    kokoro_ok = await ensure_kokoro_running()
    whisper_ok = await ensure_whisper_running()

    if not kokoro_ok or not whisper_ok:
        SAMANTHA_ACTIVE_FILE.unlink(missing_ok=True)
        return "Service startup failed"

    state._thread_stop_flag = False
    state._thread_ready = threading.Event()
    state._samantha_thread = threading.Thread(target=samantha_loop_thread, daemon=True)
    state._samantha_thread.start()
    state._thread_ready.wait(timeout=30.0)
    return "Started"


async def _stop_voice():
    """Stop voice mode programmatically."""
    import signal, time, os
    import samantha.core.state as state
    import samantha.audio.playback as playback
    from samantha.config.constants import SAMANTHA_ACTIVE_FILE
    from samantha.injection.detection import kill_orphaned_processes

    if SAMANTHA_ACTIVE_FILE.exists():
        try:
            pid = int(SAMANTHA_ACTIVE_FILE.read_text().strip())
            if pid != os.getpid():
                try:
                    os.kill(pid, signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass
        except (ValueError, Exception):
            pass

    state._thread_stop_flag = True
    playback._tts_interrupt = True
    playback._tts_playing = False
    with playback._tts_queue_lock:
        playback._tts_text_queue.clear()

    if state._samantha_thread and state._samantha_thread.is_alive():
        state._samantha_thread.join(timeout=2.0)
        if not state._samantha_thread.is_alive():
            state._samantha_thread = None

    state._audio_stream = None
    SAMANTHA_ACTIVE_FILE.unlink(missing_ok=True)
    kill_orphaned_processes()
    return "Stopped"


async def run_dashboard():
    """Start the control dashboard HTTP server."""
    try:
        from aiohttp import web
    except ImportError:
        logger.error("aiohttp is required for the dashboard. Run: pip install aiohttp")
        return

    from samantha.config.constants import SAMANTHA_ACTIVE_FILE
    from samantha.config.settings import get_profile_name, get_wake_words
    from samantha.config.profiles import PROFILES

    async def handle_index(request):
        return web.Response(text=_HTML, content_type="text/html")

    async def handle_status(request):
        active = SAMANTHA_ACTIVE_FILE.exists()
        profile = get_profile_name()
        return web.json_response({
            "active": active,
            "profile": profile,
            "wake_words": get_wake_words()[:3],
        })

    async def handle_start(request):
        result = await _start_voice()
        return web.json_response({"message": f"🎧 {result}"})

    async def handle_stop(request):
        result = await _stop_voice()
        return web.json_response({"message": f"🛑 {result}"})

    async def handle_profile(request):
        try:
            body = await request.json()
            profile = body.get("profile", "").strip().lower()
        except Exception:
            return web.json_response({"error": "invalid JSON"}, status=400)

        if profile not in PROFILES:
            available = ", ".join(PROFILES.keys())
            return web.json_response(
                {"error": f"Unknown profile. Available: {available}"}, status=400
            )

        _write_config("profile", profile)
        p = PROFILES[profile]
        wake = p["wake_words"][1] if len(p["wake_words"]) > 1 else p["wake_words"][0]
        return web.json_response({
            "message": f"✅ Switched to {profile} — say \"{wake}\" to activate"
        })

    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/status", handle_status)
    app.router.add_post("/api/start", handle_start)
    app.router.add_post("/api/stop", handle_stop)
    app.router.add_post("/api/profile", handle_profile)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", _DASHBOARD_PORT)
    await site.start()
    logger.info("Samantha dashboard running at http://localhost:%d", _DASHBOARD_PORT)
    return runner
