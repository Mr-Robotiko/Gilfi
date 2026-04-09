import hash_lib


class Cracker:
    @staticmethod
    def crack(hash_value: str, path: str):
        with open(path, "r", encoding = "latin-1") as file:
            for line in file:
                password = line.strip()


