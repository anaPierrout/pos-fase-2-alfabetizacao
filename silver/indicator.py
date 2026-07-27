"""
Camada Silver

Calcula os indicadores oficiais de alfabetização.

Saídas:

- indicador_brasil.parquet
- indicador_uf.parquet
- indicador_municipio.parquet
"""

import pandas as pd

from utils import ler_parquet
from utils import salvar_parquet


CORTE_ALFABETIZACAO = 743


def carregar_alunos():

    return ler_parquet(
        "silver/alunos_tratados.parquet"
    )


def preparar(df):

    df = df.copy()

    df = df[
        df["registro_valido"] == True
    ]

    df["alfabetizado"] = (
        df["proficiencia"] >= CORTE_ALFABETIZACAO
    )

    return df


def calcular_indicador(df, agrupamento):

    indicadores = (

        df

        .groupby(agrupamento)

        .apply(

            lambda x: pd.Series({

                "total_alunos":

                    len(x),

                "peso_total":

                    x["peso_aluno"].sum(),

                "peso_alfabetizados":

                    x.loc[
                        x["alfabetizado"],
                        "peso_aluno"
                    ].sum()

            })

        )

        .reset_index()

    )

    indicadores["indicador"] = (

        indicadores["peso_alfabetizados"]

        /

        indicadores["peso_total"]

    ) * 100

    indicadores["indicador"] = (

        indicadores["indicador"]

        .round(2)

    )

    return indicadores


def gerar_indicador_municipio(df):

    return calcular_indicador(

        df,

        [

            "ano",

            "id_municipio",

            "rede"

        ]

    )


def gerar_indicador_uf(df):

    diretorio = ler_parquet(

        "silver/diretorio_municipio_tratado.parquet"

    )

    base = df.merge(

        diretorio,

        on="id_municipio",

        how="left"

    )

    return calcular_indicador(

        base,

        [

            "ano",

            "sigla_uf",

            "rede"

        ]

    )


def gerar_indicador_brasil(df):

    return calcular_indicador(

        df,

        [

            "ano",

            "rede"

        ]

    )


def executar_indicator():

    alunos = carregar_alunos()

    alunos = preparar(alunos)

    indicador_municipio = gerar_indicador_municipio(

        alunos

    )

    indicador_uf = gerar_indicador_uf(

        alunos

    )

    indicador_brasil = gerar_indicador_brasil(

        alunos

    )

    salvar_parquet(

        indicador_municipio,

        "silver/indicador_municipio.parquet"

    )

    salvar_parquet(

        indicador_uf,

        "silver/indicador_uf.parquet"

    )

    salvar_parquet(

        indicador_brasil,

        "silver/indicador_brasil.parquet"

    )

    print()

    print("Indicadores gerados com sucesso.")

    print(

        f"Municípios : {len(indicador_municipio)}"

    )

    print(

        f"UFs        : {len(indicador_uf)}"

    )

    print(

        f"Brasil     : {len(indicador_brasil)}"

    )


if __name__ == "__main__":

    executar_indicator()
