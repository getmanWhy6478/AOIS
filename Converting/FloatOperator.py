from Constants.FloatConstants import IEEE_EXP_BITS, IEEE_SIGN_BIT, IEEE_TOTAL_BITS
from Converting.BinaryOperator import BinaryOperator
from Utils.ArrayStringConverter import ArrayStringConverter

class FloatOperator:

    def __init__(self, ieee_bits = 32):
        self.ieee_bits = ieee_bits
        self.operator = BinaryOperator()
        self.converter = ArrayStringConverter()
    def float_to_ieee754(self, num):
        """Перевод десятичного числа в IEEE-754 (32 бит)"""
        arr = [0] * self.ieee_bits

        if num == 0:
            return arr

        # Знак
        if num < 0:
            arr[0] = 1
            num = -num

        # Находим порядок
        exponent = 0
        while num >= 2:
            num /= 2
            exponent += 1
        while 1 > num > 0:
            num *= 2
            exponent -= 1

        # Смещение порядка (127 для 32 бит)
        exponent += 127

        # Записываем порядок (биты 1-8)
        for i in range(8):
            arr[8 - i] = exponent % 2
            exponent //= 2

        # Записываем мантиссу (биты 9-31, скрытая единица не хранится)
        num -= 1  # Убираем скрытую единицу
        for i in range(9, self.ieee_bits):
            num *= 2
            if num >= 1:
                arr[i] = 1
                num -= 1
            else:
                arr[i] = 0
        print(self.converter.array_to_string(arr))
        return arr

    def ieee754_to_float(self, arr):
        """Перевод IEEE-754 (32 бит) в десятичное число"""
        # Знак
        sign = -1 if arr[0] == 1 else 1

        # Порядок
        exponent = 0
        power = 1
        for i in range(7, -1, -1):
            if arr[i + 1] == 1:
                exponent += power
            power *= 2
        exponent -= 127

        # Мантисса
        mantissa = 1.0  # Скрытая единица
        power = 0.5
        for i in range(9, self.ieee_bits):
            if arr[i] == 1:
                mantissa += power
            power /= 2

        result = sign * mantissa * (2 ** exponent)
        print(result)
        return result

    def ieee754_bits_to_parts(self, bits):
        """
        Извлечь из IEEE-754 битов: знак, порядок, мантиссу
        """
        sign = bits[IEEE_SIGN_BIT]

        exp_bits = bits[IEEE_SIGN_BIT + 1: IEEE_SIGN_BIT + 1 + IEEE_EXP_BITS]
        exponent = self.operator.array_to_decimal_direct(exp_bits)

        mant_bits = bits[IEEE_SIGN_BIT + IEEE_EXP_BITS + 1: IEEE_TOTAL_BITS]

        return sign, exponent, mant_bits