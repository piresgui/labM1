"""Script auxiliar (nao faz parte do pacote) para gerar as imagens sinteticas
de entrada em images/input/. Executado uma vez durante o desenvolvimento."""

import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images", "input")
os.makedirs(OUT, exist_ok=True)

# 8x8 com padrao xadrez em RGB (para inspecao, canais, cinza, quantizacao)
size = 8
xadrez = np.zeros((size, size, 3), dtype=np.uint8)
for y in range(size):
    for x in range(size):
        if (x + y) % 2 == 0:
            xadrez[y, x] = [255, 255, 255]
        else:
            xadrez[y, x] = [0, 0, 0]
Image.fromarray(xadrez, mode="RGB").save(os.path.join(OUT, "xadrez_8x8.png"))

# 16x16 colorida com blocos de cor (imagem "real" sintetica colorida)
size2 = 16
blocos = np.zeros((size2, size2, 3), dtype=np.uint8)
cores = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
]
bloco = size2 // 2
for by in range(2):
    for bx in range(2):
        cor = cores[by * 2 + bx]
        blocos[by * bloco:(by + 1) * bloco, bx * bloco:(bx + 1) * bloco] = cor
Image.fromarray(blocos, mode="RGB").save(os.path.join(OUT, "blocos_16x16.png"))

print("imagens geradas em", OUT)
