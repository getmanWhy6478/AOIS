from typing import List, Tuple, Dict


class KarnaughMinimizer:

    # Lookup-таблицы: позиция в списке Грея → двоичное значение
    GRAY2_TO_BIN = [0, 1, 3, 2]
    GRAY3_TO_BIN = [0, 1, 3, 2, 6, 7, 5, 4]

    @staticmethod
    def _gray_code(n: int) -> List[str]:
        return [bin(i ^ (i >> 1))[2:].zfill(n) for i in range(2**n)]

    @staticmethod
    def _gray_position_to_binary(position: int, n_bits: int) -> int:
        if n_bits == 2:
            return KarnaughMinimizer.GRAY2_TO_BIN[position] if position < 4 else position
        elif n_bits == 3:
            return KarnaughMinimizer.GRAY3_TO_BIN[position] if position < 8 else position
        else:
            binary = position
            mask = binary >> 1
            while mask:
                binary ^= mask
                mask >>= 1
            return binary

    @staticmethod
    def _get_cell_index(row: int, col: int, 
                       n_col_vars: int,
                       n_row_vars: int) -> int:
        row_bin = KarnaughMinimizer._gray_position_to_binary(row, n_row_vars)
        col_bin = KarnaughMinimizer._gray_position_to_binary(col, n_col_vars)
        return (row_bin << n_col_vars) | col_bin

    @staticmethod
    def _find_all_groups_5var(func_values: List[int],
                              variables: List[str],
                              find_zeros: bool = False) -> List[Dict]:
        groups = []
        
        # 2 карты по 4×4 (bc × de)
        n_rows, n_cols = 4, 4
        n_row_vars, n_col_vars = 2, 2  # bc и de
        
        row_codes = KarnaughMinimizer._gray_code(n_row_vars)
        col_codes = KarnaughMinimizer._gray_code(n_col_vars)
        
        target_value = 0 if find_zeros else 1
        target_set = set(i for i, v in enumerate(func_values) if v == target_value)
        
        if not target_set:
            return groups
        
        possible_heights = [1, 2, 4]
        possible_widths = [1, 2, 4]
        
        # Ищем группы ВНУТРИ каждой карты (a=0 и a=1)
        for a_val in [0, 1]:
            for height in sorted(possible_heights, reverse=True):
                for width in sorted(possible_widths, reverse=True):
                    for start_row in range(n_rows):
                        for start_col in range(n_cols):
                            cells = []
                            all_target = True
                            
                            for dr in range(height):
                                for dc in range(width):
                                    row = (start_row + dr) % n_rows
                                    col = (start_col + dc) % n_cols
                                    # Индекс: a(1 бит) + bc(2 бита) + de(2 бита)
                                    row_bin = KarnaughMinimizer._gray_position_to_binary(row, 2)
                                    col_bin = KarnaughMinimizer._gray_position_to_binary(col, 2)
                                    idx = (a_val << 4) | (row_bin << 2) | col_bin
                                    cells.append((a_val, row, col))
                                    
                                    if idx >= len(func_values) or func_values[idx] != target_value:
                                        all_target = False
                            
                            if not all_target:
                                continue
                            
                            covered = set()
                            for a_val, row, col in cells:
                                row_bin = KarnaughMinimizer._gray_position_to_binary(row, 2)
                                col_bin = KarnaughMinimizer._gray_position_to_binary(col, 2)
                                idx = (a_val << 4) | (row_bin << 2) | col_bin
                                if idx < len(func_values):
                                    covered.add(idx)
                            
                            if covered and covered.issubset(target_set):
                                implicant = KarnaughMinimizer._extract_implicant_5var(
                                    cells, variables, func_values, find_zeros
                                )
                                
                                if not any(g['covered'] == covered for g in groups):
                                    groups.append({
                                        'cells': cells,
                                        'covered': covered,
                                        'implicant': implicant,
                                        'size': height * width
                                    })
        
        # Ищем группы МЕЖДУ картами (a меняется)
        for height in sorted(possible_heights, reverse=True):
            for width in sorted(possible_widths, reverse=True):
                for start_row in range(n_rows):
                    for start_col in range(n_cols):
                        cells = []
                        all_target = True
                        
                        for a_val in [0, 1]:
                            for dr in range(height):
                                for dc in range(width):
                                    row = (start_row + dr) % n_rows
                                    col = (start_col + dc) % n_cols
                                    row_bin = KarnaughMinimizer._gray_position_to_binary(row, 2)
                                    col_bin = KarnaughMinimizer._gray_position_to_binary(col, 2)
                                    idx = (a_val << 4) | (row_bin << 2) | col_bin
                                    cells.append((a_val, row, col))
                                    
                                    if idx >= len(func_values) or func_values[idx] != target_value:
                                        all_target = False
                        
                        if not all_target:
                            continue
                        
                        covered = set()
                        for a_val, row, col in cells:
                            row_bin = KarnaughMinimizer._gray_position_to_binary(row, 2)
                            col_bin = KarnaughMinimizer._gray_position_to_binary(col, 2)
                            idx = (a_val << 4) | (row_bin << 2) | col_bin
                            if idx < len(func_values):
                                covered.add(idx)
                        
                        if covered and covered.issubset(target_set):
                            implicant = KarnaughMinimizer._extract_implicant_5var(
                                cells, variables, func_values, find_zeros
                            )
                            
                            if not any(g['covered'] == covered for g in groups):
                                groups.append({
                                    'cells': cells,
                                    'covered': covered,
                                    'implicant': implicant,
                                    'size': height * width * 2  # ×2 потому что 2 карты
                                })
        
        groups.sort(key=lambda x: x['size'], reverse=True)
        return groups

    @staticmethod
    def _extract_implicant_5var(cells: List[Tuple[int, int, int]],
                               variables: List[str],
                               func_values: List[int],
                               find_zeros: bool = False) -> str:
        result_vars = []
        
        # Собираем все индексы
        indices = []
        for a_val, row, col in cells:
            row_bin = KarnaughMinimizer._gray_position_to_binary(row, 2)
            col_bin = KarnaughMinimizer._gray_position_to_binary(col, 2)
            idx = (a_val << 4) | (row_bin << 2) | col_bin
            if idx < len(func_values):
                indices.append(idx)
        
        if not indices:
            return "0" if find_zeros else "1"
        
        # Проверяем каждую переменную (a=бит4, b=бит3, c=бит2, d=бит1, e=бит0)
        var_bits = [4, 3, 2, 1, 0]  # Позиции битов для a,b,c,d,e
        
        for var_idx, bit_pos in enumerate(var_bits):
            bits = [(idx >> bit_pos) & 1 for idx in indices]
            
            if len(set(bits)) == 1:
                bit_value = bits[0]
                
                if find_zeros:
                    # КНФ: 0 → переменная, 1 → !переменная
                    result_vars.append(variables[var_idx] if bit_value == 0 else f"!{variables[var_idx]}")
                else:
                    # ДНФ: 0 → !переменная, 1 → переменная
                    result_vars.append(f"!{variables[var_idx]}" if bit_value == 0 else variables[var_idx])
        
        if find_zeros:
            return "|".join(result_vars) if result_vars else "0"
        else:
            return "&".join(result_vars) if result_vars else "1"

    @staticmethod
    def _find_all_groups(func_values: List[int],
                        variables: List[str],
                        n_vars: int,
                        find_zeros: bool = False) -> List[Dict]:
        if n_vars == 5:
            return KarnaughMinimizer._find_all_groups_5var(func_values, variables, find_zeros)
        
        # Для 2-4 переменных используем старый метод
        groups = []
        n_row_vars = n_vars // 2
        n_col_vars = n_vars - n_row_vars
        n_rows = 2 ** n_row_vars
        n_cols = 2 ** n_col_vars
        
        row_codes = KarnaughMinimizer._gray_code(n_row_vars)
        col_codes = KarnaughMinimizer._gray_code(n_col_vars)
        
        target_value = 0 if find_zeros else 1
        target_set = set(i for i, v in enumerate(func_values) if v == target_value)
        
        if not target_set:
            return groups
        
        possible_heights = [2**i for i in range(n_row_vars + 1)]
        possible_widths = [2**i for i in range(n_col_vars + 1)]
        
        for height in sorted(possible_heights, reverse=True):
            for width in sorted(possible_widths, reverse=True):
                for start_row in range(n_rows):
                    for start_col in range(n_cols):
                        cells = []
                        all_target = True
                        
                        for dr in range(height):
                            for dc in range(width):
                                row = (start_row + dr) % n_rows
                                col = (start_col + dc) % n_cols
                                cells.append((row, col))
                                
                                idx = KarnaughMinimizer._get_cell_index(
                                    row, col, n_col_vars, n_row_vars
                                )
                                if idx >= len(func_values) or func_values[idx] != target_value:
                                    all_target = False
                        
                        if not all_target:
                            continue
                        
                        covered = set()
                        for row, col in cells:
                            idx = KarnaughMinimizer._get_cell_index(
                                row, col, n_col_vars, n_row_vars
                            )
                            if idx < len(func_values):
                                covered.add(idx)
                        
                        if covered and covered.issubset(target_set):
                            implicant = KarnaughMinimizer._extract_implicant(
                                cells, variables, n_row_vars, n_col_vars, 
                                func_values, find_zeros
                            )
                            
                            if not any(g['covered'] == covered for g in groups):
                                groups.append({
                                    'cells': cells,
                                    'covered': covered,
                                    'implicant': implicant,
                                    'size': height * width
                                })
        
        groups.sort(key=lambda x: x['size'], reverse=True)
        return groups

    @staticmethod
    def _extract_implicant(cells: List[Tuple[int, int]],
                          variables: List[str],
                          n_row_vars: int,
                          n_col_vars: int,
                          func_values: List[int],
                          find_zeros: bool = False) -> str:

        result_vars = []
        
        binary_indices = []
        for row, col in cells:
            idx = KarnaughMinimizer._get_cell_index(row, col, n_col_vars, n_row_vars)
            if idx < len(func_values):
                binary_indices.append(idx)
        
        if not binary_indices:
            return "0" if find_zeros else "1"
        
        n_vars = n_row_vars + n_col_vars
        
        for var_idx in range(n_vars):
            bit_position = n_vars - 1 - var_idx
            bits = [(idx >> bit_position) & 1 for idx in binary_indices]
            
            if len(set(bits)) == 1:
                bit_value = bits[0]
                
                if find_zeros:
                    result_vars.append(variables[var_idx] if bit_value == 0 else f"!{variables[var_idx]}")
                else:
                    result_vars.append(f"!{variables[var_idx]}" if bit_value == 0 else variables[var_idx])
        
        if find_zeros:
            return "|".join(result_vars) if result_vars else "0"
        else:
            return "&".join(result_vars) if result_vars else "1"

    @staticmethod
    def _select_essential_groups(groups: List[Dict],
                                target_terms: List[int]) -> List[Dict]:

        essential = []
        remaining = set(target_terms)

        for m in target_terms:
            covering_groups = [g for g in groups if m in g['covered']]
            if len(covering_groups) == 1 and covering_groups[0] not in essential:
                essential.append(covering_groups[0])
                remaining -= covering_groups[0]['covered']

        while remaining:
            best_group = max(
                (g for g in groups if g not in essential),
                key=lambda g: len(g['covered'] & remaining),
                default=None
            )
            if best_group:
                essential.append(best_group)
                remaining -= best_group['covered']
            else:
                break

        return essential

    @staticmethod
    def minimize_dnf(func_values: List[int],
                    variables: List[str],
                    n_vars: int,
                    verbose: bool = True) -> str:

        minterms = [i for i, v in enumerate(func_values) if v == 1]

        if not minterms:
            return "0"

        if len(minterms) == len(func_values):
            return "1"

        groups = KarnaughMinimizer._find_all_groups(
            func_values, variables, n_vars, find_zeros=False
        )

        essential = KarnaughMinimizer._select_essential_groups(groups, minterms)
        result = " ∨ ".join(g['implicant'] for g in essential)

        if verbose:
            print(f"\nМинимальная ДНФ: {result}\n")

        return result

    @staticmethod
    def minimize_cnf(func_values: List[int],
                    variables: List[str],
                    n_vars: int,
                    verbose: bool = True) -> str:

        maxterms = [i for i, v in enumerate(func_values) if v == 0]

        if len(maxterms) == len(func_values):
            return "0"

        if not maxterms:
            return "1"

        groups = KarnaughMinimizer._find_all_groups(
            func_values, variables, n_vars, find_zeros=True
        )

        essential = KarnaughMinimizer._select_essential_groups(groups, maxterms)
        result = " & ".join(f"({g['implicant']})" for g in essential)

        if verbose:
            print(f"\nМинимальная КНФ: {result}\n")

        return result

    @staticmethod
    def minimize(func_values: List[int],
                variables: List[str],
                n_vars: int,
                verbose: bool = True,
                forms: List[str] = None) -> Dict[str, str]:

        if forms is None:
            forms = ['both']

        results = {}

        if 'dnf' in forms or 'both' in forms:
            results['dnf'] = KarnaughMinimizer.minimize_dnf(
                func_values, variables, n_vars, verbose
            )

        if 'cnf' in forms or 'both' in forms:
            results['cnf'] = KarnaughMinimizer.minimize_cnf(
                func_values, variables, n_vars, verbose
            )

        return results

    @staticmethod
    def print_map(func_values: List[int],
                 variables: List[str],
                 n_vars: int,
                 show_minimization: bool = True,
                 forms: List[str] = None) -> Dict[str, str]:

        print("\n--- Карта Карно ---")

        if n_vars > 5 or n_vars < 2:
            print("Карта Карно поддерживается для 2-5 переменных")
            return {}

        gray = KarnaughMinimizer._gray_code

        if n_vars <= 4:
            n_row_vars = n_vars // 2
            n_col_vars = n_vars - n_row_vars
            r_vars = variables[:n_row_vars]
            c_vars = variables[n_row_vars:]
        else:  # n_vars == 5
            # Для визуализации: 4 строки (ab) × 8 столбцов (cde)
            n_row_vars = 2
            n_col_vars = 3
            r_vars = variables[:2]
            c_vars = variables[2:]

        r_codes = gray(n_row_vars)
        c_codes = gray(n_col_vars)

        row_var_name = "".join(r_vars)
        col_var_name = "".join(c_vars)

        print(f"\n     {col_var_name}")
        print(f"     {'  '.join(c_codes)}")

        for i, rc in enumerate(r_codes):
            row_vals = []
            for j, cc in enumerate(c_codes):
                idx = KarnaughMinimizer._get_cell_index(i, j, n_col_vars, n_row_vars)
                val = func_values[idx] if idx < len(func_values) else 0
                row_vals.append(str(val))

            print(f"{row_var_name}{rc} | {'  '.join(row_vals)}")

        results = {}
        if show_minimization:
            results = KarnaughMinimizer.minimize(
                func_values, variables, n_vars, verbose=True, forms=forms
            )

        return results