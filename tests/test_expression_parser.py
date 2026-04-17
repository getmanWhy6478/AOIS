"""
Тесты для класса ExpressionParser (pytest).
"""

import pytest
from parser.expression_parser import ExpressionParser



class TestExpressionParserVariables:
    """Тесты извлечения переменных"""
    
    def test_parse_single_variable(self):
        parser = ExpressionParser()
        result = parser.parse("a")
        assert parser.variables == ['a']
        assert parser.n_vars == 1
        assert result == "a"
    
    def test_parse_multiple_variables(self):
        parser = ExpressionParser()
        result = parser.parse("a&b|c")
        assert parser.variables == ['a', 'b', 'c']
        assert parser.n_vars == 3
    
    def test_parse_variables_sorted(self):
        parser = ExpressionParser()
        parser.parse("c&a&b")
        assert parser.variables == ['a', 'b', 'c']
    
    def test_parse_duplicate_variables(self):
        parser = ExpressionParser()
        parser.parse("a&a&a")
        assert parser.variables == ['a']
        assert parser.n_vars == 1
    
    def test_parse_no_variables(self):
        parser = ExpressionParser()
        with pytest.raises(ValueError):
            parser.parse("1+1")
    
    def test_parse_invalid_variable(self):
        parser = ExpressionParser()
        with pytest.raises(ValueError):
            parser.parse("x&y")
    
    def test_parse_max_variables(self):
        parser = ExpressionParser()
        parser.parse("a&b&c&d&e")
        assert parser.variables == ['a', 'b', 'c', 'd', 'e']
        assert parser.n_vars == 5


class TestExpressionParserOperators:
    """Тесты операторов"""
    
    def test_parse_not_single(self):
        parser = ExpressionParser()
        result = parser.parse("!a")
        assert result == "(not a)"
    
    def test_parse_not_nested(self):
        parser = ExpressionParser()
        result = parser.parse("!!a")
        assert "not" in result
        assert "a" in result
    
    def test_parse_and_single(self):
        parser = ExpressionParser()
        result = parser.parse("a&b")
        assert result == "(a and b)"
    
    def test_parse_or_single(self):
        parser = ExpressionParser()
        result = parser.parse("a|b")
        assert result == "(a or b)"
    
    def test_parse_implication_single(self):
        parser = ExpressionParser()
        result = parser.parse("a->b")
        assert "impl" in result
        assert "a" in result
        assert "b" in result
    
    def test_parse_equivalence_single(self):
        parser = ExpressionParser()
        result = parser.parse("a~b")
        assert "==" in result


class TestExpressionParserPriority:
    """Тесты приоритета операций"""
    
    def test_priority_not_highest(self):
        parser = ExpressionParser()
        result1 = parser.parse("!a&b")
        result2 = parser.parse("!(a&b)")
        assert result1 != result2
    
    def test_priority_and_before_or(self):
        parser = ExpressionParser()
        result = parser.parse("a|b&c")
        assert "or" in result
        assert "and" in result
    
    def test_priority_impl_lowest(self):
        parser = ExpressionParser()
        result = parser.parse("a&b->c")
        assert "impl" in result
        assert "and" in result
    
    def test_priority_parens_override(self):
        parser = ExpressionParser()
        result1 = parser.parse("a&(b|c)")
        result2 = parser.parse("a&b|c")
        assert result1 != result2


class TestExpressionParserEvaluation:
    """Тесты вычисления"""
    
    def test_evaluate_not(self):
        parser = ExpressionParser()
        parsed = parser.parse("!a")
        
        assert self._eval(parsed, parser.scope, {'a': False}) == 1
        assert self._eval(parsed, parser.scope, {'a': True}) == 0
    
    def test_evaluate_and(self):
        parser = ExpressionParser()
        parsed = parser.parse("a&b")
        
        test_cases = [
            (False, False, 0),
            (False, True, 0),
            (True, False, 0),
            (True, True, 1),
        ]
        
        for a_val, b_val, expected in test_cases:
            result = self._eval(parsed, parser.scope, {'a': a_val, 'b': b_val})
            assert result == expected
    
    def test_evaluate_or(self):
        parser = ExpressionParser()
        parsed = parser.parse("a|b")
        
        test_cases = [
            (False, False, 0),
            (False, True, 1),
            (True, False, 1),
            (True, True, 1),
        ]
        
        for a_val, b_val, expected in test_cases:
            result = self._eval(parsed, parser.scope, {'a': a_val, 'b': b_val})
            assert result == expected
    
    def test_evaluate_implication(self):
        parser = ExpressionParser()
        parsed = parser.parse("a->b")
        
        test_cases = [
            (False, False, 1),
            (False, True, 1),
            (True, False, 0),
            (True, True, 1),
        ]
        
        for a_val, b_val, expected in test_cases:
            result = self._eval(parsed, parser.scope, {'a': a_val, 'b': b_val})
            assert result == expected
    
    def test_evaluate_equivalence(self):
        parser = ExpressionParser()
        parsed = parser.parse("a~b")
        
        test_cases = [
            (False, False, 1),
            (False, True, 0),
            (True, False, 0),
            (True, True, 1),
        ]
        
        for a_val, b_val, expected in test_cases:
            result = self._eval(parsed, parser.scope, {'a': a_val, 'b': b_val})
            assert result == expected
    
    @staticmethod
    def _eval(parsed_expr, scope, variables):
        context = {**variables, **scope}
        result = eval(parsed_expr, {}, context)
        return 1 if result else 0


class TestExpressionParserEdgeCases:
    """Граничные случаи"""
    
    def test_spaces_removed(self):
        parser = ExpressionParser()
        result1 = parser.parse("a&b")
        result2 = parser.parse("a & b")
        result3 = parser.parse(" a & b ")
        assert result1 == result2 == result3
    
    def test_parse_empty_string(self):
        parser = ExpressionParser()
        with pytest.raises(ValueError):
            parser.parse("")
    
    def test_parse_deeply_nested(self):
        parser = ExpressionParser()
        expr = "!(a&(b|!(c->d)))"
        result = parser.parse(expr)
        assert "not" in result
        assert "and" in result
        assert "or" in result
        assert "impl" in result
    
    def test_getters(self):
        parser = ExpressionParser()
        parser.parse("a&b&c")
        
        assert parser.get_variables() == ['a', 'b', 'c']
        assert isinstance(parser.get_safe_expr(), str)
        assert 'impl' in parser.get_scope()