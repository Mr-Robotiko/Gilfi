import networking_lib.shared_info
import socket
import json

# TODO:
#   - Detangle functions to use self instead of return
#   - Use return for error handeling

class Scanner():
    '''
    Scanner class with following variables and functions:
    * Private:
        * __MAX_PORT_NR:            Maximum number of ports
        * __PROTOCOLL_TRANSLATION:  Dict for looking up used SocketKind names
        * __ip:                     IP to scan
        * __scanned_ports:          Dictionary of all scanned ports with the key being the ports and the value being 
                                    another dictionary with the key being "UDP" and/or "TCP" and value being their respective status
                                    __scanned_ports[port][]
        * __shared_info:            Shared info object for accessing shared info between networking modules
        * __range_input:            List of length 1 or 2 of the ports to be scanned
    '''
    __MAX_PORT_NR = 64738
    __PROTOCOLL_TRANSLATION = {1: "TCP", 2: "UDP"}

    def __init__(self, shared_info: shared_info.Info, range_input=[0], address_family="IPV4", connection_type="BOTH"):
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
            self.__ip = self.__shared_info.ipv4_target
            return socket.AF_INET

        if str.upper(address_family) == "IPV6":
            self.__ip = self.__shared_info.ipv6_target
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

    def __socket_factory(self) -> socket.socket:
        '''
        Generator for opening sockets.

        :return: Generator object to iterate through sockets depending on the scan type (TCP/UDP/BOTH)
        :rtype: generator
        '''
        for protocoll in self.__connection_type:
            yield socket.socket(self.__address_family, protocoll)

    def __scan(self) -> None:
        '''
        Performs scan over the given ip, protocoll/s and port range.
        Modifies __scanned_ports accordingly.
        '''

        for sock in self.__socket_factory():
            port_range = self.__parse_range(self.__range_input)
            current_protocoll = self.__PROTOCOLL_TRANSLATION[sock.type]
            for port in port_range:
                status = sock.connect_ex((self.__ip, port))
                if port in self.__scanned_ports:
                    self.__scanned_ports[port][current_protocoll] = status
                else:
                    self.__scanned_ports[port] = {current_protocoll: status}

    def __add_descriptions(self, path) -> None:
        '''
        Iterates through the __scanned_ports dict and appends a description of the form
        [description, status]
        according to a json list that holds that information.

        :param path: Path to the json list
        :type path: str
        '''
        port_range = self.__parse_range(self.__range_input)
        f = open(path)
        full_file = json.loads(f.read())
        for port in port_range:
            #print(str(f"{port}" in full_file['ports']) + " and " + str(port in self.__scanned_ports))
            if port in self.__scanned_ports and f"{port}" in full_file['ports']:
                print(f"add description to port {port}")
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
    debug()
