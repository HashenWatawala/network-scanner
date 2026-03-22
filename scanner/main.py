import argparse
from datetime import datetime
from scanner.port_scanner import start_scan
from scanner.utils import validate_ip


def main():
    parser = argparse.ArgumentParser(description="Custom Network Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target IP address")

    args = parser.parse_args()
    target = args.target

    if not validate_ip(target):
        print("Invalid IP address")
        return

    start_time = datetime.now()

    start_scan(target)

    end_time = datetime.now()
    print(f"\nScan completed in: {end_time - start_time}")


if __name__ == "__main__":
    main()