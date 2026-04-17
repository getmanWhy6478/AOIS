"""
Тесты для класса PostClassesChecker (pytest).
"""

import pytest
from analysis.post_classes import PostClassesChecker


class TestPostClassesT0:
    """Тесты класса T0"""
    
    def test_t0_constant_zero(self):
        func_values = [0, 0, 0, 0]
        assert PostClassesChecker.check_t0(func_values) is True
    
    def test_t0_constant_one(self):
        func_values = [1, 1, 1, 1]
        assert PostClassesChecker.check_t0(func_values) is False
    
    def test_t0_and_function(self):
        func_values = [0, 0, 0, 1]
        assert PostClassesChecker.check_t0(func_values) is True
    
    def test_t0_or_function(self):
        func_values = [0, 1, 1, 1]
        assert PostClassesChecker.check_t0(func_values) is True
    
    def test_t0_not_function(self):
        func_values = [1, 0]
        assert PostClassesChecker.check_t0(func_values) is False


class TestPostClassesT1:
    """Тесты класса T1"""
    
    def test_t1_constant_zero(self):
        func_values = [0, 0, 0, 0]
        assert PostClassesChecker.check_t1(func_values) is False
    
    def test_t1_constant_one(self):
        func_values = [1, 1, 1, 1]
        assert PostClassesChecker.check_t1(func_values) is True
    
    def test_t1_and_function(self):
        func_values = [0, 0, 0, 1]
        assert PostClassesChecker.check_t1(func_values) is True
    
    def test_t1_or_function(self):
        func_values = [0, 1, 1, 1]
        assert PostClassesChecker.check_t1(func_values) is True
    
    def test_t1_xor_function(self):
        func_values = [0, 1, 1, 0]
        assert PostClassesChecker.check_t1(func_values) is False


class TestPostClassesSelfdual:
    """Тесты класса S"""
    
    def test_s_constant_zero(self):
        func_values = [0, 0, 0, 0]
        assert PostClassesChecker.check_selfdual(func_values) is False
    
    def test_s_constant_one(self):
        func_values = [1, 1, 1, 1]
        assert PostClassesChecker.check_selfdual(func_values) is False
    
    def test_s_not_function(self):
        func_values = [1, 0]
        assert PostClassesChecker.check_selfdual(func_values) is True


class TestPostClassesMonotonic:
    """Тесты класса M"""
    
    def test_m_constant_zero(self):
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 0)]
        assert PostClassesChecker.check_monotonic(truth_table, 2) is True
    
    def test_m_constant_one(self):
        truth_table = [((0, 0), 1), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
        assert PostClassesChecker.check_monotonic(truth_table, 2) is True
    
    def test_m_and_function(self):
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        assert PostClassesChecker.check_monotonic(truth_table, 2) is True
    
    def test_m_not_function(self):
        truth_table = [((0,), 1), ((1,), 0)]
        assert PostClassesChecker.check_monotonic(truth_table, 1) is False
    
    def test_m_xor_function(self):
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
        assert PostClassesChecker.check_monotonic(truth_table, 2) is False


class TestPostClassesIntegration:
    """Интеграционные тесты"""
    
    def test_all_classes_and(self):
        truth_table = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
        func_values = [0, 0, 0, 1]
        
        t0 = PostClassesChecker.check_t0(func_values)
        t1 = PostClassesChecker.check_t1(func_values)
        s = PostClassesChecker.check_selfdual(func_values)
        m = PostClassesChecker.check_monotonic(truth_table, 2)
        
        assert t0 is True
        assert t1 is True
        assert s is False
        assert m is True
    
    def test_all_classes_xor(self):
        truth_table = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
        func_values = [0, 1, 1, 0]
        
        t0 = PostClassesChecker.check_t0(func_values)
        t1 = PostClassesChecker.check_t1(func_values)
        s = PostClassesChecker.check_selfdual(func_values)
        m = PostClassesChecker.check_monotonic(truth_table, 2)
        
        assert t0 is True
        assert t1 is False
        assert s is False
        assert m is False