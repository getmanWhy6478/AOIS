"""
Тесты для класса FunctionAnalyzer (pytest).
"""

import pytest
from core.function_analyzer import FunctionAnalyzer


class TestFunctionAnalyzerInit:
    """Тесты инициализации"""
    
    def test_init_basic(self):
        analyzer = FunctionAnalyzer("a&b")
        assert analyzer.get_variables() == ['a', 'b']
        assert analyzer.get_n_vars() == 2
        assert isinstance(analyzer.truth_table, list)
        assert isinstance(analyzer.func_values, list)
    
    def test_init_single_variable(self):
        analyzer = FunctionAnalyzer("a")
        assert analyzer.get_variables() == ['a']
        assert analyzer.get_n_vars() == 1
    
    def test_init_five_variables(self):
        analyzer = FunctionAnalyzer("a&b&c&d&e")
        assert analyzer.get_variables() == ['a', 'b', 'c', 'd', 'e']
        assert analyzer.get_n_vars() == 5


class TestFunctionAnalyzerTruthTable:
    """Тесты таблицы истинности"""
    
    def test_build_truth_table_size_1var(self):
        analyzer = FunctionAnalyzer("a")
        analyzer.build_truth_table()
        assert len(analyzer.truth_table) == 2
        assert len(analyzer.func_values) == 2
    
    def test_build_truth_table_size_2vars(self):
        analyzer = FunctionAnalyzer("a&b")
        analyzer.build_truth_table()
        assert len(analyzer.truth_table) == 4
        assert len(analyzer.func_values) == 4
    
    def test_build_truth_table_size_3vars(self):
        analyzer = FunctionAnalyzer("a|b&c")
        analyzer.build_truth_table()
        assert len(analyzer.truth_table) == 8
        assert len(analyzer.func_values) == 8
    
    def test_build_truth_table_structure(self):
        analyzer = FunctionAnalyzer("a&b")
        analyzer.build_truth_table()
        
        for row, val in analyzer.truth_table:
            assert isinstance(row, tuple)
            assert isinstance(val, int)
            assert len(row) == analyzer.get_n_vars()
            assert val in [0, 1]
    
    def test_truth_table_and(self):
        analyzer = FunctionAnalyzer("a&b")
        analyzer.build_truth_table()
        assert analyzer.func_values == [0, 0, 0, 1]
    
    def test_truth_table_or(self):
        analyzer = FunctionAnalyzer("a|b")
        analyzer.build_truth_table()
        assert analyzer.func_values == [0, 1, 1, 1]
    
    def test_truth_table_not(self):
        analyzer = FunctionAnalyzer("!a")
        analyzer.build_truth_table()
        assert analyzer.func_values == [1, 0]
    
    def test_truth_table_implication(self):
        analyzer = FunctionAnalyzer("a->b")
        analyzer.build_truth_table()
        assert analyzer.func_values == [1, 1, 0, 1]


class TestFunctionAnalyzerGetters:
    """Тесты getter методов"""
    
    def test_get_truth_table(self):
        analyzer = FunctionAnalyzer("a&b")
        analyzer.build_truth_table()
        table = analyzer.get_truth_table()
        assert len(table) == 4
        assert isinstance(table, list)
    
    def test_get_func_values(self):
        analyzer = FunctionAnalyzer("a|b")
        analyzer.build_truth_table()
        values = analyzer.get_func_values()
        assert values == [0, 1, 1, 1]
    
    def test_get_variables(self):
        analyzer = FunctionAnalyzer("a&b&c")
        assert analyzer.get_variables() == ['a', 'b', 'c']
    
    def test_get_n_vars(self):
        analyzer = FunctionAnalyzer("a&b&c&d")
        assert analyzer.get_n_vars() == 4
    
    def test_get_methods_before_build(self):
        analyzer = FunctionAnalyzer("a&b")
        assert analyzer.get_variables() == ['a', 'b']
        assert analyzer.get_n_vars() == 2
        assert analyzer.get_truth_table() == []
        assert analyzer.get_func_values() == []

class TestFunctionAnalyzerEdgeCases:
    """Граничные случаи"""
    
    def test_single_var_all_functions(self):
        # F = 0
        analyzer = FunctionAnalyzer("a&!a")
        analyzer.build_truth_table()
        assert analyzer.func_values == [0, 0]
        
        # F = 1
        analyzer = FunctionAnalyzer("a|!a")
        analyzer.build_truth_table()
        assert analyzer.func_values == [1, 1]
        
        # F = a
        analyzer = FunctionAnalyzer("a")
        analyzer.build_truth_table()
        assert analyzer.func_values == [0, 1]
        
        # F = !a
        analyzer = FunctionAnalyzer("!a")
        analyzer.build_truth_table()
        assert analyzer.func_values == [1, 0]
    
    def test_spaces_in_expression(self):
        analyzer1 = FunctionAnalyzer("a&b")
        analyzer1.build_truth_table()
        
        analyzer2 = FunctionAnalyzer("a & b")
        analyzer2.build_truth_table()
        
        assert analyzer1.func_values == analyzer2.func_values
    
    def test_rebuild_truth_table(self):
        analyzer = FunctionAnalyzer("a&b")
        analyzer.build_truth_table()
        first_values = analyzer.func_values[:]
        
        analyzer.build_truth_table()
        second_values = analyzer.func_values[:]
        
        assert first_values == second_values