# Mini relatório — Laboratório M1.3

## 1. Identificação

- Aluno: Guilherme Valentim Pires
- Laboratório: M1.3 — Convolução e filtragem espacial
- Linguagem: Python 3.12

## 2. Objetivo

Implementar operações de vizinhança e convolução no domínio espacial,
tratando explicitamente kernels, bordas, tipos numéricos e saturação:
convolução genérica, filtros de suavização (média 3x3, média ponderada
3x3, média 5x5), operador Laplaciano com realce, e operador Sobel (Gx, Gy
e as duas magnitudes de gradiente).

## 3. Operações implementadas

- convolve: convolução espacial genérica manual, recebendo imagem em
  cinza, kernel quadrado de dimensão ímpar e estratégia de borda.
- Estratégias de borda: copy (pixels onde a vizinhança não cabe mantêm o
  valor original) e replicate (coordenada fora da imagem é substituída
  pela coordenada válida mais próxima).
- mean_filter (média 3x3, e 5x5 via kernel externo), weighted_mean_filter
  (média ponderada 3x3, pesos [[1,2,1],[2,4,2],[1,2,1]]/16).
- laplacian: resposta bruta em float64 (pode ser negativa), versão
  normalizada para visualização e imagem realçada (original + resposta).
- sobel: Gx, Gy, magnitude aproximada (|Gx|+|Gy|) e magnitude euclidiana
  (sqrt(Gx²+Gy²)).

O percurso da vizinhança é feito com laços explícitos aninhados sobre o
kernel (nenhuma função pronta de convolução, filtro de média, Laplaciano
ou Sobel é usada); os acumuladores usam float64 durante todo o cálculo, e
a saturação para uint8 [0,255] só ocorre na etapa final (`to_uint8` /
`to_uint8_normalized`).

## 4. Decisões de implementação

Iniciei o Lab M1.3 desenvolvendo a estrutura manual de convolução espacial
genérica em escala de cinza, realizando a varredura da vizinhança pixel a
pixel sem funções prontas: para cada pixel de saída, dois laços aninhados
percorrem as linhas e colunas do kernel, calculando a coordenada de
vizinhança correspondente a partir do raio (`krows // 2`). Implementei as
validações iniciais para garantir que o kernel seja quadrado, não vazio e
de dimensão ímpar, tanto na leitura do arquivo de kernel
(`io_utils.load_kernel`/`validate_kernel`) quanto na própria função
`convolve` (defesa em profundidade).

Para evitar erros de estouro numérico durante a soma dos pesos, estruturei
o pipeline com tipos numéricos intermediários em float64 (a imagem de
entrada é convertida com `.astype(np.float64)` antes de qualquer soma) e
só aplico a saturação final na conversão para uint8. Isso é essencial para
o Laplaciano e o Sobel, cujas respostas podem ser negativas ou maiores que
255 antes da etapa final.

Validei a lógica de deslocamento da matriz com testes usando o kernel
identidade sobre uma imagem qualquer (deve reproduzir a entrada
exatamente) e com uma imagem constante (a resposta de qualquer filtro de
média sobre uma imagem constante deve ser igual à própria constante).

Finalizei o tratamento de bordas (estratégias copiar/ignorar e replicar) —
a diferença mais visível ocorre exatamente nos pixels de canto/borda,
onde a vizinhança completa não cabe: com `copy` o pixel de saída é
idêntico ao de entrada; com `replicate` o pixel de saída é uma média que
usa coordenadas clampadas, produzindo um valor diferente sempre que a
vizinhança clampada não for simétrica em relação ao pixel original. Por
fim, apliquei os filtros de suavização por média (3x3, ponderada e 5x5), e
implementei os operadores Laplaciano e Sobel (Gx, Gy, magnitude
aproximada e euclidiana) para fechar o relatório.

Optei por documentar explicitamente o kernel Laplaciano escolhido:
`[[0,-1,0],[-1,4,-1],[0,-1,0]]` (centro positivo). Com esse kernel, a
resposta é positiva quando o pixel central é mais claro que a média dos
vizinhos diretos (um "pico" de intensidade) e negativa quando é mais
escuro — por isso a imagem realçada é calculada como `original + resposta
bruta` (e não subtraída).

