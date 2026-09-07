# Laboratório M1.3 — Convolução e filtragem espacial

Disciplina: Processamento de Imagens (UNIVALI, 2026-02).
Aluno: Guilherme Valentim Pires.

## Linguagem e dependências

- Python 3.12
- numpy
- pillow
- pytest

Dependências declaradas em [`requirements.txt`](requirements.txt).

## Preparar o ambiente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix-like: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Rodar os testes

```bash
python -m pytest
```

## Executar a aplicação

```bash
export PYTHONPATH=src        # Unix-like
$env:PYTHONPATH = "src"     # PowerShell

python -m pdi_lab --help
```

A imagem de entrada é sempre convertida internamente para níveis de cinza
(média ponderada, reaproveitada dos laboratórios anteriores).

### Exemplos de execução

Convolução genérica com um kernel arbitrário:

```bash
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/convolution_identity.png --operation convolution --kernel kernels/identity_3x3.txt --border replicate
```

Filtro de média 3x3 (kernel embutido) e comparação de bordas:

```bash
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/mean_3x3.png --operation mean_filter --border replicate
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/mean_3x3_copy.png --operation mean_filter --border copy
```

Filtro de média 5x5 (passando um kernel externo para `mean_filter`):

```bash
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/mean_5x5.png --operation mean_filter --kernel kernels/mean_5x5.txt --border replicate
```

Filtro de média ponderada 3x3:

```bash
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/weighted_mean_3x3.png --operation weighted_mean --border replicate
```

Laplaciano (gera `<saida>.png` normalizado para visualização e
`<saida>_enhanced.png` com a imagem realçada):

```bash
python -m pdi_lab --input images/input/quadrado_16x16.png --output images/output/laplacian.png --operation laplacian --border replicate
```

Sobel (gera `<saida>_gx.png`, `<saida>_gy.png`,
`<saida>_magnitude_approx.png` e `<saida>_magnitude_euclidean.png`):

```bash
python -m pdi_lab --input images/input/degrau_vertical_12x12.png --output images/output/sobel_vertical.png --operation sobel --border replicate
```

O código de saída é `0` em sucesso e diferente de `0` em erro, com mensagem
descritiva em `stderr` (arquivo/kernel inexistente, kernel vazio, não
quadrado, de dimensão par, ou estratégia de borda inválida).

## Formato do kernel

```text
3 3
0 0 0
0 1 0
0 0 0
```

A primeira linha informa linhas e colunas; as seguintes contêm os valores.
Veja os kernels prontos em [`kernels/`](kernels/): `identity_3x3.txt`,
`mean_3x3.txt`, `mean_5x5.txt`, `weighted_mean_3x3.txt`,
`laplacian_3x3.txt`, `sobel_gx_3x3.txt` e `sobel_gy_3x3.txt`.

## Estrutura do projeto

```text
lab_m1_3_guilherme_pires/
├── requirements.txt
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── src/pdi_lab/         # pacote python (cli.py, ops.py, io_utils.py)
├── tests/               # testes pytest
├── kernels/             # arquivos de kernel no formato do contrato
├── images/input/        # imagens sintéticas de entrada
├── images/output/       # saídas geradas pela execução do programa
└── scripts_gen_images.py  # script auxiliar que gera as imagens sintéticas
```

## Imagens de teste

- `images/input/degrau_vertical_12x12.png`: degrau vertical (colunas
  esquerdas escuras, direitas claras) — útil para observar `Gx` do Sobel.
- `images/input/quadrado_16x16.png`: quadrado branco sobre fundo preto,
  com uma faixa clara tocando a borda superior — útil para Laplaciano,
  filtros de média e comparação de estratégias de borda.

Casos adicionais (imagem 1x1, 2x2, constante, impulso, degraus vertical e
horizontal, kernels de tamanhos diferentes) são gerados em memória
diretamente nos testes automatizados.
