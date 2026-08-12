"""
=============================================================================
SINAN / VIOL - Auditoria e decodificacao das colunas
=============================================================================
Usa sinan_dicionario.py para:
    1. auditar  -> o que do dicionario existe no arquivo e o que sobrou de fora
    2. renomear -> siglas DBF viram nomes legiveis
    3. decodificar -> codigos (1, 2, 9) viram categorias (Sim, Nao, Ignorado)

Os dois arquivos precisam estar na MESMA PASTA.

    pip install pandas pyarrow

=============================================================================
"""

import os
import pandas as pd
import pyarrow.parquet as pq

from sinan_dicionario import (
    LABELS,
    CATEGORIES,
    AVISOS,
    ALVO,
    EXCLUIR_SEMPRE,
    RISCO_VAZAMENTO,
    CANDIDATOS_PREDITORES,
)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 300)
pd.set_option("display.width", 220)

ARQUIVO = os.path.expanduser(r".\dados\downloads\ducklake\sinan\VIOLBR24.parquet")


# =============================================================================
# Funcoes
# =============================================================================


def auditar_colunas(caminho):
    """Compara as colunas do arquivo com o dicionario, sem carregar os dados.

    Devolve (colunas_do_arquivo, mapeadas, nao_mapeadas, ausentes).
    """
    schema = pq.ParquetFile(caminho).schema_arrow.names
    arquivo = set(schema)
    dicionario = set(LABELS)

    mapeadas = sorted(arquivo & dicionario)
    nao_mapeadas = sorted(
        arquivo - dicionario
    )  # existem no arquivo, faltam no dicionario
    ausentes = sorted(dicionario - arquivo)  # estao no dicionario, faltam no arquivo

    print(f"Colunas no arquivo    : {len(arquivo)}")
    print(f"Cobertas pelo dicionario: {len(mapeadas)}")
    print(f"Sem traducao          : {len(nao_mapeadas)}")
    print(f"No dicionario, ausentes no arquivo: {len(ausentes)}")

    if nao_mapeadas:
        print("\n--- SEM TRADUCAO (verificar no dicionario oficial) ---")
        for c in nao_mapeadas:
            print(f"  {c}")

    if ausentes:
        print("\n--- NO DICIONARIO MAS AUSENTES NO ARQUIVO ---")
        print("  (pode ser diferenca de versao da ficha, ou grafia com acento)")
        for c in ausentes:
            print(f"  {c}")

    return list(schema), mapeadas, nao_mapeadas, ausentes


def normalizar_codigo(valor):
    """Padroniza o codigo antes de traduzir.

    O parquet pode trazer '1', ' 1', 1 ou 1.0 para o mesmo valor.
    Sem isso, o mapeamento silenciosamente nao acha nada.
    """
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto.endswith(".0"):  # 1.0 -> 1
        texto = texto[:-2]
    return texto or None


def decodificar(df, manter_codigo=False):
    """Traduz os codigos para as categorias legiveis.

    manter_codigo=True cria uma coluna extra <campo>_cod com o valor original.
    """
    saida = df.copy()

    for coluna, mapa in CATEGORIES.items():
        if coluna not in saida.columns:
            continue

        codigos = saida[coluna].map(normalizar_codigo)

        # Tenta tambem com zero a esquerda: '1' -> '01' para campos de 2 digitos
        largura = max(len(k) for k in mapa)
        if largura > 1:
            codigos = codigos.map(
                lambda v: v.zfill(largura) if v is not None and v.isdigit() else v
            )

        if manter_codigo:
            saida[f"{coluna}_cod"] = codigos

        saida[coluna] = codigos.map(mapa)

    return saida


def renomear(df):
    """Troca as siglas DBF pelos nomes legiveis."""
    return df.rename(columns={c: LABELS[c] for c in df.columns if c in LABELS})


def conferir_codigos_nao_traduzidos(df_original, df_decodificado):
    """Aponta codigos que existem no arquivo mas nao estao no dicionario.

    Se aparecer muita coisa aqui, o dicionario esta desatualizado
    em relacao a versao da ficha usada naquele ano.
    """
    problemas = []
    for coluna in CATEGORIES:
        if coluna not in df_original.columns:
            continue
        orfaos = df_original.loc[df_decodificado[coluna].isna(), coluna]
        orfaos = orfaos[orfaos.notna()].map(normalizar_codigo).value_counts()
        if not orfaos.empty:
            problemas.append((coluna, orfaos.to_dict()))

    if problemas:
        print("--- CODIGOS SEM CORRESPONDENCIA NO DICIONARIO ---")
        for coluna, contagem in problemas:
            print(f"  {coluna}: {contagem}")
    else:
        print("Todos os codigos encontrados tem correspondencia no dicionario.")

    return problemas


# =============================================================================
# Execucao
# =============================================================================

if __name__ == "__main__":

    print(AVISOS)

    # --- 1. Auditoria (nao carrega os dados) ---
    print("=" * 70)
    print("AUDITORIA DE COLUNAS")
    print("=" * 70)
    colunas_arquivo, mapeadas, nao_mapeadas, ausentes = auditar_colunas(ARQUIVO)

    # --- 2. Carrega apenas o que interessa ---
    print("\n" + "=" * 70)
    print("CARGA")
    print("=" * 70)

    desejadas = [ALVO, "NU_IDADE_N", "SG_UF_NOT"] + CANDIDATOS_PREDITORES
    ler = [c for c in dict.fromkeys(desejadas) if c in colunas_arquivo]
    faltando = [c for c in dict.fromkeys(desejadas) if c not in colunas_arquivo]

    if faltando:
        print(f"Nao encontradas no arquivo (seguindo sem elas): {faltando}")

    df = pd.read_parquet(ARQUIVO, columns=ler)
    print(f"Carregado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")

    # --- 3. Decodifica ---
    print("\n" + "=" * 70)
    print("DECODIFICACAO")
    print("=" * 70)
    decodificado = decodificar(df, manter_codigo=True)
    conferir_codigos_nao_traduzidos(df, decodificado)

    # --- 4. Amostra legivel ---
    legivel = renomear(decodificado)
    print("\n--- AMOSTRA ---")
    print(legivel.head(10).T)  # transposta: fica mais facil de ler no terminal

    # --- 5. Tabela de referencia para o artigo ---
    referencia = pd.DataFrame(
        [
            {
                "campo_dbf": c,
                "nome": LABELS.get(c, ""),
                "papel": (
                    "alvo"
                    if c == ALVO
                    else (
                        "excluir"
                        if c in EXCLUIR_SEMPRE
                        else (
                            "risco de vazamento"
                            if c in RISCO_VAZAMENTO
                            else (
                                "preditor candidato"
                                if c in CANDIDATOS_PREDITORES
                                else "nao classificado"
                            )
                        )
                    )
                ),
                # 0 = campo sem categorias (data, texto livre, codigo IBGE/CID)
                "n_categorias": len(CATEGORIES.get(c, {})),
                "no_arquivo": "sim" if c in colunas_arquivo else "nao",
            }
            for c in LABELS
        ]
    )

    referencia = referencia.sort_values(["papel", "campo_dbf"])

    # sep=";" e utf-8-sig: o Excel em pt-BR espera ponto e virgula
    # e o BOM para abrir a acentuacao corretamente.
    referencia.to_csv(
        "dicionario_colunas.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    print(
        f"\nTabela de referencia salva em: {os.path.abspath('dicionario_colunas.csv')}"
    )
