import pytest
from sympy import (
    symbols, sin, cos, tan, cot, sinh, cosh,
    tanh, coth, log, exp, sqrt, sympify
)
from app.parser import validate_expression
from main import extract_variables
from app.derivative import compute_derivative

x, y = symbols('x y')

# Локальные имена для sympify в однопеременных тестах
LOCAL = {
    'sin': sin,   'cos': cos,   'tan': tan,   'cot': cot,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh, 'coth': coth,
    'log': log,   'exp': exp,   'sqrt': sqrt,  'x': x
}


@pytest.mark.parametrize(
    "user_input, expected",
    [
        # базовые
        ("x^2",           "2*x"),
        ("sinx",          "cos(x)"),
        ("lnx",           "1/x"),
        ("cos2x",         "-2*sin(2*x)"),
        ("sqrtx",         "1/(2*sqrt(x))"),
        ("e^x",           "exp(x)"),
        ("shx",           "cosh(x)"),
        ("ctanx",         "-csc(x)**2"),

        # произведение
        ("sinx*cosx",     "-sin(x)**2 + cos(x)**2"),
        ("xsinx",         "sin(x) + x*cos(x)"),
        ("x(x+1)",        "2*x + 1"),
        ("(x-2)(x+2)",    "2*x"),

        # разность / сумма
        ("x^2 - lnx",     "2*x - 1/x"),
        ("sinx + chx",    "cos(x) + sinh(x)"),

        # c обратными функциями
        ("asinx",         "1/sqrt(1 - x**2)"),
        ("acosx",         "-1/sqrt(1 - x**2)"),
        ("atanx",         "1/(1 + x**2)"),
        ("acotx",         "-1/(1 + x**2)"),
        ("asinhx",        "1/sqrt(x**2 + 1)"),
        ("acoshx",        "1/(sqrt(x - 1)*sqrt(x + 1))"),
        ("atanhx",        "1/(-x**2 + 1)"),
        ("acothx",        "-1/(x**2 - 1)"),
    ]
)
def test_derivatives(user_input, expected):
    expr, err = validate_expression(user_input)
    assert err is None, f"Парсер ошибочно отметил ошибку в '{user_input}'"

    vars = extract_variables(user_input)
    got = compute_derivative(expr, vars).simplify()
    want = sympify(expected, locals=LOCAL)

    assert (got - want).simplify() == 0, \
        f"Для '{user_input}' получили {got}, ожидалось {want}"


@pytest.mark.parametrize("bad_input", ["2x+", "sin(", "x**", "cos)", "ln("])
def test_parser_errors(bad_input):
    _, err = validate_expression(bad_input)
    assert err is not None, f"Парсер не заметил ошибку в '{bad_input}'"


@pytest.mark.parametrize("expr, expected", [
    ("x^2 + y^2",          "2*x + 2*y"),
    ("x*y",                "x + y"),
    ("x^2*y + y^2*x",      "x**2 + y**2 + 4*x*y"),
    ("sinx + cosy",        "cos(x) - sin(y)"),
    ("ln(x*y)",            "1/x + 1/y"),
    ("e^(x+y)",            "exp(x + y) + exp(x + y)"),
])
def test_multivariable_derivatives(expr, expected):
    cleaned, err = validate_expression(expr)
    assert err is None, f"Ошибка в выражении '{expr}'"

    vars = extract_variables(expr)
    got = compute_derivative(cleaned, vars)
    want = sympify(
        expected.replace("^", "**"),
        locals={'x': x, 'y': y, 'exp': exp, 'log': log}
    )

    assert (got - want).simplify() == 0, \
        f"{expr} → получено {got}, ожидалось {want}"
