"""
Camada Silver

Responsável pelo tratamento das metas de alfabetização.

Transforma as tabelas em formato WIDE para LONG,
padroniza os tipos e grava os resultados na Silver.
"""

import pandas as pd

from utils import ler_parquet
from utils import salvar_parquet


# ==========================================================
# TRANSFORMA WIDE -> LONG
# ==========================================================

def transformar(df, nivel):

    colunas_meta = [
        c for c in df.columns
        if c.startswith("meta_alfabetizacao_")
    ]

    id_vars = [
        c for c in df.columns
        if c not in colunas_meta
    ]

    df = df.melt(

        id_vars=id_vars,

        value_vars=colunas_meta,

        var_name="ano_meta",

        value_name="meta"

    )

    df["ano_meta"] = (

        df["ano_meta"]

        .str.extract(r"(\d+)")

        .astype(int)

    )

    df["nivel"] = nivel

    return df


# ==========================================================
# PADRONIZAÇÃO
# ==========================================================

def padronizar(df):

    if "ano" in df.columns:

        df["ano"] = df["ano"].astype(int)

    if "meta" in df.columns:

        df["meta"] = pd.to_numeric(

            df["meta"],

            errors="coerce"

        )

    if "id_municipio" in df.columns:

        df["id_municipio"] = (

            df["id_municipio"]

            .astype(str)

            .str.zfill(7)

        )

    return df


# ==========================================================
# REMOÇÃO DE NULOS
# ==========================================================

def limpar(df):

    return df.dropna(subset=["meta"])


# ==========================================================
# EXECUÇÃO
# ==========================================================

def executar_metas():

    meta_brasil = ler_parquet(

        "silver/meta_brasil_tratada.parquet"

    )

    meta_uf = ler_parquet(

        "silver/meta_uf_tratada.parquet"

    )

    meta_municipio = ler_parquet(

        "silver/meta_municipio_tratada.parquet"

    )

    meta_brasil = transformar(

        meta_brasil,

        "BRASIL"

    )

    meta_uf = transformar(

        meta_uf,

        "UF"

    )

    meta_municipio = transformar(

        meta_municipio,

        "MUNICIPIO"

    )

    meta_brasil = limpar(

        padronizar(meta_brasil)

    )

    meta_uf = limpar(

        padronizar(meta_uf)

    )

    meta_municipio = limpar(

        padronizar(meta_municipio)

    )

    salvar_parquet(

        meta_brasil,

        "silver/meta_brasil_long.parquet"

    )

    salvar_parquet(

        meta_uf,

        "silver/meta_uf_long.parquet"

    )

    salvar_parquet(

        meta_municipio,

        "silver/meta_municipio_long.parquet"

    )

    print()

    print("Metas tratadas com sucesso.")

    print(f"Brasil      : {len(meta_brasil)} registros")

    print(f"UF          : {len(meta_uf)} registros")

    print(f"Município   : {len(meta_municipio)} registros")


if __name__ == "__main__":

    executar_metas()
