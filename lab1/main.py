from Converting.BCDOperator import BCDOperator
from Converting.BinaryOperator import BinaryOperator
from Converting.FloatOperator import FloatOperator
from Operations.Addition import Addition
from Operations.NotAddition import NotAddition
from Operations.Divider import Divider
from Operations.Multiplicator import Multiplicator


def print_header(title):
    """Вывод заголовка раздела"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_separator():
    """Вывод разделителя"""
    print("-" * 70)

def pause():
    """Ожидание нажатия Enter"""
    input("\n[Нажмите Enter для продолжения...]")

def menu_codes(converter, operator):
    """Меню: Представление чисел в различных кодах"""
    while True:
        print_header("ПРЕДСТАВЛЕНИЕ ЧИСЕЛ В КОДАХ")
        print("1. Показать коды одного числа")
        print("2. Сравнить коды двух чисел")
        print("3. Конвертер: десятичное ↔ двоичное")
        print("0. Назад")
        print_separator()
        
        choice = input("Выбор: ").strip()
        
        if choice == "1":
            try:
                num = int(input("Введите число: "))
                print(f"\nЧисло: {num}")
                print(f"Прямой код:   {converter.array_to_string(operator.get_direct_code(num))}")
                print(f"Обратный код: {converter.array_to_string(operator.get_inverse_code(num))}")
                print(f"Доп. код:     {converter.array_to_string(operator.get_complement_code(num))}")
                pause()
            except ValueError:
                print(" Ошибка: введите целое число!")
                pause()
                
        elif choice == "2":
            try:
                num1 = int(input("Число A: "))
                num2 = int(input("Число B: "))
                print(f"Число A = {num1}")
                print(f"  Прямой:   {converter.array_to_string(operator.get_direct_code(num1))}")
                print(f"  Обратный: {converter.array_to_string(operator.get_inverse_code(num1))}")
                print(f"  Доп.:     {converter.array_to_string(operator.get_complement_code(num1))}")
                print(f"\nЧисло B = {num2}")
                print(f"  Прямой:   {converter.array_to_string(operator.get_direct_code(num2))}")
                print(f"  Обратный: {converter.array_to_string(operator.get_inverse_code(num2))}")
                print(f"  Доп.:     {converter.array_to_string(operator.get_complement_code(num2))}")
                pause()
            except ValueError:
                print("Ошибка: введите целые числа!")
                pause()
                
        elif choice == "3":
            try:
                print("\n1. Десятичное → Двоичное")
                print("2. Двоичное → Десятичное")
                sub = input("Выбор: ").strip()
                
                if sub == "1":
                    num = int(input("Десятичное число: "))
                    print(f"Прямой код:   {converter.array_to_string(operator.get_direct_code(num))}")
                    print(f"Доп. код:     {converter.array_to_string(operator.get_complement_code(num))}")
                elif sub == "2":
                    binary = input("Двоичная строка (32 бита): ").strip()
                    if len(binary) != 32 or not all(c in '01' for c in binary):
                        print("Ошибка: введите ровно 32 бита (0 и 1)!")
                    else:
                        arr = converter.string_to_array(binary)
                        dec = operator.array_to_decimal(arr, signed=True)
                        print(f"Десятичное значение: {dec}")
                pause()
            except ValueError:
                print("Ошибка ввода!")
                pause()
                
        elif choice == "0":
            break
        else:
            print("Неверный выбор!")

def menu_fixed_point():
    """Меню: Арифметика в фиксированной точке"""
    while True:
        print_header("АРИФМЕТИКА В ФИКСИРОВАННОЙ ТОЧКЕ")
        print("1. Сложение в дополнительном коде")
        print("2. Вычитание в дополнительном коде")
        print("3. Умножение в прямом коде (32 бита)")
        print("4. Деление в прямом коде (фикс. точка 32 бита)")
        print("0. Назад")
        print_separator()
        
        choice = input("Выбор: ").strip()
        
        if choice == "1":
            try:
                a = int(input("Число A: "))
                b = int(input("Число B: "))
                add = Addition(a, b)
                add.add_complement()
                pause()
            except ValueError:
                print(" Ошибка: введите целые числа!")
                pause()
                
        elif choice == "2":
            try:
                a = int(input("Уменьшаемое: "))
                b = int(input("Вычитаемое: "))
                sub = NotAddition(a, b)
                sub.subtract_complement()
                pause()
            except ValueError:
                print(" Ошибка: введите целые числа!")
                pause()
                
        elif choice == "3":
            try:
                a = int(input("Множимое: "))
                b = int(input("Множитель: "))
                mul = Multiplicator(a, b)
                mul.multiply_direct()
                pause()
            except ValueError:
                print("Ошибка: введите целые числа!")
                pause()
                
        elif choice == "4":
            try:
                a = int(input("Делимое: "))
                b = int(input("Делитель: "))
                div = Divider(a, b)
                div.divide_direct()
                pause()
            except ValueError:
                print("Ошибка: введите целые числа!")
                pause()
            except ZeroDivisionError:
                print("Ошибка: деление на ноль!")
                pause()
                
        elif choice == "0":
            break
        else:
            print("Неверный выбор!")


def menu_ieee754(converter, float_operator):
    """Меню: Операции с плавающей точкой (IEEE-754)"""
    while True:
        print_header("IEEE-754: ПЛАВАЮЩАЯ ТОЧКА (32 БИТА)")
        print("1. Конвертация: десятичное ↔ IEEE-754")
        print("2. Сложение")
        print("3. Вычитание")
        print("4. Умножение")
        print("5. Деление")
        print("0. Назад")
        print_separator()
        
        choice = input("Выбор: ").strip()
        
        if choice == "1":
            try:
                print("\n1. Decimal → IEEE-754")
                print("2. IEEE-754 → Decimal")
                sub = input("Выбор: ").strip()
                
                if sub == "1":
                    num = float(input("Число: "))
                    bits = float_operator.float_to_ieee754(num)
                    print(f"\nIEEE-754 (bin): {converter.array_to_string(bits)}")
                    # Детализация
                    sign, exp, mant = float_operator.ieee754_bits_to_parts(bits)
                    print(f"Знак: {sign}, Порядок: {exp} (реальный: {exp-127})")
                    print(f"Мантисса: {converter.array_to_string(mant)}")
                elif sub == "2":
                    binary = input("32 бита IEEE-754: ").strip()
                    if len(binary) != 32 or not all(c in '01' for c in binary):
                        print(" Ошибка: введите ровно 32 бита!")
                    else:
                        arr = converter.string_to_array(binary)
                        result = float_operator.ieee754_to_float(arr)
                        print(f"Десятичное значение: {result}")
                pause()
            except ValueError:
                print(" Ошибка ввода!")
                pause()
                
        elif choice in ["2", "3", "4", "5"]:
            try:
                a = float(input("Число A: "))
                b = float(input("Число B: "))
                
                if choice == "2":
                    add = Addition(a, b)
                    add.ieee754_add()
                elif choice == "3":
                    sub = NotAddition(a, b)
                    sub.ieee754_sub()
                elif choice == "4":
                    mul = Multiplicator(a, b)
                    mul.ieee754_mul()
                elif choice == "5":
                    div = Divider(a, b)
                    div.ieee754_div()
                pause()
            except ValueError:
                print("Ошибка: введите числа!")
                pause()
            except ZeroDivisionError:
                print("Ошибка: деление на ноль!")
                pause()
                
        elif choice == "0":
            break
        else:
            print(" Неверный выбор!")


def menu_bcd(converter, bcd_operator):
    """Меню: Двоично-десятичные коды"""
    
    while True:
        print_header("BCD КОД")
        print("1. Перевод в BCD код")
        print("2. Сложение в 8421 BCD")
        print("0. Назад")
        print_separator()
        
        choice = input("Выбор: ").strip()
        
        if choice == "1":
            try:
                print("\n1. Decimal → BCD")
                print("2. BCD → Decimal")
                sub = input("Выбор: ").strip()
                if sub == "1":
                    num = int(input("Введите число: "))
                    print(f"\n BCD для числа {num}:")
                    bcd_arr = bcd_operator.decimal_to_bcd_8421(num)
                    print(f"BCD код: {converter.array_to_string(bcd_arr)}")
                
                if sub == "2":
                    bcd = input("Введите код BCD: ").strip()
                    arr = converter.string_to_array(bcd)
                    decoded = bcd_operator.bcd_8421_to_decimal(arr)
                    print(f"Проверка (dec): {decoded}")
                pause()
            except ValueError:
                print(" Ошибка: введите целое число!")
                pause()
                
        elif choice == "2":
            try:
                a = int(input("Число A: "))
                b = int(input("Число B: "))
                add = Addition(a, b)
                add.bcd_add()
                pause()
            except ValueError:
                print(" Ошибка: введите целые числа!")
                pause()
                
        elif choice == "0":
            break
        else:
            print(" Неверный выбор!")

def main_menu():
    """Главное меню программы"""
    operator = BinaryOperator()
    float_operator = FloatOperator()
    bcd_operator = BCDOperator()
    # Установка разрядности
    global BIT_WIDTH, IEEE_BITS, BCD_BITS
    BIT_WIDTH = IEEE_BITS = BCD_BITS = 32
    
    while True:
        print_header("ПРОГРАММА КОМПЬЮТЕРНОЙ АРИФМЕТИКИ")
        print("  Разрядность: 32 бита")
        print_separator()
        print("1. Коды чисел (прямой/обратный/дополнительный)")
        print("2. Арифметика фиксированной точки")
        print("3. IEEE-754: плавающая точка")
        print("4. BCD код 8421")

        print("0. Выход")
        print_separator()
        
        choice = input("Выберите раздел: ").strip()
        
        if choice == "1":
            menu_codes(operator.converter, operator)
        elif choice == "2":
            menu_fixed_point()
        elif choice == "3":
            menu_ieee754(float_operator.converter, float_operator)
        elif choice == "4":
            menu_bcd(bcd_operator.converter, bcd_operator)
        elif choice == "0":
            break
        else:
            print(" Неверный выбор! Попробуйте снова.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        pause()