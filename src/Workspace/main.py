"""
=============================================================================
SINAN / VIOL - Exploracao inicial dos microdados
=============================================================================
Objetivo desta etapa: NAO e modelar ainda. E descobrir o que existe na base,
confirmar os nomes reais das colunas e avaliar se o alvo escolhido
(violencia de repeticao) e utilizavel.

Rode bloco a bloco. Nao rode tudo de uma vez na primeira vez.

Dependencias:
    pip install pysus pandas pyarrow numpy
=============================================================================
"""

import os

# IMPORTANTE: definir ANTES de importar o pysus.
# O caminho de cache e resolvido no momento do import.
os.environ["PYSUS_CACHEPATH"] = os.path.abspath("./dados")

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pysus import sinan, list_files

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

ANO = 2024  # comece com um ano so

# =============================================================================
# BLOCO 1 - Ver o que existe no servidor antes de baixar
# =============================================================================

catalogo = list_files("SINAN", group="VIOL")
print(catalogo)

# Se o ano que voce quer nao aparecer aqui, ele provavelmente esta em PRELIM
# (base ainda nao consolidada) e nao em FINAIS.


# # =============================================================================
# # BLOCO 2 - Download
# # =============================================================================
# # Devolve uma LISTA de caminhos de arquivos .parquet ja convertidos.
# # Roda uma vez; nas proximas execucoes usa o cache.

caminhos = sinan(disease="VIOL", year=ANO)
print(caminhos)

arquivo = caminhos[0]


# =============================================================================
# BLOCO 3 - Inspecionar SEM carregar na memoria
# =============================================================================
# Parquet guarda o esquema separado dos dados. Da pra ler a estrutura e a
# contagem de linhas sem abrir o arquivo inteiro. Faca isso ANTES de qualquer
# read_parquet, para saber o tamanho do problema.

pf = pq.ParquetFile(arquivo)

print(f"Linhas: {pf.metadata.num_rows:,}")
print(f"Colunas: {pf.metadata.num_columns}")
print()
for i, nome in enumerate(pf.schema_arrow.names):
    print(f"{i:3d}  {nome}")

# >>> PARE AQUI E LEIA A LISTA ACIMA. <<<
# Os nomes reais do DATASUS sao siglas curtas (estilo NU_IDADE_N, SG_UF_NOT),
# nao os nomes longos da Base dos Dados. Anote quais correspondem a:
#   - idade da vitima
#   - UF / municipio de notificacao
#   - violencia de repeticao  (seu alvo)
#   - local de ocorrencia
#   - relacao com o agressor
#   - tipo de violencia


# =============================================================================
# BLOCO 4 - Amostra pequena para olhar os valores
# =============================================================================
# iter_batches le em pedacos. Pegar o primeiro lote da uma amostra real
# sem carregar milhoes de linhas.

amostra = next(pf.iter_batches(batch_size=500)).to_pandas()
print(amostra.head(20))


# =============================================================================
# BLOCO 5 - Preencha com os nomes que voce confirmou no BLOCO 3
# =============================================================================

COL_IDADE = "NU_IDADE_N"
COL_UF = "SG_UF_NOT"
COL_ALVO = "OUT_VEZES"

COLUNAS = [
    COL_IDADE,
    COL_UF,
    COL_ALVO,
    # acrescente aqui as features conforme confirmar os nomes
]

# Checagem defensiva: falha cedo e com mensagem clara se um nome estiver errado.
faltando = [c for c in COLUNAS if c not in pf.schema_arrow.names]
if faltando:
    raise KeyError(f"Colunas inexistentes no arquivo: {faltando}")


# =============================================================================
# BLOCO 6 - Carregar apenas as colunas necessarias
# =============================================================================
# Parquet e colunar: ler 6 colunas custa uma fracao de ler 200.
# Isso e o que impede o notebook de travar quando voce juntar varios anos.

df = pd.read_parquet(arquivo, columns=COLUNAS)
print(df.shape)
print(df.dtypes)


# =============================================================================
# BLOCO 7 - Idade: o campo NAO esta em anos
# =============================================================================
# ATENCAO - CONFIRMAR NO DICIONARIO DE DADOS DO SINAN.
# O padrao do SINAN codifica idade com um digito de unidade na frente:
#   1 = horas, 2 = dias, 3 = meses, 4 = anos
# Entao 4065 significa 65 ANOS, e nao "quatro mil e sessenta e cinco".
# Filtrar por `idade >= 60` no valor cru retorna lixo.
#
# Verifique empiricamente antes de confiar:

bruto = pd.to_numeric(df[COL_IDADE], errors="coerce")
print("Distribuicao do digito de unidade:")
print((bruto // 1000).value_counts(dropna=False))
print("\nMin / max do valor cru:", bruto.min(), bruto.max())

# Se a distribuicao acima confirmar o padrao (maioria com prefixo 4),
# a decodificacao e:

unidade = bruto // 1000
quantidade = bruto % 1000

df["idade_anos"] = np.where(unidade == 4, quantidade, np.nan)

print("\nIdade decodificada:")
print(df["idade_anos"].describe())


# =============================================================================
# BLOCO 8 - Recorte da populacao de interesse
# =============================================================================

idosos = df[df["idade_anos"] >= 60].copy()

print(f"Total de notificacoes no ano: {len(df):,}")
print(f"Vitimas com 60+:              {len(idosos):,}")
print(f"Proporcao:                    {len(idosos)/len(df):.1%}")


# # =============================================================================
# # BLOCO 9 - O alvo: ele e utilizavel?
# # =============================================================================
# # Esta e a checagem que decide se o projeto segue com o plano A.

# print("Distribuicao do alvo (bruta):")
# print(idosos[COL_ALVO].value_counts(dropna=False))
# print()
# print("Em proporcao:")
# print(idosos[COL_ALVO].value_counts(dropna=False, normalize=True).round(4))

# # Leitura do resultado:
# #
# # 1) Os codigos costumam ser 1=Sim, 2=Nao, 9=Ignorado. CONFIRME no dicionario.
# #
# # 2) Some "9" (Ignorado) + nulos. Esse e o seu percentual de perda.
# #    - abaixo de ~30%: segue tranquilo.
# #    - entre 30% e 60%: segue, mas a limitacao vira secao obrigatoria no texto.
# #    - acima de 60%: o alvo nao sustenta o trabalho. Troque para o plano B
# #      (classificar desfecho / encaminhamento) antes de escrever qualquer modelo.
# #
# # 3) Olhe o desbalanceamento entre Sim e Nao. Se "Sim" for menos de 20%,
# #    acuracia sera uma metrica inutil e voce vai precisar de class_weight.
# #
# # Registre esses tres numeros. Eles vao para o slide de metodologia.


# # =============================================================================
# # BLOCO 10 - Qualidade de preenchimento das demais colunas
# # =============================================================================
# # Coluna com 80% de "Ignorado" nao vira feature util.
# # Rode isso antes de escolher as features definitivas.

# resumo = pd.DataFrame({
#     "nulos_%": (idosos.isna().mean() * 100).round(1),
#     "n_categorias": idosos.nunique(),
# })
# print(resumo.sort_values("nulos_%", ascending=False))
