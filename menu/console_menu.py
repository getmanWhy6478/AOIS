"""Модуль консольного меню"""

from typing import Optional, Callable, List, Tuple
from utils.helpers import  pause


class ConsoleMenu:
    """Класс для создания консольного меню"""

    def __init__(self, title: str = "Меню"):
        self.title = title
        self.items: List[Tuple[str, Optional[Callable], Optional[str]]] = []
        self.running = True

    def add_item(self, label: str,
                 action: Optional[Callable] = None,
                 description: Optional[str] = None) -> 'ConsoleMenu':
        """Добавляет пункт меню"""
        self.items.append((label, action, description))
        return self

    def add_separator(self) -> 'ConsoleMenu':
        """Добавляет разделитель"""
        self.items.append(("", None, None))
        return self

    def add_exit(self, label: str = "Выход") -> 'ConsoleMenu':
        """Добавляет пункт выхода"""
        self.items.append((label, None, "exit"))
        return self

    def _display(self) -> None:
        """Отображает меню"""
        print()

        for i, (label, _, desc) in enumerate(self.items, 1):
            if label:
                if desc and desc != "exit":
                    print(f"{i}. {label} — {desc}")
                elif desc == "exit":
                    print(f"{i}. {label}")
                else:
                    print(f"{i}. {label}")
            else:
                print("-" * 30)
        print()

    def _get_choice(self) -> int:
        """Получает выбор пользователя"""
        while True:
            try:
                choice = input("Выберите пункт: ").strip()
                num = int(choice)
                if 1 <= num <= len(self.items):
                    if self.items[num - 1][0]:  # Не разделитель
                        return num
            except (ValueError, KeyboardInterrupt):
                pass
            print("Неверный выбор, попробуйте снова")

    def run(self) -> None:
        """Запускает меню"""
        while self.running:
            self._display()
            choice = self._get_choice()
            label, action, desc = self.items[choice - 1]

            if desc == "exit":
                self.running = False
            elif action:
                try:
                    action()
                    if desc != "no_pause":
                        pause()
                except Exception as e:
                    print(f"\nОшибка: {e}")
                    pause()