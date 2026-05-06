import re

from networking_lib.hostname_resolver import Resolver

#TODO:
# - Add validate_ip_regex
# - Omit hostname_regex after validate_ip_regex is implemented

class Info():
    # Private
    __hostname_regex = "[a-zA-Z]+"
    __r = Resolver()

    # Public
    ipv4_target = '127.0.0.1'
    ipv6_target = ''

    def __init__(self):
        pass

    def set_ip(self, ip):
        if re.search(self.__hostname_regex, ip):
            self.ipv4_target = self.__r.resolve_host(ip)
        else:
            self.ipv4_target = ip