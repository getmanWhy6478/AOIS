from typing import List, Tuple


class TruthTablePrinter:
    """Класс для форматированного вывода таблицы истинности"""

    @staticmethod
    def print_table(variables: List[str],
                    truth_table: List[Tuple[Tuple[int, ...], int]]) -> None:
        """
        Выводит таблицу истинности в консоль.

        Args:
            variables: Список имён переменных
            truth_table: Таблица истинности
        """
        print("\n--- Таблица истинности ---")
        header = " | ".join(variables) + " | F"
        print(header)
        print("-" * len(header))

        for row, res in truth_table:
            line = " | ".join(str(x) for x in row) + f" | {res}"
            print(line)