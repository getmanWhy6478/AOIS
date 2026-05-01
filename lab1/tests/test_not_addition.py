import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Operations.NotAddition import NotAddition


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sub_op_32():
    """NotAddition с 32 битами (стандартная конфигурация)"""
    return NotAddition(num1=0, num2=0)


@pytest.fixture
def sub_op_16():
    """NotAddition с 16 битами (для тестов ограниченной разрядности)"""
    # Создаём через модификацию после инициализации
    op = NotAddition(num1=0, num2=0)
    op.operator = type('Mock', (), {'bits': 16})()
    return op


# ============================================================================
# Tests for __init__
# ============================================================================

class TestNotAdditionInit:
    """Тесты инициализации класса"""

    def test_init_default(self):
        op = NotAddition(num1=10, num2=5)
        assert op.num1 == 10
        assert op.num2 == 5
        assert op.operator is not None
        assert op.float_operator is not None
        assert op.converter is not None
        assert op.additor is not None
        assert op.additor.num1 == 10
        assert op.additor.num2 == 5

    def test_init_negative_numbers(self):
        op = NotAddition(num1=-15, num2=7)
        assert op.num1 == -15
        assert op.num2 == 7

    def test_init_dependencies_types(self):
        op = NotAddition(num1=0, num2=0)
        from Converting.BinaryOperator import BinaryOperator
        from Converting.FloatOperator import FloatOperator
        from Utils.ArrayStringConverter import ArrayStringConverter
        from Operations.Addition import Addition

        assert isinstance(op.operator, BinaryOperator)
        assert isinstance(op.float_operator, FloatOperator)
        assert isinstance(op.converter, ArrayStringConverter)
        assert isinstance(op.additor, Addition)


# ============================================================================
# Tests for negate_complement
# ============================================================================

class TestNegateComplement:
    """Тесты метода отрицания в дополнительном коде"""

    # --- Zero ---

    def test_negate_zero(self, sub_op_32):
        arr = [0] * 32
        result = sub_op_32.negate_complement(arr)
        # -0 в дополнительном коде = 0
        assert result == [0] * 32

    # --- Positive numbers ---

    def test_negate_positive_one(self, sub_op_32):
        # 1 в 8-bit complement: 00000001
        arr = [0] * 7 + [1]
        result = sub_op_32.negate_complement(arr)
        # -1 = 11111111
        expected = [1] * 8
        assert result == expected

    def test_negate_positive_small(self, sub_op_32):
        # 5 в 8-bit: 00000101
        arr = [0, 0, 0, 0, 0, 1, 0, 1]
        result = sub_op_32.negate_complement(arr)
        # -5 = 11111011
        expected = [1, 1, 1, 1, 1, 0, 1, 1]
        assert result == expected

    def test_negate_positive_max_8bit(self, sub_op_32):
        # 127 в 8-bit: 01111111
        arr = [0, 1, 1, 1, 1, 1, 1, 1]
        result = sub_op_32.negate_complement(arr)
        # -127 = 10000001
        expected = [1, 0, 0, 0, 0, 0, 0, 1]
        assert result == expected

    # --- Negative numbers (double negate) ---

    def test_negate_negative_one(self, sub_op_32):
        # -1 в 8-bit: 11111111
        arr = [1] * 8
        result = sub_op_32.negate_complement(arr)
        # -(-1) = 1 = 00000001
        expected = [0] * 7 + [1]
        assert result == expected

    def test_negate_double_negation(self, sub_op_32):
        """Отрицание дважды должно вернуть исходное значение"""
        original = [0, 0, 0, 0, 1, 0, 1, 0]  # 10
        negated = sub_op_32.negate_complement(original)
        double_negated = sub_op_32.negate_complement(negated)
        assert double_negated == original

    # --- Carry propagation tests ---

    def test_negate_with_carry_chain(self, sub_op_32):
        """Проверка цепочки переносов при инвертировании"""
        # 00001111 (15) -> инверсия: 11110000 -> +1: 11110001 (-15)
        arr = [0, 0, 0, 0, 1, 1, 1, 1]
        result = sub_op_32.negate_complement(arr)
        expected = [1, 1, 1, 1, 0, 0, 0, 1]
        assert result == expected

    def test_negate_all_ones(self, sub_op_32):
        """11111111 (-1) -> инверсия: 00000000 -> +1: 00000001 (1)"""
        arr = [1] * 8
        result = sub_op_32.negate_complement(arr)
        expected = [0] * 7 + [1]
        assert result == expected

    def test_negate_min_negative_8bit(self, sub_op_32):
        """-128 в 8-bit: 10000000 -> отрицание даёт переполнение"""
        arr = [1, 0, 0, 0, 0, 0, 0, 0]
        result = sub_op_32.negate_complement(arr)
        # Инверсия: 01111111, +1: 10000000 (переполнение, остаётся -128)
        expected = [1, 0, 0, 0, 0, 0, 0, 0]
        assert result == expected

    # --- Different bit widths ---

    def test_negate_16bit(self, sub_op_32):
        arr = [0] * 14 + [1, 0]  # 2 в 16-bit
        result = sub_op_32.negate_complement(arr)
        # Проверка, что результат имеет правильную длину
        assert len(result) == 16
        # Последние биты должны быть ...1110 (-2)
        assert result[-1] == 0
        assert result[-2] == 1