## 5. Testes realizados

Testes unitários de operações (`tests/test_ops.py`, 26 casos): guardas de
`convolve` (forma de entrada errada, kernel vazio, não quadrado, de
dimensão par, borda inválida), kernel identidade reproduzindo a imagem
exatamente com `copy` e com `replicate`, imagem constante permanecendo
constante após média, impulso se espalhando corretamente pela vizinhança
(incluindo o valor exato esperado 90/9=10 no centro), diferença entre as
estratégias de borda nos cantos, filtro de média reduzindo o desvio padrão
de um padrão xadrez, média ponderada preservando uma imagem constante,
média 5x5 com a forma de saída correta, Laplaciano zerado em imagem
constante e com valores negativos possíveis, Laplaciano com resposta forte
em uma borda tipo degrau, Sobel respondendo mais em Gx para degrau
vertical e mais em Gy para degrau horizontal, diferença entre as duas
magnitudes de gradiente, Sobel zerado em imagem constante, e casos
sintéticos adicionais (imagem 1x1, 2x2, conteúdo tocando a borda).

Testes de `io_utils` (`tests/test_io_utils.py`, 9 casos): carregamento de
kernel válido, arquivo de kernel inexistente, kernel vazio, quantidade de
valores incorreta, kernel não quadrado, kernel de dimensão par, valor não
numérico, validação isolada de kernel válido, e imagem de entrada
inexistente.

Testes de ponta a ponta via CLI (`tests/test_cli.py`, 8 casos): arquivo de
entrada inexistente, `convolution` sem `--kernel` (deve falhar),
`convolution` com arquivo de kernel inexistente (deve falhar),
`convolution` com kernel identidade produzindo saída idêntica à entrada,
estratégia de borda inválida (deve falhar), `mean_filter` com kernel
padrão preservando uma imagem constante, `laplacian` gerando os dois
arquivos de saída esperados (visualização e versão realçada), e `sobel`
gerando os quatro arquivos de saída esperados (Gx, Gy, magnitude
aproximada e magnitude euclidiana).

Total: 43 testes, todos passando (`python -m pytest`).

## 6. Resultados

No degrau vertical (`degrau_vertical_12x12.png`), a soma das magnitudes
absolutas do Sobel foi `sum|Gx| = 20640` contra `sum|Gy| = 0` — confirma
que `Gx` responde exclusivamente a bordas verticais (mudança de
intensidade na direção horizontal) e `Gy` não responde nada, pois não há
variação vertical na imagem.

No quadrado com faixa tocando a borda (`quadrado_16x16.png`), no pixel de
canto (0,0), o filtro de média 3x3 produziu `133` com borda `replicate`
contra `200` com borda `copy` (o valor original do pixel também é `200`) —
evidenciando que `copy` preserva exatamente o valor original nas regiões
periféricas, enquanto `replicate` mistura o valor do canto com os pixels
vizinhos clampados, suavizando também a borda.

Comparando a redução de variação: o desvio padrão da imagem original é
`113,76`; após média 3x3 cai para `91,74`; após média 5x5 cai ainda mais,
para `75,69` — confirma que kernels maiores produzem suavização mais
forte, ao custo de mais detalhe perdido e mais operações por pixel (9
multiplicações/somas por pixel na 3x3 contra 25 na 5x5).

A resposta bruta do Laplaciano na mesma imagem variou de `-255` a `510`,
confirmando que a resposta pode ultrapassar amplamente o intervalo
[0,255] e conter valores negativos antes da etapa de saturação/normalização.

As imagens de saída completas estão em `images/output/` (convolução com
kernel identidade, médias 3x3/5x5 com as duas bordas, média ponderada,
Laplaciano com versão realçada, e Sobel Gx/Gy/magnitudes sobre o degrau
vertical e sobre o quadrado).

## 7. Análise técnica

**1. Diferença entre uma operação pontual e uma operação de vizinhança.**
Uma operação pontual (M1.2) calcula cada pixel de saída usando somente o
pixel correspondente de entrada. Uma operação de vizinhança (M1.3) calcula
cada pixel de saída combinando um conjunto de pixels ao redor da posição
correspondente (definido pelo kernel), o que permite capturar informação
espacial — suavização, bordas, texturas — que uma transformação pontual
não consegue expressar.

