from Utils.ArrayStringConverter import ArrayStringConverter


class BinaryOperator:

    def __init__(self, bits=32):
        self.bits = bits
        self.converter = ArrayStringConverter()

    def get_direct_code(self, num, length=None):
        if not isinstance(num, int):
            return None
        if length is None:
            length = self.bits
        arr = [0] * length
        negative = num < 0
        num = abs(num)

        idx = length - 1
        while num > 0 and idx >= 1:
            arr[idx] = num % 2
            num //= 2
            idx -= 1

        if negative:
            arr[0] = 1

        return arr

    def get_inverse_code(self, num, length=None):
        if not isinstance(num, int):
            return None
        if length is None:
            length = self.bits
        arr = self.get_direct_code(num, length)
        if num < 0:
            for i in range(1, length):
                arr[i] = 1 - arr[i]
        return arr

    def get_complement_code(self, num, length=None):
        if not isinstance(num, int):
            return None
        if length is None:
            length = self.bits
        arr = self.get_inverse_code(num, length)
        if num < 0:
            carry = 1
            for i in range(length - 1, -1, -1):
                arr[i] += carry
                if arr[i] > 1:
                    arr[i] = 0
                    carry = 1
                else:
                    carry = 0
        return arr

    def array_to_decimal_direct(self, arr):
        """Перевод массива бит в десятичное число (без int(x, 2))"""
        result = 0
        power = 1
        for i in range(len(arr) - 1, -1, -1):
            if arr[i] == 1:
                result += power
            power *= 2
        return result

    def array_to_decimal_complement(self, arr):
        # Если число положительное (знак 0), переводим просто как бинарный массив
        if arr[0] == 0:
            result = self.array_to_decimal_direct(arr)
            return result

        # Если отрицательное (знак 1):
        # 1. Инвертируем
        inverted = [1 - b for b in arr]
        # 2. Прибавляем 1 (получаем модуль)
        carry = 1
        for i in range(len(inverted) - 1, -1, -1):
            val = inverted[i] + carry
            inverted[i] = val % 2
            carry = val // 2

        # 3. Переводим получившийся модуль в десятичное число
        magnitude = 0
        for bit in inverted:
            magnitude = (magnitude << 1) | bit

        # 4. Возвращаем со знаком минус
        return -magnitude

    def display_codes(self, num):
        if not isinstance(num, int):
            return None
        print(f"\nЧисло: {num}")
        direct = self.get_direct_code(num)
        inverse = self.get_inverse_code(num)
        complement = self.get_complement_code(num)

        print(f"Прямой код:    {self.converter.array_to_string(direct)}")
        print(f"Обратный код:  {self.converter.array_to_string(inverse)}")
        print(f"Доп. код:      {self.converter.array_to_string(complement)}")

        return direct, inverse, complement