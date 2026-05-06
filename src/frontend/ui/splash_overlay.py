"""
Gilfi - Splash Overlay

Startup splash that appears on top of the MainWindow:
  - dark overlay covers the GUI
  - logo fades in big, centered, with pulsing glow + rotating scanner
  - "Security Tool Suite" tagline fades in below
  - after a short hold, logo simultaneously shrinks and flies to the
    AnimatedLogo's position in the nav sidebar
  - splash hides instantly at the handoff moment; the static
    AnimatedLogo (with its phase synced) takes over seamlessly

Skip: click anywhere or press any key to jump to the end state.
"""

import math

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QWidget

from ui.animated_logo import (
    build_circular_pixmap, paint_animated_logo,
)


# Background color of the overlay (matches the MainWindow bg in style.py)
COLOR_BG = QColor(26, 26, 46)            # #1a1a2e
COLOR_TAGLINE = QColor(138, 138, 160)    # #8a8aa0

# ----------------------------------------------------------------------
# Animation timeline (milliseconds since splash start)
# ----------------------------------------------------------------------
T_LOGO_FADE_END = 400      # logo done fading + scaling up
T_TAGLINE_IN_START = 250   # tagline starts fading in
T_TAGLINE_IN_END = 600     # tagline fully visible
T_HOLD_END = 1400          # end of hold phase, fly-out starts
T_TOTAL = 2100             # everything done, splash hides


def _ease_out_cubic(t):
    """t in [0,1] -> eased in [0,1] with smooth deceleration."""
    return 1.0 - (1.0 - t) ** 3


def _lerp(a, b, t):
    return a + (b - a) * t


