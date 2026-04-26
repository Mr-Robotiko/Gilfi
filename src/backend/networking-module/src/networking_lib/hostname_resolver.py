class Resolver(s):
    def resolve_host(self, host: str):
        try:
            ip_address = s.getaddrinfo(host, 80)
            return ip_address
        except shared_info.socket.gaierror:
            return "Failed"
    
    def resolve_hosts(self, hosts: list):
        ips = []
        for host in hosts:
            ips.append(resolve_host(host))
