"""
=============================================================================
sinan_dicionario.py
=============================================================================
Mapeamento das colunas do SINAN / Violencia Interpessoal e Autoprovocada.

Fonte: Dicionario de Dados - SINAN NET - Versao 5.0 / Patch 5.1
       Ministerio da Saude / SVS / GT-SINAN - revisado em junho/2015.

Duas estruturas:
    LABELS      -> nome DBF (como vem no arquivo) : nome legivel
    CATEGORIES  -> nome DBF : {codigo : categoria}

Campos sem CATEGORIES sao texto livre, data, codigo IBGE/CID ou identificador.

ATENCAO: o dicionario e da versao 5.0/5.1. Fichas de anos diferentes podem
ter campos a mais ou a menos. Sempre rode auditar_colunas() antes de usar.
=============================================================================
"""

# =============================================================================
# Blocos de codigo que se repetem em dezenas de campos
# =============================================================================

SIM_NAO = {"1": "Sim", "2": "Nao", "9": "Ignorado"}

SIM_NAO_NA = {"1": "Sim", "2": "Nao", "8": "Nao se aplica", "9": "Ignorado"}


# =============================================================================
# LABELS - nome DBF : nome legivel
# =============================================================================


LABELS = {
    # --- Identificacao da notificacao ---
    "NU_NOTIFIC": "Numero da notificacao",
    "TP_NOT": "Tipo de notificacao",
    "ID_AGRAVO": "Agravo (CID-10)",
    "DT_NOTIFIC": "Data da notificacao",
    "SEM_NOT": "Semana epidemiologica da notificacao",
    "NU_ANO": "Ano da notificacao",
    "SG_UF_NOT": "UF de notificacao",
    "ID_MUNICIP": "Municipio de notificacao",
    "ID_REGIONA": "Regional de saude de notificacao",
    "TP_UNI_EXT": "Tipo de unidade notificadora",
    "NM_UNI_EXT": "Nome da unidade notificadora",
    "CO_UNI_EXT": "Codigo da unidade notificadora",
    "ID_UNIDADE": "Unidade de saude",
    "CNES_NOT": "Codigo CNES da unidade",
    "DT_OCOR": "Data da ocorrencia da violencia",
    "SEM_PRI": "Semana epidemiologica da ocorrencia",
    # --- Identificacao da vitima ---
    "NM_PACIENT": "Nome do paciente",
    "DT_NASC": "Data de nascimento",
    "NU_IDADE_N": "Idade (codificada: 1o digito = unidade)",
    "CS_SEXO": "Sexo",
    "CS_GESTANT": "Gestante",
    "CS_RACA": "Raca/cor",
    "CS_ESCOL_N": "Escolaridade",
    "ID_CNS_SUS": "Numero do cartao SUS",
    "NM_MAE_PAC": "Nome da mae",
    "ID_OCUPA_N": "Ocupacao (CBO)",
    "SIT_CONJUG": "Situacao conjugal",
    "ORIENT_SEX": "Orientacao sexual",
    "IDENT_GEN": "Identidade de genero",
    # --- Residencia da vitima ---
    "SG_UF": "UF de residencia",
    "ID_MN_RESI": "Municipio de residencia",
    "ID_RG_RESI": "Regional de saude de residencia",
    "ID_DISTRIT": "Distrito de residencia",
    "ID_BAIRRO": "Codigo do bairro de residencia",
    "NM_BAIRRO": "Nome do bairro de residencia",
    "ID_LOGRADO": "Codigo do logradouro de residencia",
    "NM_LOGRADO": "Logradouro de residencia",
    "NU_NUMERO": "Numero do logradouro de residencia",
    "DS_COMPL": "Complemento do logradouro de residencia",
    "ID_GEO1": "Geo campo 1",
    "ID_GEO2": "Geo campo 2",
    "DS_REF_RES": "Ponto de referencia da residencia",
    "NU_CEP": "CEP de residencia",
    "DDD": "DDD",
    "FONE": "Telefone",
    "ZONA": "Zona de residencia",
    "ID_PAIS": "Pais de residencia",
    # --- Deficiencias e transtornos ---
    "DEF_TRANS": "Possui deficiencia ou transtorno",
    "DEF_FISICA": "Deficiencia fisica",
    "DEF_MENTAL": "Deficiencia intelectual",
    "DEF_VISUAL": "Deficiencia visual",
    "DEF_AUDITI": "Deficiencia auditiva",
    "TRAN_MENT": "Transtorno mental",
    "TRAN_COMP": "Transtorno de comportamento",
    "DEF_OUT": "Outras deficiencias ou sindromes",
    "DEF_ESPEC": "Outras deficiencias (especificar)",
    # --- Local da ocorrencia ---
    "SG_UF_OCOR": "UF de ocorrencia",
    "ID_MN_OCOR": "Municipio de ocorrencia",
    "ID_DIS_OCOR": "Distrito de ocorrencia",
    "ID_BA_OCOR": "Codigo do bairro de ocorrencia",
    "NM_BA_OCOR": "Nome do bairro de ocorrencia",
    "ID_LOG_OCO": "Codigo do logradouro de ocorrencia",
    "NO_LOG_OCO": "Logradouro de ocorrencia",
    "NM_LOG_RES": "Numero do logradouro de ocorrencia",
    "DS_COMP_OCOR": "Complemento do logradouro de ocorrencia",
    "ID_GEO3": "Geo campo 3",
    "ID_GEO4": "Geo campo 4",
    "DS_REF_OCOR": "Ponto de referencia da ocorrencia",
    "ZONA_OCOR": "Zona de ocorrencia",
    "HORA_OCOR": "Hora da ocorrencia",
    "LOCAL_OCOR": "Local de ocorrencia",
    "LOCAL_ESPE": "Local de ocorrencia - outro (especificar)",
    # --- Caracterizacao da violencia ---
    "OUT_VEZES": "Ocorreu outras vezes (violencia de repeticao)",
    "LES_AUTOP": "A lesao foi autoprovocada",
    "VIOL_MOTIV": "Violencia motivada por",
    "VIOL_FISIC": "Tipo de violencia - fisica",
    "VIOL_PSICO": "Tipo de violencia - psicologica/moral",
    "VIOL_TORT": "Tipo de violencia - tortura",
    "VIOL_SEXU": "Tipo de violencia - sexual",
    "VIOL_TRAF": "Tipo de violencia - trafico de seres humanos",
    "VIOL_FINAN": "Tipo de violencia - financeira/economica",
    "VIOL_NEGLI": "Tipo de violencia - negligencia/abandono",
    "VIOL_INFAN": "Tipo de violencia - trabalho infantil",
    "VIOL_LEGAL": "Tipo de violencia - intervencao legal",
    "VIOL_OUTR": "Tipo de violencia - outros",
    "VIOL_ESPEC": "Outro tipo de violencia (especificar)",
    # --- Meio de agressao ---
    "AG_FORCA": "Meio - forca corporal/espancamento",
    "AG_ENFOR": "Meio - enforcamento",
    "AG_OBJETO": "Meio - objeto contundente",
    "AG_CORTE": "Meio - objeto perfuro-cortante",
    "AG_QUENTE": "Meio - substancia/objeto quente",
    "AG_ENVEN": "Meio - envenenamento/intoxicacao",
    "AG_FOGO": "Meio - arma de fogo",
    "AG_AMEACA": "Meio - ameaca",
    "AG_OUTROS": "Meio - outro",
    "AG_ESPEC": "Outro meio de agressao (especificar)",
    # --- Violencia sexual ---
    "SEX_ASSEDI": "Violencia sexual - assedio",
    "SEX_ESTUPR": "Violencia sexual - estupro",
    "SEX_PORNO": "Violencia sexual - pornografia infantil",
    "SEX_EXPLO": "Violencia sexual - exploracao sexual",
    "SEX_OUTRO": "Violencia sexual - outro",
    "SEX_ESPEC": "Outro tipo de violencia sexual (especificar)",
    # --- Procedimentos realizados ---
    "PROC_DST": "Procedimento - profilaxia DST",
    "PROC_HIV": "Procedimento - profilaxia HIV",
    "PROC_HEPB": "Procedimento - profilaxia hepatite B",
    "PROC_SANG": "Procedimento - coleta de sangue",
    "PROC_SEMEN": "Procedimento - coleta de semen",
    "PROC_VAGINA": "Procedimento - coleta de secrecao vaginal",
    "PROC_CONTR": "Procedimento - contracepcao de emergencia",
    "PROC_ABORT": "Procedimento - aborto previsto em lei",
    # --- Provavel autor da agressao ---
    "NUM_ENVOLV": "Numero de envolvidos",
    "REL_PAI": "Autor - pai",
    "REL_MAE": "Autor - mae",
    "REL_PAD": "Autor - padrasto",
    "REL_MAD": "Autor - madrasta",
    "REL_CONJ": "Autor - conjuge",
    "REL_EXCON": "Autor - ex-conjuge",
    "REL_NAMO": "Autor - namorado(a)",
    "REL_EXNAM": "Autor - ex-namorado(a)",
    "REL_FILHO": "Autor - filho(a)",
    "REL_IRMAO": "Autor - irmao(a)",
    "REL_CONHEC": "Autor - amigo/conhecido",
    "REL_DESCO": "Autor - desconhecido",
    "REL_CUIDA": "Autor - cuidador",
    "REL_PATRAO": "Autor - patrao/chefe",
    "REL_INST": "Autor - pessoa com relacao institucional",
    "REL_POL": "Autor - policial/agente da lei",
    "REL_PROPRI": "Autor - a propria pessoa",
    "REL_OUTROS": "Autor - outros",
    "REL_ESPEC": "Autor - outros (especificar)",
    "AUTOR_SEXO": "Sexo do provavel autor",
    "AUTOR_ALCO": "Suspeita de uso de alcool pelo autor",
    "CICL_VID_AUTOR": "Ciclo de vida do provavel autor",
    # --- Encaminhamentos (ver AVISO_VAZAMENTO no fim do arquivo) ---
    "ENC_SAUDE": "Encaminhamento - rede de saude",
    "ASSIST_SOC": "Encaminhamento - assistencia social",
    "REDE_EDUCA": "Encaminhamento - rede de educacao",
    "ATEND_MULH": "Encaminhamento - rede de atendimento a mulher",
    "CONS_TUTEL": "Encaminhamento - conselho tutelar",
    "CONS_IDO": "Encaminhamento - conselho do idoso",
    "DELEG_IDOSO": "Encaminhamento - delegacia de atendimento ao idoso",
    "DIR_HUMAN": "Encaminhamento - centro de referencia de direitos humanos",
    "MPU": "Encaminhamento - ministerio publico",
    "DELEG_CRIA": "Encaminhamento - delegacia de protecao a crianca/adolescente",
    "DELEG_MULH": "Encaminhamento - delegacia de atendimento a mulher",
    "DELEG": "Encaminhamento - outras delegacias",
    "INFAN_JUV": "Encaminhamento - justica da infancia e juventude",
    "DEFEN_PUBL": "Encaminhamento - defensoria publica",
    # --- Trabalho e encerramento ---
    "REL_TRAB": "Violencia relacionada ao trabalho",
    "REL_CAT": "Foi emitida CAT",
    "CIRC_LESAO": "Circunstancia da lesao (CID-10 cap. XX)",
    "DT_ENCERRA": "Data de encerramento",
    "DS_OBS": "Observacoes adicionais",
    # --- Controle interno do sistema ---
    "NDUPLIC_N": "Nao listar / nao contar (duplicidade)",
    "IN_VINCULA": "Vinculacao",
}


