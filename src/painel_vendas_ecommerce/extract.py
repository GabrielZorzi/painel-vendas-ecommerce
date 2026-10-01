"""Extração: leitura dos CSVs originais da Olist."""

from pathlib import Path

import pandas as pd

from painel_vendas_ecommerce.config import RAW_DIR

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
