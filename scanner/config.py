COMMON_PORTS = [21, 22, 23, 25, 53, 80, 443]
TIMEOUT = 1
MAX_THREADS = 100
OUTPUT_FILE = "output/results.txt"

# NEW
SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS"
}