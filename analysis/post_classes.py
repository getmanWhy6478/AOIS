"""Модуль проверки классов Поста"""

from typing import List, Tuple


class PostClassesChecker:
    """Класс для проверки принадлежности функции классам Поста"""

    @staticmethod
    def check_t0(func_values: List[int]) -> bool:
        """Проверяет сохранение 0: f(0,0,...,0) = 0"""
        return func_values[0] == 0

    @staticmethod
    def check_t1(func_values: List[int]) -> bool:
        """Проверяет сохранение 1: f(1,1,...,1) = 1"""
        return func_values[-1] == 1

    @staticmethod
    def check_selfdual(func_values: List[int]) -> bool:
        """Проверяет самодвойственность: f(x) = ¬f(¬x)"""
        n = len(func_values)
        for i in range(n):
            inv_idx = (n - 1) - i
            if func_values[i] == func_values[inv_idx]:
                return False
        return True

    @staticmethod
    def check_monotonic(truth_table: List[Tuple[Tuple[int, ...], int]],
                        n_vars: int) -> bool:
        """Проверяет монотонность"""
        n = len(truth_table)
        for i in range(n):
            for j in range(n):
                row_i = truth_table[i][0]
                row_j = truth_table[j][0]
                if all(row_i[k] <= row_j[k] for k in range(n_vars)):
                    if truth_table[i][1] > truth_table[j][1]:
                        return False
        return True

    @staticmethod
    def print_results(t0: bool, t1: bool, s: bool, m: bool) -> None:
        """Выводит результаты проверки классов Поста"""
        print("\n--- Классы Поста ---")
        print(f"Класс T0 (сохраняет 0): {'Да' if t0 else 'Нет'}")
        print(f"Класс T1 (сохраняет 1): {'Да' if t1 else 'Нет'}")
        print(f"Класс S (самодвойственная): {'Да' if s else 'Нет'}")
        print(f"Класс M (монотонная): {'Да' if m else 'Нет'}")