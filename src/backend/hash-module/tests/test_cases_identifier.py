import unittest
import hashlib
from hash_lib.hash_identifier.identifier import HashIdentifier


class TestHashIdentifier(unittest.TestCase):
    def setUp(self):
        self.hi = HashIdentifier()
        self.test_data = b"hello world"

    def test_md5(self):
        h = hashlib.md5(self.test_data).hexdigest()
        self.assertEqual(self.hi.identify(h), ["MD5"])

    def test_sha1(self):
        h = hashlib.sha1(self.test_data).hexdigest()
        self.assertEqual(self.hi.identify(h), ["SHA-1"])

    def test_sha256(self):
        h = hashlib.sha256(self.test_data).hexdigest()
        result = self.hi.identify(h)
        self.assertIn("SHA-256", result)
        self.assertIn("SHA3-256", result)

    def test_bcrypt_format(self):
        # BCrypt isn't in hashlib standard; using a dummy valid-length/format string
        bcrypt_dummy = "$" + "a" * 59
        self.assertEqual(self.hi.identify(bcrypt_dummy), ["BCrypt"])

    def test_invalid_hex(self):
        # Contains 'g', which is not hex
        self.assertEqual(self.hi.identify("g" * 32), ["Invalid (Not Hexadecimal)"])

    def test_strip_whitespace(self):
        h = hashlib.md5(self.test_data).hexdigest()
        self.assertEqual(self.hi.identify(f"  {h}  "), ["MD5"])

    def test_unknown_length(self):
        # 10 characters is not in our hex_map
        self.assertEqual(self.hi.identify("abcde12345"), ["Unknown Algorithm"])


if __name__ == "__main__":
    unittest.main()
