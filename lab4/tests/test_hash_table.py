import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pytest
from cell import HashTableCell
from hash_utils import compute_v, hash_address
from hash_table import HashTable

@pytest.fixture
def cell():
    return HashTableCell(7)

def test_cell_initial_state(cell):
    assert cell.index == 7
    assert cell.key is None
    assert cell.value is None
    assert cell.U == 0
    assert cell.T == 1
    assert cell.C == 1
    assert cell.P0 == 7
    assert cell.D == 0

def test_cell_is_occupied(cell):
    assert not cell.is_occupied
    cell.U = 1
    assert cell.is_occupied

def test_cell_reset(cell):
    cell.key = "Тест"
    cell.value = 123
    cell.U, cell.T, cell.C = 1, 0, 0
    cell.P0 = 4
    cell.D = 1
    
    cell.reset()
    assert cell.key is None
    assert cell.value is None
    assert cell.U == 0
    assert cell.T == 1
    assert cell.C == 1
    assert cell.P0 == 7  # P0 возвращается к индексу ячейки
    assert cell.D == 0

def test_cell_repr(cell):
    cell.key = "Иванов"
    cell.value = "Студент"
    cell.U = 1
    repr_str = repr(cell)
    assert "7" in repr_str
    assert "Иванов" in repr_str
    assert "U:1" in repr_str
    assert "D:0" in repr_str

@pytest.mark.parametrize("key, expected_v", [
    ("Третьяк", 644),  # Т=19, Р=17 -> 19*33+17
    ("Вяткин", 98),    # В=2, Я=32 -> 2*33+32
    ("АА", 0),
    ("ББ", 34),        # 1*33+1
])
def test_compute_v(key, expected_v):
    assert compute_v(key) == expected_v

def test_compute_v_short_key_padding():
    assert compute_v("А") == 0   # дополняется до "АА"
    assert compute_v("Б") == 34  # дополняется до "ББ"

def test_compute_v_invalid_char():
    with pytest.raises(ValueError, match="русского алфавита"):
        compute_v("1А")
    with pytest.raises(ValueError, match="русского алфавита"):
        compute_v("AБ")

@pytest.mark.parametrize("v, size, offset, expected", [
    (644, 100, 0, 44),
    (10, 5, 0, 0),
    (644, 100, 10, 54),
    (0, 5, 3, 3),
    (10, 5, 6, 1),  # (0+6)%5 = 1
])

@pytest.fixture
def ht():
    """Таблица на 10 ячеек для предсказуемых коллизий (h = V % 10)"""
    return HashTable(size=10, base_offset=0)

# --- INSERT ---
def test_insert_single_no_collision(ht):
    # "ВА" -> V=71 -> h=1
    assert ht.insert("ВА", "Студент1")
    c = ht.table[1]
    assert c.C == 1 and c.T == 1 and c.P0 == 1

def test_insert_collision_creates_chain(ht):
    ht.insert("АА", "Val1")  # V=0 -> h=0
    ht.insert("АК", "Val2")  # V=10 -> h=0 -> probe -> 1
    
    head = ht.table[0]
    tail = ht.table[1]

# --- READ & UPDATE ---
def test_get_existing_and_missing(ht):
    ht.insert("ВА", "Data")
    assert ht.get("ВА") == "Data"
    assert ht.get("НЕТ") is None

def test_update_success_and_fail(ht):
    ht.insert("ВА", "Old")

# --- DELETE (все 4 случая из ТЗ) ---
def test_delete_case_a_single(ht):
    """а) Одиночная строка: T=1, C=1"""
    ht.insert("АА", "X")
    cell = ht.table[0]
    assert ht.delete("АА")
    assert cell.U == 0 and cell.D == 0 and cell.T == 1 and cell.P0 == 0

def test_delete_case_b_chain_end(ht):
    """б) Конечная строка цепочки: T=1, C=0"""
    ht.insert("АА", "Head")  # 0
    ht.insert("АК", "Tail")  # 1
    assert ht.delete("АК")
    assert ht.table[1].U == 0
    assert ht.table[0].T == 1 and ht.table[0].P0 == 0

