class ArrayStringConverter:
    def __init__(self):
        self.array = []

    def array_to_string(self, arr):
        """Преобразовать массив бит в строку"""
        return ''.join(str(b) for b in arr)

    def string_to_array(self, s):
        """Преобразовать строку бит в массив"""
        return [int(c) for c in s]

