#!/usr/bin/env python3
"""
Simple multithreaded TCP connect port scanner (standard library only).

Only scan systems you own or have written permission to test.

Usage:
    python port_scanner.py 127.0.0.1
    python port_scanner.py 192.168.1.1 -p 1-1024 -t 200
    python port_scanner.py scanme.nmap.org -p 22,80,443   # Nmap allows this host
"""
import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor


def parse_ports(spec: str) -> list[int]:
    """Turn '22,80,100-200' into a sorted list of ports."""
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        elif part:
            ports.add(int(part))
    bad = [p for p in ports if not 1 <= p <= 65535]
    if bad:
        raise ValueError(f"Ports out of range: {bad[:5]}")
    return sorted(ports)


def grab_banner(sock: socket.socket) -> str:
    """Try to read a short service banner (works for SSH, FTP, SMTP, etc.)."""
    try:
        sock.settimeout(1.0)
        data = sock.recv(128)
        return data.decode(errors="ignore").strip().splitlines()[0] if data else ""
    except (socket.timeout, OSError, IndexError):
        return ""


def scan_port(host: str, port: int, timeout: float):
    """Return (port, banner) if open, else None."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        # connect_ex returns 0 on success instead of raising an exception.
        if s.connect_ex((host, port)) == 0:
            return port, grab_banner(s)
    return None


def service_name(port: int) -> str:
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description="Simple TCP port scanner")
    ap.add_argument("host", help="Target hostname or IP (only scan what you own)")
    ap.add_argument("-p", "--ports", default="1-1024", help="e.g. 22,80,443 or 1-1024")
    ap.add_argument("-t", "--threads", type=int, default=100)
    ap.add_argument("--timeout", type=float, default=0.5)
    args = ap.parse_args()

    try:
        ip = socket.gethostbyname(args.host)
        ports = parse_ports(args.ports)
    except (socket.gaierror, ValueError) as e:
        print(f"Error: {e}")
        return 1

    print(f"Scanning {args.host} ({ip}), {len(ports)} ports...")
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        results = pool.map(lambda p: scan_port(ip, p, args.timeout), ports)
        open_ports = [r for r in results if r]

    print(f"\n{'PORT':<8}{'SERVICE':<12}BANNER")
    for port, banner in open_ports:
        print(f"{port:<8}{service_name(port):<12}{banner}")
    print(f"\n{len(open_ports)} open port(s) found in {time.time() - start:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
