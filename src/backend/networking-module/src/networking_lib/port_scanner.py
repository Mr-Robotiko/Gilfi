import shared_info
import socket

class Scanner():
    __MAX_PORT_NR = 64738

    def __init__(self, shared_info: shared_info.Info):
        self.shared_info = shared_info

    def __parse_range(self, range_input) -> range:
        pass

    def scan(self) -> list:
        for i in range(__MAX_PORT_NR):
            pass

