"""
Password Strength Analyzer
Analyzes password quality using regex patterns and scoring system
"""

import re
import secrets
import string
from typing import Dict, List, Tuple
from enum import Enum


class PasswordStrength(Enum):
    """Password strength levels"""
    VERY_WEAK = 0
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


class PasswordAnalyzer:
    """
    Analyzes password strength based on multiple criteria using regex patterns
    """
    
    # Regex patterns for password analysis
    PATTERNS = {
        'lowercase': re.compile(r'[a-z]'),
        'uppercase': re.compile(r'[A-Z]'),
        'digits': re.compile(r'\d'),
        'special_chars': re.compile(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]'),
        'spaces': re.compile(r'\s'),
        'consecutive_chars': re.compile(r'(.)\1{2,}'),  # 3+ same chars in a row
        'sequential_numbers': re.compile(r'(012|123|234|345|456|567|678|789|890)'),
        'sequential_letters': re.compile(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', re.IGNORECASE),
        'common_patterns': re.compile(r'(password|pass|admin|user|login|qwerty|asdf|1234|letmein)', re.IGNORECASE),
    }
    
    # Common weak passwords
    COMMON_PASSWORDS = {
        'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
        'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou', 'master',
        'sunshine', 'ashley', 'bailey', 'shadow', 'superman', 'qazwsx',
        '123123', 'admin', 'welcome', 'login', 'passw0rd', 'password1'
    }
    
    def __init__(self):
        """Initialize the password analyzer"""
        pass
    
    def analyze(self, password: str) -> Dict:
        """
        Analyze password strength and return detailed results
        
        Args:
            password: The password string to analyze
            
        Returns:
            Dictionary containing:
                - strength: PasswordStrength enum value
                - score: Numeric score (0-100)
                - length: Password length
                - checks: Dictionary of individual checks
                - suggestions: List of improvement suggestions
                - details: Detailed breakdown of analysis
        """
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        
        # Initialize results
        score = 0
        checks = {}
        suggestions = []
        details = {}
        
        # Length analysis
        length = len(password)
        details['length'] = length
        
        if length == 0:
            return self._create_result(PasswordStrength.VERY_WEAK, 0, length, checks, 
                                      ["Password cannot be empty"], details)
        
        # Length scoring
        if length >= 16:
            score += 30
            checks['length'] = 'excellent'
        elif length >= 12:
            score += 25
            checks['length'] = 'good'
        elif length >= 8:
            score += 15
            checks['length'] = 'adequate'
        elif length >= 6:
            score += 5
            checks['length'] = 'weak'
            suggestions.append("Use at least 8 characters (12+ recommended)")
        else:
            checks['length'] = 'very_weak'
            suggestions.append("Password is too short. Use at least 8 characters")
        
        # Character variety checks
        has_lowercase = bool(self.PATTERNS['lowercase'].search(password))
        has_uppercase = bool(self.PATTERNS['uppercase'].search(password))
        has_digits = bool(self.PATTERNS['digits'].search(password))
        has_special = bool(self.PATTERNS['special_chars'].search(password))
        has_spaces = bool(self.PATTERNS['spaces'].search(password))
        
        checks['has_lowercase'] = has_lowercase
        checks['has_uppercase'] = has_uppercase
        checks['has_digits'] = has_digits
        checks['has_special_chars'] = has_special
        checks['has_spaces'] = has_spaces
        
        # Character variety scoring
        variety_count = sum([has_lowercase, has_uppercase, has_digits, has_special])
        details['character_variety'] = variety_count
        
        if variety_count == 4:
            score += 25
            checks['variety'] = 'excellent'
        elif variety_count == 3:
            score += 20
            checks['variety'] = 'good'
        elif variety_count == 2:
            score += 10
            checks['variety'] = 'moderate'
        else:
            checks['variety'] = 'weak'
        
        # Add suggestions for missing character types
        if not has_lowercase:
            suggestions.append("Add lowercase letters (a-z)")
        if not has_uppercase:
            suggestions.append("Add uppercase letters (A-Z)")
        if not has_digits:
            suggestions.append("Add numbers (0-9)")
        if not has_special:
            suggestions.append("Add special characters (!@#$%^&*)")
        
        # Complexity scoring (unique characters)
        unique_chars = len(set(password))
        details['unique_characters'] = unique_chars
        uniqueness_ratio = unique_chars / length if length > 0 else 0
        
        if uniqueness_ratio >= 0.8:
            score += 15
            checks['uniqueness'] = 'excellent'
        elif uniqueness_ratio >= 0.6:
            score += 10
            checks['uniqueness'] = 'good'
        elif uniqueness_ratio >= 0.4:
            score += 5
            checks['uniqueness'] = 'moderate'
        else:
            checks['uniqueness'] = 'weak'
            suggestions.append("Avoid repeating characters too much")
        
        # Pattern detection (negative scoring)
        has_consecutive = bool(self.PATTERNS['consecutive_chars'].search(password))
        has_sequential_nums = bool(self.PATTERNS['sequential_numbers'].search(password))
        has_sequential_letters = bool(self.PATTERNS['sequential_letters'].search(password))
        has_common_patterns = bool(self.PATTERNS['common_patterns'].search(password))
        
        checks['has_consecutive_chars'] = has_consecutive
        checks['has_sequential_numbers'] = has_sequential_nums
        checks['has_sequential_letters'] = has_sequential_letters
        checks['has_common_patterns'] = has_common_patterns
        
        if has_consecutive:
            score -= 10
            suggestions.append("Avoid repeating the same character multiple times")
        
        if has_sequential_nums:
            score -= 10
            suggestions.append("Avoid sequential numbers (e.g., 123, 456)")
        
        if has_sequential_letters:
            score -= 10
            suggestions.append("Avoid sequential letters (e.g., abc, xyz)")
        
        if has_common_patterns:
            score -= 15
            suggestions.append("Avoid common words like 'password', 'admin', 'qwerty'")
        
        # Check against common passwords
        is_common = password.lower() in self.COMMON_PASSWORDS
        checks['is_common_password'] = is_common
        
        if is_common:
            score -= 30
            suggestions.append("This is a commonly used password. Choose something unique")
        
        # Entropy bonus (randomness)
        if variety_count >= 3 and not has_consecutive and not has_sequential_nums and not has_sequential_letters:
            score += 10
            checks['entropy'] = 'high'
        else:
            checks['entropy'] = 'low'
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        details['raw_score'] = score
        
        # Determine strength level
        if score >= 80:
            strength = PasswordStrength.VERY_STRONG
        elif score >= 60:
            strength = PasswordStrength.STRONG
        elif score >= 40:
            strength = PasswordStrength.MODERATE
        elif score >= 20:
            strength = PasswordStrength.WEAK
        else:
            strength = PasswordStrength.VERY_WEAK
        
        # Add general suggestions if score is low
        if score < 60 and not suggestions:
            suggestions.append("Consider using a longer password with mixed character types")
        
        return self._create_result(strength, score, length, checks, suggestions, details)
    
    def _create_result(self, strength: PasswordStrength, score: int, length: int,
                      checks: Dict, suggestions: List[str], details: Dict) -> Dict:
        """Create standardized result dictionary"""
        return {
            'strength': strength.name,
            'strength_level': strength.value,
            'score': score,
            'length': length,
            'checks': checks,
            'suggestions': suggestions,
            'details': details,
            'is_secure': score >= 60
        }
    
    def get_strength_description(self, strength: PasswordStrength) -> str:
        """Get human-readable description of password strength"""
        descriptions = {
            PasswordStrength.VERY_WEAK: "Very Weak - Easily crackable, not recommended",
            PasswordStrength.WEAK: "Weak - Vulnerable to attacks, should be improved",
            PasswordStrength.MODERATE: "Moderate - Acceptable but could be stronger",
            PasswordStrength.STRONG: "Strong - Good password, resistant to most attacks",
            PasswordStrength.VERY_STRONG: "Very Strong - Excellent password, highly secure"
        }
        return descriptions.get(strength, "Unknown")
    
    def generate_report(self, password: str) -> str:
        """
        Generate a detailed text report of password analysis
        
        Args:
            password: The password to analyze
            
        Returns:
            Formatted string report
        """
        result = self.analyze(password)
        
        report = []
        report.append("=" * 60)
        report.append("PASSWORD STRENGTH ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nPassword Length: {result['length']} characters")
        report.append(f"Strength Level: {result['strength']} ({result['score']}/100)")
        report.append(f"Security Status: {'✓ SECURE' if result['is_secure'] else '✗ NOT SECURE'}")
        
        report.append("\n" + "-" * 60)
        report.append("CHARACTER ANALYSIS:")
        report.append("-" * 60)
        checks = result['checks']
        report.append(f"  Lowercase letters: {'✓' if checks.get('has_lowercase') else '✗'}")
        report.append(f"  Uppercase letters: {'✓' if checks.get('has_uppercase') else '✗'}")
        report.append(f"  Numbers: {'✓' if checks.get('has_digits') else '✗'}")
        report.append(f"  Special characters: {'✓' if checks.get('has_special_chars') else '✗'}")
        report.append(f"  Character variety: {checks.get('variety', 'N/A').upper()}")
        
        report.append("\n" + "-" * 60)
        report.append("SECURITY CHECKS:")
        report.append("-" * 60)
        report.append(f"  Common password: {'✗ YES (WEAK!)' if checks.get('is_common_password') else '✓ No'}")
        report.append(f"  Consecutive characters: {'✗ Found' if checks.get('has_consecutive_chars') else '✓ None'}")
        report.append(f"  Sequential numbers: {'✗ Found' if checks.get('has_sequential_numbers') else '✓ None'}")
        report.append(f"  Sequential letters: {'✗ Found' if checks.get('has_sequential_letters') else '✓ None'}")
        report.append(f"  Common patterns: {'✗ Found' if checks.get('has_common_patterns') else '✓ None'}")
        
        if result['suggestions']:
            report.append("\n" + "-" * 60)
            report.append("SUGGESTIONS FOR IMPROVEMENT:")
            report.append("-" * 60)
            for i, suggestion in enumerate(result['suggestions'], 1):
                report.append(f"  {i}. {suggestion}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def generate_password(self, length: int = 16, use_lowercase: bool = True,
                         use_uppercase: bool = True, use_digits: bool = True,
                         use_special: bool = True, exclude_ambiguous: bool = True) -> Dict:
        """
        Generate a cryptographically secure random password
        
        Args:
            length: Password length (default: 16, min: 8, max: 128)
            use_lowercase: Include lowercase letters (default: True)
            use_uppercase: Include uppercase letters (default: True)
            use_digits: Include digits (default: True)
            use_special: Include special characters (default: True)
            exclude_ambiguous: Exclude ambiguous characters like 0/O, 1/l/I (default: True)
            
        Returns:
            Dictionary containing:
                - password: Generated password string
                - length: Password length
                - analysis: Strength analysis of generated password
        """
        # Validate length
        length = max(8, min(128, length))
        
        # Build character set
        char_sets = []
        
        if use_lowercase:
            lowercase = string.ascii_lowercase
            if exclude_ambiguous:
                lowercase = lowercase.replace('l', '')  # Remove lowercase L
            char_sets.append(lowercase)
        
        if use_uppercase:
            uppercase = string.ascii_uppercase
            if exclude_ambiguous:
                uppercase = uppercase.replace('O', '').replace('I', '')  # Remove O and I
            char_sets.append(uppercase)
        
        if use_digits:
            digits = string.digits
            if exclude_ambiguous:
                digits = digits.replace('0', '').replace('1', '')  # Remove 0 and 1
            char_sets.append(digits)
        
        if use_special:
            # Use common special characters
            special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            char_sets.append(special)
        
        # Ensure at least one character set is selected
        if not char_sets:
            char_sets = [string.ascii_letters + string.digits]
        
        # Combine all character sets
        all_chars = ''.join(char_sets)
        
        # Generate password ensuring at least one character from each selected set
        password_chars = []
        
        # Add at least one character from each set
        for char_set in char_sets:
            password_chars.append(secrets.choice(char_set))
        
        # Fill remaining length with random characters
        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the password characters using secrets
        # Convert to list for shuffling
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
        
        password = ''.join(password_chars)
        
        # Analyze the generated password
        analysis = self.analyze(password)
        
        return {
            'password': password,
            'length': length,
            'analysis': analysis,
            'character_sets': {
                'lowercase': use_lowercase,
                'uppercase': use_uppercase,
                'digits': use_digits,
                'special': use_special
            }
        }

# Made with Bob
