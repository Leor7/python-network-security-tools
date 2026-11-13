#!/usr/bin/env python3
"""
Basic packet sniffer using Scapy.

Setup:   pip install scapy
Run:     sudo python packet_sniffer.py -c 20            (Linux/macOS)
         Run terminal as Administrator (Windows, needs Npcap installed)

Only capture traffic on networks you own or have permission to monitor.
"""
import argparse
from datetime import datetime

from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS, DNSQR


def handle(pkt):
    if IP not in pkt:
        return
    ts = datetime.now().strftime("%H:%M:%S")
    src, dst = pkt[IP].src, pkt[IP].dst

    if TCP in pkt:
        flags = str(pkt[TCP].flags)
        print(f"[{ts}] TCP  {src}:{pkt[TCP].sport} -> {dst}:{pkt[TCP].dport} flags={flags}")
    elif UDP in pkt:
        extra = ""
        if DNS in pkt and pkt.haslayer(DNSQR):
            extra = f" DNS query: {pkt[DNSQR].qname.decode(errors='ignore')}"
        print(f"[{ts}] UDP  {src}:{pkt[UDP].sport} -> {dst}:{pkt[UDP].dport}{extra}")
    elif ICMP in pkt:
        print(f"[{ts}] ICMP {src} -> {dst} type={pkt[ICMP].type}")
    else:
        print(f"[{ts}] IP   {src} -> {dst} proto={pkt[IP].proto}")


def main():
    ap = argparse.ArgumentParser(description="Simple packet sniffer")
    ap.add_argument("-i", "--iface", help="Interface (default: Scapy's default)")
    ap.add_argument("-c", "--count", type=int, default=0, help="Packets to capture (0 = forever)")
    ap.add_argument("-f", "--filter", default="", help="BPF filter, e.g. 'tcp port 80'")
    args = ap.parse_args()

    print("Sniffing... press Ctrl+C to stop")
    sniff(iface=args.iface, count=args.count, filter=args.filter, prn=handle, store=False)


if __name__ == "__main__":
    main()
