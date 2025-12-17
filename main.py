
import re
from app.parser import validate_expression, normalize_expr
from app.derivative import compute_derivative
from sympy import sstr


# Приведение к стандартному виду
def format_expression(expr):
    s = sstr(expr)
    s = s.replace('**', '^')  # степени
    s = re.sub(r'(?<=\d)\*(?=[a-zA-Z(])', '', s)        # 2*x = 2x
    s = re.sub(r'(?<=[a-zA-Z)])\*(?=[a-zA-Z(])', '', s)  # x*sin(x) = xsin(x)
    return s


# Извлечение переменных x и y из выражения
def extract_variables(expr: str):
    norm = normalize_expr(expr)
    return sorted(set(re.findall(r'\b[xy]\b', norm)))


# ввод / вывод
def main():
    inp = input("Введите функцию f(x, y) или help: ").strip()

    if inp.lower() == "help":
        print("""
Инструкция по вводу функции:

- Поддерживаются переменные: x и y
- Допустимы: степени (x^2), скобки, тригонометрия (sinx, cosx), логарифмы (lnx)
- Можно вводить:
    ▪ sinx, siny
    ▪ sin2x, sin2y
    ▪ x^2 + y^2
    ▪ x(x+1)
- Производная будет вычислена по всем переменным, найденным в выражении.
Чтобы выйти, нажмите Ctrl+C
""")
        return

    expr, err = validate_expression(inp)
    if err is not None:
        bad = inp[err] if 0 <= err < len(inp) else ''
        print(f"Ошибка в выражении на позиции {err}: '{bad}'")
        return

    variables = extract_variables(inp)

    try:
        result = compute_derivative(expr, variables)
        print(
            f"Производная:",
            f" d(f)/d({', '.join(variables)}) = {format_expression(result)}"
        )
    except Exception as e:
        print("Ошибка при вычислении производной:", e)


if __name__ == "__main__":
    main()
