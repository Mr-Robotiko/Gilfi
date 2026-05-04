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

from networking_lib.shared_info import Info
from networking_lib.port_scanner import Scanner

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
info = Info()
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
    return jsonify({
        'status': 'healthy',
        'service': 'Gilfi Backend API',
        'version': '1.0.0'
    })

@app.route('/api/networking/port_scanner', methods=['post'])
def scan_ports():
    """
    Scan ports of a given IP
    POST /api/networking/port_scanner
    Body: {"target": "127.0.0.1", "scan_range": [0]}
    """
    try:
        data = request.get_json()
        target = data.get('target')
        scan_range = data.get('scan_range')

        if not target:
            return jsonify({'error': 'IP is required'}), 400
        
        if not scan_range:
            return jsonify({'error': 'Scan range is required'}), 400

        info.set_ip(target)
        scanner = Scanner(info, scan_range)
        scanner.start_scan("/app/data/ports/ports.json")
        return scanner.get_all_ports()

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

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
    Body: {"hash": "string", "wordlist": "path", "algorithm": "sha256"}
    """
    try:
        data = request.get_json()
        hash_value = data.get('hash')
        wordlist = data.get('wordlist', '/app/data/wordlist/rockyou.txt')
        algorithm = data.get('algorithm', 'sha256')
        
        if not hash_value:
            return jsonify({'error': 'Hash is required'}), 400
        
        # Check if wordlist exists
        if not os.path.exists(wordlist):
            return jsonify({'error': f'Wordlist not found: {wordlist}'}), 404
        
        result = cracker.crack(hash_value, wordlist, algorithm)
        
        if result:
            return jsonify({
                'success': True,
                'hash': hash_value,
                'algorithm': algorithm,
                'cracked': True,
                'plaintext': result
            })
        else:
            return jsonify({
                'success': True,
                'hash': hash_value,
                'algorithm': algorithm,
                'cracked': False,
                'message': 'Password not found in wordlist'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    """
    RSA encryption
    POST /api/rsa/encrypt
    Body: {"plaintext": number}
    """
    try:
        data = request.get_json()
        plaintext = data.get('plaintext')
        
        if plaintext is None:
            return jsonify({'error': 'Plaintext is required'}), 400
        
        # Run RSA module
        result = subprocess.run(
            [RSA_BINARY, str(plaintext)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return jsonify({'error': 'RSA module failed', 'details': result.stderr}), 500
        
        # Parse output
        output_lines = result.stdout.strip().split('\n')
        response = {
            'success': True,
            'plaintext': plaintext,
            'output': result.stdout
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
                    response['ciphertext'] = parts[-1].strip()
            elif 'Decrypted message' in line and '=' in line:
                parts = line.split('=')
                if len(parts) > 1:
                    response['decrypted'] = parts[-1].strip()
        
        return jsonify(response)
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'RSA operation timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    modules = {
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
    
    return jsonify({
        'success': True,
        'modules': modules
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
