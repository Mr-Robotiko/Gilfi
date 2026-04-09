import sqlite3
from typing import Optional, List

from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_identifier.identifier import HashIdentifier


class Cracker:
    def __init__(self, db_path = "hash_cache.db"):
        self.db_path = db_path
        self._setup_db()

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
        Checks sqlite database, if a hash is already cracked
        :param hash_value: str -> the hash value that should be checked
        :return: str -> the plaintext of the cracked hash
        """
        with sqlite3.connect(self.db_path) as connection:
            result: sqlite3.Cursor = connection.execute("SELECT plain FROM hashes WHERE hash = ?",
                                                        (hash_value,)).fetchone()
            return result[0] if result else None

    def _save_to_cache(self, hash_value, plain_text) -> None:
        """
        Save cracked hashes into the database
        :param hash_value: str -> the hash value that should be cracked
        :param plain_text: str -> the according plaintext
        :return: NONE
        """
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("INSERT OR IGNORE INTO hashes (hash, plain) VALUES (?, ?)",
                               (hash_value, plain_text))

    def crack(self, hash_value: str, path: str, algorithm: Optional[str]) -> None | str:
        """
        Cracks a given hash with a passed wordlist and a specified algorithm
        :param hash_value: str ->  the hash value that should be cracked
        :param path: str -> the path to the local wordlist
        :param algorithm: optional -> determines the algorithm
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
            with open(path, "r", encoding = "utf-8", errors = "ignore") as wordlist:
                for hash_type in hash_types:
                    for line in wordlist:
                        word = line.strip()
                        if hash_value == hasher.hash(word, hash_type):
                            self._save_to_cache(hash_value, word)
                            return word

        except FileNotFoundError:
            raise FileNotFoundError

        return None
