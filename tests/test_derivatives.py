"""
Тесты для класса BooleanDerivatives (pytest).
"""

import pytest
from analysis.derivatives import BooleanDerivatives


class TestBooleanDerivativesPartial:
    """Тесты частных производных"""
    
    def test_partial_derivative_constant_0(self):
        func_values = [0] * 8
        variables = ['a', 'b', 'c']
        
        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            assert result == "0"
    
    def test_partial_derivative_constant_1(self):
        func_values = [1] * 8
        variables = ['a', 'b', 'c']
        
        for var in variables:
            result = BooleanDerivatives.compute_partial(func_values, variables, var)
            assert result == "0"
    
    def test_partial_derivative_single_variable(self):
        func_values = [0, 0, 1, 1]
        variables = ['a', 'b']
        
        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        assert result_a == "1"
        
        result_b = BooleanDerivatives.compute_partial(func_values, variables, 'b')
        assert result_b == "0"
    
    def test_partial_derivative_and(self):
        func_values = [0, 0, 0, 1]
        variables = ['a', 'b']
        
        result_a = BooleanDerivatives.compute_partial(func_values, variables, 'a')
        assert result_a == "b"
        
        result_b = BooleanDerivatives.compute_partial(func_values, variables, 'b')
        assert result_b == "a"


class TestBooleanDerivativesMixed:
    """Тесты смешанных производных"""
    
    def test_mixed_derivative_constant(self):
        func_values = [1] * 8
        variables = ['a', 'b', 'c']
        
        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        assert result == "0"
    
    def test_mixed_derivative_and(self):
        func_values = [0, 0, 0, 1]
        variables = ['a', 'b']
        
        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b'])
        assert result == "1"
    
    def test_mixed_derivative_3rd_order(self):
        func_values = [0] * 7 + [1]
        variables = ['a', 'b', 'c']
        
        result = BooleanDerivatives.compute_mixed(func_values, variables, ['a', 'b', 'c'])
        assert result == "1"