import unittest
import hashlib
from hash_lib.hash_core.hasher import Hasher


class TestHasher(unittest.TestCase):
    def test_sha256_basic(self):
        result = Hasher.hash("hello", "sha256")
        expected = hashlib.sha256(b"hello").hexdigest()
        self.assertEqual(result, expected)

    def test_md5_basic(self):
        result = Hasher.hash("hello", "md5")
        self.assertEqual(result, "5d41402abc4b2a76b9719d911017c592")

    def test_sha1_basic(self):
        result = Hasher.hash("hello", "sha1")
        self.assertEqual(result, "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")

    def test_case_insensitive_algorithm(self):
        lower = Hasher.hash("hello", "sha256")
        upper = Hasher.hash("hello", "SHA256")
        self.assertEqual(lower, upper)

    def test_empty_string(self):
        result = Hasher.hash("", "sha256")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)

    def test_long_string(self):
        message = "a" * 10000
        result = Hasher.hash(message, "sha256")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)

    def test_unicode_string(self):
        result = Hasher.hash("你好世界", "sha256")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)

    def test_special_characters(self):
        result = Hasher.hash("!@#$%^&*()_+-=", "sha256")
        self.assertIsNotNone(result)

    def test_invalid_algorithm(self):
        result = Hasher.hash("hello", "invalid_algo")
        self.assertIsNone(result)

    def test_empty_algorithm(self):
        result = Hasher.hash("hello", "")
        self.assertIsNone(result)

    def test_whitespace_algorithm(self):
        result = Hasher.hash("hello", "   ")
        self.assertIsNone(result)

    def test_none_message(self):
        with self.assertRaises(AttributeError):
            Hasher.hash(None, "sha256")

    def test_none_algorithm(self):
        with self.assertRaises(AttributeError):
            Hasher.hash("hello", None)

    def test_numeric_message(self):
        with self.assertRaises(AttributeError):
            Hasher.hash(123, "sha256")

    def test_numeric_algorithm(self):
        with self.assertRaises(AttributeError):
            Hasher.hash("hello", 123)

    def test_same_input_same_output(self):
        r1 = Hasher.hash("test", "sha256")
        r2 = Hasher.hash("test", "sha256")
        self.assertEqual(r1, r2)

    def test_different_inputs_different_outputs(self):
        r1 = Hasher.hash("test1", "sha256")
        r2 = Hasher.hash("test2", "sha256")
        self.assertNotEqual(r1, r2)

    def test_sha256_length(self):
        result = Hasher.hash("hello", "sha256")
        self.assertEqual(len(result), 64)

    def test_md5_length(self):
        result = Hasher.hash("hello", "md5")
        self.assertEqual(len(result), 32)

    def test_sha1_length(self):
        result = Hasher.hash("hello", "sha1")
        self.assertEqual(len(result), 40)


if __name__ == "__main__":
    unittest.main()
