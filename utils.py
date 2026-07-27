from google.cloud import storage
import pandas as pd

from config import GCS_BUCKET_BRONZE
from config import GCS_BUCKET_SILVER


storage_client = storage.Client()


def ler_parquet(caminho):
    """
    Lê um parquet do Cloud Storage.
    """

    return pd.read_parquet(
        f"gs://{GCS_BUCKET_BRONZE}/{caminho}",
        engine="pyarrow"
    )


def salvar_parquet(df, caminho):
    """
    Salva dataframe na camada Silver.
    """

    destino = f"gs://{GCS_BUCKET_SILVER}/{caminho}"

    df.to_parquet(
        destino,
        index=False,
        engine="pyarrow"
    )

    print(f"Arquivo salvo em {destino}")
