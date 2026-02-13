import socket
import requests
import json
import ssl

# Google Public DNS IP for DoH (to bypass DNS resolution for the DNS server itself)
GOOGLE_DNS_IP = "8.8.8.8" 
# We use the JSON API which is simpler to use with requests
DOH_URL = f"https://{GOOGLE_DNS_IP}/resolve"

original_getaddrinfo = socket.getaddrinfo

# Cache to avoid hitting the API too much
dns_cache = {}

def resolve_doh(hostname):
    """Resolves hostname to IP using Google DNS-over-HTTPS JSON API via direct IP."""
    if hostname in dns_cache:
        return dns_cache[hostname]

    try:
        # verify=False because the Cert matches dns.google, not 8.8.8.8
        # This is safe because we trust the hardcoded IP 8.8.8.8 to be Google.
        response = requests.get(
            DOH_URL,
            params={"name": hostname, "type": "A"},
            verify=False, 
            timeout=2.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Answer" in data:
                for answer in data["Answer"]:
                    if answer["type"] == 1: # A record
                        ip = answer["data"]
                        # print(f"DEBUG: DoH Resolved {hostname} -> {ip}")
                        dns_cache[hostname] = ip
                        return ip
    except Exception as e:
        print(f"DEBUG: DoH Failed for {hostname}: {e}")
    
    return None

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # Pass through for IP addresses and localhost
    if host == "localhost" or host == "127.0.0.1" or host == "::1":
         return original_getaddrinfo(host, port, family, type, proto, flags)

    try:
        socket.inet_aton(host)
        return original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        pass 

    # Try DoH First
    ip = resolve_doh(host)
    if ip:
        try:
             # Return the result for the resolved IP
             # We must pass the IP as the host to the original function
            return original_getaddrinfo(ip, port, family, type, proto, flags)
        except Exception:
            pass
            
    # Fallback to system DNS
    return original_getaddrinfo(host, port, family, type, proto, flags)

def patch():
    print("PATCH: Applying blocked-port-resilient DNS patch (DoH via 8.8.8.8)")
    # Monkey patch
    socket.getaddrinfo = patched_getaddrinfo
