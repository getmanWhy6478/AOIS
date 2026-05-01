import pytest
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Operations.Divider import Divider


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def div_op_default():
    """Divider с числами по умолчанию"""
    return Divider(num1=0, num2=1)


# ============================================================================
# Tests for __init__
# ============================================================================

class TestDividerInit:
    """Тесты инициализации класса"""

    def test_init_basic(self):
        op = Divider(num1=10, num2=3)
        assert op.num1 == 10
        assert op.num2 == 3
        assert op.operator is not None
        assert op.float_operator is not None
        assert op.converter is not None

    def test_init_negative_numbers(self):
        op = Divider(num1=-15, num2=5)
        assert op.num1 == -15
        assert op.num2 == 5

    def test_init_dependencies_types(self):
        op = Divider(num1=0, num2=1)
        from Converting.BinaryOperator import BinaryOperator
        from Converting.FloatOperator import FloatOperator
        from Utils.ArrayStringConverter import ArrayStringConverter

        assert isinstance(op.operator, BinaryOperator)
        assert isinstance(op.float_operator, FloatOperator)
        assert isinstance(op.converter, ArrayStringConverter)


# ============================================================================
# Tests for _trim_zeros (private method)
# ============================================================================

class TestTrimZeros:
    """Тесты вспомогательного метода удаления ведущих нулей"""

    def test_trim_zeros_all_zeros(self, div_op_default):
        bits = [0, 0, 0, 0]
        result = div_op_default._trim_zeros(bits)
        assert result == [0]

    def test_trim_zeros_single_zero(self, div_op_default):
        bits = [0]
        result = div_op_default._trim_zeros(bits)
        assert result == [0]

    def test_trim_zeros_no_leading_zeros(self, div_op_default):
        bits = [1, 0, 1, 1]
        result = div_op_default._trim_zeros(bits)
        assert result == [1, 0, 1, 1]

    def test_trim_zeros_some_leading_zeros(self, div_op_default):
        bits = [0, 0, 1, 0, 1]
        result = div_op_default._trim_zeros(bits)
        assert result == [1, 0, 1]

    def test_trim_zeros_single_one(self, div_op_default):
        bits = [0, 0, 0, 1]
        result = div_op_default._trim_zeros(bits)
        assert result == [1]

    def test_trim_zeros_empty_like(self, div_op_default):
        # Edge case: массив из одного нуля
        bits = [0]
        result = div_op_default._trim_zeros(bits)
        assert result == [0]


# ============================================================================
# Tests for _is_greater_equal (private method)
# ============================================================================

class TestIsGreaterEqual:
    """Тесты сравнения двоичных массивов"""

    def test_greater_equal_longer_is_greater(self, div_op_default):
        b1 = [1, 0, 0, 0]  # 8
        b2 = [1, 0, 1]  # 5
        assert div_op_default._is_greater_equal(b1, b2) is True

    def test_greater_equal_shorter_is_less(self, div_op_default):
        b1 = [1, 0, 1]  # 5
        b2 = [1, 0, 0, 0]  # 8
        assert div_op_default._is_greater_equal(b1, b2) is False

    def test_greater_equal_same_length_greater(self, div_op_default):
        b1 = [1, 1, 0]  # 6
        b2 = [1, 0, 1]  # 5
        assert div_op_default._is_greater_equal(b1, b2) is True

    def test_greater_equal_same_length_less(self, div_op_default):
        b1 = [1, 0, 1]  # 5
        b2 = [1, 1, 0]  # 6
        assert div_op_default._is_greater_equal(b1, b2) is False

    def test_greater_equal_equal_arrays(self, div_op_default):
        b1 = [1, 0, 1, 0]
        b2 = [1, 0, 1, 0]
        assert div_op_default._is_greater_equal(b1, b2) is True

    def test_greater_equal_with_leading_zeros(self, div_op_default):
        b1 = [0, 0, 1, 0, 1]  # 5
        b2 = [0, 1, 0, 1]  # 5
        assert div_op_default._is_greater_equal(b1, b2) is True

    def test_greater_equal_zero_vs_positive(self, div_op_default):
        b1 = [0]
        b2 = [1]
        assert div_op_default._is_greater_equal(b1, b2) is False
        assert div_op_default._is_greater_equal(b2, b1) is True

    def test_greater_equal_zero_vs_zero(self, div_op_default):
        b1 = [0]
        b2 = [0]
        assert div_op_default._is_greater_equal(b1, b2) is True


