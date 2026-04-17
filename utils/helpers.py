
import sys



def pause() -> None:
    """Ожидает нажатия Enter"""
    input("\nНажмите Enter для продолжения...")


def get_valid_input(prompt: str,
                    validator: callable,
                    error_msg: str = "Неверный ввод") -> any:
    while True:
        try:
            value = input(prompt).strip()
            if validator(value):
                return value
            print(error_msg)
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана.")
            sys.exit(0)
        except Exception:
            print(error_msg)