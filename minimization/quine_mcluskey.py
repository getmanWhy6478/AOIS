"""Модуль минимизации методом Куайна-МакКласки"""

from typing import List, Set, Dict, Tuple


class QuineMcCluskeyMinimizer:
    """Класс для минимизации методом Куайна-МакКласки"""

    @staticmethod
    def _qm_step(minterms: List[str]) -> Tuple[List[str], List[str]]:
        """Один шаг склеивания"""
        grouped = {}
        for m in minterms:
            c = m.count('1')
            grouped.setdefault(c, []).append(m)

        next_minterms = []  # ← ИСПРАВЛЕНО: было next_terms
        marked = set()
        keys = sorted(grouped.keys())

        for i in range(len(keys) - 1):
            for t1 in grouped[keys[i]]:
                for t2 in grouped[keys[i + 1]]:
                    diff = sum(1 for a, b in zip(t1, t2) if a != b)
                    if diff == 1:
                        for k in range(len(t1)):
                            if t1[k] != t2[k]:
                                new_t = t1[:k] + '-' + t1[k + 1:]
                                if new_t not in next_minterms:
                                    next_minterms.append(new_t)
                                marked.add(t1)
                                marked.add(t2)
                                break

        primes = [m for m in minterms if m not in marked]
        return list(set(next_minterms)), primes  # ← ИСПРАВЛЕНО: было next_terms

    @staticmethod
    def _format_term_dnf(pattern: str, variables: List[str]) -> str:
        """Преобразует шаблон в терм ДНФ"""
        terms = []
        for var, char in zip(variables, pattern):
            if char == '1':
                terms.append(var)
            elif char == '0':
                terms.append(f"!{var}")
        return "&".join(terms) if terms else "1"

    @staticmethod
    def _format_term_cnf(pattern: str, variables: List[str]) -> str:
        """Преобразует шаблон в терм КНФ"""
        terms = []
        for var, char in zip(variables, pattern):
            if char == '0':
                terms.append(var)
            elif char == '1':
                terms.append(f"!{var}")
        return "|".join(terms) if terms else "0"

    @staticmethod
    def minimize_dnf(sdnf_nums: List[int], variables: List[str],
                     show_steps: bool = True) -> str:
        """Минимизация в ДНФ"""
        n_vars = len(variables)
        current = [bin(x)[2:].zfill(n_vars) for x in sdnf_nums]
        all_primes = []

        if show_steps:
            print(f"\n🔹 МИНИМИЗАЦИЯ В ДНФ")
            print(f"Начальные термы (F=1): {current}")

        step = 0
        while True:
            step += 1
            next_terms, primes = QuineMcCluskeyMinimizer._qm_step(current)

            if primes and show_steps:
                print(f"Шаг {step}: Простые импликанты -> {primes}")
            all_primes.extend(primes)

            if not next_terms:
                break
            if show_steps:
                print(f"Шаг {step}: Склеенные термы -> {next_terms}")
            current = next_terms

        if not all_primes:
            return "0"

        result = QuineMcCluskeyMinimizer._select_cover_dnf(all_primes, sdnf_nums, variables)

        if show_steps:
            print(f"\n✅ Минимальная ДНФ: {result}")

        return result

    @staticmethod
    def minimize_cnf(func_values: List[int], variables: List[str],
                     show_steps: bool = True) -> str:
        """Минимизация в КНФ"""
        n_vars = len(variables)
        n_total = 2 ** n_vars

        maxterms = [i for i, v in enumerate(func_values) if v == 0]

        if show_steps:
            print("\n МИНИМИЗАЦИЯ В КНФ")
            print(f"Наборы где F=0: {maxterms}")

        if len(maxterms) == n_total:
            if show_steps:
                print("\n Минимальная КНФ: 0")
            return "0"

        if not maxterms:
            if show_steps:
                print("\nМинимальная КНФ: 1")
            return "1"

        current = [bin(x)[2:].zfill(n_vars) for x in maxterms]
        all_primes = []

        if show_steps:
            print(f"Начальные термы (F=0): {current}")

        step = 0
        while True:
            step += 1
            next_terms, primes = QuineMcCluskeyMinimizer._qm_step(current)

            if primes and show_steps:
                print(f"Шаг {step}: Простые импликанты -> {primes}")
            all_primes.extend(primes)

            if not next_terms:
                break
            if show_steps:
                print(f"Шаг {step}: Склеенные термы -> {next_terms}")
            current = next_terms

        if not all_primes:
            return "1"

        result = QuineMcCluskeyMinimizer._select_cover_cnf(all_primes, maxterms, variables)

        if show_steps:
            print(f"\nМинимальная КНФ: {result}")

        return result

    @staticmethod
    def minimize(sdnf_nums: List[int], func_values: List[int],
                 variables: List[str], show_steps: bool = True,
                 forms: List[str] = None) -> Dict[str, str]:
        """Минимизация в ДНФ и/или КНФ"""
        if forms is None:
            forms = ['both']

        results = {}

        if 'dnf' in forms or 'both' in forms:
            results['dnf'] = QuineMcCluskeyMinimizer.minimize_dnf(
                sdnf_nums, variables, show_steps
            )

        if 'cnf' in forms or 'both' in forms:
            results['cnf'] = QuineMcCluskeyMinimizer.minimize_cnf(
                func_values, variables, show_steps
            )

        return results

    @staticmethod
    def _select_cover_dnf(primes: List[str],
                          minterms: List[int],
                          variables: List[str]) -> str:
        """Выбор покрытия для ДНФ"""
        n_vars = len(variables)
        coverage = {}

        for p in primes:
            covered = []
            for m in minterms:
                m_bin = bin(m)[2:].zfill(n_vars)
                if all(p[k] == '-' or p[k] == m_bin[k] for k in range(len(p))):
                    covered.append(m)
            coverage[p] = covered

        remaining = set(minterms)
        selected = []

        while remaining:
            best = max(coverage.keys(),
                       key=lambda p: len(set(coverage[p]) & remaining))
            selected.append(best)
            remaining -= set(coverage[best])

        return " | ".join(QuineMcCluskeyMinimizer._format_term_dnf(p, variables)
                          for p in selected)

    @staticmethod
    def _select_cover_cnf(primes: List[str],
                          maxterms: List[int],
                          variables: List[str]) -> str:
        """Выбор покрытия для КНФ"""
        n_vars = len(variables)
        coverage = {}

        for p in primes:
            covered = []
            for m in maxterms:
                m_bin = bin(m)[2:].zfill(n_vars)
                if all(p[k] == '-' or p[k] == m_bin[k] for k in range(len(p))):
                    covered.append(m)
            coverage[p] = covered

        remaining = set(maxterms)
        selected = []

        while remaining:
            best = max(coverage.keys(),
                       key=lambda p: len(set(coverage[p]) & remaining))
            selected.append(best)
            remaining -= set(coverage[best])

        return " & ".join(f"({QuineMcCluskeyMinimizer._format_term_cnf(p, variables)})"
                          for p in selected)

    @staticmethod
    def print_tabular(sdnf_nums: List[int], func_values: List[int],
                      variables: List[str], form: str = 'dnf') -> None:
        """Таблица покрытия для ДНФ или КНФ"""
        n_vars = len(variables)

        if form == 'dnf':
            print("\nТаблица покрытия для ДНФ:")
            current = [bin(x)[2:].zfill(n_vars) for x in sdnf_nums]
            terms_nums = sdnf_nums
        else:
            print("\nТаблица покрытия для КНФ:")
            maxterms = [i for i, v in enumerate(func_values) if v == 0]
            current = [bin(x)[2:].zfill(n_vars) for x in maxterms]
            terms_nums = maxterms

        all_primes = []
        while True:
            next_terms, primes = QuineMcCluskeyMinimizer._qm_step(current)
            all_primes.extend(primes)
            if not next_terms:
                break
            current = next_terms

        header = "ПИ    | " + " ".join(f"{m:2}" for m in terms_nums)
        print(header)
        print("-" * len(header))

        coverage = {}
        for p in all_primes:
            row = f"{p:5} | "
            cov = []
            for m in terms_nums:
                m_bin = bin(m)[2:].zfill(n_vars)
                if all(p[k] == '-' or p[k] == m_bin[k] for k in range(len(p))):
                    row += " X "
                    cov.append(m)
                else:
                    row += " . "
            coverage[p] = cov
            print(row)

        essential = []
        remaining = set(terms_nums)

        for m in terms_nums:
            owners = [p for p, c in coverage.items() if m in c]
            if len(owners) == 1 and owners[0] not in essential:
                essential.append(owners[0])
                remaining -= set(coverage[owners[0]])

        while remaining:
            best = max((p for p in coverage if p not in essential),
                       key=lambda p: len(set(coverage[p]) & remaining), default=None)
            if best:
                essential.append(best)
                remaining -= set(coverage[best])
            else:
                break

        if form == 'dnf':
            result = " | ".join(QuineMcCluskeyMinimizer._format_term_dnf(p, variables)
                                for p in essential)
            print(f"\nМинимальная ДНФ: {result}")
        else:
            result = " & ".join(f"({QuineMcCluskeyMinimizer._format_term_cnf(p, variables)})"
                                for p in essential)
            print(f"\nМинимальная КНФ: {result}")