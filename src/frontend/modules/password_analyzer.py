"""
Gilfi Module - Password Strength Analyzer
Analyzes password strength using comprehensive security criteria.
"""

from ui.toolpage import ToolPage
import api_client


# Map backend strength levels to a colour helper on the page.
def _strength_method(page, strength):
    return {
        'VERY_WEAK':   page.append_error,
        'WEAK':        page.append_error,
        'MODERATE':    page.append_warning,
        'STRONG':      page.append_success,
        'VERY_STRONG': page.append_success,
    }.get(strength, page.append_output)


def create_page():
    page = ToolPage(
        title="Password Analyzer & Generator",
        description=("Analyze password strength or generate secure random passwords "
                     "with customizable options."),
        help_text=(
            "Two modes — driven by whether you fill in the Password field:\n\n"
            "  • Analyze: enter your password and get a score (0–100) plus "
            "a breakdown of what's weak about it (sequential characters, "
            "common patterns, dictionary words, etc.).\n"
            "  • Generate: leave the Password field empty and the module "
            "produces a strong random one based on your settings.\n\n"
            "Fields:\n"
            "  • Password — empty to generate, filled to analyze.\n"
            "  • Length — for generation (8–128, default 16).\n"
            "  • Options — comma-separated subset of lowercase, uppercase, "
            "digits, special. Empty = all four.\n\n"
            "Tip: a long passphrase (4+ random words) beats a short "
            "complex password almost every time."
        )
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

    if not password:
        _generate_password(page, length_str, options_str)
    else:
        _analyze_password(page, password)


def _generate_password(page, length_str, options_str):
    """Generate a secure random password asynchronously."""
    try:
        length = int(length_str) if length_str else 16
        length = max(8, min(128, length))  # clamp 8..128
    except ValueError:
        length = 16

    options = options_str.lower() if options_str else "lowercase,uppercase,digits,special"
    use_lowercase = "lowercase" in options
    use_uppercase = "uppercase" in options
    use_digits = "digits" in options
    use_special = "special" in options

    if not any([use_lowercase, use_uppercase, use_digits, use_special]):
        use_lowercase = use_uppercase = use_digits = use_special = True

    page.run_async(
        work_fn=lambda: api_client.password_generate(
            length=length,
            use_lowercase=use_lowercase,
            use_uppercase=use_uppercase,
            use_digits=use_digits,
            use_special=use_special,
            exclude_ambiguous=True,
        ),
        on_success=lambda result: _show_generated(page, result),
        running_text="Generating secure password ...",
        done_text="Password generated",
    )


def _show_generated(page, result):
    page.append_accent("=" * 60)
    page.append_accent("🔐 GENERATED PASSWORD")
    page.append_accent("=" * 60)
    page.append_success(f"\n{result['password']}\n")
    page.append_dim("─" * 60)
    page.append_output(f"Length: {result['length']} characters")

    char_sets = result['character_sets']
    page.append_dim("\nCharacter sets used:")
    if char_sets.get('lowercase'):
        page.append_success("  ✓ Lowercase letters (a-z)")
    if char_sets.get('uppercase'):
        page.append_success("  ✓ Uppercase letters (A-Z)")
    if char_sets.get('digits'):
        page.append_success("  ✓ Numbers (0-9)")
    if char_sets.get('special'):
        page.append_success("  ✓ Special characters (!@#$%^&*...)")
    page.append_success("  ✓ Ambiguous characters excluded (0/O, 1/l/I)")

    page.append_accent("\n" + "=" * 60)
    page.append_accent("STRENGTH ANALYSIS OF GENERATED PASSWORD")
    page.append_accent("=" * 60)
    _display_results(page, result['analysis'], show_header=False)


def _analyze_password(page, password):
    """Analyze an existing password asynchronously."""
    page.run_async(
        work_fn=lambda: api_client.password_analyze(password),
        on_success=lambda result: _display_results(page, result),
        running_text="Analyzing password strength ...",
        done_text="Analysis complete",
    )


def _display_results(page, result, show_header=True):
    """Display password analysis results with formatting."""
    if show_header:
        page.append_accent("=" * 60)
        page.append_accent("PASSWORD STRENGTH ANALYSIS")
        page.append_accent("=" * 60)

    strength = result['strength']
    score = result['score']
    strength_writer = _strength_method(page, strength)

    strength_writer(f"\n{_get_strength_display(strength)}")
    page.append_output(f"Score: {score}/100")
    if result['is_secure']:
        page.append_success("Security Status: ✓ SECURE")
    else:
        page.append_error("Security Status: ✗ NOT SECURE")

    bar_length = 40
    filled = int((score / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    strength_writer(f"\n[{bar}] {score}%")

    page.append_dim("\n" + "─" * 60)
    page.append_dim("PASSWORD DETAILS:")
    page.append_dim("─" * 60)
    page.append_output(f"Length: {result['password_length']} characters")
    page.append_output(f"Unique characters: {result['details'].get('unique_characters', 'N/A')}")
    page.append_output(f"Character variety: {result['details'].get('character_variety', 'N/A')}/4 types")

    page.append_dim("\n" + "─" * 60)
    page.append_dim("CHARACTER ANALYSIS:")
    page.append_dim("─" * 60)
    checks = result['checks']
    _check_line(page, "Lowercase letters (a-z):", checks.get('has_lowercase'))
    _check_line(page, "Uppercase letters (A-Z):", checks.get('has_uppercase'))
    _check_line(page, "Numbers (0-9):", checks.get('has_digits'))
    _check_line(page, "Special characters:", checks.get('has_special_chars'))

    page.append_dim("\n" + "─" * 60)
    page.append_dim("SECURITY CHECKS:")
    page.append_dim("─" * 60)
    if checks.get('is_common_password'):
        page.append_error("  Common password:          ✗ YES (WEAK!)")
    else:
        page.append_success("  Common password:          ✓ No")
    _check_line(page, "Consecutive characters:", not checks.get('has_consecutive_chars'),
                yes_label="None", no_label="Found")
    _check_line(page, "Sequential numbers:", not checks.get('has_sequential_numbers'),
                yes_label="None", no_label="Found")
    _check_line(page, "Sequential letters:", not checks.get('has_sequential_letters'),
                yes_label="None", no_label="Found")
    _check_line(page, "Common patterns:", not checks.get('has_common_patterns'),
                yes_label="None", no_label="Found")
    entropy = checks.get('entropy', 'N/A')
    if isinstance(entropy, str):
        entropy = entropy.upper()
    page.append_output(f"  Entropy level:            {entropy}")

    suggestions = result.get('suggestions', [])
    if suggestions:
        page.append_dim("\n" + "─" * 60)
        page.append_warning("💡 SUGGESTIONS FOR IMPROVEMENT:")
        page.append_dim("─" * 60)
        for i, suggestion in enumerate(suggestions, 1):
            page.append_warning(f"  {i}. {suggestion}")
    else:
        page.append_dim("\n" + "─" * 60)
        page.append_success("✓ Excellent! No improvements needed.")
        page.append_dim("─" * 60)

    page.append_accent("\n" + "=" * 60)
    strength_writer(_get_strength_description(strength))
    page.append_accent("=" * 60)


def _check_line(page, label, ok, yes_label="Yes", no_label="No"):
    label_padded = label.ljust(26)
    if ok:
        page.append_success(f"  {label_padded} ✓ {yes_label}")
    else:
        page.append_error(f"  {label_padded} ✗ {no_label}")


def _get_strength_display(strength):
    displays = {
        'VERY_WEAK':   "Strength: ⚠️  VERY WEAK ⚠️",
        'WEAK':        "Strength: ⚠️  WEAK",
        'MODERATE':    "Strength: ⚡ MODERATE",
        'STRONG':      "Strength: ✓ STRONG",
        'VERY_STRONG': "Strength: ✓✓ VERY STRONG ✓✓",
    }
    return displays.get(strength, f"Strength: {strength}")


def _get_strength_description(strength):
    descriptions = {
        'VERY_WEAK':   "⚠️  VERY WEAK - This password is easily crackable and should NOT be used.\nIt can be broken in seconds with basic tools.",
        'WEAK':        "⚠️  WEAK - This password is vulnerable to attacks and should be improved.\nIt may be cracked within hours or days.",
        'MODERATE':    "⚡ MODERATE - This password is acceptable but could be stronger.\nConsider adding more complexity for better security.",
        'STRONG':      "✓ STRONG - This is a good password that is resistant to most attacks.\nIt would take significant time and resources to crack.",
        'VERY_STRONG': "✓✓ VERY STRONG - Excellent! This password is highly secure.\nIt would take years or centuries to crack with current technology.",
    }
    return descriptions.get(strength, "Unknown strength level")
