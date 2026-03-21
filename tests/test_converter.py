import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils.ArrayStringConverter import ArrayStringConverter


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def converter():
    """Создание экземпляра ArrayStringConverter для тестов"""
    return ArrayStringConverter()


# ============================================================================
# Tests for __init__
# ============================================================================

class TestArrayStringConverterInit:
    """Тесты инициализации класса"""

    def test_init_creates_empty_array(self):
        conv = ArrayStringConverter()
        assert conv.array == []
        assert isinstance(conv.array, list)

    def test_init_multiple_instances_independent(self):
        conv1 = ArrayStringConverter()
        conv2 = ArrayStringConverter()

        conv1.array = [1, 0, 1]
        assert conv2.array == []  # Независимые экземпляры
        assert conv1.array == [1, 0, 1]


# ============================================================================
# Tests for array_to_string
# ============================================================================

class TestArrayToString:
    """Тесты метода array_to_string"""

    # --- Empty and single element ---

    def test_array_to_string_empty(self, converter):
        result = converter.array_to_string([])
        assert result == ""
        assert isinstance(result, str)

    def test_array_to_string_single_zero(self, converter):
        result = converter.array_to_string([0])
        assert result == "0"

    def test_array_to_string_single_one(self, converter):
        result = converter.array_to_string([1])
        assert result == "1"

    # --- Multiple elements ---

    def test_array_to_string_all_zeros(self, converter):
        result = converter.array_to_string([0, 0, 0, 0])
        assert result == "0000"

    def test_array_to_string_all_ones(self, converter):
        result = converter.array_to_string([1, 1, 1, 1])
        assert result == "1111"

    def test_array_to_string_mixed_bits(self, converter):
        result = converter.array_to_string([1, 0, 1, 0, 1, 1, 0, 0])
        assert result == "10101100"

    def test_array_to_string_alternating(self, converter):
        result = converter.array_to_string([1, 0, 1, 0, 1, 0])
        assert result == "101010"

    # --- Large arrays ---

    def test_array_to_string_32_bits(self, converter):
        arr = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = converter.array_to_string(arr)
        assert len(result) == 32
        assert result[0] == "1"
        assert result[-1] == "1"

    def test_array_to_string_64_bits_pattern(self, converter):
        arr = [i % 2 for i in range(64)]
        result = converter.array_to_string(arr)
        assert len(result) == 64
        assert result == "01" * 32

    # --- Edge cases with integers ---

    def test_array_to_string_with_integer_values(self, converter):
        """Проверка, что метод работает с целыми числами 0 и 1"""
        result = converter.array_to_string([0, 1, 0, 1])
        assert result == "0101"
        # Проверяем тип элементов результата
        assert all(c in "01" for c in result)

    def test_array_to_string_preserves_order(self, converter):
        """Проверка сохранения порядка элементов"""
        original = [1, 1, 0, 0, 1, 0, 1, 0]
        result = converter.array_to_string(original)
        for i, bit in enumerate(original):
            assert result[i] == str(bit)


# ============================================================================
# Tests for string_to_array
# ============================================================================

class TestStringToArray:
    """Тесты метода string_to_array"""

    # --- Empty and single character ---

    def test_string_to_array_empty(self, converter):
        result = converter.string_to_array("")
        assert result == []
        assert isinstance(result, list)

    def test_string_to_array_single_zero(self, converter):
        result = converter.string_to_array("0")
        assert result == [0]
        assert all(isinstance(b, int) for b in result)

    def test_string_to_array_single_one(self, converter):
        result = converter.string_to_array("1")
        assert result == [1]

    # --- Multiple characters ---

    def test_string_to_array_all_zeros(self, converter):
        result = converter.string_to_array("0000")
        assert result == [0, 0, 0, 0]

    def test_string_to_array_all_ones(self, converter):
        result = converter.string_to_array("1111")
        assert result == [1, 1, 1, 1]

    def test_string_to_array_mixed_bits(self, converter):
        result = converter.string_to_array("10101100")
        assert result == [1, 0, 1, 0, 1, 1, 0, 0]

    def test_string_to_array_alternating(self, converter):
        result = converter.string_to_array("101010")
        assert result == [1, 0, 1, 0, 1, 0]

    # --- Large strings ---

    def test_string_to_array_32_chars(self, converter):
        s = "1" + "0" * 30 + "1"
        result = converter.string_to_array(s)
        assert len(result) == 32
        assert result[0] == 1
        assert result[-1] == 1
        assert all(b in (0, 1) for b in result)

    def test_string_to_array_64_chars_pattern(self, converter):
        s = "01" * 32
        result = converter.string_to_array(s)
        assert len(result) == 64
        assert result == [i % 2 for i in range(64)]

    # --- Type conversion verification ---

    def test_string_to_array_returns_integers(self, converter):
        """Проверка, что элементы результата — целые числа, не строки"""
        result = converter.string_to_array("1010")
        assert all(isinstance(b, int) for b in result)
        assert all(not isinstance(b, str) for b in result)
        assert result == [1, 0, 1, 0]


# ============================================================================
# Tests for round-trip conversions
# ============================================================================