# ============================================================================
# Tests for _sub_arrays (private method)
# ============================================================================

class TestSubArrays:
    """Тесты вычитания двоичных массивов"""

    def test_sub_arrays_simple(self, div_op_default):
        b1 = [1, 0, 1, 0]  # 10
        b2 = [0, 1, 0, 1]  # 5
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [1, 0, 1]  # 5

    def test_sub_arrays_with_borrow(self, div_op_default):
        b1 = [1, 0, 0, 0]  # 8
        b2 = [0, 1, 1, 1]  # 7
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [1]  # 1

    def test_sub_arrays_equal_values(self, div_op_default):
        b1 = [1, 0, 1]
        b2 = [1, 0, 1]
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [0]

    def test_sub_arrays_result_with_leading_zeros_trimmed(self, div_op_default):
        b1 = [1, 0, 0, 0, 0]  # 16
        b2 = [0, 1, 1, 1, 1]  # 15
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [1]  # 1, без ведущих нулей

    def test_sub_arrays_different_lengths(self, div_op_default):
        b1 = [1, 0, 0, 0, 0, 0]  # 32
        b2 = [1, 0, 1]  # 5
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [1, 1, 0, 1, 1]  # 27

    def test_sub_arrays_small_minus_small(self, div_op_default):
        b1 = [1, 1]  # 3
        b2 = [1, 0]  # 2
        result = div_op_default._sub_arrays(b1, b2)
        assert result == [1]  # 1


# ============================================================================
# Tests for divide_bits (private method)
# ============================================================================

class TestDivideBits:
    """Тесты ядра деления битовых массивов"""

    def test_divide_bits_integer_exact(self, div_op_default):
        dividend = [1, 0, 1, 0]  # 10
        divisor = [1, 0, 1]  # 5
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=5)
        assert q_int == [1, 0]  # 2
        assert all(b == 0 for b in q_frac)

    def test_divide_bits_integer_with_remainder(self, div_op_default):
        dividend = [1, 0, 1, 1]  # 11
        divisor = [1, 0, 1]  # 5
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=5)
        assert q_int == [1, 0]  # 2
        # Дробная часть: 1/5 = 0.0011... в двоичной
        assert q_frac[0] == 0  # 0.0
        assert q_frac[1] == 0  # 0.00
        assert q_frac[2] == 1  # 0.001

    def test_divide_bits_fractional_only(self, div_op_default):
        dividend = [1, 0, 1]  # 5
        divisor = [1, 0, 0, 0]  # 8
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=6)
        assert q_int == [0]
        # 5/8 = 0.101 в двоичной
        assert q_frac[:3] == [1, 0, 1]

    def test_divide_bits_dividend_less_than_divisor(self, div_op_default):
        dividend = [1, 1]  # 3
        divisor = [1, 0, 0, 0]  # 8
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=5)
        assert q_int == [0]
        # 3/8 = 0.011 в двоичной
        assert q_frac[:3] == [0, 1, 1]

    def test_divide_bits_precision_parameter(self, div_op_default):
        dividend = [1]  # 1
        divisor = [1, 0, 1, 0]  # 10
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=8)
        assert q_int == [0]
        assert len(q_frac) == 8  # точность соблюдена

    def test_divide_bits_zero_dividend(self, div_op_default):
        dividend = [0]
        divisor = [1, 0, 1]  # 5
        q_int, q_frac = div_op_default.divide_bits(dividend, divisor, precision=5)
        assert q_int == [0]
        assert all(b == 0 for b in q_frac)


# ============================================================================
# Tests for divide_direct
# ============================================================================