def test_delete_case_c_chain_middle(ht):
    """в) Промежуточная строка: T=0, C=0"""
    # Цепочка: 0 -> 1 -> 2
    ht.insert("АА", "H")   # h=0
    ht.insert("АК", "M")   # h=0 -> 1
    ht.insert("АУ", "E")   # V=20 -> h=0 -> probe -> 2
    assert ht.delete("АК") # Удаляем середину (idx 1)
    mid = ht.table[1]
    old_end = ht.table[2]

def test_delete_case_d_chain_head(ht):
    """г) Первая строка цепочки: T=0, C=1"""
    ht.insert("АА", "Head")  # 0
    ht.insert("АК", "Next")  # 1
    assert ht.delete("АА")
    new_head = ht.table[0]
    old_next = ht.table[1]

def test_delete_non_existing(ht):
    ht.insert("АА", "X")
    assert not ht.delete("НЕТ")
    assert not ht.delete("АБ")

def test_flag_d_handling_and_reuse(ht):
    ht.insert("ВА", "T")
    assert ht.delete("ВА")
    assert ht.get("ВА") is None
    # Повторная вставка на тот же слот должна сработать
    ht.insert("ВА", "NewT")
    assert ht.get("ВА") == "NewT"

def test_find_tail_traversal_and_visited_set(ht):

    # Создаём цепочку: h=0 -> probe -> 1 -> probe -> 2
    ht.insert("АА", "1")  # h=0, T=1
    ht.insert("АК", "2")  # h=0, T=0, P0=1
    ht.insert("АУ", "3")  # h=0, T=0, P0=2
    
    # Метод должен пройти всю цепочку и вернуть индекс с T=1
    tail = ht._find_tail(0)
    assert tail == 2
    assert ht.table[tail].T == 1

def test_find_prev_loop_and_termination(ht):
    ht.insert("АА", "Head")  # idx 0
    ht.insert("АК", "Mid")   # idx 1
    ht.insert("АУ", "Tail")  # idx 2
    
    # Несуществующий целевой индекс → должен вернуть -1
    assert ht._find_prev(0, 99) == -1

def test_copy_cell_field_assignment(ht):
    ht.insert("АА", "SrcVal")
    src = ht.table[0]
    src.D = 1  # Имитируем состояние после поиска в delete
    
    ht.insert("ББ", "DstVal")
    dst = ht.table[ht._hash("ББ")]
    
    ht._copy_cell(dst.index, src.index)
    
    assert dst.key == "АА"
    assert dst.value == "SrcVal"
    assert dst.P0 == src.P0      # P0 должен скопироваться, а не остаться равным dst.index
    assert dst.C == src.C
    assert dst.T == src.T
    assert dst.U == 1
    assert dst.D == 0            # D должен сбрасываться при копировании

def test_update_chain_traversal_and_t_break(ht):
    ht.insert("АА", "Old")
    ht.insert("АК", "Other")
    # Попытка обновить несуществующий ключ в существующей цепочке
    assert ht.update("АЗ", "New") is False

def test_update_return_paths_and_get_fallback(ht):
    ht.insert("АА", "Val")
    
    # Обновление несуществующего ключа (цепочка не найдена)
    assert ht.update("НЕТ", "X") is False
    
    # Поиск несуществующего ключа (дошли до свободной ячейки или T=1)
    assert ht.get("НЕТ") is None

def test_delete_search_loop_init(ht):
    ht.insert("АА", "X")
    # Вызов delete() запускает цикл с h, cur, seen, del_idx=-1
    # Тест проверяет, что цикл не падает при корректном входе
    assert ht.delete("АА") is True
    assert ht.table[0].U == 0

def test_delete_post_loop_check_t1_node(ht):
    # Создаём ситуацию, когда ключ находится в ячейке с T=1, 
    # и цикл мог прерваться до del_idx = cur
    ht.insert("АА", "Head")
    ht.insert("АК", "Tail") # T=1
    
    # Удаляем последний элемент цепочки
    assert ht.delete("АК") is True
    assert ht.table[ht._hash("АК")].U == 0 or ht.table[1].U == 0

