import socket
import dns.resolver

# Configure a robust resolver using Google and Cloudflare
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
resolver.lifetime = 5.0
resolver.timeout = 5.0

original_getaddrinfo = socket.getaddrinfo

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # Pass through for IP addresses (basic check)
    try:
        socket.inet_aton(host)
        return original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        pass # Not an IPv4 address

    try:
        # Prioritize IPv4 (A record)
        answers = resolver.resolve(host, 'A')
        ip = answers[0].to_text()
        # print(f"DEBUG: Resolved {host} to {ip} using dnspython")
        return original_getaddrinfo(ip, port, family, type, proto, flags)
    except Exception as e:
        # Fallback to system DNS if custom fails (or if it's localhost, etc.)
        # print(f"DEBUG: Custom DNS failed for {host}: {e}, falling back.")
        return original_getaddrinfo(host, port, family, type, proto, flags)

def patch():
    print("PATCH: Applying custom DNS patch (dnspython -> 8.8.8.8)")
    socket.getaddrinfo = patched_getaddrinfo
