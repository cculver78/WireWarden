# 🛡️ WireWarden

**WireWarden** is a lightweight **PyQt6 GUI** for managing **WireGuard VPN tunnels** on Linux.  
It detects `.conf` files automatically, shows each connection with clear color indicators, and lets you bring tunnels **up or down with one click** — no terminal required.

---

## ✨ Features
- 🔍 Auto-detects all `.conf` files in the app folder  
- 🟢 Red/green buttons show live connection status  
- 🚫 Prevents multiple tunnels from running at once  
- ⚠️ Warns if config filenames contain invalid characters  
- 🔄 Automatically refreshes interface status every few seconds  
- 🧠 Simple, readable Python source built with **PyQt6**

---

## Requirements
- Linux system with **WireGuard** installed (`wg`, `wg-quick`)
- Python ≥ 3.9  
- `PyQt6` installed:
  ```bash
  pip install PyQt6
  or
  pip install -r requirements.txt
  ```

---

## Run It
Clone the repo and launch:

```bash
git clone https://github.com/cculver78/WireWarden.git
cd WireWarden
python3 WireWarden.py
```

Place your `*.conf` files in the same folder as the script.

---

## Desktop Integration
To launch from your system menu, create:

`~/.local/share/applications/WireWarden.desktop`
```ini
[Desktop Entry]
Name=WireWarden
Comment=Simple PyQt6 GUI for WireGuard VPNs
Exec=pkexec python3 /path/to/WireWarden/WireWarden.py
Icon=network-vpn
Terminal=false
Type=Application
Categories=Network;System;
StartupNotify=true
```

---

## License
Released under the **MIT License** — free to use, modify, and share, provided the original copyright notice and credit to **Charles Culver** remain.

---

## Concept
WireWarden was built for sysadmins, homelab enthusiasts, and privacy-minded users who prefer a clean visual controller over the command line.

---

## Author
**Charles "Chuck" Culver**  
[GitHub](https://github.com/cculver78) • [Bluesky](https://bsky.app/profile/dhelmet78.bsky.social) • [Threads](https://www.threads.com/@cculver78)

---