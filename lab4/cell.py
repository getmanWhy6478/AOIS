class HashTableCell:

    def __init__(self, index: int):
        self.index = index
        self.key = None
        self.value = None
        self.U = 0  # Флаг занятости
        self.T = 1  # Флаг конца цепочки
        self.C = 1  # Флаг начала цепочки
        self.P0 = index  # Указатель на следующую ячейку в цепочке
        self.D = 0 #1 - помечена к удалению, 0 - нет

    @property
    def is_occupied(self) -> bool:
        return self.U == 1

    def reset(self):
        self.key = None
        self.value = None
        self.U = 0
        self.T = 1
        self.C = 1
        self.P0 = self.index
        self.D = 0

    def __repr__(self) -> str:
        if self.is_occupied:
            return (f"[{self.index:>2}] Ключ: {self.key:<12} | Знач: {self.value:<10} | "
                    f"U:{self.U} T:{self.T} C:{self.C} P0:{self.P0} D:{self.D}")
        return f"[{self.index:>2}] <СВОБОДНО>"