#!/usr/bin/env python3

import sys
from config import SUPPORTED_VARS, OUTPUT_SETTINGS

from core import FunctionAnalyzer
from analysis import (
    TruthTablePrinter, NormalFormsBuilder, PostClassesChecker,
    ZhegalkinBuilder, FictitiousFinder, BooleanDerivatives
)
from menu.console_menu import ConsoleMenu
from utils.helpers import pause, get_valid_input
from minimization import QuineMcCluskeyMinimizer, KarnaughMinimizer

def validate_expression(expr: str) -> bool:
    """Проверяет корректность выражения"""
    if not expr:
        return False
    # Простая проверка на наличие переменных
    return any(var in expr for var in SUPPORTED_VARS)


def analyze_function(expr: str) -> None:
    """Выполняет полный анализ функции"""
    try:
        # Инициализация
        analyzer = FunctionAnalyzer(expr)
        analyzer.build_truth_table()

        # 1. Таблица истинности
        if OUTPUT_SETTINGS['show_truth_table']:
            TruthTablePrinter.print_table(
                analyzer.get_variables(),
                analyzer.get_truth_table()
            )

        # 2. Нормальные формы
        sdnf = NormalFormsBuilder.build_sdnf(
            analyzer.get_variables(),
            analyzer.get_truth_table()
        )
        sknf = NormalFormsBuilder.build_sknf(
            analyzer.get_variables(),
            analyzer.get_truth_table()
        )
        NormalFormsBuilder.print_results(sdnf, sknf)
        analyzer.index_form()

        # 3. Классы Поста
        t0 = PostClassesChecker.check_t0(analyzer.get_func_values())
        t1 = PostClassesChecker.check_t1(analyzer.get_func_values())
        s = PostClassesChecker.check_selfdual(analyzer.get_func_values())
        m = PostClassesChecker.check_monotonic(
            analyzer.get_truth_table(),
            analyzer.get_n_vars()
        )
        PostClassesChecker.print_results(t0, t1, s, m)

        # 4. Полином Жегалкина
        poly = ZhegalkinBuilder.build(
            analyzer.get_func_values(),
            analyzer.get_variables()
        )
        print(f"\n--- Полином Жегалкина ---\n{poly}")
        is_linear = ZhegalkinBuilder.check_linear(analyzer.get_func_values())
        print(f"Класс L (линейная): {'Да' if is_linear else 'Нет'}")

        # 5. Фиктивные переменные
        fict = FictitiousFinder.find(
            analyzer.get_variables(),
            analyzer.get_truth_table(),
            analyzer.get_func_values()
        )
        FictitiousFinder.print_results(fict)

        # 6. Булевы производные
        if OUTPUT_SETTINGS['show_derivatives']:
            BooleanDerivatives.print_all(
                analyzer.get_func_values(),
                analyzer.get_variables(),
                analyzer.get_n_vars()
            )

        # 7. Минимизация
        if OUTPUT_SETTINGS['show_minimization'] and sdnf[1]:
            # Расчётный метод
            print("\n--- Минимизация расчётным методом  ---")
            min_calc = QuineMcCluskeyMinimizer.minimize(
                sdnf[1],  # наборы где F=1
                analyzer.get_func_values(),  # вектор значений
                analyzer.get_variables(),
                show_steps=True,
                forms=['both']
            )
            print(f"\nМинимальная форма: {min_calc}")
            print("(Минимизация Куайна-МакКласки)")
            # Табличный метод
            QuineMcCluskeyMinimizer.print_tabular(
                sdnf[1],
                analyzer.get_func_values(),
                analyzer.get_variables(),
                form='dnf'
            )
            print("\n Табличный метод (КНФ):")
            QuineMcCluskeyMinimizer.print_tabular(
                sdnf[1],
                analyzer.get_func_values(),
                analyzer.get_variables(),
                form='cnf'
            )
            # Карта Карно
            KarnaughMinimizer.print_map(
                analyzer.get_func_values(),
                analyzer.get_variables(),
                analyzer.get_n_vars()
            )

    except Exception as e:
        print(f"\nОшибка анализа: {e}")
        pause()


def main_menu() -> None:
    """Главное меню программы"""
    menu = ConsoleMenu()

    menu.add_item("Анализ новой функции",
                  lambda: run_analysis(),
                  "Ввести выражение и выполнить анализ")
    menu.add_separator()
    menu.add_exit("Выход")

    menu.run()


def run_analysis() -> None:
    """Запуск анализа функции"""

    print("\nПоддерживаемые операции:")
    print("  !  — НЕ (отрицание)")
    print("  &  — И (конъюнкция)")
    print("  |  — ИЛИ (дизъюнкция)")
    print("  -> — Импликация")
    print("  ~  — Эквиваленция")
    print(f"\nПеременные: {', '.join(SUPPORTED_VARS)}")
    print("Пример: !(!a->!b)|c\n")

    expr = get_valid_input(
        "Введите функцию: ",
        validate_expression,
        "Выражение должно содержать переменные a-e"
    )

    analyze_function(expr)


def show_help() -> None:
    """Показ справки"""

    help_text = """

Формат ввода:
• Используйте переменные: a, b, c, d, e
• Операции: ! & | -> ~
• Скобки для изменения приоритета

Примеры:
  !a | b&c
  (a->b) & !c
  a~b | !c->d
"""
    print(help_text)
    pause()



if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)