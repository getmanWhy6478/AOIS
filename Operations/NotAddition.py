from Converting.BinaryOperator import BinaryOperator
from Converting.FloatOperator import FloatOperator
from Utils.ArrayStringConverter import ArrayStringConverter
from Operations.Addition import Addition


class NotAddition:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        self.operator = BinaryOperator()
        self.float_operator = FloatOperator()
        self.converter = ArrayStringConverter()
        self.additor = Addition(num1, num2)

    def negate_complement(self, arr):
        result = [1 - b for b in arr]
        carry = 1
        for i in range(len(result) - 1, -1, -1):
            result[i] += carry
            if result[i] > 1:
                result[i] = 0
                carry = 1
            else:
                carry = 0
        return result

    def subtract_complement(self):
        """Вычитание через сложение с отрицанием вычитаемого"""
        print("\n=== ВЫЧИТАНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ ===")
        print(f"Числа: {self.num1} - {self.num2}")

        comp1 = self.operator.get_complement_code(self.num1)
        comp2 = self.operator.get_complement_code(self.num2)

        print(f"Доп. код A:      {self.converter.array_to_string(comp1)}")
        print(f"Доп. код B:      {self.converter.array_to_string(comp2)}")

        neg_comp2 = self.negate_complement(comp2)
        print(f"-B (доп. код):   {self.converter.array_to_string(neg_comp2)}")

        result = self.additor.add_arrays(comp1, neg_comp2)
        print(f"Результат:       {self.converter.array_to_string(result)}")

        result_dec = self.operator.array_to_decimal_complement(result)
        print(f"Результат (dec): {result_dec}")
        print(f"Проверка: {self.num1} - {self.num2} = {self.num1 - self.num2}")

        return result, result_dec


    def ieee754_sub(self):
        """Вычитание чисел в формате IEEE-754"""
        print("\n=== IEEE-754 ВЫЧИТАНИЕ ===")
        print(f"Числа: {self.num1} - {self.num2}")

        result = self.num1 - self.num2

        result_arr = self.float_operator.float_to_ieee754(result)
        print(f"Результат IEEE-754: {self.converter.array_to_string(result_arr)}")
        print(f"Результат (dec): {result}")

        return result_arr, result