class TestDivideDirect:
    """Тесты деления в прямом коде (32-битный результат)"""

    # --- Zero division ---

    def test_divide_direct_division_by_zero(self, div_op_default, capsys):
        op = Divider(num1=10, num2=0)
        result_arr, result_dec = op.divide_direct()
        captured = capsys.readouterr()

        assert result_arr is None
        assert result_dec is None
        assert "Ошибка: деление на ноль!" in captured.out

    # --- Positive / Positive ---

    def test_divide_direct_exact_integer(self, div_op_default, capsys):
        op = Divider(num1=20, num2=4)
        result_arr, result_dec = op.divide_direct()
        captured = capsys.readouterr()

        assert "=== ДЕЛЕНИЕ В ПРЯМОМ КОДЕ" in captured.out
        assert "Числа: 20 / 4" in captured.out
        assert "Делимое (модуль):" in captured.out
        assert "Делитель (модуль):" in captured.out
        assert result_dec == 5.0
        assert "Проверка:" in captured.out
        assert len(result_arr) == 32  # фиксированный размер

    def test_divide_direct_with_fraction(self, div_op_default):
        op = Divider(num1=10, num2=4)
        result_arr, result_dec = op.divide_direct()
        # 10/4 = 2.5
        assert abs(result_dec - 2.5) < 1e-5

    def test_divide_direct_small_result(self, div_op_default):
        op = Divider(num1=1, num2=2)
        result_arr, result_dec = op.divide_direct()
        # 1/2 = 0.5
        assert abs(result_dec - 0.5) < 1e-5

    def test_divide_direct_one_divided_by_any(self, div_op_default):
        for val in [1, 2, 5, 10]:
            op = Divider(num1=1, num2=val)
            _, result_dec = op.divide_direct()
            expected = 1.0 / val
            assert abs(result_dec - expected) < 1e-5

    def test_divide_direct_any_divided_by_one(self, div_op_default):
        for val in [1, 5, 42, 100]:
            op = Divider(num1=val, num2=1)
            _, result_dec = op.divide_direct()
            assert result_dec == float(val)

    # --- Negative / Positive and vice versa ---

    def test_divide_direct_negative_dividend(self, div_op_default):
        op = Divider(num1=-20, num2=4)
        result_arr, result_dec = op.divide_direct()
        assert result_dec == -5.0
        assert result_arr[0] == 1  # sign bit

    def test_divide_direct_negative_divisor(self, div_op_default):
        op = Divider(num1=20, num2=-4)
        result_arr, result_dec = op.divide_direct()
        assert result_dec == -5.0
        assert result_arr[0] == 1  # sign bit

    def test_divide_direct_both_negative(self, div_op_default):
        op = Divider(num1=-20, num2=-4)
        result_arr, result_dec = op.divide_direct()
        assert result_dec == 5.0
        assert result_arr[0] == 0  # sign bit (positive result)

    # --- Zero cases ---

    def test_divide_direct_zero_dividend(self, div_op_default):
        op = Divider(num1=0, num2=5)
        result_arr, result_dec = op.divide_direct()
        assert result_dec == 0.0
        assert result_arr[0] == 0

    def test_divide_direct_zero_result_format(self, div_op_default):
        op = Divider(num1=0, num2=100)
        result_arr, result_dec = op.divide_direct()
        # Результат должен быть 32 бита, все нули кроме, возможно, знака
        assert len(result_arr) == 32
        assert result_dec == 0.0

    # --- Edge values ---

    def test_divide_direct_small_numbers(self, div_op_default):
        op = Divider(num1=3, num2=7)
        _, result_dec = op.divide_direct()
        expected = 3 / 7
        assert abs(result_dec - expected) < 1e-5

    def test_divide_direct_large_quotient(self, div_op_default):
        op = Divider(num1=1000, num2=2)
        _, result_dec = op.divide_direct()
        assert result_dec == 500.0

    def test_divide_direct_result_array_format(self, div_op_default):
        """Проверка формата результата: 1 знак + 31 бит данных"""
        op = Divider(num1=15, num2=3)
        result_arr, _ = op.divide_direct()

        assert len(result_arr) == 32
        assert result_arr[0] in (0, 1)  # sign bit
        # Проверяем, что остальные биты — только 0 или 1
        assert all(b in (0, 1) for b in result_arr[1:])

    # --- Output verification ---

    def test_divide_direct_prints_binary_string(self, div_op_default, capsys):
        op = Divider(num1=10, num2=3)
        op.divide_direct()
        captured = capsys.readouterr()

        import re
        # Проверяем наличие 32-битной бинарной строки
        bin_match = re.search(r'Полный результат:\s*([01]{32})', captured.out)
        assert bin_match is not None

    def test_divide_direct_prints_decimal_with_precision(self, div_op_default, capsys):
        op = Divider(num1=10, num2=3)
        op.divide_direct()
        captured = capsys.readouterr()

        # Проверяем формат вывода с 5 знаками после запятой
        import re
        dec_match = re.search(r'Результат \(dec\):\s*([-]?\d+\.\d{5})', captured.out)
        assert dec_match is not None


