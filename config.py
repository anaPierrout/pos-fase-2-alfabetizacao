"""
Configurações da camada Silver.
Carrega todas as variáveis do ambiente.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Projeto
GCP_PROJECT = os.environ["GCP_PROJECT"]

# Buckets
GCS_BUCKET_BRONZE = os.environ["GCS_BUCKET_BRONZE"]
GCS_BUCKET_SILVER = os.environ["GCS_BUCKET_SILVER"]

# BigQuery
BQ_LOCATION = os.environ["BQ_LOCATION"]

BQ_DATASET_BRONZE = os.environ["BQ_DATASET_BRONZE"]
BQ_DATASET_SILVER = os.environ["BQ_DATASET_SILVER"]