# ============================================================================
# Tests for subtract_complement
# ============================================================================

class TestSubtractComplement:
    """Тесты вычитания в дополнительном коде"""

    # --- Positive - Positive ---

    def test_subtract_complement_positive_result(self, sub_op_32, capsys):
        op = NotAddition(num1=10, num2=3)
        result_arr, result_dec = op.subtract_complement()
        captured = capsys.readouterr()

        assert "=== ВЫЧИТАНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ ===" in captured.out
        assert "Числа: 10 - 3" in captured.out
        assert "Доп. код A:" in captured.out
        assert "Доп. код B:" in captured.out
        assert "-B (доп. код):" in captured.out
        assert "Результат:" in captured.out
        assert result_dec == 7
        assert "Проверка: 10 - 3 = 7" in captured.out

    def test_subtract_complement_negative_result(self, sub_op_32):
        op = NotAddition(num1=3, num2=10)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -7

    def test_subtract_complement_equal_numbers(self, sub_op_32):
        op = NotAddition(num1=42, num2=42)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 0

    # --- Negative - Negative ---

    def test_subtract_complement_neg_minus_neg_positive(self, sub_op_32):
        # -5 - (-10) = 5
        op = NotAddition(num1=-5, num2=-10)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 5

    def test_subtract_complement_neg_minus_neg_negative(self, sub_op_32):
        # -10 - (-5) = -5
        op = NotAddition(num1=-10, num2=-5)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -5

    # --- Mixed signs ---

    def test_subtract_complement_pos_minus_neg(self, sub_op_32):
        # 10 - (-5) = 15
        op = NotAddition(num1=10, num2=-5)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 15

    def test_subtract_complement_neg_minus_pos(self, sub_op_32):
        # -10 - 5 = -15
        op = NotAddition(num1=-10, num2=5)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -15

    # --- Zero cases ---

    def test_subtract_complement_zero_minus_zero(self, sub_op_32):
        op = NotAddition(num1=0, num2=0)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 0

    def test_subtract_complement_zero_minus_positive(self, sub_op_32):
        op = NotAddition(num1=0, num2=15)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -15

    def test_subtract_complement_zero_minus_negative(self, sub_op_32):
        op = NotAddition(num1=0, num2=-15)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 15

    def test_subtract_complement_positive_minus_zero(self, sub_op_32):
        op = NotAddition(num1=25, num2=0)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 25

    def test_subtract_complement_negative_minus_zero(self, sub_op_32):
        op = NotAddition(num1=-25, num2=0)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -25

    # --- Edge values ---

    def test_subtract_complement_max_positive_8bit(self, sub_op_32):
        op = NotAddition(num1=127, num2=0)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 127

    def test_subtract_complement_min_negative_8bit(self, sub_op_32):
        op = NotAddition(num1=-128, num2=0)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == -128

    def test_subtract_complement_overflow(self, sub_op_32):
        """Переполнение: 100 - (-50) = 150 > 127 для 8-bit"""
        op = NotAddition(num1=100, num2=-50)
        result_arr, result_dec = op.subtract_complement()
        # Результат будет некорректным из-за переполнения
        assert isinstance(result_dec, int)

    # --- Output format verification ---

    def test_subtract_complement_prints_binary_strings(self, sub_op_32, capsys):
        op = NotAddition(num1=5, num2=2)
        op.subtract_complement()
        captured = capsys.readouterr()

        import re
        # Проверяем, что напечатаны бинарные строки
        binary_matches = re.findall(r'[01]{8,32}', captured.out)
        assert len(binary_matches) >= 4  # A, B, -B, result


# ============================================================================
# Tests for ieee754_sub
# ============================================================================

