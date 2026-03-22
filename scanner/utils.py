import re
from colorama import Fore, Style, init
init(autoreset=True)


def validate_ip(ip):
    """Validate an IPv4 address"""
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(octet) <= 255 for octet in ip.split("."))


def format_result(port, status, service="", banner=""):
    if status == "OPEN":
        status_colored = Fore.GREEN + status
    else:
        status_colored = Fore.RED + status

    return f"{port:<6} {status_colored:<10} {service:<10} {banner}"