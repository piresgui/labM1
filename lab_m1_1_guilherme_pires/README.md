# Laboratório M1.1 — Representação, canais e níveis de cinza

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

A partir da raiz deste laboratório (para que o pacote `pdi_lab` em `src/` seja
encontrado, defina `PYTHONPATH=src` ou instale o pacote em modo editável):

```bash
python -m pip install -e .  # opcional, ou:
export PYTHONPATH=src        # Unix-like
$env:PYTHONPATH = "src"     # PowerShell

python -m pdi_lab --help
```

### Exemplos de execução

Inspecionar uma imagem:

```bash
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation inspect
```

Cópia manual pixel a pixel:

```bash
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation copy
```

Separação de canais:

```bash
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation channel_r
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation channel_g
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation channel_b
```

Conversão para níveis de cinza:

```bash
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation grayscale_average
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output --operation grayscale_weighted
```

Quantização (16, 8, 4 e 2 níveis):

```bash
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output/quant_16.png --operation quantize --levels 16
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output/quant_8.png  --operation quantize --levels 8
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output/quant_4.png  --operation quantize --levels 4
python -m pdi_lab --input images/input/blocos_16x16.png --output images/output/quant_2.png  --operation quantize --levels 2
```

O código de saída é `0` em sucesso e diferente de `0` em erro, com mensagem
descritiva em `stderr` (por exemplo arquivo inexistente, canais inesperados
ou `--levels` inválido).

## Estrutura do projeto

```text
lab_m1_1_guilherme_pires/
├── requirements.txt
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── src/pdi_lab/         # pacote python (cli.py, ops.py, io_utils.py)
├── tests/               # testes pytest
├── images/input/        # imagens sintéticas de entrada
├── images/output/       # saídas geradas pela execução do programa
└── scripts_gen_images.py  # script auxiliar que gera as imagens sintéticas
```

## Imagens de teste

Duas imagens sintéticas foram geradas por `scripts_gen_images.py` (sem
dependência de arquivos externos):

- `images/input/xadrez_8x8.png`: padrão xadrez preto/branco 8x8.
- `images/input/blocos_16x16.png`: imagem colorida 16x16 com quatro blocos
  (vermelho, verde, azul, amarelo).

Casos adicionais (imagem 1x1, 2x2, constante, valores nos limites 0/255) são
gerados em memória diretamente nos testes automatizados.
