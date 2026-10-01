"""Orquestração: extrai, transforma e salva as tabelas do painel."""

from pathlib import Path

import pandas as pd

from painel_vendas_ecommerce.config import END_DATE, PROCESSED_DIR, START_DATE
from painel_vendas_ecommerce.extract import read_raw_table
from painel_vendas_ecommerce.transform import (
    aggregate_items_by_order,
    build_items_fact,
    build_orders_fact,
    filter_period,
)


def build_tables() -> dict[str, pd.DataFrame]:
    """Lê os CSVs brutos e devolve as tabelas finais, indexadas pelo nome."""
    order_items = read_raw_table("order_items")

    orders_fact = build_orders_fact(
        read_raw_table("orders"),
        read_raw_table("customers"),
        aggregate_items_by_order(order_items),
    )
    orders_fact = filter_period(orders_fact, START_DATE, END_DATE)
    items_fact = build_items_fact(order_items, read_raw_table("products"), orders_fact)

    return {"fact_orders": orders_fact, "fact_order_items": items_fact}


def save_tables(tables: dict[str, pd.DataFrame], out_dir: Path = PROCESSED_DIR) -> list[Path]:
    """Salva cada tabela como CSV em out_dir e devolve os caminhos gerados."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, df in tables.items():
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False, date_format="%Y-%m-%d")
        paths.append(path)
    return paths


def main() -> None:
    tables = build_tables()
    for path in save_tables(tables):
        print(f"Salvo: {path} ({len(tables[path.stem])} linhas)")