class SplashOverlay(QWidget):
    """Opaque child widget covering the MainWindow during startup."""

    INITIAL_DIAMETER = 300       # big-logo diameter at full size
    INITIAL_SCALE = 0.8          # starting scale of the fade-in (80 %)

    def __init__(self, parent, target_widget):
        """
        Args:
            parent: usually the MainWindow. The splash sizes itself to the
                parent's rect.
            target_widget: the AnimatedLogo whose position the splash should
                fly to. Its ``_angle`` and ``_pulse_phase`` are synced to the
                splash's values on completion for a seamless visual handoff.
        """
        super().__init__(parent)
        self._target = target_widget

        # Cover the full parent area
        self.setGeometry(parent.rect())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Pre-render the circular logo at the largest size we'll ever need;
        # downscaling via drawPixmap is fast and looks crisp.
        self._pixmap = build_circular_pixmap(self.INITIAL_DIAMETER)

        # Continuous spinner state (drives glow + scanner regardless of phase)
        self._angle = 0.0
        self._pulse_phase = 0.0

        # Master clock - elapsed milliseconds since start()
        self._elapsed = 0
        self._finished = False

        # Render state, recomputed each tick from _elapsed
        self._cx = 0.0
        self._cy = 0.0
        self._radius = self.INITIAL_DIAMETER / 2 * self.INITIAL_SCALE
        self._logo_alpha = 0.0
        self._tagline_alpha = 0.0

        # Target center in our local coords (computed in start())
        self._target_center = None

        # Single ~30 fps timer drives everything
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self):
        """Show the overlay and start the animation. Call after the parent
        window is fully laid out."""
        # Compute the target center in our coordinate system.
        target_global = self._target.mapToGlobal(self._target.rect().center())
        self._target_center = self.mapFromGlobal(target_global)

        # Initial position: dead center of our rect
        self._cx = self.width() / 2
        self._cy = self.height() / 2

        self.show()
        self.raise_()
        self.setFocus()
        self._timer.start()

    # Resize with the parent if the window is resized mid-splash
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._target_center is not None:
            target_global = self._target.mapToGlobal(self._target.rect().center())
            self._target_center = self.mapFromGlobal(target_global)

    # ------------------------------------------------------------------
    # Skip
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        self._skip()

    def keyPressEvent(self, event):
        self._skip()

    def _skip(self):
        if not self._finished:
            self._elapsed = T_TOTAL
            self._finish()

    # ------------------------------------------------------------------
    # Animation tick
    # ------------------------------------------------------------------
    def _tick(self):
        if self._finished:
            return

        self._elapsed += self._timer.interval()

        # Continuous scanner / pulse - same speed as AnimatedLogo
        self._angle = (self._angle + 1.5) % 360.0
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)

        self._compute_state(min(self._elapsed, T_TOTAL))
        self.update()

        if self._elapsed >= T_TOTAL:
            self._finish()

    def _compute_state(self, t):
        """Update render state from master time t (in ms, 0..T_TOTAL)."""
        # ---- Logo opacity + radius ----
        if t < T_LOGO_FADE_END:
            p = _ease_out_cubic(t / T_LOGO_FADE_END)
            self._logo_alpha = p
            scale = _lerp(self.INITIAL_SCALE, 1.0, p)
            self._radius = self.INITIAL_DIAMETER / 2 * scale
        elif t < T_HOLD_END:
            self._logo_alpha = 1.0
            self._radius = self.INITIAL_DIAMETER / 2
        else:
            # Fly-out: shrink toward target radius
            p = _ease_out_cubic((t - T_HOLD_END) / (T_TOTAL - T_HOLD_END))
            self._logo_alpha = 1.0
            r0 = self.INITIAL_DIAMETER / 2
            r1 = self._target.LOGO_DIAMETER / 2
            self._radius = _lerp(r0, r1, p)

        # ---- Logo position (only changes during fly-out) ----
        if t < T_HOLD_END:
            self._cx = self.width() / 2
            self._cy = self.height() / 2
        else:
            p = _ease_out_cubic((t - T_HOLD_END) / (T_TOTAL - T_HOLD_END))
            x0, y0 = self.width() / 2, self.height() / 2
            x1 = self._target_center.x()
            y1 = self._target_center.y()
            self._cx = _lerp(x0, x1, p)
            self._cy = _lerp(y0, y1, p)

        # ---- Tagline opacity ----
        if t < T_TAGLINE_IN_START:
            self._tagline_alpha = 0.0
        elif t < T_TAGLINE_IN_END:
            p = (t - T_TAGLINE_IN_START) / (T_TAGLINE_IN_END - T_TAGLINE_IN_START)
            self._tagline_alpha = _ease_out_cubic(p)
        elif t < T_HOLD_END:
            self._tagline_alpha = 1.0
        else:
            # Fade out quickly so the tagline is gone before the logo has
            # moved far - otherwise the text looks "left behind".
            fade_dur = (T_TOTAL - T_HOLD_END) * 0.3
            p = min(1.0, (t - T_HOLD_END) / fade_dur)
            self._tagline_alpha = 1.0 - p

    # ------------------------------------------------------------------
    # Handoff
    # ------------------------------------------------------------------
    def _finish(self):
        if self._finished:
            return
        self._finished = True
        self._timer.stop()

        # Sync the steady-state logo's phase to ours so its scanner picks up
        # exactly where ours left off - no visible jump on handoff.
        if hasattr(self._target, "_angle"):
            self._target._angle = self._angle
            self._target._pulse_phase = self._pulse_phase
        # Reveal the target (MainWindow keeps it hidden during the splash so
        # it doesn't render twice). Showing it restarts its idle animation.
        self._target.show()
        self._target.update()

        self.hide()
        self.deleteLater()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

            # 1) Solid background fill (matches the app theme)
            p.fillRect(self.rect(), COLOR_BG)

            # 2) Tagline (only when visible) - follows the logo horizontally
            if self._tagline_alpha > 0.01:
                p.save()
                p.setOpacity(self._tagline_alpha)
                font = QFont("Segoe UI", 11, QFont.Weight.Bold)
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
                p.setFont(font)
                p.setPen(COLOR_TAGLINE)
                tagline_y = self._cy + self._radius + 32
                # Centered around the logo's current x so it tracks the
                # fly-out instead of being left in the middle of the screen.
                text_w = 400
                rect = QRectF(self._cx - text_w / 2, tagline_y, text_w, 28)
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "SECURITY TOOL SUITE")
                p.restore()

            # 3) The animated logo
            p.save()
            p.setOpacity(self._logo_alpha)
            paint_animated_logo(
                p, self._cx, self._cy, self._radius,
                self._angle, self._pulse_phase, self._pixmap,
            )
            p.restore()
        finally:
            p.end()
