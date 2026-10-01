from pathlib import Path

import pandas as pd
import pytest

from painel_vendas_ecommerce.extract import RAW_FILES, read_raw_table


def write_csv(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8-sig")


def test_read_raw_table_parses_date_columns(tmp_path: Path) -> None:
    write_csv(
        tmp_path / RAW_FILES["order_items"],
        "order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value\n"
        "o1,1,p1,s1,2017-09-19 09:45:35,58.9,13.29\n",
    )

    df = read_raw_table("order_items", raw_dir=tmp_path)

    assert pd.api.types.is_datetime64_any_dtype(df["shipping_limit_date"])
    assert df.loc[0, "price"] == 58.9


def test_read_raw_table_strips_bom_from_header(tmp_path: Path) -> None:
    write_csv(tmp_path / RAW_FILES["products"], "product_id,product_category_name\np1,perfumaria\n")

    df = read_raw_table("products", raw_dir=tmp_path)

    assert list(df.columns) == ["product_id", "product_category_name"]


def test_read_raw_table_rejects_unknown_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Tabela desconhecida"):
        read_raw_table("sales", raw_dir=tmp_path)
