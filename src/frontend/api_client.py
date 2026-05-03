"""
Gilfi Frontend API Client
Communicates with the dockerized backend via REST API
"""

import requests
from typing import Optional, Dict, Any, List


class GilfiAPIClient:
    """Client for communicating with Gilfi backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30  # seconds
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to backend API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to backend at {self.base_url}. "
                "Make sure the backend container is running."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if backend is healthy
        
        Returns:
            Health status information
        """
        return self._request('GET', '/health')
    
    def list_modules(self) -> Dict[str, Any]:
        """
        List available backend modules
        
        Returns:
            Dictionary of available modules and their endpoints
        """
        return self._request('GET', '/api/modules')

    # Networking Methods
    def scan_ports(self, target: str, scan_range: list) -> dict(int, dict(str, int | list(str, str))):
        print("Sending req")
        return self._request('POST', 'api/networking/port_scanner', json={
            'target': target,
            'scan_range': scan_range
        })
    
    # Hash Module Methods
    
    def hash_generate(self, text: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Generate hash from text
        
        Args:
            text: Text to hash
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Dictionary with hash result
        """
        return self._request('POST', '/api/hash/generate', json={
            'text': text,
            'algorithm': algorithm
        })
    
    def hash_identify(self, hash_value: str) -> Dict[str, Any]:
        """
        Identify hash type
        
        Args:
            hash_value: Hash string to identify
            
        Returns:
            Dictionary with possible hash types
        """
        return self._request('POST', '/api/hash/identify', json={
            'hash': hash_value
        })
    
    def hash_crack(self, hash_value: str, wordlist: str = '/app/data/wordlist/rockyou.txt', 
                   algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Crack hash using wordlist
        
        Args:
            hash_value: Hash to crack
            wordlist: Path to wordlist file (default: rockyou.txt)
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Dictionary with cracking result
        """
        return self._request('POST', '/api/hash/crack', json={
            'hash': hash_value,
            'wordlist': wordlist,
            'algorithm': algorithm
        })
    
    # RSA Module Methods
    
    def rsa_encrypt(self, plaintext: int) -> Dict[str, Any]:
        """
        Perform RSA encryption
        
        Args:
            plaintext: Number to encrypt
            
        Returns:
            Dictionary with RSA encryption results
        """
        return self._request('POST', '/api/rsa/encrypt', json={
            'plaintext': plaintext
        })
    
    # Ask-Gilfi Methods
    
    def askgilfi_query(self, prompt: str) -> Dict[str, Any]:
        """
        Query Ask-Gilfi chatbot
        
        Args:
            prompt: Question or prompt for the chatbot
            
        Returns:
            Dictionary with chatbot response
        """
        return self._request('POST', '/api/askgilfi/query', json={
            'prompt': prompt
        })


# Singleton instance for easy access
_client_instance: Optional[GilfiAPIClient] = None


def get_client(base_url: str = "http://localhost:8000") -> GilfiAPIClient:
    """
    Get or create API client singleton
    
    Args:
        base_url: Base URL of the backend API
        
    Returns:
        GilfiAPIClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = GilfiAPIClient(base_url)
    return _client_instance


# Convenience functions for direct use

def hash_generate(text: str, algorithm: str = 'sha256') -> str:
    """Generate hash (returns just the hash string)"""
    result = get_client().hash_generate(text, algorithm)
    return result.get('hash', '')


def hash_identify(hash_value: str) -> List[str]:
    """Identify hash type (returns list of possible types)"""
    result = get_client().hash_identify(hash_value)
    return result.get('possible_types', [])


def hash_crack(hash_value: str, wordlist: str = '/app/data/wordlist/rockyou.txt', 
               algorithm: str = 'sha256') -> Optional[str]:
    """Crack hash (returns plaintext if found, None otherwise)"""
    result = get_client().hash_crack(hash_value, wordlist, algorithm)
    if result.get('cracked'):
        return result.get('plaintext')
    return None


def rsa_encrypt(plaintext: int) -> Dict[str, Any]:
    """Perform RSA encryption"""
    return get_client().rsa_encrypt(plaintext)


def askgilfi_query(prompt: str) -> str:
    """Query Ask-Gilfi (returns response text)"""
    result = get_client().askgilfi_query(prompt)
    return result.get('response', '')


if __name__ == '__main__':
    # Test the API client
    print("Testing Gilfi API Client...")
    
    try:
        client = get_client()
        
        # Health check
        print("\n1. Health Check:")
        health = client.health_check()
        print(f"   Status: {health.get('status')}")
        print(f"   Service: {health.get('service')}")
        
        # List modules
        print("\n2. Available Modules:")
        modules = client.list_modules()
        for name, info in modules.get('modules', {}).items():
            print(f"   - {info['name']}: {info['status']}")
        
        # Test hash generation
        print("\n3. Hash Generation:")
        result = client.hash_generate("test", "sha256")
        print(f"   Input: {result.get('input')}")
        print(f"   Hash: {result.get('hash')}")
        
        print("\n✓ API client working correctly!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure the backend container is running:")
        print("  ./backend-docker.sh start")
