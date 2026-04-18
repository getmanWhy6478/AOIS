import itertools
from typing import List, Tuple, Dict, Any
from parser import ExpressionParser


class FunctionAnalyzer:

    def __init__(self, expression: str):
        self.parser = ExpressionParser()
        self.safe_expr = self.parser.parse(expression)
        self.variables = self.parser.get_variables()
        self.n_vars = len(self.variables)
        
        self.evaluator = SafeExpressionEvaluator(self.parser.scope)

        self.truth_table: List[Tuple[Tuple[int, ...], int]] = []
        self.func_values: List[int] = []

    def build_truth_table(self) -> None:
        self.truth_table = []
        self.func_values = []

        for bits in itertools.product([0, 1], repeat=self.n_vars):
            context = {var: bool(val) for var, val in zip(self.variables, bits)}
            
            try:
                res = self.evaluator.evaluate(self.safe_expr, context)
                val = 1 if res else 0
            except Exception as e:
                raise ValueError(f"Ошибка вычисления на наборе {bits}: {e}")

            self.truth_table.append((bits, val))
            self.func_values.append(val)

    def get_truth_table(self) -> List[Tuple[Tuple[int, ...], int]]:
        return self.truth_table

    def get_func_values(self) -> List[int]:
        return self.func_values

    def index_form(self) -> None:
        if not self.func_values:
            print("Индексная форма функции: 0")
            return
        
        number = ''.join(str(i) for i in self.func_values)
        print(f"Индексная форма функции: {int(number, 2)}")

    def get_variables(self) -> List[str]:
        return self.variables

    def get_n_vars(self) -> int:
        return self.n_vars