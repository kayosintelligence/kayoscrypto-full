#!/usr/bin/env python3
"""Verificador CSP: todas as projeções 2D devem ser SATOR com UMA orientação global.

Este script modela a hipercubo 6D com eixos 0..5, índices 0..4 por eixo.
Para cada projeção (par de eixos) consideramos a fatia onde os outros eixos
estão fixos no centro (2). Cada fatia 5x5 deve ser igual ao quadrado SATOR canônico
após aplicar a MESMA transformação simetria (rot/flip) global.

Uso: execute com `PYTHONPATH=src .venv/bin/python src/hyper_sator/hyper_sator_csp_global_orientation.py`
"""

from z3 import Solver, Int, Or, And, sat
import sys

# Canonical SATOR 5x5 matrix (letters)
SATOR = [
    list("SATOR"),
    list("AREPO"),
    list("TENET"),
    list("OPERA"),
    list("ROTAS"),
]

def char_code(c):
    return ord(c)

def apply_transform_idx(t, r, c):
    # t in 0..7: rotations 0,90,180,270 and their horizontal reflection variants
    if t < 4:
        rot = t
        flip = False
    else:
        rot = t - 4
        flip = True

    # rotate (r,c)
    if rot == 0:
        r2, c2 = r, c
    elif rot == 1:
        r2, c2 = c, 4 - r
    elif rot == 2:
        r2, c2 = 4 - r, 4 - c
    else:
        r2, c2 = 4 - c, r

    # flip horizontally if requested
    if flip:
        c2 = 4 - c2

    return r2, c2


def main():
    # Build variable map only for coordinates used by projections: for each pair (i,j)
    # other axes fixed at 2. This keeps problem small (~15*25 vars max, with overlap).
    pairs = []
    for i in range(6):
        for j in range(i + 1, 6):
            pairs.append((i, j))

    vars_map = {}
    def var_for(coord):
        key = tuple(coord)
        if key not in vars_map:
            vars_map[key] = Int(f"x_{'_'.join(map(str,key))}")
        return vars_map[key]

    s = Solver()

    # create a single orientation variable t in 0..7
    t = Int('orientation_t')
    s.add(And(t >= 0, t <= 7))

    # For each projection pair, for r,c in 0..4, map to coords with other axes=2
    for (a, b) in pairs:
        for r in range(5):
            for c in range(5):
                coord = [2] * 6
                coord[a] = r
                coord[b] = c
                v = var_for(coord)
                # restrict domain to ASCII letters used in SATOR (A..Z)
                s.add(And(v >= ord('A'), v <= ord('Z')))
                # map through transform t
                # We must express v == SATOR[tr][tc] where tr,tc depends on t
                # Build disjunction over 8 possibilities
                disj = []
                for tv in range(8):
                    tr, tc = apply_transform_idx(tv, r, c)
                    target = char_code(SATOR[tr][tc])
                    disj.append(And(t == tv, v == target))
                s.add(Or(*disj))

    print("Solving CSP (global orientation). Variables:", len(vars_map))
    res = s.check()
    print("Result:", res)
    if res == sat:
        m = s.model()
        chosen = m[t].as_long()
        print(f"Satisfiable with global orientation t={chosen}")
        # print one projection (axes 0,1) as example
        print("Example projection (axes 0,1) as 5x5 letters:")
        for r in range(5):
            line = []
            for c in range(5):
                coord = [2]*6
                coord[0] = r
                coord[1] = c
                v = vars_map[tuple(coord)]
                val = m[v].as_long()
                line.append(chr(val))
            print(''.join(line))
    else:
        print("UNSAT: não é possível satisfazer todas as projeções 2D como SATOR com UMA orientação global.")


def solve_global_orientation():
    """Resolve o CSP e retorna um mapping do modelo e as projeções 5x5.

    Retorna (model_map, projections, orientation_t)
    - model_map: dict mapping coord tuple string 'x_0_0_2_2_2_2' -> letter
    - projections: dict mapping axes pair tuple -> 5x5 list of letters
    - orientation_t: int 0..7
    """
    # Rebuild the same problem (to keep function self-contained)
    pairs = []
    for i in range(6):
        for j in range(i + 1, 6):
            pairs.append((i, j))

    vars_map = {}
    def var_for(coord):
        key = tuple(coord)
        if key not in vars_map:
            vars_map[key] = Int(f"x_{'_'.join(map(str,key))}")
        return vars_map[key]

    s = Solver()
    t = Int('orientation_t')
    s.add(And(t >= 0, t <= 7))

    for (a, b) in pairs:
        for r in range(5):
            for c in range(5):
                coord = [2] * 6
                coord[a] = r
                coord[b] = c
                v = var_for(coord)
                s.add(And(v >= ord('A'), v <= ord('Z')))
                disj = []
                for tv in range(8):
                    tr, tc = apply_transform_idx(tv, r, c)
                    target = char_code(SATOR[tr][tc])
                    disj.append(And(t == tv, v == target))
                s.add(Or(*disj))

    res = s.check()
    if res != sat:
        return None, None, None

    m = s.model()
    orientation = m[t].as_long()
    # build model_map
    model_map = {}
    projections = {}
    for (a, b) in pairs:
        proj = [[None]*5 for _ in range(5)]
        for r in range(5):
            for c in range(5):
                coord = [2]*6
                coord[a] = r
                coord[b] = c
                v = vars_map[tuple(coord)]
                val = m[v].as_long()
                ch = chr(val)
                model_map[f"x_{'_'.join(map(str,coord))}"] = ch
                proj[r][c] = ch
        projections[(a,b)] = proj

    return model_map, projections, orientation


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Erro:', e)
        sys.exit(2)
