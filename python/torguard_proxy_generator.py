import argparse
import sys
import urllib.parse

# Primarily European servers, more servers here: https://torguard.net/network/socks5/
socks_ips = [
    "206.217.216.4",
    "206.217.216.8",
    "46.23.78.24",
    "46.23.78.25"
]
# Available ports: 1080, 1085, 1090
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

    if not args.username or args.password:
        print("Username or password not provided")
        sys.exit(1)

    auth = "%s:%s" % (urllib.parse.quote(args.username), urllib.parse.quote(args.password))

    for ip in socks_ips:
        print("socks5://%s@%s:%s" % (auth, ip, socks_port))

    for host in https_hosts:
        print("https://%s@%s:%s" % (auth, host, https_port))
