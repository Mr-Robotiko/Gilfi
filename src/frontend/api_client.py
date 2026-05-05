"""
Gilfi Frontend API Client
Communicates with the dockerized backend via REST API
"""

import requests
from typing import Optional, Dict, Any, List


class GilfiAPIClient:
    """Client for communicating with Gilfi backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
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
    def scan_ports(self, target: str, scan_range: list, ip_type="IPV4", connection_type="BOTH") -> Dict[str, Any]:
        return self._request('POST', '/api/networking/port_scanner', json={
            'target': target,
            'scan_range': scan_range,
            'ip_type': ip_type,
            'connection_type': connection_type
        })
    
    def get_modules(self) -> List[str]:
        """
        Get list of available module names (convenience method for tests)
        
        Returns:
            List of module names
        """
        result = self._request('GET', '/api/modules')
        return result.get('modules', [])
    
    # Hash Module Methods
    
    def hash_generate(self, text: str, algorithm: str = 'sha256') -> str:
        """
        Generate hash from text
        
        Args:
            text: Text to hash
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Hash string
        """
        result = self._request('POST', '/api/hash/generate', json={
            'text': text,
            'algorithm': algorithm
        })
        return result.get('hash', '')
    
    def hash_identify(self, hash_value: str) -> List[str]:
        """
        Identify hash type
        
        Args:
            hash_value: Hash string to identify
            
        Returns:
            List of possible hash types
        """
        result = self._request('POST', '/api/hash/identify', json={
            'hash': hash_value
        })
        return result.get('possible_types', [])
    
    def hash_crack(self, hash_value: str, hash_type: str, wordlist: str = 'common') -> Optional[str]:
        """
        Crack hash using wordlist
        
        Args:
            hash_value: Hash to crack
            hash_type: Hash algorithm type (md5, sha256, etc.)
            wordlist: Wordlist name (default: common)
            
        Returns:
            Cracked plaintext if found, None otherwise
        """
        result = self._request('POST', '/api/hash/crack', json={
            'hash': hash_value,
            'hash_type': hash_type,
            'wordlist': wordlist
        })
        return result.get('result')
    
    # RSA Module Methods
    
    def rsa_encrypt(self, text: str, operation: str = 'encrypt') -> Dict[str, Any]:
        """
        Perform RSA encryption/decryption
        
        Args:
            text: Text to encrypt/decrypt
            operation: Operation type (encrypt/decrypt)
            
        Returns:
            Dictionary with RSA operation results
        """
        return self._request('POST', '/api/rsa/encrypt', json={
            'text': text,
            'operation': operation
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
def scan_ports(target: str, scan_range: list, ip_type="IPV4", connection_type="BOTH") -> Dict[int, Dict[str, int]]:
    result = get_client().scan_ports(target, scan_range)
    return result

def hash_generate(text: str, algorithm: str = 'sha256') -> str:
    """Generate hash (returns just the hash string)"""
    return get_client().hash_generate(text, algorithm)


def hash_identify(hash_value: str) -> List[str]:
    """Identify hash type (returns list of possible types)"""
    return get_client().hash_identify(hash_value)


def hash_crack(hash_value: str, hash_type: str, wordlist: str = 'common') -> Optional[str]:
    """Crack hash (returns plaintext if found, None otherwise)"""
    return get_client().hash_crack(hash_value, hash_type, wordlist)


def rsa_encrypt(text: str, operation: str = 'encrypt') -> Dict[str, Any]:
    """Perform RSA encryption"""
    return get_client().rsa_encrypt(text, operation)


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
        # Use modules_details for dict format, fallback to modules if it's a dict
        modules_dict = modules.get('modules_details', modules.get('modules', {}))
        if isinstance(modules_dict, dict):
            for name, info in modules_dict.items():
                print(f"   - {info['name']}: {info['status']}")
        else:
            # If modules is a list, just print the names
            for name in modules.get('modules', []):
                print(f"   - {name}")
        
        # Test hash generation
        print("\n3. Hash Generation:")
        hash_result = client.hash_generate("test", "sha256")
        print(f"   Input: test")
        print(f"   Hash: {hash_result}")
        
        print("\n✓ API client working correctly!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure the backend container is running:")
        print("  ./backend-docker.sh start")
