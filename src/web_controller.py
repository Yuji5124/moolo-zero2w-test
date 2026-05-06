"""Web controller for Moolo - Flask-based smartphone control interface."""

import signal
import socket
import sys
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request

# Ensure src/ is in sys.path so motor_driver can import config
sys.path.insert(0, str(Path(__file__).parent))
from motor_driver import MotorDriver  # noqa: E402

MAX_SPEED = 0.5
WATCHDOG_TIMEOUT = 0.5  # seconds; stop if no command received
DRIVE_INTERVAL_MS = 200  # JS resends drive command every 200 ms

app = Flask(__name__)
motor = MotorDriver()

_lock = threading.Lock()
_last_command_time = time.monotonic()
_current_direction = "stop"
_current_speed = 0.2
_watchdog_running = True


# ---------------------------------------------------------------------------
# Watchdog thread – stops motors when client goes silent
# ---------------------------------------------------------------------------

def _watchdog_loop() -> None:
    while _watchdog_running:
        time.sleep(0.05)
        with _lock:
            age = time.monotonic() - _last_command_time
        if age > WATCHDOG_TIMEOUT:
            motor.stop()


_watchdog_thread = threading.Thread(target=_watchdog_loop, daemon=True)


# ---------------------------------------------------------------------------
# Signal handling
# ---------------------------------------------------------------------------

def _shutdown(signum=None, frame=None) -> None:
    global _watchdog_running
    _watchdog_running = False
    motor.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp_speed(value: object) -> float:
    try:
        speed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        speed = 0.2
    return max(0.0, min(MAX_SPEED, speed))


def _get_local_ips() -> list:
    ips: set = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    if not ips:
        # Fallback: probe an unreachable address to discover the outbound interface
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0)
                s.connect(("10.254.254.254", 1))
                ips.add(s.getsockname()[0])
        except Exception:
            pass
    return sorted(ips)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return _HTML_PAGE


@app.route("/api/drive", methods=["POST"])
def api_drive():
    global _last_command_time, _current_direction, _current_speed
    data = request.get_json(silent=True) or {}
    direction = str(data.get("direction", "stop"))
    speed = _clamp_speed(data.get("speed", 0.2))

    with _lock:
        _last_command_time = time.monotonic()
        _current_direction = direction
        _current_speed = speed

    try:
        if direction == "forward":
            motor.forward(speed)
        elif direction == "backward":
            motor.backward(speed)
        elif direction == "left":
            motor.turn_left(speed)
        elif direction == "right":
            motor.turn_right(speed)
        else:
            motor.stop()
    except Exception:
        motor.stop()
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok", "direction": direction, "speed": round(speed, 3)})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    global _last_command_time, _current_direction
    with _lock:
        _last_command_time = time.monotonic()
        _current_direction = "stop"
    motor.stop()
    return jsonify({"status": "ok"})


@app.route("/api/status", methods=["GET"])
def api_status():
    with _lock:
        return jsonify(
            {
                "direction": _current_direction,
                "speed": round(_current_speed, 3),
            }
        )


# ---------------------------------------------------------------------------
# Embedded HTML UI
# ---------------------------------------------------------------------------

_HTML_PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>Moolo Controller</title>
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      touch-action: none;
      user-select: none;
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
    }
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
    }
    body {
      padding: 20px 16px 28px;
      background: #0d1b2a;
      color: #e0e0e0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
    }
    h1 {
      margin: 0;
      font-size: 1.7rem;
      letter-spacing: 0.15em;
      color: #4fc3f7;
    }
    #status {
      font-size: 0.85rem;
      color: #90a4ae;
      min-height: 1.2em;
    }
    /* Speed slider – override touch-action so it remains draggable */
    .speed-wrap {
      width: 100%;
      max-width: 320px;
    }
    .speed-label {
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
      font-size: 0.9rem;
    }
    #speed-slider {
      touch-action: pan-x;
      width: 100%;
      accent-color: #4fc3f7;
      cursor: pointer;
    }
    /* D-pad grid */
    .dpad {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
      grid-template-areas:
        ".   fwd  ."
        "lft stp  rgt"
        ".   bwd  .";
      gap: 10px;
      width: 100%;
      max-width: 320px;
    }
    .btn {
      background: #1e3a5f;
      border: 2px solid #4fc3f7;
      border-radius: 14px;
      color: #e0e0e0;
      font-size: 2.4rem;
      padding: 22px 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.07s, color 0.07s;
    }
    .btn.pressed {
      background: #4fc3f7;
      color: #0d1b2a;
      border-color: #81d4fa;
    }
    #btn-fwd { grid-area: fwd; }
    #btn-bwd { grid-area: bwd; }
    #btn-lft { grid-area: lft; }
    #btn-rgt { grid-area: rgt; }
    #btn-stp {
      grid-area: stp;
      background: #7b1516;
      border-color: #ef5350;
      color: #fff;
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: 0.06em;
    }
    #btn-stp.pressed {
      background: #ef5350;
      color: #fff;
      border-color: #ff8a80;
    }
  </style>
