import pandas as pd
import pytest

from painel_vendas_ecommerce.load import (
    build_copy_statement,
    build_truncate_statement,
    get_database_url,
    to_copy_payload,
)


def test_get_database_url_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@host:5432/postgres")

    assert get_database_url() == "postgresql://user:secret@host:5432/postgres"


def test_get_database_url_fails_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="não definida"):
        get_database_url()


def test_get_database_url_fails_with_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:[YOUR-PASSWORD]@host:5432/postgres")

    with pytest.raises(RuntimeError, match="YOUR-PASSWORD"):
        get_database_url()


def test_build_truncate_statement_lists_all_tables() -> None:
    statement = build_truncate_statement(["fact_orders", "fact_order_items"])

    assert statement.as_string() == 'TRUNCATE "painel"."fact_orders", "painel"."fact_order_items"'


def test_build_copy_statement_uses_dataframe_columns() -> None:
    statement = build_copy_statement("fact_orders", ["order_id", "revenue"])

    assert statement.as_string() == (
        'COPY "painel"."fact_orders" ("order_id", "revenue") FROM STDIN WITH (FORMAT csv)'
    )


def test_to_copy_payload_writes_csv_without_header() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1"],
            "purchase_date": pd.to_datetime(["2017-03-10"]),
            "is_canceled": [False],
            "category": ["Cama, Mesa e Banho"],
            "revenue": [33.5],
        }
    )

    assert to_copy_payload(df) == 'o1,2017-03-10,False,"Cama, Mesa e Banho",33.5\n'
