"""
Gilfi - Stylesheet (compatibility shim)

Themes now live in ``ui.theme``. This module keeps the old ``STYLESHEET``
import working so existing call sites (``main.py``) don't break.
For theme switching at runtime, use ``ui.theme.build_stylesheet(name)``
directly.
"""

from ui.theme import build_stylesheet

STYLESHEET = build_stylesheet()
