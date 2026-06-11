# Enterprise Multi-Vendor Network Security Lab

> A hybrid, multi-AS enterprise network built in EVE-NG — three BGP autonomous systems, an OSPF underlay, and a five-tunnel IPsec overlay spanning **Palo Alto, Check Point, and FortiGate**, plus a GlobalProtect remote-access VPN. Built end-to-end to demonstrate routing, firewall, and VPN engineering with an evidence-first troubleshooting methodology.

**Author:** Matan Gonen — Network & Security Specialist
**LinkedIn:** [linkedin.com/in/matan-gonen](https://linkedin.com/in/matan-gonen)

---

## Tech Stack

| Domain | Technologies |
|--------|--------------|
| **Firewalls** | Palo Alto PAN-OS 10.1 · Check Point R81 (T392) · FortiGate FortiOS 7.2 |
| **Routing** | Cisco IOS 15.9 — BGP (eBGP/iBGP), OSPFv2/v3, Route Reflector, MP-BGP IPv6 |
| **VPN** | IPsec IKEv1 (site-to-site, multi-vendor) · GlobalProtect (remote access) |
| **Analysis** | Wireshark · `fw monitor` · PA Packet Capture · FortiGate `diagnose sniffer`/`debug flow` |
| **Automation / Mgmt** | Python + Netmiko (out-of-band jump host) · Git Bash |
| **Platform** | EVE-NG on VMware Workstation |

---

## What This Lab Demonstrates

- **Multi-AS BGP design** — three autonomous systems with eBGP peering, an iBGP core using a Route Reflector, and a full path-selection feature stack (Local Preference, AS-Path Prepending, aggregation, multihop, MP-BGP for IPv6).
- **Multi-vendor firewall operations** — the same security and VPN concepts implemented on three different platforms, with a clear mapping of equivalent terminology and tooling across them.
- **A five-tunnel IPsec overlay** plus a GlobalProtect remote-access VPN, including a documented interoperability failure (Phase 2 traffic-selector mismatch) and its resolution.
- **A repeatable troubleshooting methodology** — Routing → NAT → Firewall Policy → VPN → Packet Capture — backed by packet walks and dual-sided captures.
- **Out-of-band management** — a dedicated management network and a Linux jump host for device access and automation.

---

## Architecture

The full topology diagram is in [`diagrams/NetSec_Lab_Topology.drawio`](diagrams/) (open at [app.diagrams.net](https://app.diagrams.net)).

```
                        ┌─────────────────────────────┐
                        │   AS 65003 — Transit ISP     │
                        │   R_ISP  (Lo0 5.5.5.5)       │
                        └───────┬──────────────┬───────┘
                       eBGP    │              │   eBGP
              ┌─────────────────┘              └─────────────────┐
              │                                                   │
   ┌──────────┴───────────────┐                     ┌────────────┴──────────────┐
   │   AS 65001 — HQ           │   eBGP (direct)     │   AS 65002 — Branch        │
   │                           │◄───────────────────►│                            │
   │   R1 ★ Route Reflector    │                     │   R2 ──── R4               │
   │    ├── R3 (iBGP client)   │                     │            ├── PA_BRANCH    │
   │    └── R5 (iBGP client)   │                     │            ├── Check Point  │
   │   PA_HQ · FortiGate_HQ_1  │                     │            └── FortiGate_2  │
   └───────────────────────────┘                     └────────────────────────────┘
                        ╲                                       ╱
                         ╲      Out-of-Band Management         ╱
                          ╲     192.168.230.0/24             ╱
                           ╲   Switch_MGMT · Linux_MGMT     ╱
                            └──────────── (jump host) ─────┘
```

### Autonomous Systems

| AS | Role | Devices | Key Functions |
|----|------|---------|---------------|
| **65001** | Headquarters | R1 (RR), R3, R5, PA_HQ, FortiGate_HQ_1 | iBGP core with Route Reflector, OSPF underlay, MP-BGP IPv6, route aggregation |
| **65002** | Branch | R2, R4, PA_BRANCH, Check Point, FortiGate_2 | iBGP, OSPF underlay, AS-Path Prepending, multi-vendor firewall edge |
| **65003** | Transit ISP | R_ISP | eBGP transit between HQ and Branch, eBGP-multihop to loopback |

### Inter-AS Connectivity

- **eBGP:** R1↔R_ISP, R2↔R_ISP, R1↔R2 (direct), and an eBGP-multihop session between R1 and R_ISP loopbacks.
- **iBGP (AS65001):** R1 acts as a Route Reflector for R3 and R5 (peer-group, `next-hop-self`, loopback-sourced sessions).
- **iBGP (AS65002):** R2↔R4.
- **Underlay:** OSPFv2 carries IPv4 loopbacks; OSPFv3 carries IPv6 loopbacks for MP-BGP.

---

## BGP Feature Stack

Implemented and verified in the lab:

- **eBGP & iBGP** with loopback-sourced peering and `next-hop-self`
- **Route Reflector** with two clients — verified via `Originator-ID` and `Cluster-List` attributes
- **Peer-groups** for scalable iBGP client configuration
- **OSPFv2 / OSPFv3 underlay** providing loopback reachability for BGP and MP-BGP
- **MP-BGP IPv6** unicast address family over the same iBGP sessions
- **Route aggregation** — `aggregate-address 10.0.0.0/8 summary-only as-set` (AS_SET preserves loop prevention)
- **Local Preference** — inbound route-map to prefer a specific path
- **AS-Path Prepending** — outbound route-map to influence return-path selection
- **Best-path selection** demonstrated live (AS-Path length, then lowest neighbor address as final tiebreaker)

---

## IPsec VPN Overlay

Five tunnels across three vendors, all over the BGP-routed underlay:

| # | Tunnel | Endpoints | Protected Subnets | Crypto |
|---|--------|-----------|-------------------|--------|
| 1 | PA ↔ PA | PA_HQ ↔ PA_BRANCH | 192.168.10/20 ↔ 192.168.30 | IKEv1, AES-256, SHA-256, DH14 |
| 2 | PA ↔ Check Point | PA_HQ ↔ CP_BRANCH | 192.168.10 ↔ 192.168.40 | IKEv1, AES-256, SHA-256, DH2 + PFS |
| 3 | PA ↔ FortiGate | PA_HQ ↔ FortiGate_2 | 192.168.10 ↔ 192.168.60 | IKEv1, AES-256, SHA-256, DH14 + PFS |
| 4 | FortiGate ↔ FortiGate | FortiGate_HQ_1 ↔ FortiGate_2 | 192.168.50 ↔ 192.168.60 | IKEv1, AES-256, SHA-256, DH14 |

**Key interoperability insight:** PA *Proxy-IDs*, Check Point *Encryption Domains*, and FortiGate *Phase 2 Selectors* are the same concept under different names. When one peer offers a broader traffic selector than the other (e.g. a `/16` against a `/24`), Phase 2 Quick Mode fails while Phase 1 stays up. This is documented as a Golden Scenario (see below).

---

## GlobalProtect Remote Access VPN

A client VPN on PA_HQ demonstrating remote-worker connectivity:

- **Portal + Gateway** on the WAN interface, with self-signed CA and server certificates and an SSL/TLS service profile
- **Local-database authentication**
- **Client IP pool** `10.20.20.0/24`
- **Split tunneling** — corporate subnets routed through the tunnel; collaboration apps (Zoom, Teams, YouTube) excluded so they egress locally

App-based split tunneling reduces gateway load — a practical pattern for scaling work-from-home access.

---

## Troubleshooting Methodology

Every issue in this lab was diagnosed with the same evidence-first flow rather than guesswork:

```
Routing  →  NAT  →  Firewall Policy  →  VPN (Phase 1 / Phase 2)  →  Packet Capture
```

Cross-vendor tooling used at each layer:

| Task | Palo Alto | Check Point | FortiGate |
|------|-----------|-------------|-----------|
| Packet capture | Monitor → Packet Capture (staged) | `fw monitor -e "..."` (i/I/o/O stages) | `diagnose sniffer packet` |
| Session / flow trace | `show session id` | `fw tab -t connections` | `diagnose debug flow` |
| VPN status | `show vpn ipsec-sa` | `vpn tu` | `diagnose vpn tunnel list` |
| Policy / drops | Traffic log | `fw ctl zdebug + drop` | `diagnose debug flow` |

The **Check Point `fw monitor` four-stage model** (`i` pre-inbound, `I` post-inbound, `o` pre-outbound, `O` post-outbound) is a recurring anchor: a packet seen at `i` but not `I` is dropped on inbound inspection — the direct equivalent of a staged PA capture.

---

## Golden Scenarios & Failure Library

Each significant failure is documented as a reproducible case study — symptoms, investigation steps, packet evidence, root cause, fix, and a concise interview summary.

| ID | Scenario | Root Cause | Layer |
|----|----------|-----------|-------|
| **GS2** | PA ↔ Check Point VPN — Phase 1 up, Phase 2 down | Encryption Domain (`/16`) broader than PA Proxy-ID (`/24`) → Quick Mode traffic-selector mismatch | VPN / Phase 2 |
| **FL-BGP** | BGP session Established but no routes received | Outbound prefix-list silently filtered the advertisement | Routing / BGP |
| **FL-MPBGP** | MP-BGP IPv6 session would not establish | Loopbacks not advertised into OSPFv3 → peers unreachable | Underlay / IPv6 |
| **FL-MSS** | HTTP works over VPN, HTTPS hangs | TCP MSS + ESP overhead exceeded MTU → fragmentation dropped the large TLS certificate packet (fixed with MSS clamping) | VPN / MTU |

See [`failure-library/`](failure-library/) for full write-ups.

---

## Repository Structure

```
network-security-lab/
├── README.md
├── diagrams/
│   └── NetSec_Lab_Topology.drawio      # full topology (underlay + overlay)
├── configs/
│   ├── routers/                        # R1–R5, R_ISP (Cisco IOS)
│   ├── switches/                       # Switch_HQ, Switch_MGMT
│   ├── palo-alto/                      # PA_HQ, PA_BRANCH (exported XML)
│   ├── checkpoint/                     # CP_BRANCH (Gaia clish)
│   ├── fortigate/                      # FortiGate_1, FortiGate_2
│   └── endpoints/                      # Linux / VPC setup
├── docs/
│   ├── bgp-design.md                   # AS layout, RR, path selection
│   ├── vpn-overlay.md                  # tunnel matrix, crypto, proxy-IDs
│   ├── checkpoint-vs-paloalto.md       # architecture & terminology mapping
│   ├── fortigate-cli.md                # diagnose toolset reference
│   └── globalprotect.md                # portal/gateway/split-tunnel
├── failure-library/
│   ├── GS2_pa_cp_phase2.md
│   ├── FL_bgp_no_routes.md
│   ├── FL_mpbgp_loopback_ospfv3.md
│   └── FL_mss_clamping.md
└── captures/                           # Wireshark .pcap evidence
```

---

## Lab Environment

- **EVE-NG** on **VMware Workstation** (Ubuntu host)
- **Out-of-band management:** all devices reachable on `192.168.230.0/24` via a dedicated management switch and a **Linux jump host** running Python + Netmiko
- **Images:** Cisco vIOS 15.9, PAN-OS 10.1, Check Point R81 (T392), FortiOS 7.2

---

## Key Takeaways

- The same IPsec concepts — IKE Phase 1, Phase 2 Quick Mode, and traffic selectors — apply across every vendor; only the terminology and CLI differ. Being able to map them is what makes multi-vendor troubleshooting fast.
- BGP best-path selection is deterministic. Reading `show ip bgp <prefix>` and reasoning through the tiebreakers beats trial and error every time.
- The underlay must converge before any overlay can work — a lesson learned firsthand when MP-BGP failed purely because loopbacks weren't in OSPFv3.
- Good troubleshooting is evidence-driven: correlate routing table, firewall session, policy log, and packet capture before changing anything.

---

## Contact

**Matan Gonen** — Network Security Specialist
[linkedin.com/in/matan-gonen](https://linkedin.com/in/matan-gonen)
