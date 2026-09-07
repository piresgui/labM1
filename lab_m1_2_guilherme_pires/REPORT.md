# Mini relatório — Laboratório M1.2

## 1. Identificação

- Aluno: Guilherme Valentim Pires
- Laboratório: M1.2 — Transformações de intensidade
- Linguagem: Python 3.12

## 2. Objetivo

Implementar transformações pontuais em imagens em níveis de cinza (brilho,
contraste, negativo, limiarização binária) e o histograma manual,
analisando como cada operação altera os valores dos pixels e a
distribuição das intensidades.

## 3. Operações implementadas

- grayscale_weighted: conversão para cinza reaproveitada do M1.1, usada
  como entrada de todas as transformações deste laboratório.
- brightness: g(x,y) = f(x,y) + b, com b positivo e negativo.
- contrast: g(x,y) = alpha*(f(x,y)-128) + 128, testado com alpha=0.5,
  1.0 e 1.5.
- negative: g(x,y) = 255 - f(x,y).
- threshold: limiarização binária com dois valores de T distintos.
- histogram: contagem manual de 256 posições, exportada em CSV
  (intensity,count).

Todas as transformações percorrem a imagem com laços explícitos sobre
linhas e colunas; a saturação para [0,255] é aplicada apenas ao final de
cada cálculo, com os valores intermediários calculados em float/int do
Python (nunca em uint8) para evitar overflow/underflow silencioso.

## 4. Decisões de implementação

Dando continuidade ao laboratório anterior, concentrei os esforços no
desenvolvimento do Lab M1.2 aplicando as transformações de intensidade no
domínio do valor através do acesso direto à matriz de pixels. O ponto de
partida foi estruturar a conversão das imagens para escala de cinza por
média ponderada (reaproveitando a implementação manual do M1.1) e resolver
o fluxo de leitura, de forma que toda transformação pontual recebesse
sempre uma matriz 2D já em níveis de cinza.

Em seguida implementei as funções de ajuste de brilho e contraste. A maior
atenção esteve no tratamento de overflow e underflow: para evitar
distorções visuais ao extrapolar os limites numéricos durante as somas e
multiplicações, apliquei o truncamento dos valores no intervalo [0,255]
por meio de uma função `_saturate_round` que arredonda e satura cada
resultado individualmente, aplicada somente depois do cálculo em ponto
flutuante — nunca antes, para não perder precisão prematuramente.

Com a trava de saturação validada, avancei para o filtro negativo
(255 - intensidade) e a limiarização binária, testando diferentes valores
de corte (T) na mesma imagem para observar a diferença na área
binarizada. Por fim, construí a varredura para contagem do histograma
manualmente (um vetor de 256 posições incrementado pixel a pixel),
gerando os dados de frequência das intensidades para exportação em CSV e
produzindo as evidências comparativas antes e depois das transformações.

## 5. Testes realizados

Testes unitários (`tests/test_ops.py`, 19 casos) cobrindo:

- brilho positivo, negativo, saturação em 0 e em 255, e imagem com forma
  errada (RGB em vez de cinza, deve lançar `OperationError`);
- contraste com alpha=1.0 (identidade), alpha=0.5 (reduzido, com valores
  calculados à mão) e alpha=1.5 (ampliado, provocando saturação nos dois
  extremos), além de alpha negativo inválido;
- negativo com valores conhecidos (0↔255, 128↔127);
- limiarização com dois valores de T distintos na mesma imagem e valores
  de T fora do intervalo [0,255];
- histograma: tamanho (256), soma total igual à quantidade de pixels,
  imagem constante, imagem impulso e forma de entrada incorreta.

Testes de ponta a ponta via CLI (`tests/test_cli.py`, 5 casos) cobrindo
arquivo inexistente, `brightness` sem `--value` (deve falhar), `brightness`
com sucesso (valor de pixel conferido), `threshold` com dois limiares
distintos produzindo saídas diferentes, e o formato exato do CSV do
histograma (cabeçalho `intensity,count`, 256 linhas de dados, soma
das contagens igual ao número de pixels).

Total: 24 testes, todos passando (`python -m pytest`).

## 6. Resultados

Histograma da imagem original `gradiente_16x16.png` (gradiente de 16
colunas, 16 pixels por coluna): 16 intensidades distintas
(0, 17, 34, ..., 255), cada uma com 16 ocorrências — confirma que o
gradiente é uniforme e que a contagem manual bate com a estrutura
conhecida da imagem sintética.

