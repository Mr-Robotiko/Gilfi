import socket
import re

from hostname_resolver import Resolver

#TODO:
# - Add validate_ip_regex
# - Omit hostname_regex after validate_ip_regex is implemented

class Info():
    # Private
    __hostname_regex = "[a-zA-Z.]*"
    __r = resolver(s)

    # Public
    ip_target = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_ip(self, ip):
        if re.search(hostname_regex, ip):
            self.ip_target = __r.resolve_host(ip)
        else:
            self.ip_target = ip
