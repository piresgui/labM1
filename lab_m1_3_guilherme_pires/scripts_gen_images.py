"""Script auxiliar (nao faz parte do pacote) para gerar as imagens sinteticas
de entrada em images/input/."""

import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images", "input")
os.makedirs(OUT, exist_ok=True)

# Degrau vertical (colunas esquerda escuras, direita claras) 12x12, RGB
size = 12
degrau_v = np.zeros((size, size, 3), dtype=np.uint8)
for y in range(size):
    for x in range(size):
        val = 20 if x < size // 2 else 235
        degrau_v[y, x] = [val, val, val]
Image.fromarray(degrau_v, mode="RGB").save(os.path.join(OUT, "degrau_vertical_12x12.png"))

# Quadrado branco sobre fundo preto, tocando as bordas parcialmente (forma geometrica)
size2 = 16
quadrado = np.zeros((size2, size2, 3), dtype=np.uint8)
quadrado[4:12, 4:12] = [255, 255, 255]
# conteudo tocando a borda: uma faixa branca na borda superior
quadrado[0, :] = [200, 200, 200]
Image.fromarray(quadrado, mode="RGB").save(os.path.join(OUT, "quadrado_16x16.png"))

print("imagens geradas em", OUT)
