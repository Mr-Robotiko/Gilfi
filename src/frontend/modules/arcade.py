"""
Gilfi Module - Arcade
Collection of mini-games that showcase the Gilfi modules in a playful way.

Games:
    - Crack the Code:        Caesar cipher puzzle (pure crypto fun)
    - Hash Hunter:           Find the word that produces the hash (Hash Module)
    - Survive the Cracker:   Build a password that survives our cracker (Hash Crack Module)
    - Factorize!:            Find p and q from N (RSA teaser)
"""

import hashlib
import random
import time

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QLineEdit, QTextEdit, QGridLayout, QSlider,
    QGroupBox
)

import api_client


# =============================================================================
# Cross-module helpers (let games forward data to other Gilfi tool pages)
# =============================================================================

SECONDARY_BTN_STYLE = """
QPushButton {
    background: #1a1a40;
    color: #53a8d8;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 11px;
}
QPushButton:hover {
    background: #0f3460;
    color: #ffffff;
}
QPushButton:pressed {
    background: #1a5276;
}
QPushButton:disabled {
    background: #0f0f23;
    color: #555570;
    border-color: #1a1a40;
}
"""


def _send_to_module(widget, module_name, field_values, auto_run=False):
    """
    Walk up to the MainWindow, switch to the target tool page, prefill its
    fields and optionally trigger its run. Returns True on success.
    """
    mw = widget.window()
    if not (hasattr(mw, 'nav_list') and hasattr(mw, 'stack')):
        return False

    # find the nav entry by exact label match
    target_idx = None
    for i in range(mw.nav_list.count()):
        if mw.nav_list.item(i).text() == module_name:
            target_idx = i
            break
    if target_idx is None:
        return False

    # prefill fields on the target page (it's a ToolPage with a `fields` dict)
    page = mw.stack.widget(target_idx)
    if hasattr(page, 'fields'):
        for label, val in field_values.items():
            if label in page.fields:
                page.fields[label].setText(str(val))

    # switch to the tab
    mw.nav_list.setCurrentRow(target_idx)

    # optionally trigger the run
    if auto_run and hasattr(page, 'handle_run'):
        page.handle_run()

    return True


def _show_status(widget, msg, timeout=2000):
    """Show a short message in the MainWindow status bar."""
    mw = widget.window()
    if hasattr(mw, 'statusBar'):
        mw.statusBar().showMessage(msg, timeout)


def _copy_to_clipboard(text):
    """Copy text to the system clipboard."""
    QGuiApplication.clipboard().setText(text)


# =============================================================================
# Helpers
# =============================================================================

def caesar_shift(text, shift):
    """Shift letters in the alphabet. Non-letter characters are left unchanged."""
    out = []
    for c in text:
        if c.isupper():
            out.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
        elif c.islower():
            out.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
        else:
            out.append(c)
    return ''.join(out)


