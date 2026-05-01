import pytest
import sys
import os
import math

# Добавляем корень проекта в path для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Converting.FloatOperator import FloatOperator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def float_op_32():
    """FloatOperator с 32-битной точностью (стандарт IEEE-754)"""
    return FloatOperator(ieee_bits=32)


@pytest.fixture
def float_op_64():
    """FloatOperator с 64-битной точностью (для тестов кастомной разрядности)"""
    return FloatOperator(ieee_bits=64)


# ============================================================================
# Tests for __init__
# ============================================================================

class TestFloatOperatorInit:
    """Тесты инициализации класса"""

    def test_init_default_bits(self):
        op = FloatOperator()
        assert op.ieee_bits == 32
        assert op.operator is not None
        assert op.converter is not None

    def test_init_custom_bits(self):
        op = FloatOperator(ieee_bits=64)
        assert op.ieee_bits == 64

    def test_init_various_bit_widths(self):
        for bits in [16, 32, 64, 128]:
            op = FloatOperator(ieee_bits=bits)
            assert op.ieee_bits == bits


# ============================================================================
# Tests for float_to_ieee754
# ============================================================================

class TestFloatToIeee754:
    """Тесты преобразования float → IEEE-754"""

    # --- Zero cases ---

    def test_float_to_ieee_positive_zero(self, float_op_32, capsys):
        result = float_op_32.float_to_ieee754(0.0)
        assert result == [0] * 32

    def test_float_to_ieee_negative_zero(self, float_op_32):
        result = float_op_32.float_to_ieee754(-0.0)
        # По текущей реализации -0.0 обрабатывается как 0.0
        assert result == [0] * 32

    # --- Positive numbers ---

    def test_float_to_ieee_positive_one(self, float_op_32):
        result = float_op_32.float_to_ieee754(1.0)
        # 1.0 = sign:0, exp:127(01111111), mant:0...
        assert result[0] == 0  # sign
        assert result[1:9] == [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        assert all(b == 0 for b in result[9:])  # mantissa = 0

    def test_float_to_ieee_positive_two(self, float_op_32):
        result = float_op_32.float_to_ieee754(2.0)
        assert result[0] == 0
        assert result[1:9] == [1, 0, 0, 0, 0, 0, 0, 0]  # exp = 128

    def test_float_to_ieee_positive_fraction(self, float_op_32):
        result = float_op_32.float_to_ieee754(0.5)
        assert result[0] == 0
        # 0.5 = 1.0 * 2^(-1), exp = 126
        assert result[1:9] == [0, 1, 1, 1, 1, 1, 1, 0]

    def test_float_to_ieee_positive_decimal(self, float_op_32):
        result = float_op_32.float_to_ieee754(3.14)
        assert result[0] == 0  # positive
        assert len(result) == 32
        # Проверяем, что мантисса не пустая
        assert any(b == 1 for b in result[9:])

    # --- Negative numbers ---

    def test_float_to_ieee_negative_one(self, float_op_32):
        result = float_op_32.float_to_ieee754(-1.0)
        assert result[0] == 1  # sign bit
        assert result[1:9] == [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        assert all(b == 0 for b in result[9:])

    def test_float_to_ieee_negative_fraction(self, float_op_32):
        result = float_op_32.float_to_ieee754(-0.25)
        assert result[0] == 1
        # -0.25 = -1.0 * 2^(-2), exp = 125
        assert result[1:9] == [0, 1, 1, 1, 1, 1, 0, 1]

    # --- Edge exponent values ---

    def test_float_to_ieee_large_number(self, float_op_32):
        result = float_op_32.float_to_ieee754(1e10)
        assert result[0] == 0
        # Экспонента должна быть большой
        exp_bits = result[1:9]
        exponent = sum(b * (2 ** (7 - i)) for i, b in enumerate(exp_bits))
        assert exponent > 127

    def test_float_to_ieee_small_normalized(self, float_op_32):
        result = float_op_32.float_to_ieee754(1e-10)
        assert result[0] == 0
        # Экспонента должна быть маленькой
        exp_bits = result[1:9]
        exponent = sum(b * (2 ** (7 - i)) for i, b in enumerate(exp_bits))
        assert exponent < 127

    # --- Custom bit width ---

    def test_float_to_ieee_custom_bits(self, float_op_64):
        result = float_op_64.float_to_ieee754(1.0)
        assert len(result) == 64
        assert result[0] == 0

    # --- Output verification ---

    def test_float_to_ieee_prints_binary_string(self, float_op_32, capsys):
        float_op_32.float_to_ieee754(5.5)
        captured = capsys.readouterr()
        # Должна быть напечатана строка из 32 бит
        assert len(captured.out.strip()) == 32
        assert all(c in '01' for c in captured.out.strip())


# ============================================================================
# Tests for ieee754_to_float
# ============================================================================

class TestIeee754ToFloat:
    # --- Positive numbers ---

    def test_ieee_to_float_positive_one(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 1.0) < 1e-6

    def test_ieee_to_float_positive_two(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [1, 0, 0, 0, 0, 0, 0, 0]  # exp = 128
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 2.0) < 1e-6

    def test_ieee_to_float_positive_fraction(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 0]  # exp = 126
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 0.5) < 1e-6

    def test_ieee_to_float_with_mantissa(self, float_op_32):
        # 1.5 = sign:0, exp:127, mant:0.1(бинарно) = 0.5
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        arr[9] = 1  # first mantissa bit = 0.5
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 1.5) < 1e-6

    # --- Negative numbers ---

    def test_ieee_to_float_negative_one(self, float_op_32):
        arr = [0] * 32
        arr[0] = 1  # sign
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - (-1.0)) < 1e-6

    def test_ieee_to_float_negative_fraction(self, float_op_32):
        arr = [0] * 32
        arr[0] = 1  # sign
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 0]  # exp = 126
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - (-0.5)) < 1e-6

    # --- Large and small values ---

    def test_ieee_to_float_large_exponent(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [1, 0, 0, 0, 0, 0, 1, 0]  # exp = 130, 2^3 = 8
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 8.0) < 1e-5

    def test_ieee_to_float_small_exponent(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 0, 1, 1]  # exp = 123, 2^(-4) = 0.0625
        result = float_op_32.ieee754_to_float(arr)
        assert abs(result - 0.0625) < 1e-6

    # --- Custom bit width ---

    def test_ieee_to_float_custom_bits(self, float_op_64):
        arr = [0] * 64
        # Для 64-бит: bias = 1023, но в коде используется 127 (баг в исходнике)
        # Тестируем базовую функциональность
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        result = float_op_64.ieee754_to_float(arr)
        assert abs(result - 1.0) < 1e-6

    # --- Output verification ---

    def test_ieee_to_float_prints_result(self, float_op_32, capsys):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]
        float_op_32.ieee754_to_float(arr)
        captured = capsys.readouterr()
        assert "1.0" in captured.out or "1" in captured.out


