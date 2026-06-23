"""
Gilfi - Splash Overlay

Startup splash that appears on top of the MainWindow:
  - dark overlay covers the GUI
  - logo fades in big, centered, with pulsing glow + rotating scanner
  - "Security Tool Suite" tagline fades in below
  - backend version-check status fades in under the tagline
    ("Connecting ..." -> "Connected (backend v1.0.0)" / "Offline mode")
  - after a hold phase, logo simultaneously shrinks and flies to the
    AnimatedLogo's position in the nav sidebar
  - splash hides instantly at the handoff moment; the static
    AnimatedLogo (with its phase synced) takes over seamlessly

Timing model:
    The hold phase is *dynamic*. It always lasts at least ``MIN_HOLD_MS``
    so the splash never feels rushed. If the backend responds within that
    window, we still hold for a short dwell so the user can read the
    result. If the backend doesn't respond by ``MAX_HOLD_MS``, the splash
    proceeds with "Offline mode" and starts the fly-out anyway.

Skip: click anywhere or press any key to jump to the end state.
"""

import math

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QWidget

from ui.animated_logo import (
    build_circular_pixmap, paint_animated_logo,
)
from ui import theme as theme_module


# ----------------------------------------------------------------------
# Fade timings (milliseconds since splash start) - these are fixed.
# Hold-end and total are derived dynamically (see __init__).
# ----------------------------------------------------------------------
T_LOGO_FADE_END = 500       # logo done fading in / scaling up
T_TAGLINE_IN_START = 300    # tagline starts fading in
T_TAGLINE_IN_END = 800      # tagline fully visible
T_VERSION_IN_START = 850    # version status line starts fading in
T_VERSION_IN_END = 1300     # version status line fully visible
FLYOUT_MS = 800             # duration of the fly-out


def _ease_out_cubic(t):
    return 1.0 - (1.0 - t) ** 3


def _lerp(a, b, t):
    return a + (b - a) * t


