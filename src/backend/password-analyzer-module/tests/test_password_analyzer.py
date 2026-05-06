"""
Test cases for Password Analyzer module
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from password_lib.analyzer import PasswordAnalyzer, PasswordStrength


class TestPasswordAnalyzer:
    """Test suite for PasswordAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = PasswordAnalyzer()
    
    def test_empty_password(self):
        """Test empty password returns very weak"""
        result = self.analyzer.analyze("")
        assert result['strength'] == PasswordStrength.VERY_WEAK.name
        assert result['score'] == 0
        assert result['length'] == 0
        assert not result['is_secure']
    
    def test_very_weak_password(self):
        """Test very weak passwords"""
        weak_passwords = ['123', 'abc', 'password', '12345678']
        
        for pwd in weak_passwords:
            result = self.analyzer.analyze(pwd)
            assert result['score'] < 40, f"Password '{pwd}' should be weak"
            assert not result['is_secure']
    
    def test_weak_password(self):
        """Test weak passwords"""
        result = self.analyzer.analyze('password123')
        assert result['strength'] in [PasswordStrength.WEAK.name, PasswordStrength.VERY_WEAK.name]
        assert result['score'] < 60
        assert not result['is_secure']
    
    def test_moderate_password(self):
        """Test moderate strength passwords"""
        result = self.analyzer.analyze('Password123')
        assert result['score'] >= 20
        assert result['checks']['has_lowercase']
        assert result['checks']['has_uppercase']
        assert result['checks']['has_digits']
    
    def test_strong_password(self):
        """Test strong passwords"""
        result = self.analyzer.analyze('MyP@ssw0rd2024')
        assert result['score'] >= 60
        assert result['is_secure']
        assert result['checks']['has_lowercase']
        assert result['checks']['has_uppercase']
        assert result['checks']['has_digits']
        assert result['checks']['has_special_chars']
    
    def test_very_strong_password(self):
        """Test very strong passwords"""
        result = self.analyzer.analyze('C0mpl3x!P@ssw0rd#2024$Secure')
        assert result['strength'] == PasswordStrength.VERY_STRONG.name
        assert result['score'] >= 80
        assert result['is_secure']
        assert result['checks']['variety'] == 'excellent'
    
    def test_length_scoring(self):
        """Test password length affects score"""
        short = self.analyzer.analyze('Abc1!')
        medium = self.analyzer.analyze('Abc123!@#')
        long = self.analyzer.analyze('Abc123!@#DefGhi456$%^')
        
        assert short['score'] < medium['score']
        assert medium['score'] < long['score']
    
    def test_character_variety(self):
        """Test character variety detection"""
        # Only lowercase
        result = self.analyzer.analyze('abcdefgh')
        assert result['checks']['has_lowercase']
        assert not result['checks']['has_uppercase']
        assert not result['checks']['has_digits']
        assert not result['checks']['has_special_chars']
        
        # Mixed types
        result = self.analyzer.analyze('Abc123!@#')
        assert result['checks']['has_lowercase']
        assert result['checks']['has_uppercase']
        assert result['checks']['has_digits']
        assert result['checks']['has_special_chars']
    
    def test_consecutive_characters(self):
        """Test detection of consecutive characters"""
        result = self.analyzer.analyze('Passsword111')
        assert result['checks']['has_consecutive_chars']
        assert 'repeating' in ' '.join(result['suggestions']).lower()
    
    def test_sequential_numbers(self):
        """Test detection of sequential numbers"""
        result = self.analyzer.analyze('Pass123word')
        assert result['checks']['has_sequential_numbers']
    
    def test_sequential_letters(self):
        """Test detection of sequential letters"""
        result = self.analyzer.analyze('Abcdefg123!')
        assert result['checks']['has_sequential_letters']
    
    def test_common_patterns(self):
        """Test detection of common patterns"""
        common_patterns = ['password123', 'admin2024', 'qwerty123', 'letmein!']
        
        for pwd in common_patterns:
            result = self.analyzer.analyze(pwd)
            assert result['checks']['has_common_patterns']
    
    def test_common_passwords(self):
        """Test detection of common passwords"""
        common = ['password', '123456', 'qwerty', 'admin']
        
        for pwd in common:
            result = self.analyzer.analyze(pwd)
            assert result['checks']['is_common_password']
            assert result['score'] < 40
    
    def test_uniqueness_scoring(self):
        """Test uniqueness affects score"""
        repetitive = self.analyzer.analyze('aaaaaaBBBBBB111111')
        unique = self.analyzer.analyze('Ab1!Cd2@Ef3#Gh4$')
        
        assert unique['details']['unique_characters'] > repetitive['details']['unique_characters']
    
    def test_suggestions_provided(self):
        """Test that suggestions are provided for weak passwords"""
        result = self.analyzer.analyze('weak')
        assert len(result['suggestions']) > 0
        
        result = self.analyzer.analyze('VeryStr0ng!P@ssw0rd#2024')
        # Strong passwords may have fewer or no suggestions
        assert isinstance(result['suggestions'], list)
    
    def test_type_error_handling(self):
        """Test that non-string input raises TypeError"""
        try:
            self.analyzer.analyze(12345)
            assert False, "Should raise TypeError"
        except TypeError:
            pass
    
    def test_generate_report(self):
        """Test report generation"""
        report = self.analyzer.generate_report('TestP@ss123')
        assert 'PASSWORD STRENGTH ANALYSIS REPORT' in report
        assert 'CHARACTER ANALYSIS' in report
        assert 'SECURITY CHECKS' in report
        assert isinstance(report, str)
        assert len(report) > 100
    
    def test_strength_description(self):
        """Test strength description method"""
        desc = self.analyzer.get_strength_description(PasswordStrength.VERY_STRONG)
        assert 'Very Strong' in desc
        assert 'secure' in desc.lower()
        
        desc = self.analyzer.get_strength_description(PasswordStrength.VERY_WEAK)
        assert 'Very Weak' in desc
    
    def test_result_structure(self):
        """Test that result has all required fields"""
        result = self.analyzer.analyze('TestPassword123!')
        
        required_fields = [
            'strength', 'strength_level', 'score', 'length',
            'checks', 'suggestions', 'details', 'is_secure'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_score_range(self):
        """Test that score is always between 0 and 100"""
        test_passwords = [
            '', 'a', '123', 'password', 'Password123',
            'Str0ng!Pass', 'VeryStr0ng!P@ssw0rd#2024'
        ]
        
        for pwd in test_passwords:
            result = self.analyzer.analyze(pwd)
            assert 0 <= result['score'] <= 100, f"Score out of range for '{pwd}'"
    
    def test_special_characters_detection(self):
        """Test various special characters are detected"""
        special_chars = '!@#$%^&*()_+-=[]{};\':"|,.<>?/\\`~'
        
        for char in special_chars:
            pwd = f'Pass123{char}'
            result = self.analyzer.analyze(pwd)
            assert result['checks']['has_special_chars'], f"Failed to detect: {char}"
    
    def test_spaces_detection(self):
        """Test space detection in passwords"""
        result = self.analyzer.analyze('Pass word 123')
        assert result['checks']['has_spaces']
    
    def test_entropy_bonus(self):
        """Test entropy bonus for random-looking passwords"""
        # High entropy password
        result_high = self.analyzer.analyze('Xk9#mP2@qL5$')
        
        # Low entropy password
        result_low = self.analyzer.analyze('Password123')
        
        # High entropy should have better entropy check
        assert result_high['checks'].get('entropy') == 'high' or result_high['score'] > result_low['score']


def run_tests():
    """Run all tests manually"""
    import traceback
    
    test_class = TestPasswordAnalyzer()
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("Running Password Analyzer Tests")
    print("=" * 70)
    
    for method_name in test_methods:
        test_class.setup_method()
        try:
            method = getattr(test_class, method_name)
            method()
            print(f"✓ {method_name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {method_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {method_name}: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

# Made with Bob
