"""
Unit tests for the port scanner backend (networking_lib).

Each test is labelled with the bug it covers so the mapping between
bug reports and regression tests is explicit.
"""

import socket
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import sys
import os

# Make the installed package importable when running from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                '../../src/backend/networking-module/src'))

from networking_lib.port_scanner import Scanner
from networking_lib.shared_info import Info
from networking_lib.hostname_resolver import Resolver


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_shared_info(ipv4='127.0.0.1', ipv6='::1'):
    """Return a minimal shared_info stub."""
    info = MagicMock()
    info.ipv4_target = ipv4
    info.ipv6_target = ipv6
    return info


# ---------------------------------------------------------------------------
# Bug 1 – __MAX_PORT_NR was 64738 instead of 65535
# ---------------------------------------------------------------------------

class TestMaxPortNumber(unittest.TestCase):
    """Bug 1: highest valid port (65535) was silently excluded."""

    def test_max_port_nr_is_65535(self):
        """Scanner.MAX_PORT_NR must equal 65535 (2^16 - 1)."""
        # Access the name-mangled private attribute.
        self.assertEqual(Scanner._Scanner__MAX_PORT_NR, 65535)

    def test_all_ports_range_includes_65535(self):
        """range_input=[0] must produce a range that ends at port 65535."""
        scanner = Scanner(_make_shared_info(), range_input=[0])
        r = scanner._Scanner__parse_range([0])
        self.assertEqual(r.stop, 65535 + 1)
        self.assertIn(65535, r)

    def test_all_ports_range_excludes_port_zero(self):
        """range_input=[0] is a sentinel for 'all ports'; port 0 itself must
        not be included because port 0 is not a real target port."""
        scanner = Scanner(_make_shared_info(), range_input=[0])
        r = scanner._Scanner__parse_range([0])
        self.assertNotIn(0, r)
        self.assertEqual(r.start, 1)


# ---------------------------------------------------------------------------
# Bug 2 – __parse_range off-by-one: adjacent ports rejected
# ---------------------------------------------------------------------------

class TestParseRange(unittest.TestCase):
    """Bug 2: condition was `> 1`, so [80, 81] (diff == 1) was rejected."""

    def _scanner(self):
        return Scanner(_make_shared_info(), range_input=[80, 81])

    def test_adjacent_port_range(self):
        """[80, 81] must yield range(80, 82), i.e. ports 80 and 81."""
        s = self._scanner()
        r = s._Scanner__parse_range([80, 81])
        self.assertEqual(list(r), [80, 81])

    def test_same_port_range(self):
        """[443, 443] has difference 0 — this is invalid and must raise."""
        s = Scanner(_make_shared_info(), range_input=[443])
        with self.assertRaises(ValueError):
            s._Scanner__parse_range([443, 443])

    def test_single_port_range(self):
        """[443] must yield exactly port 443."""
        s = Scanner(_make_shared_info(), range_input=[443])
        r = s._Scanner__parse_range([443])
        self.assertEqual(list(r), [443])

    def test_multi_port_range(self):
        """[8080, 8090] must yield all ten ports inclusive."""
        s = Scanner(_make_shared_info(), range_input=[8080, 8090])
        r = s._Scanner__parse_range([8080, 8090])
        self.assertEqual(list(r), list(range(8080, 8091)))

    def test_inverted_range_raises(self):
        """[90, 80] (end < start) is invalid and must raise ValueError."""
        s = Scanner(_make_shared_info(), range_input=[80])
        with self.assertRaises(ValueError):
            s._Scanner__parse_range([90, 80])

    def test_empty_list_raises(self):
        """An empty range_input list must raise an exception."""
        s = Scanner(_make_shared_info(), range_input=[80])
        with self.assertRaises((ValueError, IndexError)):
            s._Scanner__parse_range([])


# ---------------------------------------------------------------------------
# Bug 3 & 4 – Socket reuse and resource leak in __scan
# ---------------------------------------------------------------------------

class TestScanSocketLifecycle(unittest.TestCase):
    """
    Bug 3: A TCP socket was shared across all ports.  After a successful
           connect_ex() the socket is in connected state and cannot be
           reconnected to a different port without closing it first.
    Bug 4: Sockets were never closed, leaking OS file descriptors.
    """

    def test_new_socket_created_per_port(self):
        """A new socket must be created for every port in the scan range."""
        scanner = Scanner(_make_shared_info(), range_input=[80, 82],
                          connection_type="TCP")

        created_sockets = []

        original_socket = socket.socket

        def tracking_socket(family, kind):
            sock = MagicMock()
            sock.connect_ex.return_value = 111  # ECONNREFUSED
            created_sockets.append(sock)
            return sock

        with patch('networking_lib.port_scanner.socket.socket', side_effect=tracking_socket):
            scanner._Scanner__scan()

        # Ports 80, 81, 82 → 3 sockets for TCP
        self.assertEqual(len(created_sockets), 3,
                         "Expected one socket per port")

    def test_socket_closed_after_each_port(self):
        """Every socket must be closed after probing its port."""
        scanner = Scanner(_make_shared_info(), range_input=[80, 81],
                          connection_type="TCP")

        created_sockets = []

        def tracking_socket(family, kind):
            sock = MagicMock()
            sock.connect_ex.return_value = 111
            created_sockets.append(sock)
            return sock

        with patch('networking_lib.port_scanner.socket.socket', side_effect=tracking_socket):
            scanner._Scanner__scan()

        for sock in created_sockets:
            sock.close.assert_called_once()

    def test_socket_closed_even_on_connect_exception(self):
        """Socket must be closed even when connect_ex raises an exception."""
        scanner = Scanner(_make_shared_info(), range_input=[80],
                          connection_type="TCP")

        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = OSError("network error")

        with patch('networking_lib.port_scanner.socket.socket', return_value=mock_sock):
            with self.assertRaises(OSError):
                scanner._Scanner__scan()

        mock_sock.close.assert_called_once()


