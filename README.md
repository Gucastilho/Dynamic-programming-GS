# Vagalume · Global Solution FIAP 2026.2 · CitizenTech

Repositório da disciplina **Dynamic Programming** (Engenharia de Software, 2º ano).

## Ficha da CitizenTech

| | |
|---|---|
| **Nome da CitizenTech** | Vagalume |
| **Cidade e bairro** | São Paulo (SP), Av. Paulista e Bela Vista (piloto) |
| **Cidadão beneficiado** | Quem se desloca a pé ou de transporte público, com foco em mulheres, e também pessoas LGBTQIA+, idosos e quem volta tarde do trabalho ou da faculdade |
| **Problema, em uma frase** | Muitas pessoas, principalmente mulheres, não sabem quais trechos do caminho são mais seguros e acabam escolhendo a rota pelo tempo, e não pela segurança |
| **Como funciona** | O app sugere a rota de menor risco de A até B dentro de quanto a pessoa aceita andar a mais e, se ela se sentir em risco no caminho, indica o Ponto Seguro aberto mais próximo |
| **O que cada parte faz** | **Dynamic Programming:** calcula a rota mais segura dentro do orçamento de desvio (DP `dp[v][d]`) e o Ponto Seguro mais próximo (Bellman-Ford). **Data Science:** análise das ocorrências que alimentam o risco. **Database Design:** modelo de trechos, reports, ocorrências e pontos de apoio. **Java (DDD):** `RoteirizadorService` e `CalculadoraRisco`. **Network:** rede do Ponto Seguro onde roda o servidor da solução. **Agile:** backlog e iterações da squad |
| **Link do repositório** | https://github.com/Gucastilho/Dynamic-programming-GS |
| **Indicador de impacto** | Metros de trecho de alto risco evitados por rota e minutos extras de caminhada aceitos |
| **ODS conectados** | ODS 3 (metas 3.4, 3.5, 3.6), ODS 10 e ODS 11 (metas 11.2, 11.7) |

## Equipe

| Integrante | RM |
|---|---|
| Carlos Santiago Clementino | RM575749 |
| Eduarda da Silva Brito | RM567347 |
| Gustavo Castilho Gonçalves | RM566970 |
| Gustavo Moretim Canzi | RM567683 |
| Lucca Ghiraldi Urso | RM566739 |

## Estrutura

```
dynamic-programming/            entrega da disciplina (avaliada no repositório)
├── vagalume_rota_segura.ipynb  cenário, fonte dos dados, exemplos, testes e benchmark
├── rota_dp.py                  algoritmo (DP de rota segura + Bellman-Ford)
├── test_rota_dp.py             13 testes (unittest)
├── dados/                      nós, trechos e Pontos Seguros (CSV)
└── README.md                   como executar
relatorio-dp/                   relatório em PDF (até 4 páginas) e o script que o gera
prompts.md                      registro do uso de IA como copiloto
```

## Como executar

Veja [dynamic-programming/README.md](dynamic-programming/README.md).
