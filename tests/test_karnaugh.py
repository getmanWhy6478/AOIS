"""
Тесты для класса KarnaughMinimizer (pytest).
"""

import pytest
from minimization.karnaugh import KarnaughMinimizer


class TestGrayCode:
    """Тесты кодов Грея"""
    
    def test_gray_code_1bit(self):
        result = KarnaughMinimizer._gray_code(1)
        assert result == ['0', '1']
    
    def test_gray_code_2bits(self):
        result = KarnaughMinimizer._gray_code(2)
        assert result == ['00', '01', '11', '10']
    
    def test_gray_code_3bits(self):
        result = KarnaughMinimizer._gray_code(3)
        assert result == ['000', '001', '011', '010', '110', '111', '101', '100']
    
    def test_gray_code_adjacent_differs_by_one(self):
        for n in [1, 2, 3, 4]:
            codes = KarnaughMinimizer._gray_code(n)
            for i in range(len(codes) - 1):
                diff = sum(a != b for a, b in zip(codes[i], codes[i+1]))
                assert diff == 1
    
    def test_gray_code_cyclic(self):
        for n in [2, 3, 4]:
            codes = KarnaughMinimizer._gray_code(n)
            diff = sum(a != b for a, b in zip(codes[0], codes[-1]))
            assert diff == 1
    
    def test_gray_code_count(self):
        for n in range(1, 5):
            codes = KarnaughMinimizer._gray_code(n)
            assert len(codes) == 2**n


class TestGrayPositionToBinary:
    """Тесты конвертации позиции Грея в двоичное значение"""
    
    def test_gray2_lookup(self):
        assert KarnaughMinimizer._gray_position_to_binary(0, 2) == 0
        assert KarnaughMinimizer._gray_position_to_binary(1, 2) == 1
        assert KarnaughMinimizer._gray_position_to_binary(2, 2) == 3
        assert KarnaughMinimizer._gray_position_to_binary(3, 2) == 2
    
    def test_gray3_lookup(self):
        expected = [0, 1, 3, 2, 6, 7, 5, 4]
        for pos, exp in enumerate(expected):
            assert KarnaughMinimizer._gray_position_to_binary(pos, 3) == exp
    
    def test_gray_fallback_formula(self):
        # Тест общей формулы для n_bits > 3
        result = KarnaughMinimizer._gray_position_to_binary(0, 4)
        assert isinstance(result, int)
        assert 0 <= result < 16


class TestGetCellIndex:
    """Тесты вычисления индекса клетки"""
    
    def test_cell_index_2vars(self):
        # 2 переменные: 2 строки × 2 столбца
        assert KarnaughMinimizer._get_cell_index(0, 0, 1, 1) == 0  # 00 → 0
        assert KarnaughMinimizer._get_cell_index(0, 1, 1, 1) == 1  # 01 → 1
        assert KarnaughMinimizer._get_cell_index(1, 0, 1, 1) == 2  # 10 → 2
        assert KarnaughMinimizer._get_cell_index(1, 1, 1, 1) == 3  # 11 → 3
    
    def test_cell_index_3vars(self):
        # 3 переменные: 2 строки (1 var) × 4 столбца (2 var)
        assert KarnaughMinimizer._get_cell_index(0, 0, 2, 1) == 0   # a=0, bc=00 → 0
        assert KarnaughMinimizer._get_cell_index(0, 2, 2, 1) == 3   # a=0, bc=11 → 3
        assert KarnaughMinimizer._get_cell_index(1, 0, 2, 1) == 4   # a=1, bc=00 → 4
        assert KarnaughMinimizer._get_cell_index(1, 2, 2, 1) == 7   # a=1, bc=11 → 7
    
    def test_cell_index_5vars(self):
        # 5 переменные: 4 строки (2 var) × 8 столбцов (3 var)
        assert KarnaughMinimizer._get_cell_index(0, 0, 3, 2) == 0    # ab=00, cde=000 → 0
        assert KarnaughMinimizer._get_cell_index(0, 2, 3, 2) == 3    # ab=00, cde=011 → 3
        assert KarnaughMinimizer._get_cell_index(2, 0, 3, 2) == 24   # ab=11, cde=000 → 24
        assert KarnaughMinimizer._get_cell_index(2, 1, 3, 2) == 25   # ab=11, cde=001 → 25


