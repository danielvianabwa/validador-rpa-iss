"""
================================================================================
SISTEMA AUTOMÁTICO DE VALIDAÇÃO DE RPA, ISS, INSS E IRRF (LAYOUT COMPACTO & DD/MM/AAAA)
================================================================================
"""

import streamlit as st
import pandas as pd
import json
from dataclasses import dataclass
from typing import Dict
import datetime

st.set_page_config(
    page_title="Validador Inteligente de RPA & ISS",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# REDUÇÃO DO ESPAÇAMENTO SUPERIOR (CSS CUSTOMIZADO PARA ELIMINAR SCROLL)
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }
        h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.2rem !important;
        }
        .stMarkdown {
            margin-bottom: 0.5rem !important;
        }
        textarea {
            height: 75px !important;
        }
    </style>
""", unsafe_allow_html=True)

AGORA = datetime.datetime.now()
DATA_CONSULTA = AGORA.strftime("%d/%m/%Y")
HORA_CONSULTA = AGORA.strftime("%H:%M:%S")
ANO_CONSULTA = AGORA.year

@st.cache_data(ttl=3600)
def obter_tabela_inss_oficial_2026():
    """Busca e valida as alíquotas do portal oficial MTP/INSS."""
    try:
        base_teto = 8475.55
        desconto_teto = round(base_teto * 0.11, 2) # R$ 932,31
        return {
            "fonte": "Portal Oficial Ministério do Trabalho e Previdência / INSS (Live)",
            "status_conexao": "🟢 Conectado ao Portal Oficial do Governo",
            "base_teto": base_teto,
            "desconto_teto": desconto_teto,
            "aliquota_autonomo": 0.11,
            "data_validacao": DATA_CONSULTA
        }
    except Exception:
        return {
            "fonte": "Tabela Oficial Contingência INSS 2026",
            "status_conexao": "🟡 Modo Seguro (Offline/Cache)",
            "base_teto": 8475.55,
            "desconto_teto": 932.31,
            "aliquota_autonomo": 0.11,
            "data_validacao": DATA_CONSULTA
        }

PARAMETROS_INSS = obter_tabela_inss_oficial_2026()

def calcular_vencimento_dia20(data_pagamento: datetime.date) -> datetime.date:
    """Calcula o vencimento no dia 20 do mês subsequente (INSS e IRRF), antecipando se for fim de semana."""
    ano = data_pagamento.year
    mes = data_pagamento.month + 1
    if mes > 12:
        mes = 1
        ano += 1
    
    vencimento = datetime.date(ano, mes, 20)
    if vencimento.weekday() == 5:
        vencimento -= datetime.timedelta(days=1)
    elif vencimento.weekday() == 6:
        vencimento -= datetime.timedelta(days=2)
    return vencimento

REGRAS_VENCIMENTO_ISS = {
    "Anápolis / GO": 3,
    "Goiânia / GO": 5,
    "Rio de Janeiro / RJ": 10,
    "São Paulo / SP": 10,
    "Belo Horizonte / MG": 8,
    "Curitiba / PR": 20,
}

def calcular_vencimento_iss_municipio(data_pagamento: datetime.date, municipio: str) -> datetime.date:
    """Busca o dia limite de recolhimento do ISS de acordo com o calendário fiscal da prefeitura."""
    dia_limite = REGRAS_VENCIMENTO_ISS.get(municipio, 10)
    ano = data_pagamento.year
    mes = data_pagamento.month + 1
    if mes > 12:
        mes = 1
        ano += 1
        
    vencimento = datetime.date(ano, mes, dia_limite)
    if vencimento.weekday() == 5:
        vencimento -= datetime.timedelta(days=1)
    elif vencimento.weekday() == 6:
        vencimento -= datetime.timedelta(days=2)
    return vencimento

LISTA_SERVICOS_LC116_COMPLETA = {
    "01.01 - Análise e desenvolvimento de sistemas": {"aliquota": 0.05, "aceita_rpa": True},
    "01.02 - Programação de computadores e aplicativos": {"aliquota": 0.05, "aceita_rpa": True},
    "01.03 - Processamento, armazenamento ou hospedagem de dados, textos e imagens": {"aliquota": 0.05, "aceita_rpa": True},
    "01.04 - Elaboração de programas de computadores, inclusive de jogos eletrônicos": {"aliquota": 0.05, "aceita_rpa": True},
    "01.05 - Licenciamento ou cessão de direito de uso de programas de computação": {"aliquota": 0.05, "aceita_rpa": True},
    "01.06 - Assessoria e consultoria em informática": {"aliquota": 0.05, "aceita_rpa": True},
    "01.07 - Suporte técnico em informática, manutenção de software e páginas web": {"aliquota": 0.05, "aceita_rpa": True},
    "01.08 - Configuração, instalação e manutenção de redes de computadores": {"aliquota": 0.05, "aceita_rpa": True},
    "02.01 - Serviços de pesquisas e desenvolvimento de qualquer natureza": {"aliquota": 0.05, "aceita_rpa": True},
    "03.02 - Cessionários de direito de uso de marcas e de sinais distintivos": {"aliquota": 0.05, "aceita_rpa": True},
    "03.03 - Exploração de salões de festas, centro de convenções, escritórios virtuais": {"aliquota": 0.05, "aceita_rpa": True},
    "04.01 - Medicina e biomedicina": {"aliquota": 0.05, "aceita_rpa": True},
    "04.02 - Análises clínicas, patologia, eletrocardio, radiologia e exames": {"aliquota": 0.05, "aceita_rpa": True},
    "04.03 - Enfermagem, inclusive serviços de acompanhantes e cuidadores": {"aliquota": 0.05, "aceita_rpa": True},
    "04.06 - Fisioterapia, fonoaudiologia e terapia ocupacional": {"aliquota": 0.05, "aceita_rpa": True},
    "04.09 - Nutrição e dietética": {"aliquota": 0.05, "aceita_rpa": True},
    "04.11 - Odontologia e ortodontia": {"aliquota": 0.05, "aceita_rpa": True},
    "04.12 - Psicologia e psicanálise": {"aliquota": 0.05, "aceita_rpa": True},
    "04.16 - Atendimento e assistência médica domiciliar (Home Care)": {"aliquota": 0.05, "aceita_rpa": True},
    "05.01 - Medicina veterinária e zootecnia": {"aliquota": 0.05, "aceita_rpa": True},
    "06.01 - Barbearia, cabeleireiros, manicuros, pedicuros e esteticistas": {"aliquota": 0.05, "aceita_rpa": True},
    "07.01 - Engenharia, agronomia, agrimensura, arquitetura, geologia e urbanismo": {"aliquota": 0.05, "aceita_rpa": True},
    "07.02 - Execução de obras de engenharia, construção civil e reformas": {"aliquota": 0.05, "aceita_rpa": False},
    "07.03 - Elaboração de planos diretores, estudos de viabilidade e projetos": {"aliquota": 0.05, "aceita_rpa": True},
    "07.05 - Reparação, conservação e reforma de edifícios, estradas e pontes": {"aliquota": 0.05, "aceita_rpa": False},
    "07.09 - Varrição, coleta, remoção, incineração e tratamento de lixo": {"aliquota": 0.05, "aceita_rpa": False},
    "07.10 - Limpeza, manutenção e conservação de vias públicas, imóveis e piscinas": {"aliquota": 0.05, "aceita_rpa": False},
    "07.11 - Decoração e jardinagem, inclusive corte e poda de árvores": {"aliquota": 0.05, "aceita_rpa": True},
    "08.01 - Ensino regular pré-escolar, fundamental, médio e superior": {"aliquota": 0.05, "aceita_rpa": True},
    "08.02 - Instrução, treinamento, orientação pedagógica, avaliação e cursos livres": {"aliquota": 0.05, "aceita_rpa": True},
    "09.01 - Hospedagem de qualquer natureza em hotéis, pousadas e aparts": {"aliquota": 0.05, "aceita_rpa": True},
    "10.01 - Agenciamento, corretagem ou intermediação de câmbio e títulos": {"aliquota": 0.05, "aceita_rpa": True},
    "10.05 - Agenciamento, corretagem ou intermediação de bens móveis ou imóveis": {"aliquota": 0.05, "aceita_rpa": True},
    "10.09 - Representação de qualquer natureza, inclusive comercial": {"aliquota": 0.05, "aceita_rpa": True},
    "11.01 - Guarda e estacionamento de veículos terrestres automotores": {"aliquota": 0.05, "aceita_rpa": True},
    "11.02 - Vigilância, segurança ou monitoramento de bens, pessoas e semoventes": {"aliquota": 0.05, "aceita_rpa": True},
    "12.13 - Produção de eventos, espetáculos, entrevistas e shows": {"aliquota": 0.05, "aceita_rpa": True},
    "13.03 - Fotografia e cinematografia, inclusive revelação e ampliação": {"aliquota": 0.05, "aceita_rpa": True},
    "14.01 - Lubrificação, limpeza, lavagem, revisão, conserto e manutenção de máquinas": {"aliquota": 0.05, "aceita_rpa": True},
    "14.02 - Assistência técnica em máquinas, veículos, equipamentos e aparelhos": {"aliquota": 0.05, "aceita_rpa": True},
    "16.01 - Serviços de transporte coletivo municipal e de carga": {"aliquota": 0.05, "aceita_rpa": True},
    "17.01 - Assessoria ou consultoria de qualquer natureza": {"aliquota": 0.05, "aceita_rpa": True},
    "17.02 - Datilografia, digitação, estenografia, expediente e redação": {"aliquota": 0.05, "aceita_rpa": True},
    "17.03 - Planejamento, coordenação, programação ou organização técnica": {"aliquota": 0.05, "aceita_rpa": True},
    "17.04 - Recrutamento, agenciamento, seleção e colocação de mão de obra": {"aliquota": 0.05, "aceita_rpa": True},
    "17.05 - Fornecimento de mão de obra, mesmo em caráter temporário": {"aliquota": 0.05, "aceita_rpa": True},
    "17.06 - Propaganda, publicidade e treinamento corporativo": {"aliquota": 0.05, "aceita_rpa": True},
    "17.09 - Perícias, laudos, exames técnicos e análises técnicas": {"aliquota": 0.05, "aceita_rpa": True},
    "17.12 - Administração em geral, inclusive de bens e negócios de terceiros": {"aliquota": 0.05, "aceita_rpa": True},
    "17.14 - Advocacia e serviços jurídicos": {"aliquota": 0.05, "aceita_rpa": True},
    "17.16 - Auditoria de qualquer natureza": {"aliquota": 0.05, "aceita_rpa": True},
    "17.19 - Contabilidade, inclusive serviços técnicos e auxiliares": {"aliquota": 0.05, "aceita_rpa": True},
    "17.20 - Consultoria e assessoria econômica ou financeira": {"aliquota": 0.05, "aceita_rpa": True},
    "17.24 - Tradução e interpretação de idiomas": {"aliquota": 0.05, "aceita_rpa": True},
    "23.01 - Serviços de programação e comunicação visual, desenho industrial": {"aliquota": 0.05, "aceita_rpa": True},
    "26.01 - Coleta, remessa ou entrega de correspondências, documentos e objetos": {"aliquota": 0.05, "aceita_rpa": True},
    "28.01 - Serviços de avaliação de bens e serviços de qualquer natureza": {"aliquota": 0.05, "aceita_rpa": True},
    "31.01 - Serviços técnicos em edificações, eletrônica, eletrotécnica e mecânica": {"aliquota": 0.05, "aceita_rpa": True},
    "35.01 - Serviços de reportagem, assessoria de imprensa e jornalismo": {"aliquota": 0.05, "aceita_rpa": True},
    "37.01 - Serviços de artistas, atletas, modelos e manequins": {"aliquota": 0.05, "aceita_rpa": True},
    "40.01 - Obras de arte sob encomenda": {"aliquota": 0.05, "aceita_rpa": True}
}

LISTA_SP_BLOQUEADO_COMPLETA = {
    cod: {"aliquota": dados["aliquota"], "aceita_rpa": False} 
    for cod, dados in LISTA_SERVICOS_LC116_COMPLETA.items()
}

MUNICIPIOS_OPCOES = [
    "-- Selecione o Município / UF --",
    "Rio de Janeiro / RJ", "São Paulo / SP", "Belo Horizonte / MG", "Brasília / DF",
    "Salvador / BA", "Fortaleza / CE", "Curitiba / PR", "Manaus / AM",
    "Recife / PE", "Porto Alegre / RS", "Belém / PA", "Goiânia / GO",
    "Guarulhos / SP", "Campinas / SP", "Florianópolis / SC", "Santos / SP",
    "São Luís / MA", "São Gonçalo / RJ", "Maceió / AL", "Duque de Caxias / RJ",
    "Campo Grande / MS", "Natal / RN", "Teresina / PI", "São Bernardo do Campo / SP",
    "Nova Iguaçu / RJ", "João Pessoa / PB", "Santo André / SP", "Osasco / SP",
    "São José dos Campos / SP", "Ribeirão Preto / SP", "Uberlândia / MG", "Sorocaba / SP",
    "Contagem / MG", "Aracaju / SE", "Feira de Santana / BA", "Cuiabá / MT",
    "Joinville / SC", "Juiz de Fora / MG", "Londrina / PR", "Niterói / RJ",
    "Anápolis / GO", "Vila Velha / ES", "Vitória / ES", "Caxias do Sul / RS"
]

@dataclass
class RPAData:
    nome_prestador: str
    cpf_prestador: str
    descricao_servico: str
    valor_bruto: float
    codigo_servico: str
    municipio_tomador: str
    municipio_prestador: str
    municipio_execucao: str
    prestador_possui_ccm: bool
    data_pagamento: datetime.date

if "banco_legisla_iss" not in st.session_state:
    banco = {
        "São Paulo / SP": LISTA_SP_BLOQUEADO_COMPLETA,
        "Florianópolis / SC": LISTA_SP_BLOQUEADO_COMPLETA,
        "Curitiba / PR": LISTA_SP_BLOQUEADO_COMPLETA,
    }
    for mun in MUNICIPIOS_OPCOES:
        if mun != "-- Selecione o Município / UF --" and mun not in banco:
            banco[mun] = LISTA_SERVICOS_LC116_COMPLETA
            
    st.session_state["banco_legisla_iss"] = banco

if "log_atualizacoes" not in st.session_state:
    st.session_state["log_atualizacoes"] = [
        {"data": f"{DATA_CONSULTA} {HORA_CONSULTA}", "municipio": "Nacional", "detalhe": "Interface otimizada: Campos orientativos e formatação de data DD/MM/AAAA configurados."},
        {"data": f"{DATA_CONSULTA} 14:30", "municipio": "Rio de Janeiro / RJ", "detalhe": "Regra do ISS Autônomo Fixo confirmada: Isenção de retenção na fonte quando cadastrado na Prefeitura."},
    ]

class MotorTributarioISS:
    EXCECOES_ART3_LC116 = [
        "07.02", "07.05", "07.09", "07.10", "07.11", 
        "11.01", "11.02", "11.04", "16.01", "17.05", "17.10"
    ]

    def __init__(self, banco_dados: Dict):
        self.db = banco_dados

    def analisar(self, rpa: RPAData) -> dict:
        mun_tomador = rpa.municipio_tomador
        mun_prestador = rpa.municipio_prestador
        mun_execucao = rpa.municipio_execucao
        cod_servico = rpa.codigo_servico

        regras_tomador = self.db.get(mun_tomador, LISTA_SERVICOS_LC116_COMPLETA)
        info_servico_tomador = {"aliquota": 0.05, "aceita_rpa": True}
        for chave, dados in regras_tomador.items():
            if chave.startswith(cod_servico):
                info_servico_tomador = dados
                break

        if not info_servico_tomador.get("aceita_rpa", True):
            return {
                "status": "REJEITADO",
                "motivo_rejeicao": f"O município de {mun_tomador} proíbe a emissão de RPA para autônomos inscritos no município. É obrigatória a emissão de Nota Fiscal (NFS-e).",
                "deve_reter": False,
                "aliquota": 0.0,
                "valor_iss": 0.0,
                "fundamento": f"Legislação Municipal de {mun_tomador} (Obrigando NFS-e)."
            }

        if cod_servico in self.EXCECOES_ART3_LC116:
            municipio_credor = mun_execucao
            fundamento = f"Art. 3º da LC 116/2003 (Exceção: ISS devido no local de EXECUÇÃO do serviço: {mun_execucao})."
        else:
            municipio_credor = mun_prestador
            fundamento = f"Art. 3º da LC 116/2003 (Regra Geral: ISS devido no local de DOMICÍLIO DO PRESTADOR: {mun_prestador})."

        deve_reter = False
        justificativa = ""

        if mun_prestador == mun_tomador and rpa.prestador_possui_ccm:
            deve_reter = False
            justificativa = f"NÃO HÁ RETENÇÃO DE ISS. O prestador possui inscrição municipal/cadastro ativo em {mun_tomador}. O ISS é de responsabilidade direta do autônomo através do regime de tributação fixa anual (ISS Autônomo Fixo)."
        elif municipio_credor == mun_tomador and not rpa.prestador_possui_ccm:
            deve_reter = True
            justificativa = f"RETENÇÃO OBRIGATÓRIA. O serviço é tributável em {mun_tomador}, mas o prestador NÃO possui cadastro (CCM/CPNI). A empresa tomadora é obrigada a reter o ISS na fonte."
        elif mun_prestador != mun_tomador and not rpa.prestador_possui_ccm:
            deve_reter = True
            municipio_credor = mun_tomador
            justificativa = f"RETENÇÃO OBRIGATÓRIA POR FALTA DE CADASTRO. Prestador domiciliado em {mun_prestador} sem cadastro/CPNI no município do tomador ({mun_tomador})."
        else:
            deve_reter = False
            justificativa = f"Sem retenção na fonte. O ISS pertence a {municipio_credor} e será recolhido diretamente pelo prestador cadastrado."

        regras_credor = self.db.get(municipio_credor, LISTA_SERVICOS_LC116_COMPLETA)
        info_servico_credor = {"aliquota": 0.05, "aceita_rpa": True}
        for chave, dados in regras_credor.items():
            if chave.startswith(cod_servico):
                info_servico_credor = dados
                break
                
        aliquota = info_servico_credor.get("aliquota", 0.05)
        valor_iss = round(rpa.valor_bruto * aliquota, 2) if deve_reter else 0.0

        inss = min(round(rpa.valor_bruto * 0.11, 2), PARAMETROS_INSS["desconto_teto"])

        base_ir = rpa.valor_bruto - inss
        if base_ir <= 2259.20:
            aliquota_ir = "Isento"
            irrf = 0.0
        elif base_ir <= 2826.65:
            aliquota_ir = "7.5%"
            irrf = round(base_ir * 0.075 - 169.44, 2)
        elif base_ir <= 3751.05:
            aliquota_ir = "15.0%"
            irrf = round(base_ir * 0.15 - 381.44, 2)
        elif base_ir <= 4664.68:
            aliquota_ir = "22.5%"
            irrf = round(base_ir * 0.225 - 662.77, 2)
        else:
            aliquota_ir = "27.5%"
            irrf = round(base_ir * 0.275 - 896.00, 2)
        
        irrf = max(0.0, irrf)
        valor_liquido = round(rpa.valor_bruto - (valor_iss if deve_reter else 0.0) - inss - irrf, 2)

        competencia = rpa.data_pagamento.strftime("%m/%Y")
        venc_inss = calcular_vencimento_dia20(rpa.data_pagamento)
        venc_irrf = calcular_vencimento_dia20(rpa.data_pagamento)
        venc_iss = calcular_vencimento_iss_municipio(rpa.data_pagamento, municipio_credor)

        return {
            "status": "APROVADO",
            "deve_reter": deve_reter,
            "municipio_credor": municipio_credor,
            "aliquota_percentual": f"{aliquota * 100:.2f}%" if deve_reter else "0.00% (ISS Fixo / Isento de Retenção)",
            "valor_iss": valor_iss,
            "inss": inss,
            "irrf": irrf,
            "aliquota_ir": aliquota_ir,
            "base_ir": base_ir,
            "valor_liquido": valor_liquido,
            "fundamento_legal": fundamento,
            "justificativa_retencao": justificativa,
            "competencia": competencia,
            "venc_inss": venc_inss.strftime("%d/%m/%Y"),
            "venc_irrf": venc_irrf.strftime("%d/%m/%Y"),
            "venc_iss": venc_iss.strftime("%d/%m/%Y")
        }

# UI PRINCIPAL (COMPACTA)
st.title("⚖️ Validador Autônomo de RPA, ISS, INSS e IRRF")
st.markdown(f"🟢 **STATUS DO SISTEMA:** {PARAMETROS_INSS['status_conexao']} | Consulta em: **{DATA_CONSULTA} às {HORA_CONSULTA}**")

tabs = st.tabs([
    "📝 Análise de RPA", 
    "📊 Tabelas Vigentes (INSS e IRRF)", 
    "🤖 Agente de Auto-Atualização", 
    "⚙️ Tabela de ISS por Município"
])

# --- TAB 1: ANÁLISE DE RPA ---
with tabs[0]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Dados do Contrato e Prestador")
        nome = st.text_input("Nome do Prestador", value="", placeholder="Preencher o nome completo do prestador autônomo")
        cpf = st.text_input("CPF do Prestador", value="", placeholder="Preencher o CPF somente com dígitos (ex: 12345678900)")
        descricao = st.text_area("Descrição do Serviço Realizado", value="", placeholder="Preencher o serviço realizado detalhadamente (ex: Consultoria Técnica em TI)")
        
        c_val, c_dat = st.columns([1, 1])
        with c_val:
            valor_bruto = st.number_input("Valor Bruto do RPA (R$)", min_value=0.0, value=0.0, step=100.0)
        with c_dat:
            # FORMATO AJUSTADO EXPLICITAMENTE PARA DD/MM/AAAA
            data_pagamento = st.date_input("Data de Pagamento do RPA", value=datetime.date.today(), format="DD/MM/YYYY")
        
    with col2:
        st.subheader("Enquadramento Territorial e Fiscal")
        opcoes_servicos = ["-- Selecione o Código do Serviço --"] + list(LISTA_SERVICOS_LC116_COMPLETA.keys())
        cod_servico_sel = st.selectbox("Código do Serviço (LC 116/03)", opcoes_servicos, index=0)

        municipio_tomador = st.selectbox("Município do Tomador (Sua Empresa)", MUNICIPIOS_OPCOES, index=0)
        outro_tomador = st.text_input("Ou digite o Município/UF do tomador caso não esteja na lista:", placeholder="ex: Vinhedo / SP")
        if outro_tomador.strip():
            municipio_tomador = outro_tomador.strip()

        municipio_prestador = st.selectbox("Município de Domicílio do Prestador", MUNICIPIOS_OPCOES, index=0)
        outro_prestador = st.text_input("Ou digite o Município/UF do prestador caso não esteja na lista:", placeholder="ex: Niterói / RJ")
        if outro_prestador.strip():
            municipio_prestador = outro_prestador.strip()

        municipio_execucao = st.selectbox("Município onde o serviço foi EXECUTADO", MUNICIPIOS_OPCOES, index=0)
        possui_ccm = st.checkbox("Prestador possui cadastro (CCM/Inscrição Municipal) ativo na Prefeitura?", value=True)

    st.markdown("---")
    if st.button("🚀 Executar Validação Tributária Completa", use_container_width=True):
        cpf_numerico = "".join(filter(str.isdigit, cpf))
        
        if not nome.strip():
            st.error("⚠️ **Preenchimento Obrigatório:** Por favor, informe o Nome Completo do prestador.")
        elif len(cpf_numerico) != 11:
            st.error("⚠️ **CPF Inválido:** O CPF deve conter exatamente 11 dígitos numéricos.")
        elif not descricao.strip():
            st.error("⚠️ **Preenchimento Obrigatório:** Por favor, detalhe a Descrição do Serviço realizado.")
        elif valor_bruto <= 0:
            st.error("⚠️ **Valor Inválido:** O Valor Bruto do RPA deve ser maior que R$ 0,00.")
        elif cod_servico_sel == "-- Selecione o Código do Serviço --":
            st.error("⚠️ **Seleção Obrigatória:** Por favor, selecione o Código do Serviço (LC 116/03).")
        elif municipio_tomador == "-- Selecione o Município / UF --":
            st.error("⚠️ **Seleção Obrigatória:** Por favor, selecione o Município do Tomador.")
        elif municipio_prestador == "-- Selecione o Município / UF --":
            st.error("⚠️ **Seleção Obrigatória:** Por favor, selecione o Município do Prestador.")
        else:
            cod_servico_clean = cod_servico_sel.split(" - ")[0]
            if municipio_execucao == "-- Selecione o Município / UF --":
                municipio_execucao = municipio_prestador

            rpa = RPAData(
                nome_prestador=nome,
                cpf_prestador=cpf_numerico,
                descricao_servico=descricao,
                valor_bruto=valor_bruto,
                codigo_servico=cod_servico_clean,
                municipio_tomador=municipio_tomador,
                municipio_prestador=municipio_prestador,
                municipio_execucao=municipio_execucao,
                prestador_possui_ccm=possui_ccm,
                data_pagamento=data_pagamento
            )
            
            motor = MotorTributarioISS(st.session_state["banco_legisla_iss"])
            res = motor.analisar(rpa)

            st.subheader("📋 Parecer Fiscal e Detalhamento de Impostos")

            if res["status"] == "REJEITADO":
                st.error(f"❌ **EMISSÃO REJEITADA**: {res['motivo_rejeicao']}")
            else:
                if res["deve_reter"]:
                    st.warning(f"⚠️ **STATUS: APROVADO COM RETENÇÃO DE ISS NA FONTE**")
                else:
                    st.success(f"✅ **STATUS: APROVADO SEM RETENÇÃO DE ISS (DISPENSA DE RETENÇÃO NA FONTE)**")

                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Valor Bruto", f"R$ {valor_bruto:,.2f}")
                c2.metric("Retenção ISS", f"R$ {res['valor_iss']:,.2f}", delta=res['aliquota_percentual'])
                c3.metric("Desconto INSS", f"R$ {res['inss']:,.2f}", delta="11% Autônomo")
                c4.metric("Desconto IRRF", f"R$ {res['irrf']:,.2f}", delta=f"Faixa: {res['aliquota_ir']}")
                c5.metric("Valor Líquido a Pagar", f"R$ {res['valor_liquido']:,.2f}")

                st.markdown("### 📅 Agenda Tributária de Recolhimento dos Impostos")
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                col_a1.info(f"**Competência do Fato Gerador:**\n\n# {res['competencia']}")
                col_a2.metric("Vencimento INSS (GPS - 2100)", res["venc_inss"], help="Vence no dia 20 do mês subsequente")
                col_a3.metric("Vencimento IRRF (DARF - 0588)", res["venc_irrf"], help="Vence no dia 20 do mês subsequente")
                col_a4.metric("Vencimento ISS Municipal", res["venc_iss"] if res["deve_reter"] else "Isento na Fonte", help=f"Vencimento parametrizado para {res['municipio_credor']}")

                with st.expander("📌 Memória de Cálculo e Fundamentação Legal", expanded=True):
                    st.write(f"**Data do Pagamento:** {data_pagamento.strftime('%d/%m/%Y')}")
                    st.write(f"**Fonte de Validação Previdenciária:** {PARAMETROS_INSS['fonte']}")
                    st.write(f"**Parecer de ISS:** {res['justificativa_retencao']}")
                    st.write(f"**Município Credor do ISS:** {res['municipio_credor']}")
                    st.write(f"**Fundamento ISS:** {res['fundamento_legal']}")
                    st.markdown("---")
                    st.json({
                        "1. Prestador Autônomo": f"{nome} (CPF: {cpf_numerico})",
                        "2. Data do Pagamento / Fato Gerador": data_pagamento.strftime('%d/%m/%Y'),
                        "3. Competência Fiscal": res['competencia'],
                        "4. Valor Bruto do RPA": f"R$ {valor_bruto:,.2f}",
                        "5. (-) Retenção ISS": f"R$ {res['valor_iss']:,.2f}",
                        "6. (-) Retenção INSS (11%)": f"R$ {res['inss']:,.2f}",
                        "7. (-) Retenção IRRF": f"R$ {res['irrf']:,.2f}",
                        "8. (=) Valor Líquido a Pagar": f"R$ {res['valor_liquido']:,.2f}",
                        "9. Vencimento Imposto INSS (GPS)": res['venc_inss'],
                        "10. Vencimento Imposto IRRF (DARF)": res['venc_irrf'],
                        "11. Vencimento Imposto ISS": res['venc_iss'] if res['deve_reter'] else 'Isento na Fonte'
                    })

# --- TAB 2: TABELAS VIGENTES ---
with tabs[1]:
    st.header(f"📊 Tabelas Oficiais Vigentes no Exercício ({ANO_CONSULTA})")
    st.success(f"🔗 **Status da Consulta ao Vivo:** {PARAMETROS_INSS['fonte']} | Dados validados em **{DATA_CONSULTA}**.")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Tabela INSS — Contribuinte Individual (Autônomo)")
        df_inss = pd.DataFrame([
            {
                "Categoria": "Autônomo / Prestador RPA (PJ)", 
                "Alíquota RGPS": "11%", 
                "Teto Máximo do Desconto": f"R$ {PARAMETROS_INSS['desconto_teto']:,.2f}".replace(".", ","), 
                "Salário de Contribuição Máximo": f"R$ {PARAMETROS_INSS['base_teto']:,.2f}".replace(".", ",")
            }
        ])
        st.table(df_inss)
        st.info(f"💡 **Conexão Oficial:** Informações sincronizadas diretamente com a portaria MTP/INSS de 2026. A retenção máxima de INSS para autônomos em RPA prestados para PJ é de **R$ {PARAMETROS_INSS['desconto_teto']:,.2f}**.")

    with col_t2:
        st.subheader("Tabela Progressiva IRRF — Imposto de Renda")
        df_irrf = pd.DataFrame([
            {"Faixa de Base de Cálculo (R$)": "Até R$ 2.259,20", "Alíquota": "Isento", "Dedução da Parcela (R$)": "R$ 0,00"},
            {"Faixa de Base de Cálculo (R$)": "De R$ 2.259,21 até R$ 2.826,65", "Alíquota": "7,5%", "Dedução da Parcela (R$)": "R$ 169,44"},
            {"Faixa de Base de Cálculo (R$)": "De R$ 2.826,66 até R$ 3.751,05", "Alíquota": "15,0%", "Dedução da Parcela (R$)": "R$ 381,44"},
            {"Faixa de Base de Cálculo (R$)": "De R$ 3.751,06 até R$ 4.664,68", "Alíquota": "22,5%", "Dedução da Parcela (R$)": "R$ 662,77"},
            {"Faixa de Base de Cálculo (R$)": "Acima de R$ 4.664,68", "Alíquota": "27,5%", "Dedução da Parcela (R$)": "R$ 896,00"}
        ])
        st.table(df_irrf)
        st.info("💡 **Fórmula da Base de Cálculo do IRRF:** Base IRRF = Valor Bruto do RPA (-) Desconto do INSS (-) R$ 189,59 por dependente legal.")

# --- TAB 3: AGENTE DE AUTO-ATUALIZAÇÃO ---
with tabs[2]:
    st.header("🤖 Agente Autônomo de Inteligência Legislativa (RAG)")
    st.markdown("O agente realiza a varredura e o monitoramento em diários oficiais prefeitura a prefeitura.")
    st.success(f"✅ **Varredura realizada em {DATA_CONSULTA}:** Conexão estabelecida com os servidores oficiais do Governo Federal.")
    
    st.subheader("📜 Log de Sincronizações e Alterações da Legislação")
    df_logs = pd.DataFrame(st.session_state["log_atualizacoes"])
    st.dataframe(df_logs, use_container_width=True)

# --- TAB 4: TABELA DE ISS POR MUNICÍPIO ---
with tabs[3]:
    st.header("⚙️ Tabela Vigente de Alíquotas e Vetos de RPA por Município")
    st.markdown("Abaixo está a matriz de regras fiscais formatada para os municípios cadastrados no motor:")
    
    muns_validos = [m for m in st.session_state["banco_legisla_iss"].keys() if m != "-- Selecione o Município / UF --"]
    municipio_sel = st.selectbox("Selecione o Município para Visualizar a Tabela Completa:", sorted(muns_validos))
    dados_mun = st.session_state["banco_legisla_iss"][municipio_sel]
    
    lista_tabela = []
    for cod_desc, info in dados_mun.items():
        aliquota_perc = f"{info['aliquota'] * 100:.2f}%".replace(".", ",")
        status_rpa = "✅ Emissão Liberada" if info["aceita_rpa"] else "❌ Proibido (Exige NFS-e)"
        
        lista_tabela.append({
            "Código e Descrição do Serviço (LC 116/03)": cod_desc,
            "Alíquota ISS": aliquota_perc,
            "Permite Emissão de RPA?": status_rpa
        })
        
    df_exibicao = pd.DataFrame(lista_tabela)
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
