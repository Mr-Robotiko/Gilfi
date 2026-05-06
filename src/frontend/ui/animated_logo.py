"""
Gilfi - Animated Logo Widget

Custom widget for the navigation sidebar:
  - circular crop of data/assets/logo.jpeg
  - pulsing cyan glow (matches accent #53a8d8)
  - rotating scanner arc + small accent arc (security-tool vibe)
  - graceful text fallback if the image cannot be loaded

The painting code is exposed as a module-level helper (`paint_animated_logo`)
so the splash overlay can reuse it at a different size/position.
"""

import math
import os

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPixmap,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget


# Resolve <project_root>/data/assets/logo.jpeg relative to this file.
_HERE = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "..", "data", "assets", "logo.jpeg")
)

# Theme colors (kept in sync with ui/style.py)
COLOR_ACCENT = QColor(83, 168, 216)    # #53a8d8  cyan
COLOR_GREEN = QColor(74, 222, 128)     # #4ade80
COLOR_RING = QColor(15, 52, 96)        # #0f3460


# ----------------------------------------------------------------------
# Module-level helpers (shared with SplashOverlay)
# ----------------------------------------------------------------------

def build_circular_pixmap(diameter):
    """
    Load the project logo, crop the central square, mask to a circle,
    and return a QPixmap of the requested diameter (in px).

    Returns None if the logo file is missing or unreadable so callers can
    fall back to a text rendering.
    """
    if not os.path.isfile(_LOGO_PATH):
        return None

    source = QPixmap(_LOGO_PATH)
    if source.isNull():
        return None

    # The actual round logo sits in the center of the JPEG.
    side = min(source.width(), source.height())
    x = (source.width() - side) // 2
    y = (source.height() - side) // 2
    square = source.copy(x, y, side, side).scaled(
        diameter, diameter,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    circular = QPixmap(diameter, diameter)
    circular.fill(Qt.GlobalColor.transparent)

    p = QPainter(circular)
    try:
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        path = QPainterPath()
        path.addEllipse(0, 0, diameter, diameter)
        p.setClipPath(path)
        p.drawPixmap(0, 0, square)
    finally:
        p.end()

    return circular


def paint_animated_logo(painter, cx, cy, radius, angle_deg, pulse_phase, pixmap):
    """
    Paint the full animated logo (glow + ring + scanner arcs + image)
    centered at (cx, cy) with the given radius. All decorative offsets scale
    with the radius so the visual stays balanced at any size.

    Args:
        painter:      active QPainter (Antialiasing + SmoothPixmapTransform should be on)
        cx, cy:       center in painter coordinates
        radius:       inner logo radius
        angle_deg:    current rotation angle for the scanner arcs (degrees)
        pulse_phase:  current phase for the glow pulse (radians)
        pixmap:       circular logo QPixmap, or None for text fallback
    """
    # All decorative offsets scale with radius
    glow_extent = radius * 0.28
    ring_offset = max(2.0, radius * 0.06)
    scanner_offset = max(4.0, radius * 0.12)
    arc_pen_width = max(2.0, radius * 0.034)

    # 0..1 pulse value
    pulse = (math.sin(pulse_phase) + 1) / 2

    # 1) Soft pulsing glow - 8 concentric rings with fading alpha
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(8, 0, -1):
        ring_radius = radius + (glow_extent * i / 8)
        alpha = int(28 * (1 - i / 8) * (0.55 + 0.45 * pulse))
        color = QColor(COLOR_ACCENT)
        color.setAlpha(alpha)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx, cy), ring_radius, ring_radius)

    # 2) Static thin ring just outside the logo
    painter.setPen(QPen(COLOR_RING, 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(
        QPointF(cx, cy), radius + ring_offset, radius + ring_offset
    )

    # 3) Rotating scanner arcs
    arc_radius = radius + scanner_offset
    rect = QRectF(
        cx - arc_radius, cy - arc_radius,
        2 * arc_radius, 2 * arc_radius,
    )

    # Main cyan arc (60 deg)
    cyan = QColor(COLOR_ACCENT)
    cyan.setAlpha(220)
    pen = QPen(cyan, arc_pen_width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawArc(rect, int(-angle_deg * 16), 60 * 16)

    # Small green accent arc on the opposite side (20 deg)
    green = QColor(COLOR_GREEN)
    green.setAlpha(180)
    pen = QPen(green, arc_pen_width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawArc(rect, int(-(angle_deg + 180) * 16), 20 * 16)

    # 4) The pixmap itself, or a text fallback
    if pixmap is not None:
        # drawPixmap with target rect lets Qt scale smoothly to any size
        target = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
        painter.drawPixmap(target, pixmap, QRectF(pixmap.rect()))
    else:
        # Text fallback - font scales with radius
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_RING))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
        font_size = max(10, int(radius * 0.34))
        font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(COLOR_ACCENT)
        text_rect = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "GILFI")


# ----------------------------------------------------------------------
# Widget
# ----------------------------------------------------------------------

class AnimatedLogo(QWidget):
    """Circular logo with a pulsing glow and a rotating scanner ring."""

    LOGO_DIAMETER = 130     # diameter of the inner logo circle
    GLOW_PADDING = 22       # space around the logo for glow + arcs

    def __init__(self, parent=None):
        super().__init__(parent)

        size = self.LOGO_DIAMETER + 2 * self.GLOW_PADDING
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._circular_pixmap = build_circular_pixmap(self.LOGO_DIAMETER)

        # Animation state (also touched by SplashOverlay for seamless handoff)
        self._angle = 0.0          # degrees - drives the rotating arcs
        self._pulse_phase = 0.0    # radians - drives the pulsing glow

        self._timer = QTimer(self)
        self._timer.setInterval(33)   # ~30 fps - smooth + cheap
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def _tick(self):
        # ~one full rotation every 8 seconds (1.5 deg/frame at 30 fps)
        self._angle = (self._angle + 1.5) % 360.0
        # Pulse cycles roughly every 2.6 s
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)
        self.update()

    # Pause animation when not visible (saves CPU when window is minimised)
    def showEvent(self, event):
        super().showEvent(event)
        if not self._timer.isActive():
            self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            cx = self.width() / 2
            cy = self.height() / 2
            radius = self.LOGO_DIAMETER / 2
            paint_animated_logo(
                p, cx, cy, radius,
                self._angle, self._pulse_phase, self._circular_pixmap,
            )
        finally:
            p.end()