class TestRoundTripConversions:
    """Тесты сквозного преобразования: array → string → array"""

    def test_roundtrip_empty(self, converter):
        original = []
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_single_zero(self, converter):
        original = [0]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_single_one(self, converter):
        original = [1]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_mixed_small(self, converter):
        original = [1, 0, 1, 1, 0]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_8_bits(self, converter):
        original = [1, 0, 1, 0, 1, 1, 0, 0]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_32_bits(self, converter):
        original = [i % 2 for i in range(32)]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_64_bits(self, converter):
        original = [1 if i % 3 == 0 else 0 for i in range(64)]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original

    def test_roundtrip_preserves_order(self, converter):
        """Проверка, что порядок битов сохраняется при круговом преобразовании"""
        original = [1, 1, 0, 0, 1, 0, 1, 0, 1, 1]
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        for i in range(len(original)):
            assert result[i] == original[i]


# ============================================================================
# Integration tests with other components
# ============================================================================

class TestIntegration:
    """Интеграционные тесты использования конвертера"""

    def test_converter_with_binary_patterns(self, converter):
        """Использование конвертера с типичными бинарными паттернами"""
        test_cases = [
            ([0, 0, 0, 0], "0000"),
            ([1, 1, 1, 1], "1111"),
            ([1, 0, 0, 0, 0, 0, 0, 0], "10000000"),  # MSB set
            ([0, 0, 0, 0, 0, 0, 0, 1], "00000001"),  # LSB set
        ]

        for arr, expected_str in test_cases:
            assert converter.array_to_string(arr) == expected_str
            assert converter.string_to_array(expected_str) == arr

    def test_converter_independence_from_instance_state(self, converter):
        """Проверка, что методы не зависят от внутреннего состояния объекта"""
        # Устанавливаем внутреннее состояние
        converter.array = [1, 1, 1]

        # Методы должны работать с переданными аргументами, не с self.array
        result1 = converter.array_to_string([0, 0])
        assert result1 == "00"

        result2 = converter.string_to_array("10")
        assert result2 == [1, 0]

        # self.array не должен измениться
        assert converter.array == [1, 1, 1]


# ============================================================================
# Edge cases and error handling
# ============================================================================

class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_array_to_string_with_large_integers(self, converter):
        """Проверка поведения с числами != 0, 1 (некорректный ввод)"""
        # Метод использует str(b), поэтому 2 станет "2"
        result = converter.array_to_string([0, 1, 2, 3])
        assert result == "0123"
        # Это ожидаемое поведение — метод не валидирует вход

    def test_string_to_array_with_non_binary_chars(self, converter):
        """Проверка поведения с не-бинарными символами"""
        # Метод использует int(c), поэтому "2" станет 2
        result = converter.string_to_array("0123")
        assert result == [0, 1, 2, 3]
        # Это ожидаемое поведение — метод не валидирует вход

    def test_string_to_array_with_whitespace(self, converter):
        """Проверка обработки пробельных символов"""
        # int(' ') вызовет ValueError — это ожидаемое поведение
        with pytest.raises(ValueError):
            converter.string_to_array("1 0 1")

    def test_string_to_array_with_newline(self, converter):
        """Проверка обработки символа новой строки"""
        with pytest.raises(ValueError):
            converter.string_to_array("101\n")

    def test_array_to_string_with_boolean_values(self, converter):
        """Проверка работы с булевыми значениями (True/False)"""
        # bool является подклассом int в Python
        result = converter.array_to_string([True, False, True])
        assert result == "TrueFalseTrue"  # str(True) = "True"
        # Это показывает, что метод ожидает именно 0/1, не bool

    def test_string_to_array_with_leading_zeros(self, converter):
        """Проверка сохранения ведущих нулей"""
        result = converter.string_to_array("000101")
        assert result == [0, 0, 0, 1, 0, 1]
        # Ведущие нули сохраняются, что важно для битовых представлений


# ============================================================================
# Parametrized tests for comprehensive coverage
# ============================================================================

class TestParametrizedConversion:
    """Параметризованные тесты для широкого покрытия"""

    @pytest.mark.parametrize("arr,expected", [
        ([], ""),
        ([0], "0"),
        ([1], "1"),
        ([0, 0], "00"),
        ([1, 1], "11"),
        ([0, 1], "01"),
        ([1, 0], "10"),
        ([1, 0, 1, 0], "1010"),
        ([0, 0, 0, 0, 1, 1, 1, 1], "00001111"),
        ([1] * 16, "1" * 16),
        ([0] * 16, "0" * 16),
    ])
    def test_array_to_string_parametrized(self, converter, arr, expected):
        result = converter.array_to_string(arr)
        assert result == expected
        assert isinstance(result, str)

    @pytest.mark.parametrize("s,expected", [
        ("", []),
        ("0", [0]),
        ("1", [1]),
        ("00", [0, 0]),
        ("11", [1, 1]),
        ("01", [0, 1]),
        ("10", [1, 0]),
        ("1010", [1, 0, 1, 0]),
        ("00001111", [0, 0, 0, 0, 1, 1, 1, 1]),
        ("1" * 16, [1] * 16),
        ("0" * 16, [0] * 16),
    ])
    def test_string_to_array_parametrized(self, converter, s, expected):
        result = converter.string_to_array(s)
        assert result == expected
        assert all(isinstance(b, int) for b in result)

    @pytest.mark.parametrize("original", [
        [],
        [0],
        [1],
        [0, 1],
        [1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 0],
        [i % 2 for i in range(32)],
        [1 if i % 3 == 0 else 0 for i in range(20)],
    ])
    def test_roundtrip_parametrized(self, converter, original):
        """Параметризованный тест кругового преобразования"""
        s = converter.array_to_string(original)
        result = converter.string_to_array(s)
        assert result == original
        # Дополнительная проверка типов
        assert all(isinstance(b, int) for b in result)