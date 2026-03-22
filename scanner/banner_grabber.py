import socket
from scanner.config import TIMEOUT

def grab_banner(target, port):
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)
        s.connect((target, port))
        banner = s.recv(1024).decode().strip()
        s.close()
        return banner
    except:
        return "No banner"