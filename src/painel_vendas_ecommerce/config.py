"""Configurações centrais do pipeline: caminhos e regras de negócio."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

START_DATE = pd.Timestamp("2017-01-01")
END_DATE = pd.Timestamp("2018-08-31")

CANCELED_STATUSES = frozenset({"canceled", "unavailable"})
