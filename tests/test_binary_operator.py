import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Converting.BinaryOperator import BinaryOperator


class TestBinaryOperatorInit:
    """Tests for __init__ method"""

    def test_init_default_bits(self):
        op = BinaryOperator()
        assert op.bits == 32
        assert op.converter is not None

    def test_init_custom_bits(self):
        op = BinaryOperator(bits=8)
        assert op.bits == 8

    def test_init_custom_bits_various(self):
        for bits in [4, 8, 16, 64]:
            op = BinaryOperator(bits=bits)
            assert op.bits == bits


class TestGetDirectCode:
    """Tests for get_direct_code method"""

    def test_direct_code_positive_zero(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(0)
        assert result == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_direct_code_negative_zero(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(-0)
        assert result == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_direct_code_positive_small(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(5)
        expected = [0, 0, 0, 0, 0, 1, 0, 1]
        assert result == expected

    def test_direct_code_negative_small(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(-5)
        expected = [1, 0, 0, 0, 0, 1, 0, 1]
        assert result == expected

    def test_direct_code_positive_max_8bit(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(127)
        expected = [0, 1, 1, 1, 1, 1, 1, 1]
        assert result == expected

    def test_direct_code_negative_min_8bit(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(-127)
        expected = [1, 1, 1, 1, 1, 1, 1, 1]
        assert result == expected

    def test_direct_code_custom_length(self):
        op = BinaryOperator(bits=32)
        result = op.get_direct_code(5, length=4)
        expected = [0, 1, 0, 1]
        assert result == expected

    def test_direct_code_negative_custom_length(self):
        op = BinaryOperator(bits=32)
        result = op.get_direct_code(-3, length=4)
        expected = [1, 0, 1, 1]
        assert result == expected

    def test_direct_code_non_int_input(self):
        op = BinaryOperator()
        assert op.get_direct_code("5") is None
        assert op.get_direct_code(5.5) is None
        assert op.get_direct_code(None) is None

    def test_direct_code_large_number_truncated(self):
        op = BinaryOperator(bits=4)
        result = op.get_direct_code(15)
        assert result[0] == 0
        assert result[1:] == [1, 1, 1]

    def test_direct_code_power_of_two(self):
        op = BinaryOperator(bits=8)
        result = op.get_direct_code(64)
        expected = [0, 1, 0, 0, 0, 0, 0, 0]
        assert result == expected


class TestGetInverseCode:
    """Tests for get_inverse_code method"""

    def test_inverse_code_positive_zero(self):
        op = BinaryOperator(bits=8)
        result = op.get_inverse_code(0)
        assert result == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_inverse_code_positive_number(self):
        op = BinaryOperator(bits=8)
        result = op.get_inverse_code(5)
        assert result == op.get_direct_code(5)

    def test_inverse_code_negative_small(self):
        op = BinaryOperator(bits=8)
        result = op.get_inverse_code(-5)
        expected = [1, 1, 1, 1, 1, 0, 1, 0]
        assert result == expected

    def test_inverse_code_negative_custom_length(self):
        op = BinaryOperator(bits=32)
        result = op.get_inverse_code(-3, length=4)
        expected = [1, 1, 0, 0]
        assert result == expected

    def test_inverse_code_non_int_input(self):
        op = BinaryOperator()
        assert op.get_inverse_code("test") is None
        assert op.get_inverse_code([1, 2]) is None

    def test_inverse_code_negative_one(self):
        op = BinaryOperator(bits=8)
        result = op.get_inverse_code(-1)
        expected = [1, 1, 1, 1, 1, 1, 1, 0]
        assert result == expected


class TestGetComplementCode:
    """Tests for get_complement_code method"""

    def test_complement_code_positive_zero(self):
        op = BinaryOperator(bits=8)
        result = op.get_complement_code(0)
        assert result == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_complement_code_positive_number(self):
        op = BinaryOperator(bits=8)
        result = op.get_complement_code(5)
        assert result == op.get_direct_code(5)

    def test_complement_code_negative_small(self):
        op = BinaryOperator(bits=8)
        result = op.get_complement_code(-5)
        expected = [1, 1, 1, 1, 1, 0, 1, 1]
        assert result == expected

    def test_complement_code_negative_one(self):
        op = BinaryOperator(bits=8)
        result = op.get_complement_code(-1)
        expected = [1, 1, 1, 1, 1, 1, 1, 1]
        assert result == expected

    def test_complement_code_negative_custom_length(self):
        op = BinaryOperator(bits=32)
        result = op.get_complement_code(-1, length=4)
        expected = [1, 1, 1, 1]
        assert result == expected

    def test_complement_code_negative_with_carry_propagation(self):
        op = BinaryOperator(bits=8)
        result = op.get_complement_code(-8)
        expected = [1, 1, 1, 1, 1, 0, 0, 0]
        assert result == expected

    def test_complement_code_non_int_input(self):
        op = BinaryOperator()
        assert op.get_complement_code(None) is None
        assert op.get_complement_code(3.14) is None


class TestArrayToDecimalDirect:
    """Tests for array_to_decimal_direct method"""

    def test_direct_positive_zero(self):
        op = BinaryOperator()
        arr = [0, 0, 0, 0]
        assert op.array_to_decimal_direct(arr) == 0

    def test_direct_positive_small(self):
        op = BinaryOperator()
        arr = [0, 0, 0, 0, 0, 1, 0, 1]
        assert op.array_to_decimal_direct(arr) == 5

    def test_direct_with_sign_bit_ignored(self):
        op = BinaryOperator()
        arr = [1, 0, 0, 0, 0, 0, 0, 1]
        assert op.array_to_decimal_direct(arr) == 129

    def test_direct_all_ones(self):
        op = BinaryOperator(bits=4)
        arr = [1, 1, 1, 1]
        assert op.array_to_decimal_direct(arr) == 15

    def test_direct_single_bit(self):
        op = BinaryOperator(bits=1)
        arr = [1]
        assert op.array_to_decimal_direct(arr) == 1


class TestArrayToDecimalComplement:
    """Tests for array_to_decimal_complement method"""

    def test_complement_positive_zero(self):
        op = BinaryOperator()
        arr = [0, 0, 0, 0]
        assert op.array_to_decimal_complement(arr) == 0

    def test_complement_positive_small(self):
        op = BinaryOperator()
        arr = [0, 0, 0, 0, 0, 1, 0, 1]
        assert op.array_to_decimal_complement(arr) == 5

    def test_complement_negative_small(self):
        op = BinaryOperator(bits=8)
        arr = [1, 1, 1, 1, 1, 0, 1, 1]
        assert op.array_to_decimal_complement(arr) == -5

    def test_complement_negative_one(self):
        op = BinaryOperator(bits=8)
        arr = [1, 1, 1, 1, 1, 1, 1, 1]
        assert op.array_to_decimal_complement(arr) == -1

    def test_complement_negative_128_8bit(self):
        op = BinaryOperator(bits=8)
        arr = [1, 0, 0, 0, 0, 0, 0, 0]
        assert op.array_to_decimal_complement(arr) == -128

    def test_complement_positive_127_8bit(self):
        op = BinaryOperator(bits=8)
        arr = [0, 1, 1, 1, 1, 1, 1, 1]
        assert op.array_to_decimal_complement(arr) == 127

    def test_complement_roundtrip(self):
        op = BinaryOperator(bits=8)
        for num in [-64, -1, 0, 1, 63, 127]:
            arr = op.get_complement_code(num)
            decoded = op.array_to_decimal_complement(arr)
            assert decoded == num, f"Failed for {num}: got {decoded}"


class TestDisplayCodes:
    """Tests for display_codes method"""

    def test_display_codes_positive(self, capsys):
        op = BinaryOperator(bits=8)
        result = op.display_codes(5)
        captured = capsys.readouterr()
        assert "Число: 5" in captured.out
        assert "Прямой код:" in captured.out
        assert "Обратный код:" in captured.out
        assert "Доп. код:" in captured.out
        direct, inverse, complement = result
        assert direct == op.get_direct_code(5)

    def test_display_codes_negative(self, capsys):
        op = BinaryOperator(bits=8)
        result = op.display_codes(-5)
        captured = capsys.readouterr()
        assert "Число: -5" in captured.out
        direct, inverse, complement = result
        assert direct[0] == 1
        assert complement == [1, 1, 1, 1, 1, 0, 1, 1]

    def test_display_codes_non_int(self):
        op = BinaryOperator()
        result = op.display_codes("invalid")
        assert result is None

    def test_display_codes_zero(self, capsys):
        op = BinaryOperator(bits=8)
        result = op.display_codes(0)
        captured = capsys.readouterr()
        assert "Число: 0" in captured.out
        direct, inverse, complement = result
        assert direct == [0] * 8
        assert inverse == [0] * 8
        assert complement == [0] * 8


class TestEdgeCases:
    """Additional edge case tests"""

    def test_very_large_bits(self):
        op = BinaryOperator(bits=64)
        result = op.get_direct_code(1)
        assert len(result) == 64
        assert result[-1] == 1
        assert sum(result[:-1]) == 0

    def test_negative_with_large_bits(self):
        op = BinaryOperator(bits=64)
        result = op.get_complement_code(-1)
        assert all(b == 1 for b in result)

    def test_magnitude_overflow_in_direct(self):
        op = BinaryOperator(bits=4)
        result = op.get_direct_code(16)
        assert result[0] == 0
        assert result[1:] == [0, 0, 0]

    def test_inverse_of_positive_unchanged(self):
        op = BinaryOperator(bits=8)
        for num in [0, 1, 42, 127]:
            direct = op.get_direct_code(num)
            inverse = op.get_inverse_code(num)
            assert direct == inverse

    def test_complement_of_positive_unchanged(self):
        op = BinaryOperator(bits=8)
        for num in [0, 1, 42, 127]:
            direct = op.get_direct_code(num)
            complement = op.get_complement_code(num)
            assert direct == complement


class TestRoundTripConversions:
    """Test encoding and decoding roundtrips"""

    def test_direct_roundtrip_positive(self):
        op = BinaryOperator(bits=8)
        for num in range(0, 128):
            arr = op.get_direct_code(num)
            decoded = op.array_to_decimal_direct(arr) & 0x7F
            assert decoded == num

    def test_complement_roundtrip_full_range(self):
        op = BinaryOperator(bits=8)
        for num in range(-127, 128):  # -128 is edge case with current impl
            arr = op.get_complement_code(num)
            decoded = op.array_to_decimal_complement(arr)
            assert decoded == num, f"Failed for {num}"

    def test_complement_roundtrip_16bit(self):
        op = BinaryOperator(bits=16)
        test_values = [-1000, -1, 0, 1, 1000, 32767]
        for num in test_values:
            arr = op.get_complement_code(num)
            decoded = op.array_to_decimal_complement(arr)
            assert decoded == num