# ---------------------------------------------------------------------------
# Bug 5 – __PROTOCOLL_TRANSLATION keyed by raw ints instead of SocketKind
# ---------------------------------------------------------------------------

class TestProtocolTranslation(unittest.TestCase):
    """Bug 5: dict was {1: 'TCP', 2: 'UDP'}, which breaks on platforms where
    sock.type includes extra flags (e.g. SOCK_CLOEXEC).  Keys must be the
    SocketKind constants themselves."""

    def test_keys_are_socket_kind_constants(self):
        translation = Scanner._Scanner__PROTOCOLL_TRANSLATION
        self.assertIn(socket.SOCK_STREAM, translation)
        self.assertIn(socket.SOCK_DGRAM, translation)

    def test_tcp_maps_correctly(self):
        translation = Scanner._Scanner__PROTOCOLL_TRANSLATION
        self.assertEqual(translation[socket.SOCK_STREAM], "TCP")

    def test_udp_maps_correctly(self):
        translation = Scanner._Scanner__PROTOCOLL_TRANSLATION
        self.assertEqual(translation[socket.SOCK_DGRAM], "UDP")

    def test_scan_records_correct_protocol_label(self):
        """After scanning, each port's dict must contain 'TCP' and/or 'UDP' keys."""
        scanner = Scanner(_make_shared_info(), range_input=[9999],
                          connection_type="BOTH")

        def fake_socket(family, kind):
            sock = MagicMock()
            sock.connect_ex.return_value = 111
            return sock

        with patch('networking_lib.port_scanner.socket.socket', side_effect=fake_socket):
            scanner._Scanner__scan()

        ports = scanner.get_all_ports()
        self.assertIn(9999, ports)
        self.assertIn("TCP", ports[9999])
        self.assertIn("UDP", ports[9999])


# ---------------------------------------------------------------------------
# Bug 6 – File descriptor leak in __add_descriptions
# ---------------------------------------------------------------------------

class TestAddDescriptionsFileHandling(unittest.TestCase):
    """Bug 6: open() was called without a `with` statement, leaking the fd."""

    def test_file_is_closed_after_add_descriptions(self):
        """The JSON file must be closed once descriptions have been loaded."""
        scanner = Scanner(_make_shared_info(), range_input=[80],
                          connection_type="TCP")

        # Simulate a scan result so there is something to annotate.
        scanner._Scanner__scanned_ports = {80: {"TCP": 0}}

        ports_data = json.dumps({"ports": {"80": {"description": "HTTP", "status": "Official"}}})

        mock_file = mock_open(read_data=ports_data)
        with patch('builtins.open', mock_file):
            scanner._Scanner__add_descriptions('/fake/path/ports.json')

        # Verify the context manager protocol was invoked (guarantees close).
        mock_file.return_value.__enter__.assert_called_once()
        mock_file.return_value.__exit__.assert_called_once()

    def test_descriptions_are_added_correctly(self):
        """Description and status must be stored under the port's key."""
        scanner = Scanner(_make_shared_info(), range_input=[80],
                          connection_type="TCP")
        scanner._Scanner__scanned_ports = {80: {"TCP": 0}}

        ports_data = json.dumps({"ports": {"80": {"description": "HTTP", "status": "Official"}}})

        with patch('builtins.open', mock_open(read_data=ports_data)):
            scanner._Scanner__add_descriptions('/fake/path/ports.json')

        self.assertEqual(scanner.get_all_ports()[80]["Description"],
                         ["HTTP", "Official"])

    def test_list_descriptions_use_first_entry(self):
        """When a port has multiple descriptions (list), the first is used."""
        scanner = Scanner(_make_shared_info(), range_input=[10000],
                          connection_type="TCP")
        scanner._Scanner__scanned_ports = {10000: {"TCP": 0}}

        ports_data = json.dumps({"ports": {"10000": [
            {"description": "Webmin", "status": "Unofficial"},
            {"description": "BackupExec", "status": "Unofficial"},
        ]}})

        with patch('builtins.open', mock_open(read_data=ports_data)):
            scanner._Scanner__add_descriptions('/fake/path/ports.json')

        self.assertEqual(scanner.get_all_ports()[10000]["Description"][0], "Webmin")


