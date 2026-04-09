from typing import Tuple
from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_cracker.cracker import Cracker


def read_input() -> Tuple[str, str]:
    try:
        message: str = input("Message:\t")
        algorithm: str = input("Algorithm:\t")
        return message, algorithm

    except AttributeError:
        raise AttributeError


def hash_test():
    hasher: Hasher = Hasher()
    (message, algorithm) = read_input()
    print(hasher.hash(message, algorithm))


def crack_test():
    wordlist_path: str = "/Users/raphaeltack/Gilfi/data/wordlist/rockyou.txt"
    cracker: Cracker = Cracker()
    (message, algorithm) = read_input()
    print(cracker.crack(message, wordlist_path, algorithm))


def main():
    hash_test()
    crack_test()


if __name__ == '__main__':
    main()
