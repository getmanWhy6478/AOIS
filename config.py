"""Константы и настройки программы"""

# Поддерживаемые переменные
SUPPORTED_VARS = ['a', 'b', 'c', 'd', 'e']
MAX_VARS = len(SUPPORTED_VARS)

# Приоритет операций (от высокого к низкому)
OPERATOR_PRIORITY = {
    'parentheses': 5,  # ()
    'not': 4,          # !
    'and': 3,          # &
    'or': 2,           # |
    'impl': 1,         # ->
    'equiv': 1         # ~
}

# Символы операций
OPERATORS = {
    'not': '!',
    'and': '&',
    'or': '|',
    'impl': '->',
    'equiv': '~'
}

# Настройки вывода
OUTPUT_SETTINGS = {
    'show_truth_table': True,
    'show_derivatives': True,
    'show_minimization': True,
    'max_derivative_order': 4
}