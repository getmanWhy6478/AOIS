"""Модуль вычисления булевых производных через полином Жегалкина"""

from typing import List
from analysis.zhegalkin import ZhegalkinBuilder


class BooleanDerivatives:
    """Класс для вычисления булевых производных"""

    @staticmethod
    def _substitute_in_poly(monoms: List[List[str]],
                            var_name: str,
                            value: int) -> List[List[str]]:
        """Подставляет значение в полином Жегалкина"""
        new_monoms = []

        for monom in monoms:
            if var_name not in monom:
                new_monoms.append(monom[:])
            else:
                if value == 1:
                    new_monom = [v for v in monom if v != var_name]
                    new_monoms.append(new_monom)
                # value == 0: моном исчезает

        return new_monoms

    @staticmethod
    def _xor_polys(poly1: List[List[str]],
                   poly2: List[List[str]]) -> List[List[str]]:
        """XOR двух полиномов (сокращение одинаковых мономов)"""
        all_monoms = poly1[:] + poly2[:]
        monom_count = {}

        for monom in all_monoms:
            key = tuple(sorted(monom))
            monom_count[key] = monom_count.get(key, 0) + 1

        return [list(key) for key, count in monom_count.items() if count % 2 == 1]

    @staticmethod
    def _poly_to_str(monoms: List[List[str]]) -> str:
        """Преобразует полином в строку"""
        if not monoms:
            return "0"

        terms = []
        for monom in monoms:
            terms.append("1" if not monom else "&".join(monom))

        return " ^ ".join(terms)

    @staticmethod
    def compute_partial(func_values: List[int],
                        variables: List[str],
                        var_name: str) -> str:
        """Вычисляет частную производную ∂F/∂var"""
        poly = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)

        poly_0 = BooleanDerivatives._substitute_in_poly(poly, var_name, 0)
        poly_1 = BooleanDerivatives._substitute_in_poly(poly, var_name, 1)

        deriv_poly = BooleanDerivatives._xor_polys(poly_0, poly_1)
        return BooleanDerivatives._poly_to_str(deriv_poly)

    @staticmethod
    def compute_mixed(func_values: List[int],
                      variables: List[str],
                      var_names: List[str]) -> str:
        """Вычисляет смешанную производную"""
        poly = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        result_poly = []

        for mask in range(2 ** len(var_names)):
            current_poly = poly[:]
            for i, var_name in enumerate(var_names):
                value = 1 if (mask & (1 << i)) else 0
                current_poly = BooleanDerivatives._substitute_in_poly(
                    current_poly, var_name, value)
            result_poly = BooleanDerivatives._xor_polys(result_poly, current_poly)

        return BooleanDerivatives._poly_to_str(result_poly)

    @staticmethod
    def print_all(func_values: List[int], variables: List[str], n_vars: int) -> None:
        """Выводит все производные"""
        print("\n--- Булевы производные ---")

        # Полином для справки
        poly = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        print(f"Полином Жегалкина: {BooleanDerivatives._poly_to_str(poly)}")

        # Частные производные
        print("\nЧастные производные 1-го порядка:")
        for var in variables:
            deriv = BooleanDerivatives.compute_partial(func_values, variables, var)
            print(f"∂F/∂{var} = {deriv}")

        # Смешанные 2-го порядка
        if n_vars >= 2:
            print("\nСмешанные производные 2-го порядка:")
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    vars_pair = [variables[i], variables[j]]
                    mixed = BooleanDerivatives.compute_mixed(func_values, variables, vars_pair)
                    print(f"∂²F/∂{variables[i]}∂{variables[j]} = {mixed}")

        # Смешанные 3-го порядка
        if n_vars >= 3:
            print("\nСмешанные производные 3-го порядка:")
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    for k in range(j + 1, n_vars):
                        vars_triplet = [variables[i], variables[j], variables[k]]
                        mixed3 = BooleanDerivatives.compute_mixed(func_values, variables, vars_triplet)
                        print(f"∂³F/∂{variables[i]}∂{variables[j]}∂{variables[k]} = {mixed3}")

        # Смешанные 4-го порядка
        if n_vars >= 4:
            print("\nСмешанные производные 4-го порядка:")
            vars_quad = variables[:4]
            mixed4 = BooleanDerivatives.compute_mixed(func_values, variables, vars_quad)
            print(f"∂⁴F/∂{'∂'.join(vars_quad)} = {mixed4}")