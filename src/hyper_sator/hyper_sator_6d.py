"""Kayos Hyper-SATOR 6D - Prova de Conceito

Este módulo fornece uma implementação simples (POC) do hipercubo SATOR em 6D.
Para manter o PoC leve e verificável, algumas escolhas pragmáticas foram feitas:
- enchemos o hipercubo de modo que três pares ortogonais de eixos (0,1), (2,3),
  (4,5) contenham projeções 5x5 correspondentes ao quadrado SATOR clássico.
- o centro absoluto (índice 3 em 1..5, ou 0-based 2) é definido como 'N'.

O objetivo é demonstrar extração de diagonais, anti-diagonais e checagem
palindrômica em projeções 2D selecionadas.
"""

from typing import List, Tuple

SATOR_MATRIX = [
    list("SATOR"),
    list("AREPO"),
    list("TENET"),
    list("OPERA"),
    list("ROTAS"),
]

ALPHABET = ['S', 'A', 'T', 'O', 'R']


class KayosHyperSator6D:
    """Hipercubo SATOR 6D (POC).

    Observações de implementação (POC):
    - O hipercubo é representado por uma estrutura de listas aninhadas
      acessível via tuple de índices 0..4 em cada dimensão.
    - Para garantir projeções 2D SATOR em faces selecionadas, preenchemos
      o hipercubo usando SATOR_MATRIX nas combinações de eixos (0,1), (2,3),
      (4,5) mantendo independência nas dimensões restantes.
    - O centro absoluto (2,2,2,2,2,2) contém 'N'.
    """

    def __init__(self, side: int = 5, dimensions: int = 6):
        assert side == 5 and dimensions == 6, "POC assume lado 5 e 6 dimensões"
        self.side = side
        self.dimensions = dimensions
        # lazy-populated hypercube
        self.hypercube = None

    def generate_hypercube(self):
        """Constroi e armazena o hipercubo 6D.

        Strategy (POC): para cada célula, definimos o valor baseado em três
        projeções ortogonais:
        - valor0_1: SATOR_MATRIX[i0][i1]
        - valor2_3: SATOR_MATRIX[i2][i3]
        - valor4_5: SATOR_MATRIX[i4][i5]

        Combinamos essas três influências (valor0_1/valor2_3/valor4_5) em uma
        escolha determinística: se uma das projeções aponta para o centro
        (posição 2 nas duas coordenadas), priorizamos 'N'; caso contrário,
        selecionamos o primeiro valor não-centro na ordem (0,1)->(2,3)->(4,5).
        """

        # build nested lists: 6 levels
        S = self.side

        def cell_value(idx: Tuple[int, int, int, int, int, int]) -> str:
            # center check (all axes == 2 -> human coord 3)
            if all(i == 2 for i in idx):
                return 'N'

            v01 = SATOR_MATRIX[idx[0]][idx[1]]
            v23 = SATOR_MATRIX[idx[2]][idx[3]]
            v45 = SATOR_MATRIX[idx[4]][idx[5]]

            # if any local projection points at center cell of corresponding SATOR
            if (idx[0] == 2 and idx[1] == 2) or (idx[2] == 2 and idx[3] == 2) or (idx[4] == 2 and idx[5] == 2):
                return 'N'

            # deterministically prefer v01, then v23, then v45
            for v in (v01, v23, v45):
                if v != 'N':
                    return v
            return 'S'  # fallback

        # create nested lists
        self.hypercube = [[[[[[None for _ in range(S)] for _ in range(S)]
                             for _ in range(S)] for _ in range(S)] for _ in range(S)] for _ in range(S)]

        for i0 in range(S):
            for i1 in range(S):
                for i2 in range(S):
                    for i3 in range(S):
                        for i4 in range(S):
                            for i5 in range(S):
                                val = cell_value((i0, i1, i2, i3, i4, i5))
                                self.hypercube[i0][i1][i2][i3][i4][i5] = val

        return self.hypercube

    def _get(self, idx: Tuple[int, int, int, int, int, int]) -> str:
        if self.hypercube is None:
            raise RuntimeError("Hypercube não gerado: chamar generate_hypercube() primeiro")
        return self.hypercube[idx[0]][idx[1]][idx[2]][idx[3]][idx[4]][idx[5]]

    def extract_diagonal_principal(self) -> List[str]:
        """Extrai diagonal (i,i,i,i,i,i) para i=0..4 e devolve lista de letras."""
        if self.hypercube is None:
            self.generate_hypercube()
        return [self._get((i, i, i, i, i, i)) for i in range(self.side)]

    def extract_anti_diagonal(self) -> List[str]:
        if self.hypercube is None:
            self.generate_hypercube()
        S = self.side
        return [self._get((i, S - 1 - i, S - 1 - i, S - 1 - i, S - 1 - i, S - 1 - i)) for i in range(self.side)]

    def project_2d(self, axis_x: int, axis_y: int, fixed_indices: Tuple[int, ...] = None) -> List[List[str]]:
        """Projeta uma fatia 5x5 sobre os eixos axis_x e axis_y.

        Os demais eixos são fixados em `fixed_indices` (tupla com 4 valores) ou
        no centro (2) por padrão.
        """
        if self.hypercube is None:
            self.generate_hypercube()
        if fixed_indices is None:
            fixed = [2, 2, 2, 2]
        else:
            assert len(fixed_indices) == 4
            fixed = list(fixed_indices)

        # map remaining axes in order
        axes = [0, 1, 2, 3, 4, 5]
        remaining = [a for a in axes if a not in (axis_x, axis_y)]

        S = self.side
        grid = [[None for _ in range(S)] for _ in range(S)]
        for i in range(S):
            for j in range(S):
                coords = [None] * 6
                coords[axis_x] = i
                coords[axis_y] = j
                for k, ax in enumerate(remaining):
                    coords[ax] = fixed[k]
                grid[i][j] = self._get(tuple(coords))
        return grid

    @staticmethod
    def is_row_palindrome(row: List[str]) -> bool:
        return row == list(reversed(row))

    def verify_projection_palindromic(self, axis_x: int, axis_y: int, fixed_indices: Tuple[int, ...] = None) -> bool:
        grid = self.project_2d(axis_x, axis_y, fixed_indices=fixed_indices)
        S = self.side
        # check rows and columns
        for r in range(S):
            if not self.is_row_palindrome(grid[r]):
                return False
        # check columns
        for c in range(S):
            col = [grid[r][c] for r in range(S)]
            if not self.is_row_palindrome(col):
                return False
        # check main diagonal and anti-diagonal
        main = [grid[i][i] for i in range(S)]
        anti = [grid[i][S - 1 - i] for i in range(S)]
        return self.is_row_palindrome(main) and self.is_row_palindrome(anti)


def pretty_grid(grid: List[List[str]]) -> str:
    return '\n'.join(' '.join(row) for row in grid)


if __name__ == '__main__':
    # quick self-check quando executado diretamente
    engine = KayosHyperSator6D()
    engine.generate_hypercube()
    print('Diagonal principal:', ''.join(engine.extract_diagonal_principal()))
    print('Anti-diagonal:', ''.join(engine.extract_anti_diagonal()))
    grid01 = engine.project_2d(0, 1)
    print('\nProjecao (0,1):\n', pretty_grid(grid01))
    print('\nPalindromica (0,1)?', engine.verify_projection_palindromic(0, 1))