# ---------------------------------------------------------------------------
# Bug 7 – __parse_address_type / __parse_connection_type return -1 on error
# ---------------------------------------------------------------------------

class TestParseAddressType(unittest.TestCase):
    """Bug 7a: invalid address_family silently returned -1 (now raises ValueError)."""

    def test_invalid_address_family_raises(self):
        info = _make_shared_info()
        with self.assertRaises(ValueError):
            Scanner(info, address_family="IPX")

    def test_ipv4_returns_af_inet(self):
        scanner = Scanner(_make_shared_info(), address_family="IPV4")
        self.assertEqual(scanner._Scanner__address_family, socket.AF_INET)

    def test_ipv6_returns_af_inet6(self):
        scanner = Scanner(_make_shared_info(), address_family="IPV6")
        self.assertEqual(scanner._Scanner__address_family, socket.AF_INET6)

    def test_case_insensitive(self):
        scanner = Scanner(_make_shared_info(), address_family="ipv4")
        self.assertEqual(scanner._Scanner__address_family, socket.AF_INET)


class TestParseConnectionType(unittest.TestCase):
    """Bug 7b: invalid connection_type silently returned -1 (now raises ValueError)."""

    def test_invalid_connection_type_raises(self):
        with self.assertRaises(ValueError):
            Scanner(_make_shared_info(), connection_type="ICMP")

    def test_tcp_returns_sock_stream_list(self):
        scanner = Scanner(_make_shared_info(), connection_type="TCP")
        self.assertEqual(scanner._Scanner__connection_type, [socket.SOCK_STREAM])

    def test_udp_returns_sock_dgram_list(self):
        scanner = Scanner(_make_shared_info(), connection_type="UDP")
        self.assertEqual(scanner._Scanner__connection_type, [socket.SOCK_DGRAM])

    def test_both_returns_two_items(self):
        scanner = Scanner(_make_shared_info(), connection_type="BOTH")
        self.assertIn(socket.SOCK_STREAM, scanner._Scanner__connection_type)
        self.assertIn(socket.SOCK_DGRAM, scanner._Scanner__connection_type)
        self.assertEqual(len(scanner._Scanner__connection_type), 2)

    def test_case_insensitive(self):
        scanner = Scanner(_make_shared_info(), connection_type="tcp")
        self.assertEqual(scanner._Scanner__connection_type, [socket.SOCK_STREAM])


# ---------------------------------------------------------------------------
# Bug 8 – hostname_resolver.resolve_hosts missing self
# ---------------------------------------------------------------------------

class TestResolveHosts(unittest.TestCase):
    """Bug 8: resolve_hosts called bare `resolve_host(host)` → NameError."""

    def test_resolve_hosts_does_not_raise_name_error(self):
        resolver = Resolver()
        with patch.object(resolver, 'resolve_host', return_value='93.184.216.34') as mock_rh:
            result = resolver.resolve_hosts(['example.com'])
        mock_rh.assert_called_once_with('example.com')
        self.assertEqual(result, ['93.184.216.34'])

    def test_resolve_hosts_multiple(self):
        resolver = Resolver()
        side_effects = ['1.1.1.1', '8.8.8.8']
        with patch.object(resolver, 'resolve_host', side_effect=side_effects):
            result = resolver.resolve_hosts(['cloudflare.com', 'google.com'])
        self.assertEqual(result, ['1.1.1.1', '8.8.8.8'])


# ---------------------------------------------------------------------------
# Integration-level smoke test (no real network I/O)
# ---------------------------------------------------------------------------

class TestScannerIntegration(unittest.TestCase):
    """End-to-end flow with mocked sockets and a mocked port-list file."""

    def _ports_json(self, *ports):
        data = {"ports": {str(p): {"description": f"port {p}", "status": "Official"}
                          for p in ports}}
        return json.dumps(data)

    def test_start_scan_populates_results(self):
        scanner = Scanner(_make_shared_info(), range_input=[80, 81],
                          connection_type="TCP")

        call_count = [0]
        def fake_socket(family, kind):
            s = MagicMock()
            s.connect_ex.return_value = 0 if call_count[0] == 0 else 111
            call_count[0] += 1
            return s

        with patch('networking_lib.port_scanner.socket.socket', side_effect=fake_socket):
            with patch('builtins.open', mock_open(read_data=self._ports_json(80, 81))):
                scanner.start_scan('/fake/ports.json')

        ports = scanner.get_all_ports()
        self.assertIn(80, ports)
        self.assertIn(81, ports)
        self.assertIn("TCP", ports[80])
        self.assertIn("TCP", ports[81])

    def test_get_all_ports_returns_dict(self):
        scanner = Scanner(_make_shared_info(), range_input=[443],
                          connection_type="TCP")
        self.assertIsInstance(scanner.get_all_ports(), dict)


if __name__ == '__main__':
    unittest.main()
