import socket

class Resolver(object):
    def __init__(self):
        pass

    def resolve_host(self, host: str):
        try:
            ip_address = socket.gethostbyname(host)
            return ip_address
        except socket.gaierror:
            return "Failed"
    
    def resolve_hosts(self, hosts: list):
        ips = []
        for host in hosts:
            # Bug fix: was calling bare `resolve_host(host)` (NameError);
            # must be `self.resolve_host(host)`.
            ips.append(self.resolve_host(host))
        # Bug fix: was missing a return statement, so the method always
        # returned None instead of the populated list.
        return ips
