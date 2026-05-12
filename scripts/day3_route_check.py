# /home/lab/day3_route_check.py
from netmiko import ConnectHandler

def check_routes(conn, checks, device_name):

    output = conn.send_command("show ip route")
    passed = 0
    for description, search_string in checks:
        found = search_string in output
        icon  = "V" if found else "X"
        print(f"  {icon} {device_name} | {description}")
        if found:
            passed += 1
    return passed


ISP_CHECKS = [
    ("Branch WAN link reachable",  "10.0.0.4"),
    ("HQ WAN link reachable",      "10.0.0.0"),
    ("Default route exists",       "0.0.0.0"),
]

print("=" * 45)
print("  ROUTE CHECK")
print("=" * 45)

try:
    conn = ConnectHandler(
        device_type="cisco_ios",
        host="192.168.230.132",
        username="admin",
        password="admin",
    )
    passed = check_routes(conn, ISP_CHECKS, "R_ISP")
    conn.disconnect()

    total = len(ISP_CHECKS)
    print(f"\nResult: {passed}/{total}")
    if passed == total:
        print(" Routing OK")
    else:
        print(" Routing ISSUE check missing routes")

except Exception as e:
    print(f" Cannot connect to R_ISP: {e}")