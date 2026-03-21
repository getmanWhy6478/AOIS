import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Converting.BCDOperator import BCDOperator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def bcd_op_32():
    """BCDOperator с 32 битами (стандартная конфигурация)"""
    return BCDOperator(bits=32)


@pytest.fixture
def bcd_op_16():
    """BCDOperator с 16 битами (для тестов ограниченной ёмкости)"""
    return BCDOperator(bits=16)


@pytest.fixture
def bcd_op_8():
    """BCDOperator с 8 битами (минимальная конфигурация)"""
    return BCDOperator(bits=8)


# ============================================================================
# Tests for __init__
# ============================================================================

class TestBCDOperatorInit:
    """Тесты инициализации класса"""

    def test_init_default_bits(self):
        op = BCDOperator()
        assert op.bits == 32
        assert op.converter is not None

    def test_init_custom_bits(self):
        for bits in [4, 8, 16, 32, 64, 128]:
            op = BCDOperator(bits=bits)
            assert op.bits == bits
            assert op.converter is not None

    def test_init_converter_instance(self):
        op = BCDOperator()
        from Utils.ArrayStringConverter import ArrayStringConverter
        assert isinstance(op.converter, ArrayStringConverter)


# ============================================================================
# Tests for decimal_to_bcd_8421
# ============================================================================