class TestExtractImplicant:
    """Тесты извлечения импликанты для 2-4 переменных"""
    
    def test_extract_dnf_single_cell(self):
        cells = [(0, 0)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [0]*4, find_zeros=False
        )
        assert '!a' in result
        assert '!b' in result
    
    def test_extract_dnf_pair_horizontal(self):
        # Группа где a=0, b меняется
        cells = [(0, 0), (0, 1)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [0]*4, find_zeros=False
        )
        assert result == '!a'
    
    def test_extract_dnf_pair_vertical(self):
        # Группа где b=0, a меняется
        cells = [(0, 0), (1, 0)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [0]*4, find_zeros=False
        )
        assert result == '!b'
    
    def test_extract_dnf_quad(self):
        # Все 4 клетки: константа 1
        cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [1]*4, find_zeros=False
        )
        assert result == '1'
    
    def test_extract_cnf_single_cell(self):
        cells = [(0, 0)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [0]*4, find_zeros=True
        )
        assert 'a' in result
        assert 'b' in result
    
    def test_extract_cnf_pair(self):
        cells = [(0, 0), (0, 1)]
        result = KarnaughMinimizer._extract_implicant(
            cells, ['a', 'b'], 1, 1, [0]*4, find_zeros=True
        )
        assert result == 'a'


class TestExtractImplicant5var:
    """Тесты извлечения импликанты для 5 переменных"""
    
    def test_extract_5var_dnf_single_cell(self):
        cells = [(0, 0, 0)]  # a=0, bc=00, de=00 → индекс 0
        result = KarnaughMinimizer._extract_implicant_5var(
            cells, ['a', 'b', 'c', 'd', 'e'], [0]*32, find_zeros=False
        )
        assert '!a' in result
        assert '!b' in result
        assert '!c' in result
        assert '!d' in result
        assert '!e' in result
    
    def test_extract_5var_dnf_group_16_cells(self):
        # Группа где e=0 (16 клеток)
        cells = []
        for a in [0, 1]:
            for bc_row in range(4):
                for de_col in [0, 1, 3, 2]:  # Gray order для e=0
                    cells.append((a, bc_row, de_col))
        
        result = KarnaughMinimizer._extract_implicant_5var(
            cells, ['a', 'b', 'c', 'd', 'e'], [1]*32, find_zeros=False
        )
        assert '1' in result
    
    def test_extract_5var_cnf_single_cell(self):
        cells = [(0, 0, 0)]
        result = KarnaughMinimizer._extract_implicant_5var(
            cells, ['a', 'b', 'c', 'd', 'e'], [0]*32, find_zeros=True
        )
        assert 'a' in result
        assert 'b' in result
        assert 'c' in result
        assert 'd' in result
        assert 'e' in result


class TestFindAllGroups:
    """Тесты поиска групп"""
    
    def test_find_groups_empty_function_2vars(self):
        func_values = [0, 0, 0, 0]
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b'], 2)
        assert groups == []
    
    def test_find_groups_all_ones_2vars(self):
        func_values = [1, 1, 1, 1]
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b'], 2)
        assert len(groups) >= 1
        assert any(g['size'] == 4 for g in groups)
    
    def test_find_groups_and_function(self):
        func_values = [0, 0, 0, 1]
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b'], 2)
        assert any(g['implicant'] == 'a&b' for g in groups)
    
    def test_find_groups_or_function(self):
        func_values = [0, 1, 1, 1]
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b'], 2)
        assert len(groups) >= 1
    
    def test_find_groups_5var_simple(self):
        # F = a (остальные фиктивные)
        func_values = [0]*16 + [1]*16
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b', 'c', 'd', 'e'], 5)
        assert any('a' in g['implicant'] for g in groups)
    
    def test_find_groups_sorted_by_size(self):
        func_values = [0, 1, 1, 1]
        groups = KarnaughMinimizer._find_all_groups(func_values, ['a', 'b'], 2)
        sizes = [g['size'] for g in groups]
        assert sizes == sorted(sizes, reverse=True)


