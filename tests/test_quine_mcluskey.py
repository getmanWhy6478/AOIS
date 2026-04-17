"""
Тесты для класса QuineMcCluskeyMinimizer (pytest).
"""

import pytest
from minimization.quine_mcluskey import QuineMcCluskeyMinimizer


class TestQmStep:
    """Тесты шага склеивания"""
    
    def test_qm_step_no_gluing(self):
        """Шаг без возможности склеивания"""
        minterms = ['00', '11']  # Отличаются в 2 битах
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step(minterms)
        
        assert next_terms == []
        assert sorted(primes) == sorted(minterms)
    
    def test_qm_step_single_glue(self):
        """Шаг с одним склеиванием"""
        minterms = ['00', '01']  # Отличаются в 1 бите
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step(minterms)
        
        assert '0-' in next_terms
        assert primes == []
    
    def test_qm_step_multiple_glue(self):
        """Шаг с несколькими склеиваниями"""
        minterms = ['000', '001', '010', '011']
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step(minterms)
        
        assert '00-' in next_terms
        assert '01-' in next_terms
        assert primes == []
    
    def test_qm_step_empty_input(self):
        """Пустой вход"""
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step([])
        
        assert next_terms == []
        assert primes == []
    
    def test_qm_step_single_term(self):
        """Один терм на входе"""
        minterms = ['101']
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step(minterms)
        
        assert next_terms == []
        assert primes == ['101']
    
    def test_qm_step_no_duplicates(self):
        """Отсутствие дубликатов в результате"""
        minterms = ['00', '01', '10', '11']
        next_terms, primes = QuineMcCluskeyMinimizer._qm_step(minterms)
        
        assert len(next_terms) == len(set(next_terms))


class TestFormatTermDnf:
    """Тесты форматирования ДНФ"""
    
    def test_format_dnf_all_ones(self):
        result = QuineMcCluskeyMinimizer._format_term_dnf('11', ['a', 'b'])
        assert result == 'a&b'
    
    def test_format_dnf_all_zeros(self):
        result = QuineMcCluskeyMinimizer._format_term_dnf('00', ['a', 'b'])
        assert result == '!a&!b'
    
    def test_format_dnf_with_dashes(self):
        result = QuineMcCluskeyMinimizer._format_term_dnf('0-1', ['a', 'b', 'c'])
        assert result == '!a&c'
        assert 'b' not in result
    
    def test_format_dnf_all_dashes(self):
        result = QuineMcCluskeyMinimizer._format_term_dnf('--', ['a', 'b'])
        assert result == '1'
    
    def test_format_dnf_single_var(self):
        result = QuineMcCluskeyMinimizer._format_term_dnf('1', ['a'])
        assert result == 'a'


class TestFormatTermCnf:
    """Тесты форматирования КНФ"""
    
    def test_format_cnf_all_zeros(self):
        result = QuineMcCluskeyMinimizer._format_term_cnf('00', ['a', 'b'])
        assert result == 'a|b'
    
    def test_format_cnf_all_ones(self):
        result = QuineMcCluskeyMinimizer._format_term_cnf('11', ['a', 'b'])
        assert result == '!a|!b'
    
    def test_format_cnf_with_dashes(self):
        result = QuineMcCluskeyMinimizer._format_term_cnf('0-1', ['a', 'b', 'c'])
        assert 'b' not in result
    
    def test_format_cnf_all_dashes(self):
        result = QuineMcCluskeyMinimizer._format_term_cnf('--', ['a', 'b'])
        assert result == '0'


