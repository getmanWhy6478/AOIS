import itertools
import ast
from typing import List, Tuple, Dict, Any
from parser import ExpressionParser


class SafeExpressionEvaluator:
    
    # Разрешённые функции
    ALLOWED_FUNCTIONS = {
        'impl': lambda a, b: (not a) or b,
        'True': True,
        'False': False,
    }
    
    def __init__(self, scope: Dict[str, Any] = None):
        self.scope = {**self.ALLOWED_FUNCTIONS, **(scope or {})}
        self._compile_cache: Dict[str, ast.AST] = {}
    
    def _validate_node(self, node: ast.AST) -> bool:
        # Запрещённые узлы AST
        forbidden_types = {
            ast.Import, ast.ImportFrom, ast.Attribute,
            ast.Subscript, ast.Slice, ast.Lambda, ast.ListComp,
            ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.ClassDef,
            ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign,
            ast.AugAssign, ast.AnnAssign, ast.For, ast.While,
            ast.With, ast.AsyncWith, ast.Try, ast.Raise,
            ast.Assert, ast.Delete, ast.Pass, ast.Break, ast.Continue,
            ast.Return, ast.Yield, ast.YieldFrom, ast.Await,
        }
        
        # Проверяем тип узла
        for forbidden in forbidden_types:
            if isinstance(node, forbidden):
                return False
        
        # Особая проверка для Call - разрешаем только whitelisted функции
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in self.scope:
                    return False
            else:
                return False
        
        for child in ast.iter_child_nodes(node):
            if not self._validate_node(child):
                return False
        
        return True
    
    def _compile(self, expr: str) -> ast.AST:
        if expr in self._compile_cache:
            return self._compile_cache[expr]
        
        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Синтаксическая ошибка: {e}")
        
        if not self._validate_node(tree.body):
            raise ValueError("Выражение содержит запрещённые операции")
        
        self._compile_cache[expr] = tree.body
        return tree.body
    
    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, context)
        
        elif isinstance(node, ast.BoolOp):
            values = [self._eval_node(v, context) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            elif isinstance(node.op, ast.Or):
                return any(values)
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            if isinstance(node.op, ast.Not):
                return not operand
        
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            results = []
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)
                if isinstance(op, ast.Eq):
                    results.append(left == right)
                elif isinstance(op, ast.NotEq):
                    results.append(left != right)
            return all(results)
        
        elif isinstance(node, ast.Name):
            if node.id not in context:
                raise ValueError(f"Неизвестная переменная: {node.id}")
            return context[node.id]
        
        elif isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in context and callable(context[func_name]):
                    args = [self._eval_node(arg, context) for arg in node.args]
                    return context[func_name](*args)
                elif func_name in context:
                    # Для констант True/False
                    return context[func_name]
                else:
                    raise ValueError(f"Неизвестная функция: {func_name}")
        
        elif isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, context)
            if test:
                return self._eval_node(node.body, context)
            else:
                return self._eval_node(node.orelse, context)
        
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            
            if isinstance(node.op, ast.BitAnd):
                return left and right
            elif isinstance(node.op, ast.BitOr):
                return left or right
            elif isinstance(node.op, ast.BitXor):
                return left != right
        
        else:
            raise ValueError(f"Неподдерживаемый узел AST: {type(node).__name__}")
        
        return None
    
    def evaluate(self, expr: str, context: Dict[str, Any] = None) -> Any:
        context = {**self.scope, **(context or {})}
        tree = self._compile(expr)
        return self._eval_node(tree, context)


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