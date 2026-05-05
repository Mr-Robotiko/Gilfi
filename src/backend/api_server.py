"""
Gilfi Backend REST API Server
Provides HTTP endpoints for all backend modules
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys

from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_identifier.identifier import HashIdentifier
from hash_lib.hash_cracker.cracker import Cracker

# Paths
RSA_BINARY = "/app/backend/rsa-module/rsa-module"
ASKGILFI_SCRIPT = "/app/backend/ask-gilfi-module/ask-gilfi-chat.py"

# Add hash_lib to path
sys.path.insert(0, '/app/backend/hash-module/src')
sys.path.insert(0, os.path.dirname(ASKGILFI_SCRIPT))

# Import ask-gilfi module using importlib (file has hyphens in name)
import importlib.util
spec = importlib.util.spec_from_file_location("ask_gilfi_chat", ASKGILFI_SCRIPT)
ask_gilfi_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask_gilfi_module)
start_gilfi = ask_gilfi_module.start_gilfi
ask_gilfi = ask_gilfi_module.ask_gilfi

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize modules
hasher = Hasher()
identifier = HashIdentifier()
cracker = Cracker()

# Global Ollama process for reuse
_ollama_process = None

def get_ollama_process():
    """Get or start Ollama process (singleton pattern)"""
    global _ollama_process
    
    # Check if process exists and is still running
    if _ollama_process is not None:
        try:
            # Check if process is still alive
            if _ollama_process.poll() is None:
                return _ollama_process
        except:
            pass
    
    # Start new process
    _ollama_process = start_gilfi()
    return _ollama_process


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'service': 'Gilfi Backend API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@app.route('/api/hash/generate', methods=['POST'])
def hash_generate():
    """
    Generate hash from input text
    POST /api/hash/generate
    Body: {"text": "string", "algorithm": "sha256"}
    """
    try:
        data = request.get_json()
        text = data.get('text')
        algorithm = data.get('algorithm', 'sha256')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Validate algorithm
        valid_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        if algorithm.lower() not in valid_algorithms:
            return jsonify({'error': f'Invalid algorithm. Supported: {", ".join(valid_algorithms)}'}), 400
        
        result = hasher.hash(text, algorithm)
        
        return jsonify({
            'success': True,
            'input': text,
            'algorithm': algorithm,
            'hash': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hash/identify', methods=['POST'])
def hash_identify():
    """
    Identify hash type
    POST /api/hash/identify
    Body: {"hash": "string"}
    """
    try:
        data = request.get_json()
        hash_value = data.get('hash')
        
        if not hash_value:
            return jsonify({'error': 'Hash is required'}), 400
        
        result = identifier.identify(hash_value)
        
        return jsonify({
            'success': True,
            'hash': hash_value,
            'possible_types': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hash/crack', methods=['POST'])
def hash_crack():
    """
    Crack hash using wordlist
    POST /api/hash/crack
    Body: {"hash": "string", "wordlist": "path/name", "algorithm": "sha256"} or
          {"hash": "string", "wordlist": "name", "hash_type": "md5"}
    """
    try:
        data = request.get_json()
        hash_value = data.get('hash')
        wordlist = data.get('wordlist', '/app/data/wordlist/rockyou.txt')
        # Support both 'algorithm' and 'hash_type' for compatibility
        algorithm = data.get('algorithm') or data.get('hash_type', 'sha256')
        
        if not hash_value:
            return jsonify({'error': 'Hash is required'}), 400
        
        # Normalize algorithm to lowercase
        algorithm = algorithm.lower()
        
        # If wordlist is just a name (not a path), use common wordlist
        if wordlist == 'common' or not wordlist.startswith('/'):
            # For now, use rockyou as the common wordlist
            wordlist = '/app/data/wordlist/rockyou.txt'
        
        # Check if wordlist exists
        if not os.path.exists(wordlist):
            return jsonify({'error': f'Wordlist not found: {wordlist}'}), 404
        
        cracked_result = cracker.crack(hash_value, wordlist, algorithm)
        
        if cracked_result:
            return jsonify({
                'success': True,
                'hash': hash_value,
                'algorithm': algorithm,
                'cracked': True,
                'plaintext': cracked_result,
                'result': cracked_result  # Add result field for test compatibility
            })
        else:
            return jsonify({
                'success': True,
                'hash': hash_value,
                'algorithm': algorithm,
                'cracked': False,
                'result': None,  # Add result field for test compatibility
                'message': 'Password not found in wordlist'
            })
    
    except ValueError as e:
        return jsonify({'error': f'Unsupported hash algorithm: {algorithm}'}), 400
    except FileNotFoundError as e:
        return jsonify({'error': f'Wordlist not found: {wordlist}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    """
    RSA encryption
    POST /api/rsa/encrypt
    Body: {"plaintext": number} or {"text": "string", "operation": "encrypt"}
    """
    try:
        data = request.get_json()
        
        # Support both formats
        plaintext = data.get('plaintext')
        text = data.get('text')
        operation = data.get('operation', 'encrypt')
        
        # Validate operation
        valid_operations = ['encrypt', 'decrypt']
        if operation not in valid_operations:
            return jsonify({'error': f'Invalid operation. Supported: {", ".join(valid_operations)}'}), 400
        
        # Convert text to number if provided
        if text is not None and plaintext is None:
            # Convert text to a smaller number using hash
            # Use sum of ASCII values to keep number small
            plaintext = sum(ord(c) for c in text) % 1000000  # Keep it under 1 million
        
        if plaintext is None:
            return jsonify({'error': 'Plaintext or text is required'}), 400
        
        # Check if RSA binary exists
        if not os.path.exists(RSA_BINARY):
            return jsonify({'error': 'RSA module not found', 'details': f'Binary not found at {RSA_BINARY}'}), 500
        
        # Check if RSA binary is executable
        if not os.access(RSA_BINARY, os.X_OK):
            return jsonify({'error': 'RSA module not executable', 'details': 'Binary exists but is not executable'}), 500
        
        # Run RSA module
        result = subprocess.run(
            [RSA_BINARY, str(plaintext)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return jsonify({'error': 'RSA module failed', 'details': result.stderr, 'stdout': result.stdout}), 500
        
        # Parse output
        output_lines = result.stdout.strip().split('\n')
        response = {
            'success': True,
            'plaintext': plaintext,
            'output': result.stdout,
            'result': None  # Will be set below
        }
        
        # Extract key information from output
        for line in output_lines:
            if 'Public Key' in line:
                response['public_key'] = line.split('=')[1].strip()
            elif 'Private Key' in line:
                response['private_key'] = line.split('=')[1].strip()
            elif 'Ciphertext (C)' in line and '=' in line:
                parts = line.split('=')
                if len(parts) > 1:
                    ciphertext = parts[-1].strip()
                    response['ciphertext'] = ciphertext
                    response['result'] = ciphertext  # Set result for test compatibility
            elif 'Decrypted message' in line and '=' in line:
                parts = line.split('=')
                if len(parts) > 1:
                    response['decrypted'] = parts[-1].strip()
        
        return jsonify(response)
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'RSA operation timed out'}), 500
    except FileNotFoundError:
        return jsonify({'error': 'RSA binary not found', 'details': f'Could not execute {RSA_BINARY}'}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/api/askgilfi/query', methods=['POST'])
def askgilfi_query():
    """
    Query Ask-Gilfi chatbot
    POST /api/askgilfi/query
    Body: {"prompt": "string"}
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Get or start Ollama server (reuses existing process)
        ollama_process = get_ollama_process()
        
        # Query the model (don't terminate process - keep it running)
        response = ask_gilfi(prompt)
        
        if response is None:
            return jsonify({
                'success': False,
                'error': 'Ollama server not responding'
            }), 500
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/modules', methods=['GET'])
def list_modules():
    """List available backend modules"""
    modules_dict = {
        'hash': {
            'name': 'Hash Module',
            'endpoints': [
                '/api/hash/generate',
                '/api/hash/identify',
                '/api/hash/crack'
            ],
            'status': 'available'
        },
        'rsa': {
            'name': 'RSA Module',
            'endpoints': ['/api/rsa/encrypt'],
            'status': 'available' if os.path.exists(RSA_BINARY) else 'unavailable'
        },
        'askgilfi': {
            'name': 'Ask-Gilfi Chatbot',
            'endpoints': ['/api/askgilfi/query'],
            'status': 'available' if os.path.exists(ASKGILFI_SCRIPT) else 'unavailable'
        }
    }
    
    # Return both formats for backward compatibility
    # New format: list of module names (for tests)
    # Old format: dict with details (for frontend)
    return jsonify({
        'success': True,
        'modules': list(modules_dict.keys()),  # List format for tests
        'modules_details': modules_dict  # Dict format for frontend
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("  Gilfi Backend API Server")
    print("=" * 50)
    print("Starting server on http://0.0.0.0:8000")
    print("\nAvailable endpoints:")
    print("  GET  /health")
    print("  GET  /api/modules")
    print("  POST /api/hash/generate")
    print("  POST /api/hash/identify")
    print("  POST /api/hash/crack")
    print("  POST /api/rsa/encrypt")
    print("  POST /api/askgilfi/query")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=False)