# Codigos IBGE de UF (2 digitos) - Fonte: tabela de UFs do IBGE.
UF_CODIGO = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}

UF_NOME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapa",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Para",
    "PB": "Paraíba",
    "PR": "Parana",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# =============================================================================
# CATEGORIES - nome DBF : {codigo : categoria}
# =============================================================================

CATEGORIES = {
    "TP_NOT": {
        "1": "Negativa",
        "2": "Individual",
        "3": "Surto",
        "4": "Agregado",
    },
    "TP_UNI_EXT": {
        "1": "Unidade de saude",
        "2": "Unidade de assistencia social",
        "3": "Estabelecimento de ensino",
        "4": "Conselho tutelar",
        "5": "Unidade de saude indigena",
        "6": "Centro especializado de atendimento a mulher",
        "7": "Outros",
    },
    "CS_SEXO": {"M": "Masculino", "F": "Feminino", "I": "Ignorado"},
    "CS_GESTANT": {
        "1": "1o trimestre",
        "2": "2o trimestre",
        "3": "3o trimestre",
        "4": "Idade gestacional ignorada",
        "5": "Nao",
        "6": "Nao se aplica",
        "9": "Ignorado",
    },
    "CS_RACA": {
        "1": "Branca",
        "2": "Preta",
        "3": "Amarela",
        "4": "Parda",
        "5": "Indigena",
        "9": "Ignorado",
    },
    # ATENCAO: o PDF do dicionario traz "43 Analfabeto" antes da lista 1-10,
    # o que e artefato de extracao. O padrao do SINAN usa 0 = Analfabeto.
    # VERIFICAR contra os valores reais do arquivo antes de confiar.
    "CS_ESCOL_N": {
        "0": "Analfabeto",
        "1": "1a a 4a serie incompleta do EF",
        "2": "4a serie completa do EF",
        "3": "5a a 8a serie incompleta do EF",
        "4": "Ensino fundamental completo",
        "5": "Ensino medio incompleto",
        "6": "Ensino medio completo",
        "7": "Educacao superior incompleta",
        "8": "Educacao superior completa",
        "9": "Ignorado",
        "10": "Nao se aplica",
    },
    "SIT_CONJUG": {
        "1": "Solteiro",
        "2": "Casado/uniao consensual",
        "3": "Viuvo",
        "4": "Separado",
        "8": "Nao se aplica",
        "9": "Ignorado",
    },
    "ORIENT_SEX": {
        "1": "Heterossexual",
        "2": "Homossexual",
        "3": "Bissexual",
        "8": "Nao se aplica",
        "9": "Ignorado",
    },
    "IDENT_GEN": {
        "1": "Travesti",
        "2": "Transexual mulher",
        "3": "Transexual homem",
        "8": "Nao se aplica",
        "9": "Ignorado",
    },
    "ZONA": {"1": "Urbana", "2": "Rural", "3": "Periurbana", "9": "Ignorado"},
    "ZONA_OCOR": {"1": "Urbana", "2": "Rural", "3": "Periurbana", "9": "Ignorado"},
    "LOCAL_OCOR": {
        "01": "Residencia",
        "02": "Habitacao coletiva",
        "03": "Escola",
        "04": "Local de pratica esportiva",
        "05": "Bar ou similar",
        "06": "Via publica",
        "07": "Comercio/servicos",
        "08": "Industrias/construcao",
        "09": "Outro",
        "99": "Ignorado",
    },
    "VIOL_MOTIV": {
        "01": "Sexismo",
        "02": "Homofobia/lesbofobia/bifobia/transfobia",
        "03": "Racismo",
        "04": "Intolerancia religiosa",
        "05": "Xenofobia",
        "06": "Conflito geracional",
        "07": "Situacao de rua",
        "08": "Deficiencia",
        "09": "Outros",
        "88": "Nao se aplica",
        "99": "Ignorado",
    },
    "NUM_ENVOLV": {"1": "Um", "2": "Dois ou mais", "9": "Ignorado"},
    "AUTOR_SEXO": {
        "1": "Masculino",
        "2": "Feminino",
        "3": "Ambos os sexos",
        "9": "Ignorado",
    },
    "CICL_VID_AUTOR": {
        "1": "Crianca",
        "2": "Adolescente",
        "3": "Jovem",
        "4": "Pessoa adulta",
        "5": "Pessoa idosa",
        "9": "Ignorado",
    },
    "NDUPLIC_N": {
        "0": "Nao identificado",
        "1": "Nao e duplicidade (nao listar)",
        "2": "Duplicidade (nao contar)",
    },
    "IN_VINCULA": {"0": "Nao vinculado", "1": "Vinculado"},
}

