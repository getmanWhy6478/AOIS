"""Модуль парсинга логических выражений"""

import re
from typing import List, Dict, Callable


class ExpressionParser:

    def __init__(self):
        self.variables: List[str] = []
        self.n_vars: int = 0
        self.safe_expr: str = ""
        self.scope: Dict[str, Callable] = {}

    def parse(self, expr: str) -> str:
        """
        Преобразует логическое выражение в исполняемый Python-код.

        Args:
            expr: Исходное выражение в строковом виде

        Returns:
            Строка с безопасным Python-выражением
        """
        s = expr.replace(' ', '')

        # Выделяем переменные
        self.variables = sorted(list(set(re.findall(r'[a-e]', s))))
        if not self.variables:
            raise ValueError("Не найдено переменных (a-e)")
        self.n_vars = len(self.variables)

        self.scope = {
            'impl': lambda a, b: (not a) or b,
            'True': True,
            'False': False
        }

        return self._parse_recursive(s)

    def _find_op_outside_parens(self, text: str, op: str) -> int:
        """Находит позицию оператора вне скобок"""
        balance = 0
        positions = []
        i = 0

        while i < len(text):
            if text[i] == '(':
                balance += 1
            elif text[i] == ')':
                balance -= 1
            elif balance == 0:
                if op == '->':
                    if i < len(text) - 1 and text[i:i + 2] == '->':
                        positions.append(i)
                        i += 2
                        continue
                elif op == '~':
                    if text[i] == '~':
                        positions.append(i)
                elif len(op) == 1 and text[i] == op:
                    positions.append(i)
            i += 1

        return positions[-1] if positions else -1

    def _parse_recursive(self, text: str) -> str:
        """Рекурсивный парсинг с учётом приоритета операций"""
        text = text.strip()
        if not text:
            return "False"

        # Удаление внешних скобок
        while text.startswith('(') and text.endswith(')'):
            balance = 0
            is_outer = True
            for i in range(len(text) - 1):
                if text[i] == '(':
                    balance += 1
                elif text[i] == ')':
                    balance -= 1
                if balance == 0:
                    is_outer = False
                    break
            if is_outer:
                text = text[1:-1]
            else:
                break

        # Импликация -> (низший приоритет)
        idx = self._find_op_outside_parens(text, '->')
        if idx != -1:
            left = self._parse_recursive(text[:idx])
            right = self._parse_recursive(text[idx + 2:])
            return f"impl({left}, {right})"

        # Эквиваленция ~
        idx = self._find_op_outside_parens(text, '~')
        if idx != -1:
            left = self._parse_recursive(text[:idx])
            right = self._parse_recursive(text[idx + 1:])
            return f"({left} == {right})"

        # ИЛИ |
        idx = self._find_op_outside_parens(text, '|')
        if idx != -1:
            left = self._parse_recursive(text[:idx])
            right = self._parse_recursive(text[idx + 1:])
            return f"({left} or {right})"

        # И &
        idx = self._find_op_outside_parens(text, '&')
        if idx != -1:
            left = self._parse_recursive(text[:idx])
            right = self._parse_recursive(text[idx + 1:])
            return f"({left} and {right})"

        # НЕ !
        if text.startswith('!'):
            inner = self._parse_recursive(text[1:])
            return f"(not {inner})"

        # Переменная
        if re.match(r'^[a-e]$', text):
            return text

        return text

    def get_variables(self) -> List[str]:
        return self.variables

    def get_safe_expr(self) -> str:
        return self.safe_expr

    def get_scope(self) -> Dict:
        return self.scope