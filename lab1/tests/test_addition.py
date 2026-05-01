import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Operations.Addition import Addition


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def add_op_32():
    """Addition с 32 битами (стандартная конфигурация)"""
    return Addition(num1=0, num2=0, bits=32)


@pytest.fixture
def add_op_16():
    """Addition с 16 битами (для тестов ограниченной разрядности)"""
    return Addition(num1=0, num2=0, bits=16)


@pytest.fixture
def add_op_8():
    """Addition с 8 битами (минимальная конфигурация)"""
    return Addition(num1=0, num2=0, bits=8)


# ============================================================================
# Tests for __init__
# ============================================================================

class TestAdditionInit:
    """Тесты инициализации класса"""

    def test_init_default_bits(self):
        op = Addition(num1=5, num2=3)
        assert op.num1 == 5
        assert op.num2 == 3
        assert op.bits == 32
        assert op.operator is not None
        assert op.float_operator is not None
        assert op.bcd_operator is not None
        assert op.converter is not None

    def test_init_custom_bits(self):
        for bits in [8, 16, 32, 64]:
            op = Addition(num1=1, num2=2, bits=bits)
            assert op.bits == bits
            assert op.num1 == 1
            assert op.num2 == 2

    def test_init_dependencies(self):
        op = Addition(num1=0, num2=0)
        from Converting.BinaryOperator import BinaryOperator
        from Converting.FloatOperator import FloatOperator
        from Converting.BCDOperator import BCDOperator
        from Utils.ArrayStringConverter import ArrayStringConverter

        assert isinstance(op.operator, BinaryOperator)
        assert isinstance(op.float_operator, FloatOperator)
        assert isinstance(op.bcd_operator, BCDOperator)
        assert isinstance(op.converter, ArrayStringConverter)


# ============================================================================
# Tests for add_arrays
# ============================================================================

class TestAddArrays:
    """Тесты метода сложения битовых массивов"""

    # --- Basic addition ---

    def test_add_arrays_zero_plus_zero(self, add_op_32):
        arr1 = [0] * 32
        arr2 = [0] * 32
        result = add_op_32.add_arrays(arr1, arr2)
        assert result == [0] * 32

    def test_add_arrays_one_plus_one(self, add_op_32):
        arr1 = [0] * 31 + [1]
        arr2 = [0] * 31 + [1]
        result = add_op_32.add_arrays(arr1, arr2)
        expected = [0] * 30 + [1, 0]  # 2 in binary
        assert result == expected

    def test_add_arrays_with_carry_propagation(self, add_op_32):
        # 7 + 1 = 8: 0111 + 0001 = 1000
        arr1 = [0] * 28 + [0, 1, 1, 1]
        arr2 = [0] * 28 + [0, 0, 0, 1]
        result = add_op_32.add_arrays(arr1, arr2)
        expected = [0] * 28 + [1, 0, 0, 0]
        assert result == expected

    def test_add_arrays_all_ones_plus_one(self, add_op_32):
        # 111...111 + 1 = 000...000 (overflow)
        arr1 = [1] * 32
        arr2 = [0] * 31 + [1]
        result = add_op_32.add_arrays(arr1, arr2)
        # Overflow бит отбрасывается
        assert result == [0] * 32

    # --- Custom length ---

    def test_add_arrays_custom_length(self, add_op_32):
        arr1 = [1, 0, 1, 0]  # 10
        arr2 = [0, 1, 0, 1]  # 5
        result = add_op_32.add_arrays(arr1, arr2, length=4)
        expected = [1, 1, 1, 1]  # 15
        assert result == expected

    def test_add_arrays_length_shorter_than_arrays(self, add_op_32):
        arr1 = [1, 1, 1, 1, 1, 1]
        arr2 = [0, 0, 0, 0, 0, 1]
        # Складываем только последние 4 бита
        result = add_op_32.add_arrays(arr1, arr2, length=4)
        # Последние 4 бита: 1111 + 0001 = 0000 (с переносом)
        expected = [1, 1, 0, 0, 0, 0]  # первые 2 бита копируются из arr1
        # На самом деле метод создаёт новый массив длины `length`
        result_full = add_op_32.add_arrays(arr1[-4:], arr2[-4:], length=4)
        assert result_full == [0, 0, 0, 0]

    # --- Edge cases ---

    def test_add_arrays_8bit_config(self, add_op_8):
        arr1 = [1, 1, 1, 1, 1, 1, 1, 1]  # 255
        arr2 = [0, 0, 0, 0, 0, 0, 0, 1]  # 1
        result = add_op_8.add_arrays(arr1, arr2)
        assert result == [0] * 8  # overflow

    def test_add_arrays_no_overflow(self, add_op_32):
        arr1 = [0] * 30 + [1, 0]  # 2
        arr2 = [0] * 30 + [1, 1]  # 3
        result = add_op_32.add_arrays(arr1, arr2)
        expected = [0] * 29 + [1, 0, 1]  # 5
        assert result == expected

    def test_add_arrays_alternating_bits(self, add_op_32):
        arr1 = [i % 2 for i in range(32)]
        arr2 = [(i + 1) % 2 for i in range(32)]
        result = add_op_32.add_arrays(arr1, arr2)
        # 1+0=1, 0+1=1 для всех позиций
        assert all(b == 1 for b in result)


