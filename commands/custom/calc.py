from cprint import *

__desc__ = "Calculate things"
__long_desc__ = """[R]calc[P]

A way to do simple mathemetical equations on the command line"""


def main(*equation:str):
    "Calculate things"
    __help__ = "[B]Equation[G] any simple equation"

    equation = ''.join(equation)
    out = eval(equation)
    cprint(f"[Y] {equation}[G] = [L]{out}")