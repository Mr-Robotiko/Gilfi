import shared_info

def resolve_host(host: str):
    try:
        ip_address = shared_info.socket.getaddrinfo(host, 80)
        return ip_address
    except shared_info.socket.gaierror:
        return None
    
def resolve_hosts(hosts: list):
    ips = []
    for host in hosts:
        ips.append(resolve_host(host))