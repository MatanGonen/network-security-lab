from netmiko import ConnectHandler

Router = {
    "device_type": "cisco_ios",   
    "host": "192.168.230.132",           
    "username": "admin",
    "password": "admin",
    "port": 22,
}
Switch = {
    "device_type": "cisco_ios",    
    "host": "192.168.230.133",           
    "username": "admin",
    "password": "admin",
    "port": 22,
}
PA_HQ = {
    "device_type": "paloalto_panos",    
    "host": "192.168.230.130", 
    "username": "admin",
    "password": "MatanGG!",
    "port": 22,
}
PA_BRANCH = {
    "device_type": "paloalto_panos",    
    "host": "192.168.230.131",           
    "username": "admin",
    "password": "MatanGG!",
    "port": 22,
}
LINUX_LAN = {
    "device_type": "linux",    
    "host": "192.168.230.69",
    "username": "root",
    "password": "eve",
    "port": 22,
}
LINUX_DMZ = {
    "device_type": "linux",    
    "host": "192.168.230.70",
    "username": "root",
    "password": "eve",
    "port": 22,
}
LINUX_BRANCH = {
    "device_type": "linux",    
    "host": "192.168.230.71",
    "username": "root",
    "password": "eve",
    "port": 22,
}

print("Connecting to R_ISP...")
connection = ConnectHandler(**Router)

output1 = connection.send_command("show ip route")
output2 = connection.send_command("show ip interface brief")
print(output1)
print(output2)

connection.disconnect()
print("Done.")

