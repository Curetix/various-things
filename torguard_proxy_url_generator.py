import argparse
import sys
import urllib.parse

# Primarily European servers, more servers here: https://torguard.net/network/socks5/
socks_ips = [
    "206.217.216.4",
    "206.217.216.8",
    "89.248.168.20",
    "89.248.168.60",
    "89.248.168.61",
    "89.248.168.63",
    "89.248.168.69",
    "89.248.168.70",
    "89.248.168.71",
    "89.248.168.72",
    "89.248.168.73",
    "89.248.168.112",
    "46.23.78.25"
]
# Available ports: 990, 1080, 1085, 1090
socks_port = 1080

# Primarily European servers, more servers here: https://torguard.net/network/ssl/
https_hosts = [
    "aus.secureconnect.me",
    "bg.secureconnect.me",
    "dn.secureconnect.me",
    "fr.secureconnect.me",
    "ger.secureconnect.me",
    "it.secureconnect.me",
    "nl.secureconnect.me",
    "no.secureconnect.me",
    "pl.secureconnect.me",
    "swiss.secureconnect.me"
]
# Available ports: 23, 489, 465, 993, 282, 778,  592, 7070,
https_port = 489

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TorGuard Proxy Generator")
    parser.add_argument("-u", "--username", help="TorGuard username / email")
    parser.add_argument("-p", "--password", help="TorGuard password")
    args = parser.parse_args()

    if not args.username or not args.password:
        print("Username or password not provided")
        sys.exit(1)

    auth = "%s:%s" % (urllib.parse.quote(args.username), urllib.parse.quote(args.password))

    for ip in socks_ips:
        print("socks5://%s@%s:%s" % (auth, ip, socks_port))

    for host in https_hosts:
        print("https://%s@%s:%s" % (auth, host, https_port))
