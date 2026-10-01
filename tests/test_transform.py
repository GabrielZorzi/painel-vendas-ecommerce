import pandas as pd
import pytest

from painel_vendas_ecommerce.transform import (
    aggregate_items_by_order,
    build_items_fact,
    build_orders_fact,
    filter_period,
    flag_canceled,
    format_category_names,
)


@pytest.fixture
def order_items() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "price": [10.0, 20.0, 50.0],
            "freight_value": [1.5, 1.5, 5.0],
        }
    )


@pytest.fixture
def orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "customer_id": ["c1", "c2", "c3"],
            "order_status": ["delivered", "canceled", "unavailable"],
            "order_purchase_timestamp": pd.to_datetime(
                ["2017-03-10 14:30", "2018-08-31 23:59", "2018-01-05 08:00"]
            ),
        }
    )


@pytest.fixture
def customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["c1", "c2", "c3"],
            "customer_unique_id": ["u1", "u2", "u1"],
            "customer_state": ["SP", "RJ", "SP"],
        }
    )


def test_aggregate_items_by_order_sums_each_order(order_items: pd.DataFrame) -> None:
    result = aggregate_items_by_order(order_items).set_index("order_id")

    assert result.loc["o1", "products_value"] == 30.0
    assert result.loc["o1", "freight_value"] == 3.0
    assert result.loc["o1", "revenue"] == 33.0
    assert result.loc["o1", "items_count"] == 2
    assert result.loc["o2", "revenue"] == 55.0


def test_flag_canceled_marks_canceled_and_unavailable() -> None:
    status = pd.Series(["delivered", "canceled", "unavailable", "shipped"])

    assert flag_canceled(status).tolist() == [False, True, True, False]


def test_build_orders_fact_drops_orders_without_items(
    orders: pd.DataFrame, customers: pd.DataFrame, order_items: pd.DataFrame
) -> None:
    fact = build_orders_fact(orders, customers, aggregate_items_by_order(order_items))

    assert fact["order_id"].tolist() == ["o1", "o2"]


def test_build_orders_fact_keeps_revenue_total(
    orders: pd.DataFrame, customers: pd.DataFrame, order_items: pd.DataFrame
) -> None:
    fact = build_orders_fact(orders, customers, aggregate_items_by_order(order_items))

    expected = (order_items["price"] + order_items["freight_value"]).sum()
    assert fact["revenue"].sum() == pytest.approx(expected)


def test_build_orders_fact_adds_state_date_and_cancel_flag(
    orders: pd.DataFrame, customers: pd.DataFrame, order_items: pd.DataFrame
) -> None:
    fact = build_orders_fact(orders, customers, aggregate_items_by_order(order_items))
    o2 = fact.set_index("order_id").loc["o2"]

    assert o2["customer_state"] == "RJ"
    assert o2["purchase_date"] == pd.Timestamp("2018-08-31")
    assert bool(o2["is_canceled"]) is True


def test_filter_period_includes_whole_end_day() -> None:
    df = pd.DataFrame(
        {
            "purchase_date": pd.to_datetime(
                ["2016-12-31 10:00", "2017-01-01 00:00", "2018-08-31 23:59", "2018-09-01 00:00"]
            )
        }
    )

    result = filter_period(df, pd.Timestamp("2017-01-01"), pd.Timestamp("2018-08-31"))

    assert result["purchase_date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2017-01-01",
        "2018-08-31",
    ]


@pytest.fixture
def products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": ["p1", "p2"],
            "product_category_name": ["cama_mesa_banho", None],
        }
    )


@pytest.fixture
def items_with_products(order_items: pd.DataFrame) -> pd.DataFrame:
    return order_items.assign(product_id=["p1", "p2", "p1"])


def test_format_category_names_uses_pt_br_labels() -> None:
    categories = pd.Series(["cama_mesa_banho", "pcs", "beleza_saude"])

    assert format_category_names(categories).tolist() == [
        "Cama, Mesa e Banho",
        "Computadores",
        "Beleza e Saúde",
    ]


def test_format_category_names_merges_duplicated_categories() -> None:
    categories = pd.Series(["casa_conforto", "casa_conforto_2"])

    assert format_category_names(categories).tolist() == ["Casa e Conforto", "Casa e Conforto"]


def test_format_category_names_handles_unknown_and_missing() -> None:
    categories = pd.Series(["nova_categoria", None])

    assert format_category_names(categories).tolist() == ["Nova categoria", "Sem categoria"]


def test_build_items_fact_keeps_one_row_per_item(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    items_with_products: pd.DataFrame,
) -> None:
    orders_fact = build_orders_fact(orders, customers, aggregate_items_by_order(items_with_products))

    fact = build_items_fact(items_with_products, products, orders_fact)

    assert len(fact) == len(items_with_products)
    assert fact["revenue"].sum() == pytest.approx(orders_fact["revenue"].sum())
    assert fact["category"].tolist() == ["Cama, Mesa e Banho", "Sem categoria", "Cama, Mesa e Banho"]


def test_build_items_fact_inherits_order_attributes(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    items_with_products: pd.DataFrame,
) -> None:
    orders_fact = build_orders_fact(orders, customers, aggregate_items_by_order(items_with_products))

    o2_item = build_items_fact(items_with_products, products, orders_fact).set_index("order_id").loc["o2"]

    assert o2_item["customer_state"] == "RJ"
    assert o2_item["purchase_date"] == pd.Timestamp("2018-08-31")
    assert bool(o2_item["is_canceled"]) is True


def test_build_items_fact_drops_items_outside_orders_fact(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    items_with_products: pd.DataFrame,
) -> None:
    orders_fact = build_orders_fact(orders, customers, aggregate_items_by_order(items_with_products))
    only_o1 = orders_fact[orders_fact["order_id"] == "o1"]

    fact = build_items_fact(items_with_products, products, only_o1)

    assert set(fact["order_id"]) == {"o1"}
