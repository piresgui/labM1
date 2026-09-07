# Mini relatório — Laboratório M1.1

## 1. Identificação

- Aluno: Guilherme Valentim Pires
- Laboratório: M1.1 — Representação, canais e níveis de cinza
- Linguagem: Python 3.12

## 2. Objetivo

Implementar operações fundamentais de representação de imagens digitais por
meio de acesso direto aos pixels: inspeção, cópia manual, separação de
canais, conversão para níveis de cinza (média simples e ponderada) e
quantização, relacionando dimensões, canais, intensidade e resolução
radiométrica.

## 3. Operações implementadas

- inspect: largura, altura, número de canais, tipo, quantidade de pixels,
  mínimo, máximo e média — geral e por canal — calculados com percurso
  explícito de pixels (src/pdi_lab/ops.py::inspect).
- copy: cópia pixel a pixel para uma nova matriz (copy_manual).
- channel_r / channel_g / channel_b: isolamento de cada canal,
  zerando os demais (channel_isolate).
- grayscale_average: g = (R+G+B)/3.
- grayscale_weighted: g = 0,299R + 0,587G + 0,114B.
- quantize: redução para N níveis (16, 8, 4, 2), com faixas de largura
  256/N e valor representativo no ponto médio da faixa, saturado em [0,255].

Todas as operações avaliadas percorrem a imagem com laços explícitos sobre
linhas e colunas (e canais, quando aplicável); numpy é usado apenas para
alocar as matrizes de saída e para operações aritméticas elemento a
elemento durante o cálculo, nunca para substituir a operação avaliada.
Pillow é usado somente para abrir e salvar arquivos.

## 4. Decisões de implementação

Optei por Python para o laboratório e comecei pela inspeção da imagem,
calculando manualmente largura, altura, canais, valores mínimo/máximo e
média por canal. Na primeira versão eu não estava convertendo a imagem para
RGB antes de processá-la, o que quebrava o código para imagens em outros
modos (por exemplo, PNGs em modo P ou L); corrigi isso adicionando a
conversão explícita para RGB logo na leitura (io_utils.load_image_rgb),
de forma que todo o restante do pipeline pudesse assumir uma convenção fixa
de canais.

Em seguida implementei a cópia manual, percorrendo pixel a pixel e
validando que a saída fosse numericamente idêntica à entrada (isso é
coberto pelos testes test_copy_is_numerically_identical e
test_copy_2x2).

Ao trabalhar a separação dos canais RGB, tive dificuldade inicial para
confirmar a ordem correta dos canais — o Pillow usa RGB, enquanto outras
bibliotecas de visão computacional (como OpenCV) usam BGR por padrão — e
isso gerou confusão ao isolar e zerar os canais. Resolvi isso documentando
explicitamente, no topo de ops.py, a convenção RGB usada em todo o
projeto (índice 0 = R, 1 = G, 2 = B), e cobri a ordem com testes dedicados
por canal.

Para a quantização, escolhi representar cada faixa pelo seu ponto médio
(em vez do limite inferior), o que produz um resultado visualmente mais
equilibrado e evita que o nível mais alto (255) fique sistematicamente
sub-representado.

## 5. Testes realizados

Testes unitários (tests/test_ops.py, 18 casos) cobrindo:

- inspect em imagem 1x1, imagem constante e entrada com número de canais
  incorreto (deve lançar OperationError);
- copy com verificação de igualdade numérica exata e não-aliasing;
- separação de cada canal (r/g/b) e canal inválido;
- grayscale_average e grayscale_weighted com valores conhecidos
  calculados à mão, incluindo saturação nos limites 0 e 255;
- diferença entre média simples e ponderada para uma cor saturada;
- quantize com 2, 4 e 16 níveis, valores nos limites e níveis inválidos
  (0, 1 e 257).

Testes de ponta a ponta via CLI (tests/test_cli.py, 5 casos) cobrindo
arquivo inexistente, inspect, copy (comparando a imagem salva em disco
com a entrada), quantize sem --levels (deve falhar) e quantize com
--levels válido.

Total: 23 testes, todos passando (python -m pytest).

## 6. Resultados

Executando inspect na imagem sintética blocos_16x16.png (4 blocos
vermelho/verde/azul/amarelo):

```text
width=16 height=16 channels=3 pixels=256 type=uint8
min=0 max=255 mean=106.2500
channel_r_mean=127.5000 channel_g_mean=127.5000 channel_b_mean=63.7500
```

