"""
Network Scanner - Tkinter GUI
A modern, dark-themed GUI for the network scanner.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import socket
import queue
import time
from datetime import datetime

from scanner.config import TIMEOUT, COMMON_PORTS, OUTPUT_FILE, SERVICES
from scanner.banner_grabber import grab_banner
from scanner.utils import validate_ip


# ── Color Palette ──────────────────────────────────────────────
BG_DARK       = "#1a1b2e"
BG_CARD       = "#232540"
BG_INPUT      = "#2d2f4e"
BG_HEADER     = "#1e1f38"
FG_PRIMARY    = "#e4e4f0"
FG_SECONDARY  = "#8888a8"
FG_DIM        = "#5c5c7a"
ACCENT        = "#6c63ff"
ACCENT_HOVER  = "#7f78ff"
ACCENT_DARK   = "#5548d4"
GREEN         = "#2ecc71"
RED           = "#e74c3c"
ORANGE        = "#f39c12"
CYAN          = "#00d4aa"
BORDER        = "#3a3c5c"


class NetworkScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Network Scanner")
        self.root.geometry("960x720")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_DARK)

        # State
        self.scanning = False
        self.scan_thread = None
        self.result_queue = queue.Queue()
        self.open_ports_count = 0
        self.closed_ports_count = 0
        self.scanned_count = 0
        self.total_ports = 0

        # Try to set icon (won't fail if not available)
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self._configure_styles()
        self._build_ui()
        self._poll_queue()

    # ── Styles ─────────────────────────────────────────────────
    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Treeview
        self.style.configure("Scan.Treeview",
            background=BG_CARD,
            foreground=FG_PRIMARY,
            fieldbackground=BG_CARD,
            borderwidth=0,
            rowheight=32,
            font=("Consolas", 10)
        )
        self.style.configure("Scan.Treeview.Heading",
            background=BG_HEADER,
            foreground=CYAN,
            font=("Segoe UI Semibold", 10),
            borderwidth=0,
            relief="flat"
        )
        self.style.map("Scan.Treeview",
            background=[("selected", ACCENT_DARK)],
            foreground=[("selected", "#ffffff")]
        )

        # Progress bar
        self.style.configure("Accent.Horizontal.TProgressbar",
            troughcolor=BG_INPUT,
            background=ACCENT,
            borderwidth=0,
            lightcolor=ACCENT,
            darkcolor=ACCENT
        )

        # Notebook tabs
        self.style.configure("Dark.TNotebook",
            background=BG_DARK,
            borderwidth=0
        )
        self.style.configure("Dark.TNotebook.Tab",
            background=BG_CARD,
            foreground=FG_SECONDARY,
            padding=[16, 8],
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.map("Dark.TNotebook.Tab",
            background=[("selected", ACCENT_DARK)],
            foreground=[("selected", "#ffffff")]
        )

    # ── Build UI ───────────────────────────────────────────────
    def _build_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # Title bar
        self._build_title_bar(main)

        # Input card
        self._build_input_card(main)

        # Results section
        self._build_results_section(main)

        # Status bar
        self._build_status_bar(main)

    def _build_title_bar(self, parent):
        title_frame = tk.Frame(parent, bg=BG_DARK)
        title_frame.pack(fill="x", pady=(0, 12))

        title = tk.Label(title_frame,
            text="⚡ Network Scanner",
            font=("Segoe UI", 22, "bold"),
            fg=FG_PRIMARY, bg=BG_DARK
        )
        title.pack(side="left")

        subtitle = tk.Label(title_frame,
            text="Port Scanner & Service Detector",
            font=("Segoe UI", 10),
            fg=FG_SECONDARY, bg=BG_DARK
        )
        subtitle.pack(side="left", padx=(12, 0), pady=(8, 0))

    def _build_input_card(self, parent):
        # Outer card with border effect
        card_outer = tk.Frame(parent, bg=BORDER)
        card_outer.pack(fill="x", pady=(0, 12))

        card = tk.Frame(card_outer, bg=BG_CARD, padx=20, pady=16)
        card.pack(fill="x", padx=1, pady=1)

        # ── Row 1: Scan mode + Target ─────────────────────────
        row1 = tk.Frame(card, bg=BG_CARD)
        row1.pack(fill="x", pady=(0, 10))

        # Scan mode
        mode_frame = tk.Frame(row1, bg=BG_CARD)
        mode_frame.pack(side="left")

        tk.Label(mode_frame, text="MODE", font=("Segoe UI", 8, "bold"),
                 fg=FG_DIM, bg=BG_CARD).pack(anchor="w")

        self.scan_mode = tk.StringVar(value="single")

        modes = [("Single IP", "single"), ("IP Range", "range")]
        btn_frame = tk.Frame(mode_frame, bg=BG_CARD)
        btn_frame.pack(anchor="w", pady=(4, 0))

        for text, val in modes:
            rb = tk.Radiobutton(btn_frame,
                text=text, variable=self.scan_mode, value=val,
                font=("Segoe UI", 9),
                fg=FG_PRIMARY, bg=BG_CARD,
                selectcolor=BG_INPUT,
                activebackground=BG_CARD, activeforeground=FG_PRIMARY,
                indicatoron=True,
                command=self._on_mode_change
            )
            rb.pack(side="left", padx=(0, 16))

        # Target input
        target_frame = tk.Frame(row1, bg=BG_CARD)
        target_frame.pack(side="left", fill="x", expand=True, padx=(24, 0))

        self.target_label = tk.Label(target_frame, text="TARGET IP",
            font=("Segoe UI", 8, "bold"),
            fg=FG_DIM, bg=BG_CARD
        )
        self.target_label.pack(anchor="w")

        self.target_entry = tk.Entry(target_frame,
            font=("Consolas", 12),
            fg=FG_PRIMARY, bg=BG_INPUT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.target_entry.pack(fill="x", pady=(4, 0), ipady=6)
        self.target_entry.insert(0, "192.168.1.1")

        # ── Row 2: Port range + Timeout + Buttons ─────────────
        row2 = tk.Frame(card, bg=BG_CARD)
        row2.pack(fill="x")

        # Port range
        port_frame = tk.Frame(row2, bg=BG_CARD)
        port_frame.pack(side="left")

        tk.Label(port_frame, text="PORT RANGE",
            font=("Segoe UI", 8, "bold"),
            fg=FG_DIM, bg=BG_CARD
        ).pack(anchor="w")

        port_input_frame = tk.Frame(port_frame, bg=BG_CARD)
        port_input_frame.pack(anchor="w", pady=(4, 0))

        self.port_start = tk.Entry(port_input_frame,
            width=8, font=("Consolas", 12),
            fg=FG_PRIMARY, bg=BG_INPUT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.port_start.pack(side="left", ipady=6)
        self.port_start.insert(0, "1")

        tk.Label(port_input_frame, text=" — ", font=("Segoe UI", 12),
                 fg=FG_DIM, bg=BG_CARD).pack(side="left")

        self.port_end = tk.Entry(port_input_frame,
            width=8, font=("Consolas", 12),
            fg=FG_PRIMARY, bg=BG_INPUT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.port_end.pack(side="left", ipady=6)
        self.port_end.insert(0, "1024")

        # Common ports checkbox
        self.use_common = tk.BooleanVar(value=True)
        self.common_cb = tk.Checkbutton(port_input_frame,
            text="Common ports only",
            variable=self.use_common,
            font=("Segoe UI", 9),
            fg=FG_SECONDARY, bg=BG_CARD,
            selectcolor=BG_INPUT,
            activebackground=BG_CARD,
            activeforeground=FG_PRIMARY,
            command=self._toggle_port_inputs
        )
        self.common_cb.pack(side="left", padx=(20, 0))

        # Buttons
        btn_container = tk.Frame(row2, bg=BG_CARD)
        btn_container.pack(side="right", pady=(20, 0))

        self.scan_btn = tk.Button(btn_container,
            text="▶  Start Scan",
            font=("Segoe UI Semibold", 11),
            fg="#ffffff", bg=ACCENT,
            activebackground=ACCENT_HOVER,
            activeforeground="#ffffff",
            relief="flat", bd=0,
            cursor="hand2",
            padx=24, pady=8,
            command=self._start_scan
        )
        self.scan_btn.pack(side="left", padx=(0, 8))
        self.scan_btn.bind("<Enter>", lambda e: self.scan_btn.config(bg=ACCENT_HOVER))
        self.scan_btn.bind("<Leave>", lambda e: self.scan_btn.config(bg=ACCENT))

        self.stop_btn = tk.Button(btn_container,
            text="■  Stop",
            font=("Segoe UI Semibold", 11),
            fg="#ffffff", bg=RED,
            activebackground="#c0392b",
            activeforeground="#ffffff",
            relief="flat", bd=0,
            cursor="hand2",
            padx=16, pady=8,
            state="disabled",
            command=self._stop_scan
        )
        self.stop_btn.pack(side="left")

        # Initially disable port inputs (common ports is checked)
        self._toggle_port_inputs()

    def _build_results_section(self, parent):
        # Header with action buttons
        header = tk.Frame(parent, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 6))

        tk.Label(header, text="SCAN RESULTS",
            font=("Segoe UI", 9, "bold"),
            fg=FG_DIM, bg=BG_DARK
        ).pack(side="left")

        # Action buttons on the right
        self.export_btn = tk.Button(header,
            text="💾 Export",
            font=("Segoe UI", 9),
            fg=FG_SECONDARY, bg=BG_CARD,
            activebackground=BG_INPUT,
            activeforeground=FG_PRIMARY,
            relief="flat", bd=0,
            cursor="hand2",
            padx=12, pady=4,
            command=self._export_results
        )
        self.export_btn.pack(side="right", padx=(6, 0))

        self.clear_btn = tk.Button(header,
            text="🗑 Clear",
            font=("Segoe UI", 9),
            fg=FG_SECONDARY, bg=BG_CARD,
            activebackground=BG_INPUT,
            activeforeground=FG_PRIMARY,
            relief="flat", bd=0,
            cursor="hand2",
            padx=12, pady=4,
            command=self._clear_results
        )
        self.clear_btn.pack(side="right")

        # Treeview card
        tree_outer = tk.Frame(parent, bg=BORDER)
        tree_outer.pack(fill="both", expand=True)

        tree_inner = tk.Frame(tree_outer, bg=BG_CARD)
        tree_inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Columns
        columns = ("port", "status", "service", "banner")
        self.tree = ttk.Treeview(tree_inner,
            columns=columns,
            show="headings",
            style="Scan.Treeview",
            selectmode="browse"
        )

        self.tree.heading("port",    text="PORT",    anchor="w")
        self.tree.heading("status",  text="STATUS",  anchor="w")
        self.tree.heading("service", text="SERVICE", anchor="w")
        self.tree.heading("banner",  text="BANNER",  anchor="w")

        self.tree.column("port",    width=80,  minwidth=60,  stretch=False)
        self.tree.column("status",  width=100, minwidth=80,  stretch=False)
        self.tree.column("service", width=120, minwidth=80,  stretch=False)
        self.tree.column("banner",  width=400, minwidth=200, stretch=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tag for coloring rows
        self.tree.tag_configure("open",   foreground=GREEN)
        self.tree.tag_configure("closed", foreground=RED)

    def _build_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg=BG_DARK)
        status_frame.pack(fill="x", pady=(8, 0))

        # Progress bar
        self.progress = ttk.Progressbar(status_frame,
            style="Accent.Horizontal.TProgressbar",
            mode="determinate",
            length=200
        )
        self.progress.pack(fill="x", pady=(0, 6))

        # Stats row
        stats_row = tk.Frame(status_frame, bg=BG_DARK)
        stats_row.pack(fill="x")

        self.status_label = tk.Label(stats_row,
            text="Ready to scan",
            font=("Segoe UI", 9),
            fg=FG_SECONDARY, bg=BG_DARK,
            anchor="w"
        )
        self.status_label.pack(side="left")

        self.stats_label = tk.Label(stats_row,
            text="",
            font=("Consolas", 9),
            fg=FG_DIM, bg=BG_DARK,
            anchor="e"
        )
        self.stats_label.pack(side="right")

    # ── Event Handlers ─────────────────────────────────────────
    def _on_mode_change(self):
        if self.scan_mode.get() == "range":
            self.target_label.config(text="IP RANGE (e.g. 192.168.1.1-10)")
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, "192.168.1.1-10")
        else:
            self.target_label.config(text="TARGET IP")
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, "192.168.1.1")

    def _toggle_port_inputs(self):
        state = "disabled" if self.use_common.get() else "normal"
        self.port_start.config(state=state)
        self.port_end.config(state=state)

    def _start_scan(self):
        if self.scanning:
            return

        target_text = self.target_entry.get().strip()
        if not target_text:
            messagebox.showwarning("Input Error", "Please enter a target IP address.")
            return

        # Determine target IPs
        if self.scan_mode.get() == "range":
            try:
                targets = self._generate_ips(target_text)
            except Exception:
                messagebox.showerror("Input Error",
                    "Invalid IP range format.\nUse format: 192.168.1.1-10")
                return
        else:
            targets = [target_text]

        # Validate all IPs
        for ip in targets:
            if not validate_ip(ip):
                messagebox.showerror("Invalid IP",
                    f"'{ip}' is not a valid IPv4 address.")
                return

        # Determine ports
        if self.use_common.get():
            ports = COMMON_PORTS
        else:
            try:
                p_start = int(self.port_start.get())
                p_end = int(self.port_end.get())
                if p_start < 1 or p_end > 65535 or p_start > p_end:
                    raise ValueError
                ports = list(range(p_start, p_end + 1))
            except ValueError:
                messagebox.showerror("Input Error",
                    "Invalid port range. Use values between 1 and 65535.")
                return

        # Clear & prepare
        self._clear_results()
        self.scanning = True
        self.open_ports_count = 0
        self.closed_ports_count = 0
        self.scanned_count = 0
        self.total_ports = len(ports) * len(targets)

        self.scan_btn.config(state="disabled", bg=FG_DIM)
        self.stop_btn.config(state="normal")
        self.progress.config(mode="determinate", maximum=self.total_ports, value=0)
        self.status_label.config(text="Scanning...", fg=ORANGE)

        # Start background scan
        self.scan_thread = threading.Thread(
            target=self._run_scan, args=(targets, ports), daemon=True
        )
        self.scan_thread.start()

    def _stop_scan(self):
        self.scanning = False
        self.status_label.config(text="Scan stopped by user", fg=RED)
        self._scan_finished()

    def _run_scan(self, targets, ports):
        start_time = time.time()

        for target in targets:
            if not self.scanning:
                break
            self.result_queue.put(("header", target, None, None, None))

            threads = []
            for port in ports:
                if not self.scanning:
                    break
                t = threading.Thread(
                    target=self._scan_single_port,
                    args=(target, port),
                    daemon=True
                )
                threads.append(t)
                t.start()

                # Limit concurrent threads
                while threading.active_count() > 150:
                    time.sleep(0.01)

            for t in threads:
                t.join(timeout=TIMEOUT + 1)

        elapsed = time.time() - start_time
        self.result_queue.put(("done", elapsed, None, None, None))

    def _scan_single_port(self, target, port):
        if not self.scanning:
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(TIMEOUT)
            result = s.connect_ex((target, port))

            if result == 0:
                service = SERVICES.get(port, "Unknown")
                banner = grab_banner(target, port)
                self.result_queue.put(("open", port, "OPEN", service, banner))
            else:
                service = SERVICES.get(port, "—")
                self.result_queue.put(("closed", port, "CLOSED", service, ""))
            s.close()
        except Exception as e:
            service = SERVICES.get(port, "—")
            self.result_queue.put(("closed", port, "CLOSED", service, str(e)))
        finally:
            self.result_queue.put(("progress", None, None, None, None))

    # ── Queue Polling ──────────────────────────────────────────
    def _poll_queue(self):
        try:
            while True:
                msg = self.result_queue.get_nowait()
                msg_type = msg[0]

                if msg_type == "open":
                    _, port, status, service, banner = msg
                    self.tree.insert("", "end",
                        values=(port, status, service, banner),
                        tags=("open",)
                    )
                    self.open_ports_count += 1
                    self.tree.yview_moveto(1.0)

                elif msg_type == "closed":
                    _, port, status, service, banner = msg
                    self.tree.insert("", "end",
                        values=(port, status, service, banner),
                        tags=("closed",)
                    )
                    self.closed_ports_count += 1
                    self.tree.yview_moveto(1.0)

                elif msg_type == "header":
                    _, target, _, _, _ = msg
                    self.tree.insert("", "end",
                        values=(f"── {target}", "──────", "──────", "──────"),
                        tags=()
                    )

                elif msg_type == "progress":
                    self.scanned_count += 1
                    self.progress.config(value=self.scanned_count)
                    pct = int((self.scanned_count / max(self.total_ports, 1)) * 100)
                    self.stats_label.config(
                        text=f"Scanned: {self.scanned_count}/{self.total_ports}  |  "
                             f"Open: {self.open_ports_count}  |  "
                             f"Closed: {self.closed_ports_count}  |  {pct}%"
                    )

                elif msg_type == "done":
                    elapsed = msg[1]
                    self.status_label.config(
                        text=f"✅ Scan complete — {self.open_ports_count} open port(s) "
                             f"found in {elapsed:.1f}s",
                        fg=GREEN
                    )
                    self._scan_finished()

        except queue.Empty:
            pass

        self.root.after(50, self._poll_queue)

    def _scan_finished(self):
        self.scanning = False
        self.scan_btn.config(state="normal", bg=ACCENT)
        self.stop_btn.config(state="disabled")

    # ── Actions ────────────────────────────────────────────────
    def _clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.open_ports_count = 0
        self.closed_ports_count = 0
        self.scanned_count = 0
        self.progress.config(value=0)
        self.stats_label.config(text="")
        self.status_label.config(text="Ready to scan", fg=FG_SECONDARY)

    def _export_results(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("Export", "No results to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                f.write(f"Network Scanner Results — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"{'PORT':<8} {'STATUS':<10} {'SERVICE':<12} {'BANNER'}\n")
                f.write("-" * 60 + "\n")

                for item in items:
                    vals = self.tree.item(item, "values")
                    f.write(f"{vals[0]:<8} {vals[1]:<10} {vals[2]:<12} {vals[3]}\n")

            messagebox.showinfo("Export", f"Results saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Utilities ──────────────────────────────────────────────
    def _generate_ips(self, ip_range):
        base = ".".join(ip_range.split(".")[:3])
        start, end = map(int, ip_range.split(".")[-1].split("-"))
        return [f"{base}.{i}" for i in range(start, end + 1)]


def launch_gui():
    """Entry point to launch the GUI."""
    root = tk.Tk()
    app = NetworkScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
