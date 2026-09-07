# labM1

Laboratórios individuais da M1 — disciplina de Processamento de Imagens (UNIVALI, 2026-02).

Aluno: Guilherme Valentim Pires

## Laboratórios

| Laboratório | Tema | Link |
|---|---|---|
| M1.1 | Representação, canais e níveis de cinza | [`lab_m1_1_guilherme_pires/`](lab_m1_1_guilherme_pires/) |
| M1.2 | Transformações de intensidade | [`lab_m1_2_guilherme_pires/`](lab_m1_2_guilherme_pires/) |
| M1.3 | Convolução e filtragem espacial | [`lab_m1_3_guilherme_pires/`](lab_m1_3_guilherme_pires/) |

Cada laboratório é um projeto Python independente e segue a estrutura comum definida
pelo contrato técnico da disciplina:

```text
lab_m1_x_guilherme_pires/
├── README.md          # como preparar o ambiente e executar
├── REPORT.md          # objetivo, testes, resultados e análise
├── AI_USAGE.md        # declaração de uso de IA generativa
├── lab.json           # metadados do laboratório
├── images/{input,output}/
├── results/           # saídas tabulares (ex.: histogramas em CSV)
├── src/pdi_lab/       # implementação
└── tests/             # testes automatizados (pytest)
```

Veja o `README.md` de cada pasta para instruções específicas de ambiente e execução
(as três seguem o mesmo padrão: `python -m venv .venv`, `pip install -r requirements.txt`,
`python -m pytest`, `python -m pdi_lab --help`).
