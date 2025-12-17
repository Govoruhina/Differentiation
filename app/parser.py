import re
from sympy import (
    symbols, sin, cos, tan, cot, asin, acos, atan, acot,
    sinh, cosh, tanh, coth, asinh, acosh, atanh, acoth,
    log, exp, E, sqrt, sympify
)

x, y = symbols('x y')
ALLOWED_VARS = {'x', 'y', 'e'}

# функции, которые поддерживаются
FUNC_MAP = {
    'sin': sin, 'cos': cos, 'tan': tan, 'cot': cot,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh, 'coth': coth,
    'asin': asin, 'acos': acos, 'atan': atan, 'acot': acot,
    'asinh': asinh, 'acosh': acosh, 'atanh': atanh, 'acoth': acoth,
    'log': log, 'exp': exp, 'sqrt': sqrt,
}

# перевод в поддерживаемые функции
ALIASES = {
    'ln': 'log', 'ctan': 'cot', 'ctg': 'cot', 'tg': 'tan',
    'sh': 'sinh', 'ch': 'cosh', 'th': 'tanh', 'cth': 'coth',
    'arccos': 'acos', 'arcsin': 'asin', 'arctan': 'atan',
    'arccot': 'acot', 'arctg': 'atan', 'arccotg': 'acot',
    'arcsinh': 'asinh', 'arccosh': 'acosh', 'arctanh': 'atanh',
    'arccoth': 'acoth', 'arcth': 'atanh', 'arccth': 'acoth', 'e': 'exp'
}


# замена в поддерживаемые функции
def _apply_aliases(expr: str) -> str:
    expr = expr.lower().replace('^', '**')
    for k, v in ALIASES.items():
        expr = re.sub(rf'\b{k}(?=[a-z0-9(])', v, expr)
    return expr


# приведение к стандартному виду
def _parenthesise(expr: str) -> str:
    """
    sinx -> sin(x), sin2x -> sin(2*x),
    sinx**3 -> sin(x)**3, sin2*x -> sin(2*x)
    """
    for f in FUNC_MAP:
        # sin2x / sin2y → sin(2*x) / sin(2*y)
        expr = re.sub(rf'\b{f}(\d+)\*?([xy])\b', rf'{f}(\1*\2)', expr)
        # sinx / siny → sin(x) / sin(y)
        expr = re.sub(rf'\b{f}\*?([xy])\b', rf'{f}(\1)', expr)
        # sinx**3 / siny**3 → sin(x)**3 / sin(y)**3
        expr = re.sub(rf'\b{f}\*?([xy])\*\*(\d+)', rf'{f}(\1)**\2', expr)
    return expr


# вставка * между числами и переменными
def _insert_mul(expr: str) -> str:
    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)   # 2x -> 2*x
    expr = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', expr)  # x2 -> x*2
    expr = re.sub(r'([x\)])(?=[a-z])', r'\1*', expr)    # xsin -> x*sin
    expr = re.sub(r'([x\)])\(', r'\1*(', expr)          # x(  -> x*(
    return expr


# подготовка
def normalize_expr(expr: str) -> str:
    expr = _apply_aliases(expr)
    expr = _parenthesise(expr)    # 1-й проход: sinx, cos2x
    expr = _insert_mul(expr)      # вставляем *
    expr = _parenthesise(expr)    # 2-й проход:   x*sinx  -> x*sin(x)
    return expr


# проверка корректности выражения
def validate_expression(expr: str) -> tuple[str, int | None]:
    # удаляет пробелы и запоминает соответствие индексов
    pos_map = [i for i, c in enumerate(expr) if c != ' ']
    raw = expr.replace(' ', '')
    cleaned = normalize_expr(raw)

    # доп проверка на наличие ошибок
    stack = []
    prev = ''
    for i, ch in enumerate(cleaned):
        # скобоки
        if ch == '(':
            stack.append(i)
        elif ch == ')':
            if not stack:
                return expr, i
            stack.pop()

        # двойные операторы
        if prev in '+-*/^' and ch in '+-*/^':
            if not (prev == '*' and ch == '*'):
                return expr, pos_map[i - 1]

        #  знак =
        if ch == '=':
            return expr, i

        prev = ch

    # незакрытые скобки
    if stack:
        return expr, stack[-1]

    for m in re.finditer(r'[A-Za-z]+', cleaned):
        w = m.group().lower()
        # разрешены только x, e, и функции из словарей
        if w not in ALLOWED_VARS and w not in FUNC_MAP and w not in ALIASES:
            return expr, pos_map[m.start()]

    # проверка через sympy
    try:
        sympify(cleaned, locals={**FUNC_MAP, 'x': x, 'e': E})
        return cleaned, None
    except Exception as err:
        m = re.search(r'at position (\d+)', str(err))
        return expr, pos_map[int(m.group(1))] if m else -1
