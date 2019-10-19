#!/usr/bin/env python3
import datetime, ipaddress, os, pprint, socket, subprocess, sys, threading, time


def get_ip():
    """
    Get the IP address used to access the local network of the host.
    """
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        s.connect(("1.1.1.1", 1))
        ip = s.getsockname()[0]
    except:
        print("Couldn't find a suitable IP address, exiting!" )
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
        print(f"Your OS is {my_os}, only Windows and Linux are supported.")
        sys.exit(1)


def get_netmask(host_os, host_ip):
    """
    Get the netmask associated with the IP address retrieved by the "get_ip" function.
    """
    if host_os == "windows":
        output = subprocess.run(["ipconfig"], capture_output=True, text=True)
        output = output.stdout.splitlines()
        for i, line in enumerate(output):
            if host_ip in line:
                return output[i+1].split()[-1]

    if host_os == "linux":
        output = subprocess.run(["ip", "a"], capture_output=True, text=True)
        output = output.stdout.splitlines()
        for i, line in enumerate(output):
            if host_ip in line:
                return line.split()[1].split("/")[1]


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


def ping_ptr(host, host_os):
    """
    Send ping using the subprocess module.
    Do a reverse DNS lookup for each IP.
    The variable "host_os" must be set to either "windows" or "linux".
    """
    if host_os == "windows":
        proc = subprocess.Popen(["ping", "-n", "1", "-w", "1000",  str(host)], stdout=subprocess.PIPE).stdout.read()
        if "ms" in proc.decode(encoding="utf_8", errors="ignore"):
            host_rdns = get_ptr(host)
            ping_result(icmp_alive, host, host_rdns)
        else:
            host_rdns = get_ptr(host)
            ping_result(icmp_unknown, host, host_rdns)
    elif host_os == "linux":
        proc = subprocess.Popen(["ping", "-c", "1", "-w", "1", str(host)], stdout=subprocess.PIPE).stdout.read()
        if "100%" in proc.decode(encoding="utf_8", errors="ignore"):
            host_rdns = get_ptr(host)
            ping_result(icmp_unknown, host, host_rdns)
        else:
            host_rdns = get_ptr(host)
            ping_result(icmp_alive, host, host_rdns)


def ping_result(listname, host, hostname):
    listname.append({"ip": str(host), "hostname": hostname})


def beginning(host_name, host_ip, my_network, my_network_hosts):
    print("-"*80)
    print(f"{host_name} has the IP address: {host_ip}, the network is {my_network}.")
    print(f"This network can have up to {len(my_network_hosts)} hosts.")
    print(f"First IP address: {my_network_hosts[0]}, last IP address: {my_network_hosts[-1]}.")
    print("-"*80)
    print()
    input("Press 'Enter' to start pinging (^C to abort).\n")


def ending(icmp_alive, icmp_unknown):
    print("The scan is done!\n")
    print(f"{len(icmp_alive)} host(s) replied to our ICMP Echo Request:")
    pprint.pprint(icmp_alive)
    print()
    print(f"{len(icmp_unknown)} host(s) DIDN'T reply to our ICMP Echo Request:")
    pprint.pprint(icmp_unknown)
    print("Beware: this doesn't mean that these IPs are available!\n")


def export_file(icmp_alive, icmp_unknown):
    now = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d_%H-%M")
    file = "localNetPinger_" + now + ".txt"

    with open(file, "w", encoding="utf-8") as f:
        f.write("Responding to ping: " + str(icmp_alive))
        f.write("\n\n")
        f.write("Silent to ping: " + str(icmp_unknown))
    
    print("File saved to: " + os.path.abspath(file))


def main():
    host_name = socket.gethostname()
    host_ip = get_ip()
    host_os = get_os()
    host_netmask = get_netmask(host_os, host_ip)
    my_ip = ipaddress.IPv4Interface(f"{host_ip}/{host_netmask}")
    my_network = my_ip.network
    my_network_hosts = list(my_network.hosts())

    beginning(host_name, host_ip, my_network, my_network_hosts)

    threads = []
    for host in my_network_hosts:
        proc = threading.Thread(target=ping_ptr, args=(
            host, host_os))
        proc.start()
        threads.append(proc)

    start = time.time()
    print("Scan in progress...")

    for proc in threads:
        proc.join()

    end = time.time()
    print(f"The scan took {end - start} seconds.\n")

    ending(icmp_alive, icmp_unknown)

    while True:
        exp = input("Would you like to export the result to a file ? (y/n)")
        if exp == "y":
            export_file(icmp_alive, icmp_unknown)
            break
        elif exp == "n":
            break

    sys.exit(0)


if __name__ == "__main__":
    icmp_alive = []
    icmp_unknown = []
    main()
