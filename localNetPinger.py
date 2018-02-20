#!/usr/bin/env python
import os, sys, subprocess, socket, ipaddress, threading, time

host_name = socket.gethostname()

def get_ip():
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        s.connect(('1.1.1.1', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

host_ip = get_ip()

def get_os():
    my_os = sys.platform
    if "win" in my_os:
        return "windows"
    elif "linux" in my_os:
        return "linux"
    else:
        print("The operating system of this host couldn't be determined.")
        sys.exit(1)

host_os = get_os()

def get_netmask():
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

host_netmask = get_netmask()

my_ip = ipaddress.IPv4Interface("{}/{}".format(host_ip, host_netmask))
my_network = my_ip.network
my_network_hosts = list(my_network.hosts())

print()
print("-"*110)
print("{} has the IP address: {}, it's network is {}.".format(host_name, host_ip, my_network))
print("This network can have up to {} hosts.".format(len(my_network_hosts)))
print("The first IP address: {}, last IP address: {}.".format(my_network_hosts[0], my_network_hosts[-1]))
print("-"*110)
print()
input("I'll start pinging, press 'Enter' to continue (^C to abort).")

icmp_alive = []
icmp_unknown = []

def ping(host):
    if host_os == "windows":
        proc = subprocess.Popen(["ping", "-n", "1", "-w", "1",  str(host)], stdout=subprocess.PIPE).stdout.read()
        if "ms" in proc.decode(encoding="utf_8", errors="ignore"):
            icmp_alive.append(host)
        else:
            icmp_unknown.append(host)
    elif host_os == "linux":
        proc = subprocess.Popen(["ping", "-c", "1", "-w", "1", str(host)], stdout=subprocess.PIPE).stdout.read()
        if "100%" in proc.decode(encoding="utf_8", errors="ignore"):
            icmp_unknown.append(host)
        else:
            icmp_alive.append(host)


for host in my_network_hosts:
    threading.Thread(target=ping,args=(host,)).start()

print()
i = 5
while i > 0:
    print("Scan done in ", i, " sec")
    time.sleep(1)
    i -= 1
print()

alive = []
dead = []

for host in icmp_alive:
    host = str(host)
    alive.append(host)

for host in icmp_unknown:
    host = str(host)
    dead.append(host)

alive.sort()
dead.sort()

print("The scan is done!\n")
print("{} host(s) replied to our ICMP Echo Request: ".format(len(alive)))
print(alive)
print()
print("{} host(s) DIDN'T reply to our ICMP Echo Request: ".format(len(dead)))
print(dead)
print("Beware: this doesn't mean that these IPs are available!")

input("Press 'Enter' to quit.")
sys.exit(0)