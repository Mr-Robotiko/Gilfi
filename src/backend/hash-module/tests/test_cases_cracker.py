import unittest
from unittest.mock import patch, mock_open
import sqlite3
import os
import tempfile
from hash_lib.hash_cracker.cracker import Cracker


class TestCracker(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database path for each test."""
        self.test_db = tempfile.NamedTemporaryFile(suffix = ".db", delete = False)
        self.test_db.close()  # Close so Cracker can open it
        self.cracker = Cracker(db_path = self.test_db.name)
        self.sample_hash = "5ebe2294ecd0e0f08eab7690d2a6ee69"  # MD5 for 'secret'

    def tearDown(self):
        """Clean up the temporary database file."""
        if os.path.exists(self.test_db.name):
            os.remove(self.test_db.name)

    # --- Cache Tests ---

    def test_database_initialization(self):
        """Verify the 'hashes' table is created automatically."""
        with sqlite3.connect(self.test_db.name) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hashes'")
            self.assertIsNotNone(cursor.fetchone())

    def test_cache_logic(self):
        """Ensure a hash is retrieved from the DB if it was previously saved."""
        self.cracker._save_to_cache(self.sample_hash, "secret")
        # We pass a non-existent path; if it returns 'secret', it definitely hit the cache
        result = self.cracker.crack(self.sample_hash, "non_existent.txt", "MD5")
        self.assertEqual(result, "secret")

    # --- Cracking Logic Tests ---

    @patch("builtins.open", new_callable = mock_open, read_data = "password\nadmin\nsecret\n12345")
    def test_successful_crack(self, mock_file):
        """Verify the cracker finds the word in the list and saves it to cache."""
        result = self.cracker.crack(self.sample_hash, "/Users/raphaeltack/Gilfi/data/wordlist/rockyou.txt", "MD5")

        self.assertEqual(result, "secret")
        # Verify it was cached
        self.assertEqual(self.cracker._check_cache(self.sample_hash), "secret")

    @patch("builtins.open", new_callable = mock_open, read_data = "wrong_pass\nno_match")
    def test_failed_crack(self, mock_file):
        """Verify it returns None when the wordlist is exhausted."""
        result = self.cracker.crack(self.sample_hash, "mock_path.txt", "MD5")
        self.assertIsNone(result)

    def test_file_not_found(self):
        """Ensure FileNotFoundError is propagated correctly."""
        with self.assertRaises(FileNotFoundError):
            self.cracker.crack(self.sample_hash, "invalid_path_to_file.txt", "MD5")

    # --- Identification Integration ---

    @patch("builtins.open", new_callable = mock_open, read_data = "secret")
    @patch("hash_lib.hash_identifier.identifier.HashIdentifier.identify")
    def test_automatic_algorithm_detection(self, mock_identify, mock_file):
        """Test that Cracker calls HashIdentifier if algorithm is None."""
        mock_identify.return_value = ["MD5"]

        # We don't provide an algorithm here
        result = self.cracker.crack(self.sample_hash, "mock_path.txt", None)

        mock_identify.assert_called_once_with(self.sample_hash)
        self.assertEqual(result, "secret")


if __name__ == "__main__":
    unittest.main()
