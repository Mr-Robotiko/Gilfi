from hasher import Hasher

if __name__ == '__main__':
    hasher: Hasher = Hasher()
    var: str = hasher.hash("Gilfi".upper(), "md5")
    print(var)
