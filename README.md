# Consultor Inteligente de Carreiras em TI

Sistema Especialista baseado em regras (Python + **Experta** + **Streamlit**) que entrevista o usuário
e recomenda 1 entre 10 trilhas de carreira em TI, justificando com as regras disparadas.

Disciplina de Inteligência Artificial, UNIPAC Barbacena, Ciência da Computação.

## Trilhas
Back-end, Front-end & UI/UX, Ciência de Dados e ML, Engenharia de Dados, Cibersegurança,
DevOps & SRE, Computação em Nuvem, Mobile, QA, Gestão de Produtos.

## Estrutura
```
engine.py           # Fatos, base de conhecimento (40 regras) e motor Experta
app.py              # Interface web (Streamlit)
test_personas.py    # Fase 4: 12 personas de validação
matriz_decisao.md   # Fase 1: matriz de decisão
requirements.txt
```

## Instalação e execução
Requer Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testes (personas)
```bash
python test_personas.py          # tabela com esperado x obtido
pytest -v                        # opcional
```

## Como funciona
1. A entrevista é dinâmica: a pergunta sobre foco em dados só aparece para quem demonstrou interesse em dados, e quem quer apps de celular não precisa escolher plataforma. As respostas viram um fato `Resposta`.
2. **Nível 1** (D1..D7): regras derivam fatos `Perfil` (analítico, infra, visual, negócios, dados, defensivo, iniciante).
3. **Nível 2** (R01..R40): regras cruzam respostas e perfis e pontuam as trilhas (com penalidades para evitar ambiguidade).
4. **Decisão** (R99, menor salience): escolhe a trilha de maior pontuação e exibe as regras que a sustentam.

## Observação sobre o Experta no Python 3.10+
O Experta 1.9.x usa uma versão antiga do `frozendict` que depende de `collections.Mapping` (removido no Python 3.10).
O `engine.py` já inclui um pequeno shim no início do arquivo que resolve isso, então basta o `pip install -r requirements.txt`.
## Validação com personas (Fase 4)

`python test_personas.py` executa 12 personas e compara a trilha esperada com a obtida.

| Persona | Matemática | Atuação | Linguagem | Entrega | Foco em dados | Esperada | Obtida |
|---|---|---|---|---|---|---|---|
| Ana - perfil analítico | Alta | Analisar dados brutos | Python | Conhecimento extraído dos dados | Treinar modelos, prever e fazer experimentos estatísticos | DS | DS |
| Bruno - perfil infra/segurança | Média | Garantir segurança e procurar vulnerabilidades | Linux / Redes | A segurança contra invasões | Dados não são meu foco | SEC | SEC |
| Carla - perfil visual/front-end | Baixa | Criar layouts visuais e interfaces | JavaScript | O produto final que o usuário toca e usa | Dados não são meu foco | FE | FE |
| Diego - perfil negócios/produto | Média | Definir o que construir: usuários, prioridades e negócio | Nenhuma / Iniciante | A estratégia: construir o produto certo | Dados não são meu foco | PM | PM |
| Elisa - pipelines e Data Lake | Média | Analisar dados brutos | SQL / Bancos de dados | A infraestrutura que sustenta o sistema | Construir pipelines e arquitetura que movem e armazenam dados | DE | DE |
| Fábio - APIs e regras de negócio | Média | Lidar com servidores, APIs e bancos de dados | Java / C# | O motor do sistema: regras de negócio e dados por trás | Dados não são meu foco | BE | BE |
| Gabi - automação e CI/CD | Média | Automatizar processos, builds e deploys | Linux / Redes | A infraestrutura que sustenta o sistema | Dados não são meu foco | DO | DO |
| Hugo - arquitetura na nuvem | Média | Planejar e desenhar infraestrutura escalável | Linux / Redes | A infraestrutura que sustenta o sistema | Dados não são meu foco | CL | CL |
| Iara - apps de celular | Média | Construir aplicativos para celular | Dart / Kotlin / Swift | O produto final que o usuário toca e usa | Dados não são meu foco | MO | MO |
| João - qualidade e testes | Média | Testar software e caçar bugs | Python | A confiança de que o software funciona | Dados não são meu foco | QA | QA |
| Karen - matemática alta, mas ama pipelines (DE, não DS) | Alta | Analisar dados brutos | Python | Conhecimento extraído dos dados | Construir pipelines e arquitetura que movem e armazenam dados | DE | DE |
| Leo - JS + celular (MO, não FE) | Média | Construir aplicativos para celular | JavaScript | O produto final que o usuário toca e usa | Dados não são meu foco | MO | MO |
