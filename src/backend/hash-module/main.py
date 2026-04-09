from typing import Tuple


def main():
    # Your logic here
    pass


def read_input() -> Tuple[str, str]:
    try:
        message: str = input("Message:\t")
        algorithm: str = input("Algorithm:\t")
        return message, algorithm

    except AttributeError:
        raise AttributeError


def main():
    hasher: Hasher = Hasher()
    (message, algorithm) = read_input()
    print(Hasher.hash(message, algorithm))


if __name__ == '__main__':
    main()
