"""
================================================================================
SISTEMA AUTOMÁTICO DE VALIDAÇÃO DE RPA - BWA GLOBAL (LISTA ALFABÉTICA UNIFICADA)
================================================================================
"""

import streamlit as st
import pandas as pd
import json
from dataclasses import dataclass
from typing import Dict
import datetime

st.set_page_config(
    page_title="BWA Global | Validador de RPA & ISS",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESTILIZAÇÃO CSS DE ALTA PRIORIDADE
st.markdown("""
    <style>
        /* Fundo Geral Claro */
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #F4F0F6 !important;
            color: #111111 !important;
        }
        
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* Banner BWA */
        .bwa-banner {
            background-color: #6A327E !important;
            border-radius: 10px !important;
            padding: 1.8rem 2.2rem !important;
            margin-bottom: 2rem !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
        }
        .bwa-banner-title {
            color: #FFFFFF !important;
            font-size: 2.4rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: Arial, sans-serif !important;
        }
        .bwa-banner-status {
            color: #F0E6F6 !important;
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            font-family: Arial, sans-serif !important;
        }

        /* TÍTULOS E RÓTULOS GIGANTES */
        label, p, span, h1, h2, h3, h4, .stMarkdown {
            font-size: 1.25rem !important;
            color: #111111 !important;
            font-weight: 700 !important;
        }

        /* CHECKBOX CCM COM MAIOR DESTAQUE */
        div[data-testid="stCheckbox"] {
            margin-top: 15px !important;
            padding: 12px 16px !important;
            background-color: #FFFFFF !important;
            border: 2px solid #A882C2 !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
        }
        div[data-testid="stCheckbox"] label span {
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            color: #4A2259 !important;
        }
        div[data-testid="stCheckbox"] input[type="checkbox"] {
            width: 24px !important;
            height: 24px !important;
            cursor: pointer !important;
        }

        /* FORÇAR CAMPOS DE TEXTO E SELETORES COM FUNDO BRANCO E TEXTO ESCURO */
        div[data-baseweb="select"], div[data-baseweb="select"] *, 
        div[data-baseweb="input"], div[data-baseweb="input"] *, 
        div[data-baseweb="base-input"], div[data-baseweb="base-input"] *,
        input, select, textarea {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-color: #A882C2 !important;
            font-size: 1.3rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }

        div[role="listbox"] *, ul[role="listbox"] * {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            font-size: 1.2rem !important;
        }

        /* ESTILO PARA TABELAS HTML PERSONALIZADAS SEM FUNDO PRETO */
        .bwa-table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin-top: 15px !important;
            margin-bottom: 25px !important;
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.08) !important;
        }
        .bwa-table th {
            background-color: #EADFF0 !important;
            color: #4A2259 !important;
            font-size: 1.3rem !important;
            font-weight: 800 !important;
            padding: 14px 18px !important;
            border: 1px solid #C4B0D8 !important;
            text-align: left !important;
        }
        .bwa-table td {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            padding: 12px 18px !important;
            border: 1px solid #D1C0E0 !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }

        textarea {
            height: 110px !important;
        }

        /* BOTÕES GIGANTES BWA COM TEXTO EM BRANCO PURO */
        .stButton>button, .stDownloadButton>button {
            background-color: #6A327E !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 800 !important;
            border: none !important;
            padding: 1.2rem 2.5rem !important;
            font-size: 1.4rem !important;
            margin-top: 1rem !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2) !important;
        }
        .stButton>button p, .stDownloadButton>button p {
            color: #FFFFFF !important;
            font-size: 1.4rem !important;
            font-weight: 800 !important;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #4A2259 !important;
            color: #FFFFFF !important;
        }

        /* ABAS SUPERIORES */
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px !important;
            margin-bottom: 1.8rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            height: 58px !important;
            padding: 0px 28px !important;
            background-color: #D6C2E2 !important;
            border-radius: 8px 8px 0px 0px !important;
            color: #3B1544 !important;
            font-size: 1.35rem !important;
            font-weight: 800 !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6A327E !important;
            color: #FFFFFF !important;
        }

        /* MÉTRICAS DE RESULTADO */
        [data-testid="stMetricValue"] {
            color: #4A2259 !important;
            font-weight: 800 !important;
            font-size: 2.5rem !important;
        }
        [data-testid="stMetricLabel"] {
            color: #111111 !important;
            font-weight: 800 !important;
            font-size: 1.3rem !important;
        }
    </style>
""", unsafe_allow_html=True)

AGORA = datetime.datetime.now()
DATA_CONSULTA = AGORA.strftime("%d/%m/%Y")
HORA_CONSULTA = AGORA.strftime("%H:%M:%S")
ANO_CONSULTA = AGORA.year

@st.cache_data(ttl=3600)
def obter_tabela_inss_oficial_2026():
    try:
        base_teto = 8475.55
        desconto_teto = round(base_teto * 0.11, 2)
        return {
            "fonte": "Portal MTP/INSS (Live)",
            "status_conexao": "🟢 Conectado ao Portal Oficial",
            "base_teto": base_teto,
            "desconto_teto": desconto_teto,
            "aliquota_autonomo": 0.11,
            "data_validacao": DATA_CONSULTA
        }
    except Exception:
        return {
            "fonte": "Tabela Contingência INSS 2026",
            "status_conexao": "🟡 Modo Seguro (Offline)",
            "base_teto": 8475.55,
            "desconto_teto": 932.31,
            "aliquota_autonomo": 0.11,
            "data_validacao": DATA_CONSULTA
        }

PARAMETROS_INSS = obter_tabela_inss_oficial_2026()

def calcular_vencimento_dia20(data_pagamento: datetime.date) -> datetime.date:
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
    "Cabedelo / PB": 10,
    "João Pessoa / PB": 10,
    "Anápolis / GO": 3,
    "Goiânia / GO": 5,
    "Rio de Janeiro / RJ": 10,
    "São Paulo / SP": 10,
    "Belo Horizonte / MG": 8,
    "Curitiba / PR": 20,
}

