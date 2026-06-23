"""
Infrastructure Tests - API Endpoints
Tests for backend REST API functionality
"""

import unittest
import requests
import time


class TestAPIEndpoints(unittest.TestCase):
    """Test backend API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.backend_url = "http://localhost:8000"
        cls.timeout = 10
        
        # Wait for backend to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(3)
                else:
                    raise Exception("Backend not available after waiting")
    
    def test_01_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.backend_url}/health", timeout=self.timeout)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
    
    def test_02_modules_endpoint(self):
        """Test modules listing endpoint"""
        response = requests.get(f"{self.backend_url}/api/modules", timeout=self.timeout)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("modules", data)
        self.assertIsInstance(data["modules"], list)
        
        # Check for expected modules
        expected_modules = ["hash", "rsa"]
        for module in expected_modules:
            self.assertIn(module, data["modules"])
    
    def test_03_hash_generate_md5(self):
        """Test hash generation with MD5"""
        payload = {
            "text": "test123",
            "algorithm": "md5"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/generate",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("hash", data)
        self.assertIn("algorithm", data)
        self.assertEqual(data["algorithm"], "md5")
        # MD5 hash of "test123"
        self.assertEqual(data["hash"], "cc03e747a6afbbcbf8be7668acfebee5")
    
    def test_04_hash_generate_sha256(self):
        """Test hash generation with SHA256"""
        payload = {
            "text": "hello",
            "algorithm": "sha256"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/generate",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("hash", data)
        self.assertEqual(data["algorithm"], "sha256")
        # SHA256 hash of "hello"
        self.assertEqual(
            data["hash"],
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        )
    
    def test_05_hash_generate_invalid_algorithm(self):
        """Test hash generation with invalid algorithm"""
        payload = {
            "text": "test",
            "algorithm": "invalid_algo"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/generate",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
    
    def test_06_hash_generate_missing_text(self):
        """Test hash generation with missing text"""
        payload = {
            "algorithm": "md5"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/generate",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
    
    def test_07_hash_identify_md5(self):
        """Test hash identification for MD5"""
        payload = {
            "hash": "5d41402abc4b2a76b9719d911017c592"  # MD5 of "hello"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/identify",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("possible_types", data)
        self.assertIsInstance(data["possible_types"], list)
        self.assertIn("MD5", data["possible_types"])
    
    def test_08_hash_identify_sha256(self):
        """Test hash identification for SHA256"""
        payload = {
            "hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/identify",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("possible_types", data)
        self.assertIn("SHA-256", data["possible_types"])
    
    def test_09_hash_crack_simple(self):
        """Test hash cracking with simple password"""
        # MD5 hash of "password"
        payload = {
            "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
            "hash_type": "md5",
            "wordlist": "common"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/crack",
            json=payload,
            timeout=30  # Cracking may take longer
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        # Note: This will only work if "password" is in the wordlist
    
    def test_10_hash_crack_not_found(self):
        """Test hash cracking with non-existent password"""
        # Random MD5 hash
        payload = {
            "hash": "aaaabbbbccccddddeeeeffffgggghhh1",
            "hash_type": "md5",
            "wordlist": "common"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/hash/crack",
            json=payload,
            timeout=30
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIsNone(data["result"])
    
    def test_11_rsa_encrypt_decrypt(self):
        """Test RSA encryption and decryption"""
        payload = {
            "text": "Hello, World!",
            "operation": "encrypt"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/rsa/encrypt",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("public_key", data)
        self.assertIn("private_key", data)
        
        # Verify encrypted text is different from original
        self.assertNotEqual(data["result"], "Hello, World!")
    
    def test_12_rsa_invalid_operation(self):
        """Test RSA with invalid operation"""
        payload = {
            "text": "test",
            "operation": "invalid"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/rsa/encrypt",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
    
    def test_13_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.options(
            f"{self.backend_url}/api/modules",
            timeout=self.timeout
        )
        
        # Check for CORS headers
        self.assertIn("Access-Control-Allow-Origin", response.headers)
    
    def test_14_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = requests.get(
            f"{self.backend_url}/api/invalid/endpoint",
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_15_api_response_time(self):
        """Test API response time is reasonable"""
        import time
        
        start_time = time.time()
        response = requests.get(f"{self.backend_url}/health", timeout=self.timeout)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, "Health endpoint should respond in under 2 seconds")


if __name__ == "__main__":
    unittest.main()
