"""
Тесты для класса NormalFormsBuilder (pytest).
"""

import pytest
from analysis.normal_forms import NormalFormsBuilder


class TestNormalFormsBuilderSDNF:
    """Тесты СДНФ"""
    
    def test_sdnf_constant_zero(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 0)]
        
        sdnf_str, sdnf_nums = NormalFormsBuilder.build_sdnf(variables, truth_table)
        
        assert sdnf_str == "0"
        assert sdnf_nums == []
    
    def test_sdnf_constant_one(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 1), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        
        sdnf_str, sdnf_nums = NormalFormsBuilder.build_sdnf(variables, truth_table)
        
        assert sdnf_nums == [0, 1, 2, 3]
        assert len(sdnf_str.split(" | ")) == 4
    
    def test_sdnf_and_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        
        sdnf_str, sdnf_nums = NormalFormsBuilder.build_sdnf(variables, truth_table)
        
        assert sdnf_nums == [3]
        assert "a" in sdnf_str
        assert "b" in sdnf_str
    
    def test_sdnf_or_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        
        sdnf_str, sdnf_nums = NormalFormsBuilder.build_sdnf(variables, truth_table)
        
        assert sorted(sdnf_nums) == [1, 2, 3]
    
    def test_sdnf_xor_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
        
        sdnf_str, sdnf_nums = NormalFormsBuilder.build_sdnf(variables, truth_table)
        
        assert sorted(sdnf_nums) == [1, 2]


class TestNormalFormsBuilderSKNF:
    """Тесты СКНФ"""
    
    def test_sknf_constant_zero(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 0)]
        
        sknf_str, sknf_nums = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        assert sknf_nums == [0, 1, 2, 3]
        assert len(sknf_str.split(" & ")) == 4
    
    def test_sknf_constant_one(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 1), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        
        sknf_str, sknf_nums = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        assert sknf_str == "1"
        assert sknf_nums == []
    
    def test_sknf_and_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        
        sknf_str, sknf_nums = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        assert sorted(sknf_nums) == [0, 1, 2]
    
    def test_sknf_or_function(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        
        sknf_str, sknf_nums = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        assert sknf_nums == [0]


class TestNormalFormsBuilderIntegration:
    """Интеграционные тесты"""
    
    def test_sdnf_sknf_complement(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 0), ((1, 1), 1)]
        
        sdnf = NormalFormsBuilder.build_sdnf(variables, truth_table)
        sknf = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        all_nums = set(range(4))
        assert set(sdnf[1]) | set(sknf[1]) == all_nums
        assert set(sdnf[1]) & set(sknf[1]) == set()
    
    def test_print_results(self):
        variables = ['a', 'b']
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 0), ((1, 1), 1)]
        
        sdnf = NormalFormsBuilder.build_sdnf(variables, truth_table)
        sknf = NormalFormsBuilder.build_sknf(variables, truth_table)
        
        NormalFormsBuilder.print_results(sdnf, sknf)