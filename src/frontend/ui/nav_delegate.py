"""
Gilfi - Navigation list item delegate

Paints the standard QListWidget item, plus a pulsing dot on the right
edge of any item that's currently marked as busy (i.e. its tool page has
an ``run_async`` job in flight).

Usage
-----
The delegate is owned by the nav list. The MainWindow maintains a set of
"busy" row indices and calls ``set_busy(row, busy)`` on the delegate; the
delegate handles all the animation timing internally. When nothing is
busy, the timer stops, so we don't burn CPU in idle.
"""

import math

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle

from ui import theme as theme_module


# ---------------------------------------------------------------------------
# Tuning
# ---------------------------------------------------------------------------

DOT_DIAMETER = 8           # pixel diameter at the brightest peak
DOT_RIGHT_MARGIN = 14      # distance from the right edge of the item
PULSE_PERIOD_MS = 1100     # one full pulse cycle (dim -> bright -> dim)
TICK_INTERVAL_MS = 50      # how often we repaint the affected items


class NavItemDelegate(QStyledItemDelegate):
    """QListWidget delegate that draws a pulsing busy indicator."""

    def __init__(self, parent_list):
        super().__init__(parent_list)
        self._list = parent_list
        self._busy_rows = set()
        self._phase = 0.0  # 0..1 within the current pulse cycle

        # Single shared timer for all busy items.
        self._timer = QTimer(self)
        self._timer.setInterval(TICK_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # Public API used by MainWindow
    # ------------------------------------------------------------------
    def set_busy(self, row: int, busy: bool):
        """Mark / unmark a row as busy."""
        if busy:
            self._busy_rows.add(row)
        else:
            self._busy_rows.discard(row)

        if self._busy_rows and not self._timer.isActive():
            self._timer.start()
        elif not self._busy_rows and self._timer.isActive():
            self._timer.stop()
            self._phase = 0.0

        # Repaint just the affected row so the indicator appears /
        # disappears immediately.
        self._repaint_row(row)

    def is_busy(self, row: int) -> bool:
        return row in self._busy_rows

    # ------------------------------------------------------------------
    # Animation tick
    # ------------------------------------------------------------------
    def _tick(self):
        # Advance phase. We don't bother with wall-clock time here; the
        # timer is reliable enough at 20 Hz, and a tiny drift is invisible.
        self._phase = (self._phase + TICK_INTERVAL_MS / PULSE_PERIOD_MS) % 1.0
        # Repaint only the busy rows.
        for row in list(self._busy_rows):
            self._repaint_row(row)

    def _repaint_row(self, row: int):
        item = self._list.item(row)
        if item is None:
            return
        rect = self._list.visualItemRect(item)
        if rect.isValid():
            self._list.viewport().update(rect)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paint(self, painter, option, index):
        # Draw the standard item (text, hover, selection, etc.).
        super().paint(painter, option, index)

        row = index.row()
        if row not in self._busy_rows:
            return

        # Pulse: smooth sine wave, alpha in [0.35, 1.0]
        alpha_f = 0.35 + 0.65 * 0.5 * (1.0 + math.sin(self._phase * 2 * math.pi))

        palette = theme_module.current_theme()
        # Use a colour that pops on both selected and unselected backgrounds.
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        color_key = "selection_text" if is_selected else "accent"
        color_hex = palette.get(color_key, palette["accent"])

        color = QColor(color_hex)
        color.setAlphaF(alpha_f)

        # Position: vertically centred, just inside the right edge.
        rect = option.rect
        cx = rect.right() - DOT_RIGHT_MARGIN
        cy = rect.center().y()

        # Outer faint halo for a softer glow effect.
        halo = QColor(color_hex)
        halo.setAlphaF(alpha_f * 0.35)

        painter.save()
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(Qt.PenStyle.NoPen)

            halo_r = DOT_DIAMETER * 0.9
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(
                QRectF(cx - halo_r, cy - halo_r, halo_r * 2, halo_r * 2)
            )

            inner_r = DOT_DIAMETER / 2
            painter.setBrush(QBrush(color))
            painter.drawEllipse(
                QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
            )
        finally:
            painter.restore()
