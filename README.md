# localNetPinger.py

*Written for Python 3.7+ using only the standard library*

*Tested on Debian 10, Windows 10 and macOS 10.15*

## What is localNetPinger.py ?

localNetPinger is a script that pings all the hosts on your local network. It does so by doing the following:

- Retrieves:
  - Hostname
  - OS Type (Windows / Linux / macOS)
  - IP Address/Netmask
  - Network Address
  - List of possible host IP Addresses

Once the necessary informations gathered, it sends an **ICMP Echo Request** to every possible host in the network.
Finally it prints a list of IPs that replied with an **ICMP Echo Reply**, and a second list with the other IPs.

## How to use localNetPinger.py

Run the script using Python 3

```sh
# On windows
python localNetPinger.py

# On Linux and macOS
python3 localNetPinger.py
```

Running localNetPinger.py on macOS may require you to raise the number of simultaneous open files.
To do so use the command `ulimit -n 1024` for example to raise the limit to 1024 open files.