class SplashOverlay(QWidget):
    """Opaque child widget covering the MainWindow during startup."""

    INITIAL_DIAMETER = 300       # big-logo diameter at full size
    INITIAL_SCALE = 0.8          # starting scale of the fade-in (80 %)

    # Hold-phase bounds. The actual hold-end falls somewhere in this range,
    # determined by when the version check completes (or times out).
    MIN_HOLD_MS = 2500
    MAX_HOLD_MS = 4500
    # After the version result arrives, hold at least this long so the user
    # can read it before the fly-out starts.
    DWELL_AFTER_CHECK_MS = 800

    def __init__(self, parent, target_widget):
        super().__init__(parent)
        self._target = target_widget

        # Cover the full parent area
        self.setGeometry(parent.rect())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

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
        self._version_alpha = 0.0

        # Target center in our local coords (computed in start())
        self._target_center = None

        # --- Dynamic timeline ---
        self._t_hold_end = self.MIN_HOLD_MS
        self._t_total = self._t_hold_end + FLYOUT_MS

        # --- Version-check state ---
        self._version_received = False
        self._version_text = "Connecting to backend ..."
        # Resolved against the active theme palette at paint time.
        self._version_color_key = "text_dim"

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
        target_global = self._target.mapToGlobal(self._target.rect().center())
        self._target_center = self.mapFromGlobal(target_global)

        # Initial position: dead center of our rect
        self._cx = self.width() / 2
        self._cy = self.height() / 2

        self.show()
        self.raise_()
        self.setFocus()
        self._timer.start()

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
            self._elapsed = self._t_total
            self._finish()

    # ------------------------------------------------------------------
    # Version-check hook (called by MainWindow when the first heartbeat
    # comes back)
    # ------------------------------------------------------------------
    def on_version_info(self, healthy: bool, info: dict):
        """Update the version status line.

        We accept this only once. Further heartbeats during the splash
        lifetime are ignored - the splash is a snapshot, not a live view.
        """
        if self._finished or self._version_received:
            return
        self._version_received = True

        if healthy:
            version = (info or {}).get("version", "").strip()
            self._version_text = (
                f"Connected (backend v{version})" if version else "Connected"
            )
            self._version_color_key = "success"
        else:
            self._version_text = "Offline mode — backend unreachable"
            self._version_color_key = "error"

        # Extend the hold so the user has time to read the result, but
        # cap it at MAX_HOLD_MS.
        target_hold = max(
            self.MIN_HOLD_MS,
            self._elapsed + self.DWELL_AFTER_CHECK_MS,
        )
        self._t_hold_end = min(target_hold, self.MAX_HOLD_MS)
        self._t_total = self._t_hold_end + FLYOUT_MS

    # ------------------------------------------------------------------
    # Animation tick
    # ------------------------------------------------------------------
    def _tick(self):
        if self._finished:
            return

        self._elapsed += self._timer.interval()

        # Timeout the version check if it never came back.
        if (not self._version_received
                and self._elapsed >= self.MAX_HOLD_MS - FLYOUT_MS):
            # Treat as offline so the splash can move on.
            self.on_version_info(False, {})

        # Continuous scanner / pulse - same speed as AnimatedLogo
        self._angle = (self._angle + 1.5) % 360.0
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)

        self._compute_state(min(self._elapsed, self._t_total))
        self.update()

        if self._elapsed >= self._t_total:
            self._finish()

    def _compute_state(self, t):
        """Update render state from master time t (ms, 0.._t_total)."""
        hold_end = self._t_hold_end
        total = self._t_total

        # ---- Logo opacity + radius ----
        if t < T_LOGO_FADE_END:
            p = _ease_out_cubic(t / T_LOGO_FADE_END)
            self._logo_alpha = p
            scale = _lerp(self.INITIAL_SCALE, 1.0, p)
            self._radius = self.INITIAL_DIAMETER / 2 * scale
        elif t < hold_end:
            self._logo_alpha = 1.0
            self._radius = self.INITIAL_DIAMETER / 2
        else:
            p = _ease_out_cubic((t - hold_end) / max(1, total - hold_end))
            self._logo_alpha = 1.0
            r0 = self.INITIAL_DIAMETER / 2
            r1 = self._target.LOGO_DIAMETER / 2
            self._radius = _lerp(r0, r1, p)

        # ---- Logo position (only changes during fly-out) ----
        if t < hold_end:
            self._cx = self.width() / 2
            self._cy = self.height() / 2
        else:
            p = _ease_out_cubic((t - hold_end) / max(1, total - hold_end))
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
        elif t < hold_end:
            self._tagline_alpha = 1.0
        else:
            fade_dur = (total - hold_end) * 0.3
            p = min(1.0, (t - hold_end) / max(1, fade_dur))
            self._tagline_alpha = 1.0 - p

        # ---- Version-status opacity ----
        if t < T_VERSION_IN_START:
            self._version_alpha = 0.0
        elif t < T_VERSION_IN_END:
            p = (t - T_VERSION_IN_START) / (T_VERSION_IN_END - T_VERSION_IN_START)
            self._version_alpha = _ease_out_cubic(p)
        elif t < hold_end:
            self._version_alpha = 1.0
        else:
            fade_dur = (total - hold_end) * 0.3
            p = min(1.0, (t - hold_end) / max(1, fade_dur))
            self._version_alpha = 1.0 - p

    # ------------------------------------------------------------------
    # Handoff
    # ------------------------------------------------------------------
    def _finish(self):
        if self._finished:
            return
        self._finished = True
        self._timer.stop()

        if hasattr(self._target, "_angle"):
            self._target._angle = self._angle
            self._target._pulse_phase = self._pulse_phase
        self._target.show()
        self._target.update()

        self.hide()
        self.deleteLater()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        palette = theme_module.current_theme()
        bg_color = QColor(palette["bg"])
        tagline_color = QColor(palette["text_dim"])
        version_color = QColor(
            palette.get(self._version_color_key, palette["text_dim"])
        )

        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

            # 1) Solid background fill
            p.fillRect(self.rect(), bg_color)

            # 2) Tagline
            if self._tagline_alpha > 0.01:
                p.save()
                p.setOpacity(self._tagline_alpha)
                font = QFont()
                font.setStyleHint(QFont.StyleHint.SansSerif)
                font.setPointSize(11)
                font.setWeight(QFont.Weight.Bold)
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
                p.setFont(font)
                p.setPen(tagline_color)
                tagline_y = self._cy + self._radius + 32
                text_w = 400
                rect = QRectF(self._cx - text_w / 2, tagline_y, text_w, 28)
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "SECURITY TOOL SUITE")
                p.restore()

            # 3) Version-check status line
            if self._version_alpha > 0.01:
                p.save()
                p.setOpacity(self._version_alpha)
                font = QFont()
                font.setStyleHint(QFont.StyleHint.SansSerif)
                font.setPointSize(9)
                p.setFont(font)
                p.setPen(version_color)
                version_y = self._cy + self._radius + 60
                text_w = 500
                rect = QRectF(self._cx - text_w / 2, version_y, text_w, 22)
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._version_text)
                p.restore()

            # 4) The animated logo
            p.save()
            p.setOpacity(self._logo_alpha)
            paint_animated_logo(
                p, self._cx, self._cy, self._radius,
                self._angle, self._pulse_phase, self._pixmap,
            )
            p.restore()
        finally:
            p.end()
