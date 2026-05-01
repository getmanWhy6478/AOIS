ALPHABET_RU = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
BASE = 33


def compute_v(key: str, alphabet: str = ALPHABET_RU) -> int:
    key = str(key).upper().strip()
    if len(key) < 2:
        key = key.ljust(2, key[0] if key else alphabet[0])

    c1, c2 = key[0], key[1]
    if c1 not in alphabet or c2 not in alphabet:
        raise ValueError("Ключ должен начинаться с двух букв русского алфавита.")

    return alphabet.index(c1) * BASE + alphabet.index(c2)


def hash_address(v: int, table_size: int, base_offset: int = 0) -> int:
    """
    h(V) = (V mod H) + B
    """
    return v % table_size + base_offset