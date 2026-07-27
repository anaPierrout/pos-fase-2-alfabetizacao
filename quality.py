"""
Camada Silver

Responsável pela qualidade dos dados.

Valida:

- Duplicidades
- Valores nulos
- Corte de alfabetização
- Registros válidos
- Peso dos alunos
- Município
"""

import pandas as pd

from utils import ler_parquet


class QualityReport:

    def __init__(self):

        self.relatorio = {}

    def adicionar(self, nome, valor):

        self.relatorio[nome] = valor

    def imprimir(self):

        print("\n")
        print("=" * 60)
        print("RELATÓRIO DE QUALIDADE - SILVER")
        print("=" * 60)

        for chave, valor in self.relatorio.items():

            print(f"{chave:.<45}{valor}")

        print("=" * 60)


# -------------------------------------------------------
# DUPLICADOS
# -------------------------------------------------------

def verificar_duplicados(df):

    return df.duplicated(
        subset=["id_aluno", "ano"]
    ).sum()


# -------------------------------------------------------
# NULOS
# -------------------------------------------------------

def verificar_nulos(df):

    return df.isnull().sum().sort_values(
        ascending=False
    )


# -------------------------------------------------------
# CORTE 743
# -------------------------------------------------------

def validar_corte(df):

    divergencias = (

        df["alfabetizado"]

        !=

        df["alfabetizado_calculado"]

    )

    return divergencias.sum()


# -------------------------------------------------------
# REGISTROS VÁLIDOS
# -------------------------------------------------------

def registros_validos(df):

    return (

        df["registro_valido"]

        ==

        True

    ).sum()


# -------------------------------------------------------
# PESO NULO
# -------------------------------------------------------

def peso_nulo(df):

    return df["peso_aluno"].isnull().sum()


# -------------------------------------------------------
# MUNICÍPIO
# -------------------------------------------------------

def municipio_invalido(df):

    municipio = (

        df["id_municipio"]

        .astype(str)

        .str.len()

    )

    return (municipio != 7).sum()


# -------------------------------------------------------
# EXECUÇÃO
# -------------------------------------------------------

def executar_quality():

    alunos = ler_parquet(

        "silver/alunos_tratados.parquet"

    )

    report = QualityReport()

    report.adicionar(

        "Quantidade de registros",

        len(alunos)

    )

    report.adicionar(

        "Duplicados",

        verificar_duplicados(alunos)

    )

    report.adicionar(

        "Registros válidos",

        registros_validos(alunos)

    )

    report.adicionar(

        "Peso nulo",

        peso_nulo(alunos)

    )

    report.adicionar(

        "Municípios inválidos",

        municipio_invalido(alunos)

    )

    report.adicionar(

        "Divergência corte 743",

        validar_corte(alunos)

    )

    print()

    print(verificar_nulos(alunos))

    report.imprimir()


if __name__ == "__main__":

    executar_quality()
