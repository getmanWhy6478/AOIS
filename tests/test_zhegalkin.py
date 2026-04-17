"""
Тесты для класса ZhegalkinBuilder (pytest).
"""

import pytest
from analysis.zhegalkin import ZhegalkinBuilder


class TestZhegalkinBuilderPoly:
    """Тесты построения полинома"""
    
    def test_poly_constant_zero(self):
        func_values = [0, 0, 0, 0]
        variables = ['a', 'b']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "0"
    
    def test_poly_constant_one(self):
        func_values = [1, 1, 1, 1]
        variables = ['a', 'b']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "1"
    
    def test_poly_single_variable(self):
        func_values = [0, 1]
        variables = ['a']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "a"
    
    def test_poly_and_function(self):
        func_values = [0, 0, 0, 1]
        variables = ['a', 'b']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "a&b"
    
    def test_poly_xor_function(self):
        func_values = [0, 1, 1, 0]
        variables = ['a', 'b']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert "a" in poly
        assert "b" in poly
        assert "&" not in poly


class TestZhegalkinBuilderLinearity:
    """Тесты линейности"""
    
    def test_linear_constant_zero(self):
        func_values = [0, 0, 0, 0]
        assert ZhegalkinBuilder.check_linear(func_values) is True
    
    def test_linear_constant_one(self):
        func_values = [1, 1, 1, 1]
        assert ZhegalkinBuilder.check_linear(func_values) is True
    
    def test_linear_xor(self):
        func_values = [0, 1, 1, 0]
        assert ZhegalkinBuilder.check_linear(func_values) is True
    
    def test_nonlinear_and(self):
        func_values = [0, 0, 0, 1]
        assert ZhegalkinBuilder.check_linear(func_values) is False
    
    def test_nonlinear_or(self):
        func_values = [0, 1, 1, 1]
        assert ZhegalkinBuilder.check_linear(func_values) is False


class TestZhegalkinBuilderMonoms:
    """Тесты мономов"""
    
    def test_monoms_constant_zero(self):
        func_values = [0, 0, 0, 0]
        variables = ['a', 'b']
        
        monoms = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        assert monoms == []
    
    def test_monoms_constant_one(self):
        func_values = [1, 1, 1, 1]
        variables = ['a', 'b']
        
        monoms = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        assert monoms == [[]]
    
    def test_monoms_single_variable(self):
        func_values = [0, 1]
        variables = ['a']
        
        monoms = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        assert monoms == [['a']]
    
    def test_monoms_and_function(self):
        func_values = [0, 0, 0, 1]
        variables = ['a', 'b']
        
        monoms = ZhegalkinBuilder.get_poly_as_monoms(func_values, variables)
        assert monoms == [['a', 'b']]


class TestZhegalkinBuilderEdgeCases:
    """Граничные случаи"""
    
    def test_poly_3vars_conjunction(self):
        func_values = [0, 0, 0, 0, 0, 0, 0, 1]
        variables = ['a', 'b', 'c']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "a&b&c"
    
    def test_poly_4vars(self):
        func_values = [0] * 15 + [1]
        variables = ['a', 'b', 'c', 'd']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "a&b&c&d"
    
    def test_poly_5vars(self):
        func_values = [0] * 16 + [1] * 16
        variables = ['a', 'b', 'c', 'd', 'e']
        
        poly = ZhegalkinBuilder.build(func_values, variables)
        assert poly == "a"