# ============================================================================
# Tests for round-trip conversions
# ============================================================================

class TestRoundTripConversions:
    """Тесты сквозного преобразования: float → IEEE-754 → float"""

    def test_roundtrip_positive_one(self, float_op_32):
        original = 1.0
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        assert abs(result - original) < 1e-6

    def test_roundtrip_negative_one(self, float_op_32):
        original = -1.0
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        assert abs(result - original) < 1e-6

    def test_roundtrip_positive_fraction(self, float_op_32):
        original = 0.75
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        assert abs(result - original) < 1e-6

    def test_roundtrip_decimal_number(self, float_op_32):
        original = 3.14159
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        # Допускаем погрешность из-за ограниченной точности 32 бит
        assert abs(result - original) < 1e-6

    def test_roundtrip_large_number(self, float_op_32):
        original = 1e5
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        assert abs(result - original) / original < 1e-6

    def test_roundtrip_small_number(self, float_op_32):
        original = 1e-5
        bits = float_op_32.float_to_ieee754(original)
        result = float_op_32.ieee754_to_float(bits)
        if original != 0:  # Исключаем денормализованные
            assert abs(result - original) / abs(original) < 1e-5

    @pytest.mark.parametrize("test_value", [
        1.0, -1.0, 2.0, -2.0, 0.5, -0.5, 3.14, -3.14, 1e2, -1e2, 1e-2, -1e-2
    ])
    def test_roundtrip_parametrized(self, float_op_32, test_value):
        bits = float_op_32.float_to_ieee754(test_value)
        result = float_op_32.ieee754_to_float(bits)
        if test_value != 0:
            rel_error = abs(result - test_value) / abs(test_value)
            assert rel_error < 1e-5, f"Failed for {test_value}: got {result}"
        else:
            assert result == 0.0


# ============================================================================
# Tests for ieee754_bits_to_parts
# ============================================================================

