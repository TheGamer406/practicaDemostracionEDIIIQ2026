import pytest

from app.logica import (
    COMBINACIONES,
    contar_operaciones,
    evaluar_acceso_legacy,
    evaluar_acceso_optimizado,
    probar_equivalencia,
    tabla_comparacion,
    tabla_verdad_legacy,
)
from app.demostracion import PASOS, verificar_pasos


def test_tabla_verdad_tiene_8_filas():
    assert len(tabla_verdad_legacy()) == 8


def test_legacy_verdadero_solo_en_011_101_111():
    verdaderas = {(f["A"], f["B"], f["C"]) for f in tabla_verdad_legacy() if f["legacy"]}
    assert verdaderas == {(False, True, True), (True, True, True), (True, False, True)}


def test_equivalencia_en_las_8_combinaciones():
    for A, B, C in COMBINACIONES:
        assert bool(evaluar_acceso_legacy(A, B, C)) == bool(evaluar_acceso_optimizado(A, B, C))


def test_probar_equivalencia_no_lanza():
    assert probar_equivalencia() is True


def test_tabla_comparacion_todas_coinciden():
    assert all(f["coincide"] for f in tabla_comparacion())


def test_conteo_operaciones_legacy_y_optimizado():
    assert contar_operaciones(evaluar_acceso_legacy) == 10
    assert contar_operaciones(evaluar_acceso_optimizado) == 2


def test_todos_los_pasos_de_la_demostracion_son_equivalentes():
    resultados = verificar_pasos(PASOS)
    assert len(resultados) == len(PASOS)
    assert all(r["igual_a_original"] for r in resultados)


def test_paso_final_coincide_con_optimizado():
    for A, B, C in COMBINACIONES:
        assert PASOS[-1]["fn"](A, B, C) == evaluar_acceso_optimizado(A, B, C)


def test_un_paso_adulterado_se_detecta_como_invalido():
    paso_roto = dict(PASOS[-1])
    paso_roto["fn"] = lambda A, B, C: not PASOS[-1]["fn"](A, B, C)
    resultados = verificar_pasos([paso_roto])
    assert resultados[0]["igual_a_original"] is False