Comparando média simples e ponderada nos quatro blocos de cor pura:

| Bloco | grayscale_average | grayscale_weighted |
|---|---:|---:|
| vermelho (255,0,0) | 85 | 76 |
| verde (0,255,0) | 85 | 150 |
| azul (0,0,255) | 85 | 29 |
| amarelo (255,255,0) | 170 | 226 |

As imagens de saída (copy.png, channel_r.png, channel_g.png,
channel_b.png, gray_average.png, gray_weighted.png, quant_16.png,
quant_8.png, quant_4.png, quant_2.png) estão em images/output/.

## 7. Análise técnica

1. Diferença entre resolução espacial e resolução radiométrica.
Resolução espacial é a quantidade de amostras (pixels) usadas para
representar a imagem no plano — está ligada à largura e altura em pixels
e determina o nível de detalhe geométrico capturado. Resolução
radiométrica é a quantidade de níveis distintos disponíveis para
representar a intensidade de cada pixel (no nosso caso, 256 níveis por
canal em 8 bits) — está ligada à precisão com que a intensidade é
representada. A operação quantize deste laboratório reduz exclusivamente
a resolução radiométrica, sem alterar largura/altura.

2. Por que a média ponderada produz resultado diferente da média
simples. A tabela acima mostra isso claramente: a média simples trata os
três canais como igualmente relevantes (peso 1/3 cada), enquanto a média
ponderada usa os pesos 0,299/0,587/0,114, que refletem a sensibilidade
diferente do olho humano a cada cor (maior sensibilidade ao verde, menor ao
azul). Por isso um bloco puro verde (0,255,0) resulta em 85 na média
simples mas 150 na ponderada, e um bloco azul puro (0,0,255) cai para 29 na
ponderada — a mesma magnitude de canal produz luminâncias percebidas muito
diferentes.

3. O que ocorre visualmente quando a quantidade de níveis é reduzida.
Ao reduzir de 16 para 2 níveis, a imagem perde gradações suaves e passa a
apresentar contornos em "faixas" (posterização): regiões que antes tinham
uma transição gradual de tons passam a ter saltos abruptos entre um número
pequeno de intensidades. Com 2 níveis a imagem se torna essencialmente
binária.

4. Em quais regiões a perda de informação fica mais evidente. A perda é
mais evidente em regiões de gradiente suave (transições graduais de
intensidade), onde a quantização grosseira introduz bandas visíveis
("banding"). Em regiões já homogêneas (como os blocos de cor sólida da
imagem sintética), a perda é imperceptível, pois todos os pixels da região
já caem na mesma faixa de quantização.

5. Como o tipo e o número de canais interferem no acesso a um pixel.
Uma imagem em escala de cinza (H, W) é acessada com dois índices
imagem[y, x] e retorna um escalar; uma imagem RGB (H, W, 3) exige um
terceiro índice de canal imagem[y, x, c]. Isso afeta diretamente os laços
de percurso: operações como inspect e copy precisam de um laço adicional
sobre os canais, enquanto grayscale_average/grayscale_weighted leem os
três canais de um pixel de entrada mas escrevem um único valor de saída.
Além disso, o tipo (uint8) limita o intervalo válido a [0, 255] e exige
cuidado com overflow/underflow durante os cálculos intermediários (por isso
os cálculos de média são feitos em float/int do Python antes da
saturação final).

## 8. Limitações

- A conversão para RGB na leitura (load_image_rgb) padroniza a entrada,
  mas descarta o canal alfa de imagens RGBA sem realizar composição sobre um
  fundo — para os fins deste laboratório (imagens sem transparência
  relevante) isso não é um problema, mas é uma simplificação consciente.
- A implementação usa laços Python explícitos (não vetorizados) para
  atender à regra de percurso manual da disciplina; isso é adequado para as
  imagens de teste utilizadas, mas seria lento para imagens muito grandes —
  trade-off aceito porque o objetivo do laboratório é didático, não
  desempenho.
- Os testes cobrem os casos exigidos pelo enunciado (imagem pequena,
  valores nos limites, quantidade de canais), mas não incluem imagens
  fotográficas reais de alta resolução.

## 9. Declaração de uso de IA

Ver AI_USAGE.md.

## 10. Referências

- Slides e material da disciplina de Processamento de Imagens (UNIVALI,
  2026-02).
- Documentação oficial do NumPy e do Pillow (para uso permitido de
  I/O e alocação de matrizes).
