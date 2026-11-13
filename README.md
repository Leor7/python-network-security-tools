# Python Network Security Tools

A cybersecurity portfolio project featuring a **multithreaded TCP port scanner** and a **packet sniffer** written in Python. I built these tools to practice network enumeration, traffic analysis, socket programming, and responsible security testing.

> **Authorized use only:** Scan or capture traffic only on devices and networks you own or have explicit permission to test.

## Included tools

| Tool | File | What it does |
| --- | --- | --- |
| TCP port scanner | `port_scanner.py` | Tests TCP connections to selected ports, identifies common service names, and attempts to read banners |
| Packet sniffer | `packet_sniffer.py` | Captures IPv4 traffic and displays TCP, UDP, ICMP, and DNS-query information |

### Port scanner features

- Uses Python's built-in `socket` library, with no third-party dependencies.
- Supports single ports, lists, and ranges (for example, `22,80,100-200`).
- Runs concurrent TCP connect scans using a thread pool (`-t`).
- Supports a configurable connection timeout (`--timeout`).
- Reports open ports, typical service names, available banners, and elapsed time.

### Packet sniffer features

- Uses [Scapy](https://scapy.net/) to capture traffic.
- Displays source and destination IPv4 addresses, TCP and UDP ports, TCP flags, ICMP types, and DNS queries when available.
- Supports packet count (`-c`), interface selection (`-i`), and BPF capture filters (`-f`).

## Requirements

- Python 3.9 or newer.
- **Port scanner:** Python standard library only.
- **Packet sniffer:** Scapy, installed from `requirements.txt`.
- **Windows packet capture:** [Npcap](https://npcap.com/) and a PowerShell or VS Code terminal running as Administrator (subject to Npcap installation settings).
- **Linux/macOS packet capture:** sufficient packet-capture permissions (often `sudo`).

## Setup in VS Code (Windows PowerShell)

Open the project folder in VS Code and open **Terminal → New Terminal**. If you're using the original local folder:

```powershell
cd "C:\Users\leosk\Documents\cyber-project"
```

Install the packet-sniffer dependency:

```powershell
python -m pip install -r requirements.txt
```

You can run the port scanner without installing Scapy.

## How to use the tools

### 1. TCP port scanner

Scan your own computer (ports 1 through 1024):

```powershell
python port_scanner.py 127.0.0.1 -p 1-1024
```

Scan selected ports:

```powershell
python port_scanner.py 127.0.0.1 -p 22,80,443
```

Try 500 concurrent workers:

```powershell
python port_scanner.py 127.0.0.1 -p 1-1024 -t 500
```

Change the timeout:

```powershell
python port_scanner.py 127.0.0.1 -p 1-1024 --timeout 1
```

See all options:

```powershell
python port_scanner.py --help
```

**How it works:** The script performs a **TCP connect scan**. A successful connection indicates that the tested TCP port accepted the connection. The script then tries to read a small response as a banner. Some services don't announce themselves, so an empty banner is normal. Service names come from port-number mappings and do not prove which application is listening.

### 2. Packet sniffer

On Windows, first install Npcap and open VS Code or PowerShell **as Administrator**. 

## Windows Setup: Installing Scapy and Npcap

The port scanner uses Python's built-in libraries, but the packet sniffer requires **Scapy** and **Npcap** to capture network traffic on Windows.

### Step 1: Install Python Dependencies

Open the project folder in VS Code and run the following command in the PowerShell terminal:

`python -m pip install -r requirements.txt`

Alternatively, install Scapy directly:

`python -m pip install scapy`

### Step 2: Verify Scapy Installation

Check that Scapy installed successfully:

`python -m pip show scapy`

You should see the installed version and package information.

### Step 3: Install Npcap (Windows Only)

Scapy requires Npcap for packet capturing on Windows.

1. Visit [Npcap's official website](https://npcap.com/#download).
2. Download and run the Npcap installer.
3. Follow the installation instructions using the default settings.
4. Close VS Code and reopen it as Administrator if packet capture permissions are required.

### Step 4: Run the Packet Sniffer

Open the VS Code terminal and run:

`python packet_sniffer.py -c 20`

This captures up to 20 packets and then stops.

To capture TCP traffic only, run:

`python packet_sniffer.py -c 20 -f "tcp"`

Generate some network traffic by opening a website while the sniffer is running. Press `Ctrl+C` to stop capturing manually.

### Troubleshooting: ModuleNotFoundError

If you encounter:

`ModuleNotFoundError: No module named 'scapy'`

Python cannot locate Scapy in the environment running your script.

**Solution:**

1. Run `python -m pip install scapy`.
2. Verify installation with `python -m pip show scapy`.
3. Make sure VS Code is using the same Python interpreter where Scapy was installed.
4. Restart the terminal and run the script again.

**Important:** If you use the `-i` argument to select a network interface, replace `INTERFACE_NAME` with an actual interface. Otherwise, omit `-i` and let Scapy use its default interface.

**Ethical Use:** Capture traffic only on networks you own or have permission to monitor.

Then run:

```powershell
python packet_sniffer.py -c 20
```

To capture matching TCP traffic only:

```powershell
python packet_sniffer.py -c 20 -f "tcp port 80"
```

To capture on a specific interface (replace `INTERFACE_NAME` with an actual interface name):

```powershell
python packet_sniffer.py -i "INTERFACE_NAME" -c 20
```

On Linux or macOS, `python3` may be needed in place of `python`, and capture permissions are often required. Stop an indefinite capture with **Ctrl+C**.

**Note:** The `-c` option counts captured packets, but the script prints output only for packets with an IPv4 layer. Therefore, the number of printed lines may be lower than the capture count.

## My test results (November 13, 2026)

I tested the scanner against my Windows machine using `127.0.0.1`.

**Default scan (100 threads):**

```text
Scanning 127.0.0.1 (127.0.0.1), 1024 ports...

PORT    SERVICE     BANNER
135     epmap
445     microsoft-ds

2 open port(s) found in 5.63s
```

**500-thread scan:**

```text
Scanning 127.0.0.1 (127.0.0.1), 1024 ports...

PORT    SERVICE     BANNER
135     epmap
445     microsoft-ds

2 open port(s) found in 1.54s
```

| Configuration | Time | Ports reported open |
| --- | ---: | --- |
| Default, 100 threads | 5.63 seconds | 135, 445 |
| 500 threads | 1.54 seconds | 135, 445 |

The 500-thread run was **about 73% faster** in this one comparison. Actual speed varies with the computer, network, target, and timeout, so this is not a controlled benchmark.

- **135 (`epmap`)** is commonly associated with Microsoft's RPC Endpoint Mapper.
- **445 (`microsoft-ds`)** is commonly associated with SMB file sharing.

I also scanned a small selection of ports on `scanme.nmap.org`, an Nmap-provided test target, and received an SSH banner on port 22 along with other open ports. Follow the host's published testing rules and avoid intrusive or high-volume scanning.

### Packet-sniffer testing status

The packet sniffer has been written, but a successful live packet capture has **not yet been documented**. A screenshot and sample capture output can be added after testing.

## What I learned

- TCP connect scanning, socket timeouts, and banner limitations.
- How threading can change the time required to scan a range of ports.
- The difference between a port's typical service name and actual service identification.
- How to inspect packet protocols and metadata with Scapy.
- Why capture permissions, responsible scope, and clear documentation matter.

## Limitations and ideas for improvements

- The scanner supports IPv4 TCP connect scans, not IPv6 or UDP scanning.
- Service names are inferred from ports; full service fingerprinting is not implemented.
- Some service banners are empty or contain binary/non-printable characters.
- High worker counts can consume resources and generate more traffic.
- The sniffer currently prints to the console rather than saving PCAP files.
- Automated tests and CSV/JSON exports could be added in the future.

## Project layout

```text
python-network-security-tools/
├── port_scanner.py
├── packet_sniffer.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Responsible use

These tools are for educational, defensive, and **authorized** security testing. Never upload real credentials, private traffic captures, or confidential company information to a public GitHub repository.

## License

Released under the [MIT License](LICENSE).
