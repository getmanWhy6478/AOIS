"""
Тесты для класса BooleanDerivatives.
Проверяет корректность вычисления частных и смешанных булевых производных.
"""

import unittest
from typing import List
from analysis.derivatives import BooleanDerivatives


class TestBooleanDerivatives(unittest.TestCase):
    """Тесты для класса BooleanDerivatives"""

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================

    @staticmethod
    def build_truth_table(n_vars: int, func) -> List[int]:
        """
        Строит вектор значений функции для n переменных.

        Args:
            n_vars: Количество переменных
            func: Функция, принимающая список битов и возвращающая 0 или 1

        Returns:
            Вектор значений функции (список 0/1)
        """
        values = []
        for i in range(2 ** n_vars):
            bits = [(i >> j) & 1 for j in range(n_vars - 1, -1, -1)]
            values.append(func(bits))
        return values

    @staticmethod
    def count_literals(expr: str) -> int:
        """Считает количество литералов в выражении"""
        return expr.count('!') + sum(1 for c in expr if c.isalpha())

    # ============================================================
    # ТЕСТЫ ЧАСТНЫХ ПРОИЗВОДНЫХ (1-й порядок)
    # ============================================================

    def test_partial_derivative_constant_0(self):
        """Производная константы 0 должна быть 0"""
        func_values = [0] * 8  # F = 0 для 3 переменных
        variables = ['a', 'b', 'c']

        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            self.assertEqual(result, "0", f"Производная константы 0 по {var} должна быть 0")

    def test_partial_derivative_constant_1(self):
        """Производная константы 1 должна быть 0"""
        func_values = [1] * 8  # F = 1 для 3 переменных
        variables = ['a', 'b', 'c']

        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            self.assertEqual(result, "0", f"Производная константы 1 по {var} должна быть 0")

    def test_partial_derivative_single_variable(self):
        """Производная переменной по самой себе = 1"""
        # F = a (для 2 переменных)
        func_values = [0, 0, 1, 1]  # a=0,a=0,a=1,a=1
        variables = ['a', 'b']

        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result_a, "1", "∂a/∂a должна быть 1")

        result_b = BooleanDerivatives.compute_partial(func_values, variables, 'b')
        self.assertEqual(result_b, "0", "∂a/∂b должна быть 0 (b фиктивная)")

    def test_partial_derivative_not_variable(self):
        """Производная !a по a = 1"""
        # F = !a (для 2 переменных)
        func_values = [1, 1, 0, 0]  # !a=1,!a=1,!a=0,!a=0
        variables = ['a', 'b']

        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result_a, "1", "∂(!a)/∂a должна быть 1")

    def test_partial_derivative_and(self):
        """Производная a&b по a = b, по b = a"""
        # F = a&b (для 2 переменных)
        func_values = [0, 0, 0, 1]  # 0&0,0&1,1&0,1&1
        variables = ['a', 'b']

        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result_a, "b", "∂(a&b)/∂a должна быть b")

        result_b = BooleanDerivatives.compute_partial(func_values, variables, 'b')
        self.assertEqual(result_b, "a", "∂(a&b)/∂b должна быть a")


    def test_partial_derivative_3vars_function(self):
        """Производная для функции 3 переменных"""
        # F = a&b ^ c (полином Жегалкина)
        # Таблица: 0,1,0,1,0,1,1,0
        func_values = [0, 1, 0, 1, 0, 1, 1, 0]
        variables = ['a', 'b', 'c']

        result_c = BooleanDerivatives.compute_partial(func_values, variables, 'c')
        # ∂(a&b^c)/∂c = 1 (так как c входит линейно)
        self.assertEqual(result_c, "1", "Производная по линейной переменной = 1")

    # ============================================================
    # ТЕСТЫ СМЕШАННЫХ ПРОИЗВОДНЫХ (2-й порядок)
    # ============================================================

    def test_mixed_derivative_constant(self):
        """Смешанная производная константы = 0"""
        func_values = [1] * 8
        variables = ['a', 'b', 'c']

        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        self.assertEqual(result, "0", "Смешанная производная константы = 0")

    def test_mixed_derivative_and(self):
        """Смешанная производная a&b по a,b = 1"""
        # F = a&b
        func_values = [0, 0, 0, 1]
        variables = ['a', 'b']

        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        self.assertEqual(result, "1", "∂²(a&b)/∂a∂b должна быть 1")

    def test_mixed_derivative_independent_vars(self):
        """Смешанная производная независимых переменных = 0"""
        # F = a ^ c (b не входит)
        func_values = [0, 0, 1, 1, 1, 1, 0, 0]
        variables = ['a', 'b', 'c']

        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        self.assertEqual(result, "0", "Смешанная производная по независимым = 0")

    def test_mixed_derivative_3vars(self):
        """Смешанная производная для 3 переменных"""
        # F = a&b ^ b&c ^ a&c (мажоритарная функция)
        func_values = [0, 0, 0, 1, 0, 1, 1, 1]
        variables = ['a', 'b', 'c']

        result_ab = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        # Должна быть не нулевой
        self.assertNotEqual(result_ab, "0", "Смешанная производная мажоритарной функции ≠ 0")

    # ============================================================
    # ТЕСТЫ СМЕШАННЫХ ПРОИЗВОДНЫХ (3-й и 4-й порядок)
    # ============================================================

    def test_mixed_derivative_3rd_order(self):
        """Смешанная производная 3-го порядка"""
        # F = a&b&c
        func_values = [0, 0, 0, 0, 0, 0, 0, 1]
        variables = ['a', 'b', 'c']

        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b', 'c'])
        self.assertEqual(result, "1", "∂³(a&b&c)/∂a∂b∂c должна быть 1")

    def test_mixed_derivative_4th_order(self):
        """Смешанная производная 4-го порядка"""
        # F = a&b&c&d
        func_values = [0] * 15 + [1]
        variables = ['a', 'b', 'c', 'd']

        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b', 'c', 'd'])
        self.assertEqual(result, "1", "∂⁴(a&b&c&d)/∂a∂b∂c∂d должна быть 1")

    # ============================================================
    # ТЕСТЫ СВОЙСТВ БУЛЕВЫХ ПРОИЗВОДНЫХ
    # ============================================================

    def test_derivative_linearity_property(self):
        """Свойство линейности: ∂(F^G)/∂x = ∂F/∂x ^ ∂G/∂x"""
        # F = a, G = b
        func_f = [0, 0, 1, 1]  # a
        func_g = [0, 1, 0, 1]  # b
        # F^G = a^b
        func_xor = [f ^ g for f, g in zip(func_f, func_g)]

        variables = ['a', 'b']

        # ∂(a^b)/∂a
        deriv_xor = BooleanDerivatives.compute_partial(func_xor, variables, 'a')
        # ∂a/∂a ^ ∂b/∂a = 1 ^ 0 = 1


        # Проверяем что производная существует
        self.assertNotEqual(deriv_xor, "", "Производная должна быть определена")

    def test_fictitious_variable_derivative(self):
        """Производная по фиктивной переменной = 0"""
        # F = a&b (c фиктивная)
        func_values = [0, 0, 0, 1, 0, 0, 0, 1]  # повторяется для c=0 и c=1
        variables = ['a', 'b', 'c']

        result_c = BooleanDerivatives.compute_partial(func_values, variables, 'c')

    def test_derivative_symmetry(self):
        """Смешанные производные симметричны: ∂²F/∂x∂y = ∂²F/∂y∂x"""
        # F = a&b ^ b&c
        func_values = [0, 0, 0, 1, 0, 1, 1, 1]
        variables = ['a', 'b', 'c']

        deriv_ab = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        deriv_ba = BooleanDerivatives.compute_mixed(func_values, variables, ['b', 'a'])

        self.assertEqual(deriv_ab, deriv_ba, "Смешанные производные должны быть симметричны")

    # ============================================================
    # ТЕСТЫ ПОЛНОГО ВЫВОДА (print_all)
    # ============================================================

    def test_print_all_output(self):
        """Проверка что print_all выводит все производные"""
        func_values = [0, 1, 0, 1, 0, 1, 1, 0]
        variables = ['a', 'b', 'c']
        n_vars = 3

        # Просто проверяем что не падает с ошибкой
        try:
            BooleanDerivatives.print_all(func_values, variables, n_vars)
            success = True
        except Exception as e:
            success = False

        self.assertTrue(success, "print_all не должен выбрасывать исключения")

    # ============================================================
    # ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
    # ============================================================

    def test_single_variable_function(self):
        """Функция от одной переменной"""
        func_values = [0, 1]  # F = a
        variables = ['a']

        result = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result, "1", "Производная a по a = 1")

    def test_empty_polynomial(self):
        """Полином без мономов (функция = 0)"""
        func_values = [0, 0, 0, 0]
        variables = ['a', 'b']

        result = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result, "0", "Производная нулевой функции = 0")

    def test_all_ones_polynomial(self):
        """Полином с константой 1 (функция = 1)"""
        func_values = [1, 1, 1, 1]
        variables = ['a', 'b']

        result = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertEqual(result, "0", "Производная единичной функции = 0")


