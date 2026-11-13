# Uso de IA como copiloto

Conforme os combinados da GS, a IA foi usada para aprender e revisar. Abaixo, os prompts usados e o que foi aproveitado de cada um. Todos os integrantes sabem explicar cada linha do código entregue.

<!-- TODO: registrar os prompts usados pela equipe antes desta revisão (concepção do algoritmo, código, notebook e relatório) -->

| # | Ferramenta | Prompt (resumo) | Para quê | O que foi aproveitado / alterado |
|---|---|---|---|---|
| 1 | | | | |
| 2 | Claude Code | "Faça uma análise do projeto" | Revisão técnica do código, dos testes e do notebook | Lista de pontos de atenção: limite da discretização, validação da hora e escolha do Bellman-Ford. Nenhum código foi alterado |
| 3 | Claude Code | "Faça uma auditoria avaliativa com base nos requisitos do documento, com foco em Dynamic Programming" | Conferir a entrega contra os slides 34 e 35 do briefing da GS | Checklist por critério e nota estimada. Apontou capa com placeholders, repositório inexistente e falta do `prompts.md` |
| 4 | Claude Code | "Organize a estrutura do repositório para prosseguirmos" | Organizar o repositório no GitHub | Pastas `dynamic-programming/` e `relatorio-dp/` na raiz, README com a Ficha da CitizenTech, `.gitignore` e este arquivo |
| 5 | Claude Code | Preencher os pontos em aberto usando a documentação do projeto como base | Alinhar o repositório à documentação da equipe | Indicadores de impacto da Ficha; três ajustes de texto no relatório e no notebook (garantia de ótimo na distância discretizada, dados de Data Science "na versão integrada" e justificativa do Bellman-Ford) |
| 6 | Claude Code | "Realize essas etapas pendentes" | Validar e fechar a entrega | Instalou Python 3.12 e as dependências, rodou os 13 testes (todos passaram), executou o notebook do início ao fim sem erro e gerou o PDF de novo (4 páginas, capa com equipe, RMs e link) |
