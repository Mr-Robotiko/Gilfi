"""
Gilfi Module - Password Strength Analyzer
Analyzes password strength using comprehensive security criteria.
"""

from ui.toolpage import ToolPage
import api_client


def create_page():
    page = ToolPage(
        title="Password Analyzer & Generator",
        description="Analyze password strength or generate secure random passwords with customizable options."
    )
    page.add_field("Password", "Enter password to analyze (leave empty to generate)")
    page.add_field("Length", "Password length for generation (default: 16)")
    page.add_field("Options", "lowercase,uppercase,digits,special (default: all)")
    page.set_button_text("Analyze / Generate")
    page.on_run = run
    return page


def run(page):
    password = page.get_input("Password")
    length_str = page.get_input("Length")
    options_str = page.get_input("Options")

    page.clear_output()
    
    try:
        # If no password provided, generate one
        if not password:
            _generate_password(page, length_str, options_str)
        else:
            # Analyze provided password
            _analyze_password(page, password)
        
    except ConnectionError as e:
        page.set_status("Backend not available", error=True)
        page.append_output(str(e))
        page.append_output("\nMake sure the backend container is running:")
        page.append_output("  ./backend-docker.sh start")
    except Exception as e:
        page.set_status("Error", error=True)
        page.append_output(f"Error: {str(e)}")


def _generate_password(page, length_str, options_str):
    """Generate a secure random password"""
    page.set_status("Generating secure password...")
    
    # Parse length
    try:
        length = int(length_str) if length_str else 16
        length = max(8, min(128, length))  # Clamp between 8 and 128
    except ValueError:
        length = 16
    
    # Parse options
    options = options_str.lower() if options_str else "lowercase,uppercase,digits,special"
    use_lowercase = "lowercase" in options
    use_uppercase = "uppercase" in options
    use_digits = "digits" in options
    use_special = "special" in options
    
    # Ensure at least one option is selected
    if not any([use_lowercase, use_uppercase, use_digits, use_special]):
        use_lowercase = use_uppercase = use_digits = use_special = True
    
    # Generate password
    result = api_client.password_generate(
        length=length,
        use_lowercase=use_lowercase,
        use_uppercase=use_uppercase,
        use_digits=use_digits,
        use_special=use_special,
        exclude_ambiguous=True
    )
    
    # Display generated password
    page.append_output("=" * 60)
    page.append_output("🔐 GENERATED PASSWORD")
    page.append_output("=" * 60)
    page.append_output(f"\n{result['password']}\n")
    page.append_output("─" * 60)
    page.append_output(f"Length: {result['length']} characters")
    
    char_sets = result['character_sets']
    page.append_output("\nCharacter sets used:")
    if char_sets.get('lowercase'):
        page.append_output("  ✓ Lowercase letters (a-z)")
    if char_sets.get('uppercase'):
        page.append_output("  ✓ Uppercase letters (A-Z)")
    if char_sets.get('digits'):
        page.append_output("  ✓ Numbers (0-9)")
    if char_sets.get('special'):
        page.append_output("  ✓ Special characters (!@#$%^&*...)")
    page.append_output("  ✓ Ambiguous characters excluded (0/O, 1/l/I)")
    
    # Display analysis of generated password
    page.append_output("\n" + "=" * 60)
    page.append_output("STRENGTH ANALYSIS OF GENERATED PASSWORD")
    page.append_output("=" * 60)
    _display_results(page, result['analysis'], show_header=False)
    
    page.set_status("Password generated successfully")


def _analyze_password(page, password):
    """Analyze an existing password"""
    page.set_status("Analyzing password strength...")
    
    # Call API to analyze password
    result = api_client.password_analyze(password)
    
    # Display results with color-coded strength
    _display_results(page, result)
    page.set_status("Analysis complete")


