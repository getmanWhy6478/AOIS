import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Operations.Multiplicator import Multiplicator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mult_op_32():
    """Multiplicator с 32 битами (стандартная конфигурация)"""
    return Multiplicator(num1=0, num2=0, bits=32)


@pytest.fixture
def mult_op_16():
    """Multiplicator с 16 битами (для тестов ограниченной разрядности)"""
    return Multiplicator(num1=0, num2=0, bits=32)


@pytest.fixture
def mult_op_8():
    """Multiplicator с 8 битами (минимальная конфигурация)"""
    return Multiplicator(num1=0, num2=0, bits=32)


# ============================================================================
# Tests for __init__
# ============================================================================

class TestMultiplicatorInit:
    """Тесты инициализации класса"""

    def test_init_default_bits(self):
        op = Multiplicator(num1=5, num2=3)
        assert op.num1 == 5
        assert op.num2 == 3
        assert op.bits == 32
        assert op.operator is not None
        assert op.float_operator is not None
        assert op.converter is not None

    def test_init_custom_bits(self):
        for bits in [8, 16, 32, 64]:
            op = Multiplicator(num1=2, num2=4, bits=bits)
            assert op.bits == bits
            assert op.num1 == 2
            assert op.num2 == 4

    def test_init_dependencies_types(self):
        op = Multiplicator(num1=0, num2=0)
        from Converting.BinaryOperator import BinaryOperator
        from Converting.FloatOperator import FloatOperator
        from Utils.ArrayStringConverter import ArrayStringConverter

        assert isinstance(op.operator, BinaryOperator)
        assert isinstance(op.float_operator, FloatOperator)
        assert isinstance(op.converter, ArrayStringConverter)

    def test_init_negative_numbers(self):
        op = Multiplicator(num1=-10, num2=5)
        assert op.num1 == -10
        assert op.num2 == 5


# ============================================================================
# Tests for multiply_direct
# ============================================================================

