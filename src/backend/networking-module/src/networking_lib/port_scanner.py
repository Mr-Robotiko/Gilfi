import networking_lib.shared_info
import socket

# TODO:
#   - Detangle functions to use self instead of return
#   - Use return for error handeling
#   - Add get_all_ports

class Scanner():
    __MAX_PORT_NR = 64738
    __IP = '127.0.0.1'

    def __init__(self, shared_info: shared_info.Info, range_input=[0], address_family="IPV4", connection_type="BOTH"):
        '''
        Docstring
        '''

        self.__open_ports =  []
        self.shared_info = shared_info
        self.port_range = self.__parse_range(range_input)
        self.address_family = self.__parse_address_type(address_family)
        self.connection_type = self.__parse_connection_type(connection_type)

    def __parse_range(self, range_input) -> range:
        '''
        Returns a range of ports to iterate through. 
        If input is [0] returns range of all ports.

        :param range_input: 1 or 2 item long list of port range
        :type range_input: list
        :return: Range between the given ports
        :rtype: range
        '''

        if len(range_input) == 1:
            if range_input[0] == 0:
                return range(1, self.__MAX_PORT_NR+1)
            return range(range_input, range_input+1)

        # Check if range is valid
        if len(range_input) == 2 and (range_input[1] - range_input[0]) > 1:
            return range(range_input[0], range_input[1]+1)

        print("Wrong usage of function, please consult the documentation")
        return range(0)
            
    
    def __parse_address_type(self, address_family) -> socket.AddressFamily:
        '''
        Sets the internal IP of the class to the IP from shared_info based on the address_family.
        Returns a corresponding AddressFamily for the scanning socket.

        :param address_family: IP-Protocoll of the connection (IPV4/IPV6)
        :type address_family: str
        :return: Corresponding AddressFamily
        :rtype: socket.AddressFamily
        '''

        if str.upper(address_family) == "IPV4":
            self.__IP = self.shared_info.ipv4_target
            return socket.AF_INET

        if str.upper(address_family) == "IPV6":
            self.__IP = self.shared_info.ipv6_target
            return socket.AF_INET6

        print("Please enter a supported address_family [IPV4/IPV6]")
        return -1

    def __parse_connection_type(self, connection_type) -> list[socket.SocketKind]:
        '''
        Returns a corresponding SocketKind for the protocoll.

        :param connection_type: Type of the connection (TCP/UDP/BOTH)
        :type connection_type: str
        :return: Corresponding SocketKind
        :rtype: socket.SocketKind
        '''

        if str.upper(connection_type) == "BOTH":
            return [socket.SOCK_STREAM, socket.SOCK_DGRAM]

        if str.upper(connection_type) == "TCP":
            return [socket.SOCK_STREAM]

        if str.upper(connection_type) == "UDP":
            return [socket.SOCK_DGRAM]

        print("Please enter a supported connection_type [TCP/UDP/BOTH]")
        return -1

    def socket_factory(self):
        '''
        Generator for opening sockets.

        :return: Generator object to iterate through sockets depending on the scan type (TCP/UDP/BOTH)
        :rtype: generator
        '''
        for protocoll in self.connection_type:
            yield socket.socket(self.address_family, protocoll)

    def __scan(self) -> list:
        '''
        Docstring
        '''

        for i in range(__MAX_PORT_NR):
            pass

    def get_open_ports(self):
        return __open_ports

    def start_scan(self):
        pass

def tests():
    shared = networking_lib.shared_info.Info()
    scanner = Scanner(shared)
    sock = scanner.socket_factory()
    print(type(sock))
    for i in sock:
        print(i)

if __name__ == "__main__":
    tests()
