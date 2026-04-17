"""
Тесты для класса FictitiousFinder (pytest).
"""

import pytest
from analysis.fictitious import FictitiousFinder


class TestFictitiousFinderBasic:
    """Базовые тесты"""
    
    def test_no_fictitious_variables(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        func_values = [0, 0, 0, 1]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert result == []
    
    def test_all_variables_fictitious(self):
        variables = ['a', 'b', 'c']
        truth_table = [((0, 0, 0), 1) for _ in range(8)]
        func_values = [1] * 8
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert sorted(result) == ['a', 'b', 'c']
    
    def test_constant_zero_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0) for _ in range(4)]
        func_values = [0] * 4
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert sorted(result) == ['a', 'b']


class TestFictitiousFinderMultiple:
    """Тесты нескольких фиктивных переменных"""
    
    def test_two_fictitious_variables(self):
        variables = ['a', 'b', 'c']
        truth_table = [((i // 4, (i // 2) % 2, i % 2), i // 4) for i in range(8)]
        func_values = [0, 0, 0, 0, 1, 1, 1, 1]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert sorted(result) == ['b', 'c']
    
    def test_multiple_fictitious_4vars(self):
        variables = ['a', 'b', 'c', 'd']
        func_values = []
        for i in range(16):
            a = (i >> 3) & 1
            b = (i >> 2) & 1
            func_values.append(a & b)
        
        truth_table = [((i >> 3 & 1, i >> 2 & 1, i >> 1 & 1, i & 1), func_values[i]) for i in range(16)]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert sorted(result) == ['c', 'd']


class TestFictitiousFinderKnownFunctions:
    """Тесты известных функций"""
    
    def test_xor_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
        func_values = [0, 1, 1, 0]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert result == []
    
    def test_or_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        func_values = [0, 1, 1, 1]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert result == []
    
    def test_and_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        func_values = [0, 0, 0, 1]
        
        result = FictitiousFinder.find(variables, truth_table, func_values)
        assert result == []

