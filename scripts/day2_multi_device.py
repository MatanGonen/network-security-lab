
from netmiko import ConnectHandler

DEVICES = [
    {
        "label":       "R_ISP",
        "device_type": "cisco_ios",
        "host":        "192.168.230.132",
        "username":    "admin",
        "password":    "admin",
        "command":     "show ip route",
    },
    {
        "label":       "Switch_HQ",
        "device_type": "cisco_ios",
        "host":        "192.168.230.133", 
        "username":    "admin",
        "password":    "admin",
        "command":     "show interfaces status",
    },
    {
        "label":       "PA_HQ",
        "device_type": "paloalto_panos",
        "host":        "192.168.230.130",   
        "username":    "admin",
        "password":    "MatanGG!",
        "command":     "show routing route",
    },
    {
        "label":       "PA_BRANCH",
        "device_type": "paloalto_panos",
        "host":        "192.168.230.131",  
        "username":    "admin",
        "password":    "MatanGG!",
        "command":     "show routing route",
    },
]

report_path = "/home/lab/routing_report.txt"

with open(report_path, "w") as report:
    for dev in DEVICES:
        print(f"Connecting to {dev['label']}...")
        try:
            conn = ConnectHandler(**{k: v for k, v in dev.items() if k not in ("label", "command")})
            output = conn.send_command(dev["command"])
            conn.disconnect()
            status = "OK"
        except Exception as e:
            output = f"ERROR: {e}"
            status = "FAILED"

        line = f"\n{'='*50}\n[{status}] {dev['label']} ({dev['host']})\n"
        print(line.strip())
        report.write(line)
        report.write(output + "\n")

print(f"\nReport saved: {report_path}")


print("<<<<<<<<<<<<<<<<<<<<<Done>>>>>>>>>>>>>>>>>>>>")

