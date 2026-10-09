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
