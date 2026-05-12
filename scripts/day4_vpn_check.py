# /home/lab/day4_vpn_check.py
from netmiko import ConnectHandler
import re

def check_vpn(host, label):
    print(f"\n[{label}] Connecting...")
    try:
        conn = ConnectHandler(
            device_type="paloalto_panos",
            host=host,
            username="admin",
            password="MatanGG!",
        )

        # Phase 1 - IKE SA
        ike_out = conn.send_command("show vpn ike-sa")
        p1_ok   = "established" in ike_out.lower()
        print(f"  {'V' if p1_ok else 'X'} Phase 1 (IKE) - "
              f"{'ESTABLISHED' if p1_ok else 'DOWN'}")
        if not p1_ok:
            for line in ike_out.split("\n"):
                if any(w in line.lower() for w in ["init","error","no sa"]):
                    print(f"     ? {line.strip()}")

        # Phase 2 - IPsec SA
        ipsec_out = conn.send_command("show vpn ipsec-sa")
        match = re.search(r'(\d+) ipsec sa found', ipsec_out.lower())
        p2_ok = bool(match and int(match.group(1)) > 0)
        print(f"  {'V' if p2_ok else 'X'} Phase 2 (IPsec) - "
              f"{'ACTIVE' if p2_ok else 'DOWN'}")

        # Flow counters - ENC/DEC
        flow_out = conn.send_command("show vpn flow")
        for line in flow_out.split("\n"):
            if any(w in line.lower() for w in ["encap","decap","encrypt","decrypt"]):
                print(f"     ? {line.strip()}")

        conn.disconnect()
        return p1_ok and p2_ok

    except Exception as e:
        print(f"  X Cannot reach {label}: {e}")
        return False


print("=" * 45)
print("  VPN HEALTH CHECK")
print("=" * 45)

hq_ok     = check_vpn("192.168.230.130", "PA_HQ")     # UNSPECIFIED
branch_ok = check_vpn("192.168.230.131", "PA_BRANCH")  # UNSPECIFIED

print("\n" + "=" * 45)
if hq_ok and branch_ok:
    print("GREEN VPN OK - Both sides UP")
elif hq_ok or branch_ok:
    print("YELLOW VPN PARTIAL - One side DOWN")
else:
    print("RED VPN DOWN - Both sides report issues")
print("=" * 45)