#!/usr/bin/env python3
"""
Nmap-Pro V7 — Ultrasonic Autonomous Edition
Developer: Vishal ❤️ Subhi
Features: Auto-Installer, Searchsploit, Nuclei, Nikto, Stealth
"""

import asyncio, subprocess, sys, os, json, re, threading, queue, webbrowser
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string

# --- Configuration ---
BASE_DIR = Path("./ultrasonic_vault")
BASE_DIR.mkdir(exist_ok=True)
LOG_QUEUE = queue.Queue()

# --- Auto-Installer & Dependency Checker ---
def setup_environment():
    tools = {
        "nmap": "sudo apt-get install nmap -y",
        "nuclei": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        "searchsploit": "sudo apt-get install exploitdb -y",
        "nikto": "sudo apt-get install nikto -y"
    }
    
    print("[*] Initializing Ultrasonic Environment...")
    for tool, install_cmd in tools.items():
        if not shutil.which(tool):
            print(f"[!] {tool} not found. Attempting autonomous installation...")
            try:
                subprocess.run(install_cmd, shell=True, check=True)
            except Exception as e:
                print(f"[X] Failed to install {tool}. Please install it manually.")
    
    # Update Searchsploit DB
    print("[*] Syncing Exploit Database...")
    subprocess.run(["searchsploit", "-u"], capture_output=True)

import shutil

# --- Matrix UI Template ---
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Nmap-Pro V7: ULTRASONIC</title>
    <style>
        body { background: #000; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; }
        .grid { display: grid; grid-template-columns: 2fr 1fr; height: 100vh; }
        #terminal { padding: 20px; overflow-y: auto; border-right: 1px solid #00ff41; background: rgba(0,10,0,0.95); }
        #sidebar { padding: 20px; background: #050505; overflow-y: auto; }
        .log-entry { margin-bottom: 5px; font-size: 0.9em; border-left: 2px solid #004400; padding-left: 10px; }
        .vuln-card { background: #1a0000; border: 1px solid #ff0000; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
        .critical { color: #ff0000; text-transform: uppercase; font-weight: bold; animation: blink 1s infinite; }
        .high { color: #ff8c00; }
        .tech-tag { background: #004400; color: #00ff41; padding: 2px 5px; border-radius: 3px; font-size: 0.8em; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
        header { background: #00ff41; color: #000; padding: 5px 20px; font-weight: bold; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
    <header>
        <span>VISHAL ❤️ SUBHI | ULTRASONIC V7</span>
        <span id="status">SYSTEM ACTIVE</span>
    </header>
    <div class="grid">
        <div id="terminal"></div>
        <div id="sidebar">
            <h3 style="color: #ff0000; border-bottom: 1px solid #ff0000;">CRITICAL VULNS</h3>
            <div id="vulns"></div>
        </div>
    </div>
    <script>
        var evtSource = new EventSource("/stream");
        evtSource.onmessage = function(e) {
            let data = JSON.parse(e.data);
            let container = data.type === "VULN" ? document.getElementById("vulns") : document.getElementById("terminal");
            let div = document.createElement("div");
            
            if(data.type === "VULN") {
                div.className = "vuln-card";
                div.innerHTML = `<span class="${data.level.toLowerCase()}">[${data.level}]</span><br>${data.msg}`;
            } else {
                div.className = "log-entry";
                div.innerHTML = `[${data.time}] ${data.msg}`;
            }
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

# --- Core Engine ---
app = Flask(__name__)

def push_log(msg, level="INFO", type="LOG"):
    data = {"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level, "type": type}
    LOG_QUEUE.put(json.dumps(data))

async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    return stdout.decode()

async def ultrasonic_scan(target):
    push_log(f"Starting Ultrasonic Recon on: {target}", "INIT")

    # 1. Tech Discovery (WhatWeb Logic)
    push_log(f"Fingerprinting tech stack for {target}...", "TECH")
    tech_res = await run_cmd(["whatweb", target, "--color=never"])
    push_log(f"Tech Found: {tech_res[:200]}...", "INFO")

    # 2. Stealth Nmap with Service Versioning
    push_log(f"Injected Stealth Nmap on {target}", "STEALTH")
    nmap_res = await run_cmd(["nmap", "-Pn", "-sV", "-T2", "-f", "--data-length", "32", target])
    
    # Extract versions for Searchsploit
    versions = re.findall(r"open\s+(\S+)\s+(.+)", nmap_res)
    for port_info, version in versions:
        push_log(f"Found Service: {version} on {port_info}", "SERVICE")
        
        # 3. Searchsploit Integration
        exploit_json = await run_cmd(["searchsploit", version, "--json"])
        try:
            exp_data = json.loads(exploit_json)
            if exp_data.get("Results"):
                for e in exp_data["Results"]:
                    push_log(f"EXPLOIT FOUND: {e['Title']}", "HIGH", "VULN")
        except: pass

    # 4. Deep Vulnerability Scan (Nuclei)
    push_log(f"Running Nuclei Deep Scan on {target}...", "NUCLEI")
    nuclei_res = await run_cmd(["nuclei", "-u", target, "-severity", "critical,high", "-silent"])
    if nuclei_res:
        for line in nuclei_res.split('\n'):
            if line: push_log(line, "CRITICAL", "VULN")

    # 5. Web Server Misconfiguration (Nikto)
    push_log(f"Checking Web Configs (Nikto) for {target}...", "NIKTO")
    nikto_res = await run_cmd(["nikto", "-h", target, "-Tuning", "1,2,3,b"])
    if "0 error(s)" not in nikto_res:
        with open(BASE_DIR/f"{target}_nikto.txt", "w") as f: f.write(nikto_res)

    push_log(f"Ultrasonic Scan Complete for {target}. Report saved.", "SUCCESS")

# --- Flask Routes ---
@app.route("/")
def index(): return render_template_string(_HTML_TEMPLATE)

@app.route("/stream")
def stream():
    def event():
        while True: yield f"data: {LOG_QUEUE.get()}\n\n"
    return app.response_class(event(), mimetype="text/event-stream")

async def engine(targets):
    sem = asyncio.Semaphore(2)
    tasks = [asyncio.ensure_future(wrapped_scan(t, sem)) for t in targets]
    await asyncio.gather(*tasks)

async def wrapped_scan(t, sem):
    async with sem: await ultrasonic_scan(t)

# --- Main ---
if __name__ == "__main__":
    setup_environment() # Autonomous Setup
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True, help="Target IP, URL, or File")
    args = parser.parse_args()

    # Autonomous Input Parsing
    if os.path.isfile(args.target):
        targets = open(args.target).read().splitlines()
    else:
        targets = [args.target]

    def start_web():
        webbrowser.open("http://127.0.0.1:5000")
        app.run(port=5000, debug=False, use_reloader=False)

    threading.Thread(target=start_web, daemon=True).start()
    
    try:
        asyncio.run(engine(targets))
    except KeyboardInterrupt:
        print("\n[!] Ultrasonic Shutdown Initiated.")