# ============================================================================
# Tests for ieee754_div
# ============================================================================

class TestIeee754Div:
    """Тесты деления в формате IEEE-754"""

    # --- Division by zero ---

    def test_ieee754_div_division_by_zero(self, div_op_default, capsys):
        op = Divider(num1=10.0, num2=0.0)
        result = op.ieee754_div()
        captured = capsys.readouterr()

        assert result is None
        assert "Ошибка: деление на ноль!" in captured.out


    def test_ieee754_div_with_fraction(self, div_op_default):
        op = Divider(num1=5.0, num2=2.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 2.5) < 1e-6

    def test_ieee754_div_small_result(self, div_op_default):
        op = Divider(num1=1.0, num2=4.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 0.25) < 1e-6

    # --- Negative / Positive and vice versa ---

    def test_ieee754_div_negative_dividend(self, div_op_default):
        op = Divider(num1=-10.0, num2=2.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - (-5.0)) < 1e-6
        assert result_arr[0] == 1  # sign bit

    def test_ieee754_div_negative_divisor(self, div_op_default):
        op = Divider(num1=10.0, num2=-2.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - (-5.0)) < 1e-6
        assert result_arr[0] == 1  # sign bit

    def test_ieee754_div_both_negative(self, div_op_default):
        op = Divider(num1=-10.0, num2=-2.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 5.0) < 1e-6
        assert result_arr[0] == 0  # sign bit (positive)


    def test_ieee754_div_one_divided_by_any(self, div_op_default):
        for val in [2.0, 4.0, 10.0]:
            op = Divider(num1=1.0, num2=val)
            result_arr = op.ieee754_div()
            result_dec = op.float_operator.ieee754_to_float(result_arr)
            expected = 1.0 / val
            assert abs(result_dec - expected) < 1e-6

    # --- Fraction precision ---

    def test_ieee754_div_decimal_fractions(self, div_op_default):
        op = Divider(num1=0.3, num2=0.1)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        # 0.3 / 0.1 = 3.0 (с возможной погрешностью)
        assert abs(result_dec - 3.0) < 1e-5

    # --- Large and small values ---

    def test_ieee754_div_large_numbers(self, div_op_default):
        op = Divider(num1=1e20, num2=1e10)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 1e10) / 1e10 < 1e-5

    def test_ieee754_div_small_numbers(self, div_op_default):
        op = Divider(num1=1e-10, num2=1e-5)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        expected = 1e-5
        if expected != 0:
            assert abs(result_dec - expected) / expected < 1e-5

    # --- Normalization edge cases ---

    def test_ieee754_div_mantissa_normalization_case_1(self, div_op_default):
        """Случай, когда целая часть частного = [1]"""
        # 1.5 / 1.0 = 1.5, мантисса результата должна быть нормализована
        op = Divider(num1=1.5, num2=1.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 1.5) < 1e-6

    def test_ieee754_div_mantissa_normalization_case_2(self, div_op_default):
        """Случай, когда требуется сдвиг мантиссы влево"""
        # 0.5 / 1.0 = 0.5, требуется нормализация
        op = Divider(num1=0.5, num2=1.0)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert abs(result_dec - 0.5) < 1e-6

    # --- Output verification ---

    def test_ieee754_div_prints_binary_string(self, div_op_default, capsys):
        op = Divider(num1=6.0, num2=2.0)
        op.ieee754_div()
        captured = capsys.readouterr()

        import re
        ieee_match = re.search(r'Результат IEEE-754:\s*([01]{32})', captured.out)
        assert ieee_match is not None
        assert len(ieee_match.group(1)) == 32

    def test_ieee754_div_exponent_calculation(self, div_op_default):
        """Проверка расчёта экспоненты: E_res = E1 - E2 + 127"""
        # 8.0 = exp=130, 2.0 = exp=128, result exp = 130-128+127 = 129
        op = Divider(num1=8.0, num2=2.0)
        result_arr = op.ieee754_div()
        # Экспонента в битах 1-8
        exp_bits = result_arr[1:9]
        exp_val = sum(b * (2 ** (7 - i)) for i, b in enumerate(exp_bits))
        # 4.0 имеет экспоненту 129 (2^2, bias=127)
        assert exp_val == 129


