import hashlib


class Hasher:
    @staticmethod
    def hash(message: str,
             algorithm: str) -> str | None:

        # Check if arguments match data types
        if not isinstance(message, str) or not isinstance(algorithm, str):
            print("=====================")
            print("Unsupported argument schema")
            print("=====================")
            raise AttributeError

        # Hash the provided values
        try:
            h = hashlib.new(algorithm.lower())
            h.update(message.encode("UTF-8"))
            hash_value: str = h.hexdigest()
            return hash_value

        # If ir fails, the supported algorithm is wrong
        except ValueError:
            print("=====================")
            print("Unsupported hash type")
            print("=====================")
            raise ValueError
