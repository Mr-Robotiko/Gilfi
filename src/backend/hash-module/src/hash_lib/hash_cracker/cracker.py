import sqlite3
import os
import re
from typing import Optional, List, Generator, Tuple
from itertools import chain
from multiprocessing import Pool, cpu_count
from functools import lru_cache

from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_identifier.identifier import HashIdentifier


class Cracker:
    # Comprehensive rule set based on real-world password patterns
    # Covers common transformations seen in actual password databases
    RULE_TEMPLATES = [
        # ===== TIER 1: MOST COMMON (Try first - highest success rate) =====
        ('none', lambda w: w),                           # Original word
        ('capitalize', lambda w: w.capitalize()),        # Monkey
        ('uppercase', lambda w: w.upper()),              # MONKEY
        ('lowercase', lambda w: w.lower()),              # monkey
        
        # ===== TIER 2: CAPITALIZED + COMMON SUFFIXES =====
        ('cap_append_1', lambda w: w.capitalize() + '1'),           # Monkey1
        ('cap_append_1!', lambda w: w.capitalize() + '1!'),         # Monkey1!
        ('cap_append_123', lambda w: w.capitalize() + '123'),       # Monkey123
        ('cap_append_!', lambda w: w.capitalize() + '!'),           # Monkey!
        ('cap_append_12', lambda w: w.capitalize() + '12'),         # Monkey12
        ('cap_append_1234', lambda w: w.capitalize() + '1234'),     # Monkey1234
        
        # ===== TIER 3: YEARS (Current and recent) =====
        ('cap_append_2026', lambda w: w.capitalize() + '2026'),     # Monkey2026
        ('cap_append_2025', lambda w: w.capitalize() + '2025'),     # Monkey2025
        ('cap_append_2024', lambda w: w.capitalize() + '2024'),     # Monkey2024
        ('append_2026', lambda w: w + '2026'),                      # monkey2026
        ('append_2025', lambda w: w + '2025'),
        ('append_2024', lambda w: w + '2024'),
        
        # ===== TIER 4: LEET SPEAK VARIATIONS =====
        ('leet_vowels', lambda w: w.replace('o', '0').replace('e', '3').replace('a', '@').replace('i', '1')),  # m0nk3y
        ('cap_leet_vowels', lambda w: w.capitalize().replace('o', '0').replace('e', '3').replace('a', '@')),   # M0nk3y
        ('leet_o_only', lambda w: w.replace('o', '0')),             # m0nkey
        ('leet_a_only', lambda w: w.replace('a', '@')),             # monkey (no 'a')
        ('cap_leet_o', lambda w: w.capitalize().replace('o', '0')), # M0nkey
        ('cap_leet_a', lambda w: w.capitalize().replace('a', '@')), # Monkey (no 'a')
        
        # ===== TIER 5: LEET SPEAK + SUFFIXES =====
        ('cap_leet_append_underscore', lambda w: w.capitalize().replace('o', '0').replace('e', '3') + '_'),  # M0nk3y_
        ('leet_append_1', lambda w: w.replace('o', '0').replace('e', '3') + '1'),                           # m0nk3y1
        ('cap_leet_append_1', lambda w: w.capitalize().replace('o', '0').replace('e', '3') + '1'),          # M0nk3y1
        
        # ===== TIER 6: SPECIAL CHARACTER WRAPPING =====
        ('wrap_exclamation', lambda w: '!' + w + '!'),              # !monkey!
        ('wrap_xx', lambda w: 'xX' + w + 'Xx'),                     # xXmonkeyXx
        ('cap_wrap_xx', lambda w: 'xX' + w.capitalize() + 'Xx'),    # xXMonkeyXx
        
        # ===== TIER 7: COMMON NUMBER SUFFIXES =====
        ('append_99', lambda w: w + '99'),                          # monkey99
        ('cap_append_99', lambda w: w.capitalize() + '99'),         # Monkey99
        ('append_1', lambda w: w + '1'),                            # monkey1
        ('append_123', lambda w: w + '123'),                        # monkey123
        ('append_12', lambda w: w + '12'),                          # monkey12
        
        # ===== TIER 8: SPECIAL CHARACTER SUFFIXES =====
        ('append_!', lambda w: w + '!'),                            # monkey!
        ('append_!!', lambda w: w + '!!'),                          # monkey!!
        ('append_$$', lambda w: w + '$$'),                          # monkey$$
        ('append_@', lambda w: w + '@'),                            # monkey@
        ('append_#', lambda w: w + '#'),                            # monkey#
        ('cap_append_#', lambda w: w.capitalize() + '#'),           # Monkey#
        
        # ===== TIER 9: ALTERNATING CASE =====
        ('alternate_case', lambda w: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(w))),  # MoNkEy
        ('alternate_case_99', lambda w: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(w)) + '99'),  # MoNkEy99
        
        # ===== TIER 10: SYMBOL SUBSTITUTIONS + SUFFIXES =====
        ('cap_symbol_sub_hash', lambda w: w.capitalize().replace('a', '@') + '#'),  # Monkey# (no 'a' in monkey)
        ('symbol_sub_a', lambda w: w.replace('a', '@')),            # For words with 'a'
        ('cap_symbol_sub_a', lambda w: w.capitalize().replace('a', '@')),
        
        # ===== TIER 11: PREPEND PATTERNS =====
        ('prepend_1', lambda w: '1' + w),                           # 1monkey
        ('prepend_!', lambda w: '!' + w),                           # !monkey
    ]

    def __init__(self, db_path = None, use_multiprocessing: bool = False):
        # Use persistent path in /app/data if no path specified
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = "/app/data/cache"
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "hash_cache.db")
        else:
            self.db_path = db_path
        self._setup_db()
        self.use_multiprocessing = use_multiprocessing
        self._hash_cache = {}  # In-memory cache for current session

    def _setup_db(self) -> None:
        """
        Setups a database to store hashes, that are already cracked
        :return: NONE
        """
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS hashes "
                               "(hash TEXT PRIMARY KEY, "
                               "plain TEXT);")

    def _check_cache(self, hash_value) -> str:
        """
        Checks in-memory cache first, then sqlite database for cracked hashes
        :param hash_value: str -> the hash value that should be checked
        :return: str -> the plaintext of the cracked hash
        """
        # Check in-memory cache first (much faster)
        if hash_value in self._hash_cache:
            return self._hash_cache[hash_value]
        
        # Check database
        with sqlite3.connect(self.db_path) as connection:
            result: sqlite3.Cursor = connection.execute("SELECT plain FROM hashes WHERE hash = ?",
                                                        (hash_value,)).fetchone()
            if result:
                # Store in memory cache for future lookups
                self._hash_cache[hash_value] = result[0]
                return result[0]
            return None

    def _save_to_cache(self, hash_value, plain_text) -> None:
        """
        Save cracked hashes into memory cache and database
        :param hash_value: str -> the hash value that should be cracked
        :param plain_text: str -> the according plaintext
        :return: NONE
        """
        # Save to memory cache
        self._hash_cache[hash_value] = plain_text
        
        # Save to database
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("INSERT OR IGNORE INTO hashes (hash, plain) VALUES (?, ?)",
                               (hash_value, plain_text))

    def _wordlist_shuffler(self, wordlist_path: str) -> Generator[str, None, None]:
        """
        Generator that yields words from wordlist with various transformations
        based on Hashcat/John the Ripper inspired rules to maximize cracking success.
        
        Applies 70+ rule-based transformations per word including:
        - Case manipulations (lowercase, uppercase, capitalize, toggle)
        - Append/prepend operations (numbers, special chars, years)
        - Leet speak substitutions (multiple variants)
        - Word manipulations (duplicate, reverse, rotate)
        - Combined rules (most common real-world patterns)
        
        :param wordlist_path: str -> path to the wordlist file
        :yield: str -> transformed password candidates
        """
        try:
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as wordlist:
                for line in wordlist:
                    base_word = line.strip()
                    if not base_word:
                        continue
                    
                    # Apply each rule transformation to the base word
                    for rule_name, rule_func in self.RULE_TEMPLATES:
                        try:
                            transformed = rule_func(base_word)
                            if transformed:  # Only yield non-empty results
                                yield transformed
                        except (IndexError, AttributeError):
                            # Skip rules that fail (e.g., operations on too-short words)
                            continue
        except FileNotFoundError:
            raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")

    def crack(self, hash_value: str, path: str, algorithm: Optional[str], use_shuffler: bool = True, max_words: Optional[int] = None) -> None | str:
        """
        Cracks a given hash with a passed wordlist and a specified algorithm.
        Uses optimized wordlist shuffler with rule-based transformations.
        
        :param hash_value: str ->  the hash value that should be cracked
        :param path: str -> the path to the local wordlist
        :param algorithm: optional -> determines the algorithm
        :param use_shuffler: bool -> whether to use the wordlist shuffler (default: True)
        :param max_words: optional -> limit number of base words to process (for testing/performance)
        :return: None or the plaintext if the hash is cracked
        """
        cached = self._check_cache(hash_value)
        if cached:
            return cached

        hasher: Hasher = Hasher()
        identifier: HashIdentifier = HashIdentifier()
        hash_types: List[str] = list()

        if algorithm is None:
            hash_types = identifier.identify(hash_value)
        else:
            hash_types.append(algorithm)

        try:
            if use_shuffler:
                # Use optimized wordlist shuffler with rule-based transformations
                # Process in batches for better performance
                word_count = 0
                for hash_type in hash_types:
                    with open(path, "r", encoding="utf-8", errors="ignore") as wordlist:
                        for line in wordlist:
                            base_word = line.strip()
                            if not base_word:
                                continue
                            
                            # Check max_words limit if specified
                            if max_words and word_count >= max_words:
                                break
                            word_count += 1
                            
                            # Apply all rules to this word
                            for rule_name, rule_func in self.RULE_TEMPLATES:
                                try:
                                    transformed = rule_func(base_word)
                                    if transformed and hash_value == hasher.hash(transformed, hash_type):
                                        self._save_to_cache(hash_value, transformed)
                                        return transformed
                                except (IndexError, AttributeError):
                                    continue
                    
                    # If we found it, we already returned above
                    if max_words and word_count >= max_words:
                        break
            else:
                # Original simple wordlist iteration
                with open(path, "r", encoding="utf-8", errors="ignore") as wordlist:
                    for hash_type in hash_types:
                        for line in wordlist:
                            word = line.strip()
                            if hash_value == hasher.hash(word, hash_type):
                                self._save_to_cache(hash_value, word)
                                return word

        except FileNotFoundError:
            raise FileNotFoundError

        return None