class TestMinimizeDnf:
    """Тесты минимизации ДНФ"""
    
    def test_minimize_dnf_constant_zero(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([], ['a', 'b'], show_steps=False)
        assert result == '0'
    
    def test_minimize_dnf_constant_one(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([0, 1, 2, 3], ['a', 'b'], show_steps=False)
        assert result == '1'
    
    def test_minimize_dnf_and_function(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([3], ['a', 'b'], show_steps=False)
        assert result == 'a&b'
    
    def test_minimize_dnf_or_function(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([1, 2, 3], ['a', 'b'], show_steps=False)
        assert 'a' in result
        assert 'b' in result
    
    def test_minimize_dnf_xor_function(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([1, 2], ['a', 'b'], show_steps=False)
        assert '!a' in result or '!b' in result
    
    def test_minimize_dnf_3vars(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([1, 2, 3, 5, 7], ['a', 'b', 'c'], show_steps=False)
        assert 'c' in result or '!a' in result
    
    def test_minimize_dnf_5vars(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf(list(range(16, 32)), ['a', 'b', 'c', 'd', 'e'], show_steps=False)
        assert result == 'a'
    
    def test_minimize_dnf_single_minterm(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([5], ['a', 'b', 'c'], show_steps=False)
        assert 'a' in result
        assert '!b' in result
        assert 'c' in result


class TestMinimizeCnf:
    """Тесты минимизации КНФ"""
    
    def test_minimize_cnf_constant_zero(self):
        func_values = [0] * 4
        result = QuineMcCluskeyMinimizer.minimize_cnf(func_values, ['a', 'b'], show_steps=False)
        assert result == '0'
    
    def test_minimize_cnf_constant_one(self):
        func_values = [1] * 4
        result = QuineMcCluskeyMinimizer.minimize_cnf(func_values, ['a', 'b'], show_steps=False)
        assert result == '1'
    
    def test_minimize_cnf_and_function(self):
        func_values = [0, 0, 0, 1]
        result = QuineMcCluskeyMinimizer.minimize_cnf(func_values, ['a', 'b'], show_steps=False)
        assert 'a' in result or 'b' in result
    
    def test_minimize_cnf_or_function(self):
        func_values = [0, 1, 1, 1]
        result = QuineMcCluskeyMinimizer.minimize_cnf(func_values, ['a', 'b'], show_steps=False)
        assert 'a' in result
        assert 'b' in result


class TestMinimizeCombined:
    """Тесты комбинированной минимизации"""
    
    def test_minimize_both_forms(self):
        func_values = [0, 1, 1, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 2, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        assert 'dnf' in results
        assert 'cnf' in results
    
    def test_minimize_dnf_only(self):
        func_values = [0, 1, 1, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 2, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['dnf']
        )
        
        assert 'dnf' in results
        assert 'cnf' not in results
    
    def test_minimize_cnf_only(self):
        func_values = [0, 1, 1, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 2, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['cnf']
        )
        
        assert 'cnf' in results
        assert 'dnf' not in results


class TestSelectCoverDnf:
    """Тесты выбора покрытия для ДНФ"""
    
    def test_select_cover_single_prime(self):
        primes = ['--']
        minterms = [0, 1, 2, 3]
        result = QuineMcCluskeyMinimizer._select_cover_dnf(primes, minterms, ['a', 'b'])
        assert result == '1'
    
    def test_select_cover_two_primes(self):
        primes = ['0-', '-1']
        minterms = [0, 1, 3]
        result = QuineMcCluskeyMinimizer._select_cover_dnf(primes, minterms, ['a', 'b'])
        assert '!a' in result or 'b' in result
    
    def test_select_cover_empty_minterms(self):
        primes = ['0-', '1-']
        minterms = []
        result = QuineMcCluskeyMinimizer._select_cover_dnf(primes, minterms, ['a', 'b'])
        assert result == ''


class TestSelectCoverCnf:
    """Тесты выбора покрытия для КНФ"""
    
    def test_select_cover_single_prime(self):
        primes = ['--']
        maxterms = [0, 1, 2, 3]
        result = QuineMcCluskeyMinimizer._select_cover_cnf(primes, maxterms, ['a', 'b'])
        assert result == '(0)'


class TestPrintTabular:
    """Тесты табличного метода"""
    
    def test_print_tabular_dnf(self, capsys):
        QuineMcCluskeyMinimizer.print_tabular([1, 2, 3], [0, 1, 1, 1], ['a', 'b'], form='dnf')
        captured = capsys.readouterr()
        
        assert "Таблица покрытия для ДНФ" in captured.out
        assert "ПИ" in captured.out
    
    def test_print_tabular_cnf(self, capsys):
        QuineMcCluskeyMinimizer.print_tabular([1, 2, 3], [0, 1, 1, 1], ['a', 'b'], form='cnf')
        captured = capsys.readouterr()
        
        assert "Таблица покрытия для КНФ" in captured.out
        assert "ПИ" in captured.out
    
    def test_print_tabular_contains_x_marks(self, capsys):
        QuineMcCluskeyMinimizer.print_tabular([3], [0, 0, 0, 1], ['a', 'b'], form='dnf')
        captured = capsys.readouterr()
        
        assert " X " in captured.out


class TestKnownFunctions:
    """Тесты на известных функциях"""
    
    def test_nand_function(self):
        func_values = [1, 1, 1, 0]
        results = QuineMcCluskeyMinimizer.minimize(
            [0, 1, 2], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        assert '!a' in results['dnf'] or '!b' in results['dnf']
    
    def test_nor_function(self):
        func_values = [1, 0, 0, 0]
        results = QuineMcCluskeyMinimizer.minimize(
            [0], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        assert '!a' in results['dnf']
        assert '!b' in results['dnf']
    
    def test_equivalence_function(self):
        func_values = [1, 0, 0, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [0, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        assert len(results['dnf']) > 0
    
    def test_majority_function_3vars(self):
        func_values = [0, 0, 0, 1, 0, 1, 1, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [3, 5, 6, 7], func_values, ['a', 'b', 'c'], 
            show_steps=False, forms=['both']
        )
        
        assert '|' in results['dnf'] or '&' in results['dnf']
    
    def test_parity_function_3vars(self):
        func_values = [0, 1, 1, 0, 1, 0, 0, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 2, 4, 7], func_values, ['a', 'b', 'c'], 
            show_steps=False, forms=['both']
        )
        
        assert 'a' in results['dnf']
        assert 'b' in results['dnf']
        assert 'c' in results['dnf']


class TestCorrectness:
    """Тесты корректности результатов"""
    
    def test_dnf_correctness_and(self):
        """Проверка корректности ДНФ для AND"""
        from core.function_analyzer import FunctionAnalyzer
        
        result = QuineMcCluskeyMinimizer.minimize_dnf([3], ['a', 'b'], show_steps=False)
        analyzer = FunctionAnalyzer(result)
        analyzer.build_truth_table()
        
        assert analyzer.func_values == [0, 0, 0, 1]
    
    def test_dnf_correctness_or(self):
        """Проверка корректности ДНФ для OR"""
        from core.function_analyzer import FunctionAnalyzer
        
        result = QuineMcCluskeyMinimizer.minimize_dnf([1, 2, 3], ['a', 'b'], show_steps=False)
        analyzer = FunctionAnalyzer(result)
        analyzer.build_truth_table()
        
        assert analyzer.func_values == [0, 1, 1, 1]
    
    def test_cnf_correctness_and(self):
        """Проверка корректности КНФ для AND"""
        from core.function_analyzer import FunctionAnalyzer
        
        func_values = [0, 0, 0, 1]
        result = QuineMcCluskeyMinimizer.minimize_cnf(func_values, ['a', 'b'], show_steps=False)
        analyzer = FunctionAnalyzer(result)
        analyzer.build_truth_table()
        
        assert analyzer.func_values == func_values
    
    def test_dnf_cnf_equivalence(self):
        """ДНФ и КНФ должны быть эквивалентны"""
        from core.function_analyzer import FunctionAnalyzer
        
        func_values = [0, 1, 0, 1]
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        analyzer_dnf = FunctionAnalyzer(results['dnf'])
        analyzer_dnf.build_truth_table()
        
        analyzer_cnf = FunctionAnalyzer(results['cnf'])
        analyzer_cnf.build_truth_table()
        
        assert analyzer_dnf.func_values == analyzer_cnf.func_values


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_empty_sdnf(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([], ['a', 'b'], show_steps=False)
        assert result == '0'
    
    def test_single_variable(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf([1], ['a'], show_steps=False)
        assert result == 'a'
    
    def test_large_number_of_minterms(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf(
            list(range(15)), ['a', 'b', 'c', 'd'], show_steps=False
        )
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_sparse_minterms(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf(
            [0, 15], ['a', 'b', 'c', 'd'], show_steps=False
        )
        assert isinstance(result, str)
    
    def test_cyclic_pattern(self):
        result = QuineMcCluskeyMinimizer.minimize_dnf(
            [0, 2, 4, 6], ['a', 'b', 'c'], show_steps=False
        )
        assert '!c' in result


class TestPerformance:
    """Тесты производительности"""
    
    def test_performance_2vars(self):
        import time
        
        start = time.time()
        QuineMcCluskeyMinimizer.minimize_dnf([1, 2, 3], ['a', 'b'], show_steps=False)
        elapsed = time.time() - start
        
        assert elapsed < 0.1
    
    def test_performance_4vars(self):
        import time
        
        start = time.time()
        QuineMcCluskeyMinimizer.minimize_dnf(
            list(range(16)), ['a', 'b', 'c', 'd'], show_steps=False
        )
        elapsed = time.time() - start
        
        assert elapsed < 1.0
    
    def test_performance_5vars(self):
        import time
        
        start = time.time()
        QuineMcCluskeyMinimizer.minimize_dnf(
            list(range(32)), ['a', 'b', 'c', 'd', 'e'], show_steps=False
        )
        elapsed = time.time() - start
        
        assert elapsed < 5.0


class TestRepeatability:
    """Тесты повторяемости"""
    
    def test_repeatability(self):
        result1 = QuineMcCluskeyMinimizer.minimize_dnf(
            [1, 3, 5, 7], ['a', 'b', 'c'], show_steps=False
        )
        result2 = QuineMcCluskeyMinimizer.minimize_dnf(
            [1, 3, 5, 7], ['a', 'b', 'c'], show_steps=False
        )
        
        assert result1 == result2
    
    def test_consistency_across_methods(self):
        func_values = [0, 1, 0, 1]
        
        results = QuineMcCluskeyMinimizer.minimize(
            [1, 3], func_values, ['a', 'b'], 
            show_steps=False, forms=['both']
        )
        
        assert 'dnf' in results
        assert 'cnf' in results
        assert isinstance(results['dnf'], str)
        assert isinstance(results['cnf'], str)
