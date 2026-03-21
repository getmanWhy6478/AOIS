from Converting.BCDOperator import BCDOperator
from Converting.BinaryOperator import BinaryOperator
from Converting.FloatOperator import FloatOperator
from Utils.ArrayStringConverter import ArrayStringConverter


class Addition:
    def __init__(self, num1,num2, bits = 32):
        self.num1 = num1
        self.num2 = num2
        self.bits = bits
        self.operator = BinaryOperator()
        self.float_operator = FloatOperator()
        self.converter = ArrayStringConverter()
        self.bcd_operator = BCDOperator()

    def add_arrays(self, arr1, arr2, length=None):
        if length is None:
            length = self.bits
        """Сложение двух массивов бит"""
        result = [0] * length
        carry = 0

        for i in range(length - 1, -1, -1):
            sum_val = arr1[i] + arr2[i] + carry
            result[i] = sum_val % 2
            carry = sum_val // 2

        return result

    def add_complement(self):
        """Сложение двух чисел в дополнительном коде"""
        print("\n=== СЛОЖЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ ===")
        print(f"Числа: {self.num1} + {self.num2}")

        comp1 = self.operator.get_complement_code(self.num1)
        comp2 = self.operator.get_complement_code(self.num2)

        print(f"Доп. код A: {self.converter.array_to_string(comp1)}")
        print(f"Доп. код B: {self.converter.array_to_string(comp2)}")

        result = self.add_arrays(comp1, comp2)
        print(f"Сумма:      {self.converter.array_to_string(result)}")

        result_dec = self.operator.array_to_decimal_complement(result)
        print(f"Результат (dec): {result_dec}")
        print(f"Проверка: {self.num1} + {self.num2} = {self.num1 + self.num2}")

        return result, result_dec

    def ieee754_add(self):
        """Сложение чисел в формате IEEE-754"""
        print("\n=== IEEE-754 СЛОЖЕНИЕ ===")
        print(f"Числа: {self.num1} + {self.num2}")

        arr1 = self.float_operator.float_to_ieee754(self.num1)
        arr2 = self.float_operator.float_to_ieee754(self.num2)

        print(f"IEEE-754 A: {self.converter.array_to_string(arr1)}")
        print(f"IEEE-754 B: {self.converter.array_to_string(arr2)}")

        result = self.num1 + self.num2

        result_arr = self.float_operator.float_to_ieee754(result)
        print(f"Результат IEEE-754: {self.converter.array_to_string(result_arr)}")
        print(f"Результат (dec): {result}")

        return result_arr, result

    def bcd_add(self):
        """Сложение в BCD коде"""
        print("\n=== BCD 8421 СЛОЖЕНИЕ ===")
        print(f"Числа: {self.num1} + {self.num2}")

        result = self.num1 + self.num2
        arr = self.bcd_operator.decimal_to_bcd_8421(result)

        print(f"Результат BCD: {self.converter.array_to_string(arr)}")
        print(f"Результат (dec): {result}")

        return arr, result