Após `brightness --value 40`, o histograma se desloca inteiramente para a
direita: as intensidades passam a ser 40, 57, 74, ..., 255, e a última
faixa (que ultrapassaria 255) se acumula em 255 com 48 ocorrências (em vez
de 16), evidenciando a saturação — três colunas do gradiente original
(221, 238, 255) colapsam no mesmo valor 255 após somar 40 e saturar.

Após `threshold --threshold 100` aplicado à imagem original, o histograma
colapsa para apenas dois valores: 0 com 96 ocorrências e 255 com 160
ocorrências (de um total de 256 pixels) — toda a informação de gradação
intermediária é perdida, restando apenas a informação binária "abaixo" ou
"acima" do limiar.

As imagens de saída (`brightness_pos.png`, `brightness_neg.png`,
`contrast_05.png`, `contrast_10.png`, `contrast_15.png`, `negative.png`,
`threshold_100.png`, `threshold_180.png`, `degrau_negative.png`) estão em
`images/output/`; os históricos em `results/hist_original.csv`,
`results/hist_brightness_pos.csv` e `results/hist_threshold_100.csv`.

## 7. Análise técnica

**1. Diferença entre alteração de brilho e alteração de contraste.** O
brilho desloca todos os valores de intensidade pela mesma quantidade
aditiva (translação do histograma), preservando a diferença entre
intensidades vizinhas. O contraste, por sua vez, escala a distância de
cada valor em relação ao ponto médio (128): com alpha > 1 as diferenças
entre pixels são amplificadas (a imagem "estica" o histograma), e com
alpha < 1 as diferenças são reduzidas (o histograma "comprime" em torno de
128). Ou seja, brilho translada, contraste expande/comprime.

**2. Em quais testes ocorreu saturação e qual foi seu efeito.** Ocorreu
saturação em `brightness --value 40` (as três colunas de maior intensidade
do gradiente colapsaram em 255, perdendo distinção entre elas — visível no
histograma como o pico anômalo de 48 ocorrências em 255) e em
`contrast --alpha 1.5` (o valor mínimo (0-128)*1.5+128 = -64 satura em 0,
e o máximo (255-128)*1.5+128 = 318,5 satura em 255). O efeito da saturação
é sempre perda de informação: múltiplos valores de entrada distintos
passam a produzir o mesmo valor de saída, tornando essa parte da
transformação não-inversível.

**3. Como o histograma se deslocou após alterar o brilho.** Como descrito
nos resultados, o histograma inteiro se deslocou 40 posições para a
direita, mantendo o mesmo formato (16 barras de mesma altura) exceto pela
extremidade direita, onde a saturação empilhou três barras que
ultrapassariam 255 em uma única barra em 255.

**4. Como a distribuição das intensidades mudou ao alterar o contraste.**
Com alpha=1.0 a distribuição é idêntica à original (transformação
identidade). Com alpha=0.5 as 16 barras se aproximam do centro (128),
reduzindo a amplitude total ocupada no eixo de intensidades — a imagem
fica visualmente "achatada", com menos contraste perceptível. Com
alpha=1.5 as barras se afastam do centro e duas delas colapsam nos
extremos 0 e 255 por saturação, aumentando o contraste aparente mas
perdendo informação nos extremos.

**5. Que informação é perdida após a limiarização.** Toda a informação de
gradação de intensidade é perdida: a limiarização reduz uma imagem de 256
níveis possíveis para apenas 2 (0 ou 255), preservando somente a
informação posicional de estar acima ou abaixo do limiar T. Não é possível
recuperar a intensidade original de um pixel a partir do resultado
binarizado.

## 8. Limitações

- As transformações pontuais assumem imagens já em níveis de cinza; a
  conversão de RGB para cinza usa sempre a média ponderada (não há opção
  de aplicar as operações diretamente sobre uma imagem colorida canal a
  canal, o que não foi exigido pelo enunciado).
- Os laços explícitos em Python tornam a execução mais lenta que uma
  implementação vetorizada; aceitável para as imagens de teste utilizadas
  (até 16x16), mas não otimizado para imagens grandes.
- Os valores de `--alpha` e `--threshold` são validados quanto ao
  intervalo, mas não há limite superior para `--value` (brilho), pois
  qualquer deslocamento inteiro é matematicamente válido — a saturação
  final garante que a saída permaneça em [0,255] mesmo com valores
  extremos.

## 9. Declaração de uso de IA

Ver AI_USAGE.md.

## 10. Referências

- Slides e material da disciplina de Processamento de Imagens (UNIVALI,
  2026-02).
- Documentação oficial do NumPy e do Pillow.