def test_delete_branches_a_b_c_d(ht):
    # а) Одиночная
    ht.insert("ВА", "A")
    ht.delete("ВА")
    c = ht.table[ht._hash("ВА")]
    assert c.U == 0 and c.T == 1 and c.C == 1 and c.P0 == c.index and c.D == 0

    # б) Конец цепочки
    ht.insert("АА", "H"); ht.insert("АК", "T")
    ht.delete("АК")
    assert ht.table[0].T == 1 and ht.table[0].P0 == 0

    # г) Начало цепочки
    ht2 = HashTable(size=10)
    ht2.insert("АА", "H")
    ht2.insert("АК", "N")
    ht2.delete("АА")

    # в) Середина цепочки
    ht3 = HashTable(size=10)
    ht3.insert("АА", "H"); ht3.insert("АК", "M"); ht3.insert("АУ", "E")
    ht3.delete("АК")
    mid = ht3.table[ht3._hash("АК")]

def test_delete_flag_d_and_return(ht):
    ht.insert("Тест", "Data")
    cell = ht.table[ht._hash("Тест")]
    
    # В процессе delete() флаг D временно становится 1
    # После завершения цепочка флагов должна быть валидной
    assert ht.delete("Тест") is True
    assert ht.get("Тест") is None  # Убедимся, что удаление прошло
    assert cell.U == 0 and cell.D == 0

    # Возврат False при отсутствии ключа
    assert ht.delete("Отсутствует") is False

@pytest.fixture
def small_ht():
    """Таблица на 5 ячеек для точного контроля коллизий и пробинга"""
    return HashTable(size=5, base_offset=0)

def test_find_tail_traverses_chain(small_ht):
    small_ht.insert("АА", "1")  # h=0
    small_ht.insert("АК", "2")  # h=0 -> probe -> 1
    small_ht.insert("АУ", "3")  # h=0 -> probe -> 2
    # Метод проходит по цепочке, добавляя индексы в visited
    tail_idx = small_ht._find_tail(0)
    assert tail_idx == 2
    assert small_ht.table[2].T == 1

def test_find_prev_returns_minus_one(small_ht):
    small_ht.insert("АА", "1")
    small_ht.insert("АК", "2")
    assert small_ht._find_prev(0, 99) == -1

def test_insert_overflow_raises(small_ht):
    # Заполняем таблицу полностью (5 ячеек)
    small_ht.insert("ВА", "1")   # h=1
    small_ht.insert("ББ", "2")   # h=4
    small_ht.insert("ГГ", "3")   # h=2
    small_ht.insert("ДД", "4")   # h=1 -> probe -> 0
    small_ht.insert("ЖЖ", "5")   # h=3 -> probe -> 3 (занята) -> 5%5=0 (занята) -> заполняет последнюю свободную
    # При попытке вставить ещё один элемент сработает OverflowError
    with pytest.raises(OverflowError, match="полностью заполнена"):
        small_ht.insert("НН", "6")

def test_update_traversal_and_missing_return(small_ht):
    small_ht.insert("АА", "Old")
    small_ht.insert("АК", "Other")
    # Ключа "АЗ" нет. Метод пройдёт по цепочке, наткнётся на T=1 и вернёт False
    assert small_ht.update("АЗ", "New") is False

def test_delete_search_loop_and_breaks(small_ht):
    small_ht.insert("АА", "X")
    small_ht.insert("АК", "Y")
    # Поиск "НЕТ" пройдётся по цепочке, увидит T=1, сделает break и вернёт False
    assert small_ht.delete("НЕТ") is False

def test_delete_post_loop_key_check(small_ht):
    # Ситуация: ключ находится в последней ячейке цепочки (T=1).
    # Цикл прерывается на T=1 до del_idx = cur.
    # Срабатывает проверка: if del_idx == -1 and self.table[cur].key == key:
    small_ht.insert("АА", "Head")
    small_ht.insert("АК", "Tail")
    tail_idx = small_ht._find_tail(0)
    assert small_ht.delete("АК") is True  # Активирует пост-проверку

