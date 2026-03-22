import socket

def validate_ip(target):
    try:
        socket.inet_aton(target)
        return True
    except socket.error:
        return False


def format_result(port, status, service="", banner=""):
    return f"{port:<6} {status:<8} {service:<10} {banner}"