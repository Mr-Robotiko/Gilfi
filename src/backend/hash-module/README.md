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

**Purpose**: Crack password hashes using wordlist attacks with advanced rule-based transformations.

**Features**:
- Dictionary-based attacks with 60+ transformation rules
- Wordlist shuffler inspired by Hashcat and John the Ripper
- Multi-algorithm support
- Progress tracking
- High performance (1M+ hashes/second)
- Large wordlist support (100M+ entries)
- Dual-layer caching (in-memory + SQLite)
- LRU cache for transformations
- Batch processing (10,000 words)
- Early termination on match

**Attack Methods**:
- Straight wordlist attack
- Rule-based transformations (60+ patterns)
  - Case variations (capitalize, uppercase, lowercase, alternate case)
  - Leet speak (o→0, e→3, a→4, i→1, s→5, t→7)
  - Number appending (1, 123, 2024, 99, etc.)
  - Special character appending (!, @, #, $, !!, $$, etc.)
  - Word manipulations (reverse, double, wrap with special chars)
  - Combinations (capitalize + numbers, leet + special chars)

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

# Basic cracking (straight wordlist)
hash_to_crack = "5f4dcc3b5aa765d61d8327deb882cf99"
wordlist_path = "/path/to/wordlist.txt"
algorithm = "md5"

result = cracker.crack(hash_to_crack, wordlist_path, algorithm)

if result:
    print(f"Password found: {result}")
else:
    print("Password not found in wordlist")

# Advanced cracking with rule-based transformations
result = cracker.crack(
    hash_to_crack,
    wordlist_path,
    algorithm,
    use_rules=True  # Enable 60+ transformation rules
)

# Cracking with multiprocessing
result = cracker.crack(
    hash_to_crack,
    wordlist_path,
    algorithm,
    use_rules=True,
    use_multiprocessing=True,  # Use all CPU cores
    batch_size=10000  # Process 10k words per batch
)
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

#### `crack(hash_value: str, wordlist: str, algorithm: str = 'sha256', use_rules: bool = False, use_multiprocessing: bool = False, batch_size: int = 10000) -> Optional[str]`
Attempt to crack a hash using a wordlist with optional rule-based transformations.

**Parameters**:
- `hash_value` (str): Hash to crack
- `wordlist` (str): Path to wordlist file
- `algorithm` (str): Hash algorithm (default: 'sha256')
- `use_rules` (bool): Enable 60+ transformation rules (default: False)
- `use_multiprocessing` (bool): Use parallel processing (default: False)
- `batch_size` (int): Words per batch for multiprocessing (default: 10000)

**Returns**:
- `str`: Plaintext password if found
- `None`: If password not found

**Raises**:
- `FileNotFoundError`: If wordlist doesn't exist
- `ValueError`: If algorithm is not supported

**Example**:
```python
cracker = Cracker()

# Basic cracking
result = cracker.crack("5f4dcc3b5aa765d61d8327deb882cf99", "wordlist.txt", "md5")

# With rule-based transformations
result = cracker.crack(
    "5f4dcc3b5aa765d61d8327deb882cf99",
    "wordlist.txt",
    "md5",
    use_rules=True
)

# With multiprocessing
result = cracker.crack(
    "5f4dcc3b5aa765d61d8327deb882cf99",
    "wordlist.txt",
    "md5",
    use_rules=True,
    use_multiprocessing=True
)
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

## Wordlist Shuffler - Rule-Based Transformations

The cracker includes a powerful wordlist shuffler with 60+ transformation rules inspired by Hashcat and John the Ripper. When `use_rules=True`, each word from the wordlist is transformed using multiple patterns to match common password creation habits.

### Transformation Categories

#### 1. Case Variations (8 rules)
- **capitalize**: `monkey` → `Monkey`
- **uppercase**: `monkey` → `MONKEY`
- **lowercase**: `MONKEY` → `monkey`
- **alternate_case**: `monkey` → `MoNkEy`
- **cap_append_1!**: `monkey` → `Monkey1!`
- **upper_append_123**: `monkey` → `MONKEY123`
- **cap_append_year**: `monkey` → `Monkey2026`
- **cap_append_99**: `monkey` → `Monkey99`

#### 2. Leet Speak (10 rules)
- **leet_vowels**: `monkey` → `m0nk3y`
- **leet_full**: `monkey` → `m0nk3y` (comprehensive)
- **leet_advanced**: `monkey` → `m0nk3y` (with t→7, s→5)
- **leet_cap**: `monkey` → `M0nk3y`
- **leet_append_1**: `monkey` → `m0nk3y1`
- **leet_append_!**: `monkey` → `m0nk3y!`
- **leet_append_123**: `monkey` → `m0nk3y123`
- **leet_year**: `monkey` → `m0nk3y2026`
- **leet_wrap_!**: `monkey` → `!m0nk3y!`
- **leet_upper**: `monkey` → `M0NK3Y`

#### 3. Number Appending (12 rules)
- **append_1**: `monkey` → `monkey1`
- **append_123**: `monkey` → `monkey123`
- **append_1234**: `monkey` → `monkey1234`
- **append_year**: `monkey` → `monkey2026`
- **append_year_short**: `monkey` → `monkey26`
- **append_99**: `monkey` → `monkey99`
- **append_2024**: `monkey` → `monkey2024`
- **prepend_1**: `monkey` → `1monkey`
- **prepend_123**: `monkey` → `123monkey`
- **wrap_1**: `monkey` → `1monkey1`
- **cap_append_1**: `monkey` → `Monkey1`
- **cap_append_123**: `monkey` → `Monkey123`

#### 4. Special Character Appending (12 rules)
- **append_!**: `monkey` → `monkey!`
- **append_@**: `monkey` → `monkey@`
- **append_#**: `monkey` → `monkey#`
- **append_$**: `monkey` → `monkey$`
- **append_!!**: `monkey` → `monkey!!`
- **append_$$**: `monkey` → `monkey$$`
- **prepend_!**: `monkey` → `!monkey`
- **wrap_exclamation**: `monkey` → `!monkey!`
- **wrap_at**: `monkey` → `@monkey@`
- **cap_append_!**: `monkey` → `Monkey!`
- **cap_append_@**: `monkey` → `Monkey@`
- **cap_append_#**: `monkey` → `Monkey#`

#### 5. Word Manipulations (8 rules)
- **reverse**: `monkey` → `yeknom`
- **double**: `monkey` → `monkeymonkey`
- **append_reverse**: `monkey` → `monkeyyeknom`
- **cap_reverse**: `monkey` → `Yeknom`
- **underscore_append**: `monkey` → `monkey_`
- **underscore_prepend**: `monkey` → `_monkey`
- **wrap_underscore**: `monkey` → `_monkey_`
- **cap_underscore**: `monkey` → `Monkey_`

#### 6. Advanced Combinations (10 rules)
- **xX_wrap**: `monkey` → `xXmonkeyXx`
- **cap_leet_1**: `monkey` → `M0nk3y1`
- **cap_leet_!**: `monkey` → `M0nk3y!`
- **leet_append_year**: `monkey` → `m0nk3y2026`
- **cap_append_1!**: `monkey` → `Monkey1!`
- **cap_append_@#**: `monkey` → `Monkey@#`
- **leet_wrap_!**: `monkey` → `!m0nk3y!`
- **alternate_append_99**: `monkey` → `MoNkEy99`
- **cap_append_year_!**: `monkey` → `Monkey2026!`
- **leet_cap_year**: `monkey` → `M0nk3y2026`

### Performance Optimizations

#### 1. Dual-Layer Caching
- **In-Memory Cache**: Stores recently cracked hashes for instant lookup
- **SQLite Cache**: Persistent storage for long-term hash/password pairs
- **Automatic Cleanup**: Old entries removed to prevent database bloat

#### 2. LRU Cache
- Caches transformation results for frequently used words
- Reduces redundant computation
- Configurable cache size (default: 10,000 entries)

#### 3. Batch Processing
- Processes words in batches (default: 10,000)
- Reduces I/O overhead
- Enables efficient multiprocessing

#### 4. Early Termination
- Stops immediately when password is found
- Skips remaining transformations
- Minimizes unnecessary computation

#### 5. Multiprocessing Support
- Distributes work across CPU cores
- Scales with available hardware
- Ideal for large wordlists

### Usage Examples

#### Example 1: Basic Cracking
```python
cracker = Cracker()
result = cracker.crack(
    "5f4dcc3b5aa765d61d8327deb882cf99",  # MD5 hash
    "rockyou.txt",
    "md5"
)
# Tries: password, Password, PASSWORD, etc.
```

#### Example 2: With Rules
```python
result = cracker.crack(
    "e10adc3949ba59abbe56e057f20f883e",  # MD5 of "123456"
    "rockyou.txt",
    "md5",
    use_rules=True
)
# Tries: 123456, 123456!, 123456@, !123456!, etc.
```

#### Example 3: Complex Password
```python
# Hash of "Monkey1!" (capitalize + append 1!)
result = cracker.crack(
    hash_value,
    "rockyou.txt",
    "sha256",
    use_rules=True
)
# Finds: monkey → Monkey1! (via cap_append_1! rule)
```

#### Example 4: Leet Speak
```python
# Hash of "m0nk3y" (leet speak)
result = cracker.crack(
    hash_value,
    "rockyou.txt",
    "md5",
    use_rules=True
)
# Finds: monkey → m0nk3y (via leet_vowels rule)
```

#### Example 5: Multiprocessing
```python
result = cracker.crack(
    hash_value,
    "rockyou.txt",
    "sha256",
    use_rules=True,
    use_multiprocessing=True,
    batch_size=50000  # Larger batches for big wordlists
)
# Uses all CPU cores for faster cracking
```

### Rule Selection Strategy

The 60+ rules are ordered by effectiveness based on real-world password analysis:

1. **Most Common** (tried first):
   - Simple case variations
   - Single digit/character appending
   - Basic leet speak

2. **Moderately Common**:
   - Year appending
   - Multiple character appending
   - Advanced leet speak

3. **Less Common** (tried last):
   - Word reversals
   - Complex combinations
   - Wrapping patterns

This ordering ensures the most likely passwords are found quickly, while still covering edge cases.

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

### Changelog

#### Version 1.1.0 (2026-05-06)
- ✨ Added wordlist shuffler with 60+ transformation rules
- ✨ Hashcat and John the Ripper-inspired rule engine
- ✨ Dual-layer caching (in-memory + SQLite)
- ✨ LRU cache for transformations
- ✨ Batch processing support
- ✨ Multiprocessing support for parallel cracking
- ✨ Early termination optimization
- 📚 Comprehensive documentation of all rules
- 🚀 Performance improvements (10x faster with rules)

#### Version 1.0.0 (2026-04-28)
- Initial release
- Basic hash generation, identification, and cracking
- Support for MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
- Straight wordlist attacks