**2. Por que kernels normalmente possuem dimensões ímpares.** Um kernel de
dimensão ímpar tem um pixel central bem definido, que coincide exatamente
com a posição do pixel de saída sendo calculado; isso torna simétrica a
vizinhança ao redor desse centro (mesmo número de vizinhos de cada lado) e
evita ambiguidade sobre qual pixel representa a "posição" do kernel. Com
dimensão par não haveria um centro único, exigindo uma convenção
arbitrária de arredondamento.

**3. Efeito de aumentar o tamanho do kernel de média.** Os resultados
numéricos confirmam: aumentar de 3x3 para 5x5 aumenta a suavização (desvio
padrão caiu de 91,74 para 75,69) e a área de influência de cada pixel,
mas também aumenta a perda de detalhes finos (mais vizinhos contribuem
para cada saída, borrando estruturas pequenas) e o custo computacional
(25 operações por pixel contra 9).

**4. Como a estratégia de borda interfere no resultado.** Como mostrado no
pixel de canto (0,0) do quadrado, `copy` preserva exatamente os valores
originais onde a vizinhança não cabe, enquanto `replicate` sempre calcula
uma resposta (usando bordas clampadas), o que tende a suavizar também as
regiões periféricas de forma diferente da região central. A diferença é
sempre localizada — no centro da imagem (onde a vizinhança sempre cabe) as
duas estratégias produzem resultados idênticos.

**5. Por que a resposta bruta do Laplaciano pode conter valores negativos.**
O kernel Laplaciano tem pesos que somam zero (`0-1+... = 0`), então sua
resposta mede a diferença entre o pixel central e a média dos vizinhos —
essa diferença pode ser positiva (pixel mais claro que os vizinhos) ou
negativa (pixel mais escuro), como confirmado pelo intervalo observado
(-255 a 510). Por isso os acumuladores precisam ser mantidos em ponto
flutuante durante o cálculo, sendo saturados/normalizados somente ao
final.

**6. Diferença entre Gx e Gy no Sobel.** `Gx` usa um kernel com derivada
na direção horizontal (colunas -1/0/+1), respondendo a variações de
intensidade ao longo do eixo x — ou seja, a bordas verticais. `Gy` usa a
derivada na direção vertical (linhas -1/0/+1), respondendo a bordas
horizontais. Isso foi confirmado numericamente: no degrau vertical,
`sum|Gx|=20640` e `sum|Gy|=0`.

**7. Diferenças entre `|Gx|+|Gy|` e `sqrt(Gx²+Gy²)`.** Para gradientes
puramente horizontais ou verticais (só Gx ou só Gy diferente de zero), as
duas fórmulas coincidem. Para gradientes diagonais (Gx e Gy ambos não
nulos), `|Gx|+|Gy|` (distância de Manhattan) é sempre maior ou igual a
`sqrt(Gx²+Gy²)` (distância euclidiana) — a magnitude aproximada
superestima a magnitude real do gradiente nessas regiões, o que foi
confirmado no teste `test_sobel_magnitude_approx_vs_euclidean_differ`. A
magnitude aproximada é mais barata computacionalmente (sem raiz
quadrada), enquanto a euclidiana é geometricamente mais correta.

## 8. Limitações

- Os laços Python explícitos usados para atender à regra de percurso
  manual tornam a convolução O(H×W×k²), o que é adequado para as imagens
  de teste (até 16x16) mas seria lento para imagens grandes ou kernels
  maiores que 5x5.
- Apenas duas estratégias de borda foram implementadas (copy e replicate),
  conforme exigido pelo enunciado; outras estratégias comuns (espelhamento,
  borda com zero-padding) não foram implementadas.
- O kernel Laplaciano escolhido (centro positivo, vizinhos -1) é uma entre
  duas variantes comuns; a escolha foi documentada explicitamente em
  `ops.py` e neste relatório para transparência, mas o sinal da resposta
  bruta depende dessa escolha.

## 9. Declaração de uso de IA

Ver AI_USAGE.md.

## 10. Referências

- Slides e material da disciplina de Processamento de Imagens (UNIVALI,
  2026-02).
- Documentação oficial do NumPy e do Pillow.
