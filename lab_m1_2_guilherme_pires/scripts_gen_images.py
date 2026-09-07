"""Script auxiliar (nao faz parte do pacote) para gerar as imagens sinteticas
de entrada em images/input/."""

import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images", "input")
os.makedirs(OUT, exist_ok=True)

# Degrau horizontal em tons de cinza (8x8): metade esquerda escura, direita clara
size = 8
degrau = np.zeros((size, size, 3), dtype=np.uint8)
for y in range(size):
    for x in range(size):
        val = 40 if x < size // 2 else 220
        degrau[y, x] = [val, val, val]
Image.fromarray(degrau, mode="RGB").save(os.path.join(OUT, "degrau_8x8.png"))

# Imagem colorida 16x16 com gradiente de cinza para testar histograma/threshold
size2 = 16
gradiente = np.zeros((size2, size2, 3), dtype=np.uint8)
for y in range(size2):
    for x in range(size2):
        val = int((x / (size2 - 1)) * 255)
        gradiente[y, x] = [val, val, val]
Image.fromarray(gradiente, mode="RGB").save(os.path.join(OUT, "gradiente_16x16.png"))

print("imagens geradas em", OUT)
