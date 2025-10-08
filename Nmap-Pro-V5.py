#!/usr/bin/env python3
"""
Nmap-Pro V5 — Ultrasonic Advanced Edition
Developer: Vishal ❤️ Subhi
Purpose: Advanced ethical scanning & automation
"""

import asyncio
import subprocess
import sys
import shutil
import argparse
import signal
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template_string

# ------------------------------
# Configuration
# ------------------------------
RESULTS_DIR = Path("./results")
RESULTS_DIR.mkdir(exist_ok=True)

# HTML dashboard template
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Nmap-Pro V5 Dashboard</title>
<style>
body { background:#0d0d0d; color:#00ff00; font-family:monospace; }
h1 { text-align:center; }
#log { padding:10px; margin:10px; height:80vh; overflow:auto; border:1px solid #00ff00; }
</style>
</head>
<body>
<h1>🏵️💮 Vishal ❤️ Subhi 💮🏵️ Nmap-Pro V5 Dashboard</h1>
<div id="log"></div>
<script>
var evtSource = new EventSource("/stream");
evtSource.onmessage = function(e) {
    let log = document.getElementById("log");
    log.innerHTML += e.data + "<br>";
    log.scrollTop = log.scrollHeight;
}
</script>
</body>
</html>
"""

# ------------------------------
# Argument Parsing
# ------------------------------
parser = argparse.ArgumentParser(description="Nmap-Pro V5 — Ultrasonic Advanced Scanning")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i","--input", help="Input file with targets")
group.add_argument("-u","--url", help="Single target URL/IP")
parser.add_argument("--out", help="Output file for consolidated report", default=RESULTS_DIR/"nmap_pro_report.txt")
parser.add_argument("--profile", choices=["light","normal","deep"], default="normal")
parser.add_argument("--concurrency", type=int, default=5)
parser.add_argument("--timeout", type=int, default=60)
parser.add_argument("--auto", action="store_true", help="Enable ultrasonic auto mode")
parser.add_argument("--gui", action="store_true", help="Start browser GUI")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5000)

args = parser.parse_args()

# ------------------------------
# Flask App
# ------------------------------
app = Flask(__name__)
clients = []

@app.route("/")
def index():
    return render_template_string(_HTML_TEMPLATE)

@app.route("/stream")
def stream():
    async def event_stream():
        while True:
            if hasattr(app, "log_queue"):
                while not app.log_queue.empty():
                    yield f"data: {app.log_queue.get_nowait()}\n\n"
            await asyncio.sleep(0.1)
    return app.response_class(event_stream(), mimetype="text/event-stream")

# ------------------------------
# Logging
# ------------------------------
import queue
import threading
app.log_queue = queue.Queue()

def log(msg):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    app.log_queue.put(line)

# ------------------------------
# Ctrl+C Handler
# ------------------------------
stop_event = threading.Event()
def signal_handler(sig, frame):
    log("Scan interrupted by user. Saving results...")
    stop_event.set()
signal.signal(signal.SIGINT, signal_handler)

# ------------------------------
# Utilities
# ------------------------------
def load_targets(file):
    targets = set()
    with open(file,"r") as f:
        for line in f:
            line = line.strip()
            if line: targets.add(line)
    return list(targets)

async def nmap_scan(target, profile):
    scripts = "default,safe,http-headers,ssl-cert"
    if args.auto and profile=="deep":
        scripts += ",http-waf-detect,http-vuln*"
    cmd = ["nmap", "-Pn", "-sV", "--script", scripts, target]
    log(f"Running nmap on {target} ({scripts})")
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        log(f"Completed scan for {target}")
        return stdout.decode()
    except Exception as e:
        log(f"Error scanning {target}: {e}")
        return ""

# ------------------------------
# Main Scan Logic
# ------------------------------
async def main_scan():
    targets = []
    if args.input:
        targets = load_targets(args.input)
    elif args.url:
        targets = [args.url]

    live_targets = []
    log("Starting live host discovery...")
    for t in targets:
        if stop_event.is_set(): break
        result = subprocess.run(["ping","-c","1",t], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode==0:
            log(f"Alive: {t}")
            live_targets.append(t)
        else:
            log(f"Not alive / filtered: {t}")

    log(f"Found {len(live_targets)} live targets. Starting scans...")
    consolidated = []
    sem = asyncio.Semaphore(args.concurrency)
    async def scan_target(t):
        async with sem:
            if stop_event.is_set(): return
            result = await nmap_scan(t, args.profile)
            if "open" in result or args.profile=="deep":
                consolidated.append((t,result))
    await asyncio.gather(*(scan_target(t) for t in live_targets))

    # Save results
    with open(args.out,"w") as f:
        for t, r in consolidated:
            f.write(f"==== {t} ====\n{r}\n\n")
    log(f"Finished. Consolidated report: {args.out}")

# ------------------------------
# Run
# ------------------------------
def start_gui():
    import webbrowser
    threading.Timer(1, lambda: webbrowser.open(f"http://{args.host}:{args.port}")).start()
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)

if args.gui:
    gui_thread = threading.Thread(target=start_gui)
    gui_thread.start()

asyncio.run(main_scan())
