"""Модуль поиска фиктивных переменных"""

from typing import List, Tuple


class FictitiousFinder:
    """Класс для поиска фиктивных переменных"""

    @staticmethod
    def find(variables: List[str],
             truth_table: List[Tuple[Tuple[int, ...], int]],
             func_values: List[int]) -> List[str]:
        fictitious = []

        for var_idx, var_name in enumerate(variables):
            is_fict = True

            for i, (row, _) in enumerate(truth_table):
                if row[var_idx] == 0:
                    neighbor = list(row)
                    neighbor[var_idx] = 1
                    neighbor_t = tuple(neighbor)

                    try:
                        j = next(idx for idx, (r, _)
                                 in enumerate(truth_table) if r == neighbor_t)
                        if func_values[i] != func_values[j]:
                            is_fict = False
                            break
                    except StopIteration:
                        pass

            if is_fict:
                fictitious.append(var_name)

        return fictitious

    @staticmethod
    def print_results(fictitious: List[str]) -> None:
        """Выводит результаты поиска"""
        print("\n--- Фиктивные переменные ---")
        if fictitious:
            print(f"Фиктивные переменные: {', '.join(fictitious)}")
        else:
            print("Фиктивных переменных нет")