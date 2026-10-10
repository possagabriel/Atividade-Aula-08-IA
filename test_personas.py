"""
Fase 4 - Validação com Personas de Teste.

Executar:  python test_personas.py      (ou: pytest -v)
As 4 primeiras são as personas exigidas no enunciado; as demais cobrem as outras
trilhas e os casos de ambiguidade (Cientista de Dados x Engenheiro de Dados).
"""
from engine import diagnosticar, TRILHAS

PERSONAS = [
    # ---- As 4 personas do enunciado ----------------------------------------
    {
        "nome": "Ana - perfil analítico",
        "esperado": "DS",
        "respostas": dict(matematica="Alta", atuacao="dados_brutos", linguagem="python",
                          entrega="insights", dados_foco="modelos", plataforma="indiferente",
                          comunicacao="Média"),
    },
    {
        "nome": "Bruno - perfil infra/segurança",
        "esperado": "SEC",
        "respostas": dict(matematica="Média", atuacao="seguranca", linguagem="linux_redes",
                          entrega="seguranca", dados_foco="nao_aplica", plataforma="indiferente",
                          comunicacao="Baixa"),
    },
    {
        "nome": "Carla - perfil visual/front-end",
        "esperado": "FE",
        "respostas": dict(matematica="Baixa", atuacao="layouts", linguagem="javascript",
                          entrega="produto_usuario", dados_foco="nao_aplica", plataforma="web",
                          comunicacao="Alta"),
    },
    {
        "nome": "Diego - perfil negócios/produto",
        "esperado": "PM",
        "respostas": dict(matematica="Média", atuacao="negocio", linguagem="nenhuma",
                          entrega="negocio", dados_foco="nao_aplica", plataforma="indiferente",
                          comunicacao="Alta"),
    },
    # ---- Demais trilhas ------------------------------------------------------
    {
        "nome": "Elisa - pipelines e Data Lake",
        "esperado": "DE",
        "respostas": dict(matematica="Média", atuacao="dados_brutos", linguagem="sql",
                          entrega="infraestrutura", dados_foco="pipelines", plataforma="indiferente",
                          comunicacao="Média"),
    },
    {
        "nome": "Fábio - APIs e regras de negócio",
        "esperado": "BE",
        "respostas": dict(matematica="Média", atuacao="servidores", linguagem="java_csharp",
                          entrega="regras_sistema", dados_foco="nao_aplica", plataforma="api",
                          comunicacao="Baixa"),
    },
    {
        "nome": "Gabi - automação e CI/CD",
        "esperado": "DO",
        "respostas": dict(matematica="Média", atuacao="automacao", linguagem="linux_redes",
                          entrega="infraestrutura", dados_foco="nao_aplica", plataforma="indiferente",
                          comunicacao="Média"),
    },
    {
        "nome": "Hugo - arquitetura na nuvem",
        "esperado": "CL",
        "respostas": dict(matematica="Média", atuacao="planejar_infra", linguagem="linux_redes",
                          entrega="infraestrutura", dados_foco="nao_aplica", plataforma="nuvem",
                          comunicacao="Alta"),
    },
    {
        "nome": "Iara - apps de celular",
        "esperado": "MO",
        "respostas": dict(matematica="Média", atuacao="apps_celular", linguagem="mobile_nativo",
                          entrega="produto_usuario", dados_foco="nao_aplica", plataforma="celular",
                          comunicacao="Média"),
    },
    {
        "nome": "João - qualidade e testes",
        "esperado": "QA",
        "respostas": dict(matematica="Média", atuacao="qualidade", linguagem="python",
                          entrega="qualidade", dados_foco="nao_aplica", plataforma="indiferente",
                          comunicacao="Média"),
    },
    # ---- Ambiguidade DS x DE: mesma afinidade alta com dados/Python -----------
    {
        "nome": "Karen - matemática alta, mas ama pipelines (DE, não DS)",
        "esperado": "DE",
        "respostas": dict(matematica="Alta", atuacao="dados_brutos", linguagem="python",
                          entrega="insights", dados_foco="pipelines", plataforma="indiferente",
                          comunicacao="Média"),
    },
    {
        "nome": "Leo - JS + celular (MO, não FE)",
        "esperado": "MO",
        "respostas": dict(matematica="Média", atuacao="apps_celular", linguagem="javascript",
                          entrega="produto_usuario", dados_foco="nao_aplica", plataforma="celular",
                          comunicacao="Média"),
    },
]


def test_personas():
    falhas = []
    for p in PERSONAS:
        r = diagnosticar(p["respostas"])
        if r["recomendacao"] != p["esperado"]:
            falhas.append((p["nome"], p["esperado"], r["recomendacao"], r["ranking"][:3]))
    assert not falhas, f"Personas com recomendação incorreta: {falhas}"


if __name__ == "__main__":
    ok = 0
    print(f"{'Persona':58} {'Esperado':9} {'Obtido':9} Placar (top 2)   Resultado")
    print("-" * 112)
    for p in PERSONAS:
        r = diagnosticar(p["respostas"])
        passou = r["recomendacao"] == p["esperado"]
        ok += passou
        top = ", ".join(f"{t}={s}" for t, s in r["ranking"][:2])
        print(f"{p['nome']:58} {p['esperado']:9} {str(r['recomendacao']):9} {top:16} {'OK' if passou else 'FALHOU'}")
    print("-" * 112)
    print(f"{ok}/{len(PERSONAS)} personas corretas")
    raise SystemExit(0 if ok == len(PERSONAS) else 1)