</head>
<body>
  <h1>MOOLO</h1>
  <div id="status">待機中</div>

  <div class="speed-wrap">
    <div class="speed-label">
      <span>速度</span>
      <span id="speed-disp">0.20</span>
    </div>
    <input id="speed-slider" type="range" min="0" max="50" value="20" step="1">
  </div>

  <div class="dpad">
    <button class="btn" id="btn-fwd">&#x25B2;</button>
    <button class="btn" id="btn-lft">&#x25C4;</button>
    <button class="btn" id="btn-stp">STOP</button>
    <button class="btn" id="btn-rgt">&#x25BA;</button>
    <button class="btn" id="btn-bwd">&#x25BC;</button>
  </div>

  <script>
    'use strict';

    const statusEl   = document.getElementById('status');
    const speedSlider = document.getElementById('speed-slider');
    const speedDisp  = document.getElementById('speed-disp');

    speedSlider.addEventListener('input', () => {
      speedDisp.textContent = getSpeed().toFixed(2);
    });

    function getSpeed() {
      return speedSlider.value / 100;
    }

    let driveInterval = null;
    let activeBtn = null;

    function post(url, body) {
      return fetch(url, {
        method: 'POST',
        headers: body ? {'Content-Type': 'application/json'} : {},
        body: body ? JSON.stringify(body) : undefined,
        keepalive: true,
      }).catch(() => {});
    }

    function sendDrive(direction) {
      post('/api/drive', {direction, speed: getSpeed()})
        .then(r => r && r.json())
        .then(d => { if (d) statusEl.textContent = d.direction; })
        .catch(() => { statusEl.textContent = '接続エラー'; });
    }

    function sendStop() {
      post('/api/stop');
      statusEl.textContent = '停止';
    }

    function startDrive(direction, btn) {
      if (activeBtn === btn) return;
      endDrive();
      activeBtn = btn;
      btn.classList.add('pressed');
      sendDrive(direction);
      driveInterval = setInterval(() => sendDrive(direction), 200);
    }

    function endDrive() {
      if (driveInterval !== null) {
        clearInterval(driveInterval);
        driveInterval = null;
      }
      if (activeBtn !== null) {
        activeBtn.classList.remove('pressed');
        activeBtn = null;
      }
      sendStop();
    }

    function bindDriveBtn(id, direction) {
      const btn = document.getElementById(id);
      btn.addEventListener('touchstart',  e => { e.preventDefault(); startDrive(direction, btn); }, {passive: false});
      btn.addEventListener('touchend',    e => { e.preventDefault(); endDrive(); }, {passive: false});
      btn.addEventListener('touchcancel', e => { e.preventDefault(); endDrive(); }, {passive: false});
      btn.addEventListener('mousedown', () => startDrive(direction, btn));
      btn.addEventListener('mouseup',   () => endDrive());
      btn.addEventListener('mouseleave',() => { if (activeBtn === btn) endDrive(); });
    }

    bindDriveBtn('btn-fwd', 'forward');
    bindDriveBtn('btn-bwd', 'backward');
    bindDriveBtn('btn-lft', 'left');
    bindDriveBtn('btn-rgt', 'right');

    // STOP button: immediate stop on any press, no hold needed
    const stopBtn = document.getElementById('btn-stp');
    function onStopPress(e) { e.preventDefault(); stopBtn.classList.add('pressed'); endDrive(); }
    function onStopRelease(e) { e.preventDefault(); stopBtn.classList.remove('pressed'); }
    stopBtn.addEventListener('touchstart',  onStopPress,   {passive: false});
    stopBtn.addEventListener('touchend',    onStopRelease, {passive: false});
    stopBtn.addEventListener('touchcancel', onStopRelease, {passive: false});
    stopBtn.addEventListener('mousedown', () => { stopBtn.classList.add('pressed'); endDrive(); });
    stopBtn.addEventListener('mouseup',   () => stopBtn.classList.remove('pressed'));
    stopBtn.addEventListener('mouseleave',() => stopBtn.classList.remove('pressed'));

    // Safety: stop when page goes hidden or is closed
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        endDrive();
        navigator.sendBeacon('/api/stop');
      }
    });
    ['beforeunload', 'pagehide'].forEach(ev => {
      window.addEventListener(ev, () => { navigator.sendBeacon('/api/stop'); });
    });
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _watchdog_thread.start()

    ips = _get_local_ips()
    print()
    print("=" * 44)
    print("  Moolo Web Controller")
    print("=" * 44)
    if ips:
        for ip in ips:
            print(f"  http://{ip}:8080")
    else:
        print("  http://<Pi の IP アドレス>:8080")
        print("  Pi 上で  hostname -I  を実行して IP を確認してください")
    print()
    print("  スマホと Pi を同じ Wi-Fi に接続してください")
    print("  Ctrl+C で停止します")
    print("=" * 44)
    print()

    try:
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False, threaded=True)
    except Exception:
        motor.stop()
        raise
    finally:
        motor.stop()
