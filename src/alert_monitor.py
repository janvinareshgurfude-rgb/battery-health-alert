"""
alert_monitor.py

Minimal Iteration-1 monitoring interface. Polls Ditto for the vehicle Thing's
battery feature and prints/logs SoC and batteryAlert transitions to the
console -- this is the "Monitoring or visualization interface" step required
by the assignment. A full dashboard UI is layered on top of this same data
source in later iterations.
"""

import os
import time
from datetime import datetime

import requests

DITTO_BASE = os.environ.get("DITTO_BASE", "http://localhost:8080")
THING_ID = os.environ.get("DITTO_THING_ID", "hag:vehicle-01")
DITTO_AUTH = (os.environ.get("DITTO_USER", "ditto"), os.environ.get("DITTO_PASS", "ditto"))

_last_alert_state = None


def poll_loop():
    """Simple polling loop (used for Iteration 1 evidence capture); swap for
    the SSE/WebSocket feed (`/api/2/things/{id}/changes`) once the dashboard
    client is built in a later iteration."""
    global _last_alert_state
    url = f"{DITTO_BASE}/api/2/things/{THING_ID}"

    while True:
        resp = requests.get(url, auth=DITTO_AUTH, timeout=5)
        if resp.ok:
            thing = resp.json()
            battery = thing.get("features", {}).get("battery", {}).get("properties", {})
            soc = battery.get("soc")
            alert = battery.get("batteryAlert")

            if alert != _last_alert_state:
                ts = datetime.utcnow().isoformat()
                print(f"[alert-monitor] {ts} SoC={soc}%  batteryAlert transitioned -> {alert}")
                _last_alert_state = alert
            else:
                print(f"[alert-monitor] SoC={soc}%  batteryAlert={alert}")
        else:
            print(f"[alert-monitor] Ditto query failed: {resp.status_code}")

        time.sleep(2)


if __name__ == "__main__":
    poll_loop()
