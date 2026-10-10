"""Los pasos de la demostración algebraica, cada uno con su ley, su explicación y su función ejecutable."""
from app.logica import evaluar_acceso_legacy

PASOS = [
    {
        "n": 0,
        "expr": "(¬A ∧ B ∧ C) ∨ (A ∧ B ∧ C) ∨ (A ∧ ¬B ∧ C)",
        "ley": "Expresión original",
        "detalle": "Forma canónica (suma de productos) tomada directamente del código legacy.",
        "fn": lambda A, B, C: ((not A) and B and C) or (A and B and C) or (A and (not B) and C),
    },
    {
        "n": 1,
        "expr": "C ∧ [(¬A ∧ B) ∨ (A ∧ B) ∨ (A ∧ ¬B)]",
        "ley": "Conmutativa, asociativa y distributiva",
        "detalle": "C aparece en los tres términos; se factoriza: (x∧C)∨(y∧C)∨(z∧C) ≡ C∧(x∨y∨z).",
        "fn": lambda A, B, C: C and (((not A) and B) or (A and B) or (A and (not B))),
    },
    {
        "n": 2,
        "expr": "C ∧ [(B ∧ ¬A) ∨ (B ∧ A) ∨ (A ∧ ¬B)]",
        "ley": "Conmutativa",
        "detalle": "p∧q ≡ q∧p: se reordenan los operandos de los dos primeros términos para dejar B primero.",
        "fn": lambda A, B, C: C and ((B and (not A)) or (B and A) or (A and (not B))),
    },
    {
        "n": 3,
        "expr": "C ∧ [(B ∧ (¬A ∨ A)) ∨ (A ∧ ¬B)]",
        "ley": "Distributiva",
        "detalle": "p∧q ∨ p∧r ≡ p∧(q∨r): se factoriza B de los dos primeros términos.",
        "fn": lambda A, B, C: C and ((B and ((not A) or A)) or (A and (not B))),
    },
    {
        "n": 4,
        "expr": "C ∧ [(B ∧ T) ∨ (A ∧ ¬B)]",
        "ley": "Complemento",
        "detalle": "¬A ∨ A ≡ T: la disyunción de una proposición y su negación es siempre verdadera.",
        "fn": lambda A, B, C: C and ((B and True) or (A and (not B))),
    },
    {
        "n": 5,
        "expr": "C ∧ [B ∨ (A ∧ ¬B)]",
        "ley": "Identidad",
        "detalle": "B ∧ T ≡ B: conjuntar con la tautología T no cambia el valor de verdad.",
        "fn": lambda A, B, C: C and (B or (A and (not B))),
    },
    {
        "n": 6,
        "expr": "C ∧ [(B ∨ A) ∧ (B ∨ ¬B)]",
        "ley": "Distributiva",
        "detalle": "p ∨ (q∧r) ≡ (p∨q) ∧ (p∨r): se distribuye B sobre (A ∧ ¬B).",
        "fn": lambda A, B, C: C and ((B or A) and (B or (not B))),
    },
    {
        "n": 7,
        "expr": "C ∧ [(B ∨ A) ∧ T]",
        "ley": "Complemento",
        "detalle": "B ∨ ¬B ≡ T: la disyunción de una proposición y su negación es siempre verdadera.",
        "fn": lambda A, B, C: C and ((B or A) and True),
    },
    {
        "n": 8,
        "expr": "C ∧ (A ∨ B)",
        "ley": "Identidad y conmutativa",
        "detalle": "p ∧ T ≡ p, y B ∨ A ≡ A ∨ B: forma final, equivalente a evaluar_acceso_optimizado.",
        "fn": lambda A, B, C: C and (A or B),
    },
]


def verificar_pasos(pasos=None):
    """Para cada paso, evalúa fn en las 8 combinaciones y compara contra la función original."""
    from app.logica import COMBINACIONES

    pasos = pasos if pasos is not None else PASOS
    resultados = []
    for paso in pasos:
        columna = []
        for A, B, C in COMBINACIONES:
            columna.append(1 if paso["fn"](A, B, C) else 0)
        original = [1 if evaluar_acceso_legacy(A, B, C) else 0 for A, B, C in COMBINACIONES]
        resultados.append({
            "n": paso["n"],
            "expr": paso["expr"],
            "ley": paso["ley"],
            "detalle": paso["detalle"],
            "columna": columna,
            "igual_a_original": columna == original,
        })
    return resultados
