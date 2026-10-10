"""
Consultor Inteligente de Carreiras em TI - Base de Conhecimento e Motor de Inferência.

Sistema Especialista baseado em regras (encadeamento para frente) usando Experta.

Fluxo de inferência:
  1. As respostas da entrevista entram como fatos `Resposta`.
  2. Regras de NÍVEL 1 (D1..D7, salience alta) derivam fatos intermediários `Perfil`.
  3. Regras de NÍVEL 2 (R01..R40) cruzam respostas + perfis e pontuam as trilhas
     (pontos positivos e penalidades para desambiguar trilhas parecidas).
  4. Regra final (salience mais baixa) soma o placar e declara a recomendação.
"""

# --- Compatibilidade: Experta 1.9.x depende de frozendict antigo, que usa
# --- collections.Mapping (removido no Python 3.10+). Este shim resolve.
import collections
import collections.abc

for _nome in ("Mapping", "MutableMapping", "Sequence", "Iterable", "Callable"):
    if not hasattr(collections, _nome):
        setattr(collections, _nome, getattr(collections.abc, _nome))

from experta import Fact, KnowledgeEngine, Rule, P  # noqa: E402

# ----------------------------------------------------------------------------
# Vocabulário da entrevista (chave interna -> texto exibido)
# ----------------------------------------------------------------------------
TRILHAS = {
    "BE": "Desenvolvimento Back-end",
    "FE": "Desenvolvimento Front-end & UI/UX",
    "DS": "Ciência de Dados e Machine Learning",
    "DE": "Engenharia de Dados",
    "SEC": "Cibersegurança (Security / Pentesting)",
    "DO": "DevOps & SRE",
    "CL": "Computação em Nuvem (Cloud Architecture)",
    "MO": "Desenvolvimento Mobile",
    "QA": "Engenharia de Qualidade e Testes (QA)",
    "PM": "Gestão de Produtos (Product Management)",
}

DESCRICOES = {
    "BE": "Lógica de servidores, construção de APIs, regras de negócio e bancos de dados.",
    "FE": "Interfaces web responsivas, experiência do usuário e frameworks reativos.",
    "DS": "Estatística, modelagem preditiva, análise de grandes massas de dados e IA.",
    "DE": "Arquitetura de dados, pipelines (ETL/ELT) e infraestrutura para Data Lakes.",
    "SEC": "Defesa cibernética, análise de vulnerabilidades, criptografia e redes seguras.",
    "DO": "Automação de processos, CI/CD e contêineres.",
    "CL": "Planejamento, migração e gestão de infraestruturas escaláveis (AWS/Azure/GCP).",
    "MO": "Ecossistema de dispositivos móveis (nativo ou Flutter/React Native).",
    "QA": "Testes automatizados, confiabilidade de software e processos de qualidade.",
    "PM": "Ponte entre negócio, design e desenvolvimento, métodos ágeis e priorização.",
}

MATEMATICA = ["Baixa", "Média", "Alta"]

ATUACAO = {
    "algoritmos": "Escrever algoritmos e lógica de programação",
    "layouts": "Criar layouts visuais e interfaces",
    "servidores": "Lidar com servidores, APIs e bancos de dados",
    "dados_brutos": "Analisar dados brutos",
    "seguranca": "Garantir segurança e procurar vulnerabilidades",
    "automacao": "Automatizar processos, builds e deploys",
    "planejar_infra": "Planejar e desenhar infraestrutura escalável",
    "apps_celular": "Construir aplicativos para celular",
    "qualidade": "Testar software e caçar bugs",
    "negocio": "Definir o que construir: usuários, prioridades e negócio",
}

LINGUAGEM = {
    "python": "Python",
    "javascript": "JavaScript",
    "linux_redes": "Linux / Redes",
    "sql": "SQL / Bancos de dados",
    "java_csharp": "Java / C#",
    "mobile_nativo": "Dart / Kotlin / Swift",
    "nenhuma": "Nenhuma / Iniciante",
}