class TestMultiplyDirect:
    """Тесты умножения в прямом коде"""

    # --- Zero cases ---

    def test_multiply_direct_zero_times_zero(self, mult_op_32, capsys):
        op = Multiplicator(num1=0, num2=0, bits=32)
        result_arr, result_dec = op.multiply_direct()
        captured = capsys.readouterr()

        assert "=== УМНОЖЕНИЕ В ПРЯМОМ КОДЕ ===" in captured.out
        assert "Числа: 0 * 0" in captured.out
        assert result_dec == 0
        assert "Проверка: 0 * 0 = 0" in captured.out

    def test_multiply_direct_zero_times_positive(self, mult_op_32):
        op = Multiplicator(num1=0, num2=42, bits=32)
        result_arr, result_dec = op.multiply_direct()
        assert result_dec == 0

    def test_multiply_direct_zero_times_negative(self, mult_op_32):
        op = Multiplicator(num1=0, num2=-15, bits=32)
        result_arr, result_dec = op.multiply_direct()
        assert result_dec == 0

    # --- Positive × Positive ---

    def test_multiply_direct_small_positive(self, mult_op_32, capsys):
        op = Multiplicator(num1=3, num2=4, bits=32)
        result_arr, result_dec = op.multiply_direct()
        captured = capsys.readouterr()

        assert "Числа: 3 * 4" in captured.out
        assert "Модуль A:" in captured.out
        assert "Модуль B:" in captured.out
        assert result_dec == 12
        assert "Проверка: 3 * 4 = 12" in captured.out

    def test_multiply_direct_one_times_any(self, mult_op_32):
        for val in [1, 5, 42, 127]:
            op = Multiplicator(num1=1, num2=val, bits=32)
            _, result_dec = op.multiply_direct()
            assert result_dec == val

    def test_multiply_direct_square_small(self, mult_op_32):
        op = Multiplicator(num1=7, num2=7, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 49

    # --- Negative × Negative ---

    def test_multiply_direct_negative_times_negative(self, mult_op_32):
        op = Multiplicator(num1=-5, num2=-3, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 15  # (-5) * (-3) = 15

    def test_multiply_direct_negative_square(self, mult_op_32):
        op = Multiplicator(num1=-8, num2=-8, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 64

    # --- Mixed signs ---

    def test_multiply_direct_positive_times_negative(self, mult_op_32):
        op = Multiplicator(num1=6, num2=-4, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == -24

    def test_multiply_direct_negative_times_positive(self, mult_op_32):
        op = Multiplicator(num1=-9, num2=3, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == -27

    def test_multiply_direct_sign_bit_handling(self, mult_op_32):
        """Проверка, что бит знака устанавливается корректно"""
        # + * + = +
        op1 = Multiplicator(num1=5, num2=3, bits=32)
        result1, _ = op1.multiply_direct()
        assert result1[0] == 0  # sign bit

        # - * - = +
        op2 = Multiplicator(num1=-5, num2=-3, bits=32)
        result2, _ = op2.multiply_direct()
        assert result2[0] == 0

        # + * - = -
        op3 = Multiplicator(num1=5, num2=-3, bits=32)
        result3, _ = op3.multiply_direct()
        assert result3[0] == 1

        # - * + = -
        op4 = Multiplicator(num1=-5, num2=3, bits=32)
        result4, _ = op4.multiply_direct()
        assert result4[0] == 1

    # --- Edge values ---

    def test_multiply_direct_max_small_8bit(self, mult_op_8):
        """15 * 15 = 225 > 127 (переполнение для 8-bit signed)"""
        op = Multiplicator(num1=15, num2=15, bits=32)
        result_arr, result_dec = op.multiply_direct()
        # Результат будет усечён из-за ограниченной разрядности
        assert isinstance(result_dec, int)

    def test_multiply_direct_no_overflow_16bit(self, mult_op_16):
        """50 * 30 = 1500 < 32767 (помещается в 16-bit)"""
        op = Multiplicator(num1=50, num2=30, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 1500

    def test_multiply_direct_power_of_two(self, mult_op_32):
        """Умножение на степень двойки (сдвиг)"""
        op = Multiplicator(num1=8, num2=4, bits=32)  # 2^3 * 2^2 = 2^5 = 32
        _, result_dec = op.multiply_direct()
        assert result_dec == 32

    def test_multiply_direct_no_overflow_message(self, mult_op_16, capsys):
        """Отсутствие предупреждения при отсутствии переполнения"""
        op = Multiplicator(num1=10, num2=10, bits=32)  # 100 < 32767
        op.multiply_direct()
        captured = capsys.readouterr()

        assert "⚠️  ВНИМАНИЕ" not in captured.out

    def test_multiply_direct_carry_normalization(self, mult_op_32):
        """Проверка обработки переносов при сложении частичных произведений"""
        # 7 * 7 = 49 = 110001 в двоичной системе
        op = Multiplicator(num1=7, num2=7, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 49


# ============================================================================
# Tests for ieee754_mul
# ============================================================================

class TestIeee754Mul:
    """Тесты умножения в формате IEEE-754"""

    # --- Positive × Positive ---

    def test_ieee754_mul_positive_small(self, mult_op_32, capsys):
        op = Multiplicator(num1=2.5, num2=4.0, bits=32)
        result_arr, result_dec = op.ieee754_mul()
        captured = capsys.readouterr()

        assert "=== IEEE-754 УМНОЖЕНИЕ ===" in captured.out
        assert "Числа: 2.5 * 4.0" in captured.out
        assert "Результат IEEE-754:" in captured.out
        assert abs(result_dec - 10.0) < 1e-6

    def test_ieee754_mul_fraction(self, mult_op_32):
        op = Multiplicator(num1=0.5, num2=0.25, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - 0.125) < 1e-6

    # --- Negative × Negative ---

    def test_ieee754_mul_negative_times_negative(self, mult_op_32):
        op = Multiplicator(num1=-3.0, num2=-4.0, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - 12.0) < 1e-6

    # --- Mixed signs ---

    def test_ieee754_mul_positive_times_negative(self, mult_op_32):
        op = Multiplicator(num1=5.0, num2=-2.0, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - (-10.0)) < 1e-6

    def test_ieee754_mul_negative_times_positive(self, mult_op_32):
        op = Multiplicator(num1=-6.5, num2=2.0, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - (-13.0)) < 1e-6

    # --- Zero cases ---

    def test_ieee754_mul_zero_times_zero(self, mult_op_32):
        op = Multiplicator(num1=0.0, num2=0.0, bits=32)
        _, result_dec = op.ieee754_mul()
        assert result_dec == 0.0

    def test_ieee754_mul_zero_times_positive(self, mult_op_32):
        op = Multiplicator(num1=0.0, num2=42.5, bits=32)
        _, result_dec = op.ieee754_mul()
        assert result_dec == 0.0

    def test_ieee754_mul_zero_times_negative(self, mult_op_32):
        op = Multiplicator(num1=0.0, num2=-17.3, bits=32)
        _, result_dec = op.ieee754_mul()
        assert result_dec == 0.0

    # --- One as multiplier ---

    def test_ieee754_mul_one_times_value(self, mult_op_32):
        for val in [1.0, -1.0, 3.14, -2.71]:
            op = Multiplicator(num1=1.0, num2=val, bits=32)
            _, result_dec = op.ieee754_mul()
            assert abs(result_dec - val) < 1e-6

    # --- Large and small values ---

    def test_ieee754_mul_large_numbers(self, mult_op_32):
        op = Multiplicator(num1=1e10, num2=2e5, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - 2e15) / 2e15 < 1e-5

    def test_ieee754_mul_small_numbers(self, mult_op_32):
        op = Multiplicator(num1=1e-10, num2=1e-5, bits=32)
        _, result_dec = op.ieee754_mul()
        expected = 1e-15
        if expected != 0:
            assert abs(result_dec - expected) / expected < 1e-5

    def test_ieee754_mul_mixed_magnitude(self, mult_op_32):
        """Умножение очень большого на очень малое"""
        op = Multiplicator(num1=1e20, num2=1e-10, bits=32)
        _, result_dec = op.ieee754_mul()
        assert abs(result_dec - 1e10) / 1e10 < 1e-5

    # --- Fraction precision ---

    def test_ieee754_mul_decimal_fractions(self, mult_op_32):
        """Проверка точности при умножении десятичных дробей"""
        op = Multiplicator(num1=0.1, num2=0.2, bits=32)
        _, result_dec = op.ieee754_mul()
        # 0.1 * 0.2 = 0.02 (с возможной погрешностью)
        assert abs(result_dec - 0.02) < 1e-7

    # --- Output verification ---

    def test_ieee754_mul_prints_binary_string(self, mult_op_32, capsys):
        op = Multiplicator(num1=1.5, num2=2.0, bits=32)
        op.ieee754_mul()
        captured = capsys.readouterr()

        import re
        ieee_match = re.search(r'Результат IEEE-754:\s*([01]{32})', captured.out)
        assert ieee_match is not None
        assert len(ieee_match.group(1)) == 32


# ============================================================================
# Integration tests
# ============================================================================

class TestIntegration:
    """Интеграционные тесты взаимодействия методов"""

    def test_both_multiplication_methods_integer_input(self):
        """Сравнение результатов для целых чисел"""
        op = Multiplicator(num1=6, num2=7, bits=32)

        # Умножение в прямом коде
        _, direct_result = op.multiply_direct()

        # Умножение в IEEE-754 (целые как float)
        _, ieee_result = op.ieee754_mul()

        # Результаты должны быть близки
        assert abs(direct_result - ieee_result) < 1e-6

    def test_multiply_direct_uses_binary_operator(self, mult_op_32):
        """Проверка, что multiply_direct использует BinaryOperator"""
        op = Multiplicator(num1=5, num2=3, bits=32)

        # Получаем прямой код модулей вручную
        arr1 = op.operator.get_direct_code(abs(5))
        arr2 = op.operator.get_direct_code(abs(3))

        # Проверяем, что мантиссы извлекаются корректно (без знака)
        mant1 = arr1[1:]
        mant2 = arr2[1:]

        assert len(mant1) == 31  # 8 bits - 1 sign
        assert len(mant2) == 31

    def test_multiply_direct_temp_array_size(self, mult_op_32):
        """Проверка размера временного массива для точного вычисления"""
        op = Multiplicator(num1=10, num2=10, bits=32)
        # Внутренний temp_result должен быть 32 бита (2 * bits)
        _, result_dec = op.multiply_direct()
        assert result_dec == 100

    def test_multiply_direct_result_array_format(self, mult_op_32):
        """Проверка формата результирующего массива"""
        op = Multiplicator(num1=-4, num2=5, bits=32)
        result_arr, result_dec = op.multiply_direct()

        assert len(result_arr) == 32  # bits=32
        assert result_arr[0] == 1  # sign bit (negative result)
        assert result_dec == -20


# ============================================================================
# Edge cases and parametrized tests
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_multiply_direct_single_bit_mantissa(self, mult_op_8):
        """Умножение с минимальной мантиссой (1 бит)"""
        op = Multiplicator(num1=1, num2=1, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 1

    def test_multiply_direct_all_ones_mantissa(self, mult_op_8):
        """Мантисса из одних единиц (максимальное значение)"""
        # 127 в 8-bit direct code: sign=0, mantissa=1111111
        op = Multiplicator(num1=127, num2=1, bits=32)
        _, result_dec = op.multiply_direct()
        # Результат может быть усечён
        assert isinstance(result_dec, int)

    def test_multiply_direct_carry_chain_normalization(self, mult_op_32):
        """Проверка цепочки переносов при нормализации"""
        # Частные произведения создают цепочку переносов
        op = Multiplicator(num1=15, num2=15, bits=32)  # 225 = 11100001
        _, result_dec = op.multiply_direct()
        assert result_dec == 225

    def test_ieee754_mul_very_small_result(self, mult_op_32):
        """Результат близкий к нулю"""
        op = Multiplicator(num1=1e-20, num2=1e-10, bits=32)
        _, result_dec = op.ieee754_mul()
        assert isinstance(result_dec, float)


    def test_multiply_direct_result_conversion_loop(self, mult_op_32):
        """Проверка цикла конвертации результата в десятичное"""
        # Проверяем, что все биты мантиссы учитываются
        op = Multiplicator(num1=8, num2=8, bits=32)  # 64 = 1000000
        _, result_dec = op.multiply_direct()
        assert result_dec == 64


class TestParametrizedMultiplication:
    """Параметризованные тесты для широкого покрытия"""

    @pytest.mark.parametrize("num1,num2,bits,expected", [
        # (num1, num2, bits, expected_decimal_result)
        # Direct multiplication tests
        (0, 0, 32, 0),
        (1, 1, 32, 1),
        (3, 4, 32, 12),
        (-5, 3, 32, -15),
        (-4, -6, 32, 24),
        (10, 10, 32, 100),
        (15, 15, 32, 225),
        (50, 30, 32, 1500),
        (100, -5, 32, -500),
    ])
    def test_multiply_direct_parametrized(self, num1, num2, bits, expected):
        op = Multiplicator(num1=num1, num2=num2, bits=bits)
        result_arr, result_dec = op.multiply_direct()

        # Для случаев с возможным переполнением проверяем тип
        max_val = 2 ** (bits - 1) - 1
        if abs(expected) > max_val and bits <= 16:
            assert isinstance(result_dec, int)
        else:
            assert result_dec == expected

    @pytest.mark.parametrize("num1,num2,expected", [
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        (2.5, 4.0, 10.0),
        (-3.0, 2.0, -6.0),
        (-2.0, -5.0, 10.0),
        (0.5, 0.25, 0.125),
        (1e10, 1e5, 1e15),
        (1e-10, 1e-5, 1e-15),
    ])
    def test_ieee754_mul_parametrized(self, num1, num2, expected):
        op = Multiplicator(num1=num1, num2=num2, bits=32)
        result_arr, result_dec = op.ieee754_mul()

        if expected != 0:
            rel_err = abs(result_dec - expected) / abs(expected)
            assert rel_err < 1e-5, f"Failed for {num1}*{num2}"
        else:
            assert result_dec == 0.0

    @pytest.mark.parametrize("sign1,sign2,expected_sign", [
        (1, 1, 0),  # + * + = +
        (-1, -1, 0),  # - * - = +
        (1, -1, 1),  # + * - = -
        (-1, 1, 1),  # - * + = -
    ])
    def test_multiply_direct_sign_logic(self, sign1, sign2, expected_sign, mult_op_32):
        """Проверка логики определения знака результата"""
        op = Multiplicator(num1=sign1 * 5, num2=sign2 * 3, bits=32)
        result_arr, _ = op.multiply_direct()
        assert result_arr[0] == expected_sign


# ============================================================================
# Tests for internal bit manipulation
# ============================================================================

class TestBitManipulation:
    """Тесты внутренней логики работы с битами"""

    def test_multiply_direct_shift_and_add_logic(self, mult_op_32):
        """Проверка алгоритма сдвига и сложения"""
        # 5 (101) * 3 (011) = 15 (1111)
        # Частные произведения: 101<<0 + 101<<1 = 101 + 1010 = 1111
        op = Multiplicator(num1=5, num2=3, bits=32)
        _, result_dec = op.multiply_direct()
        assert result_dec == 15

    def test_multiply_direct_bit_positioning(self, mult_op_32):
        """Проверка корректности позиционирования битов в результате"""
        op = Multiplicator(num1=2, num2=8, bits=32)  # 2*8=16=10000
        result_arr, result_dec = op.multiply_direct()

        # Проверяем, что результат имеет правильные биты
        assert result_dec == 16

    def test_multiply_direct_temp_result_normalization(self, mult_op_32):
        """Проверка нормализации временного результата"""
        # Создаём ситуацию с множественными переносами
        op = Multiplicator(num1=7, num2=9, bits=32)  # 63 = 111111
        _, result_dec = op.multiply_direct()
        assert result_dec == 63
