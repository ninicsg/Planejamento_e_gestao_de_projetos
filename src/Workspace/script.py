"""
=============================================================================
SINAN / VIOL - Exportacao para Excel
=============================================================================
Le o arquivo .parquet baixado pelo PySUS, filtra vitimas 60+ e exporta
para .xlsx (ou .csv, se o volume for grande demais para o Excel).

Independente do script de exploracao. Roda sozinho.

Pre-requisito: o arquivo .parquet ja baixado.
    pip install pandas pyarrow openpyxl

ANTES DE RODAR: confira os nomes de coluna no BLOCO 2 e ajuste no BLOCO 1.
=============================================================================
"""

import os
import pandas as pd
import pyarrow.parquet as pq
from sinan_dicionario import LABELS, CATEGORIES

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)


# =============================================================================
# BLOCO 1 - Configuracao
# =============================================================================

ARQUIVO = os.path.expanduser(
    r"C:\Users\User\Documents\GitHub\Planejamento_e_gestao_de_projetos\src\Workspace\dados\downloads\ducklake\sinan\VIOLBR24.parquet"
)

SAIDA = "sinan_viol_idosos_01.xlsx"

IDADE_MINIMA = 60

# Acima deste valor o script exporta CSV automaticamente.
LIMITE_EXCEL = 1_000_000

# Nomes das colunas - CONFIRME NO BLOCO 2 ANTES DE CONFIAR.
COL_IDADE = "NU_IDADE_N"

# Colunas a exportar. Deixe a lista VAZIA para exportar todas.
COLUNAS = [
    "OUT_VEZES",
    "SG_UF_OCOR",
    "CS_RACA",
    "CS_SEXO",
    "AUTOR_ALCO",
    "AUTOR_SEXO",
    "LOCAL_OCOR",
    "REL_CONHEC",
    "REL_CONJ",
    "REL_CUIDA",
    "REL_DESCO",
    "REL_EXCON",
    "REL_FILHO",
    "REL_INST",
    "REL_IRMAO",
    "REL_MAE",
    "REL_OUTROS",
    "REL_PAI",
    "REL_PATRAO",
    "REL_POL",
    "AG_AMEACA",
    "AG_CORTE",
    "AG_ENFOR",
    "AG_ENVEN",
    "AG_FOGO",
    "AG_FORCA",
    "AG_OBJETO",
    "AG_OUTROS",
    "AG_QUENTE",
    "DEF_AUDITI",
    "DEF_FISICA",
    "DEF_MENTAL",
    "DEF_OUT",
    "DEF_TRANS",
    "DEF_VISUAL",
    "LES_AUTOP",
    "NUM_ENVOLV",
    "SIT_CONJUG",
    "TRAN_COMP",
    "TRAN_MENT",
    "VIOL_FINAN",
    "VIOL_FISIC",
    "VIOL_LEGAL",
    "VIOL_MOTIV",
    "VIOL_NEGLI",
    "VIOL_OUTR",
    "VIOL_PSICO",
    "VIOL_SEXU",
    "VIOL_TORT",
    "VIOL_TRAF",
    COL_IDADE,
]


# =============================================================================
# BLOCO 2 - Inspecionar o arquivo sem carregar
# =============================================================================
# Parquet guarda o esquema separado dos dados: da para ler estrutura e
# numero de linhas sem abrir o arquivo inteiro.

pf = pq.ParquetFile(ARQUIVO)
colunas_reais = list(pf.schema_arrow.names)

print(f"Arquivo : {ARQUIVO}")
print(f"Linhas  : {pf.metadata.num_rows:,}")
print(f"Colunas : {pf.metadata.num_columns}")
print()
print("--- COLUNAS DISPONIVEIS ---")
for i, nome in enumerate(colunas_reais):
    print(f"{i:3d}  {nome}")
print()

