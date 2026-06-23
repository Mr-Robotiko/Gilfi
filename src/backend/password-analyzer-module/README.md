# Password Analyzer Module

Comprehensive password strength analysis and secure password generation module for Gilfi.

## Features

### Password Analysis
- **Strength Levels**: VERY_WEAK, WEAK, MODERATE, STRONG, VERY_STRONG
- **Scoring System**: 0-100 points based on multiple security criteria
- **Character Analysis**: Lowercase, uppercase, digits, special characters
- **Pattern Detection**: Consecutive chars, sequential numbers/letters, common patterns
- **Common Password Check**: Database of 20+ commonly used weak passwords
- **Entropy Calculation**: Randomness and unpredictability assessment
- **Actionable Suggestions**: Specific recommendations for improvement

### Password Generation
- **Cryptographically Secure**: Uses Python's `secrets` module
- **Customizable Length**: 8-128 characters
- **Configurable Character Sets**: Lowercase, uppercase, digits, special characters
- **Ambiguous Character Exclusion**: Optionally excludes 0/O, 1/l/I for clarity
- **Character Set Diversity**: Ensures at least one character from each selected set
- **Automatic Analysis**: Generated passwords are automatically analyzed for strength

## Installation

```bash
cd src/backend/password-analyzer-module
pip install -e .
```

## Usage

### Password Analysis

```python
from password_lib.analyzer import PasswordAnalyzer

analyzer = PasswordAnalyzer()

# Analyze a password
result = analyzer.analyze("MyP@ssw0rd2024")

print(f"Strength: {result['strength']}")  # STRONG
print(f"Score: {result['score']}/100")    # 75/100
print(f"Secure: {result['is_secure']}")   # True

# Get suggestions
for suggestion in result['suggestions']:
    print(f"- {suggestion}")
```

### Password Generation

```python
from password_lib.analyzer import PasswordAnalyzer

analyzer = PasswordAnalyzer()

# Generate a secure password
result = analyzer.generate_password(
    length=16,
    use_lowercase=True,
    use_uppercase=True,
    use_digits=True,
    use_special=True,
    exclude_ambiguous=True
)

print(f"Password: {result['password']}")
print(f"Strength: {result['analysis']['strength']}")
print(f"Score: {result['analysis']['score']}/100")
```

### Generate Report

```python
analyzer = PasswordAnalyzer()

# Generate detailed text report
report = analyzer.generate_report("TestPassword123!")
print(report)
```

## Analysis Criteria

### Length Scoring (30 points max)
- 16+ characters: 30 points (excellent)
- 12-15 characters: 25 points (good)
- 8-11 characters: 15 points (adequate)
- 6-7 characters: 5 points (weak)
- <6 characters: 0 points (very weak)

### Character Variety (25 points max)
- 4 types (lowercase, uppercase, digits, special): 25 points
- 3 types: 20 points
- 2 types: 10 points
- 1 type: 0 points

### Uniqueness (15 points max)
- Based on ratio of unique characters to total length
- 80%+ unique: 15 points
- 60-79% unique: 10 points
- 40-59% unique: 5 points
- <40% unique: 0 points

### Entropy Bonus (10 points)
- Awarded for high randomness (variety + no patterns)

### Negative Scoring
- Consecutive characters (aaa, 111): -10 points
- Sequential numbers (123, 456): -10 points
- Sequential letters (abc, xyz): -10 points
- Common patterns (password, admin): -15 points
- Common password: -30 points

## Strength Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| VERY_WEAK | 0-19 | Easily crackable, not recommended |
| WEAK | 20-39 | Vulnerable to attacks, should be improved |
| MODERATE | 40-59 | Acceptable but could be stronger |
| STRONG | 60-79 | Good password, resistant to most attacks |
| VERY_STRONG | 80-100 | Excellent password, highly secure |

## Password Generation Options