class TestSelectEssentialGroups:
    """Тесты выбора существенно необходимых групп"""
    
    def test_select_empty(self):
        result = KarnaughMinimizer._select_essential_groups([], [])
        assert result == []
    
    def test_select_single_group(self):
        groups = [{'covered': {0, 1, 2, 3}, 'implicant': '1', 'size': 4}]
        result = KarnaughMinimizer._select_essential_groups(groups, [0, 1, 2, 3])
        assert len(result) == 1
    
    def test_select_unique_coverage(self):
        groups = [
            {'covered': {0, 1}, 'implicant': '!a', 'size': 2},
            {'covered': {2, 3}, 'implicant': 'a', 'size': 2}
        ]
        result = KarnaughMinimizer._select_essential_groups(groups, [0, 1, 2, 3])
        assert len(result) == 2
    
    def test_select_prefers_larger(self):
        groups = [
            {'covered': {0}, 'implicant': 'small', 'size': 1},
            {'covered': {0, 1, 2, 3}, 'implicant': 'large', 'size': 4}
        ]
        result = KarnaughMinimizer._select_essential_groups(groups, [0, 1, 2, 3])
        assert len(result) == 1
        assert result[0]['implicant'] == 'large'


class TestMinimizeDnf:
    """Тесты минимизации ДНФ"""
    
    def test_minimize_dnf_constant_zero(self):
        result = KarnaughMinimizer.minimize_dnf([0]*4, ['a', 'b'], 2, verbose=False)
        assert result == '0'
    
    def test_minimize_dnf_constant_one(self):
        result = KarnaughMinimizer.minimize_dnf([1]*4, ['a', 'b'], 2, verbose=False)
        assert result == '1'
    
    def test_minimize_dnf_and_function(self):
        result = KarnaughMinimizer.minimize_dnf([0, 0, 0, 1], ['a', 'b'], 2, verbose=False)
        assert result == 'a&b'
    
    def test_minimize_dnf_or_function(self):
        result = KarnaughMinimizer.minimize_dnf([0, 1, 1, 1], ['a', 'b'], 2, verbose=False)
        assert 'a' in result or 'b' in result
    
    def test_minimize_dnf_xor_function(self):
        result = KarnaughMinimizer.minimize_dnf([0, 1, 1, 0], ['a', 'b'], 2, verbose=False)
        assert len(result) > 0
    
    def test_minimize_dnf_3vars(self):
        result = KarnaughMinimizer.minimize_dnf([1, 2, 3, 5, 7], ['a', 'b', 'c'], 3, verbose=False)
        assert 'c' in result or '!a' in result
    
    def test_minimize_dnf_5vars(self):
        result = KarnaughMinimizer.minimize_dnf(
            [0]*16 + [1]*16, ['a', 'b', 'c', 'd', 'e'], 5, verbose=False
        )
        assert result == 'a'