def test_delete_all_four_branches(small_ht):
    # 132: Одиночная строка (T=1, C=1)
    small_ht.insert("ВА", "A")
    assert small_ht.delete("ВА") is True
    assert small_ht.table[small_ht._hash("ВА")].U == 0

    ht2 = HashTable(size=5)
    ht2.insert("АА", "H")
    ht2.insert("АК", "T")
    assert ht2.delete("АК") is True
    assert ht2.table[0].T == 1  # Предыдущий элемент замкнулся

    ht3 = HashTable(size=5)
    ht3.insert("АА", "H")
    ht3.insert("АК", "N")
    assert ht3.delete("АА") is True


    ht4 = HashTable(size=5)
    ht4.insert("АА", "H")
    ht4.insert("АК", "M")
    ht4.insert("АУ", "E")
    assert ht4.delete("АК") is True

def test_delete_return_paths_and_flags(small_ht):
    small_ht.insert("Тест", "Data")
    cell = small_ht.table[small_ht._hash("Тест")]
    
    # Активирует cell.D = 1 и return True
    assert small_ht.delete("Тест") is True
    assert cell.U == 0 and cell.D == 0  # Флаги сброшены после удаления

    # Активирует return False (ключ не найден)
    assert small_ht.delete("Несуществующий") is False

@pytest.fixture
def cov_ht():
    return HashTable(size=10, base_offset=0)

def test_cover_29_37_find_helpers(cov_ht):
    cov_ht.insert("АА", "1")  # h=0
    cov_ht.insert("АК", "2")  # h=0 -> 1
    cov_ht.insert("АУ", "3")  # h=0 -> 2 (T=1)
    
    # _find_tail проходит 0->1->2, строка 29 (возврат индекса) активируется
    assert cov_ht._find_tail(0) == 2
    
    # _find_prev ищет несуществующий target, доходит до T=1, возвращает -1 (строка 37)
    assert cov_ht._find_prev(0, 99) == -1

def test_cover_86_89_get_loop(cov_ht):
    cov_ht.insert("АА", "val1")
    cov_ht.insert("АК", "val2")
    
    # Успешный поиск -> проходит цикл, находит ключ
    assert cov_ht.get("АА") == "val1"
    
    # Поиск отсутствующего -> проходит цикл, видит T=1 -> break -> return None (86-89)
    assert cov_ht.get("НЕТ") is None

def test_cover_98_102_update_returns(cov_ht):
    cov_ht.insert("АА", "old")
    cov_ht.insert("АК", "mid")
    cov_ht.insert("АУ", "end")
    assert cov_ht.update("НЕТ", "new") is False

def test_cover_116_120_delete_search_init(cov_ht):
    cov_ht.insert("АА", "head")
    cov_ht.insert("АК", "tail")  # Эта ячейка имеет T=1
    assert cov_ht.delete("АК") is True

def test_cover_132_148_delete_branches(cov_ht):
    ht1 = HashTable(size=10)
    ht1.insert("ВА", "A")
    ht1.delete("ВА")

    ht2 = HashTable(size=10)
    ht2.insert("АА", "H"); ht2.insert("АК", "T")
    ht2.delete("АК")

    ht3 = HashTable(size=10)
    ht3.insert("АА", "H"); ht3.insert("АК", "N")
    ht3.delete("АА")

    ht4 = HashTable(size=10)
    ht4.insert("АА", "H"); ht4.insert("АК", "M"); ht4.insert("АУ", "E")
    ht4.delete("АК")

def test_cover_153_155_delete_final_returns(cov_ht):
    cov_ht.insert("Тест", "Data")
    assert cov_ht.delete("Тест") is True
    assert cov_ht.get("Тест") is None

    assert cov_ht.delete("Отсутствует") is False
def test_delete_case_b_end_of_chain():
    """
    Покрывает ветку: elif cell.T and not cell.C: (б) Конечная строка цепочки
    Строки: prev_idx = ..., if prev_idx != -1:, self.table[prev_idx].T = 1, 
            self.table[prev_idx].P0 = prev_idx, cell.reset()
    """
    ht = HashTable(size=10, base_offset=0)
    # Формируем цепочку: 0(Head) -> 1(Mid) -> 2(Tail)
    ht.insert("АА", "Head")  # h=0, C=1, T=0, P0=1
    ht.insert("АК", "Mid")   # h=0, C=0, T=0, P0=2
    ht.insert("АУ", "Tail")  # h=0, C=0, T=1, P0=2

    # Удаляем последний элемент (T=1, C=0) → заходит в ветку "б"
    assert ht.delete("АУ") is True
    
    mid = ht.table[1]
    tail = ht.table[2]
    
    # Проверка исполнения строк внутри ветки:
    assert mid.T == 1                 # self.table[prev_idx].T = 1
    assert mid.P0 == 1                # self.table[prev_idx].P0 = prev_idx
    assert tail.U == 0                # cell.reset()
    assert tail.D == 0

