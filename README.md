<p align="center">
  <h1 align="center">⚡ Network Scanner</h1>
  <p align="center">
    A powerful, multi-threaded network scanner built with Python — featuring port scanning, service detection, banner grabbing, and a modern dark-themed GUI.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tkinter-GUI-6c63ff?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/License-GPL--3.0-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey?style=for-the-badge" alt="Platform">
</p>

---

## 📸 Screenshot

![GUI](https://github.com/user-attachments/assets/481c2d70-0e8c-47f6-aa63-906fc72c0979)


---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔍 **Port Scanning** | Scan common ports or define a custom range (1–65535) |
| 🌐 **IP Range Scanning** | Scan multiple hosts at once (e.g. `192.168.1.1-10`) |
| 🏷️ **Service Detection** | Identify services running on open ports (FTP, SSH, HTTP, etc.) |
| 📡 **Banner Grabbing** | Retrieve version banners from open services |
| ⚡ **Multi-Threaded** | Fast, concurrent scanning with up to 150 threads |
| 🖥️ **Modern GUI** | Dark-themed Tkinter interface with real-time results |
| 📊 **Live Progress** | Progress bar and stats (scanned, open, closed) update in real-time |
| 💾 **Export Results** | Save scan results to `.txt` or `.csv` |
| 🖨️ **CLI Mode** | Full command-line interface for scripting and automation |

---

## 📁 Project Structure

```
network-scanner/
├── scanner/
│   ├── __init__.py            # Package initializer
│   ├── main.py                # CLI entry point & argument parsing
│   ├── gui.py                 # Tkinter GUI application
│   ├── port_scanner.py        # Multi-threaded port scanning engine
│   ├── banner_grabber.py      # Banner grabbing from open services
│   ├── config.py              # Configuration (ports, timeout, services)
│   └── utils.py               # IP validation & output formatting
├── output/
│   └── results.txt            # Scan results output (auto-generated)
├── screenshots/
│   └── gui_screenshot.png     # GUI screenshot
├── requirements.txt           # Python dependencies
├── LICENSE                    # GPL-3.0 License
└── README.md
```

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/HashenWatawala/network-scanner.git
cd network-scanner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** Tkinter comes pre-installed with Python on Windows and macOS. On Linux, install it with:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## ▶️ Usage

### GUI Mode (Recommended)

Launch the graphical interface:

```bash
python -m scanner.gui
```

**How to use the GUI:**
1. Select **Single IP** or **IP Range** mode
2. Enter the target IP address (e.g. `127.0.0.1` or `192.168.1.1-10`)
3. Choose **Common ports only** or uncheck it and set a custom port range
4. Click **▶ Start Scan** and watch results appear in real-time
5. Use **💾 Export** to save results or **🗑 Clear** to reset

---

### CLI Mode

#### Scan a single target (common ports)
```bash
python -m scanner.main -t 192.168.1.1
```

#### Scan with a custom port range
```bash
python -m scanner.main -t 192.168.1.1 -p 1-1024
```

#### Scan a range of IPs
```bash
python -m scanner.main -r 192.168.1.1-10
```

#### Scan an IP range with custom ports
```bash
python -m scanner.main -r 192.168.1.1-10 -p 80-443
```

---

## ⚙️ CLI Options

| Flag | Description | Example |
|------|-------------|---------|
| `-t`, `--target` | Target IP address | `-t 192.168.1.1` |
| `-r`, `--range` | IP range to scan | `-r 192.168.1.1-10` |
| `-p`, `--ports` | Port range to scan | `-p 1-1024` |

---

## 🔧 Configuration

Default settings can be modified in [`scanner/config.py`](scanner/config.py):

| Setting | Default | Description |
|---------|---------|-------------|
| `COMMON_PORTS` | `[21, 22, 23, 25, 53, 80, 443]` | Ports scanned in "common" mode |
| `TIMEOUT` | `1` second | Socket connection timeout |
| `MAX_THREADS` | `100` | Maximum concurrent threads |
| `OUTPUT_FILE` | `output/results.txt` | CLI results output file |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GPL-3.0 License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/HashenWatawala">Hashen Watawala</a>
</p>
