import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class info():
    ip_target = ""
    ip_range_start = ""
    ip_range_end = ""

    def set_ip(self, ip):
        self.ip_target = ip

    def set_ip_range(self, ip_start, ip_end):
        self.ip_range_start = ip_start
        self.ip_range_end = ip_end