# >>> COMPARE A LISTA ACIMA COM O BLOCO 1. <<<
# Os nomes do DATASUS sao siglas curtas, diferentes dos nomes longos
# usados pela Base dos Dados. Ajuste COLUNAS e COL_IDADE se divergirem.


# =============================================================================
# BLOCO 3 - Validar os nomes configurados
# =============================================================================
# Falha cedo e com mensagem clara, em vez de quebrar 30 linhas adiante.

if COLUNAS:
    faltando = [c for c in COLUNAS if c not in colunas_reais]
    if faltando:
        raise KeyError(
            f"Colunas inexistentes no arquivo: {faltando}\n"
            f"Ajuste a lista COLUNAS no BLOCO 1 usando os nomes impressos acima."
        )
    colunas_ler = COLUNAS
else:
    colunas_ler = None  # None = todas

if COL_IDADE not in colunas_reais:
    raise KeyError(f"Coluna de idade '{COL_IDADE}' nao existe. Ajuste COL_IDADE.")


# =============================================================================
# BLOCO 4 - Carregar
# =============================================================================
# Parquet e colunar: ler 8 colunas custa uma fracao de ler 200.

df = pd.read_parquet(ARQUIVO, columns=colunas_ler)
print(f"Carregado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")


# =============================================================================
# BLOCO 5 - Decodificar a idade
# =============================================================================
# ATENCAO: o campo de idade do SINAN NAO esta em anos.
# O padrao usa um digito de unidade na frente:
#     1 = horas, 2 = dias, 3 = meses, 4 = anos
# Entao 4065 = 65 ANOS. Filtrar >= 60 no valor cru retorna lixo
# (um bebe de 65 dias vira "2065" e passaria no filtro).
#
# CONFIRMAR NO DICIONARIO DE DADOS DO SINAN NET.

bruto = pd.to_numeric(df[COL_IDADE], errors="coerce")

