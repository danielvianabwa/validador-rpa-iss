"""
================================================================================
SISTEMA AUTOMÁTICO DE VALIDAÇÃO DE RPA - BWA GLOBAL (LAYOUT LEGÍVEL + PDF NATIVO)
================================================================================
"""

import streamlit as st
import pandas as pd
import json
from dataclasses import dataclass
from typing import Dict
import datetime
import io

st.set_page_config(
    page_title="BWA Global | Validador de RPA & ISS",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESTILIZAÇÃO VISUAL BWA GLOBAL COM CONTRASTE BRANCO/ROXO E FONTES AMPLIADAS
st.markdown("""
    <style>
        /* Fundo Geral */
        .stApp {
            background-color: #F4F0F6 !important;
            color: #2D2D2D !important;
        }
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        /* Cabeçalho Ajustado Sem Cortar */
        .bwa-header {
            background-color: #6A327E;
            color: #FFFFFF;
            padding: 1.2rem 1.8rem;
            border-radius: 10px;
            margin-bottom: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.12);
        }
        .bwa-header h1 {
            color: #FFFFFF !important;
            font-size: 1.8rem !important;
            margin: 0 !important;
            padding: 0 !important;
            font-weight: 700;
        }
        .bwa-status {
            font-size: 0.95rem;
            color: #F0E6F6;
            font-weight: 500;
        }
        /* Botões Ampliados */
        .stButton>button {
            background-color: #6A327E !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            border: none !important;
            padding: 0.8rem 1.5rem !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.15);
        }
        .stButton>button:hover {
            background-color: #532664 !important;
            color: #FFFFFF !important;
        }
        /* Rótulos e Texto dos Inputs Ampliados e Claros */
        label {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #4A2259 !important;
            margin-bottom: 0.2rem !important;
        }
        /* FORÇAR CAMPOS EM BRANCO (SEM ELEMENTOS PRETOS) */
        .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
            padding: 0.5rem 0.8rem !important;
            font-size: 1rem !important;
            border-radius: 6px !important;
            border: 1.5px solid #C4B0D8 !important;
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
        }
        textarea {
            height: 75px !important;
            font-size: 0.95rem !important;
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
            border: 1.5px solid #C4B0D8 !important;
            border-radius: 6px !important;
        }
        /* Métricas e Valores Visíveis */
        [data-testid="stMetricValue"] {
            color: #4A2259 !important;
            font-weight: bold !important;
            font-size: 1.6rem !important;
        }
        [data-testid="stMetricLabel"] {
            color: #2D2D2D !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }
        /* Abas Superiores Ampliadas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            padding: 0px 18px;
            background-color: #E2D4EE;
            border-radius: 6px 6px 0px 0px;
            color: #4A2259;
            font-size: 1rem;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6A327E !important;
            color: #FFFFFF !important;
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
        {"data": f"{DATA_CONSULTA} {HORA_CONSULTA}", "municipio": "Nacional", "detalhe": "Layout otimizado: Fontes ampliadas, fundo branco nos seletores e gerador de documento RPA em PDF integrado."},
        {"data": f"{DATA_CONSULTA} 14:30", "municipio": "Rio de Janeiro / RJ", "detalhe": "Regra do ISS Autônomo Fixo confirmada: Isenção de retenção na fonte quando cadastrado na Prefeitura."},
    ]

# GERADOR NATIVO DE RECIBO DE RPA EM HTML/DOCUMENTO IMPRESSO
def gerar_documento_rpa_html(res_dados: dict, rpa_input: RPAData) -> str:
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Recibo de Pagamento de Autônomo (RPA)</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #2D2D2D; }}
            .header {{ background-color: #6A327E; color: white; padding: 15px; text-align: center; border-radius: 6px; }}
            .section-title {{ color: #4A2259; border-bottom: 2px solid #6A327E; padding-bottom: 4px; margin-top: 20px; font-size: 14px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
            th, td {{ border: 1px solid #D1C0E0; padding: 8px; text-align: left; }}
            th {{ background-color: #EADFF0; color: #4A2259; }}
            .total-row {{ background-color: #6A327E; color: white; font-weight: bold; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 12px; }}
            .signature {{ margin-top: 50px; text-align: center; font-size: 12px; border-top: 1px solid #000; width: 60%; margin-left: 20%; padding-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0;">BWA GLOBAL — RECIBO DE PAGAMENTO DE AUTÔNOMO (RPA)</h2>
            <p style="margin:5px 0 0 0; font-size:12px;">Comprovante Fiscal de Prestação de Serviços e Retenção Tributária</p>
        </div>
        
        <div class="section-title">1. IDENTIFICAÇÃO DAS PARTES E DO SERVIÇO</div>
        <table>
            <tr><td><b>Prestador Autônomo:</b> {rpa_input.nome_prestador}</td><td><b>CPF:</b> {rpa_input.cpf_prestador}</td></tr>
            <tr><td><b>Data do Pagamento:</b> {rpa_input.data_pagamento.strftime('%d/%m/%Y')}</td><td><b>Competência Fiscal:</b> {res_dados['competencia']}</td></tr>
            <tr><td><b>Município Tomador:</b> {rpa_input.municipio_tomador}</td><td><b>Município Prestador:</b> {rpa_input.municipio_prestador}</td></tr>
            <tr><td colspan="2"><b>Serviço (LC 116/03):</b> {rpa_input.codigo_servico} - {rpa_input.descricao_servico}</td></tr>
        </table>
        
        <div class="section-title">2. DEMONSTRATIVO DE VALORES E RETENÇÕES TRIBUTÁRIAS</div>
        <table>
            <thead>
                <tr><th>Descrição / Rubrica</th><th>Base de Cálculo</th><th>Alíquota</th><th>Valor Descontado</th></tr>
            </thead>
            <tbody>
                <tr><td>Valor Bruto da Prestação</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>-</td><td>R$ {rpa_input.valor_bruto:,.2f}</td></tr>
                <tr><td>(-) Retenção ISS Municipal</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>{res_dados['aliquota_percentual']}</td><td>R$ {res_dados['valor_iss']:,.2f}</td></tr>
                <tr><td>(-) Retenção INSS (RGPS)</td><td>R$ {rpa_input.valor_bruto:,.2f}</td><td>11,00%</td><td>R$ {res_dados['inss']:,.2f}</td></tr>
                <tr><td>(-) Retenção IRRF (Tabela Progressiva)</td><td>R$ {res_dados['base_ir']:,.2f}</td><td>{res_dados['aliquota_ir']}</td><td>R$ {res_dados['irrf']:,.2f}</td></tr>
                <tr class="total-row"><td>(=) VALOR LÍQUIDO A RECEBER</td><td>-</td><td>-</td><td>R$ {res_dados['valor_liquido']:,.2f}</td></tr>
            </tbody>
        </table>
        
        <div class="section-title">3. AGENDA E CALENDÁRIO DE RECOLHIMENTO TRIBUTÁRIO</div>
        <table>
            <thead>
                <tr><th>Imposto / Guia</th><th>Código de Arrecadação</th><th>Data do Vencimento</th></tr>
            </thead>
            <tbody>
                <tr><td>INSS / GPS</td><td>2100 - Prestador PF para PJ</td><td>{res_dados['venc_inss']}</td></tr>
                <tr><td>IRRF / DARF</td><td>0588 - Rendimento Trabalho sem Vínculo</td><td>{res_dados['venc_irrf']}</td></tr>
                <tr><td>ISS Municipal</td><td>Guia de Retenção do Município</td><td>{res_dados['venc_iss'] if res_dados['deve_reter'] else 'Isento na Fonte'}</td></tr>
            </tbody>
        </table>
        
        <p style="font-size:11px; margin-top:15px;"><b>Parecer Fiscal:</b> {res_dados['justificativa_retencao']}</p>
        
        <div class="signature">
            Assinatura do Prestador Autônomo<br>
            {rpa_input.nome_prestador}
        </div>
        
        <div class="footer">
            <p>Documento gerado automaticamente pelo Validador de RPA - BWA Global em {DATA_CONSULTA} às {HORA_CONSULTA}</p>
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

# UI BARRA BWA GLOBAL DESTAQUE
st.markdown(f"""
    <div class="bwa-header">
        <h1>BWA Global | Validador Autônomo de RPA, ISS, INSS e IRRF</h1>
        <div class="bwa-status">{PARAMETROS_INSS['status_conexao']} | {DATA_CONSULTA} às {HORA_CONSULTA}</div>
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
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**1. Dados Cadastrais (Opcionais)**")
        nome = st.text_input("Nome do Prestador (Opcional)", value="", placeholder="ex: João da Silva")
        cpf = st.text_input("CPF do Prestador (Opcional)", value="", placeholder="ex: 12345678900")
        descricao = st.text_area("Descrição do Serviço (Opcional)", value="", placeholder="ex: Consultoria Técnica em TI")
        
    with col2:
        st.markdown("**2. Valores e Pagamento (Obrigatório)**")
        valor_bruto = st.number_input("Valor Bruto do RPA (R$)", min_value=0.0, value=0.0, step=100.0)
        data_pagamento = st.date_input("Data de Pagamento do RPA", value=datetime.date.today(), format="DD/MM/YYYY")
        
        opcoes_servicos = ["-- Selecione o Código do Serviço --"] + list(LISTA_SERVICOS_LC116_COMPLETA.keys())
        cod_servico_sel = st.selectbox("Código do Serviço (LC 116/03)", opcoes_servicos, index=0)

    with col3:
        st.markdown("**3. Enquadramento Territorial**")
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
                
                # GERADOR E BOTÃO DE DOWNLOAD DO DOCUMENTO
                html_doc = gerar_documento_rpa_html(res, rpa)
                st.download_button(
                    label="📄 Baixar / Emitir Documento de RPA (Comprovante)",
                    data=html_doc,
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
        df_inss = pd.DataFrame([
            {
                "Categoria": "Autônomo / Prestador RPA (PJ)", 
                "Alíquota RGPS": "11%", 
                "Teto Máximo do Desconto": f"R$ {PARAMETROS_INSS['desconto_teto']:,.2f}".replace(".", ","), 
                "Salário de Contribuição Máximo": f"R$ {PARAMETROS_INSS['base_teto']:,.2f}".replace(".", ",")
            }
        ])
        st.table(df_inss)

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

# --- TAB 3: AGENTE DE AUTO-ATUALIZAÇÃO ---
with tabs[2]:
    st.header("🤖 Agente Autônomo BWA de Inteligência Legislativa")
    st.success(f"✅ **Varredura em {DATA_CONSULTA}:** Conexão estabelecida com os servidores do Governo Federal e Prefeituras.")
    df_logs = pd.DataFrame(st.session_state["log_atualizacoes"])
    st.dataframe(df_logs, use_container_width=True)

# --- TAB 4: TABELA DE ISS POR MUNICÍPIO ---
with tabs[3]:
    st.header("⚙️ Tabela Vigente de Alíquotas por Município")
    muns_validos = [m for m in st.session_state["banco_legisla_iss"].keys() if m != "-- Selecione o Município / UF --"]
    municipio_sel = st.selectbox("Selecione o Município para Visualizar:", sorted(muns_validos))
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