ENTREGA = {
    "produto_usuario": "O produto final que o usuário toca e usa",
    "regras_sistema": "O motor do sistema: regras de negócio e dados por trás",
    "infraestrutura": "A infraestrutura que sustenta o sistema",
    "seguranca": "A segurança contra invasões",
    "insights": "Conhecimento extraído dos dados",
    "qualidade": "A confiança de que o software funciona",
    "negocio": "A estratégia: construir o produto certo",
}

DADOS_FOCO = {
    "modelos": "Treinar modelos, prever e fazer experimentos estatísticos",
    "pipelines": "Construir pipelines e arquitetura que movem e armazenam dados",
    "nao_aplica": "Dados não são meu foco",
}

PLATAFORMA = {
    "web": "Web (navegador)",
    "celular": "Celular (Android/iOS)",
    "api": "Servidor / APIs",
    "nuvem": "Nuvem (AWS/Azure/GCP)",
    "indiferente": "Tanto faz",
}

COMUNICACAO = ["Baixa", "Média", "Alta"]  # gosto de conversar com pessoas/stakeholders

# Ordem de desempate (usada só se pontos e nº de regras empatarem)
ORDEM_DESEMPATE = ["BE", "FE", "DS", "DE", "SEC", "DO", "CL", "MO", "QA", "PM"]


# ----------------------------------------------------------------------------
# Classes de fatos
# ----------------------------------------------------------------------------
class Resposta(Fact):
    """Respostas da entrevista (fatos de entrada)."""


class Perfil(Fact):
    """Fatos intermediários derivados pelas regras de nível 1."""


class Fase(Fact):
    """Marcador de fase: dispara a regra final de decisão."""


def EM(*valores):
    """Casa se o valor do campo estiver no conjunto informado."""
    return P(lambda v: v in valores)


def DIFERENTE(valor):
    return P(lambda v: v != valor)


