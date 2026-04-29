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
            ips.append(resolve_host(host))
