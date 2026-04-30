import subprocess
import socket

def get_wifi_ssid():
    try:
        output = subprocess.check_output(
            "netsh wlan show interfaces", shell=True
        ).decode(errors="ignore")

        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        return None

    return None

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()

def detect_location():
    ssid = get_wifi_ssid()
    ip = get_local_ip() or ""

    if ssid == "HA":
        return "home"
    if ssid == "Kristy's S26 Ultra":
        return "office"

    if ip.startswith("192.168.4."):
        return "home"
    if ip.startswith("172.19.170."):
        return "office"
    if ip.startswith("10.34.4."):
        return "office"

    return "unknown"
