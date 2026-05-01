from hash_table import HashTable

def show_menu() -> None:
    print("МЕНЮ ХЕШ-ТАБЛИЦЫ")
    print("1.Вставить запись")
    print("2.Найти запись по ключу")
    print("3.Обновить запись")
    print("4.Удалить запись")
    print("5.Показать таблицу")
    print("0.Выход")

def main() -> None:
    size = 20

    ht = HashTable(size=size, base_offset=0)
    lit_to_add = [
    ( "Герой нашего времени","Лермонтов"),
    ("Война и мир", "Толстой"),
    ("Анна Каренина", "Толстой"),
    ("Реквием", "Ахматова"),
    ("Исповедь хулигана", "Есенин"),
    ("Капитанская дочка", "Пушкин"),
    ("Двенадцать", "Блок"),
    ("Преступление и наказание", "Достоевский"),
    ("Отцы и дети","Тургенев"),
    ("Дон Кихот", "Сервантес"),
    ("Евгений Онегин", "Пушкин"),
    ("Мастер и Маргарита", "Булгаков"),
    ("Собачье сердце", "Булгаков"),
    ("Мертвые души", "Гоголь"),
    ("Гроза", "Островский"),
    ("Вишневый сад", "Чехов"),
    ("Пиковая дама", "Пушкин")
]

    for name, info in lit_to_add:
        ht.insert(name, info)
    while True:
        show_menu()
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            key = input("Введите ключ (фамилия, мин. 2 рус. буквы): ").strip()
            if not key:
                print("Ключ не может быть пустым.")
            else:
                value = input("Введите значение: ").strip()
                try:
                    if ht.insert(key, value):
                        print("Запись успешно добавлена!")
                    else:
                        print("Ошибка добавления (возможно, ключ уже существует).")
                except Exception as e:
                    print(f"Ошибка хеширования: {e}")

        elif choice == '2':
            key = input("Введите ключ для поиска: ").strip()
            result = ht.get(key)
            if result is not None:
                print(f"Найдено: [{key}] → {result}")
            else:
                print(f"Запись с ключом '{key}' не найдена.")

        elif choice == '3':
            key = input("Введите ключ для обновления: ").strip()
            new_val = input("Введите новое значение: ").strip()
            if ht.update(key, new_val):
                print("Запись успешно обновлена!")
            else:
                print("Ключ не найден. Обновление невозможно.")

        elif choice == '4':
            key = input("Введите ключ для удаления: ").strip()
            if ht.delete(key):
                print("Запись успешно удалена!")
            else:
                print("Ключ не найден в таблице.")

        elif choice == '5':
            ht.display()

        elif choice == '0':
            print("\nЗавершение работы. Спасибо за использование!")
            break
        else:
            print("Неверный выбор. Введите число от 0 до 5.")

if __name__ == "__main__":
    main()