# localNetPinger.py

This script does the following:

* Retrieves:
    * Hostname
    * IP Address/Netmask
    * Network Address
    * List of possible host IP Addresses
    * OS Type (Windows / Linux)

Once the necessary informations gathered, it sends an **ICMP Echo Request** to every possible host in the network.
Finally it prints a list of IPs that replied with an **ICMP Echo Reply**, and a second list with the other IPs.

*Tested on Debian 9 and Windows 10*