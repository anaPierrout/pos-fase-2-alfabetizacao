"""
Camada Silver

Responsável por:

- Ler os dados da Bronze
- Unificar Batch + Streaming
- Remover duplicidades
- Corrigir tipos
- Criar flags de validade
- Recalcular alfabetização
- Tratar metas
- Salvar tudo na Silver
"""

import pandas as pd

from utils import ler_parquet
from utils import salvar_parquet


# ============================================================
# LEITURA
# ============================================================

def carregar_bronze():

    bronze = {}

    bronze["alunos"] = ler_parquet("bronze/alunos/")
    bronze["alunos_streaming"] = ler_parquet("bronze/alunos_streaming/")

    bronze["municipio"] = ler_parquet("bronze/municipio/")
    bronze["uf"] = ler_parquet("bronze/uf/")
    bronze["diretorio"] = ler_parquet("bronze/diretorio_municipio/")

    bronze["meta_brasil"] = ler_parquet(
        "bronze/meta_alfabetizacao_brasil/"
    )

    bronze["meta_uf"] = ler_parquet(
        "bronze/meta_alfabetizacao_uf/"
    )

    bronze["meta_municipio"] = ler_parquet(
        "bronze/meta_alfabetizacao_municipio/"
    )

    return bronze


# ============================================================
# DEDUPLICAÇÃO
# ============================================================

def remover_duplicados(df):

    df = df.sort_values(["ano"])

    df = df.drop_duplicates(
        subset=[
            "id_aluno",
            "ano"
        ],
        keep="first"
    )

    return df


# ============================================================
# PADRONIZAÇÃO
# ============================================================

def padronizar_tipos(df):

    if "ano" in df.columns:
        df["ano"] = df["ano"].astype(int)

    if "peso_aluno" in df.columns:
        df["peso_aluno"] = (
            pd.to_numeric(
                df["peso_aluno"],
                errors="coerce"
            )
        )

    if "proficiencia" in df.columns:
        df["proficiencia"] = (
            pd.to_numeric(
                df["proficiencia"],
                errors="coerce"
            )
        )

    if "id_municipio" in df.columns:

        df["id_municipio"] = (
            df["id_municipio"]
            .astype(str)
            .str.zfill(7)
        )

    return df


# ============================================================
# VALIDADE
# ============================================================

def criar_flag_validade(df):

    df["registro_valido"] = (
        (df["presenca"] == 1)
        &
        (df["preenchimento_caderno"] == 1)
    )

    return df


# ============================================================
# CORTE 743
# ============================================================

def recalcular_alfabetizacao(df):

    df["alfabetizado_calculado"] = (
        df["proficiencia"] >= 743
    )

    df["validacao_corte"] = (
        df["alfabetizado"]
        ==
        df["alfabetizado_calculado"]
    )

    return df


# ============================================================
# LIMPEZA
# ============================================================

def limpar_nulos(df):

    if "peso_aluno" in df.columns:

        df = df.dropna(
            subset=[
                "peso_aluno"
            ]
        )

    return df


# ============================================================
# STREAMING
# ============================================================

def unir_batch_streaming(batch, streaming):

    alunos = pd.concat(
        [
            batch,
            streaming
        ],
        ignore_index=True
    )

    alunos = remover_duplicados(alunos)

    return alunos


# ============================================================
# METAS
# ============================================================

def transformar_metas(df):

    colunas = [
        c
        for c in df.columns
        if c.startswith("meta_alfabetizacao_")
    ]

    if len(colunas) == 0:
        return df

    id_vars = [
        c
        for c in df.columns
        if c not in colunas
    ]

    df = df.melt(

        id_vars=id_vars,

        value_vars=colunas,

        var_name="ano_meta",

        value_name="valor_meta"

    )

    df["ano_meta"] = (
        df["ano_meta"]
        .str.extract(r"(\d+)")
        .astype(int)
    )

    return df


# ============================================================
# PIPELINE
# ============================================================

def executar_transformacao():

    bronze = carregar_bronze()

    alunos = unir_batch_streaming(
        bronze["alunos"],
        bronze["alunos_streaming"]
    )

    alunos = padronizar_tipos(alunos)

    alunos = limpar_nulos(alunos)

    alunos = criar_flag_validade(alunos)

    alunos = recalcular_alfabetizacao(alunos)

    municipio = padronizar_tipos(
        bronze["municipio"]
    )

    uf = bronze["uf"]

    diretorio = bronze["diretorio"]

    meta_brasil = transformar_metas(
        bronze["meta_brasil"]
    )

    meta_uf = transformar_metas(
        bronze["meta_uf"]
    )

    meta_municipio = transformar_metas(
        bronze["meta_municipio"]
    )

    salvar_parquet(
        alunos,
        "silver/alunos_tratados.parquet"
    )

    salvar_parquet(
        municipio,
        "silver/municipio_tratado.parquet"
    )

    salvar_parquet(
        uf,
        "silver/uf_tratado.parquet"
    )

    salvar_parquet(
        diretorio,
        "silver/diretorio_municipio_tratado.parquet"
    )

    salvar_parquet(
        meta_brasil,
        "silver/meta_brasil_tratada.parquet"
    )

    salvar_parquet(
        meta_uf,
        "silver/meta_uf_tratada.parquet"
    )

    salvar_parquet(
        meta_municipio,
        "silver/meta_municipio_tratada.parquet"
    )

    print("\nTransformação Silver concluída.")


if __name__ == "__main__":

    executar_transformacao()
