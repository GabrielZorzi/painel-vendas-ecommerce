"""Extração: download e leitura dos CSVs originais da Olist."""

import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from painel_vendas_ecommerce.config import RAW_DIR

RAW_DATA_URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
USER_AGENT = "painel-vendas-ecommerce"
DOWNLOAD_TIMEOUT_SECONDS = 120

RAW_FILES: dict[str, str] = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
}

DATE_COLUMNS: dict[str, list[str]] = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
}


def read_raw_table(name: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Lê uma tabela bruta pelo nome lógico, já com as colunas de data convertidas."""
    if name not in RAW_FILES:
        raise ValueError(f"Tabela desconhecida: {name!r}. Opções: {sorted(RAW_FILES)}")

    return pd.read_csv(
        raw_dir / RAW_FILES[name],
        encoding="utf-8-sig",
        parse_dates=DATE_COLUMNS.get(name, []),
    )


def missing_raw_files(raw_dir: Path = RAW_DIR) -> list[str]:
    """Lista os CSVs necessários que ainda não estão em raw_dir."""
    return [filename for filename in RAW_FILES.values() if not (raw_dir / filename).exists()]


def download_file(url: str, destination: Path) -> None:
    """Baixa url para destination via HTTP GET (segue redirecionamentos)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        with destination.open("wb") as file:
            shutil.copyfileobj(response, file)


def extract_csv_files(zip_path: Path, raw_dir: Path) -> None:
    """Extrai só os arquivos .csv do zip para raw_dir."""
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.endswith(".csv")]
        archive.extractall(raw_dir, members=csv_names)


def download_raw_data(raw_dir: Path = RAW_DIR, url: str = RAW_DATA_URL) -> bool:
    """Garante os CSVs em raw_dir, baixando o dataset se faltar algum.

    Devolve True se precisou baixar e False se os arquivos já estavam lá.
    """
    if not missing_raw_files(raw_dir):
        return False

    raw_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / "dataset.zip"
        download_file(url, zip_path)
        extract_csv_files(zip_path, raw_dir)

    still_missing = missing_raw_files(raw_dir)
    if still_missing:
        raise RuntimeError(f"O download não trouxe os arquivos esperados: {still_missing}")
    return True
