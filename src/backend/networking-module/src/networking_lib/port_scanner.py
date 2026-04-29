import shared_info

class Scanner():
    __MAX_PORT_NR = 64738

    def __init__(self, shared_info: shared_info.Info):
        self.shared_info = shared_info

    def scan(self):
        for i in range(__MAX_PORT_NR):
            pass