class TestIeee754Sub:
    """Тесты вычитания в формате IEEE-754"""

    # --- Positive - Positive ---

    def test_ieee754_sub_positive_result(self, sub_op_32, capsys):
        op = NotAddition(num1=5.5, num2=2.0)
        result_arr, result_dec = op.ieee754_sub()
        captured = capsys.readouterr()

        assert "=== IEEE-754 ВЫЧИТАНИЕ ===" in captured.out
        assert "Числа: 5.5 - 2.0" in captured.out
        assert "Результат IEEE-754:" in captured.out
        assert abs(result_dec - 3.5) < 1e-6

    def test_ieee754_sub_negative_result(self, sub_op_32):
        op = NotAddition(num1=2.0, num2=5.5)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - (-3.5)) < 1e-6

    def test_ieee754_sub_equal_numbers(self, sub_op_32):
        op = NotAddition(num1=3.14, num2=3.14)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec) < 1e-6

    # --- Negative - Negative ---

    def test_ieee754_sub_neg_minus_neg_positive(self, sub_op_32):
        # -2.5 - (-7.5) = 5.0
        op = NotAddition(num1=-2.5, num2=-7.5)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - 5.0) < 1e-6

    def test_ieee754_sub_neg_minus_neg_negative(self, sub_op_32):
        # -7.5 - (-2.5) = -5.0
        op = NotAddition(num1=-7.5, num2=-2.5)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - (-5.0)) < 1e-6

    # --- Mixed signs ---

    def test_ieee754_sub_pos_minus_neg(self, sub_op_32):
        # 10.0 - (-5.0) = 15.0
        op = NotAddition(num1=10.0, num2=-5.0)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - 15.0) < 1e-6

    def test_ieee754_sub_neg_minus_pos(self, sub_op_32):
        # -10.0 - 5.0 = -15.0
        op = NotAddition(num1=-10.0, num2=5.0)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - (-15.0)) < 1e-6

    # --- Zero cases ---

    def test_ieee754_sub_zero_minus_zero(self, sub_op_32):
        op = NotAddition(num1=0.0, num2=0.0)
        result_arr, result_dec = op.ieee754_sub()
        assert result_dec == 0.0

    def test_ieee754_sub_zero_minus_positive(self, sub_op_32):
        op = NotAddition(num1=0.0, num2=42.5)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - (-42.5)) < 1e-6

    def test_ieee754_sub_zero_minus_negative(self, sub_op_32):
        op = NotAddition(num1=0.0, num2=-42.5)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - 42.5) < 1e-6

    def test_ieee754_sub_positive_minus_zero(self, sub_op_32):
        op = NotAddition(num1=17.25, num2=0.0)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - 17.25) < 1e-6

    def test_ieee754_sub_negative_minus_zero(self, sub_op_32):
        op = NotAddition(num1=-17.25, num2=0.0)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - (-17.25)) < 1e-6

    # --- Fraction precision ---

    def test_ieee754_sub_fraction_precision(self, sub_op_32):
        op = NotAddition(num1=0.3, num2=0.1)
        result_arr, result_dec = op.ieee754_sub()
        # 0.3 - 0.1 = 0.2 (с возможной погрешностью)
        assert abs(result_dec - 0.2) < 1e-6

    # --- Large and small values ---

    def test_ieee754_sub_large_numbers(self, sub_op_32):
        op = NotAddition(num1=1e20, num2=1e19)
        result_arr, result_dec = op.ieee754_sub()
        assert abs(result_dec - 9e19) / 9e19 < 1e-5

    def test_ieee754_sub_small_numbers(self, sub_op_32):
        op = NotAddition(num1=1e-10, num2=1e-11)
        result_arr, result_dec = op.ieee754_sub()
        expected = 9e-11
        if expected != 0:
            assert abs(result_dec - expected) / expected < 1e-5

    # --- Output verification ---

    def test_ieee754_sub_prints_binary_string(self, sub_op_32, capsys):
        op = NotAddition(num1=1.5, num2=0.5)
        op.ieee754_sub()
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

    def test_both_subtraction_methods_consistency(self):
        """Проверка согласованности результатов для целых чисел"""
        op = NotAddition(num1=20, num2=8)

        # Вычитание в дополнительном коде
        _, comp_result = op.subtract_complement()

        # Вычитание в IEEE-754 (целые как float)
        _, ieee_result = op.ieee754_sub()

        # Результаты должны быть близки
        assert abs(comp_result - ieee_result) < 1e-6

    def test_negate_then_add_equals_subtract(self, sub_op_32):
        """Проверка: a - b == a + (-b)"""
        a, b = 15, 7

        # Прямое вычитание
        op1 = NotAddition(num1=a, num2=b)
        _, result_sub = op1.subtract_complement()

        # Сложение с отрицанием через negate_complement
        op2 = NotAddition(num1=a, num2=b)
        comp_b = op2.operator.get_complement_code(b)
        neg_b = op2.negate_complement(comp_b)
        comp_a = op2.operator.get_complement_code(a)
        sum_arr = op2.additor.add_arrays(comp_a, neg_b)
        result_add = op2.operator.array_to_decimal_complement(sum_arr)

        assert result_sub == result_add == a - b

    def test_subtract_complement_uses_add_arrays(self, sub_op_32):
        """Проверка, что subtract_complement использует add_arrays из Addition"""
        op = NotAddition(num1=10, num2=4)

        # Получаем компоненты вручную
        comp1 = op.operator.get_complement_code(10)
        comp2 = op.operator.get_complement_code(4)
        neg_comp2 = op.negate_complement(comp2)

        # Складываем через add_arrays
        manual_result = op.additor.add_arrays(comp1, neg_comp2)

        # Сравниваем с результатом метода
        method_result, _ = op.subtract_complement()
        assert method_result == manual_result


