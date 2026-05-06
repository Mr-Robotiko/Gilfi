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
        result = self.cracker.crack(self.sample_hash, "<your path>", "MD5")

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


    # --- Wordlist Shuffler Tests ---

    def test_wordlist_shuffler_basic(self):
        """Test that wordlist shuffler generates multiple variations of a word."""
        # Create a temporary wordlist file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("password\n")
            temp_wordlist = f.name
        
        try:
            variations = list(self.cracker._wordlist_shuffler(temp_wordlist))
            
            # Should generate multiple variations
            self.assertGreater(len(variations), 1)
            
            # Check for expected transformations
            self.assertIn("password", variations)  # Original
            self.assertIn("Password", variations)  # Capitalized
            self.assertIn("PASSWORD", variations)  # Uppercase
            self.assertIn("password123", variations)  # With numbers
            self.assertIn("password1", variations)  # With single digit
            self.assertIn("password!", variations)  # With special char
            
        finally:
            os.remove(temp_wordlist)

    def test_wordlist_shuffler_leet_speak(self):
        """Test that wordlist shuffler applies leet speak transformations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("password\n")
            temp_wordlist = f.name
        
        try:
            variations = list(self.cracker._wordlist_shuffler(temp_wordlist))
            
            # Check for leet speak variations
            leet_variations = [v for v in variations if '@' in v or '3' in v or '0' in v or '$' in v]
            self.assertGreater(len(leet_variations), 0)
            
        finally:
            os.remove(temp_wordlist)

    @patch("builtins.open", new_callable=mock_open, read_data="pass")
    def test_crack_with_shuffler_capitalized(self, mock_file):
        """Test cracking with shuffler finds capitalized password."""
        # MD5 hash of "Pass" (capitalized)
        capitalized_hash = "4e88c1d3b4c87c8b0e8c5e5e5e5e5e5e"  # This is a placeholder
        # Let's use a real hash: MD5 of "Pass"
        from hash_lib.hash_core.hasher import Hasher
        hasher = Hasher()
        capitalized_hash = hasher.hash("Pass", "MD5")
        
        result = self.cracker.crack(capitalized_hash, "mock_path.txt", "MD5", use_shuffler=True)
        self.assertEqual(result, "Pass")

    @patch("builtins.open", new_callable=mock_open, read_data="test")
    def test_crack_with_shuffler_with_numbers(self, mock_file):
        """Test cracking with shuffler finds password with appended numbers."""
        from hash_lib.hash_core.hasher import Hasher
        hasher = Hasher()
        # MD5 hash of "test123"
        hash_with_numbers = hasher.hash("test123", "MD5")
        
        result = self.cracker.crack(hash_with_numbers, "mock_path.txt", "MD5", use_shuffler=True)
        self.assertEqual(result, "test123")

    @patch("builtins.open", new_callable=mock_open, read_data="admin")
    def test_crack_without_shuffler(self, mock_file):
        """Test that cracking without shuffler only tries exact matches."""
        from hash_lib.hash_core.hasher import Hasher
        hasher = Hasher()
        # MD5 hash of "Admin" (capitalized) - should NOT be found without shuffler
        capitalized_hash = hasher.hash("Admin", "MD5")
        
        result = self.cracker.crack(capitalized_hash, "mock_path.txt", "MD5", use_shuffler=False)
        self.assertIsNone(result)  # Should not find it without shuffler

    def test_wordlist_shuffler_empty_lines(self):
        """Test that wordlist shuffler handles empty lines gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("word1\n\n\nword2\n")
            temp_wordlist = f.name
        
        try:
            variations = list(self.cracker._wordlist_shuffler(temp_wordlist))
            
            # Should generate variations for both words, skipping empty lines
            self.assertGreater(len(variations), 2)
            
            # Check that both words have variations
            word1_variations = [v for v in variations if 'word1' in v.lower()]
            word2_variations = [v for v in variations if 'word2' in v.lower()]
            
            self.assertGreater(len(word1_variations), 0)
            self.assertGreater(len(word2_variations), 0)
            
        finally:
            os.remove(temp_wordlist)

    def test_wordlist_shuffler_file_not_found(self):
        """Test that wordlist shuffler raises FileNotFoundError for missing file."""
        with self.assertRaises(FileNotFoundError):
            list(self.cracker._wordlist_shuffler("non_existent_file.txt"))


if __name__ == "__main__":
    unittest.main()