# --- Campos que usam os blocos padrao -------------------------------------

_SIM_NAO_FIELDS = [
    "OUT_VEZES",
    "DEF_TRANS",
    "VIOL_FISIC",
    "VIOL_PSICO",
    "VIOL_TORT",
    "VIOL_SEXU",
    "VIOL_TRAF",
    "VIOL_FINAN",
    "VIOL_NEGLI",
    "VIOL_INFAN",
    "VIOL_LEGAL",
    "VIOL_OUTR",
    "AG_FORCA",
    "AG_ENFOR",
    "AG_OBJETO",
    "AG_CORTE",
    "AG_QUENTE",
    "AG_ENVEN",
    "AG_FOGO",
    "AG_AMEACA",
    "AG_OUTROS",
    "REL_PAI",
    "REL_MAE",
    "REL_PAD",
    "REL_MAD",
    "REL_CONJ",
    "REL_EXCON",
    "REL_NAMO",
    "REL_EXNAM",
    "REL_FILHO",
    "REL_IRMAO",
    "REL_CONHEC",
    "REL_DESCO",
    "REL_CUIDA",
    "REL_PATRAO",
    "REL_INST",
    "REL_POL",
    "REL_PROPRI",
    "REL_OUTROS",
    "AUTOR_ALCO",
    "REL_TRAB",
    "ENC_SAUDE",
    "ASSIST_SOC",
    "REDE_EDUCA",
    "ATEND_MULH",
    "CONS_TUTEL",
    "CONS_IDO",
    "DELEG_IDOSO",
    "DIR_HUMAN",
    "MPU",
    "DELEG_CRIA",
    "DELEG_MULH",
    "DELEG",
    "INFAN_JUV",
    "DEFEN_PUBL",
]