class TestMinimizeCnf:
    """Тесты минимизации КНФ"""
    
    def test_minimize_cnf_constant_zero(self):
        result = KarnaughMinimizer.minimize_cnf([0]*4, ['a', 'b'], 2, verbose=False)
        assert result == '0'
    
    def test_minimize_cnf_constant_one(self):
        result = KarnaughMinimizer.minimize_cnf([1]*4, ['a', 'b'], 2, verbose=False)
        assert result == '1'
    
    def test_minimize_cnf_and_function(self):
        result = KarnaughMinimizer.minimize_cnf([0, 0, 0, 1], ['a', 'b'], 2, verbose=False)
        assert 'a' in result or 'b' in result
    
    def test_minimize_cnf_or_function(self):
        result = KarnaughMinimizer.minimize_cnf([0, 1, 1, 1], ['a', 'b'], 2, verbose=False)
        assert 'a' in result
        assert 'b' in result
    
    def test_minimize_cnf_5vars(self):
        result = KarnaughMinimizer.minimize_cnf(
            [0]*16 + [1]*16, ['a', 'b', 'c', 'd', 'e'], 5, verbose=False
        )
        assert '(a)' in result


class TestMinimizeCombined:
    """Тесты комбинированной минимизации"""
    
    def test_minimize_both_forms(self):
        func_values = [0, 1, 1, 1]
        results = KarnaughMinimizer.minimize(
            [1, 2, 3], func_values, 2, verbose=False, forms=['both']
        )
        assert 'dnf' in results
        assert 'cnf' in results
    
    def test_minimize_dnf_only(self):
        func_values = [0, 1, 1, 1]
        results = KarnaughMinimizer.minimize(
            [1, 2, 3], func_values, 2, verbose=False, forms=['dnf']
        )
        assert 'dnf' in results
        assert 'cnf' not in results
    
    def test_minimize_cnf_only(self):
        func_values = [0, 1, 1, 1]
        results = KarnaughMinimizer.minimize(
            [1, 2, 3], func_values, 2, verbose=False, forms=['cnf']
        )
        assert 'cnf' in results
        assert 'dnf' not in results


class TestPrintMap:
    """Тесты вывода карты Карно"""
    
    def test_print_map_2vars(self, capsys):
        result = KarnaughMinimizer.print_map(
            [0, 1, 1, 0], ['a', 'b'], 2, show_minimization=False
        )
        captured = capsys.readouterr()
        assert "Карта Карно" in captured.out
        assert "b" in captured.out
    
    def test_print_map_3vars(self, capsys):
        result = KarnaughMinimizer.print_map(
            [0, 1, 0, 1, 1, 0, 1, 0], ['a', 'b', 'c'], 3, show_minimization=False
        )
        captured = capsys.readouterr()
        assert "Карта Карно" in captured.out
        assert "bc" in captured.out
    
    def test_print_map_5vars(self, capsys):
        result = KarnaughMinimizer.print_map(
            [i % 2 for i in range(32)], ['a', 'b', 'c', 'd', 'e'], 5, show_minimization=False
        )
        captured = capsys.readouterr()
        assert "Карта Карно" in captured.out
        assert "cde" in captured.out
    
    def test_print_map_unsupported_vars(self, capsys):
        result = KarnaughMinimizer.print_map([0, 1], ['a'], 1, show_minimization=False)
        captured = capsys.readouterr()
        assert "поддерживается" in captured.out
    
    def test_print_map_with_minimization(self, capsys):
        result = KarnaughMinimizer.print_map(
            [0, 1, 1, 1], ['a', 'b'], 2, show_minimization=True, forms=['dnf']
        )
        captured = capsys.readouterr()
        assert "Карта Карно" in captured.out
        assert "Минимальная ДНФ" in captured.out


class TestCorrectness:
    
    def test_dnf_correctness_or(self):
        from core.function_analyzer import FunctionAnalyzer
        
        result = KarnaughMinimizer.minimize_dnf([1, 2, 3], ['a', 'b'], 2, verbose=False)
        analyzer = FunctionAnalyzer(result)
        analyzer.build_truth_table()
        
        assert analyzer.func_values == [1, 0, 0, 0]
    
    def test_cnf_correctness_and(self):
        from core.function_analyzer import FunctionAnalyzer
        
        func_values = [0, 0, 0, 1]
        result = KarnaughMinimizer.minimize_cnf(func_values, ['a', 'b'], 2, verbose=False)
        analyzer = FunctionAnalyzer(result)
        analyzer.build_truth_table()
        
        assert analyzer.func_values == func_values


