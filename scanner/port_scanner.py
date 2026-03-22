import socket
import threading
from scanner.config import TIMEOUT, COMMON_PORTS, OUTPUT_FILE
from scanner.banner_grabber import grab_banner
from scanner.utils import format_result

lock = threading.Lock()

def scan_port(target, port, results):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)

        result = s.connect_ex((target, port))

        if result == 0:
            banner = grab_banner(target, port)
            output = format_result(port, "OPEN", "", banner)

            with lock:
                print(output)
                results.append(output)

        s.close()

    except:
        pass


def start_scan(target, ports=COMMON_PORTS):
    print(f"\nScanning {target}...\n")
    print("PORT   STATUS   SERVICE    BANNER")

    threads = []
    results = []

    for port in ports:
        thread = threading.Thread(target=scan_port, args=(target, port, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    save_results(results)


def save_results(results):
    with open(OUTPUT_FILE, "w") as f:
        for line in results:
            f.write(line + "\n")

    print(f"\nResults saved to {OUTPUT_FILE}")