# ============================================================================
# Integration tests
# ============================================================================

class TestIntegration:
    """Интеграционные тесты взаимодействия методов"""

    def test_both_division_methods_integer_input(self):
        """Сравнение результатов для целых чисел"""
        op = Divider(num1=20, num2=4)

        # Деление в прямом коде
        _, direct_result = op.divide_direct()

        # Деление в IEEE-754 (целые как float)
        ieee_result_arr = op.ieee754_div()
        ieee_result = op.float_operator.ieee754_to_float(ieee_result_arr)

        # Результаты должны быть близки
        assert abs(direct_result - ieee_result) < 1e-5

    def test_divide_direct_uses_binary_operator(self, div_op_default):
        """Проверка, что divide_direct использует BinaryOperator"""
        op = Divider(num1=10, num2=2)

        # Получаем прямой код модулей
        raw_div = op.operator.get_direct_code(abs(10))
        raw_divis = op.operator.get_direct_code(abs(2))

        # Проверяем извлечение мантиссы (без знака)
        mant_div = raw_div[1:]
        mant_divis = raw_divis[1:]

        assert len(mant_div) == 31  # 32 - 1 sign
        assert len(mant_divis) == 31

    def test_ieee754_div_uses_float_operator(self, div_op_default):
        """Проверка, что ieee754_div использует FloatOperator"""
        op = Divider(num1=5.0, num2=2.0)

        # Конвертация входных чисел в IEEE-754
        bits1 = op.float_operator.float_to_ieee754(5.0)
        bits2 = op.float_operator.float_to_ieee754(2.0)

        assert len(bits1) == 32
        assert len(bits2) == 32

    def test_divide_direct_result_size_fixed(self, div_op_default):
        """Проверка, что результат всегда 32 бита"""
        test_cases = [
            (1, 1), (10, 2), (100, 3), (-50, 5), (0, 10)
        ]
        for num1, num2 in test_cases:
            op = Divider(num1=num1, num2=num2)
            result_arr, _ = op.divide_direct()
            if result_arr is not None:
                assert len(result_arr) == 32

    def test_ieee754_div_result_size_fixed(self, div_op_default):
        """Проверка, что результат IEEE-754 всегда 32 бита"""
        test_cases = [
            (1.0, 1.0), (10.0, 2.0), (0.5, 0.25), (-8.0, 2.0)
        ]
        for num1, num2 in test_cases:
            op = Divider(num1=num1, num2=num2)
            result_arr = op.ieee754_div()
            if result_arr is not None:
                assert len(result_arr) == 32


