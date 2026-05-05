"""
Infrastructure Tests - Docker Backend
Tests for backend Docker container functionality
"""

import unittest
import subprocess
import time
import requests
import os


class TestDockerBackend(unittest.TestCase):
    """Test Docker backend container setup and functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.backend_url = "http://localhost:8000"
        cls.container_name = "gilfi_backend"
        cls.compose_file = "docker-compose.backend.yaml"
        
    def test_01_docker_available(self):
        """Test if Docker or Podman is available"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(result.returncode, 0, "Docker should be available")
            self.assertIn("Docker", result.stdout, "Docker version should be displayed")
        except FileNotFoundError:
            # Try Podman
            try:
                result = subprocess.run(
                    ["podman", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self.assertEqual(result.returncode, 0, "Podman should be available")
                self.assertIn("podman", result.stdout.lower(), "Podman version should be displayed")
            except FileNotFoundError:
                self.fail("Neither Docker nor Podman is available")
    
    def test_02_compose_file_exists(self):
        """Test if docker-compose configuration exists"""
        self.assertTrue(
            os.path.exists(self.compose_file),
            f"{self.compose_file} should exist"
        )
    
    def test_03_dockerfile_exists(self):
        """Test if backend Dockerfile exists"""
        dockerfile_path = "src/backend/Dockerfile"
        self.assertTrue(
            os.path.exists(dockerfile_path),
            f"{dockerfile_path} should exist"
        )
    
    def test_04_entrypoint_exists(self):
        """Test if entrypoint script exists"""
        entrypoint_path = "src/backend/entrypoint.sh"
        self.assertTrue(
            os.path.exists(entrypoint_path),
            f"{entrypoint_path} should exist"
        )
    
    def test_05_backend_requirements_exists(self):
        """Test if backend requirements.txt exists"""
        requirements_path = "src/backend/requirements.txt"
        self.assertTrue(
            os.path.exists(requirements_path),
            f"{requirements_path} should exist"
        )
    
    def test_06_api_server_exists(self):
        """Test if API server file exists"""
        api_server_path = "src/backend/api_server.py"
        self.assertTrue(
            os.path.exists(api_server_path),
            f"{api_server_path} should exist"
        )
    
    def test_07_ollama_binaries_exist(self):
        """Test if Ollama binaries exist for all platforms"""
        binaries = {
            "linux": "src/backend/ask-gilfi-module/bin/linux/ollama",
            "mac": "src/backend/ask-gilfi-module/bin/mac/ollama",
            "windows": "src/backend/ask-gilfi-module/bin/windows/ollama.exe"
        }
        
        for platform, path in binaries.items():
            with self.subTest(platform=platform):
                self.assertTrue(
                    os.path.exists(path),
                    f"Ollama binary for {platform} should exist at {path}"
                )
    
    def test_08_container_can_start(self):
        """Test if backend container can start"""
        # Check if container is already running
        check_result = subprocess.run(
            ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        container_already_running = self.container_name in check_result.stdout
        
        if not container_already_running:
            # Stop any existing container
            subprocess.run(
                ["docker", "compose", "-f", self.compose_file, "down"],
                capture_output=True,
                timeout=30
            )
            
            # Start container
            result = subprocess.run(
                ["docker", "compose", "-f", self.compose_file, "up", "-d"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.assertEqual(result.returncode, 0, "Container should start successfully")
        else:
            # Container is already running, which is fine - just verify it's healthy
            self.assertTrue(True, "Container is already running")
        
        # Wait for container to be ready
        time.sleep(10)
        
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertIn("Up", result.stdout, "Container should be running")
    
    def test_09_backend_health_endpoint(self):
        """Test if backend health endpoint responds"""
        max_retries = 5
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(5)
                else:
                    raise
        
        self.assertEqual(response.status_code, 200, "Health endpoint should return 200")
        data = response.json()
        self.assertEqual(data["status"], "healthy", "Backend should be healthy")
    
    def test_10_backend_modules_endpoint(self):
        """Test if backend modules endpoint responds"""
        response = requests.get(f"{self.backend_url}/api/modules", timeout=5)
        self.assertEqual(response.status_code, 200, "Modules endpoint should return 200")
        
        data = response.json()
        self.assertIn("modules", data, "Response should contain modules list")
        self.assertIsInstance(data["modules"], list, "Modules should be a list")
    
    def test_11_rsa_module_compiled(self):
        """Test if RSA module is compiled in container"""
        result = subprocess.run(
            ["docker", "exec", self.container_name, "test", "-f", "/app/backend/rsa-module/rsa-module"],
            capture_output=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0, "RSA module should be compiled")
    
    def test_12_ollama_binary_executable(self):
        """Test if Ollama binary is executable in container"""
        result = subprocess.run(
            ["docker", "exec", self.container_name, "test", "-x", "/app/backend/ask-gilfi-module/bin/linux/ollama"],
            capture_output=True,
            timeout=5
        )
        
        self.assertEqual(result.returncode, 0, "Ollama binary should be executable")
    
    def test_13_environment_variables_set(self):
        """Test if required environment variables are set in container"""
        result = subprocess.run(
            ["docker", "exec", self.container_name, "env"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        self.assertIn("OLLAMA_MODELS", result.stdout, "OLLAMA_MODELS should be set")
        self.assertIn("FLASK_APP", result.stdout, "FLASK_APP should be set")
    
    def test_14_container_logs_no_errors(self):
        """Test if container logs don't contain critical errors"""
        result = subprocess.run(
            ["docker", "logs", self.container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check for common error patterns
        error_patterns = ["CRITICAL", "FATAL", "Traceback (most recent call last)"]
        for pattern in error_patterns:
            self.assertNotIn(
                pattern,
                result.stderr,
                f"Container logs should not contain '{pattern}'"
            )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        # Stop container
        subprocess.run(
            ["docker", "compose", "-f", cls.compose_file, "down"],
            capture_output=True,
            timeout=30
        )


if __name__ == "__main__":
    unittest.main()