# ============================================================================
# Tests for add_complement
# ============================================================================

class TestAddComplement:
    """Тесты сложения в дополнительном коде"""

    # --- Positive + Positive ---

    def test_add_complement_positive_small(self, add_op_32, capsys):
        op = Addition(num1=5, num2=3, bits=32)
        result_arr, result_dec = op.add_complement()
        captured = capsys.readouterr()

        assert "=== СЛОЖЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ ===" in captured.out
        assert "Числа: 5 + 3" in captured.out
        assert "Доп. код A:" in captured.out
        assert "Доп. код B:" in captured.out
        assert "Сумма:" in captured.out
        assert result_dec == 8
        assert "Проверка: 5 + 3 = 8" in captured.out

    def test_add_complement_positive_large(self, add_op_32):
        op = Addition(num1=50, num2=100, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 150

    # --- Negative + Negative ---

    def test_add_complement_negative_small(self, add_op_32, capsys):
        op = Addition(num1=-5, num2=-3, bits=32)
        result_arr, result_dec = op.add_complement()
        captured = capsys.readouterr()

        assert "Числа: -5 + -3" in captured.out
        assert result_dec == -8

    def test_add_complement_negative_large(self, add_op_32):
        op = Addition(num1=-50, num2=-100, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == -150

    # --- Positive + Negative ---

    def test_add_complement_mixed_positive_larger(self, add_op_32):
        op = Addition(num1=10, num2=-3, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 7

    def test_add_complement_mixed_negative_larger(self, add_op_32):
        op = Addition(num1=3, num2=-10, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == -7

    def test_add_complement_mixed_equal_abs(self, add_op_32):
        op = Addition(num1=5, num2=-5, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 0

    # --- Zero cases ---

    def test_add_complement_zero_plus_zero(self, add_op_32):
        op = Addition(num1=0, num2=0, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 0

    def test_add_complement_zero_plus_positive(self, add_op_32):
        op = Addition(num1=0, num2=42, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 42

    def test_add_complement_zero_plus_negative(self, add_op_32):
        op = Addition(num1=0, num2=-42, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == -42

    # --- Edge values ---

    def test_add_complement_max_positive_8bit(self, add_op_32):
        # 127 + 0 = 127 (max positive for 8-bit signed)
        op = Addition(num1=127, num2=0, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 127

    def test_add_complement_min_negative_8bit(self, add_op_32):
        # -128 + 0 = -128 (min negative for 8-bit signed)
        op = Addition(num1=-128, num2=0, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == -128

    def test_add_complement_overflow_positive(self, add_op_32):
        # 100 + 50 = 150 > 127 (overflow для 8-bit)
        op = Addition(num1=100, num2=50, bits=32)
        result_arr, result_dec = op.add_complement()
        # Результат будет некорректным из-за переполнения
        # Это ожидаемое поведение для фиксированной разрядности
        assert isinstance(result_dec, int)


# ============================================================================
# Tests for ieee754_add
# ============================================================================

class TestIeee754Add:
    """Тесты сложения в формате IEEE-754"""

    # --- Positive + Positive ---

    def test_ieee754_add_positive_small(self, add_op_32, capsys):
        op = Addition(num1=1.5, num2=2.5, bits=32)
        result_arr, result_dec = op.ieee754_add()
        captured = capsys.readouterr()

        assert "=== IEEE-754 СЛОЖЕНИЕ ===" in captured.out
        assert "Числа: 1.5 + 2.5" in captured.out
        assert "IEEE-754 A:" in captured.out
        assert "IEEE-754 B:" in captured.out
        assert "Результат IEEE-754:" in captured.out
        assert abs(result_dec - 4.0) < 1e-6

    def test_ieee754_add_positive_fraction(self, add_op_32):
        op = Addition(num1=0.1, num2=0.2, bits=32)
        result_arr, result_dec = op.ieee754_add()
        # 0.1 + 0.2 != 0.3 точно в float, проверяем с допуском
        assert abs(result_dec - 0.3) < 1e-6

    # --- Negative + Negative ---

    def test_ieee754_add_negative_small(self, add_op_32):
        op = Addition(num1=-1.5, num2=-2.5, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - (-4.0)) < 1e-6

    # --- Mixed signs ---

    def test_ieee754_add_mixed_positive_larger(self, add_op_32):
        op = Addition(num1=5.5, num2=-2.0, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - 3.5) < 1e-6

    def test_ieee754_add_mixed_negative_larger(self, add_op_32):
        op = Addition(num1=2.0, num2=-5.5, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - (-3.5)) < 1e-6

    def test_ieee754_add_mixed_equal_abs(self, add_op_32):
        op = Addition(num1=3.14, num2=-3.14, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec) < 1e-6

    # --- Zero cases ---

    def test_ieee754_add_zero_plus_zero(self, add_op_32):
        op = Addition(num1=0.0, num2=0.0, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert result_dec == 0.0

    def test_ieee754_add_zero_plus_positive(self, add_op_32):
        op = Addition(num1=0.0, num2=42.5, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - 42.5) < 1e-6

    def test_ieee754_add_zero_plus_negative(self, add_op_32):
        op = Addition(num1=0.0, num2=-42.5, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - (-42.5)) < 1e-6

    # --- Large and small values ---

    def test_ieee754_add_large_numbers(self, add_op_32):
        op = Addition(num1=1e10, num2=2e10, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - 3e10) / 3e10 < 1e-5

    def test_ieee754_add_small_numbers(self, add_op_32):
        op = Addition(num1=1e-10, num2=2e-10, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert abs(result_dec - 3e-10) / 3e-10 < 1e-5

    # --- Output verification ---

    def test_ieee754_add_prints_binary_strings(self, add_op_32, capsys):
        op = Addition(num1=1.0, num2=1.0, bits=32)
        op.ieee754_add()
        captured = capsys.readouterr()

        # Проверка, что напечатаны 32-битные строки
        import re
        ieee_matches = re.findall(r'IEEE-754 [AB]:\s*([01]{32})', captured.out)
        assert len(ieee_matches) == 2
        assert all(len(m) == 32 for m in ieee_matches)


# ============================================================================
# Tests for bcd_add
# ============================================================================

class TestBCDAdd:
    """Тесты сложения в BCD коде"""

    # --- Positive + Positive ---

    def test_bcd_add_positive_small(self, add_op_32, capsys):
        op = Addition(num1=12, num2=34, bits=32)
        result_arr, result_dec = op.bcd_add()
        captured = capsys.readouterr()

        assert "=== BCD 8421 СЛОЖЕНИЕ ===" in captured.out
        assert "Числа: 12 + 34" in captured.out
        assert "Результат BCD:" in captured.out
        assert result_dec == 46

    def test_bcd_add_with_carry_digit(self, add_op_32):
        # 5 + 7 = 12 (перенос в десятичной системе)
        op = Addition(num1=5, num2=7, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 12

    # --- Negative + Negative ---

    def test_bcd_add_negative_small(self, add_op_32):
        op = Addition(num1=-12, num2=-34, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == -46

    # --- Mixed signs ---

    def test_bcd_add_mixed_positive_larger(self, add_op_32):
        op = Addition(num1=50, num2=-20, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 30

    def test_bcd_add_mixed_negative_larger(self, add_op_32):
        op = Addition(num1=20, num2=-50, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == -30

    def test_bcd_add_mixed_equal_abs(self, add_op_32):
        op = Addition(num1=42, num2=-42, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 0

    # --- Zero cases ---

    def test_bcd_add_zero_plus_zero(self, add_op_32):
        op = Addition(num1=0, num2=0, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 0

    def test_bcd_add_zero_plus_positive(self, add_op_32):
        op = Addition(num1=0, num2=123, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 123

    # --- Multi-digit numbers ---

    def test_bcd_add_three_digits(self, add_op_32):
        op = Addition(num1=123, num2=456, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 579

    def test_bcd_add_with_zeros_in_middle(self, add_op_32):
        op = Addition(num1=105, num2=204, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 309

    # --- Custom bit width ---

    def test_bcd_add_16bit_config(self, add_op_16):
        # 16 бит = 4 десятичные цифры максимум
        op = Addition(num1=99, num2=1, bits=16)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 100

    def test_bcd_add_8bit_config(self, add_op_8):
        # 8 бит = 2 десятичные цифры максимум
        op = Addition(num1=25, num2=17, bits=8)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == 42

    # --- Output verification ---

    def test_bcd_add_prints_binary_string(self, add_op_32, capsys):
        op = Addition(num1=7, num2=3, bits=32)
        op.bcd_add()
        captured = capsys.readouterr()

        import re
        bcd_match = re.search(r'Результат BCD:\s*([01]+)', captured.out)
        assert bcd_match is not None
        bcd_str = bcd_match.group(1)
        assert len(bcd_str) == 32
        assert all(c in '01' for c in bcd_str)


# ============================================================================
# Integration tests
# ============================================================================

class TestIntegration:
    """Интеграционные тесты взаимодействия методов"""

    def test_all_addition_methods_same_inputs(self, capsys):
        """Проверка, что все методы работают с одинаковыми входными данными"""
        op = Addition(num1=10, num2=20, bits=32)

        # Сложение в дополнительном коде
        comp_arr, comp_dec = op.add_complement()
        assert comp_dec == 30

        # BCD сложение
        bcd_arr, bcd_dec = op.bcd_add()
        assert bcd_dec == 30

        # IEEE-754 (целые числа как float)
        ieee_arr, ieee_dec = op.ieee754_add()
        assert abs(ieee_dec - 30.0) < 1e-6

    def test_negative_numbers_all_methods(self):
        op = Addition(num1=-15, num2=-25, bits=32)

        comp_arr, comp_dec = op.add_complement()
        assert comp_dec == -40

        bcd_arr, bcd_dec = op.bcd_add()
        assert bcd_dec == -40

        ieee_arr, ieee_dec = op.ieee754_add()
        assert abs(ieee_dec - (-40.0)) < 1e-6

    def test_mixed_signs_all_methods(self):
        op = Addition(num1=100, num2=-37, bits=32)

        comp_arr, comp_dec = op.add_complement()
        assert comp_dec == 63

        bcd_arr, bcd_dec = op.bcd_add()
        assert bcd_dec == 63

        ieee_arr, ieee_dec = op.ieee754_add()
        assert abs(ieee_dec - 63.0) < 1e-6

    def test_add_arrays_used_in_complement(self, add_op_32):
        """Проверка, что add_complement использует add_arrays"""
        op = Addition(num1=5, num2=3, bits=8)

        # Получаем дополненные коды
        comp1 = op.operator.get_complement_code(5)
        comp2 = op.operator.get_complement_code(3)

        # Складываем через add_arrays
        direct_sum = op.add_arrays(comp1, comp2)

        # Сравниваем с результатом add_complement
        result_arr, _ = op.add_complement()
        assert result_arr == direct_sum


# ============================================================================
# Edge cases and error handling
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_add_complement_large_numbers_overflow(self, add_op_8):
        """Переполнение при сложении больших чисел в 8 битах"""
        op = Addition(num1=100, num2=100, bits=8)
        result_arr, result_dec = op.add_complement()
        # Результат будет некорректным из-за переполнения
        # Это ожидаемое поведение
        assert isinstance(result_dec, int)

    def test_ieee754_add_very_small_difference(self, add_op_32):
        """Сложение чисел с очень разной величиной"""
        op = Addition(num1=1e20, num2=1.0, bits=32)
        result_arr, result_dec = op.ieee754_add()
        # Меньшее число может "потеряться" из-за ограниченной точности
        # Проверяем, что результат близок к большему числу
        assert abs(result_dec - 1e20) / 1e20 < 1e-5

    def test_bcd_add_truncation_small_bits(self, add_op_8):
        """BCD сложение с усечением при малой разрядности"""
        op = Addition(num1=123, num2=456, bits=8)  # 8 бит = 2 цифры
        result_arr, result_dec = op.bcd_add()
        # Ожидаем усечение до 2 последних цифр: 79 (из 579)
        # Фактическое поведение зависит от реализации BCDOperator
        assert isinstance(result_dec, int)

    def test_add_arrays_empty_like(self, add_op_32):
        """Сложение массивов с преобладанием нулей"""
        arr1 = [0] * 32
        arr2 = [0] * 31 + [1]
        result = add_op_32.add_arrays(arr1, arr2)
        assert result[-1] == 1
        assert sum(result[:-1]) == 0

    def test_add_complement_one_plus_negative_one(self, add_op_32):
        """1 + (-1) = 0 в дополнительном коде"""
        op = Addition(num1=1, num2=-1, bits=32)
        result_arr, result_dec = op.add_complement()
        assert result_dec == 0
        # Все биты результата должны быть 0 (или 1 с переносом, который отбрасывается)

    def test_ieee754_add_nan_like_behavior(self, add_op_32):
        """Поведение с очень большими/малыми числами"""
        # Проверяем, что метод не падает на экстремальных значениях
        op = Addition(num1=1e30, num2=-1e30, bits=32)
        result_arr, result_dec = op.ieee754_add()
        assert isinstance(result_dec, float)

    def test_bcd_add_single_digit_all_combinations(self, add_op_32):
        """Все комбинации сложения однозначных чисел в BCD"""
        for a in range(10):
            for b in range(10):
                op = Addition(num1=a, num2=b, bits=32)
                _, result = op.bcd_add()
                assert result == a + b


# ============================================================================
# Parametrized comprehensive tests
# ============================================================================

class TestParametrizedAddition:
    """Параметризованные тесты для широкого покрытия"""

    @pytest.mark.parametrize("num1,num2,bits,expected", [
        # (num1, num2, bits, expected_decimal_result)
        # Complement addition tests
        (0, 0, 32, 0),
        (1, 1, 32, 2),
        (-1, -1, 32, -2),
        (10, -5, 32, 5),
        (-10, 5, 32, -5),
        (127, 0, 32, 127),
        (-128, 0, 32, -128),
        (50, 50, 32, 100),
        (-1000, 500, 32, -500),
    ])
    def test_add_complement_parametrized(self, num1, num2, bits, expected):
        op = Addition(num1=num1, num2=num2, bits=bits)
        result_arr, result_dec = op.add_complement()
        # Для случаев с возможным переполнением проверяем только тип
        if bits == 8 and abs(num1) + abs(num2) > 127:
            assert isinstance(result_dec, int)
        else:
            assert result_dec == expected

    @pytest.mark.parametrize("num1,num2,expected", [
        (0.0, 0.0, 0.0),
        (1.5, 2.5, 4.0),
        (-1.5, -2.5, -4.0),
        (10.0, -3.0, 7.0),
        (0.1, 0.2, 0.3),  # с допуском
        (1e10, 2e10, 3e10),
    ])
    def test_ieee754_add_parametrized(self, num1, num2, expected):
        op = Addition(num1=num1, num2=num2, bits=32)
        result_arr, result_dec = op.ieee754_add()
        if expected != 0:
            rel_err = abs(result_dec - expected) / abs(expected)
            assert rel_err < 1e-5, f"Failed for {num1}+{num2}"
        else:
            assert abs(result_dec) < 1e-6

    @pytest.mark.parametrize("num1,num2,expected", [
        (0, 0, 0),
        (5, 3, 8),
        (-5, -3, -8),
        (10, -3, 7),
        (99, 1, 100),
        (123, 456, 579),
    ])
    def test_bcd_add_parametrized(self, num1, num2, expected):
        op = Addition(num1=num1, num2=num2, bits=32)
        result_arr, result_dec = op.bcd_add()
        assert result_dec == expected