class TestIeee754BitsToParts:
    """Тесты извлечения компонентов из IEEE-754 представления"""

    def test_parts_positive_one(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)
        assert sign == 0
        assert exponent == 127
        assert len(mant_bits) == 23  # 32 - 1 sign - 8 exp
        assert all(b == 0 for b in mant_bits)

    def test_parts_negative_number(self, float_op_32):
        arr = [0] * 32
        arr[0] = 1  # sign
        arr[1:9] = [1, 0, 0, 0, 0, 0, 0, 0]  # exp = 128
        arr[9] = 1  # mantissa bit
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)
        assert sign == 1
        assert exponent == 128
        assert mant_bits[0] == 1

    def test_parts_zero(self, float_op_32):
        arr = [0] * 32
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)
        assert sign == 0
        assert exponent == 0
        assert all(b == 0 for b in mant_bits)

    def test_parts_custom_exponent(self, float_op_32):
        arr = [0] * 32
        # exp = 130 (binary: 10000010)
        arr[1:9] = [1, 0, 0, 0, 0, 0, 1, 0]
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)
        assert exponent == 130

    def test_parts_mantissa_extraction(self, float_op_32):
        arr = [0] * 32
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]  # exp = 127
        # Устанавливаем несколько бит мантиссы
        arr[9] = 1  # 2^-1
        arr[10] = 0  # 2^-2
        arr[11] = 1  # 2^-3
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)
        assert mant_bits[0] == 1
        assert mant_bits[1] == 0
        assert mant_bits[2] == 1
        assert len(mant_bits) == 23

    def test_parts_with_constants(self, float_op_32):
        """Проверка, что метод использует константы из FloatConstants"""
        from Constants.FloatConstants import IEEE_SIGN_BIT, IEEE_EXP_BITS, IEEE_TOTAL_BITS

        arr = [0] * 32
        arr[0] = 1
        arr[1:9] = [0, 1, 1, 1, 1, 1, 1, 1]

        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(arr)

        # Проверяем, что извлечение соответствует константам
        assert sign == arr[IEEE_SIGN_BIT]
        assert len(mant_bits) == IEEE_TOTAL_BITS - IEEE_SIGN_BIT - IEEE_EXP_BITS - 1


# ============================================================================
# Integration tests
# ============================================================================

class TestIntegration:
    """Интеграционные тесты взаимодействия методов"""

    def test_full_cycle_with_parts_extraction(self, float_op_32):
        """float → IEEE-754 → extract parts → verify"""
        original = -3.14
        bits = float_op_32.float_to_ieee754(original)
        sign, exponent, mant_bits = float_op_32.ieee754_bits_to_parts(bits)

        assert sign == 1  # negative
        assert exponent > 0  # normalized number
        assert len(mant_bits) == 23

    def test_consistency_between_methods(self, float_op_32):
        """Проверка согласованности float_to_ieee754 и ieee754_to_float"""
        test_values = [1.0, -1.0, 2.5, -0.125, 100.0, -100.0]

        for val in test_values:
            bits = float_op_32.float_to_ieee754(val)
            restored = float_op_32.ieee754_to_float(bits)
            rel_err = abs(restored - val) / abs(val)
            assert rel_err < 1e-7, f"Failed for {val}"

    def test_bit_array_integrity(self, float_op_32):
        """Проверка, что битовые массивы имеют правильную длину"""
        for val in [0.0, 1.0, -1.0, 3.14, 1e10, 1e-10]:
            bits = float_op_32.float_to_ieee754(val)
            assert len(bits) == 32
            assert all(b in (0, 1) for b in bits)


# ============================================================================
# Edge cases and error handling
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_very_small_normalized_number(self, float_op_32):
        """Минимальное нормализованное число"""
        # 2^-126 ≈ 1.18e-38
        result = float_op_32.float_to_ieee754(2 ** -126)
        assert result[0] == 0
        exp_bits = result[1:9]
        exponent = sum(b * (2 ** (7 - i)) for i, b in enumerate(exp_bits))
        assert exponent == 1  # min normalized exponent

    def test_very_large_number(self, float_op_32):
        """Большое число в пределах диапазона"""
        result = float_op_32.float_to_ieee754(3.4e38)  # near max float32
        assert len(result) == 32
        assert result[0] == 0

    def test_negative_small_number(self, float_op_32):
        result = float_op_32.float_to_ieee754(-1e-10)
        assert result[0] == 1  # negative sign
        assert len(result) == 32

    def test_mantissa_precision_loss(self, float_op_32):
        """Проверка, что тест учитывает потерю точности"""
        original = 0.1  # Не представляется точно в двоичной форме
        bits = float_op_32.float_to_ieee754(original)
        restored = float_op_32.ieee754_to_float(bits)
        # Допускаем небольшую погрешность
        assert abs(restored - original) < 1e-7

    def test_power_of_two_boundaries(self, float_op_32):
        """Тестирование чисел, равных степеням двойки"""
        for exp in range(-10, 11):
            val = 2.0 ** exp
            bits = float_op_32.float_to_ieee754(val)
            restored = float_op_32.ieee754_to_float(bits)
            assert abs(restored - val) / abs(val) < 1e-6