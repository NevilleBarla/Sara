# ============================================================
#  SARA -- modules/net_monitor.py
#  Detects internet connection and switches online/offline mode
# ============================================================

import socket
import threading
import time
import logging
from pathlib import Path

# Setup logging
LOG_PATH = Path(__file__).parent.parent / "data" / "logs" / "sara.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s"
)

# ── Constants ─────────────────────────────────────────────────
CHECK_INTERVAL  = 10          # seconds between each check
TEST_HOST       = "8.8.8.8"  # Google DNS (reliable ping target)
TEST_PORT       = 53          # DNS port
TIMEOUT         = 3           # seconds before giving up

# ── Internal state ────────────────────────────────────────────
_online         = False
_callbacks      = []          # functions to call when status changes
_monitor_thread = None
_running        = False


# ── Core check ───────────────────────────────────────────────
def is_online() -> bool:
    """Check internet right now. Returns True if connected."""
    try:
        socket.setdefaulttimeout(TIMEOUT)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
            (TEST_HOST, TEST_PORT)
        )
        return True
    except (socket.error, OSError):
        return False


# ── Callback system ──────────────────────────────────────────
def on_status_change(callback):
    """
    Register a function to call when internet status changes.
    Your callback will receive one argument: True (online) or False (offline).

    Example:
        def handle_change(online):
            if online:
                print("Back online!")
            else:
                print("Lost connection!")

        net_monitor.on_status_change(handle_change)
    """
    _callbacks.append(callback)


def _notify(status: bool):
    """Fire all registered callbacks with the new status."""
    for cb in _callbacks:
        try:
            cb(status)
        except Exception as e:
            logging.error(f"net_monitor callback error: {e}")


# ── Background monitor ────────────────────────────────────────
def _monitor_loop():
    """Runs in background thread. Checks connection every N seconds."""
    global _online

    while _running:
        current = is_online()

        if current != _online:           # Status changed!
            _online = current
            status_str = "ONLINE" if _online else "OFFLINE"
            logging.info(f"Network status changed --> {status_str}")
            print(f"  [NetMonitor] Status changed: {status_str}")
            _notify(_online)

        time.sleep(CHECK_INTERVAL)


def start():
    """Start the background network monitor thread."""
    global _online, _running, _monitor_thread

    _online  = is_online()               # Get initial status immediately
    _running = True

    _monitor_thread = threading.Thread(
        target=_monitor_loop,
        daemon=True,                     # Dies when main program exits
        name="NetMonitorThread"
    )
    _monitor_thread.start()

    status = "ONLINE" if _online else "OFFLINE"
    logging.info(f"NetMonitor started. Initial status: {status}")
    print(f"  [NetMonitor] Started. Currently: {status}")


def stop():
    """Stop the background monitor."""
    global _running
    _running = False
    logging.info("NetMonitor stopped.")
    print("  [NetMonitor] Stopped.")


def get_status() -> bool:
    """Return the last known connection status (no new check)."""
    return _online


def get_status_label() -> str:
    """Return human-readable status string."""
    return "Online" if _online else "Offline"


# ── Quick test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== SARA Net Monitor Test ===\n")

    def my_callback(online):
        if online:
            print("  --> SARA switching to ONLINE mode (GPT)")
        else:
            print("  --> SARA switching to OFFLINE mode (Ollama)")

    on_status_change(my_callback)
    start()

    print(f"\n  Current status : {get_status_label()}")
    print(f"  Raw bool value : {get_status()}")
    print("\n  Monitoring for 30 seconds...")
    print("  (Try turning off WiFi to test the callback!)\n")

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n  Interrupted by user.")

    stop()
    print("\n=== Test complete ===")
