"""Regressões de ambiguidade e do fluxo interativo Streamlit."""
import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from engine import diagnosticar


def respostas(linguagem="python"):
    return dict(matematica="Média", atuacao="layouts", linguagem=linguagem,
                entrega="negocio", dados_foco="nao_aplica",
                plataforma="indiferente", comunicacao="Baixa")


@pytest.mark.parametrize("linguagem", ["python", "nenhuma"])
def test_ambiguidades_pedem_preferencia(linguagem):
    r = diagnosticar(respostas(linguagem))
    assert r["desempate_pendente"]
    assert r["recomendacao"] is None
    assert set(r["candidatas"]) == {"FE", "PM"}
    for trilha in r["candidatas"]:
        escolhido = diagnosticar(respostas(linguagem), preferencia=trilha)
        assert escolhido["recomendacao"] == trilha
        assert not escolhido["desempate_pendente"]
        assert escolhido["ranking"] == r["ranking"]
        assert escolhido["motivos"]


def test_preferencia_fora_das_candidatas_e_rejeitada():
    with pytest.raises(ValueError):
        diagnosticar(respostas(), preferencia="DS")


def test_interface_desempata_e_invalida_resultado_antigo():
    app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
    assert not app.exception
    app.radio(key="atuacao").set_value("layouts")
    app.radio(key="entrega").set_value("negocio")
    app.select_slider(key="comunicacao").set_value("Baixa")
    app.run()
    app.button[0].click().run()
    assert not app.success
    assert app.radio(key="preferencia_desempate").value is None
    app.radio(key="preferencia_desempate").set_value("PM").run()
    assert "Gestão de Produtos" in app.success[0].value
    assert not app.exception
    app.radio(key="atuacao").set_value("qualidade").run()
    assert not app.success
    app.button[0].click().run()
    assert not app.exception
    assert "Qualidade" in app.success[0].value
    app.radio(key="atuacao").set_value("layouts").run()
    app.button[0].click().run()
    assert app.radio(key="preferencia_desempate").value is None
