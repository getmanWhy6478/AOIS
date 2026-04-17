"""
Тесты для класса SafeExpressionEvaluator (pytest).
"""

import pytest
from core.function_analyzer import SafeExpressionEvaluator


class TestSafeExpressionEvaluatorBasic:
    """Базовые тесты"""
    
    def test_evaluate_constant_true(self):
        evaluator = SafeExpressionEvaluator()
        result = evaluator.evaluate("True")
        assert result is True
    
    def test_evaluate_constant_false(self):
        evaluator = SafeExpressionEvaluator()
        result = evaluator.evaluate("False")
        assert result is False
    
    def test_evaluate_variable(self):
        evaluator = SafeExpressionEvaluator()
        result = evaluator.evaluate("a", {"a": True})
        assert result is True
    
    def test_evaluate_not(self):
        evaluator = SafeExpressionEvaluator()
        result = evaluator.evaluate("not a", {"a": True})
        assert result is False


class TestSafeExpressionEvaluatorOperators:
    """Тесты операторов"""
    
    def test_evaluate_and(self):
        evaluator = SafeExpressionEvaluator()
        assert evaluator.evaluate("a and b", {"a": True, "b": True}) is True
        assert evaluator.evaluate("a and b", {"a": True, "b": False}) is False
    
    def test_evaluate_or(self):
        evaluator = SafeExpressionEvaluator()
        assert evaluator.evaluate("a or b", {"a": False, "b": True}) is True
        assert evaluator.evaluate("a or b", {"a": False, "b": False}) is False
    
    def test_evaluate_comparison(self):
        evaluator = SafeExpressionEvaluator()
        assert evaluator.evaluate("a == b", {"a": 1, "b": 1}) is True
        assert evaluator.evaluate("a != b", {"a": 1, "b": 2}) is True


class TestSafeExpressionEvaluatorSecurity:
    """Тесты безопасности"""
    
    def test_forbid_import(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("__import__('os')")
    
    def test_forbid_attribute_access(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("().__class__.__mro__")
    
    def test_forbid_function_call(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("eval('1+1')")
    
    def test_forbid_assignment(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("a = 1")


class TestSafeExpressionEvaluatorCache:
    """Тесты кэширования"""
    
    def test_compile_cache(self):
        evaluator = SafeExpressionEvaluator()
        
        # Первое вычисление
        evaluator.evaluate("a and b", {"a": True, "b": True})
        
        # Проверка что AST в кэше
        assert "a and b" in evaluator._compile_cache


class TestSafeExpressionEvaluatorErrors:
    """Тесты ошибок"""
    
    def test_unknown_variable(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("x", {})
    
    def test_syntax_error(self):
        evaluator = SafeExpressionEvaluator()
        with pytest.raises(ValueError):
            evaluator.evaluate("a and")