def is_prime(n):
    """Simple prime check (fast enough for the number sizes used in Factorize)."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


# =============================================================================
# Game 1: Crack the Code (Caesar Cipher Puzzle)
# =============================================================================

PUZZLE_SENTENCES = [
    "THE SECRETS OF THE CRYPTOGRAPHER ARE WELL GUARDED",
    "JULIUS CAESAR INVENTED THIS KIND OF ENCRYPTION",
    "GILFI IS THE BEST SECURITY SUITE ON CAMPUS",
    "IF YOU CAN READ THIS YOU CRACKED THE CAESAR",
    "NEVER USE PASSWORDS SHORTER THAN EIGHT CHARACTERS",
    "ASYMMETRIC ENCRYPTION IS A BRILLIANT IDEA",
    "THE STUDY OF SECRET COMMUNICATION IS CALLED CRYPTOLOGY",
    "IN COMPUTER SCIENCE NOTHING IS AS CERTAIN AS RANDOMNESS",
    "ALAN TURING WAS A BRITISH MATHEMATICIAN AND CODE BREAKER",
    "PUBLIC KEY AND PRIVATE KEY BELONG TOGETHER",
    "MY PASSWORD IS LONGER THAN EIGHTEEN CHARACTERS",
    "ENCRYPTION PROTECTS INDIVIDUAL PRIVACY",
]

SLIDER_STYLE = """
QSlider::groove:horizontal {
    height: 6px;
    background: #0f0f23;
    border-radius: 3px;
    border: 1px solid #0f3460;
}
QSlider::handle:horizontal {
    background: #53a8d8;
    width: 18px;
    margin: -7px 0;
    border-radius: 9px;
}
QSlider::sub-page:horizontal {
    background: #0f3460;
    border-radius: 3px;
}
"""


class CrackTheCodeGame(QWidget):
    """Caesar cipher puzzle. Move the slider to decrypt the text live."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0
        self.current_shift = 0
        self.original = ""
        self.encrypted = ""
        self.start_time = 0.0
        self._setup_ui()
        self._new_puzzle()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # header
        header = QLabel("Crack the Code")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #53a8d8;")
        layout.addWidget(header)

        info = QLabel(
            "The text was shifted with a Caesar cipher. Move the slider until "
            "the plaintext makes sense. Uses: plain crypto math (no backend)."
        )
        info.setStyleSheet("color: #8a8aa0; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # encrypted display
        enc_group = QGroupBox("Encrypted")
        enc_l = QVBoxLayout(enc_group)
        self.encrypted_label = QLabel("")
        self.encrypted_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.encrypted_label.setStyleSheet(
            "color: #f06b78; padding: 12px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460;"
        )
        self.encrypted_label.setWordWrap(True)
        self.encrypted_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encrypted_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        enc_l.addWidget(self.encrypted_label)
        layout.addWidget(enc_group)

        # shift slider
        slider_group = QGroupBox("Shift")
        slider_l = QVBoxLayout(slider_group)
        slider_row = QHBoxLayout()

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(25)
        self.slider.setStyleSheet(SLIDER_STYLE)
        self.slider.valueChanged.connect(self._on_shift_changed)
        slider_row.addWidget(self.slider, stretch=1)

        self.shift_label = QLabel("0")
        self.shift_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.shift_label.setStyleSheet("color: #53a8d8; min-width: 34px;")
        self.shift_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_row.addWidget(self.shift_label)
        slider_l.addLayout(slider_row)
        layout.addWidget(slider_group)

        # decrypted preview
        dec_group = QGroupBox("Your Attempt")
        dec_l = QVBoxLayout(dec_group)
        self.decrypted_label = QLabel("")
        self.decrypted_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.decrypted_label.setStyleSheet(
            "color: #4ade80; padding: 12px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460;"
        )
        self.decrypted_label.setWordWrap(True)
        self.decrypted_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decrypted_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        dec_l.addWidget(self.decrypted_label)
        layout.addWidget(dec_group)

        # controls row
        btn_row = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8a8aa0; font-size: 12px;")
        btn_row.addWidget(self.status_label)
        btn_row.addStretch()

        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet("color: #53a8d8; font-weight: bold;")
        btn_row.addWidget(self.score_label)
        btn_row.addSpacing(16)

        self.submit_btn = QPushButton("Solved!")
        self.submit_btn.setObjectName("btnRun")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._check_answer)
        btn_row.addWidget(self.submit_btn)

        self.new_btn = QPushButton("New")
        self.new_btn.setObjectName("btnRun")
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.clicked.connect(self._new_puzzle)
        btn_row.addWidget(self.new_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

    def _new_puzzle(self):
        self.original = random.choice(PUZZLE_SENTENCES)
        self.current_shift = random.randint(1, 25)
        self.encrypted = caesar_shift(self.original, self.current_shift)
        self.encrypted_label.setText(self.encrypted)
        self.slider.setValue(0)
        self._on_shift_changed(0)
        self.start_time = time.time()
        self.status_label.setText("New puzzle!")
        self.status_label.setStyleSheet("color: #8a8aa0; font-size: 12px;")

    def _on_shift_changed(self, value):
        self.shift_label.setText(str(value))
        # decrypt = shift back
        attempt = caesar_shift(self.encrypted, -value)
        self.decrypted_label.setText(attempt)

    def _check_answer(self):
        if self.slider.value() == self.current_shift:
            elapsed = time.time() - self.start_time
            points = max(10, int(100 - elapsed * 2))
            self.score += points
            self.score_label.setText(f"Score: {self.score}")
            self.status_label.setText(f"Correct! +{points} points  ({elapsed:.1f}s)")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")
            QTimer.singleShot(1800, self._new_puzzle)
        else:
            self.status_label.setText(
                f"Nope, correct shift was {self.current_shift}. Try another round!"
            )
            self.status_label.setStyleSheet("color: #f06b78; font-size: 12px;")


# =============================================================================
# Game 2: Hash Hunter
# =============================================================================

HASH_WORDS_EASY = [
    "password", "admin", "hello", "qwerty", "login", "master",
    "dragon", "secret", "welcome", "monkey", "letmein", "shadow",
    "batman", "ninja", "football", "iloveyou", "trustno1", "password1",
    "abc123", "sunshine",
]

HASH_WORDS_MEDIUM = [
    "princess", "superman", "asdf1234", "passw0rd", "starwars", "freedom",
    "whatever", "computer", "butterfly", "dragon123", "thunder", "mercedes",
    "charlie", "daniel", "peanut", "robert", "matrix", "harley",
    "bailey", "access",
]

HASH_WORDS_HARD = [
    "correcthorse", "batterystaple", "gilfi2024", "p@ssw0rd!", "Tr0ub4dor&3",
    "kryptonite", "openSesame", "Zaq1@Wsx", "Hunter2!", "Passphrase",
    "xkcd936", "Jurassic!Park", "abcdef123456", "Qwerty!2024", "moonlight99",
    "coffeeLover42", "BlueSky!77", "IceCream#01", "CodeBreaker9", "NightOwl2023",
]


class HashHunterGame(QWidget):
    """The hash is shown, the user has to pick the matching word from 9 options."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0
        self.lives = 3
        self.current_word = ""
        self.current_algo = "md5"
        self._setup_ui()
        self._new_round()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QLabel("Hash Hunter")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #53a8d8;")
        layout.addWidget(header)

        info = QLabel(
            "Which word produces the hash shown? Click the correct one. "
            "Difficulty goes up with your score. Uses: local hashing (same algos as Hash Module)."
        )
        info.setStyleSheet("color: #8a8aa0; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # target hash
        hash_group = QGroupBox("Target Hash")
        hash_l = QVBoxLayout(hash_group)

        self.algo_label = QLabel("")
        self.algo_label.setStyleSheet("color: #8a8aa0; font-size: 11px;")
        self.algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hash_l.addWidget(self.algo_label)

        self.hash_label = QLabel("")
        self.hash_label.setFont(QFont("Consolas", 11))
        self.hash_label.setStyleSheet(
            "color: #4ade80; padding: 10px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460;"
        )
        self.hash_label.setWordWrap(True)
        self.hash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hash_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hash_l.addWidget(self.hash_label)
        layout.addWidget(hash_group)

        # action row: copy hash / send to hash module / send to crack module
        action_row = QHBoxLayout()
        action_row.addStretch()

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_hash)
        action_row.addWidget(self.copy_btn)

        self.to_hash_btn = QPushButton("Send to Hash Module")
        self.to_hash_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        self.to_hash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.to_hash_btn.clicked.connect(self._send_to_hash_module)
        action_row.addWidget(self.to_hash_btn)

        self.to_crack_btn = QPushButton("Send to Crack Module")
        self.to_crack_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        self.to_crack_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.to_crack_btn.clicked.connect(self._send_to_crack_module)
        action_row.addWidget(self.to_crack_btn)

        layout.addLayout(action_row)

        # 3x3 candidate grid
        grid_group = QGroupBox("Candidates")
        grid = QGridLayout(grid_group)
        grid.setSpacing(8)
        self.word_buttons = []
        for i in range(9):
            btn = QPushButton("")
            btn.setObjectName("btnRun")
            btn.setMinimumHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self._on_word_clicked(idx))
            grid.addWidget(btn, i // 3, i % 3)
            self.word_buttons.append(btn)
        layout.addWidget(grid_group)

        # status row
        status_row = QHBoxLayout()
        self.lives_label = QLabel("Lives: 3")
        self.lives_label.setStyleSheet("color: #f06b78; font-weight: bold; font-size: 13px;")
        status_row.addWidget(self.lives_label)
        status_row.addStretch()

        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("color: #8a8aa0;")
        status_row.addWidget(self.feedback_label)
        status_row.addStretch()

        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet("color: #53a8d8; font-weight: bold;")
        status_row.addWidget(self.score_label)
        layout.addLayout(status_row)

        layout.addStretch()

    def _hash(self, text, algo):
        h = hashlib.new(algo)
        h.update(text.encode())
        return h.hexdigest()

    def _new_round(self):
        # difficulty depends on score
        if self.score < 150:
            pool = HASH_WORDS_EASY
            self.current_algo = "md5"
        elif self.score < 400:
            pool = HASH_WORDS_EASY + HASH_WORDS_MEDIUM
            self.current_algo = "sha1"
        else:
            pool = HASH_WORDS_MEDIUM + HASH_WORDS_HARD
            self.current_algo = "sha256"

        self.current_word = random.choice(pool)
        others = random.sample([w for w in pool if w != self.current_word], 8)
        candidates = others + [self.current_word]
        random.shuffle(candidates)

        self.algo_label.setText(f"Algorithm: {self.current_algo.upper()}")
        self.hash_label.setText(self._hash(self.current_word, self.current_algo))

        for btn, word in zip(self.word_buttons, candidates):
            btn.setText(word)
            btn.setProperty("word", word)
            btn.setEnabled(True)
            btn.setStyleSheet("")

    def _on_word_clicked(self, idx):
        btn = self.word_buttons[idx]
        word = btn.property("word")
        for b in self.word_buttons:
            b.setEnabled(False)

        if word == self.current_word:
            self.score += 50
            self.score_label.setText(f"Score: {self.score}")
            btn.setStyleSheet("background: #4ade80; color: #0f0f23; font-weight: bold;")
            self.feedback_label.setText("Correct!")
            self.feedback_label.setStyleSheet("color: #4ade80; font-weight: bold;")
        else:
            self.lives -= 1
            self.lives_label.setText(f"Lives: {self.lives}")
            btn.setStyleSheet("background: #f06b78; color: #ffffff; font-weight: bold;")
            # highlight the correct answer
            for b in self.word_buttons:
                if b.property("word") == self.current_word:
                    b.setStyleSheet("background: #4ade80; color: #0f0f23; font-weight: bold;")
            self.feedback_label.setText(f"Was: {self.current_word}")
            self.feedback_label.setStyleSheet("color: #f06b78; font-weight: bold;")

        if self.lives <= 0:
            QTimer.singleShot(1800, self._game_over)
        else:
            QTimer.singleShot(1500, self._new_round)

    def _copy_hash(self):
        _copy_to_clipboard(self.hash_label.text())
        _show_status(self, "Hash copied to clipboard", 2000)

    def _send_to_hash_module(self):
        ok = _send_to_module(self, "Hash Module", {
            "Input": self.hash_label.text(),
            "Algorithm": self.current_algo,
            "Mode": "identify",
        }, auto_run=True)
        if not ok:
            _show_status(self, "Could not find Hash Module", 2000)

    def _send_to_crack_module(self):
        # don't auto-run - cracking takes a while, let the user press Start
        ok = _send_to_module(self, "Hash Crack Module", {
            "Hash": self.hash_label.text(),
            "Algorithm": self.current_algo,
        }, auto_run=False)
        if not ok:
            _show_status(self, "Could not find Hash Crack Module", 2000)

    def _game_over(self):
        self.hash_label.setText(f"GAME OVER  -  Final Score: {self.score}")
        self.hash_label.setStyleSheet(
            "color: #f06b78; padding: 10px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460; font-weight: bold;"
        )
        self.algo_label.setText("Click any tile to restart")
        self.feedback_label.setText("")
        # no hash to copy/send once the game is over
        self.copy_btn.setEnabled(False)
        self.to_hash_btn.setEnabled(False)
        self.to_crack_btn.setEnabled(False)
        for btn in self.word_buttons:
            btn.setText("Restart")
            btn.setEnabled(True)
            btn.setStyleSheet("background: #0f3460; color: #53a8d8;")
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(self._restart)

    def _restart(self):
        self.score = 0
        self.lives = 3
        self.score_label.setText("Score: 0")
        self.lives_label.setText("Lives: 3")
        self.copy_btn.setEnabled(True)
        self.to_hash_btn.setEnabled(True)
        self.to_crack_btn.setEnabled(True)
        self.hash_label.setStyleSheet(
            "color: #4ade80; padding: 10px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460;"
        )
        for i, btn in enumerate(self.word_buttons):
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(lambda checked, idx=i: self._on_word_clicked(idx))
        self._new_round()


# =============================================================================
# Game 3: Survive the Cracker
# =============================================================================

class CrackerWorker(QThread):
    """Runs the hash-crack API call in a background thread so the GUI stays responsive."""
    done = pyqtSignal(object)   # plaintext (str) if cracked, else None
    error = pyqtSignal(str)

    def __init__(self, password, algo="sha256"):
        super().__init__()
        self.password = password
        self.algo = algo

    def run(self):
        try:
            # hash locally, let the backend do the cracking
            h = hashlib.new(self.algo)
            h.update(self.password.encode())
            hash_val = h.hexdigest()

            result = api_client.hash_crack(hash_val, algorithm=self.algo)
            self.done.emit(result)  # None or plaintext str
        except ConnectionError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))


class SurviveTheCrackerGame(QWidget):
    """User enters a password, the real cracker (rockyou.txt) tries to crack it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.start_time = 0.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QLabel("Survive the Cracker")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #53a8d8;")
        layout.addWidget(header)

        info = QLabel(
            "Come up with a password and see if it survives our hash cracker "
            "(rockyou.txt attack). Uses: Hash Crack Module (backend)."
        )
        info.setStyleSheet("color: #8a8aa0; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # input field
        input_group = QGroupBox("Your Password")
        il = QVBoxLayout(input_group)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter the password you want to defend ...")
        self.password_input.returnPressed.connect(self._start_defense)
        il.addWidget(self.password_input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.start_btn = QPushButton("Start Defense")
        self.start_btn.setObjectName("btnRun")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_defense)
        btn_row.addWidget(self.start_btn)
        il.addLayout(btn_row)
        layout.addWidget(input_group)

        # timer + log
        result_group = QGroupBox("Attack Log")
        rl = QVBoxLayout(result_group)

        self.timer_label = QLabel("0.0s")
        self.timer_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: #53a8d8; padding: 8px;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self.timer_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Attack log will appear here ...")
        self.log.setMinimumHeight(140)
        rl.addWidget(self.log)

        layout.addWidget(result_group, stretch=1)

    def _start_defense(self):
        password = self.password_input.text().strip()
        if not password:
            return
        if self.worker and self.worker.isRunning():
            return

        self.log.clear()
        self.log.append("[0.0s] Hashing password with SHA-256 ...")
        self.log.append("[0.0s] Launching dictionary attack (rockyou.txt) ...")
        self.log.append("")

        self.start_time = time.time()
        self.timer_label.setText("0.0s")
        self.timer_label.setStyleSheet("color: #53a8d8; padding: 8px;")
        self.timer.start(100)
        self.start_btn.setEnabled(False)

        self.worker = CrackerWorker(password, algo="sha256")
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _tick(self):
        elapsed = time.time() - self.start_time
        self.timer_label.setText(f"{elapsed:.1f}s")

    def _on_done(self, result):
        self.timer.stop()
        elapsed = time.time() - self.start_time

        if result is None:
            # survived
            self.log.append(f"[{elapsed:.1f}s] Dictionary exhausted.")
            self.log.append("")
            self.log.append("=" * 50)
            self.log.append("YOUR PASSWORD SURVIVED!")
            self.log.append(f"    Time held: {elapsed:.1f}s")
            self.log.append("    Not found in rockyou.txt (14M+ leaked passwords)")
            self.log.append("=" * 50)
            self.log.append("")
            self.log.append("Note: surviving rockyou is not a guarantee of security.")
            self.log.append("Brute force or targeted attacks can still crack short")
            self.log.append("passwords. Use long passphrases with symbols.")
            self.timer_label.setText(f"SURVIVED  ({elapsed:.1f}s)")
            self.timer_label.setStyleSheet("color: #4ade80; padding: 8px; font-weight: bold;")
        else:
            # cracked
            self.log.append(f"[{elapsed:.1f}s] MATCH FOUND!")
            self.log.append("")
            self.log.append("=" * 50)
            self.log.append(f"PASSWORD CRACKED IN {elapsed:.1f}s")
            self.log.append(f"    Plaintext: {result}")
            self.log.append("=" * 50)
            self.log.append("")
            self.log.append("Your password was in rockyou.txt - it was leaked in real")
            self.log.append("past breaches. Never reuse it anywhere!")
            self.timer_label.setText(f"CRACKED  ({elapsed:.1f}s)")
            self.timer_label.setStyleSheet("color: #f06b78; padding: 8px; font-weight: bold;")

        self.start_btn.setEnabled(True)

    def _on_error(self, err):
        self.timer.stop()
        self.log.append(f"[ERROR] {err}")
        self.log.append("")
        self.log.append("Make sure the backend container is running:")
        self.log.append("  ./backend-docker.sh start")
        self.timer_label.setText("Backend offline")
        self.timer_label.setStyleSheet("color: #f06b78; padding: 8px;")
        self.start_btn.setEnabled(True)


# =============================================================================
# Game 4: Factorize!
# =============================================================================

class FactorizeGame(QWidget):
    """Find p and q such that p * q = N. Difficulty goes up, final boss is unsolvable."""

    # (lower_bound, upper_bound, time_in_seconds)
    LEVELS = [
        (2, 20, 30),
        (10, 100, 45),
        (100, 1000, 60),
        (1000, 10000, 90),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.level = 0
        self.p = 0
        self.q = 0
        self.n = 0
        self.time_left = 0
        self.score = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._setup_ui()
        self._new_level()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QLabel("Factorize!")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #53a8d8;")
        layout.addWidget(header)

        info = QLabel(
            "RSA is based on the difficulty of factoring large numbers into primes. "
            "Find p and q such that p * q = N. Uses: pure number theory (RSA teaser)."
        )
        info.setStyleSheet("color: #8a8aa0; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # N display
        n_group = QGroupBox("N = p * q")
        nl = QVBoxLayout(n_group)
        self.n_label = QLabel("")
        self.n_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.n_label.setStyleSheet(
            "color: #4ade80; padding: 14px; background: #0f0f23; "
            "border-radius: 4px; border: 1px solid #0f3460;"
        )
        self.n_label.setWordWrap(True)
        self.n_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.n_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        nl.addWidget(self.n_label)
        layout.addWidget(n_group)

        # input
        input_group = QGroupBox("Your Factors")
        ig = QGridLayout(input_group)
        ig.setHorizontalSpacing(10)
        ig.setVerticalSpacing(8)

        p_lbl = QLabel("p =")
        p_lbl.setStyleSheet("color: #8a8aa0;")
        ig.addWidget(p_lbl, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("First prime")
        ig.addWidget(self.p_input, 0, 1)

        q_lbl = QLabel("q =")
        q_lbl.setStyleSheet("color: #8a8aa0;")
        ig.addWidget(q_lbl, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.q_input = QLineEdit()
        self.q_input.setPlaceholderText("Second prime")
        self.q_input.returnPressed.connect(self._check_answer)
        ig.addWidget(self.q_input, 1, 1)

        self.submit_btn = QPushButton("Check")
        self.submit_btn.setObjectName("btnRun")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._check_answer)
        ig.addWidget(self.submit_btn, 2, 1)

        layout.addWidget(input_group)

        # status
        sr = QHBoxLayout()
        self.level_label = QLabel("Level 1/5")
        self.level_label.setStyleSheet("color: #53a8d8; font-weight: bold;")
        sr.addWidget(self.level_label)
        sr.addStretch()

        self.timer_label = QLabel("")
        self.timer_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: #53a8d8;")
        sr.addWidget(self.timer_label)
        sr.addStretch()

        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet("color: #53a8d8; font-weight: bold;")
        sr.addWidget(self.score_label)
        layout.addLayout(sr)

        # message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8a8aa0;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _new_level(self):
        if self.level >= len(self.LEVELS):
            self._show_boss()
            return

        lo, hi, secs = self.LEVELS[self.level]
        primes = [x for x in range(lo, hi) if is_prime(x)]
        self.p = random.choice(primes)
        self.q = random.choice([x for x in primes if x != self.p])
        if self.p > self.q:
            self.p, self.q = self.q, self.p
        self.n = self.p * self.q

        self.n_label.setText(str(self.n))
        self.n_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.p_input.setText("")
        self.q_input.setText("")
        self.p_input.setEnabled(True)
        self.q_input.setEnabled(True)
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("Check")

        self.time_left = secs
        self.level_label.setText(f"Level {self.level + 1}/5")
        self.timer_label.setText(f"{self.time_left}s")
        self.timer_label.setStyleSheet("color: #53a8d8;")
        self.status_label.setText("")
        self.timer.start(1000)

    def _tick(self):
        self.time_left -= 1
        self.timer_label.setText(f"{self.time_left}s")
        if self.time_left <= 5:
            self.timer_label.setStyleSheet("color: #f06b78;")
        if self.time_left <= 0:
            self.timer.stop()
            self.status_label.setText(f"Time up! It was {self.p} * {self.q} = {self.n}")
            self.status_label.setStyleSheet("color: #f06b78;")
            self.submit_btn.setEnabled(False)
            QTimer.singleShot(2200, self._advance)

    def _check_answer(self):
        try:
            p_in = int(self.p_input.text().strip())
            q_in = int(self.q_input.text().strip())
        except ValueError:
            self.status_label.setText("Please enter integers!")
            self.status_label.setStyleSheet("color: #f06b78;")
            return

        if {p_in, q_in} == {self.p, self.q}:
            self.timer.stop()
            points = (self.level + 1) * 100
            self.score += points
            self.score_label.setText(f"Score: {self.score}")
            self.status_label.setText(
                f"Correct! {self.p} * {self.q} = {self.n}  (+{points} points)"
            )
            self.status_label.setStyleSheet("color: #4ade80; font-weight: bold;")
            self.submit_btn.setEnabled(False)
            QTimer.singleShot(1800, self._advance)
        else:
            self.status_label.setText(
                f"{p_in} * {q_in} = {p_in * q_in}, not {self.n}. Try again!"
            )
            self.status_label.setStyleSheet("color: #f06b78;")

    def _advance(self):
        self.level += 1
        self._new_level()

    def _show_boss(self):
        """Final level: a huge number that is practically unfactorable by hand."""
        self.timer.stop()
        # two large primes, pre-picked
        self.p = 9999999967
        self.q = 9999999943
        self.n = self.p * self.q

        self.n_label.setText(str(self.n))
        self.level_label.setText("Level 5/5 - BOSS")
        self.timer_label.setText("inf")
        self.timer_label.setStyleSheet("color: #f06b78; font-weight: bold;")
        self.status_label.setText(
            "This N has 20 digits. Real RSA uses 600+. Good luck trying - "
            "but this is exactly why RSA is secure. Click 'Give Up' for the answer."
        )
        self.status_label.setStyleSheet("color: #f06b78;")
        self.submit_btn.setText("Give Up")
        # IMPORTANT: re-enable the button here. _check_answer and _tick disable
        # it before scheduling _advance, which eventually calls _show_boss.
        self.submit_btn.setEnabled(True)
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._show_rsa_lesson)

    def _show_rsa_lesson(self):
        self.n_label.setText(f"{self.p}  *  {self.q}  =  {self.n}")
        self.n_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.status_label.setText(
            "RSA-2048 uses primes with ~300 digits each, making N ~600 digits long. "
            "The best known algorithms would take longer than the age of the universe "
            "to factor such an N. That is the one-way function behind RSA. "
            "Check the 'RSA Encryption' tab for the real thing in Gilfi."
        )
        self.status_label.setStyleSheet("color: #53a8d8;")
        self.submit_btn.setText("Restart")
        self.submit_btn.setEnabled(True)
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._restart)

    def _restart(self):
        self.level = 0
        self.score = 0
        self.score_label.setText("Score: 0")
        self.submit_btn.setText("Check")
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._check_answer)
        self._new_level()


# =============================================================================
# Arcade Widget (contains all 4 games as tabs)
# =============================================================================

ARCADE_TABS_STYLE = """
QTabWidget::pane {
    background: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    top: -1px;
}
QTabBar::tab {
    background: #16213e;
    color: #8a8aa0;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border: 1px solid #0f3460;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #0f3460;
    color: #ffffff;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #1a5276;
    color: #ffffff;
}
"""


class ArcadeWidget(QWidget):
    """Root widget of the arcade. Holds a QTabWidget with the 4 games."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title = QLabel("Gilfi Arcade")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        desc = QLabel(
            "Mini-games to learn crypto basics the fun way. "
            "Each game uses one of our Gilfi modules."
        )
        desc.setStyleSheet("color: #8a8aa0; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(ARCADE_TABS_STYLE)
        self.tabs.addTab(CrackTheCodeGame(),      "Crack the Code")
        self.tabs.addTab(HashHunterGame(),        "Hash Hunter")
        self.tabs.addTab(SurviveTheCrackerGame(), "Survive the Cracker")
        self.tabs.addTab(FactorizeGame(),         "Factorize!")

        layout.addWidget(self.tabs, stretch=1)


def create_page():
    """Entry point - called by mainwindow.register_tools()."""
    return ArcadeWidget()
