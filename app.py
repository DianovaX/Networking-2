from flask import Flask, jsonify, render_template
from scapy.all import IP, ICMP, sr1
from datetime import datetime
import json
import os
import time

# index.html sits next to app.py, style.css is inside the "style" folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=os.path.join(BASE_DIR, "style"),
    static_url_path="/static",
)

TARGET = "google.com"
PING_COUNT = 5

# Every scan attempt is saved in this file, so the record stays after a restart
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")


def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []  # no file yet (or unreadable): start with an empty record


def save_attempt(data):
    history = load_history()
    history.append({
        "attempt": len(history) + 1,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target": TARGET,
        "success": data["success"],
        "replies": data.get("replies", 0),
        "sent": PING_COUNT,
        "average_ms": data.get("average_ms"),
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def run_latency_test():
    results = []

    # Same logic as latency_test.py in the module
    for i in range(PING_COUNT):
        start = time.time()
        reply = sr1(IP(dst=TARGET) / ICMP(), timeout=1, verbose=0)
        end = time.time()
        if reply:
            results.append(end - start)

    if not results:
        return {"success": False, "message": "No response received"}

    return {
        "success": True,
        "target": TARGET,
        "sent": PING_COUNT,
        "replies": len(results),
        # module prints seconds; shown here in milliseconds
        "average_ms": round(sum(results) / len(results) * 1000, 2),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan")
def scan():
    try:
        data = run_latency_test()
    except (PermissionError, OSError, RuntimeError) as err:
        # Scapy needs admin/root to send raw ICMP packets (and Npcap on Windows)
        return jsonify({
            "success": False,
            "message": "Scapy could not send packets. Run as administrator/root "
                       "(and install Npcap on Windows). Details: " + str(err),
        })

    save_attempt(data)  # record this attempt, even if there was no response
    return jsonify(data)


@app.route("/history")
def history():
    # newest attempt first
    return jsonify(list(reversed(load_history())))


if __name__ == "__main__":
    app.run(debug=True)