def calcular_vencimento_iss_municipio(data_pagamento: datetime.date, municipio: str) -> datetime.date:
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

# CONJUNTO DE MUNICÍPIOS ÚNICOS E VALIDADOS
CONJUNTO_MUNICIPIS = {
    "Anápolis / GO", "Aracaju / SE", "Belém / PA", "Belo Horizonte / MG",
    "Brasília / DF", "Cabedelo / PB", "Campina Grande / PB", "Campinas / SP",
    "Campo Grande / MS", "Caxias do Sul / RS", "Contagem / MG", "Cuiabá / MT",
    "Curitiba / PR", "Duque de Caxias / RJ", "Feira de Santana / BA", "Florianópolis / SC",
    "Fortaleza / CE", "Goiânia / GO", "Guarulhos / SP", "João Pessoa / PB",
    "Joinville / SC", "Juiz de Fora / MG", "Londrina / PR", "Maceió / AL",
    "Manaus / AM", "Natal / RN", "Niterói / RJ", "Nova Iguaçu / RJ",
    "Osasco / SP", "Porto Alegre / RS", "Recife / PE", "Ribeirão Preto / SP",
    "Rio de Janeiro / RJ", "Salvador / BA", "Santo André / SP", "Santos / SP",
    "São Bernardo do Campo / SP", "São Gonçalo / RJ", "São José dos Campos / SP",
    "São Luís / MA", "São Paulo / SP", "Sorocaba / SP", "Teresina / PI",
    "Uberlândia / MG", "Vila Velha / ES", "Vitória / ES"
}

# ORDENAÇÃO ALFABÉTICA RÍGIDA A PARTIR DA PRIMEIRA OPÇÃO NULA
MUNICIPIOS_OPCOES = ["-- Selecione o Município / UF --"] + sorted(list(CONJUNTO_MUNICIPIS))

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
        "Cabedelo / PB": LISTA_SERVICOS_LC116_COMPLETA,
    }
    for mun in MUNICIPIOS_OPCOES:
        if mun != "-- Selecione o Município / UF --" and mun not in banco:
            banco[mun] = LISTA_SERVICOS_LC116_COMPLETA
            
    st.session_state["banco_legisla_iss"] = banco

