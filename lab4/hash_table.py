from cell import HashTableCell
from hash_utils import compute_v, hash_address


class HashTable:
    def __init__(self, size: int, base_offset: int = 0):
        self.size = size
        self.B = base_offset
        self.table = [HashTableCell(i) for i in range(size)]

    def _hash(self, key: str) -> int:
        v = compute_v(key)
        return hash_address(v, self.size, self.B)

    def _place(self, idx: int, key: str, value, head: bool, tail: bool):
        c = self.table[idx]
        c.key, c.value = key, value
        c.U, c.C, c.T = 1, int(head), int(tail)
        c.P0 = idx

    def _find_tail(self, head_idx: int) -> int:
        cur = head_idx
        visited = set()
        while cur not in visited:
            visited.add(cur)
            if self.table[cur].T == 1:
                return cur
            cur = self.table[cur].P0
        return cur  # Возвращает текущий, если цепочка замкнута (защита)

    def _find_prev(self, head_idx: int, target_idx: int) -> int:
        cur = head_idx
        while self.table[cur].P0 != target_idx:
            if self.table[cur].T:
                return -1
            cur = self.table[cur].P0
        return cur

    def _copy_cell(self, dst_idx: int, src_idx: int):
        src = self.table[src_idx]
        dst = self.table[dst_idx]
        dst.key = src.key
        dst.value = src.value
        dst.P0 = src.P0
        dst.C = src.C
        dst.T = src.T
        dst.U = 1
        dst.D = 0

    def insert(self, key: str, value) -> bool:
        h = self._hash(key)

        if not self.table[h].is_occupied:
            self._place(h, key, value, head=True, tail=True)
            return True

        cur = (h + 1) % self.size
        steps = 0
        while self.table[cur].is_occupied and steps < self.size:
            cur = (cur + 1) % self.size
            steps += 1

        if steps == self.size:
            raise OverflowError("Хеш-таблица полностью заполнена")

        tail_idx = self._find_tail(h)

        # Старый последний элемент перестаёт быть последним
        self.table[tail_idx].T = 0
        # Связываем его с новой свободной ячейкой
        self.table[tail_idx].P0 = cur

        # 4. Размещаем новую запись в найденный слот
        self._place(cur, key, value, head=False, tail=True)
        return True

    def get(self, key: str):
        h, cur, seen = self._hash(key), self._hash(key), set()
        while cur not in seen:
            seen.add(cur)
            c = self.table[cur]
            if not c.is_occupied:
                return None
            if c.key == key:
                return c.value
            if c.T:
                break
            cur = c.P0
        return None

    def update(self, key: str, new_value) -> bool:
        h, cur, seen = self._hash(key), self._hash(key), set()
        while cur not in seen:
            seen.add(cur)
            c = self.table[cur]
            if not c.is_occupied or c.T:
                return False
            if c.key == key:
                c.value = new_value
                return True
            cur = c.P0
        return False

    def delete(self, key: str) -> bool:
        h, cur, seen, del_idx = self._hash(key), self._hash(key), set(), -1

        # 1. Поиск удаляемой строки
        while cur not in seen:
            seen.add(cur)
            c = self.table[cur]
            if c.key == key:
                del_idx = cur
                break
            if not c.is_occupied or c.T:
                break
            cur = c.P0

        # Проверка на случай, если ключ в последней ячейке (T=1)
        if del_idx == -1 and self.table[cur].key == key:
            del_idx = cur
        if del_idx == -1:
            return False

        cell = self.table[del_idx]
        cell.D = 1  # Шаг 1 ТЗ: флажок вычёркивания
        h_del = del_idx

        # 2. Анализ флагов (строго по комбинации T и C)
        if cell.T and cell.C:  # а) Одиночная строка
            cell.reset()

        elif cell.T and not cell.C:  # б) Конечная строка цепочки
            prev_idx = self._find_prev(h, h_del)
            if prev_idx != -1:
                self.table[prev_idx].T = 1
                self.table[prev_idx].P0 = prev_idx  # Замыкаем предыдущую на себя
            cell.reset()

        elif cell.C and not cell.T:  # г) Первая в цепочке
            next_idx = cell.P0
            self._copy_cell(h_del, next_idx)
            self.table[h_del].C = 1  # Новая ячейка становится началом
            self.table[next_idx].reset()

        elif not cell.C and not cell.T:  # в) Промежуточная строка
            next_idx = cell.P0
            self._copy_cell(h_del, next_idx)
            self.table[next_idx].reset()

        return True

    def display(self):
        print("ХЕШ-ТАБЛИЦА")
        for i in range(self.size):
            print(self.table[i])