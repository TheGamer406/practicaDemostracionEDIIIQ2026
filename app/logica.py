"""Fuente única de verdad: legacy, optimizado, tabla de verdad, validación y conteo de operaciones."""
import ast
import inspect
from itertools import product

COMBINACIONES = list(product([False, True], repeat=3))


def evaluar_acceso_legacy(A, B, C):
    opcion_1 = (not A) and B and C
    opcion_2 = A and B and C
    opcion_3 = A and (not B) and C
    return opcion_1 or opcion_2 or opcion_3


def evaluar_acceso_optimizado(A, B, C):
    return C and (A or B)


def tabla_verdad_legacy():
    filas = []
    for i, (A, B, C) in enumerate(COMBINACIONES):
        opcion_1 = (not A) and B and C
        opcion_2 = A and B and C
        opcion_3 = A and (not B) and C
        filas.append({
            "i": i, "A": A, "B": B, "C": C,
            "opcion_1": opcion_1, "opcion_2": opcion_2, "opcion_3": opcion_3,
            "legacy": opcion_1 or opcion_2 or opcion_3,
        })
    return filas


def tabla_comparacion():
    filas = []
    for i, (A, B, C) in enumerate(COMBINACIONES):
        legacy = bool(evaluar_acceso_legacy(A, B, C))
        optimizado = bool(evaluar_acceso_optimizado(A, B, C))
        filas.append({
            "i": i, "A": A, "B": B, "C": C,
            "legacy": legacy, "optimizado": optimizado,
            "coincide": legacy == optimizado,
        })
    return filas


def probar_equivalencia():
    for fila in tabla_comparacion():
        assert fila["coincide"], (
            f"Diferencia en A={fila['A']}, B={fila['B']}, C={fila['C']}"
        )
    return True


def _contar_operaciones_logicas(nodo_ast):
    operaciones = 0
    for n in ast.walk(nodo_ast):
        if isinstance(n, ast.BoolOp):
            operaciones += len(n.values) - 1
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            operaciones += 1
    return operaciones


def contar_operaciones(func):
    arbol = ast.parse(inspect.getsource(func))
    return _contar_operaciones_logicas(arbol)


def codigo_fuente(func):
    return inspect.getsource(func)
