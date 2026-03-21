from Converting.BinaryOperator import BinaryOperator
from Converting.FloatOperator import FloatOperator
from Utils.ArrayStringConverter import ArrayStringConverter
from math import log2, ceil

class Divider:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2
        self.operator = BinaryOperator()
        self.float_operator = FloatOperator()
        self.converter = ArrayStringConverter()

    def _is_greater_equal(self, bits1, bits2):
        """Сравнение двух двоичных массивов (bits1 >= bits2)"""
        # Убираем ведущие нули для корректного сравнения длин
        b1 = self._trim_zeros(bits1)
        b2 = self._trim_zeros(bits2)

        if len(b1) > len(b2): 
            return True
        if len(b1) < len(b2): 
            return False

        for i in range(len(b1)):
            if b1[i] > b2[i]: 
                return True
            if b1[i] < b2[i]: 
                return False
        return True

    def _sub_arrays(self, bits1, bits2):
        """Вычитание двоичных массивов: bits1 - bits2"""
        res = []
        b1 = bits1[:]
        b2 = [0] * (len(b1) - len(bits2)) + bits2  # Выравниваем длины

        borrow = 0
        for i in range(len(b1) - 1, -1, -1):
            sub = b1[i] - b2[i] - borrow
            if sub < 0:
                sub += 2
                borrow = 1
            else:
                borrow = 0
            res.insert(0, sub)
        return self._trim_zeros(res)

    def _trim_zeros(self, bits):
        """Удаление ведущих нулей"""
        i = 0
        while i < len(bits) - 1 and bits[i] == 0:
            i += 1
        return bits[i:]

    def divide_bits(self, dividend, divisor, precision=5):
        """Ядро деления: работа с массивами 0 и 1"""
        quotient_int = []
        remainder = []

        # Целая часть
        for bit in dividend:
            remainder.append(bit)
            if self._is_greater_equal(remainder, divisor):
                remainder = self._sub_arrays(remainder, divisor)
                quotient_int.append(1)
            else:
                quotient_int.append(0)

        # Дробная часть
        quotient_frac = []
        for _ in range(precision):
            remainder.append(0)  # Эквивалент remainder *= 2
            remainder = self._trim_zeros(remainder)
            if self._is_greater_equal(remainder, divisor):
                remainder = self._sub_arrays(remainder, divisor)
                quotient_frac.append(1)
            else:
                quotient_frac.append(0)

        return self._trim_zeros(quotient_int) or [0], quotient_frac

    def divide_direct(self):
        print("\n=== ДЕЛЕНИЕ В ПРЯМОМ КОДЕ (32-битный результат) ===")
        print("Числа: {self.num1} / {self.num2}")

        if self.num2 == 0:
            print("Ошибка: деление на ноль!")
            return None, None

        # Константы формата
        SIGN_BITS = 1

        # 1. Определяем знак результата
        sign = 0 if (self.num1 >= 0) == (self.num2 >= 0) else 1

        # 2. Получаем модули чисел в битах (без знака)
        raw_dividend = self.operator.get_direct_code(abs(self.num1))[1:]
        raw_divisor = self.operator.get_direct_code(abs(self.num2))[1:]

        # Удаляем ведущие нули для корректного деления
        dividend = self._trim_zeros(raw_dividend)
        divisor = self._trim_zeros(raw_divisor)

        print(f"Делимое (модуль): {self.converter.array_to_string(dividend)}")
        print(f"Делитель (модуль): {self.converter.array_to_string(divisor)}")

        # 3. Преобразуем битовые массивы в целые числа для вычислений
        dividend_int = self.operator.array_to_decimal_direct(dividend)
        divisor_int = self.operator.array_to_decimal_direct(divisor)

        # 4. Вычисляем целую часть частного
        int_quotient = dividend_int // divisor_int
        print(int_quotient)
        if int_quotient != 0:
            print(ceil(log2(int_quotient)))
        if int_quotient == 0:
            int_bits = 1
        elif int_quotient == 1:
            int_bits = 2
        else:
            int_bits = ceil(log2(int_quotient)) + 2
        frac_bits = 31 - int_bits
        remainder = dividend_int % divisor_int

        # Конвертируем целую часть в биты (правое выравнивание)
        int_part_bits = self.operator.get_direct_code(int_quotient, int_bits)

        # 5. Вычисляем дробную часть (алгоритм "умножение остатка на 2")
        frac_part_bits = [0] * frac_bits
        current_remainder = remainder

        for i in range(frac_bits):
            # Умножаем остаток на 2 (сдвиг влево)
            current_remainder *= 2

            # Если остаток >= делителя, бит дробной части = 1
            if current_remainder >= divisor_int:
                frac_part_bits[i] = 1
                current_remainder -= divisor_int
            # else бит остаётся 0

        # 6. Собираем итоговый 32-битный результат
        # Формат: [знак][целая часть][дробная часть]
        result = [sign] + int_part_bits + frac_part_bits

        # Обрезаем или дополняем до ровно 32 бит
        if len(result) > 32:
            result = result[:32]
        elif len(result) < 32:
            result += [0] * (32 - len(result))

        # 7. Конвертация результата обратно в десятичное для проверки
        # Целая часть
        int_dec = 0
        for i in range(int_bits):
            if result[SIGN_BITS + i] == 1:
                int_dec += (2 ** (int_bits - 1 - i))

        # Дробная часть
        frac_dec = 0
        for i in range(frac_bits):
            if result[SIGN_BITS + int_bits + i] == 1:
                frac_dec += (2 ** -(i + 1))

        # Полный результат с учётом знака
        result_dec = (int_dec + frac_dec) * (-1 if sign == 1 else 1)

        # 8. Вывод результатов
        print(f"\n{'=' * 60}")
        print(f"Полный результат: {self.converter.array_to_string(result)}")

        print(f"\nРезультат (dec): {result_dec:.5f}")
        print(f"Проверка: {self.num1 / self.num2:.5f}")

        # Проверка на переполнение целой части
        if int_quotient >= (2 ** int_bits):
            print(f"\nВНИМАНИЕ: Целая часть ({int_quotient}) не помещается в {int_bits} бит!")

        return result, result_dec

    def ieee754_div(self):
        print("\n=== IEEE-754 ДЕЛЕНИЕ (BIT-LEVEL) ===")
        if self.num2 == 0:
            print("Ошибка: деление на ноль!")
            return None

        bits1 = self.float_operator.float_to_ieee754(self.num1)
        bits2 = self.float_operator.float_to_ieee754(self.num2)

        res_sign = bits1[0] ^ bits2[0]

        # 3. Экспонента
        # Формула: $E_{res} = E_1 - E_2 + 127$
        exp1_val = self.operator.array_to_decimal_direct(bits1[1:9])
        exp2_val = self.operator.array_to_decimal_direct(bits2[1:9])
        res_exp_val = exp1_val - exp2_val + 127

        # 4. Мантисса (с неявной единицей)
        m1 = [1] + bits1[9:]
        m2 = [1] + bits2[9:]

        # Делим мантиссы (берем с запасом для нормализации)
        q_int, q_frac = self.divide_bits(m1, m2, precision=25)

        # 5. Нормализация
        # Если целая часть [1], то мантисса — это q_frac
        # Если целая часть [0], нужно сдвинуть влево (но при делении 1.x / 1.y результат всегда 0.1... или 1.x)
        if q_int == [1]:
            res_mantissa = q_frac[:23]
        else:
            # Сдвиг влево
            res_mantissa = q_frac[1:24]
            res_exp_val -= 1

        # Собираем экспоненту обратно в биты (8 бит)
        res_exp_bits = [(res_exp_val >> i) & 1 for i in range(7, -1, -1)]

        # Итоговый результат
        final_res = [res_sign] + res_exp_bits + res_mantissa
        final_res_dec = self.float_operator.ieee754_to_float(final_res)
        if self.num1 == 0:
            final_res = [0] * 32
            final_res_dec = 0.0
        print(f"Результат IEEE-754: {self.converter.array_to_string(final_res)}")
        print(f"Результат в десятичном коде: {final_res_dec}")
        print(f"Проверка: {self.num1 / self.num2}")

        return final_res

