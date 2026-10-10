"""Versión de consola, sin dependencias externas. Pedida por la consigna (P1.1, P1.2, P1.3)."""
import ast
import inspect
from itertools import product


def evaluar_acceso_legacy(A, B, C):
    opcion_1 = (not A) and B and C
    opcion_2 = A and B and C
    opcion_3 = A and (not B) and C
    return opcion_1 or opcion_2 or opcion_3


def evaluar_acceso_optimizado(A, B, C):
    return C and (A or B)  # equivalente, demostrado paso a paso en la web


def tabla_verdad():
    print(f"{'A':<6}{'B':<6}{'C':<6}{'legacy':<8}{'optimizado'}")
    for A, B, C in product([False, True], repeat=3):
        print(f"{A!s:<6}{B!s:<6}{C!s:<6}"
              f"{bool(evaluar_acceso_legacy(A, B, C))!s:<8}"
              f"{bool(evaluar_acceso_optimizado(A, B, C))}")


def probar_equivalencia():
    for A, B, C in product([False, True], repeat=3):
        assert bool(evaluar_acceso_legacy(A, B, C)) == bool(evaluar_acceso_optimizado(A, B, C)), \
            f"Diferencia en A={A}, B={B}, C={C}"
    print("\n✔ Las 8 combinaciones coinciden: funciones equivalentes.")


def contar_operaciones(func):
    operaciones = 0
    for n in ast.walk(ast.parse(inspect.getsource(func))):
        if isinstance(n, ast.BoolOp):
            operaciones += len(n.values) - 1
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            operaciones += 1
    return operaciones


def mostrar_conteo_operaciones():
    legacy = contar_operaciones(evaluar_acceso_legacy)
    optimizado = contar_operaciones(evaluar_acceso_optimizado)
    print(f"\nOperaciones lógicas — legacy: {legacy}, optimizado: {optimizado} "
          f"(reducción: {round((1 - optimizado / legacy) * 100, 1)}%)")


if __name__ == "__main__":
    tabla_verdad()
    probar_equivalencia()
    mostrar_conteo_operaciones()