# ============================================================================
# Edge cases and parametrized tests
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_negate_complement_empty_like_array(self, sub_op_32):
        """Отрицание массива из одних нулей"""
        arr = [0] * 16
        result = sub_op_32.negate_complement(arr)
        assert result == [0] * 16

    def test_subtract_complement_large_difference(self, sub_op_32):
        """Большая разница между числами"""
        op = NotAddition(num1=100, num2=-100)
        result_arr, result_dec = op.subtract_complement()
        assert result_dec == 200

    def test_ieee754_sub_very_different_magnitudes(self, sub_op_32):
        """Вычитание чисел с очень разной величиной"""
        op = NotAddition(num1=1e30, num2=1.0)
        result_arr, result_dec = op.ieee754_sub()
        # Меньшее число может "потеряться"
        assert abs(result_dec - 1e30) / 1e30 < 1e-5

    def test_subtract_complement_min_max_8bit(self, sub_op_32):
        """-128 - 127 = -255 (переполнение для 8-bit)"""
        op = NotAddition(num1=-128, num2=127)
        result_arr, result_dec = op.subtract_complement()
        # Ожидаем переполнение
        assert isinstance(result_dec, int)


class TestParametrizedSubtraction:
    """Параметризованные тесты для широкого покрытия"""

    @pytest.mark.parametrize("num1,num2,expected", [
        # Complement subtraction tests
        (10, 3, 7),
        (3, 10, -7),
        (0, 0, 0),
        (0, 5, -5),
        (5, 0, 5),
        (-5, -3, -2),
        (-3, -5, 2),
        (10, -5, 15),
        (-10, 5, -15),
        (42, 42, 0),
    ])
    def test_subtract_complement_parametrized(self, num1, num2, expected):
        op = NotAddition(num1=num1, num2=num2)
        result_arr, result_dec = op.subtract_complement()
        # Для 32-бит переполнение маловероятно для этих значений
        assert result_dec == expected

    @pytest.mark.parametrize("num1,num2,expected", [
        (5.5, 2.0, 3.5),
        (2.0, 5.5, -3.5),
        (0.0, 0.0, 0.0),
        (0.0, 1.5, -1.5),
        (-2.5, -7.5, 5.0),
        (10.0, -5.0, 15.0),
        (0.3, 0.1, 0.2),  # с допуском
    ])
    def test_ieee754_sub_parametrized(self, num1, num2, expected):
        op = NotAddition(num1=num1, num2=num2)
        result_arr, result_dec = op.ieee754_sub()
        if expected != 0:
            rel_err = abs(result_dec - expected) / abs(expected)
            assert rel_err < 1e-5, f"Failed for {num1}-{num2}"
        else:
            assert abs(result_dec) < 1e-6

    @pytest.mark.parametrize("bits,num1,num2", [
        (8, 10, 3),
        (8, -5, 2),
        (16, 100, 50),
        (16, -200, 100),
    ])
    def test_subtract_different_bit_widths(self, bits, num1, num2):
        """Проверка работы с разной разрядностью"""
        op = NotAddition(num1=num1, num2=num2)
        # Биты задаются в BinaryOperator внутри, проверяем тип результата
        result_arr, result_dec = op.subtract_complement()
        assert isinstance(result_dec, int)
        assert len(result_arr) >= 8  # Минимальная длина