# ----------------------------------------------------------------------------
# Motor de inferência
# ----------------------------------------------------------------------------
class ConsultorCarreiras(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.placar = {t: 0 for t in TRILHAS}
        self.disparos = []          # (id_regra, trilha, pontos, motivo)
        self.perfis = []            # perfis derivados (nível 1)
        self.ranking = []           # [(trilha, pontos)]
        self.recomendacao = None    # sigla da trilha vencedora

    # utilitário: registra pontuação + justificativa
    def pontuar(self, trilha, pontos, regra, motivo):
        self.placar[trilha] += pontos
        self.disparos.append((regra, trilha, pontos, motivo))

    # ======================= NÍVEL 1: perfis derivados ========================
    @Rule(Resposta(matematica="Alta", atuacao=EM("dados_brutos", "algoritmos")), salience=10)
    def d1_perfil_analitico(self):
        self.perfis.append(("D1", "analítico", "Matemática alta + gosto por dados/algoritmos"))
        self.declare(Perfil(tipo="analitico"))

    @Rule(Resposta(atuacao=EM("automacao", "planejar_infra")), salience=10)
    def d2a_perfil_infra(self):
        self.perfis.append(("D2a", "infraestrutura", "Rotina voltada a automação/planejamento de infra"))
        self.declare(Perfil(tipo="infra"))

    @Rule(Resposta(entrega="infraestrutura"), salience=10)
    def d2b_perfil_infra(self):
        self.perfis.append(("D2b", "infraestrutura", "Valoriza entregar a infraestrutura que sustenta o sistema"))
        self.declare(Perfil(tipo="infra"))

    @Rule(Resposta(atuacao="layouts"), salience=10)
    def d3a_perfil_visual(self):
        self.perfis.append(("D3a", "visual", "Prefere criar layouts visuais"))
        self.declare(Perfil(tipo="visual"))

    @Rule(Resposta(entrega="produto_usuario", plataforma="web"), salience=10)
    def d3b_perfil_visual(self):
        self.perfis.append(("D3b", "visual", "Quer entregar o produto final na web"))
        self.declare(Perfil(tipo="visual"))

    @Rule(Resposta(comunicacao="Alta", entrega="negocio"), salience=10)
    def d4_perfil_negocio(self):
        self.perfis.append(("D4", "negócios", "Comunicação alta + foco em estratégia de produto"))
        self.declare(Perfil(tipo="negocio"))

    @Rule(Resposta(atuacao="dados_brutos"), salience=10)
    def d5a_perfil_dados(self):
        self.perfis.append(("D5a", "dados", "Gosta de analisar dados brutos"))
        self.declare(Perfil(tipo="dados"))

    @Rule(Resposta(entrega="insights"), salience=10)
    def d5b_perfil_dados(self):
        self.perfis.append(("D5b", "dados", "Valoriza extrair conhecimento dos dados"))
        self.declare(Perfil(tipo="dados"))

    @Rule(Resposta(atuacao="seguranca"), salience=10)
    def d6a_perfil_defensivo(self):
        self.perfis.append(("D6a", "segurança", "Prefere atuar com segurança no dia a dia"))
        self.declare(Perfil(tipo="defensivo"))

    @Rule(Resposta(entrega="seguranca"), salience=10)
    def d6b_perfil_defensivo(self):
        self.perfis.append(("D6b", "segurança", "Valoriza entregar segurança contra invasões"))
        self.declare(Perfil(tipo="defensivo"))

    @Rule(Resposta(linguagem="nenhuma", matematica="Baixa"), salience=10)
    def d7_perfil_iniciante(self):
        self.perfis.append(("D7", "iniciante", "Sem linguagem de afinidade e matemática baixa"))
        self.declare(Perfil(tipo="iniciante"))

    # ======================= NÍVEL 2: pontuação das trilhas ===================
    # ---- Back-end -----------------------------------------------------------
    @Rule(Resposta(atuacao=EM("algoritmos", "servidores"), plataforma="api"))
    def r01_be(self):
        self.pontuar("BE", 4, "R01", "Gosta de lógica/servidores e quer construir APIs")

    @Rule(Resposta(atuacao=EM("algoritmos", "servidores"), linguagem=EM("python", "sql", "java_csharp")))
    def r02_be(self):
        self.pontuar("BE", 3, "R02", "Linguagem de afinidade típica de back-end (Python/SQL/Java/C#) + lógica de servidor")

    @Rule(Resposta(entrega="regras_sistema"))
    def r03_be(self):
        self.pontuar("BE", 4, "R03", "Quer entregar o motor do sistema: regras de negócio e dados")

    @Rule(Resposta(atuacao="servidores"))
    def r04_be(self):
        self.pontuar("BE", 3, "R04", "Rotina diária com servidores, APIs e bancos de dados")

    # ---- Front-end & UX -----------------------------------------------------
    @Rule(Resposta(atuacao="layouts"))
    def r05_fe(self):
        self.pontuar("FE", 5, "R05", "Prefere criar layouts visuais e interfaces")

    @Rule(Resposta(linguagem="javascript", plataforma="web"))
    def r06_fe(self):
        self.pontuar("FE", 3, "R06", "JavaScript + plataforma web (ecossistema de frameworks reativos)")

    @Rule(Resposta(entrega="produto_usuario", plataforma="web"))
    def r07_fe(self):
        self.pontuar("FE", 3, "R07", "Quer entregar o produto que o usuário usa, no navegador")

    @Rule(Perfil(tipo="visual"), Resposta(linguagem="javascript"))
    def r08_fe(self):
        self.pontuar("FE", 2, "R08", "Perfil visual com JavaScript como ferramenta")

    # ---- Ciência de Dados & ML ---------------------------------------------
    @Rule(Resposta(matematica="Alta", dados_foco="modelos"))
    def r09_ds(self):
        self.pontuar("DS", 6, "R09", "Afinidade alta com matemática/estatística e interesse em modelagem")

    @Rule(Resposta(atuacao="dados_brutos", dados_foco="modelos"))
    def r10_ds(self):
        self.pontuar("DS", 3, "R10", "Analisa dados brutos com foco em modelos preditivos")

    @Rule(Perfil(tipo="analitico"), Perfil(tipo="dados"), Resposta(dados_foco="modelos", linguagem="python"))
    def r11_ds(self):
        self.pontuar("DS", 3, "R11", "Perfil analítico + dados + Python + modelagem (combinação típica de DS)")

    @Rule(Resposta(entrega="insights", dados_foco="modelos"))
    def r12_ds(self):
        self.pontuar("DS", 2, "R12", "Valor entregue como conhecimento/predições extraídos dos dados")

    @Rule(Resposta(matematica="Baixa"))
    def r13_ds_penal(self):
        self.pontuar("DS", -4, "R13", "Matemática/estatística baixa reduz a aderência a DS e ML")

    @Rule(Resposta(dados_foco="pipelines"))
    def r14_ds_penal(self):
        self.pontuar("DS", -3, "R14", "Foco em pipelines/arquitetura (e não em modelos) afasta de DS")

    @Rule(Perfil(tipo="iniciante"))
    def r15_ds_penal(self):
        self.pontuar("DS", -3, "R15", "Perfil iniciante sem base de exatas: DS exige fundamentos pesados")

    # ---- Engenharia de Dados -----------------------------------------------
    @Rule(Resposta(dados_foco="pipelines"))
    def r16_de(self):
        self.pontuar("DE", 6, "R16", "Quer construir pipelines e arquitetura de dados (ETL/ELT)")

    @Rule(Resposta(atuacao="dados_brutos", dados_foco="pipelines", linguagem=EM("sql", "python")))
    def r17_de(self):
        self.pontuar("DE", 3, "R17", "Dados brutos + pipelines + SQL/Python (ferramentas centrais de DE)")

    @Rule(Perfil(tipo="dados"), Perfil(tipo="infra"), Resposta(dados_foco="pipelines"))
    def r18_de(self):
        self.pontuar("DE", 3, "R18", "Perfil dados + infraestrutura: base de Data Lakes e pipelines")

    @Rule(Resposta(dados_foco="modelos"))
    def r19_de_penal(self):
        self.pontuar("DE", -3, "R19", "Foco em modelagem/experimentos (e não em pipelines) afasta de DE")

    # ---- Cibersegurança -----------------------------------------------------
    @Rule(Resposta(atuacao="seguranca"))
    def r20_sec(self):
        self.pontuar("SEC", 6, "R20", "Rotina diária voltada a segurança e vulnerabilidades")

    @Rule(Resposta(entrega="seguranca"))
    def r21_sec(self):
        self.pontuar("SEC", 4, "R21", "Valor entregue: segurança contra invasões")

    @Rule(Perfil(tipo="defensivo"), Resposta(linguagem="linux_redes"))
    def r22_sec(self):
        self.pontuar("SEC", 3, "R22", "Perfil de segurança + Linux/Redes (base de pentest e defesa de redes)")

    @Rule(Resposta(matematica="Alta", atuacao="seguranca"))
    def r23_sec(self):
        self.pontuar("SEC", 1, "R23", "Matemática alta ajuda em criptografia")

    # ---- DevOps & SRE -------------------------------------------------------
    @Rule(Resposta(atuacao="automacao"))
    def r24_do(self):
        self.pontuar("DO", 6, "R24", "Rotina voltada a automatizar builds, deploys e processos (CI/CD)")

    @Rule(Resposta(atuacao="automacao", linguagem="linux_redes"))
    def r25_do(self):
        self.pontuar("DO", 3, "R25", "Automação com Linux/Redes (contêineres, scripts, operação)")

    @Rule(Resposta(entrega="infraestrutura", atuacao=EM("automacao", "servidores")))
    def r26_do(self):
        self.pontuar("DO", 2, "R26", "Entrega infraestrutura confiável, operando servidores/automação")

    # ---- Computação em Nuvem ------------------------------------------------
    @Rule(Resposta(atuacao="planejar_infra"))
    def r27_cl(self):
        self.pontuar("CL", 6, "R27", "Gosta de planejar/desenhar infraestrutura escalável")

    @Rule(Resposta(plataforma="nuvem"))
    def r28_cl(self):
        self.pontuar("CL", 4, "R28", "Plataforma-alvo é a nuvem (AWS/Azure/GCP)")

    @Rule(Resposta(entrega="infraestrutura", plataforma="nuvem", comunicacao=DIFERENTE("Baixa")))
    def r29_cl(self):
        self.pontuar("CL", 2, "R29", "Infra na nuvem + diálogo com times: perfil de arquiteto")

    # ---- Mobile ---------------------------------------------------------------
    @Rule(Resposta(atuacao="apps_celular"))
    def r30_mo(self):
        self.pontuar("MO", 6, "R30", "Quer construir aplicativos para celular")

    @Rule(Resposta(plataforma="celular"))
    def r31_mo(self):
        self.pontuar("MO", 5, "R31", "Plataforma-alvo é o celular (Android/iOS)")

    @Rule(Resposta(linguagem="mobile_nativo"))
    def r32_mo(self):
        self.pontuar("MO", 3, "R32", "Linguagem de afinidade é de mobile (Dart/Kotlin/Swift)")

    @Rule(Resposta(plataforma="celular", entrega="produto_usuario"))
    def r33_mo(self):
        self.pontuar("MO", 2, "R33", "Quer entregar ao usuário final direto no celular")

    # ---- QA -------------------------------------------------------------------
    @Rule(Resposta(atuacao="qualidade"))
    def r34_qa(self):
        self.pontuar("QA", 6, "R34", "Rotina voltada a testar software e caçar bugs")

    @Rule(Resposta(entrega="qualidade"))
    def r35_qa(self):
        self.pontuar("QA", 4, "R35", "Valor entregue: confiança de que o software funciona")

    @Rule(Resposta(atuacao="qualidade", linguagem=EM("python", "javascript", "java_csharp")))
    def r36_qa(self):
        self.pontuar("QA", 2, "R36", "Qualidade + linguagem de programação: base para testes automatizados")

    # ---- Product Management -------------------------------------------------
    @Rule(Resposta(atuacao="negocio"))
    def r37_pm(self):
        self.pontuar("PM", 6, "R37", "Quer definir o que construir: usuários, prioridades e negócio")

    @Rule(Resposta(entrega="negocio"))
    def r38_pm(self):
        self.pontuar("PM", 4, "R38", "Valor entregue: estratégia e produto certo")

    @Rule(Perfil(tipo="negocio"))
    def r39_pm(self):
        self.pontuar("PM", 2, "R39", "Perfil de negócios: comunicação alta + foco em estratégia")

    @Rule(Resposta(linguagem="nenhuma", entrega="negocio"))
    def r40_pm(self):
        self.pontuar("PM", 1, "R40", "Trilha em que profundidade técnica inicial não é barreira")

    # ======================= DECISÃO FINAL ====================================
    @Rule(Fase(nome="decisao"), salience=-100)
    def r99_decisao(self):
        n_regras = {t: sum(1 for d in self.disparos if d[1] == t and d[2] > 0) for t in TRILHAS}
        self.ranking = sorted(
            self.placar.items(),
            key=lambda kv: (-kv[1], -n_regras[kv[0]], ORDEM_DESEMPATE.index(kv[0])),
        )
        if self.ranking[0][1] > 0:
            self.recomendacao = self.ranking[0][0]


# ----------------------------------------------------------------------------
# API de alto nível (usada pelo Streamlit e pelos testes)
# ----------------------------------------------------------------------------
def diagnosticar(respostas: dict) -> dict:
    """Executa o motor com as respostas e devolve o diagnóstico completo."""
    motor = ConsultorCarreiras()
    motor.reset()
    motor.declare(Resposta(**respostas))
    motor.declare(Fase(nome="decisao"))
    motor.run()

    rec = motor.recomendacao
    margem = None
    if rec and len(motor.ranking) > 1:
        margem = motor.ranking[0][1] - motor.ranking[1][1]

    if margem is None:
        certeza = "Indeterminada"
    elif margem >= 5:
        certeza = "Alta"
    elif margem >= 2:
        certeza = "Média"
    else:
        certeza = "Baixa (trilhas muito próximas)"

    motivos = sorted(
        [d for d in motor.disparos if rec and d[1] == rec],
        key=lambda d: -d[2],
    )
    return {
        "recomendacao": rec,
        "nome": TRILHAS.get(rec),
        "ranking": motor.ranking,
        "motivos": motivos,                 # regras que sustentam a recomendação
        "disparos": motor.disparos,         # todas as regras de pontuação disparadas
        "perfis": motor.perfis,             # regras de nível 1 disparadas
        "margem": margem,
        "certeza": certeza,
    }
