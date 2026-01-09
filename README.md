<img width="1024" height="1024" alt="1000104052" src="https://github.com/user-attachments/assets/2c06fb51-0df6-4d30-85b8-daa49b97f3c1" />
# 🔱 Nmap-Pro V7: Ultrasonic Autonomous Edition 🔱
### Developed by: Vishal ❤️ Subhi
**Purpose:** Advanced Stealth Reconnaissance, Autonomous Vulnerability Mapping, and Exploit Discovery.

---

## 🚀 Overview
Nmap-Pro V7 is an "Ultrasonic" pentesting framework designed to operate autonomously. It combines the power of industry-standard tools (Nmap, Nuclei, Searchsploit, Nikto) into a single engine with a real-time "Matrix Green" web dashboard.

### 🛡️ Ultrasonic Features:
* **Self-Healing Setup:** Automatically detects and installs missing dependencies.
* **Ghost Stealth Mode:** Uses packet fragmentation and data padding to bypass AI-based Firewalls/IDS.
* **Exploit-DB Integration:** Automatically matches service versions with the local Searchsploit database.
* **Dual-View Dashboard:** Real-time logs on the left, Critical Vulnerabilities (Red Alerts) on the right.
* **Multi-Tool Fusion:** Orchestrates WhatWeb, Nmap, Nuclei, and Nikto in a single thread.

---

## 🛠️ Installation & Setup

Simply run the script with `sudo`, and it will handle the environment setup for you.

### 1. Clone or Save the script
```bash
# Save the code to a file
nano nmap_pro_v7.py
# (Paste the code and save using Ctrl+O, Enter, Ctrl+X)


chmod +x nmap_pro_v7.py
sudo python3 nmap_pro_v7.py -t 192.168.1.1
sudo python3 nmap_pro_v7.py -t targets.txt

.
├── nmap_pro_v7.py          # Main Engine
├── README.md               # Documentation
└── ultrasonic_vault/       # Autonomous Results Directory
    ├── 192.168.1.1.txt     # Consolidated Report
    └── nikto_reports/      # Detailed Web Scan Logs