class TestDecimalToBCD8421:
    """Тесты преобразования десятичного числа в BCD 8421"""

    # --- Zero cases ---

    def test_bcd_zero_positive(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(0)
        assert len(result) == 32
        # Все биты должны быть 0
        assert all(b == 0 for b in result)

    def test_bcd_zero_negative(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(-0)
        assert result == [0] * 32

    # --- Single digit positive ---

    @pytest.mark.parametrize("digit", range(10))
    def test_bcd_single_digit_positive(self, bcd_op_32, digit):
        result = bcd_op_32.decimal_to_bcd_8421(digit)
        # Проверяем последние 4 бита
        last_4 = result[-4:]
        expected_bcd = [int(b) for b in f"{digit:04b}"]
        assert last_4 == expected_bcd

    # --- Single digit negative ---

    @pytest.mark.parametrize("digit", range(1, 10))
    def test_bcd_single_digit_negative(self, bcd_op_32, digit):
        result = bcd_op_32.decimal_to_bcd_8421(-digit)
        assert result[0] == 1  # sign bit
        last_4 = result[-4:]
        expected_bcd = [int(b) for b in f"{digit:04b}"]
        assert last_4 == expected_bcd

    # --- Multi-digit positive ---

    def test_bcd_two_digit_positive(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(42)
        # 42 = 0100 0010 в BCD
        assert result[-8:-4] == [0, 1, 0, 0]  # 4
        assert result[-4:] == [0, 0, 1, 0]  # 2

    def test_bcd_three_digit_positive(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(123)
        # 123 = 0001 0010 0011 в BCD
        assert result[-12:-8] == [0, 0, 0, 1]  # 1
        assert result[-8:-4] == [0, 0, 1, 0]  # 2
        assert result[-4:] == [0, 0, 1, 1]  # 3

    def test_bcd_multi_digit_with_zeros(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(1005)
        # 1005 = 0001 0000 0000 0101 в BCD
        assert result[-16:-12] == [0, 0, 0, 1]  # 1
        assert result[-12:-8] == [0, 0, 0, 0]  # 0
        assert result[-8:-4] == [0, 0, 0, 0]  # 0
        assert result[-4:] == [0, 1, 0, 1]  # 5

    # --- Multi-digit negative ---

    def test_bcd_two_digit_negative(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(-42)
        assert result[0] == 1  # sign bit
        assert result[-8:-4] == [0, 1, 0, 0]  # 4
        assert result[-4:] == [0, 0, 1, 0]  # 2

    def test_bcd_large_negative(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(-999)
        assert result[0] == 1
        # 999 = 1001 1001 1001 в BCD
        assert result[-12:-8] == [1, 0, 0, 1]
        assert result[-8:-4] == [1, 0, 0, 1]
        assert result[-4:] == [1, 0, 0, 1]

    # --- Limited bit width ---

    def test_bcd_8bit_single_digit(self, bcd_op_8):
        result = bcd_op_8.decimal_to_bcd_8421(7)
        assert len(result) == 8
        assert result[-4:] == [0, 1, 1, 1]  # 7 in binary

    def test_bcd_16bit_two_digits(self, bcd_op_16):
        result = bcd_op_16.decimal_to_bcd_8421(85)
        assert len(result) == 16
        assert result[-8:-4] == [1, 0, 0, 0]  # 8
        assert result[-4:] == [0, 1, 0, 1]  # 5

    def test_bcd_overflow_truncation(self, bcd_op_8):
        """Число, не помещающееся в 8 бит (2 цифры), должно обрезаться"""
        result = bcd_op_8.decimal_to_bcd_8421(42)
        # В 8 битах поместится только одна цифра (последняя)
        assert result[-4:] == [0, 0, 1, 0]  # 2

    # --- Edge values ---

    def test_bcd_max_single_digit(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(9)
        assert result[-4:] == [1, 0, 0, 1]  # 9 in BCD

    def test_bcd_large_number(self, bcd_op_32):
        result = bcd_op_32.decimal_to_bcd_8421(12345678)
        assert result[0] == 0  # positive
        assert len(result) == 32
        # Проверяем, что хотя бы некоторые биты установлены
        assert any(b == 1 for b in result)


# ============================================================================
# Tests for bcd_8421_to_decimal
# ============================================================================

class TestBCD8421ToDecimal:
    """Тесты преобразования BCD 8421 в десятичное число"""

    # --- Zero cases ---

    def test_decimal_from_bcd_zero(self, bcd_op_32):
        arr = [0] * 32
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        assert result == 0

    # --- Single digit ---

    @pytest.mark.parametrize("digit", range(10))
    def test_decimal_from_bcd_single_digit(self, bcd_op_32, digit):
        arr = [0] * 32
        # Устанавливаем последние 4 бита как BCD цифру
        bcd_bits = [int(b) for b in f"{digit:04b}"]
        for i, bit in enumerate(bcd_bits):
            arr[32 - 4 + i] = bit
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        assert result == digit

    def test_decimal_from_bcd_two_digits(self, bcd_op_32):
        arr = [0] * 32
        # 42: 4 = 0100, 2 = 0010
        arr[-8:-4] = [0, 1, 0, 0]  # 4
        arr[-4:] = [0, 0, 1, 0]  # 2
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        assert result == 42

    def test_decimal_from_bcd_three_digits(self, bcd_op_32):
        arr = [0] * 32
        # 123: 1=0001, 2=0010, 3=0011
        arr[-12:-8] = [0, 0, 0, 1]
        arr[-8:-4] = [0, 0, 1, 0]
        arr[-4:] = [0, 0, 1, 1]
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        assert result == 123

    def test_decimal_from_bcd_with_zeros(self, bcd_op_32):
        arr = [0] * 32
        # 1005: 1=0001, 0=0000, 0=0000, 5=0101
        arr[-16:-12] = [0, 0, 0, 1]
        arr[-12:-8] = [0, 0, 0, 0]
        arr[-8:-4] = [0, 0, 0, 0]
        arr[-4:] = [0, 1, 0, 1]
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        assert result == 1005

    # --- Limited bit width ---

    def test_decimal_from_bcd_16bit(self, bcd_op_16):
        arr = [0] * 16
        arr[-8:-4] = [1, 0, 0, 1]  # 9
        arr[-4:] = [0, 1, 1, 1]  # 7
        result = bcd_op_16.bcd_8421_to_decimal(arr)
        assert result == 97

    def test_decimal_from_bcd_8bit(self, bcd_op_8):
        arr = [0] * 8
        arr[-4:] = [0, 1, 0, 1]  # 5
        result = bcd_op_8.bcd_8421_to_decimal(arr)
        assert result == 5

    # --- Invalid BCD digits (>=10) ---

    def test_decimal_from_bcd_invalid_digit_skipped(self, bcd_op_32):
        """BCD цифра >= 10 должна игнорироваться по логике кода"""
        arr = [0] * 32
        # Устанавливаем "цифру" 15 (1111), которая невалидна для BCD
        arr[-4:] = [1, 1, 1, 1]  # 15, не валидный BCD
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        # По коду: if digit < 10: добавляем, иначе пропускаем
        assert result == 0

    def test_decimal_from_bcd_mixed_valid_invalid(self, bcd_op_32):
        arr = [0] * 32
        # Первая "цифра" валидна (5), вторая нет (12)
        arr[-8:-4] = [1, 1, 0, 0]  # 12 - невалидно
        arr[-4:] = [0, 1, 0, 1]  # 5 - валидно
        result = bcd_op_32.bcd_8421_to_decimal(arr)
        # Должна обработаться только последняя валидная цифра
        assert result == 5


# ============================================================================
# Tests for round-trip conversions
# ============================================================================

class TestRoundTripConversions:
    """Тесты сквозного преобразования: decimal → BCD → decimal"""

    @pytest.mark.parametrize("value", [0, 1, 5, 9])
    def test_roundtrip_single_digit(self, bcd_op_32, value):
        bcd = bcd_op_32.decimal_to_bcd_8421(value)
        result = bcd_op_32.bcd_8421_to_decimal(bcd)
        assert result == value

    @pytest.mark.parametrize("value", [10, 42, 99, 100, 999])
    def test_roundtrip_multi_digit(self, bcd_op_32, value):
        bcd = bcd_op_32.decimal_to_bcd_8421(value)
        result = bcd_op_32.bcd_8421_to_decimal(bcd)
        assert result == value

    @pytest.mark.parametrize("value", [1234, 5678, 9999])
    def test_roundtrip_four_digits(self, bcd_op_32, value):
        """4 цифры = 16 бит, помещается в 32-битный массив"""
        bcd = bcd_op_32.decimal_to_bcd_8421(value)
        result = bcd_op_32.bcd_8421_to_decimal(bcd)
        assert result == value

    def test_roundtrip_16bit_config(self, bcd_op_16):
        """16 бит = 4 десятичные цифры максимум"""
        for value in [0, 42, 999]:
            bcd = bcd_op_16.decimal_to_bcd_8421(value)
            result = bcd_op_16.bcd_8421_to_decimal(bcd)
            assert result == value

    def test_roundtrip_8bit_config(self, bcd_op_8):
        """8 бит = 2 десятичные цифры максимум"""
        for value in [0, 5, 42]:
            bcd = bcd_op_8.decimal_to_bcd_8421(value)
            result = bcd_op_8.bcd_8421_to_decimal(bcd)
            assert result == value

    def test_roundtrip_overflow_truncation(self, bcd_op_8):
        """Число с 3 цифрами в 8-битном режиме должно обрезаться"""
        original = 123  # 3 цифры, но 8 бит = 2 цифры максимум
        bcd = bcd_op_8.decimal_to_bcd_8421(original)
        result = bcd_op_8.bcd_8421_to_decimal(bcd)
        # Ожидаем только последние 2 цифры: 23
        assert result == 23


# ============================================================================
# Tests for display_bcd
# ============================================================================

class TestDisplayBCD:
    """Тесты метода display_bcd"""

    def test_display_bcd_positive(self, bcd_op_32, capsys):
        result = bcd_op_32.display_bcd(42)
        captured = capsys.readouterr()

        assert "=== BCD 8421 ===" in captured.out
        assert "Число: 42" in captured.out
        assert "BCD код:" in captured.out
        assert "Проверка (dec): 42" in captured.out
        assert isinstance(result, list)
        assert len(result) == 32

    def test_display_bcd_zero(self, bcd_op_32, capsys):
        result = bcd_op_32.display_bcd(0)
        captured = capsys.readouterr()

        assert "Число: 0" in captured.out
        assert "Проверка (dec): 0" in captured.out
        assert all(b == 0 for b in result)

    def test_display_bcd_with_converter(self, bcd_op_32, capsys):
        """Проверка, что используется converter.array_to_string"""
        bcd_op_32.display_bcd(7)
        captured = capsys.readouterr()

        # BCD код должен быть строкой из 0 и 1 длиной 32
        import re
        bcd_match = re.search(r'BCD код:\s*([01]+)', captured.out)
        assert bcd_match is not None
        bcd_str = bcd_match.group(1)
        assert len(bcd_str) == 32
        assert all(c in '01' for c in bcd_str)


# ============================================================================
# Integration and edge case tests
# ============================================================================

class TestIntegrationAndEdges:
    """Интеграционные тесты и граничные случаи"""

    def test_bcd_bit_array_integrity(self, bcd_op_32):
        """Проверка, что все битовые массивы имеют правильную длину и значения"""
        for val in [0, 1, -1, 42, -999, 12345]:
            bcd = bcd_op_32.decimal_to_bcd_8421(val)
            assert len(bcd) == 32
            assert all(b in (0, 1) for b in bcd)

    def test_bcd_sign_bit_consistency(self, bcd_op_32):
        """Проверка, что знак сохраняется корректно"""
        for val in [1, 42, 999]:
            pos_bcd = bcd_op_32.decimal_to_bcd_8421(val)
            neg_bcd = bcd_op_32.decimal_to_bcd_8421(-val)

            assert pos_bcd[0] == 0
            assert neg_bcd[0] == 1
            # Остальные биты (кроме знака) должны совпадать
            assert pos_bcd[1:] == neg_bcd[1:]

    def test_bcd_max_digits_for_32bit(self, bcd_op_32):
        """32 бита = 1 знак + 31 бит данных = 7 полных цифр (28 бит) + 3 бита"""
        # Максимум 7 цифр поместится полностью
        value = 9999999
        bcd = bcd_op_32.decimal_to_bcd_8421(value)
        result = bcd_op_32.bcd_8421_to_decimal(bcd)
        assert result == value


    def test_bcd_encoding_order(self, bcd_op_32):
        """Проверка, что цифры кодируются в правильном порядке (от младшей)"""
        # 123: цифры извлекаются как [3, 2, 1], но в BCD должны быть [1][2][3]
        result = bcd_op_32.decimal_to_bcd_8421(123)
        # Проверяем позиции: последние 4 бита = 3, предыдущие 4 = 2, ещё предыдущие = 1
        assert result[-4:] == [0, 0, 1, 1]  # 3
        assert result[-8:-4] == [0, 0, 1, 0]  # 2
        assert result[-12:-8] == [0, 0, 0, 1]  # 1

    def test_bcd_large_value_truncation(self, bcd_op_16):
        """Число, не помещающееся в заданное количество бит, обрезается"""
        # 16 бит = 4 тетрады = 4 цифры максимум
        original = 12345  # 5 цифр
        bcd = bcd_op_16.decimal_to_bcd_8421(original)
        result = bcd_op_16.bcd_8421_to_decimal(bcd)
        # Должны остаться только последние 4 цифры: 2345
        assert result == 2345
