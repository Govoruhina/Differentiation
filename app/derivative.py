from sympy import symbols, diff, sympify, E, log, exp, simplify
from .parser import FUNC_MAP

x, y = symbols('x y')


# приведение к стандартному виду
def _powE_to_exp(expr):  # E**x -> exp(x)
    return expr.replace(
        lambda t: t.is_Pow and t.base == E,
        lambda t: exp(t.exp)
    )


def _powE_to_exp(expr):
    return expr.replace(
        lambda t: t.is_Pow and t.base == E,
        lambda t: exp(t.exp)
    )


# вычисление производной
def compute_derivative(expr_str: str, variables):
    """
    variables: список строк, например ['x'] или ['x','y'].
    Для каждого var берём diff, а потом суммируем частичные.
    """
    expr = sympify(expr_str, locals={**FUNC_MAP, 'x': x, 'y': y, 'e': E})

    # символы, по которым дифференцировать
    sym_vars = []
    for v in variables:
        if v == 'x':
            sym_vars.append(x)
        elif v == 'y':
            sym_vars.append(y)
        else:
            raise ValueError(f"Неподдерживаемая переменная '{v}'")

    # считает частные производные и их сумму
    total = 0
    for var in sym_vars:
        d = diff(expr, var)
        d = d.subs(log(E), 1)
        d = _powE_to_exp(d)
        total += d

    return simplify(total)
