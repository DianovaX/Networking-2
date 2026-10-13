from flask import Flask, jsonify, render_template
from scapy.all import IP, ICMP, sr1
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
        return jsonify(run_latency_test())
    except (PermissionError, OSError, RuntimeError) as err:
        # Scapy needs admin/root to send raw ICMP packets (and Npcap on Windows)
        return jsonify({
            "success": False,
            "message": "Scapy could not send packets. Run as administrator/root "
                       "(and install Npcap on Windows). Details: " + str(err),
        })


if __name__ == "__main__":
    app.run(debug=True)