print("\n--- VERIFICACAO DA CODIFICACAO DA IDADE ---")
print("Distribuicao do digito de unidade (esperado: maioria = 4):")
print((bruto // 1000).value_counts(dropna=False).sort_index())
print(f"\nValor cru - min: {bruto.min()} | max: {bruto.max()}")

unidade = bruto // 1000
quantidade = bruto % 1000

df["idade_anos"] = quantidade.where(unidade == 4)

print("\nIdade decodificada:")
print(df["idade_anos"].describe())


def normalizar_codigo(valor):
    """O parquet traz '1', ' 1', 1 ou 1.0 para o mesmo valor.
    Sem padronizar, o mapeamento falha em silencio e devolve nulo."""
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto or None


# =============================================================================
# BLOCO 6 - Filtrar a populacao de interesse
# =============================================================================

idosos = df[df["idade_anos"] >= IDADE_MINIMA].copy()


print(f"\n--- RECORTE ---")
print(f"Total de Notificações : {len(df):,}")
print(f"Vitimas {IDADE_MINIMA}+          : {len(idosos):,}")
if len(df):
    print(f"Proporcao             : {len(idosos)/len(df):.1%}")

if idosos.empty:
    raise SystemExit(
        "Nenhum registro apos o filtro. Revise o BLOCO 5: "
        "a codificacao da idade provavelmente e diferente do esperado."
    )

# Traduzir UF


from sinan_dicionario import UF_CODIGO, UF_NOME


def traduzir_uf(serie, para="sigla"):
    """Aceita codigo IBGE ou sigla e devolve sigla ou nome por extenso."""
    valores = serie.map(normalizar_codigo)
    # Se vier numerico, converte para sigla primeiro
    siglas = valores.map(lambda v: UF_CODIGO.get(v.zfill(2), v) if v else None)
    return siglas if para == "sigla" else siglas.map(UF_NOME)


idosos["SG_UF_OCOR"]
idosos["uf_nome"] = traduzir_uf(idosos["SG_UF_OCOR"], para="nome")

# =============================================================================
# BLOCO 6.5 - Traduzir codigos e nomes de coluna
# =============================================================================
# Duas traducoes distintas:
#   CATEGORIES -> valor:  "1" vira "Sim"
#   LABELS     -> coluna: "OUT_VEZES" vira "Ocorreu outras vezes"
# A ordem importa: decodifica primeiro, renomeia depois. Se inverter,
# as chaves de CATEGORIES nao encontram mais as colunas.


legivel = idosos.copy()

for coluna, mapa in CATEGORIES.items():
    if coluna not in legivel.columns:
        continue

    codigos = legivel[coluna].map(normalizar_codigo)

    # Campos de 2 digitos: '1' precisa virar '01' para bater com o mapa
    largura = max(len(k) for k in mapa)
    if largura > 1:
        codigos = codigos.map(
            lambda v: v.zfill(largura) if v is not None and v.isdigit() else v
        )

    traduzido = codigos.map(mapa)

    # Codigo fora do dicionario vira nulo em silencio. Avisa em vez disso.
    orfaos = codigos[traduzido.isna() & codigos.notna()].value_counts()
    if not orfaos.empty:
        print(f"AVISO {coluna}: codigos sem traducao -> {orfaos.to_dict()}")

    legivel[coluna] = traduzido

legivel = legivel.rename(columns={c: LABELS[c] for c in legivel.columns if c in LABELS})

# =============================================================================
# BLOCO 6.6 - Amostra para inspecao
# =============================================================================
# Reduz o volume so para conferir a traducao e o preenchimento no Excel.
# Coloque None para exportar tudo.

N_AMOSTRA = 500

if N_AMOSTRA:
    legivel = legivel.sample(n=min(N_AMOSTRA, len(legivel)), random_state=42)

# =============================================================================
# BLOCO 6.7 - Portao de decisao: o alvo e utilizavel?
# =============================================================================
# Roda sobre `idosos` (base completa, codigos originais).
# NAO usar `legivel` nem a amostra de 500.

ALVO = "OUT_VEZES"

contagem = idosos[ALVO].value_counts(dropna=False)
proporcao = idosos[ALVO].value_counts(dropna=False, normalize=True)

print("\n--- DISTRIBUICAO DO ALVO ---")
print(pd.DataFrame({"n": contagem, "%": (proporcao * 100).round(2)}))

# Perda = codigo 9 (Ignorado) + nulos. Essas linhas saem do treino:
# nao se pode imputar a variavel-resposta.
codigos = idosos[ALVO].map(normalizar_codigo)
perda = codigos.isna().sum() + (codigos == "9").sum()

sim = (codigos == "1").sum()
nao = (codigos == "2").sum()
uteis = sim + nao

print(f"\nTotal 60+        : {len(idosos):,}")
print(f"Perda (9 + nulo) : {perda:,}  ({perda/len(idosos):.1%})")
print(f"Casos uteis      : {uteis:,}")

if uteis:
    print(f"  Sim : {sim:,}  ({sim/uteis:.1%})")
    print(f"  Nao : {nao:,}  ({nao/uteis:.1%})")
    print(f"\nTeto de variaveis (10 positivos por variavel): {min(sim, nao)//10}")

#  Exportar

del idosos["NU_IDADE_N"]
del idosos["SG_UF_OCOR"]

legivel = legivel.drop(
    columns=["Idade (codificada: 1o digito = unidade)", "UF de ocorrencia"]
)


ordem = ["idade_anos"] + [c for c in legivel.columns if c != "idade_anos"]
legivel = legivel[ordem]

if len(idosos) > LIMITE_EXCEL:
    saida = os.path.splitext(SAIDA)[0] + ".csv"
    legivel.to_csv(saida, index=False, encoding="utf-8-sig", sep=";")
    print(f"\nVolume alto ({len(idosos):,} linhas) - exportado como CSV.")
else:
    saida = SAIDA
    legivel.to_excel(saida, index=False)

print(f"Arquivo gerado: {os.path.abspath(saida)}")

print(idosos["idade_anos"].min(), idosos["idade_anos"].max())
