"""Fase 3 - Interface web (Streamlit) integrada ao motor Experta.

Entrevista dinâmica: as perguntas se adaptam às respostas anteriores.
  - A pergunta sobre foco em dados só aparece se o usuário demonstrou interesse em dados.
  - A pergunta sobre plataforma é pulada para quem quer construir apps de celular.

Executar:  streamlit run app.py
"""
import streamlit as st

from engine import (
    ATUACAO, COMUNICACAO, DADOS_FOCO, DESCRICOES, ENTREGA, LINGUAGEM, MATEMATICA,
    PLATAFORMA, TRILHAS, diagnosticar,
)

st.set_page_config(page_title="Consultor de Carreiras em TI", page_icon="🧭", layout="centered")

st.title("🧭 Consultor Inteligente de Carreiras em TI")
st.caption(
    "Sistema Especialista baseado em regras (Experta, encadeamento para frente). "
    "Responda a entrevista e descubra qual das 10 trilhas combina mais com você."
)

st.subheader("Entrevista")

# Contador para numerar as perguntas conforme elas vão aparecendo
n = 0


def proxima():
    global n
    n += 1
    return n


matematica = st.select_slider(
    f"{proxima()}. Qual sua afinidade com matemática e estatística?",
    options=MATEMATICA, value="Média", key="matematica",
)
atuacao = st.radio(
    f"{proxima()}. O que você mais gostaria de fazer no dia a dia?",
    list(ATUACAO), format_func=ATUACAO.get, key="atuacao",
)
linguagem = st.radio(
    f"{proxima()}. Linguagem/ferramenta de maior afinidade atual:",
    list(LINGUAGEM), format_func=LINGUAGEM.get, key="linguagem",
)
entrega = st.radio(
    f"{proxima()}. Que tipo de entrega de valor você prefere?",
    list(ENTREGA), format_func=ENTREGA.get, key="entrega",
)

# --- Pergunta condicional 1: só pergunta sobre foco em dados se houver interesse em dados
if atuacao == "dados_brutos" or entrega == "insights":
    dados_foco = st.radio(
        f"{proxima()}. Já que você curte dados: o que mais te empolgaria?",
        ["modelos", "pipelines"], format_func=DADOS_FOCO.get, key="dados_foco",
    )
else:
    dados_foco = "nao_aplica"

# --- Pergunta condicional 2: quem quer apps de celular não precisa escolher plataforma
if atuacao == "apps_celular":
    plataforma = "celular"
    st.caption("📱 Como você quer construir apps, considerei o celular como plataforma-alvo.")
else:
    plataforma = st.radio(
        f"{proxima()}. Em que plataforma você prefere atuar?",
        list(PLATAFORMA), format_func=PLATAFORMA.get, index=len(PLATAFORMA) - 1, key="plataforma",
    )

comunicacao = st.select_slider(
    f"{proxima()}. Quanto você gosta de conversar com pessoas/áreas diferentes no trabalho?",
    options=COMUNICACAO, value="Média", key="comunicacao",
)

if st.button("Descobrir minha trilha", type="primary"):
    respostas = dict(
        matematica=matematica, atuacao=atuacao, linguagem=linguagem, entrega=entrega,
        dados_foco=dados_foco, plataforma=plataforma, comunicacao=comunicacao,
    )
    r = diagnosticar(respostas)

    st.divider()
    if not r["recomendacao"]:
        st.warning("Não foi possível chegar a uma recomendação com essas respostas. Tente variar as escolhas.")
        st.stop()

    st.success(f"### Trilha recomendada: {r['nome']}")
    st.write(DESCRICOES[r["recomendacao"]])
    st.write(f"**Grau de certeza:** {r['certeza']}")

    if r["margem"] is not None and r["margem"] < 2:
        segunda = r["ranking"][1][0]
        st.info(f"Vale olhar também: **{TRILHAS[segunda]}** (pontuação muito próxima).")

    st.subheader("Por que essa trilha? (regras disparadas)")
    for regra, _trilha, pts, motivo in r["motivos"]:
        st.markdown(f"- **{regra}** ({pts:+d}): {motivo}")

    if r["perfis"]:
        with st.expander("Perfis intermediários inferidos (regras de nível 1)"):
            for regra, perfil, motivo in r["perfis"]:
                st.markdown(f"- **{regra}** → perfil *{perfil}*: {motivo}")

    with st.expander("Ranking completo das 10 trilhas"):
        st.bar_chart({TRILHAS[t]: pts for t, pts in r["ranking"]}, horizontal=True)

    with st.expander("Todas as regras de pontuação disparadas"):
        for regra, trilha, pts, motivo in r["disparos"]:
            st.markdown(f"- **{regra}** → {TRILHAS[trilha]} ({pts:+d}): {motivo}")
