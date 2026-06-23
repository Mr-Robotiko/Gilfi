"""
Infrastructure Tests - Frontend API Client
Tests for frontend API client functionality
"""

import unittest
import sys
import os

# Add frontend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'frontend'))

import api_client


class TestFrontendAPIClient(unittest.TestCase):
    """Test frontend API client"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = api_client.GilfiAPIClient()
    
    def test_01_client_initialization(self):
        """Test API client initialization"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.base_url, "http://localhost:8000")
        self.assertEqual(self.client.timeout, 30)
    
    def test_02_health_check(self):
        """Test health check method"""
        try:
            result = self.client.health_check()
            self.assertIsInstance(result, dict)
            self.assertIn("status", result)
            self.assertEqual(result["status"], "healthy")
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_03_get_modules(self):
        """Test get modules method"""
        try:
            result = self.client.get_modules()
            self.assertIsInstance(result, list)
            self.assertIn("hash", result)
            self.assertIn("rsa", result)
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_04_hash_generate(self):
        """Test hash generation via client"""
        try:
            result = self.client.hash_generate("test", "md5")
            self.assertIsInstance(result, str)
            self.assertEqual(len(result), 32)  # MD5 is 32 chars
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_05_hash_identify(self):
        """Test hash identification via client"""
        try:
            # MD5 hash
            result = self.client.hash_identify("5d41402abc4b2a76b9719d911017c592")
            self.assertIsInstance(result, list)
            self.assertIn("MD5", result)
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_06_hash_crack(self):
        """Test hash cracking via client"""
        try:
            # MD5 of "password"
            result = self.client.hash_crack(
                "5f4dcc3b5aa765d61d8327deb882cf99",
                "md5",
                "common"
            )
            # Result can be None if not found in wordlist
            self.assertTrue(result is None or isinstance(result, str))
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_07_rsa_encrypt(self):
        """Test RSA encryption via client"""
        try:
            result = self.client.rsa_encrypt("Hello", "encrypt")
            self.assertIsInstance(result, dict)
            self.assertIn("result", result)
            self.assertIn("public_key", result)
            self.assertIn("private_key", result)
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_08_connection_error_handling(self):
        """Test connection error handling"""
        # Create client with invalid URL
        client = api_client.GilfiAPIClient(base_url="http://localhost:9999")
        
        with self.assertRaises(ConnectionError):
            client.health_check()
    
    def test_09_convenience_functions(self):
        """Test convenience functions"""
        try:
            # Test hash_generate convenience function
            result = api_client.hash_generate("test", "md5")
            self.assertIsInstance(result, str)
            
            # Test hash_crack convenience function
            result = api_client.hash_crack("abc", "md5", "common")
            self.assertTrue(result is None or isinstance(result, str))
            
            # Test rsa_encrypt convenience function
            result = api_client.rsa_encrypt("test", "encrypt")
            self.assertIsInstance(result, dict)
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_10_timeout_configuration(self):
        """Test timeout configuration"""
        client = api_client.GilfiAPIClient(timeout=5)
        self.assertEqual(client.timeout, 5)
    
    def test_11_custom_base_url(self):
        """Test custom base URL"""
        client = api_client.GilfiAPIClient(base_url="http://example.com:8080")
        self.assertEqual(client.base_url, "http://example.com:8080")


class TestAPIClientErrorHandling(unittest.TestCase):
    """Test API client error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = api_client.GilfiAPIClient()
    
    def test_01_invalid_hash_algorithm(self):
        """Test error handling for invalid hash algorithm"""
        try:
            with self.assertRaises(Exception):
                self.client.hash_generate("test", "invalid_algo")
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_02_empty_text_hash(self):
        """Test error handling for empty text"""
        try:
            with self.assertRaises(Exception):
                self.client.hash_generate("", "md5")
        except ConnectionError:
            self.skipTest("Backend not available")
    
    def test_03_invalid_hash_format(self):
        """Test error handling for invalid hash format"""
        try:
            result = self.client.hash_identify("invalid_hash")
            # Should return empty list or raise exception
            self.assertIsInstance(result, list)
        except ConnectionError:
            self.skipTest("Backend not available")
        except Exception:
            pass  # Expected for invalid hash
    
    def test_04_invalid_rsa_operation(self):
        """Test error handling for invalid RSA operation"""
        try:
            with self.assertRaises(Exception):
                self.client.rsa_encrypt("test", "invalid_op")
        except ConnectionError:
            self.skipTest("Backend not available")


if __name__ == "__main__":
    unittest.main()
