"""Модуль построения полинома Жегалкина"""

from typing import List


class ZhegalkinBuilder:
    """Класс для построения полинома Жегалкина"""

    @staticmethod
    def build(func_values: List[int], variables: List[str]) -> str:
        """
        Строит полином Жегалкина методом треугольника.

        Args:
            func_values: Вектор значений функции
            variables: Список переменных

        Returns:
            Строковое представление полинома
        """
        n = len(func_values)
        triangle = [list(func_values)]
        curr = func_values[:]

        while len(curr) > 1:
            next_row = [curr[i] ^ curr[i + 1] for i in range(len(curr) - 1)]
            triangle.append(next_row)
            curr = next_row

        coeffs = [row[0] for row in triangle]
        terms = []

        if coeffs[0] == 1:
            terms.append("1")

        for i in range(1, n):
            if coeffs[i] == 1:
                bin_i = bin(i)[2:].zfill(len(variables))
                term_vars = [var for var, bit in zip(variables, bin_i) if bit == '1']
                terms.append("&".join(term_vars))

        return " ^ ".join(terms) if terms else "0"

    @staticmethod
    def check_linear(func_values: List[int]) -> bool:
        """Проверяет линейность функции"""
        n = len(func_values)
        triangle = [list(func_values)]
        curr = func_values[:]

        while len(curr) > 1:
            next_row = [curr[i] ^ curr[i + 1] for i in range(len(curr) - 1)]
            triangle.append(next_row)
            curr = next_row

        coeffs = [row[0] for row in triangle]

        for i in range(1, n):
            if coeffs[i] == 1 and bin(i).count('1') > 1:
                return False
        return True

    @staticmethod
    def get_poly_as_monoms(func_values: List[int],
                           variables: List[str]) -> List[List[str]]:
        """
        Возвращает полином как список мономов.

        Returns:
            Список списков, где каждый список — переменные монома
        """
        n = len(func_values)
        triangle = [list(func_values)]
        curr = func_values[:]

        while len(curr) > 1:
            next_row = [curr[i] ^ curr[i + 1] for i in range(len(curr) - 1)]
            triangle.append(next_row)
            curr = next_row

        coeffs = [row[0] for row in triangle]
        monoms = []

        if coeffs[0] == 1:
            monoms.append([])

        for i in range(1, n):
            if coeffs[i] == 1:
                bin_i = bin(i)[2:].zfill(len(variables))
                monom_vars = [var for var, bit in zip(variables, bin_i) if bit == '1']
                monoms.append(monom_vars)

        return monoms