def _display_results(page, result, show_header=True):
    """Display password analysis results with formatting"""
    
    # Header
    if show_header:
        page.append_output("=" * 60)
        page.append_output("PASSWORD STRENGTH ANALYSIS")
        page.append_output("=" * 60)
    
    # Strength indicator with visual representation
    strength = result['strength']
    score = result['score']
    
    # Color-coded strength display
    strength_display = _get_strength_display(strength, score)
    page.append_output(f"\n{strength_display}")
    page.append_output(f"Score: {score}/100")
    page.append_output(f"Security Status: {'✓ SECURE' if result['is_secure'] else '✗ NOT SECURE'}")
    
    # Progress bar
    bar_length = 40
    filled = int((score / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    page.append_output(f"\n[{bar}] {score}%")
    
    # Password details
    page.append_output("\n" + "─" * 60)
    page.append_output("PASSWORD DETAILS:")
    page.append_output("─" * 60)
    page.append_output(f"Length: {result['password_length']} characters")
    page.append_output(f"Unique characters: {result['details'].get('unique_characters', 'N/A')}")
    page.append_output(f"Character variety: {result['details'].get('character_variety', 'N/A')}/4 types")
    
    # Character type checks
    page.append_output("\n" + "─" * 60)
    page.append_output("CHARACTER ANALYSIS:")
    page.append_output("─" * 60)
    checks = result['checks']
    page.append_output(f"  Lowercase letters (a-z):  {'✓ Yes' if checks.get('has_lowercase') else '✗ No'}")
    page.append_output(f"  Uppercase letters (A-Z):  {'✓ Yes' if checks.get('has_uppercase') else '✗ No'}")
    page.append_output(f"  Numbers (0-9):            {'✓ Yes' if checks.get('has_digits') else '✗ No'}")
    page.append_output(f"  Special characters:       {'✓ Yes' if checks.get('has_special_chars') else '✗ No'}")
    
    # Security checks
    page.append_output("\n" + "─" * 60)
    page.append_output("SECURITY CHECKS:")
    page.append_output("─" * 60)
    page.append_output(f"  Common password:          {'✗ YES (WEAK!)' if checks.get('is_common_password') else '✓ No'}")
    page.append_output(f"  Consecutive characters:   {'✗ Found' if checks.get('has_consecutive_chars') else '✓ None'}")
    page.append_output(f"  Sequential numbers:       {'✗ Found' if checks.get('has_sequential_numbers') else '✓ None'}")
    page.append_output(f"  Sequential letters:       {'✗ Found' if checks.get('has_sequential_letters') else '✓ None'}")
    page.append_output(f"  Common patterns:          {'✗ Found' if checks.get('has_common_patterns') else '✓ None'}")
    page.append_output(f"  Entropy level:            {checks.get('entropy', 'N/A').upper()}")
    
    # Suggestions for improvement
    suggestions = result.get('suggestions', [])
    if suggestions:
        page.append_output("\n" + "─" * 60)
        page.append_output("💡 SUGGESTIONS FOR IMPROVEMENT:")
        page.append_output("─" * 60)
        for i, suggestion in enumerate(suggestions, 1):
            page.append_output(f"  {i}. {suggestion}")
    else:
        page.append_output("\n" + "─" * 60)
        page.append_output("✓ Excellent! No improvements needed.")
        page.append_output("─" * 60)
    
    # Strength description
    page.append_output("\n" + "=" * 60)
    page.append_output(_get_strength_description(strength))
    page.append_output("=" * 60)


def _get_strength_display(strength, score):
    """Get color-coded strength display"""
    displays = {
        'VERY_WEAK': f"Strength: ⚠️  VERY WEAK ⚠️",
        'WEAK': f"Strength: ⚠️  WEAK",
        'MODERATE': f"Strength: ⚡ MODERATE",
        'STRONG': f"Strength: ✓ STRONG",
        'VERY_STRONG': f"Strength: ✓✓ VERY STRONG ✓✓"
    }
    return displays.get(strength, f"Strength: {strength}")


def _get_strength_description(strength):
    """Get detailed description of strength level"""
    descriptions = {
        'VERY_WEAK': "⚠️  VERY WEAK - This password is easily crackable and should NOT be used.\nIt can be broken in seconds with basic tools.",
        'WEAK': "⚠️  WEAK - This password is vulnerable to attacks and should be improved.\nIt may be cracked within hours or days.",
        'MODERATE': "⚡ MODERATE - This password is acceptable but could be stronger.\nConsider adding more complexity for better security.",
        'STRONG': "✓ STRONG - This is a good password that is resistant to most attacks.\nIt would take significant time and resources to crack.",
        'VERY_STRONG': "✓✓ VERY STRONG - Excellent! This password is highly secure.\nIt would take years or centuries to crack with current technology."
    }
    return descriptions.get(strength, "Unknown strength level")

# Made with Bob