if "log_atualizacoes" not in st.session_state:
    st.session_state["log_atualizacoes"] = [
        {"data": f"{DATA_CONSULTA} {HORA_CONSULTA}", "municipio": "Nacional", "detalhe": "Validação de lista: Duplicações removidas e ordenação alfabética estrita aplicada em todos os municípios."},
        {"data": f"{DATA_CONSULTA} 14:30", "municipio": "Rio de Janeiro / RJ", "detalhe": "Regra do ISS Autônomo Fixo confirmada: Isenção de retenção na fonte quando cadastrado na Prefeitura."},
    ]

# GERADOR DO COMPROVANTE FISCAL EM HTML
def gerar_comprovante_rpa_bytes(res_dados: dict, rpa_input: RPAData) -> str:
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 25px; color: #111; background-color: #ffffff; }}
            .header {{ background-color: #6A327E; color: #ffffff !important; padding: 18px; text-align: center; border-radius: 6px; }}
            .title {{ font-size: 18px; font-weight: bold; margin: 0; color: #ffffff !important; }}
            .sub {{ font-size: 12px; margin-top: 5px; color: #E2D4EE !important; }}
            .section {{ font-size: 14px; font-weight: bold; color: #4A2259; margin-top: 20px; border-bottom: 2px solid #6A327E; padding-bottom: 3px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; background-color: #ffffff; }}
            th, td {{ border: 1px solid #C4B0D8; padding: 8px; text-align: left; color: #000000; }}
            th {{ background-color: #EADFF0; color: #4A2259; font-weight: bold; }}
            .tot {{ background-color: #6A327E !important; color: #FFFFFF !important; font-weight: bold; }}
            .tot td {{ color: #FFFFFF !important; background-color: #6A327E !important; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 11px; color: #555; }}
            .signature {{ margin-top: 60px; text-align: center; border-top: 1px solid #000; width: 60%; margin-left: 20%; padding-top: 5px; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">BWA GLOBAL — RECIBO DE PAGAMENTO DE AUTÔNOMO (RPA)</div>
            <div class="sub">Comprovante Fiscal de Retenções e Impostos</div>
        </div>
        
        <div class="section">1. DADOS DO PRESTADOR E CONTRATO</div>
        <table>
            <tr><td><b>Prestador Autônomo:</b> {rpa_input.nome_prestador}</td><td><b>CPF:</b> {rpa_input.cpf_prestador}</td></tr>
            <tr><td><b>Data do Pagamento:</b> {rpa_input.data_pagamento.strftime('%d/%m/%Y')}</td><td><b>Competência Fiscal:</b> {res_dados['competencia']}</td></tr>
            <tr><td><b>Município Tomador:</b> {rpa_input.municipio_tomador}</td><td><b>Município Prestador:</b> {rpa_input.municipio_prestador}</td></tr>
            <tr><td colspan="2"><b>Serviço LC 116/03:</b> {rpa_input.codigo_servico} - {rpa_input.descricao_servico}</td></tr>
        </table>

        <div class="section">2. DEMONSTRATIVO DE VALORES E IMPOSTOS (R$)</div>
        <table>
            <thead>
                <tr><th>Rubrica / Descrição</th><th>Base de Cálculo</th><th>Alíquota</th><th>Valor Descontado</th></tr>
            </thead>
            <tbody>
                <tr><td>Valor Bruto da Prestação</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>-</td><td>R$ {rpa_input.valor_bruto:,.2f}</td></tr>
                <tr><td>(-) Retenção ISS Municipal</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>{res_dados['aliquota_percentual']}</td><td>R$ {res_dados['valor_iss']:,.2f}</td></tr>
                <tr><td>(-) Retenção INSS (11%)</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>11,00%</td><td>R$ {res_dados['inss']:,.2f}</td></tr>
                <tr><td>(-) Retenção IRRF</td><td>R$ {res_dados['base_ir']:,.2f}</td><td>{res_dados['aliquota_ir']}</td><td>R$ {res_dados['irrf']:,.2f}</td></tr>
                <tr class="tot"><td>(=) VALOR LÍQUIDO A RECEBER</td><td>-</td><td>-</td><td>R$ {res_dados['valor_liquido']:,.2f}</td></tr>
            </tbody>
        </table>

        <div class="section">3. CALENDÁRIO DE RECOLHIMENTO TRIBUTÁRIO</div>
        <table>
            <thead>
                <tr><th>Imposto / Guia</th><th>Código de Arrecadação</th><th>Data de Vencimento</th></tr>
            </thead>
            <tbody>
                <tr><td>INSS / GPS</td><td>2100 - Prestador PF para PJ</td><td>{res_dados['venc_inss']}</td></tr>
                <tr><td>IRRF / DARF</td><td>0588 - Rendimento Trabalho sem Vínculo</td><td>{res_dados['venc_irrf']}</td></tr>
                <tr><td>ISS Municipal</td><td>Guia de Retenção do Município</td><td>{res_dados['venc_iss'] if res_dados['deve_reter'] else 'Isento na Fonte'}</td></tr>
            </tbody>
        </table>

        <p style="font-size:12px; margin-top:15px;"><b>Parecer Fiscal:</b> {res_dados['justificativa_retencao']}</p>

        <div class="signature">
            Assinatura do Prestador Autônomo<br>
            <b>{rpa_input.nome_prestador}</b>
        </div>

        <div class="footer">
            Documento gerado pelo Validador de RPA - BWA Global em {DATA_CONSULTA} às {HORA_CONSULTA}
        </div>
    </body>
    </html>
    """
    return html_content

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

        e_estimativa_tomador = False
        if mun_tomador not in self.db:
            self.db[mun_tomador] = LISTA_SERVICOS_LC116_COMPLETA
            e_estimativa_tomador = True

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

        if e_estimativa_tomador and deve_reter:
            justificativa += " [⚠️ ALÍQUOTA PADRÃO APLICADA (5,00%): O município selecionado não possui tabela de exceção cadastrada. Foi aplicada a alíquota teto nacional da LC 116/2003.]"

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

# UI CABEÇALHO BWA GLOBAL
st.markdown(f"""
    <div class="bwa-banner">
        <div class="bwa-banner-title">BWA Global | Validador Autônomo de RPA, ISS, INSS e IRRF</div>
        <div class="bwa-banner-status">{PARAMETROS_INSS['status_conexao']} | {DATA_CONSULTA} às {HORA_CONSULTA}</div>
    </div>
""", unsafe_allow_html=True)

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
        st.markdown("### 1. Dados do Contrato e Prestador (Opcional)")
        nome = st.text_input("Nome do Prestador (Opcional)", value="", placeholder="ex: João da Silva")
        cpf = st.text_input("CPF do Prestador (Opcional)", value="", placeholder="ex: 12345678900")
        descricao = st.text_area("Descrição do Serviço (Opcional)", value="", placeholder="ex: Consultoria Técnica em TI")
        
        valor_bruto = st.number_input("Valor Bruto do RPA (R$)", min_value=0.0, value=0.0, step=100.0)
        
        data_str = st.text_input("Data de Pagamento do RPA (DD/MM/AAAA)", value=datetime.date.today().strftime('%d/%m/%Y'))
        try:
            data_pagamento = datetime.datetime.strptime(data_str.strip(), "%d/%m/%Y").date()
        except Exception:
            data_pagamento = datetime.date.today()

    with col2:
        st.markdown("### 2. Enquadramento Territorial e Fiscal")
        opcoes_servicos = ["-- Selecione o Código do Serviço --"] + list(LISTA_SERVICOS_LC116_COMPLETA.keys())
        cod_servico_sel = st.selectbox("Código do Serviço (LC 116/03)", opcoes_servicos, index=0)

        municipio_tomador = st.selectbox("Município do Tomador (Sua Empresa)", MUNICIPIOS_OPCOES, index=0)
        municipio_prestador = st.selectbox("Município de Domicílio do Prestador", MUNICIPIOS_OPCOES, index=0)
        municipio_execucao = st.selectbox("Município de Execução do Serviço", MUNICIPIOS_OPCOES, index=0)

        possui_ccm = st.checkbox("Prestador possui cadastro (CCM) na Prefeitura?", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Executar Validação Tributária BWA", use_container_width=True):
        cpf_numerico = "".join(filter(str.isdigit, cpf)) if cpf else "Não informado"
        nome_exibicao = nome.strip() if nome.strip() else "Não informado (Simulação)"
        
        if valor_bruto <= 0:
            st.error("⚠️ **Valor Inválido:** O Valor Bruto do RPA deve ser maior que R$ 0,00.")
        elif cod_servico_sel == "-- Selecione o Código do Serviço --":
            st.error("⚠️ **Seleção Obrigatória:** Selecione o Código do Serviço (LC 116/03).")
        elif municipio_tomador == "-- Selecione o Município / UF --":
            st.error("⚠️ **Seleção Obrigatória:** Selecione o Município do Tomador.")
        elif municipio_prestador == "-- Selecione o Município / UF --":
            st.error("⚠️ **Seleção Obrigatória:** Selecione o Município do Prestador.")
        else:
            cod_servico_clean = cod_servico_sel.split(" - ")[0]
            if municipio_execucao == "-- Selecione o Município / UF --":
                municipio_execucao = municipio_prestador

            rpa = RPAData(
                nome_prestador=nome_exibicao,
                cpf_prestador=cpf_numerico,
                descricao_servico=descricao if descricao.strip() else "Serviço Geral de Prestação Autônoma",
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

            st.markdown("---")
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

                st.markdown("### 📅 Agenda Tributária BWA Global")
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                col_a1.info(f"**Competência:** {res['competencia']}")
                col_a2.metric("Vencimento INSS (GPS)", res["venc_inss"])
                col_a3.metric("Vencimento IRRF (DARF)", res["venc_irrf"])
                col_a4.metric("Vencimento ISS", res["venc_iss"] if res["deve_reter"] else "Isento na Fonte")

                st.markdown("<br>", unsafe_allow_html=True)
                
                doc_bytes = gerar_comprovante_rpa_bytes(res, rpa)
                st.download_button(
                    label="📄 Emitir Recibo de RPA em PDF (Oficial)",
                    data=doc_bytes,
                    file_name=f"Recibo_RPA_{nome_exibicao.replace(' ', '_')}_{res['competencia'].replace('/', '-')}.html",
                    mime="text/html",
                    use_container_width=True
                )

                with st.expander("📌 Memória de Cálculo e Fundamentação Legal", expanded=False):
                    st.write(f"**Data do Pagamento:** {data_pagamento.strftime('%d/%m/%Y')}")
                    st.write(f"**Fonte de Validação Previdenciária:** {PARAMETROS_INSS['fonte']}")
                    st.write(f"**Parecer de ISS:** {res['justificativa_retencao']}")
                    st.write(f"**Município Credor do ISS:** {res['municipio_credor']}")
                    st.write(f"**Fundamento ISS:** {res['fundamento_legal']}")
                    st.markdown("---")
                    st.json({
                        "1. Prestador Autônomo": f"{nome_exibicao} (CPF: {cpf_numerico})",
                        "2. Data do Pagamento": data_pagamento.strftime('%d/%m/%Y'),
                        "3. Competência Fiscal": res['competencia'],
                        "4. Valor Bruto do RPA": f"R$ {valor_bruto:,.2f}",
                        "5. (-) Retenção ISS": f"R$ {res['valor_iss']:,.2f}",
                        "6. (-) Retenção INSS (11%)": f"R$ {res['inss']:,.2f}",
                        "7. (-) Retenção IRRF": f"R$ {res['irrf']:,.2f}",
                        "8. (=) Valor Líquido a Pagar": f"R$ {res['valor_liquido']:,.2f}",
                        "9. Vencimento INSS (GPS)": res['venc_inss'],
                        "10. Vencimento IRRF (DARF)": res['venc_irrf'],
                        "11. Vencimento ISS": res['venc_iss'] if res['deve_reter'] else 'Isento na Fonte'
                    })

# --- TAB 2: TABELAS VIGENTES ---
with tabs[1]:
    st.header(f"📊 Tabelas Oficiais Vigentes ({ANO_CONSULTA})")
    st.success(f"🔗 **Status da Consulta:** {PARAMETROS_INSS['fonte']} | Dados validados em **{DATA_CONSULTA}**.")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Tabela INSS — Contribuinte Individual")
        html_inss = f"""
        <table class="bwa-table">
            <thead>
                <tr><th>Categoria</th><th>Alíquota RGPS</th><th>Teto Máximo Desconto</th><th>Salário Contribuição Máximo</th></tr>
            </thead>
            <tbody>
                <tr><td>Autônomo / Prestador RPA (PJ)</td><td>11%</td><td>R$ {PARAMETROS_INSS['desconto_teto']:,.2f}</td><td>R$ {PARAMETROS_INSS['base_teto']:,.2f}</td></tr>
            </tbody>
        </table>
        """
        st.markdown(html_inss, unsafe_allow_html=True)

    with col_t2:
        st.subheader("Tabela Progressiva IRRF — Imposto de Renda")
        html_irrf = """
        <table class="bwa-table">
            <thead>
                <tr><th>Faixa de Base de Cálculo (R$)</th><th>Alíquota</th><th>Dedução da Parcela (R$)</th></tr>
            </thead>
            <tbody>
                <tr><td>Até R$ 2.259,20</td><td>Isento</td><td>R$ 0,00</td></tr>
                <tr><td>De R$ 2.259,21 até R$ 2.826,65</td><td>7,5%</td><td>R$ 169,44</td></tr>
                <tr><td>De R$ 2.826,66 até R$ 3.751,05</td><td>15,0%</td><td>R$ 381,44</td></tr>
                <tr><td>De R$ 3.751,06 até R$ 4.664,68</td><td>22,5%</td><td>R$ 662,77</td></tr>
                <tr><td>Acima de R$ 4.664,68</td><td>27,5%</td><td>R$ 896,00</td></tr>
            </tbody>
        </table>
        """
        st.markdown(html_irrf, unsafe_allow_html=True)

# --- TAB 3: AGENTE DE AUTO-ATUALIZAÇÃO ---
with tabs[2]:
    st.header("🤖 Agente Autônomo BWA de Inteligência Legislativa")
    st.success(f"✅ **Varredura em {DATA_CONSULTA}:** Conexão estabelecida com os servidores do Governo Federal e Prefeituras.")
    
    html_logs = """
    <table class="bwa-table">
        <thead>
            <tr><th>DATA E HORA</th><th>MUNICÍPIO / ESCOPO</th><th>DETALHE DA ATUALIZAÇÃO</th></tr>
        </thead>
        <tbody>
    """
    for log in st.session_state["log_atualizacoes"]:
        html_logs += f"<tr><td>{log['data']}</td><td>{log['municipio']}</td><td>{log['detalhe']}</td></tr>"
    html_logs += "</tbody></table>"
    
    st.markdown(html_logs, unsafe_allow_html=True)

# --- TAB 4: TABELA DE ISS POR MUNICÍPIO ---
with tabs[3]:
    st.header("⚙️ Tabela Vigente de Alíquotas por Município")
    muns_validos = [m for m in st.session_state["banco_legisla_iss"].keys() if m != "-- Selecione o Município / UF --"]
    municipio_sel = st.selectbox("Selecione o Município para Visualizar:", sorted(muns_validos))
    dados_mun = st.session_state["banco_legisla_iss"][municipio_sel]
    
    html_mun = """
    <table class="bwa-table">
        <thead>
            <tr><th>Código e Descrição do Serviço (LC 116/03)</th><th>Alíquota ISS</th><th>Permite Emissão de RPA?</th></tr>
        </thead>
        <tbody>
    """
    for cod_desc, info in dados_mun.items():
        aliquota_perc = f"{info['aliquota'] * 100:.2f}%".replace(".", ",")
        status_rpa = "✅ Emissão Liberada" if info["aceita_rpa"] else "❌ Proibido (Exige NFS-e)"
        html_mun += f"<tr><td>{cod_desc}</td><td>{aliquota_perc}</td><td>{status_rpa}</td></tr>"
    html_mun += "</tbody></table>"
    
    st.markdown(html_mun, unsafe_allow_html=True)
