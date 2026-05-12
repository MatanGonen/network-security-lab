# /home/lab/day5_health_check.py
from netmiko import ConnectHandler
import subprocess
import datetime
import re

# CONFIG
R_ISP_IP     = "192.168.230.132"
PA_HQ_IP     = "192.168.230.130"
PA_BRANCH_IP = "192.168.230.131"
SSH_USER     = "admin"
SSH_PASS     = "admin"
PA_PASS      = "MatanGG!"

PING_TARGETS = [
    ("Linux_DMZ",    "192.168.230.70"),
    ("Linux_BRANCH", "192.168.230.71"),
    ("R_ISP WAN",    "10.0.0.1"),
]

results = []

def result(label, ok, detail=""):
    icon = "[OK]" if ok else "[FAIL]"
    msg  = f"  {icon} {label}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append((label, ok))
    return ok

def connect(ip, dtype="cisco_ios", password=None):
    return ConnectHandler(
        device_type=dtype, host=ip,
        username=SSH_USER,
        password=password or SSH_PASS
    )

def ping(ip):
    r = subprocess.run(
        ["ping", "-c", "3", "-W", "2", ip],
        capture_output=True, text=True
    )
    return r.returncode == 0

print("=" * 50)
print("  GOLDEN SCENARIO HEALTH CHECK")
print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 50)

# 1. ROUTING
print("\n[1/4] Routing (R_ISP)")
try:
    conn = connect(R_ISP_IP)
    rt   = conn.send_command("show ip route")
    conn.disconnect()
    result("Route to Branch WAN (10.0.0.4)", "10.0.0.4" in rt)
    result("Route to HQ WAN (10.0.0.0)",     "10.0.0.0" in rt)
    result("Default route (0.0.0.0)",         "0.0.0.0"  in rt)
except Exception as e:
    result("R_ISP reachable", False, str(e))

# 2. VPN
print("\n[2/4] VPN (PA_HQ)")
try:
    conn  = connect(PA_HQ_IP, "paloalto_panos", PA_PASS)
    ike   = conn.send_command("show vpn ike-sa")
    ipsec = conn.send_command("show vpn ipsec-sa")
    conn.disconnect()
    result("Phase 1 IKE -- Established", "established" in ike.lower())
    match = re.search(r'(\d+) ipsec sa found', ipsec.lower())
    result("Phase 2 IPsec -- Active", bool(match and int(match.group(1)) > 0))
except Exception as e:
    result("PA_HQ reachable", False, str(e))

# 3. CONNECTIVITY (PING)
print("\n[3/4] Connectivity (Ping from MGMT)")
for label, ip in PING_TARGETS:
    result(f"Ping {label} ({ip})", ping(ip))

# 4. APP LAYER (curl HTTP)
print("\n[4/4] Application Layer (HTTP to DMZ)")
curl = subprocess.run(
    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
     "--max-time", "5", "http://192.168.230.70"],
    capture_output=True, text=True
)
http_code = curl.stdout.strip()
http_ok   = http_code == "200"
result(f"HTTP GET Linux_DMZ (code={http_code})", http_ok)

# SUMMARY
print("\n" + "=" * 50)
passed = sum(1 for _, ok in results if ok)
total  = len(results)
print(f"  RESULT: {passed}/{total} checks passed")
failed = [label for label, ok in results if not ok]
if failed:
    print("\n  Failed checks:")
    for f in failed:
        print(f"    - {f}")
    print("\n  Troubleshoot order:")
    print("    Routing -> VPN Phase1 -> Phase2 -> NAT -> FW Policy")
else:
    print("  ALL OK -- Network Healthy")
print("=" * 50)

# Save to log
with open("/home/lab/health_log.txt", "a") as log:
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    log.write(f"{ts} | {passed}/{total} | "
              f"Failed: {failed if failed else 'none'}\n")