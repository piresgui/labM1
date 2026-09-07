# Laboratório M1.2 — Transformações de intensidade

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
(média ponderada) antes das transformações pontuais deste laboratório.

### Exemplos de execução

Brilho (positivo e negativo):

```bash
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/brightness_pos.png --operation brightness --value 40
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/brightness_neg.png --operation brightness --value -40
```

Contraste (reduzido, identidade, ampliado):

```bash
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/contrast_05.png --operation contrast --alpha 0.5
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/contrast_10.png --operation contrast --alpha 1.0
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/contrast_15.png --operation contrast --alpha 1.5
```

Negativo:

```bash
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/negative.png --operation negative
```

Limiarização binária (dois valores de T):

```bash
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/threshold_100.png --operation threshold --threshold 100
python -m pdi_lab --input images/input/gradiente_16x16.png --output images/output/threshold_180.png --operation threshold --threshold 180
```

Histograma (CSV `intensidade,quantidade` com 256 linhas de dados):

```bash
python -m pdi_lab --input images/input/gradiente_16x16.png --output results/hist_original.csv --operation histogram
python -m pdi_lab --input images/output/brightness_pos.png --output results/hist_brightness_pos.csv --operation histogram
python -m pdi_lab --input images/output/threshold_100.png --output results/hist_threshold_100.csv --operation histogram
```

O código de saída é `0` em sucesso e diferente de `0` em erro, com mensagem
descritiva em `stderr` (arquivo inexistente, `--value`/`--alpha`/`--threshold`
ausentes ou fora do intervalo válido, etc.).

## Estrutura do projeto

```text
lab_m1_2_guilherme_pires/
├── requirements.txt
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── src/pdi_lab/         # pacote python (cli.py, ops.py, io_utils.py)
├── tests/               # testes pytest
├── images/input/        # imagens sintéticas de entrada
├── images/output/       # saídas geradas pela execução do programa
├── results/             # histogramas em CSV
└── scripts_gen_images.py  # script auxiliar que gera as imagens sintéticas
```

## Imagens de teste

- `images/input/degrau_8x8.png`: degrau horizontal (metade escura, metade
  clara) em tons de cinza.
- `images/input/gradiente_16x16.png`: gradiente horizontal de cinza (0 a
  255), útil para observar deslocamento de histograma e efeitos de
  saturação.

Casos adicionais (imagem 1x1, constante, impulso, valores nos limites
0/255) são gerados em memória diretamente nos testes automatizados.
