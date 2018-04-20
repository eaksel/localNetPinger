#!/usr/bin/env python3
import ipaddress, pprint, socket, subprocess, sys, threading, time

def get_ip():
    """
    Get the IP address used to access the local network of the host.
    """
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        s.connect(('1.1.1.1', 1))
        ip = s.getsockname()[0]
    except:
        print("Couldn't find suitable IP address, exiting!" )
        sys.exit(1)
    finally:
        s.close()
    return ip

def get_os():
    """
    Get the OS platform of the host (Windows/Linux).
    """
    my_os = sys.platform
    if "win" in my_os.lower():
        return "windows"
    elif "linux" in my_os.lower():
        return "linux"
    else:
        print("The operating system of this host couldn't be determined.")
        sys.exit(1)

def get_netmask():
    """
    Get the netmask associated with the IP address retrieved by the "get_ip" function.
    """
    if host_os == "windows":
        proc = subprocess.Popen('ipconfig',stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if host_ip.encode() in line:
                break
        return proc.stdout.readline().split()[-1].decode()
 
    elif host_os == "linux":
        proc = subprocess.Popen(["ip", "a"],stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if host_ip.encode() in line:
                break
        return line.split()[1].decode().split("/")[1]

def get_ptr(host):
    """
    Function to return the reverse dns from an IP address using the socket module.
    If ht reverse dns name isn't found, returns the string "N/A".
    """
    try:
        ptr = socket.gethostbyaddr(str(host))
        ptr = ptr[0]
        return ptr
    except socket.herror:
        ptr = "N/A"
        return ptr

def ping_ptr(host):
    """
    Send ping using the subprocess module.
    Do a reverse DNS lookup for each IP.
    The variable "host_os" must be set to either "windows" or "linux".
    """
    if host_os == "windows":
        proc = subprocess.Popen(["ping", "-n", "1", "-w", "1000",  str(host)], stdout=subprocess.PIPE).stdout.read()
        if "ms" in proc.decode(encoding="utf_8", errors="ignore"):
            host_rdns = get_ptr(host)
            icmp_alive.append({str(host): host_rdns})
        else:
            host_rdns = get_ptr(host)
            icmp_unknown.append({str(host): host_rdns})
    elif host_os == "linux":
        proc = subprocess.Popen(["ping", "-c", "1", "-w", "1", str(host)], stdout=subprocess.PIPE).stdout.read()
        if "100%" in proc.decode(encoding="utf_8", errors="ignore"):
            host_rdns = get_ptr(host)
            icmp_unknown.append({str(host): host_rdns})
        else:
            host_rdns = get_ptr(host)
            icmp_alive.append({str(host): host_rdns})

host_name = socket.gethostname()
host_ip = get_ip()
host_os = get_os()
host_netmask = get_netmask()
my_ip = ipaddress.IPv4Interface("{}/{}".format(host_ip, host_netmask))
my_network = my_ip.network
my_network_hosts = list(my_network.hosts())

icmp_alive = []
icmp_unknown = []

print("-"*80)
print("{} has the IP address: {}, its network is {}.".format(host_name, host_ip, my_network))
print("This network can have up to {} hosts.".format(len(my_network_hosts)))
print("First IP address: {}, last IP address: {}.".format(my_network_hosts[0], my_network_hosts[-1]))
print("-"*80)
print()
input("I'll start pinging, press 'Enter' to continue (^C to abort).\n")

for host in my_network_hosts:
    threading.Thread(target=ping_ptr,args=(host,)).start()

i = 15
while i > 0:
    print("Scan done in ", i, " sec")
    time.sleep(1)
    i -= 1

print("The scan is done!\n")
print("{} host(s) replied to our ICMP Echo Request: ".format(len(icmp_alive)))
pprint.pprint(icmp_alive)
print()
print("{} host(s) DIDN'T reply to our ICMP Echo Request: ".format(len(icmp_unknown)))
pprint.pprint(icmp_unknown)
print("Beware: this doesn't mean that these IPs are available!\n")

input("Press 'Enter' to quit.")
sys.exit(0)