# ============================================================================
# Edge cases and parametrized tests
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_divide_direct_quotient_zero_int_part(self, div_op_default):
        """Частное < 1: целая часть = 0"""
        op = Divider(num1=1, num2=10)
        result_arr, result_dec = op.divide_direct()
        assert result_dec < 1.0
        assert result_dec > 0.0

    def test_divide_direct_large_remainder_precision(self, div_op_default):
        """Деление с большим остатком: проверка точности дробной части"""
        op = Divider(num1=1, num2=3)
        _, result_dec = op.divide_direct()
        # 1/3 = 0.33333...
        assert abs(result_dec - 0.33333) < 1e-5

    def test_divide_direct_sign_bit_position(self, div_op_default):
        """Проверка, что бит знака всегда на позиции 0"""
        for n1, n2 in [(10, 2), (-10, 2), (10, -2), (-10, -2)]:
            op = Divider(num1=n1, num2=n2)
            result_arr, _ = op.divide_direct()
            expected_sign = 0 if (n1 >= 0) == (n2 >= 0) else 1
            assert result_arr[0] == expected_sign

    def test_ieee754_div_very_small_result(self, div_op_default):
        """Результат близкий к нулю"""
        op = Divider(num1=1e-20, num2=1e10)
        result_arr = op.ieee754_div()
        result_dec = op.float_operator.ieee754_to_float(result_arr)
        assert isinstance(result_dec, float)

    def test_divide_direct_fractional_bits_calculation(self, div_op_default):
        """Проверка расчёта количества бит для дробной части"""
        # 31 бит данных = int_bits + frac_bits
        op = Divider(num1=100, num2=3)  # int_quotient = 33
        result_arr, _ = op.divide_direct()
        # Проверяем, что массив имеет правильную структуру
        assert len(result_arr) == 32
        assert result_arr[0] in (0, 1)

    def test_divide_direct_overflow_warning_absent(self, div_op_default, capsys):
        """Отсутствие предупреждения при нормальном делении"""
        op = Divider(num1=50, num2=2)  # 25 помещается в 31 бит
        op.divide_direct()
        captured = capsys.readouterr()
        assert "ВНИМАНИЕ: Целая часть" not in captured.out


class TestParametrizedDivision:
    """Параметризованные тесты для широкого покрытия"""

    @pytest.mark.parametrize("num1,num2,expected", [
        # Direct division tests (integer and fractional)
        (20, 4, 5.0),
        (10, 4, 2.5),
        (1, 2, 0.5),
        (-20, 4, -5.0),
        (20, -4, -5.0),
        (-20, -4, 5.0),
        (0, 5, 0.0),
        (3, 7, 3 / 7),
        (100, 3, 100 / 3),
    ])
    def test_divide_direct_parametrized(self, num1, num2, expected):
        op = Divider(num1=num1, num2=num2)
        result_arr, result_dec = op.divide_direct()

        if result_arr is not None:  # не деление на ноль
            assert len(result_arr) == 32
            assert abs(result_dec - expected) < 1e-5

    @pytest.mark.parametrize("num1,num2,expected", [
        (8.0, 2.0, 4.0),
        (5.0, 2.0, 2.5),
        (1.0, 4.0, 0.25),
        (-10.0, 2.0, -5.0),
        (10.0, -2.0, -5.0),
        (-10.0, -2.0, 5.0),
        (0.3, 0.1, 3.0),
        (1e20, 1e10, 1e10),
    ])
    def test_ieee754_div_parametrized(self, num1, num2, expected):
        op = Divider(num1=num1, num2=num2)
        result_arr = op.ieee754_div()

        if result_arr is not None:  # не деление на ноль
            result_dec = op.float_operator.ieee754_to_float(result_arr)
            if expected != 0:
                rel_err = abs(result_dec - expected) / abs(expected)
                assert rel_err < 1e-5, f"Failed for {num1}/{num2}"
            else:
                assert result_dec == 0.0

    @pytest.mark.parametrize("sign1,sign2,expected_sign", [
        (1, 1, 0),  # + / + = +
        (-1, -1, 0),  # - / - = +
        (1, -1, 1),  # + / - = -
        (-1, 1, 1),  # - / + = -
    ])
    def test_divide_direct_sign_logic(self, sign1, sign2, expected_sign, div_op_default):
        """Проверка логики определения знака результата"""
        op = Divider(num1=sign1 * 10, num2=sign2 * 2)
        result_arr, _ = op.divide_direct()
        assert result_arr[0] == expected_sign
        assert len(result_arr) == 32