_SIM_NAO_NA_FIELDS = [
    "LES_AUTOP",
    "REL_CAT",
    "DEF_FISICA",
    "DEF_MENTAL",
    "DEF_VISUAL",
    "DEF_AUDITI",
    "TRAN_MENT",
    "TRAN_COMP",
    "DEF_OUT",
    "SEX_ASSEDI",
    "SEX_ESTUPR",
    "SEX_PORNO",
    "SEX_EXPLO",
    "SEX_OUTRO",
    "PROC_DST",
    "PROC_HIV",
    "PROC_HEPB",
    "PROC_SANG",
    "PROC_SEMEN",
    "PROC_VAGINA",
    "PROC_CONTR",
    "PROC_ABORT",
]

for _f in _SIM_NAO_FIELDS:
    CATEGORIES.setdefault(_f, dict(SIM_NAO))

for _f in _SIM_NAO_NA_FIELDS:
    CATEGORIES.setdefault(_f, dict(SIM_NAO_NA))


# =============================================================================
# Grupos uteis para a modelagem
# =============================================================================

ALVO = "OUT_VEZES"

# Identificadores e texto livre: nunca entram no modelo.
EXCLUIR_SEMPRE = [
    "NU_NOTIFIC",
    "NM_PACIENT",
    "NM_MAE_PAC",
    "ID_CNS_SUS",
    "NM_UNI_EXT",
    "CO_UNI_EXT",
    "ID_UNIDADE",
    "CNES_NOT",
    "NM_BAIRRO",
    "NM_LOGRADO",
    "NU_NUMERO",
    "DS_COMPL",
    "DS_REF_RES",
    "NU_CEP",
    "DDD",
    "FONE",
    "NM_BA_OCOR",
    "NO_LOG_OCO",
    "NM_LOG_RES",
    "DS_COMP_OCOR",
    "DS_REF_OCOR",
    "ID_GEO1",
    "ID_GEO2",
    "ID_GEO3",
    "ID_GEO4",
    "DEF_ESPEC",
    "LOCAL_ESPE",
    "VIOL_ESPEC",
    "AG_ESPEC",
    "SEX_ESPEC",
    "REL_ESPEC",
    "DS_OBS",
    "NDUPLIC_N",
    "IN_VINCULA",
]