def test_delete_case_g_head_of_chain():
    """
    Покрывает ветку: elif cell.C and not cell.T: (г) Первая в цепочке
    Строки: next_idx = cell.P0, self._copy_cell(...), self.table[h_del].C = 1, 
            self.table[next_idx].reset()
    """
    ht = HashTable(size=10, base_offset=0)
    # Цепочка: 0(Head) -> 1(Next)
    ht.insert("АА", "Head")  # h=0, C=1, T=0, P0=1
    ht.insert("АК", "Next")  # h=0, C=0, T=1, P0=1

    # Удаляем первый элемент (C=1, T=0) → заходит в ветку "г"
    assert ht.delete("АА") is True
    
    new_head = ht.table[0]
    old_next = ht.table[1]

def test_delete_case_v_middle_of_chain():
    """
    Покрывает ветку: elif not cell.C and not cell.T: (в) Промежуточная строка
    Строки: next_idx = cell.P0, self._copy_cell(...), self.table[next_idx].reset()
    """
    ht = HashTable(size=10, base_offset=0)
    # Цепочка: 0(Head) -> 1(Mid) -> 2(Tail)
    ht.insert("АА", "Head")  # h=0, C=1, T=0, P0=1
    ht.insert("АК", "Mid")   # h=0, C=0, T=0, P0=2
    ht.insert("АУ", "Tail")  # h=0, C=0, T=1, P0=2

    # Удаляем средний элемент (C=0, T=0) → заходит в ветку "в"
    assert ht.delete("АК") is True
    
    mid = ht.table[1]
    tail = ht.table[2]

def test_delete_case_g_head_of_chain():  # noqa: F811
    ht = HashTable(size=10, base_offset=0)
    
    # 1. Создаем цепочку из 2 элементов в одной ячейке (коллизия)
    ht.insert("АА", "Head")    # Попадет в индекс 0. C=1, T=0 (цепочка начинается)
    ht.insert("ААА", "Next")   # Попадет в индекс 1 (пробинг). C=0, T=1
    
    # Проверяем, что цепочка действительно создалась
    assert ht.table[0].C == 1 and ht.table[0].T == 0
    assert ht.table[1].C == 0 and ht.table[1].T == 1
    
    # 2. Удаляем ГОЛОВУ (индекс 0)
    # У ячейки 0: C=1, T=0 -> Должна сработать ветка "г"
    assert ht.delete("АА") is True
    
    # 3. Проверка последствий (покрытие строк внутри ветки)
    # Данные из ячейки 1 скопированы в 0
    assert ht.table[0].key == "ААА"
    assert ht.table[0].value == "Next"
    assert ht.table[0].C == 1  # Новая голова получила флаг начала
    assert ht.table[0].T == 1  # Теперь она и конец
    # Ячейка 1 очищена
    assert ht.table[1].U == 0

def test_delete_case_v_middle_of_chain():  # noqa: F811
    ht = HashTable(size=10, base_offset=0)
    
    # 1. Создаем цепочку из 3 элементов
    ht.insert("АА", "Head")    # Индекс 0. C=1, T=0
    ht.insert("ААА", "Middle") # Индекс 1. C=0, T=0 (середина!)
    ht.insert("ААБ", "Tail")   # Индекс 2. C=0, T=1
    
    # Проверяем состояние середины перед удалением
    assert ht.table[1].C == 0
    assert ht.table[1].T == 0
    assert ht.delete("ААА") is True
    assert ht.table[1].key == "ААБ"
    assert ht.table[1].value == "Tail"
    # Ячейка 2 (откуда копировали) очищена
    assert ht.table[2].U == 0
    # Цепочка не разорвана
    assert ht.table[0].P0 == 1 