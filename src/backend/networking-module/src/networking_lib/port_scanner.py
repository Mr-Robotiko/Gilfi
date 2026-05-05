import networking_lib.shared_info
import socket
import json

class Scanner():
    '''
    Scanner class with following variables and functions:
    * Private:
        * __MAX_PORT_NR:           Maximum number of ports (65535, the highest valid TCP/UDP port)
        * __PROTOCOL_TRANSLATION:  Dict for looking up used SocketKind names
        * __ip:                     IP to scan
        * __scanned_ports:          Dictionary of all scanned ports with the key being the ports and the value being 
                                    another dictionary with the key being "UDP" and/or "TCP" and value being their respective status
                                    __scanned_ports[port][]
        * __shared_info:            Shared info object for accessing shared info between networking modules
        * __range_input:            List of length 1 or 2 of the ports to be scanned
    '''
    # Bug fix: was 64738, which incorrectly excluded valid ports 64739–65535.
    __MAX_PORT_NR = 65535
    # Bug fix: use SocketKind constants as keys so the lookup works correctly on
    # all platforms (some platforms encode extra flags in sock.type).
    __PROTOCOL_TRANSLATION = {socket.SOCK_STREAM: "TCP", socket.SOCK_DGRAM: "UDP"}

    def __init__(self, shared_info, range_input=[0], address_family="IPV4", connection_type="BOTH"):
        self.__ip = '127.0.0.1'
        self.__scanned_ports = {}
        self.__shared_info = shared_info
        self.__range_input = range_input

        self.__address_family = self.__parse_address_type(address_family)
        self.__connection_type = self.__parse_connection_type(connection_type)

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
            return range(range_input[0], range_input[0]+1)

        # Bug fix: was `> 1`, which incorrectly rejected valid adjacent-port
        # ranges such as [80, 81] (difference == 1).  The correct guard is
        # `>= 1` (or equivalently `range_input[1] >= range_input[0]`).
        if len(range_input) == 2 and (range_input[1] - range_input[0]) >= 1:
            return range(range_input[0], range_input[1]+1)

        raise ValueError(
            f"Invalid range_input {range_input!r}: expected a 1- or 2-element list "
            f"where the second value is >= the first."
        )
            
    
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
            self.__ip = self.__shared_info.ipv4_target
            return socket.AF_INET

        if str.upper(address_family) == "IPV6":
            self.__ip = self.__shared_info.ipv6_target
            return socket.AF_INET6

        # Bug fix: was silently returning -1, which caused a cryptic OSError
        # later when trying to create a socket.  Raise a clear ValueError instead.
        raise ValueError(
            f"Unsupported address_family {address_family!r}. "
            "Please use 'IPV4' or 'IPV6'."
        )

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

        # Bug fix: was silently returning -1, which caused a cryptic TypeError
        # ("'int' object is not iterable") when the value was later iterated in
        # __socket_factory.  Raise a clear ValueError instead.
        raise ValueError(
            f"Unsupported connection_type {connection_type!r}. "
            "Please use 'TCP', 'UDP', or 'BOTH'."
        )

    def __scan(self) -> None:
        '''
        Performs scan over the given ip, protocoll/s and port range.
        Modifies __scanned_ports accordingly.

        Bug fixes applied here:
        * A TCP socket that has been successfully connected cannot be reused for
          a second connect() call on a different port.  A fresh socket must be
          created for every port.
        * Sockets were never closed, leaking OS file descriptors.  Each socket
          is now closed in a finally block immediately after use.
        * __PROTOCOLL_TRANSLATION is now keyed by SocketKind (not raw int) so
          the lookup is correct on all platforms.
        '''

        for protocol in self.__connection_type:
            port_range = self.__parse_range(self.__range_input)
            current_protocol = self.__PROTOCOL_TRANSLATION[protocol]
            for port in port_range:
                # Bug fix: create a new socket per port.  Reusing one socket
                # across all ports fails for TCP because a connected socket
                # cannot reconnect to a different destination.
                sock = socket.socket(self.__address_family, protocol)
                try:
                    status = sock.connect_ex((self.__ip, port))
                finally:
                    # Bug fix: always close the socket to avoid file-descriptor leaks.
                    sock.close()
                if port in self.__scanned_ports:
                    self.__scanned_ports[port][current_protocol] = status
                else:
                    self.__scanned_ports[port] = {current_protocol: status}

    def __add_descriptions(self, path) -> None:
        '''
        Iterates through the __scanned_ports dict and appends a description of the form
        [description, status]
        according to a json list that holds that information.

        :param path: Path to the json list
        :type path: str
        '''
        port_range = self.__parse_range(self.__range_input)
        # Bug fix: the file was opened but never closed, leaking the file
        # descriptor.  Use a `with` statement to guarantee closure.
        with open(path) as f:
            full_file = json.loads(f.read())
        for port in port_range:
            if port in self.__scanned_ports and f"{port}" in full_file['ports']:
                description = full_file['ports'][f"{port}"]
                # TODO: Handle double descriptions better
                if type(description) == list:
                    description = description[0]
                self.__scanned_ports[port]["Description"] = [description['description'], description['status']]

    def get_all_ports(self) -> dict:
        '''
        Returns the a dictionary of all scanned ports.

        :return: Dictionary of all scanned ports
        :rtype: dict
        '''
        return self.__scanned_ports

    def start_scan(self, path_to_port_list):
        self.__scan()
        self.__add_descriptions(path_to_port_list)

def debug():
    print("Port scanner debug Info: ")
    shared = networking_lib.shared_info.Info()
    scanner = Scanner(shared)
    scanner.start_scan("data/ports/ports.json")

if __name__ == "__main__":
    pass
    #debug()