### Length
- Minimum: 8 characters
- Maximum: 128 characters
- Recommended: 16+ characters

### Character Sets
- **Lowercase**: a-z (26 characters)
- **Uppercase**: A-Z (26 characters)
- **Digits**: 0-9 (10 characters)
- **Special**: !@#$%^&*()_+-=[]{}|;:,.<>? (25 characters)

### Ambiguous Character Exclusion
When enabled, excludes:
- `0` (zero) - can be confused with `O` (letter O)
- `1` (one) - can be confused with `l` (lowercase L) or `I` (uppercase i)
- `O` (uppercase O) - can be confused with `0` (zero)
- `I` (uppercase I) - can be confused with `1` (one) or `l` (lowercase L)
- `l` (lowercase L) - can be confused with `1` (one) or `I` (uppercase i)

## API Integration

### Analyze Password
```bash
curl -X POST http://localhost:8000/api/password/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd2024"}'
```

### Generate Password
```bash
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{
    "length": 16,
    "use_lowercase": true,
    "use_uppercase": true,
    "use_digits": true,
    "use_special": true,
    "exclude_ambiguous": true
  }'
```

## Testing

Run the test suite:

```bash
cd src/backend/password-analyzer-module
python -m pytest tests/
```

Or run tests manually:

```bash
python tests/test_password_analyzer.py
```

## Security Considerations

### For Analysis
- This module analyzes password strength but does NOT store passwords
- Analysis is performed locally without network transmission
- Results are returned immediately without logging

### For Generation
- Uses `secrets` module for cryptographically secure randomness
- NOT suitable for cryptographic keys (use dedicated key generation tools)
- Generated passwords should be stored securely (use password managers)
- Never transmit passwords over unencrypted connections

### Best Practices
1. **Minimum Length**: Use at least 12 characters (16+ recommended)
2. **Character Variety**: Include all four character types
3. **Avoid Patterns**: No sequential or repeated characters
4. **Unique Passwords**: Different password for each service
5. **Regular Updates**: Change passwords periodically
6. **Password Manager**: Use a password manager to store complex passwords

## Common Weak Passwords

The analyzer checks against a database of commonly used weak passwords:
- password, 123456, 12345678, qwerty, abc123
- monkey, letmein, trustno1, dragon, baseball
- iloveyou, master, sunshine, ashley, bailey
- shadow, superman, qazwsx, 123123, admin
- welcome, login, passw0rd, password1

## Examples

### Example 1: Weak Password
```python
result = analyzer.analyze("password123")
# Strength: WEAK
# Score: 25/100
# Suggestions:
#   - Add uppercase letters (A-Z)
#   - Add special characters (!@#$%^&*)
#   - Avoid common words like 'password'
```

### Example 2: Strong Password
```python
result = analyzer.analyze("Xk9#mP2@qL5$")
# Strength: STRONG
# Score: 75/100
# Suggestions: (none - good password!)
```

### Example 3: Very Strong Password
```python
result = analyzer.analyze("C0mpl3x!P@ssw0rd#2024$Secure")
# Strength: VERY_STRONG
# Score: 95/100
# Suggestions: (none - excellent password!)
```

### Example 4: Generate Password
```python
result = analyzer.generate_password(length=20)
# Password: Xk9#mP2@qL5$wR3!tY7%
# Strength: VERY_STRONG
# Score: 98/100
```

## Version History

### Version 1.1.0 (2026-05-06)
- ✨ Added secure password generation with `secrets` module
- ✨ Customizable character sets and length
- ✨ Ambiguous character exclusion option
- ✨ Automatic strength analysis of generated passwords
- 📚 Enhanced documentation

### Version 1.0.0 (2026-04-28)
- Initial release
- Password strength analysis
- Scoring system (0-100)
- Pattern detection
- Common password checking
- Detailed reporting

## License

See main project LICENSE file.

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass
2. Code follows existing style
3. Documentation is updated
4. Security best practices are followed
