"""Transformação: monta as tabelas do painel a partir das tabelas brutas."""

import pandas as pd

from painel_vendas_ecommerce.categories import CATEGORY_LABELS
from painel_vendas_ecommerce.config import CANCELED_STATUSES

ORDERS_FACT_COLUMNS = [
    "order_id",
    "purchase_date",
    "order_status",
    "is_canceled",
    "customer_state",
    "customer_unique_id",
    "products_value",
    "freight_value",
    "revenue",
    "items_count",
]

ITEMS_FACT_COLUMNS = [
    "order_id",
    "order_item_id",
    "purchase_date",
    "order_status",
    "is_canceled",
    "customer_state",
    "category",
    "price",
    "freight_value",
    "revenue",
]

MISSING_CATEGORY = "Sem categoria"


def aggregate_items_by_order(order_items: pd.DataFrame) -> pd.DataFrame:
    """Soma os itens de cada pedido: uma linha por order_id."""
    by_order = order_items.groupby("order_id", as_index=False).agg(
        products_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        items_count=("order_item_id", "count"),
    )
    by_order["revenue"] = by_order["products_value"] + by_order["freight_value"]
    money_columns = ["products_value", "freight_value", "revenue"]
    by_order[money_columns] = by_order[money_columns].round(2)
    return by_order


def flag_canceled(order_status: pd.Series) -> pd.Series:
    """Indica se o pedido não virou venda (cancelado ou indisponível)."""
    return order_status.isin(CANCELED_STATUSES)


def build_orders_fact(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    items_by_order: pd.DataFrame,
) -> pd.DataFrame:
    """Monta a tabela de pedidos (uma linha por pedido); descarta pedidos sem itens."""
    fact = (
        orders.merge(items_by_order, on="order_id", how="inner", validate="one_to_one")
        .merge(customers, on="customer_id", how="left", validate="many_to_one")
    )
    fact["purchase_date"] = fact["order_purchase_timestamp"].dt.normalize()
    fact["is_canceled"] = flag_canceled(fact["order_status"])
    return fact[ORDERS_FACT_COLUMNS]


def filter_period(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    date_column: str = "purchase_date",
) -> pd.DataFrame:
    """Mantém as linhas entre start e end, incluindo o dia inteiro de end."""
    days = df[date_column].dt.normalize()
    return df[days.between(start, end)].reset_index(drop=True)


def format_category_names(categories: pd.Series) -> pd.Series:
    """Traduz o nome técnico para o nome de exibição: 'cama_mesa_banho' -> 'Cama, Mesa e Banho'.

    Categoria fora do dicionário (ex.: nova na base) recebe uma formatação automática;
    nulo vira 'Sem categoria'.
    """
    fallback = categories.str.replace("_", " ").str.capitalize()
    return categories.map(CATEGORY_LABELS).fillna(fallback).fillna(MISSING_CATEGORY)


def build_items_fact(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    orders_fact: pd.DataFrame,
) -> pd.DataFrame:
    """Monta a tabela de itens (uma linha por item), herdando data, status e estado do pedido.

    O join com orders_fact é inner: só entram itens de pedidos que já passaram
    pelas regras da tabela de pedidos (inclusive o recorte de período).
    """
    order_columns = ["order_id", "purchase_date", "order_status", "is_canceled", "customer_state"]
    fact = (
        order_items.merge(orders_fact[order_columns], on="order_id", how="inner", validate="many_to_one")
        .merge(products[["product_id", "product_category_name"]], on="product_id", how="left", validate="many_to_one")
    )
    fact["category"] = format_category_names(fact["product_category_name"])
    fact["revenue"] = (fact["price"] + fact["freight_value"]).round(2)
    return fact[ITEMS_FACT_COLUMNS]
