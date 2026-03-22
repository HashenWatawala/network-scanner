import argparse
from datetime import datetime
from scanner.port_scanner import start_scan
from scanner.utils import validate_ip


def generate_ips(ip_range):
    """Generate a list of IPs from a range like 192.168.1.1-10"""
    base = ".".join(ip_range.split(".")[:3])
    start, end = map(int, ip_range.split(".")[-1].split("-"))
    return [f"{base}.{i}" for i in range(start, end + 1)]


def main():
    parser = argparse.ArgumentParser(description="Custom Network Scanner")
    parser.add_argument("-t", "--target", help="Target IP address")
    parser.add_argument("-r", "--range", help="IP range (e.g. 192.168.1.1-10)")
    parser.add_argument("-p", "--ports", help="Port range (e.g. 1-1024)")

    args = parser.parse_args()

    if not args.target and not args.range:
        parser.error("You must specify either --target or --range")

    # Parse port range
    if args.ports:
        start, end = map(int, args.ports.split("-"))
        ports = range(start, end + 1)
    else:
        ports = None

    # Determine targets
    if args.range:
        targets = generate_ips(args.range)
    elif args.target:
        targets = [args.target]

    # Validate all IPs
    for t in targets:
        if not validate_ip(t):
            print(f"Invalid IP address: {t}")
            return

    start_time = datetime.now()

    for t in targets:
        start_scan(t, ports)

    end_time = datetime.now()
    print(f"\nScan completed in: {end_time - start_time}")


if __name__ == "__main__":
    main()