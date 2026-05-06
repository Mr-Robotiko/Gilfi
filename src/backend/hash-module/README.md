# Hash Module - Comprehensive Documentation

## Overview

The Hash Module is a Python package that provides comprehensive cryptographic hash operations including generation, identification, and cracking capabilities. It is designed for educational purposes and security analysis.

## Table of Contents

1. [Installation](#installation)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Testing](#testing)

---

## Installation

### Development Installation

```bash
cd src/backend/hash-module
pip install -e .
```

### Production Installation

```bash
pip install hash-lib
```

### Dependencies

- Python 3.8+
- hashlib (built-in)
- No external dependencies required

---

## Architecture

```
hash-module/
├── src/
│   └── hash_lib/
│       ├── __init__.py
│       ├── hash_core/
│       │   ├── __init__.py
│       │   └── hasher.py          # Hash generation
│       ├── hash_identifier/
│       │   ├── __init__.py
│       │   └── identifier.py      # Hash type identification
│       └── hash_cracker/
│           ├── __init__.py
│           └── cracker.py         # Hash cracking
├── tests/
│   ├── test_cases_hasher.py
│   ├── test_cases_identifier.py
│   └── test_cases_cracker.py
└── pyproject.toml
```

---

## Components

### 1. Hasher (hash_core.hasher)

**Purpose**: Generate cryptographic hashes from text input.

**Supported Algorithms**:
- MD5
- SHA-1
- SHA-224
- SHA-256 (default)
- SHA-384
- SHA-512

**Features**:
- Fast hash generation (< 1ms for most inputs)
- Support for all major hash algorithms
- Input validation
- Hexadecimal output format

### 2. HashIdentifier (hash_identifier.identifier)

**Purpose**: Identify hash types based on format and length.

**Detection Methods**:
- Length-based identification
- Character set validation
- Pattern matching
- Confidence scoring

**Supported Hash Types**:
- MD5 (32 characters)
- SHA-1 (40 characters)
- SHA-224 (56 characters)
- SHA-256 (64 characters)
- SHA-384 (96 characters)
- SHA-512 (128 characters)

### 3. Cracker (hash_cracker.cracker)

**Purpose**: Crack password hashes using wordlist attacks with optimized Hashcat/John the Ripper-inspired rules.

**Features**:
- Dictionary-based attacks with optimized rule engine
- Multi-algorithm support
- **25+ High-Impact Transformation Rules** (ENABLED BY DEFAULT)
- Tiered rule system prioritizing most effective patterns
- Automatic password variations (capitalization, numbers, special chars)
- Selective leet speak transformations
- High performance - optimized for large wordlists
- Large wordlist support (100M+ entries like rockyou.txt)
- SQLite caching for cracked hashes
- Smart batching to prevent timeouts

**Optimized Rule-Based Attack** (Inspired by Hashcat/John the Ripper):
- **Tier 1 Rules**: Most common patterns (original, capitalize, append 123/1)
- **Tier 2 Rules**: Common variations (uppercase, lowercase, special chars)
- **Tier 3 Rules**: Years (2023-2025) - very common in real passwords
- **Tier 4 Rules**: Selective leet speak (highest impact substitutions)
- **Tier 5 Rules**: Additional patterns (prepend, combined rules)
- **25+ optimized rules applied to EVERY word in rockyou.txt**

---

## Usage Examples

### Basic Hash Generation

```python
from hash_lib.hash_core.hasher import Hasher

hasher = Hasher()

# Generate SHA-256 hash (default)
hash_value = hasher.hash("password")
print(hash_value)
# Output: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

# Generate MD5 hash
md5_hash = hasher.hash("password", "md5")
print(md5_hash)
# Output: 5f4dcc3b5aa765d61d8327deb882cf99

# Generate SHA-512 hash
sha512_hash = hasher.hash("password", "sha512")
print(sha512_hash)
```

### Hash Type Identification

```python
from hash_lib.hash_identifier.identifier import HashIdentifier

identifier = HashIdentifier()

# Identify MD5 hash
hash_value = "5f4dcc3b5aa765d61d8327deb882cf99"
possible_types = identifier.identify(hash_value)
print(possible_types)
# Output: ['MD5', 'MD4', 'MD2']

# Identify SHA-256 hash
sha256_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
types = identifier.identify(sha256_hash)
print(types)
# Output: ['SHA-256']
```

### Hash Cracking

```python
from hash_lib.hash_cracker.cracker import Cracker

cracker = Cracker()

# Crack MD5 hash with wordlist shuffler (default)
hash_to_crack = "5f4dcc3b5aa765d61d8327deb882cf99"
wordlist_path = "/path/to/wordlist.txt"
algorithm = "md5"

result = cracker.crack(hash_to_crack, wordlist_path, algorithm)

if result:
    print(f"Password found: {result}")
else:
    print("Password not found in wordlist")

# Crack without shuffler (exact matches only)
result = cracker.crack(hash_to_crack, wordlist_path, algorithm, use_shuffler=False)
```

### Wordlist Shuffler with Hashcat/John the Ripper Rules

The wordlist shuffler uses **70+ rule-based transformations** inspired by Hashcat and John the Ripper, automatically applied to each word in the wordlist. This dramatically increases cracking success rates against real-world passwords.

```python
from hash_lib.hash_cracker.cracker import Cracker

cracker = Cracker()

# Example: If wordlist contains "password", the rule engine will try:
#
# BASIC RULES (Hashcat notation):
# - password           (:  - nothing)
# - PASSWORD           (u  - uppercase)
# - Password           (c  - capitalize)
# - pASSWORD           (C  - invert)
# - PaSsWoRd           (t  - toggle case)
#
# APPEND RULES (Hashcat $X):
# - password1          ($1)
# - password123        ($1$2$3)
# - password!          ($!)
# - password2024       ($2$0$2$4)
#
# PREPEND RULES (Hashcat ^X):
# - 1password          (^1)
# - 123password        (^3^2^1)
#
# LEET SPEAK (Hashcat sXY):
# - p@ssw0rd           (sa@se3si1so0ss$)
# - p4ssw0rd           (sa4se3si!so0)
#
# MANIPULATION RULES:
# - drowssap           (r  - reverse)
# - asswordp           ({  - rotate left)
# - passwordpassword   (d  - duplicate)
#
# COMBINED RULES:
# - Password1          (c$1)
# - Password123        (c$1$2$3)
# - Password2024       (c$2$0$2$4)
# - P@ssw0rd1          (csa@se3$1)
# - And 50+ more variations per word!

# Crack with rule engine enabled (default)
hash_value = "482c811da5d5b4bc6d497ffa98491e38"  # MD5 of "Password123"
result = cracker.crack(hash_value, "wordlist.txt", "md5")
# Will find "Password123" even if wordlist only contains "password"
```

**Optimized Rule Tiers** (25+ rules, prioritized by effectiveness):

**Tier 1 - Highest Success Rate** (Try first):
- `:` Nothing (original word)
- `c` Capitalize (Password)
- `$1$2$3` Append 123 (password123)
- `$1` Append 1 (password1)
- `c$1$2$3` Combined (Password123) ⭐ Most common
- `c$1` Combined (Password1)

**Tier 2 - Common Variations**:
- `u` Uppercase (PASSWORD)
- `l` Lowercase (password)
- `$1$2` Append 12
- `$!` Append !
- `c$!` Capitalize + ! (Password!)
- `$1$!` Append 1! (password1!)

**Tier 3 - Years** (Very common in real passwords):
- `$2$0$2$3` Append 2023
- `$2$0$2$4` Append 2024 ⭐ Current year
- `$2$0$2$5` Append 2025
- `c$2$0$2$4` Combined (Password2024)

**Tier 4 - Selective Leet Speak** (Highest impact):
- `sa@se3si1so0` Basic leet (p@ssw0rd)
- `sa@` Just a→@ (p@ssword)
- `so0` Just o→0 (passw0rd)

**Tier 5 - Additional Patterns**:
- `^1` Prepend 1 (1password)
- `$@` Append @ (password@)
- `c$1$2` Capitalize + 12 (Password12)
- `$1$2$3$4` Append 1234

**Performance Optimization**:
- Rules applied inline during wordlist iteration
- No intermediate storage - memory efficient
- Early termination on match
- Optimized for rockyou.txt (14M+ words)
- Prevents API timeouts with smart processing

### Advanced Usage - Progress Tracking

```python
from hash_lib.hash_cracker.cracker import Cracker

cracker = Cracker()

# Crack with progress tracking
for progress in cracker.crack_with_progress(hash_value, wordlist, algorithm):
    if progress['found']:
        print(f"Cracked! Password: {progress['plaintext']}")
        break
    else:
        print(f"Progress: {progress['attempts']} attempts, {progress['speed']} h/s")
```

---

## API Reference

### Hasher Class

#### `__init__()`
Initialize the Hasher instance.

#### `hash(text: str, algorithm: str = 'sha256') -> str`
Generate a hash from input text.

**Parameters**:
- `text` (str): Text to hash
- `algorithm` (str): Hash algorithm (default: 'sha256')

**Returns**:
- `str`: Hexadecimal hash string

**Raises**:
- `ValueError`: If algorithm is not supported
- `TypeError`: If text is not a string

**Example**:
```python
hasher = Hasher()
hash_value = hasher.hash("password", "sha256")
```

#### `supported_algorithms() -> list`
Get list of supported hash algorithms.

**Returns**:
- `list`: List of algorithm names

---

### HashIdentifier Class

#### `__init__()`
Initialize the HashIdentifier instance.

#### `identify(hash_value: str) -> list`
Identify possible hash types.

**Parameters**:
- `hash_value` (str): Hash string to identify

**Returns**:
- `list`: List of possible hash type names

**Raises**:
- `ValueError`: If hash format is invalid

**Example**:
```python
identifier = HashIdentifier()
types = identifier.identify("5f4dcc3b5aa765d61d8327deb882cf99")
```

---

### Cracker Class

#### `__init__()`
Initialize the Cracker instance.

#### `crack(hash_value: str, wordlist: str, algorithm: str = 'sha256', use_shuffler: bool = True) -> Optional[str]`
Attempt to crack a hash using a wordlist with optional shuffler.

**Parameters**:
- `hash_value` (str): Hash to crack
- `wordlist` (str): Path to wordlist file
- `algorithm` (str): Hash algorithm (default: 'sha256')
- `use_shuffler` (bool): Enable wordlist shuffler with regex templates (default: True)

**Returns**:
- `str`: Plaintext password if found
- `None`: If password not found

**Raises**:
- `FileNotFoundError`: If wordlist doesn't exist
- `ValueError`: If algorithm is not supported

**Example**:
```python
cracker = Cracker()

# With shuffler (recommended)
result = cracker.crack("5f4dcc3b5aa765d61d8327deb882cf99", "wordlist.txt", "md5")

# Without shuffler (exact matches only)
result = cracker.crack("5f4dcc3b5aa765d61d8327deb882cf99", "wordlist.txt", "md5", use_shuffler=False)
```

#### `_wordlist_shuffler(wordlist_path: str) -> Generator[str, None, None]`
Internal generator that yields transformed password candidates.

**Parameters**:
- `wordlist_path` (str): Path to wordlist file

**Yields**:
- `str`: Transformed password candidates based on regex templates

**Features**:
- Applies 25+ transformation patterns per word
- Handles empty lines gracefully
- Memory efficient (generator-based)
- Supports large wordlists (100M+ entries)

#### `crack_with_progress(hash_value: str, wordlist: str, algorithm: str) -> Generator`
Crack hash with progress updates.

**Parameters**:
- Same as `crack()`

**Yields**:
- `dict`: Progress information
  - `attempts` (int): Number of attempts
  - `speed` (float): Hashes per second
  - `found` (bool): Whether password was found
  - `plaintext` (str): Password if found

---

## Testing

### Running Tests

```bash
# Run all tests
cd tests
python -m pytest

# Run specific test file
python -m pytest test_cases_hasher.py

# Run with coverage
python -m pytest --cov=hash_lib --cov-report=html
```

### Test Cases

#### Hasher Tests
- Test all supported algorithms
- Test invalid algorithm handling
- Test empty string input
- Test special characters
- Test Unicode input
- Performance benchmarks

#### Identifier Tests
- Test MD5 identification
- Test SHA family identification
- Test invalid hash format
- Test edge cases (wrong length, invalid characters)

#### Cracker Tests
- Test successful cracking
- Test unsuccessful cracking
- Test invalid wordlist path
- Test large wordlist handling
- **Test wordlist shuffler basic transformations**
- **Test wordlist shuffler leet speak**
- **Test cracking with shuffler (capitalized passwords)**
- **Test cracking with shuffler (passwords with numbers)**
- **Test cracking without shuffler**
- **Test shuffler with empty lines**
- **Test shuffler file not found error**
- Performance benchmarks

### Example Test

```python
import pytest
from hash_lib.hash_core.hasher import Hasher

def test_sha256_hash():
    hasher = Hasher()
    result = hasher.hash("password", "sha256")
    expected = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    assert result == expected

def test_invalid_algorithm():
    hasher = Hasher()
    with pytest.raises(ValueError):
        hasher.hash("password", "invalid_algo")
```

---

## Best Practices

### Security Considerations

1. **Never use MD5 or SHA-1 for passwords**: Use bcrypt, Argon2, or PBKDF2
2. **This module is for education**: Not suitable for production password storage
3. **Ethical use only**: Only crack hashes you have permission to test
4. **Secure wordlists**: Keep wordlists secure and up-to-date

### Code Examples

#### Good Practice
```python
# Use strong algorithm for new hashes
hasher = Hasher()
secure_hash = hasher.hash(password, "sha512")

# Validate input before hashing
if not isinstance(password, str):
    raise TypeError("Password must be a string")
```

#### Bad Practice
```python
# Don't use weak algorithms for security
weak_hash = hasher.hash(password, "md5")  # ❌ Weak!

# Don't ignore errors
try:
    result = cracker.crack(hash_value, wordlist, algo)
except Exception:
    pass  # ❌ Don't ignore errors!
```

---

## Troubleshooting

### Common Issues

#### Issue: "Algorithm not supported"
**Solution**: Check supported algorithms with `hasher.supported_algorithms()`

#### Issue: "Wordlist not found"
**Solution**: Verify wordlist path is correct and file exists

#### Issue: "Slow cracking performance"
**Solution**:
- Use faster algorithm (MD5 vs SHA-512)
- Reduce wordlist size
- Use SSD for wordlist storage
- Consider parallel processing

#### Issue: "Memory error with large wordlist"
**Solution**: Cracker streams wordlist, but ensure sufficient RAM for OS caching

---

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/gilfi.git
cd gilfi/src/backend/hash-module

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Submitting Changes

1. Create a feature branch
2. Write tests for your changes
3. Ensure all tests pass
4. Submit a pull request


**Version**: 1.1.0
**Last Updated**: 2026-05-06
**Maintained By**: Gilfi Development Team

---

## Changelog

### Version 1.1.0 (2026-05-06)
- ✨ **NEW**: Wordlist shuffler with regex templates
- ✨ Added 25+ password transformation patterns
- ✨ Leet speak substitutions
- ✨ Case variations (capitalize, uppercase, lowercase)
- ✨ Number and special character combinations
- ✨ SQLite caching for cracked hashes
- 🧪 Added 6 new comprehensive tests for shuffler
- 📚 Updated documentation with shuffler examples
- 🚀 Significantly improved cracking success rate

### Version 1.0.0 (2026-04-28)
- Initial release
- Hash generation (MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512)
- Hash identification
- Basic wordlist cracking