import re
from typing import List


class HashIdentifier:
    def __init__(self):

        self.hex_map = {                                # Common Hash character lengths
            32:  ["MD5"],
            40:  ["SHA-1"],
            56:  ["SHA-224", "SHA3-224"],
            64:  ["SHA-256", "SHA3-256"],
            96:  ["SHA-384", "SHA3-384"],
            128: ["SHA-512", "SHA3-512", "Whirlpool"]
        }

    def identify(self, hash_value: str) -> List[str]:
        """
        Determine the type of hash based on the length of a given hash value
        :param hash_value: str -> the given hash value
        :return: List[str] -> a list of potential algorithm
        """
        hash_value: str = hash_value.strip()
        length_hash: int = len(hash_value)

        # BCrypt format
        if hash_value.startswith('$') and length_hash == 60:
            return ["BCrypt"]

        # Validate Hexadecimal
        if not re.fullmatch(r'[a-fA-F0-9]+', hash_value):
            return ["Invalid (Not Hexadecimal)"]

        return self.hex_map.get(length_hash, ["Unknown Algorithm"])