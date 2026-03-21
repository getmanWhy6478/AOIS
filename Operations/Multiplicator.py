from Converting.BinaryOperator import BinaryOperator
from Converting.FloatOperator import FloatOperator
from Utils.ArrayStringConverter import ArrayStringConverter


class Multiplicator:
    def __init__(self, num1, num2, bits=32):
        self.num1 = num1
        self.num2 = num2
        self.bits = bits
        self.operator = BinaryOperator()
        self.float_operator = FloatOperator()
        self.converter = ArrayStringConverter()

    def multiply_direct(self):
        """Умножение двух чисел в прямом коде (32-битный результат)"""
        print("\n=== УМНОЖЕНИЕ В ПРЯМОМ КОДЕ ===")
        print(f"Числа: {self.num1} * {self.num2}")

        # Определяем знак результата
        sign = 0 if (self.num1 >= 0) == (self.num2 >= 0) else 1
        mod1 = abs(self.num1)
        mod2 = abs(self.num2)

        # Получаем двоичные представления модулей (прямой код, знак отдельно)
        arr1 = self.operator.get_direct_code(mod1)
        arr2 = self.operator.get_direct_code(mod2)

        # Извлекаем только мантиссу (биты 1-31, без знака)
        mant1 = arr1[1:]  # 31 бит
        mant2 = arr2[1:]  # 31 бит

        print(f"Модуль A: {self.converter.array_to_string(mant1)}")
        print(f"Модуль B: {self.converter.array_to_string(mant2)}")

        # Умножение через сдвиг и сложение
        # Используем 64-битный временный массив для точного вычисления
        temp_result = [0] * (self.bits * 2)  # 64 бита

        for i in range(self.bits - 1):  # Проходим по 31 биту мантиссы
            if mant2[(self.bits - 1) - 1 - i] == 1:  # Проверяем бит B
                # Добавляем A со сдвигом
                for j in range(self.bits - 1):  # 31 бит мантиссы A
                    # Позиция в результирующем массиве
                    pos = (self.bits * 2 - 1) - i - j
                    if pos >= 0:
                        temp_result[pos] += mant1[(self.bits - 1) - 1 - j]

        # Нормализация (обработка переносов)
        carry = 0
        for i in range(len(temp_result) - 1, -1, -1):
            temp_result[i] += carry
            carry = temp_result[i] // 2
            temp_result[i] = temp_result[i] % 2

        # Извлекаем младшие 31 бит для мантиссы результата
        # (биты с индексами 33-63 в 64-битном массиве)
        result_mant = [0] * (self.bits - 1)
        for i in range(self.bits - 1):
            src_idx = len(temp_result) - 1 - i
            result_mant[(self.bits - 1) - 1 - i] = temp_result[src_idx]

        # Проверяем переполнение (старшие биты результата не нулевые)
        overflow = any(temp_result[i] == 1 for i in range(len(temp_result) - (self.bits - 1)))

        # Формируем итоговый 32-битный результат в прямом коде
        result = [0] * self.bits
        result[0] = sign  # Бит знака
        for i in range(self.bits - 1):
            result[i + 1] = result_mant[i]  # Мантисса

        # Конвертация результата в десятичное число
        result_dec = 0
        power = 1
        # Проходим по мантиссе справа налево (от младшего бита к старшему)
        for i in range(self.bits - 1, 0, -1):
            if result[i] == 1:
                result_dec += power
            power *= 2

        # Применяем знак
        if sign == 1:
            result_dec = -result_dec

        print(f"Результат (bin): {self.converter.array_to_string(result)}")
        print(f"Результат (dec): {result_dec}")
        print(f"Проверка: {self.num1} * {self.num2} = {self.num1 * self.num2}")

        if overflow:
            print("⚠️  ВНИМАНИЕ: Произошло переполнение 32-битного результата!")
            print("   Полный результат не помещается в 32 бита")

        return result, result_dec

    def ieee754_mul(self):
        """Умножение чисел в формате IEEE-754"""
        print("\n=== IEEE-754 УМНОЖЕНИЕ ===")
        print(f"Числа: {self.num1} * {self.num2}")

        result = self.num1 * self.num2

        result_arr = self.float_operator.float_to_ieee754(result)
        print(f"Результат IEEE-754: {self.converter.array_to_string(result_arr)}")
        print(f"Результат (dec): {result}")

        return result_arr, result
c = Multiplicator(-5, 34)
c.multiply_direct()