class TestKnownFunctions:
    
    def test_nor_function(self):
        func_values = [1, 0, 0, 0]
        results = KarnaughMinimizer.minimize(
            [0], func_values, ['a', 'b'], verbose=False, forms=['both']
        )
        assert '0' in results['dnf']


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_single_variable_dnf(self):
        result = KarnaughMinimizer.minimize_dnf([1], ['a'], 1, verbose=False)
        assert result == '1'
    
    def test_single_variable_cnf(self):
        result = KarnaughMinimizer.minimize_cnf([0, 1], ['a'], 1, verbose=False)
        assert isinstance(result, str)
    
    def test_4vars_large_group(self):
        result = KarnaughMinimizer.minimize_dnf(
            list(range(8, 16)), ['a', 'b', 'c', 'd'], 4, verbose=False
        )
        assert '0' in result
    
    def test_5vars_complex_pattern(self):
        # Сложный паттерн для 5 переменных
        func_values = [1 if i % 3 == 0 else 0 for i in range(32)]
        result = KarnaughMinimizer.minimize_dnf(
            func_values, ['a', 'b', 'c', 'd', 'e'], 5, verbose=False
        )
        assert isinstance(result, str)
    
    def test_cyclic_group_2vars(self):
        # Единицы на краях (должны склеиваться циклически)
        func_values = [1, 0, 0, 1]
        result = KarnaughMinimizer.minimize_dnf(func_values, ['a', 'b'], 2, verbose=False)
        assert len(result) > 0


class TestPerformance:
    """Тесты производительности"""
    
    def test_performance_2vars(self):
        import time
        start = time.time()
        KarnaughMinimizer.minimize_dnf([1, 2, 3], ['a', 'b'], 2, verbose=False)
        elapsed = time.time() - start
        assert elapsed < 0.1
    
    def test_performance_4vars(self):
        import time
        start = time.time()
        KarnaughMinimizer.minimize_dnf(
            list(range(16)), ['a', 'b', 'c', 'd'], 4, verbose=False
        )
        elapsed = time.time() - start
        assert elapsed < 1.0
    
    def test_performance_5vars(self):
        import time
        start = time.time()
        KarnaughMinimizer.minimize_dnf(
            list(range(32)), ['a', 'b', 'c', 'd', 'e'], 5, verbose=False
        )
        elapsed = time.time() - start
        assert elapsed < 5.0


class TestRepeatability:
    """Тесты повторяемости"""
    
    def test_repeatability_dnf(self):
        result1 = KarnaughMinimizer.minimize_dnf(
            [1, 3, 5, 7], ['a', 'b', 'c'], 3, verbose=False
        )
        result2 = KarnaughMinimizer.minimize_dnf(
            [1, 3, 5, 7], ['a', 'b', 'c'], 3, verbose=False
        )
        assert result1 == result2
    
    def test_repeatability_cnf(self):
        func_values = [0, 1, 0, 1]
        result1 = KarnaughMinimizer.minimize_cnf(
            func_values, ['a', 'b'], 2, verbose=False
        )
        result2 = KarnaughMinimizer.minimize_cnf(
            func_values, ['a', 'b'], 2, verbose=False
        )
        assert result1 == result2
    
    def test_consistency_across_calls(self):
        func_values = [0, 1, 1, 1]
        results1 = KarnaughMinimizer.minimize(
            [1, 2, 3], func_values, 2, verbose=False, forms=['both']
        )
        results2 = KarnaughMinimizer.minimize(
            [1, 2, 3], func_values, 2, verbose=False, forms=['both']
        )
        assert results1 == results2