
def print_section(title):
    print(f"\n{title}")


def get_sdnf(variables, minterms):
    n = len(variables)
    terms = []
    for m in minterms:
        b = format(m, f'0{n}b')
        parts = [var if bit == '1' else f'¬{var}' for var, bit in zip(variables, b)]
        terms.append('·'.join(parts))
    return ' + '.join(terms)


def qm_minimize(variables, minterms):
    n = len(variables)
    if not minterms:
        return "0"

    # 1. Группировка по количеству единиц
    groups = {}
    for m in minterms:
        b = format(m, f'0{n}b')
        groups.setdefault(b.count('1'), []).append((b, {m}))

    prime_implicants = []
    while groups:
        new_groups = {}
        used = set()
        keys = sorted(groups.keys())

        # 2. Склеивание соседних групп
        for k in range(len(keys) - 1):
            for term1, mt1 in groups[keys[k]]:
                for term2, mt2 in groups[keys[k + 1]]:
                    diff = sum(a != b for a, b in zip(term1, term2))
                    if diff == 1:
                        comb = ''.join('-' if a != b else a for a, b in zip(term1, term2))
                        new_groups.setdefault(comb.count('1'), []).append((comb, mt1 | mt2))
                        used.add((term1, frozenset(mt1)))
                        used.add((term2, frozenset(mt2)))

        # 3. Сохранение неприменяемых термов как простых импликант
        for k in groups:
            for term, mt in groups[k]:
                if (term, frozenset(mt)) not in used:
                    prime_implicants.append((term, set(mt)))

        if not new_groups:
            break
        groups = new_groups

    remaining = set(minterms)
    result_cubes = []
    prime_implicants.sort(key=lambda x: len(x[1]), reverse=True)

    while remaining:
        best = max(prime_implicants, key=lambda x: len(x[1] & remaining))
        result_cubes.append(best[0])
        remaining -= best[1]

    def cube_to_str(cube):
        parts = []
        for var, bit in zip(variables, cube):
            if bit == '-': continue
            parts.append(var if bit == '1' else f'¬{var}')
        return '·'.join(parts) if parts else '1'

    return ' + '.join(cube_to_str(c) for c in result_cubes)


print_section("Одноразрядный сумматор (ОДС-3) в СДНФ")
vars_fa = ['A', 'B', 'Cin']
sum_minterms = [1, 2, 4, 7]  # 001, 010, 100, 111
cout_minterms = [3, 5, 6, 7]  # 011, 101, 110, 111

print("СДНФ Sum  :", get_sdnf(vars_fa, sum_minterms))
print("СДНФ Cout :", get_sdnf(vars_fa, cout_minterms))
print("\nМинимизированные функции (ДНФ):")
print("Sum  =", qm_minimize(vars_fa, sum_minterms))
print("Cout =", qm_minimize(vars_fa, cout_minterms))

print_section("Вычитающий счётчик (8 состояний) на Т-триггерах")
vars_cnt = ['Q2', 'Q1', 'Q0']
t0_minterms = [0, 1, 2, 3, 4, 5, 6, 7]  # T0=1 всегда
t1_minterms = [0, 2, 4, 6]  # T1=1 когда Q0=0
t2_minterms = [0, 4]  # T2=1 когда Q1=0 и Q0=0

print("СДНФ T0:", get_sdnf(vars_cnt, t0_minterms))
print("СДНФ T1:", get_sdnf(vars_cnt, t1_minterms))
print("СДНФ T2:", get_sdnf(vars_cnt, t2_minterms))
print("\nМинимизированные уравнения в базисе НЕ-И-ИЛИ:")
print("T0 =", qm_minimize(vars_cnt, t0_minterms))
print("T1 =", qm_minimize(vars_cnt, t1_minterms))
print("T2 =", qm_minimize(vars_cnt, t2_minterms))