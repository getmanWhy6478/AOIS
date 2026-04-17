"""Модуль построения СДНФ и СКНФ"""

from typing import List, Tuple


class NormalFormsBuilder:
    """Класс для построения нормальных форм"""

    @staticmethod
    def build_sdnf(variables: List[str],
                   truth_table: List[Tuple[Tuple[int, ...], int]]) -> Tuple[str, List[int]]:
        """
        Строит СДНФ по таблице истинности.

        Returns:
            Кортеж (строковое представление, числовые наборы)
        """
        terms = []
        nums = []

        for i, (row, res) in enumerate(truth_table):
            if res == 1:
                nums.append(int("".join(map(str, row)), 2))
                term = [var if val == 1 else f"!{var}"
                        for var, val in zip(variables, row)]
                terms.append("&".join(term))

        sdnf_str = " | ".join(terms) if terms else "0"
        return sdnf_str, nums

    @staticmethod
    def build_sknf(variables: List[str],
                   truth_table: List[Tuple[Tuple[int, ...], int]]) -> Tuple[str, List[int]]:
        """
        Строит СКНФ по таблице истинности.

        Returns:
            Кортеж (строковое представление, числовые наборы)
        """
        terms = []
        nums = []

        for i, (row, res) in enumerate(truth_table):
            if res == 0:
                nums.append(int("".join(map(str, row)), 2))
                term = [var if val == 0 else f"!{var}"
                        for var, val in zip(variables, row)]
                terms.append("(" + "|".join(term) + ")")

        sknf_str = " & ".join(terms) if terms else "1"
        return sknf_str, nums

    @staticmethod
    def print_results(sdnf: Tuple[str, List[int]],
                      sknf: Tuple[str, List[int]]) -> None:
        """Выводит результаты построения нормальных форм"""
        print("\n--- СДНФ и СКНФ ---")

        print(f"СДНФ (строка): {sdnf[0]}")
        print(f"СДНФ (числовая): ∑({', '.join(map(str, sdnf[1]))})")

        print(f"СКНФ (строка): {sknf[0]}")
        print(f"СКНФ (числовая): ∏({', '.join(map(str, sknf[1]))})")