# Campos preenchidos DEPOIS ou POR CAUSA do desfecho.
# Usar como preditor infla o desempenho e o modelo nao funciona em caso novo.
RISCO_VAZAMENTO = [
    "ENC_SAUDE",
    "ASSIST_SOC",
    "REDE_EDUCA",
    "ATEND_MULH",
    "CONS_TUTEL",
    "CONS_IDO",
    "DELEG_IDOSO",
    "DIR_HUMAN",
    "MPU",
    "DELEG_CRIA",
    "DELEG_MULH",
    "DELEG",
    "INFAN_JUV",
    "DEFEN_PUBL",
    "PROC_DST",
    "PROC_HIV",
    "PROC_HEPB",
    "PROC_SANG",
    "PROC_SEMEN",
    "PROC_VAGINA",
    "PROC_CONTR",
    "PROC_ABORT",
    "DT_ENCERRA",
    "CIRC_LESAO",
    "REL_CAT",
]

# Campos que descrevem o caso no momento da notificacao.
# Sao os candidatos legitimos a preditor.
CANDIDATOS_PREDITORES = [
    # perfil da vitima
    "CS_SEXO",
    "CS_RACA",
    "CS_ESCOL_N",
    "SIT_CONJUG",
    "ZONA",
    "DEF_TRANS",
    "DEF_FISICA",
    "DEF_MENTAL",
    "DEF_VISUAL",
    "DEF_AUDITI",
    "TRAN_MENT",
    "TRAN_COMP",
    "DEF_OUT",
    # contexto da ocorrencia
    "LOCAL_OCOR",
    "ZONA_OCOR",
    "TP_UNI_EXT",
    "VIOL_MOTIV",
    "LES_AUTOP",
    # tipo de violencia
    "VIOL_FISIC",
    "VIOL_PSICO",
    "VIOL_TORT",
    "VIOL_SEXU",
    "VIOL_TRAF",
    "VIOL_FINAN",
    "VIOL_NEGLI",
    "VIOL_LEGAL",
    "VIOL_OUTR",
    # meio de agressao
    "AG_FORCA",
    "AG_ENFOR",
    "AG_OBJETO",
    "AG_CORTE",
    "AG_QUENTE",
    "AG_ENVEN",
    "AG_FOGO",
    "AG_AMEACA",
    "AG_OUTROS",
    # provavel autor
    "NUM_ENVOLV",
    "AUTOR_SEXO",
    "AUTOR_ALCO",
    "CICL_VID_AUTOR",
    "REL_PAI",
    "REL_MAE",
    "REL_CONJ",
    "REL_EXCON",
    "REL_FILHO",
    "REL_IRMAO",
    "REL_CONHEC",
    "REL_DESCO",
    "REL_CUIDA",
    "REL_INST",
    "REL_PATRAO",
    "REL_POL",
    "REL_OUTROS",
]


# =============================================================================
# Avisos de uso
# =============================================================================

AVISOS = """
1. ESCOLARIDADE (CS_ESCOL_N): o codigo de "Analfabeto" foi assumido como 0.
   O PDF do dicionario apresenta "43 Analfabeto", que e artefato de extracao.
   Confirme contra os valores reais do arquivo.

2. NOMES COM ACENTO: o dicionario grafa REL_IRMAO com til (REL_IRMÃO) e quebra
   CICL_VID_AUTOR em duas linhas. Se auditar_colunas() apontar esses campos
   como nao encontrados, procure a variacao equivalente no arquivo.

3. ENCAMINHAMENTOS E PROCEDIMENTOS: preenchidos apos a conduta do caso.
   Usar como preditor e vazamento de dado. Ver RISCO_VAZAMENTO.

4. IDADE (NU_IDADE_N): o 1o digito e a unidade de tempo
   (1 hora, 2 dia, 3 mes, 4 ano). 4065 = 65 anos.

5. VERSAO: dicionario 5.0/Patch 5.1, revisado em junho/2015. Fichas de anos
   posteriores podem ter campos adicionais nao cobertos aqui.
"""
