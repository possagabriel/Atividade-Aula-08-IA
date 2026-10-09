# Fase 1 - Matriz de Decisão

Como as respostas da entrevista ativam as regras de cada trilha.
Pontos positivos somam à trilha; pontos negativos (penalidades) existem para desambiguar trilhas parecidas.

## Variáveis da entrevista

| Variável | Valores |
|---|---|
| `matematica` | Baixa, Média, Alta |
| `atuacao` | algoritmos, layouts, servidores, dados_brutos, seguranca, automacao, planejar_infra, apps_celular, qualidade, negocio |
| `linguagem` | python, javascript, linux_redes, sql, java_csharp, mobile_nativo, nenhuma |
| `entrega` | produto_usuario, regras_sistema, infraestrutura, seguranca, insights, qualidade, negocio |
| `dados_foco` | modelos, pipelines, nao_aplica |
| `plataforma` | web, celular, api, nuvem, indiferente |
| `comunicacao` | Baixa, Média, Alta |

## Nível 1: perfis derivados (salience 10)

| Regra | Condição | Fato derivado |
|---|---|---|
| D1 | matematica=Alta e atuacao ∈ {dados_brutos, algoritmos} | Perfil analítico |
| D2a / D2b | atuacao ∈ {automacao, planejar_infra} / entrega=infraestrutura | Perfil infra |
| D3a / D3b | atuacao=layouts / entrega=produto_usuario e plataforma=web | Perfil visual |
| D4 | comunicacao=Alta e entrega=negocio | Perfil negócios |
| D5a / D5b | atuacao=dados_brutos / entrega=insights | Perfil dados |
| D6a / D6b | atuacao=seguranca / entrega=seguranca | Perfil defensivo |
| D7 | linguagem=nenhuma e matematica=Baixa | Perfil iniciante |

## Nível 2: pontuação por trilha (salience 0)

| Trilha | Regra | Condição | Pts |
|---|---|---|---|
| Back-end | R01 | atuacao ∈ {algoritmos, servidores} e plataforma=api | +4 |
| | R02 | atuacao ∈ {algoritmos, servidores} e linguagem ∈ {python, sql, java_csharp} | +3 |
| | R03 | entrega=regras_sistema | +4 |
| | R04 | atuacao=servidores | +3 |
| Front-end & UX | R05 | atuacao=layouts | +5 |
| | R06 | linguagem=javascript e plataforma=web | +3 |
| | R07 | entrega=produto_usuario e plataforma=web | +3 |
| | R08 | Perfil visual e linguagem=javascript | +2 |
| Ciência de Dados & ML | R09 | matematica=Alta e dados_foco=modelos | +6 |
| | R10 | atuacao=dados_brutos e dados_foco=modelos | +3 |
| | R11 | Perfil analítico + Perfil dados + dados_foco=modelos + python | +3 |
| | R12 | entrega=insights e dados_foco=modelos | +2 |
| | R13 | matematica=Baixa | -4 |
| | R14 | dados_foco=pipelines | -3 |
| | R15 | Perfil iniciante | -3 |
| Engenharia de Dados | R16 | dados_foco=pipelines | +6 |
| | R17 | atuacao=dados_brutos, dados_foco=pipelines, linguagem ∈ {sql, python} | +3 |
| | R18 | Perfil dados + Perfil infra + dados_foco=pipelines | +3 |
| | R19 | dados_foco=modelos | -3 |
| Cibersegurança | R20 | atuacao=seguranca | +6 |
| | R21 | entrega=seguranca | +4 |
| | R22 | Perfil defensivo e linguagem=linux_redes | +3 |
| | R23 | matematica=Alta e atuacao=seguranca | +1 |
| DevOps & SRE | R24 | atuacao=automacao | +6 |
| | R25 | atuacao=automacao e linguagem=linux_redes | +3 |
| | R26 | entrega=infraestrutura e atuacao ∈ {automacao, servidores} | +2 |
| Nuvem | R27 | atuacao=planejar_infra | +6 |
| | R28 | plataforma=nuvem | +4 |
| | R29 | entrega=infraestrutura, plataforma=nuvem, comunicacao ≠ Baixa | +2 |
| Mobile | R30 | atuacao=apps_celular | +6 |
| | R31 | plataforma=celular | +5 |
| | R32 | linguagem=mobile_nativo | +3 |
| | R33 | plataforma=celular e entrega=produto_usuario | +2 |
| QA | R34 | atuacao=qualidade | +6 |
| | R35 | entrega=qualidade | +4 |
| | R36 | atuacao=qualidade e linguagem ∈ {python, javascript, java_csharp} | +2 |
| Product Mgmt | R37 | atuacao=negocio | +6 |
| | R38 | entrega=negocio | +4 |
| | R39 | Perfil negócios | +2 |
| | R40 | linguagem=nenhuma e entrega=negocio | +1 |

## Decisão final (R99, salience -100)

Ordena o placar por: (1) pontos, (2) nº de regras positivas disparadas, (3) ordem fixa de desempate.
A margem entre 1º e 2º lugar define o grau de certeza: >= 5 Alta, >= 2 Média, senão Baixa.

## Desambiguação Cientista de Dados x Engenheiro de Dados

A pergunta `dados_foco` é a chave: "modelos" dá pontos a DS (R09-R12) e penaliza DE (R19);
"pipelines" dá pontos a DE (R16-R18) e penaliza DS (R14). Persona Karen nos testes: matemática
alta + Python + dados brutos, mas foco em pipelines, resulta em DE.