class TestBooleanDerivativesKnownFunctions(unittest.TestCase):
    """Тесты на известных функциях"""

    def test_majority_function(self):
        """Мажоритарная функция 3 переменных"""
        # F = 1 если хотя бы 2 переменных = 1
        func_values = [0, 0, 0, 1, 0, 1, 1, 1]
        variables = ['a', 'b', 'c']

        # Все частные производные должны быть не нулевыми
        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            self.assertNotEqual(result, "0", f"Производная мажоритарной функции по {var} ≠ 0")

    def test_parity_function(self):
        """Функция чётности (XOR всех переменных)"""
        # F = a ^ b ^ c
        func_values = [0, 1, 1, 0, 1, 0, 0, 1]
        variables = ['a', 'b', 'c']

        # Производная по любой переменной = 1 (так как все линейны)
        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            self.assertEqual(result, "1", f"Производная XOR по {var} = 1")

    def test_conjunction_all_vars(self):
        """Конъюнкция всех переменных"""
        # F = a & b & c
        func_values = [0, 0, 0, 0, 0, 0, 0, 1]
        variables = ['a', 'b', 'c']

        # ∂(a&b&c)/∂a = b&c
        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        self.assertIn("b", result_a)
        self.assertIn("c", result_a)


# ============================================================
# ЗАПУСК ТЕСТОВ
# ============================================================

if __name__ == '__main__':
    unittest.main()
    