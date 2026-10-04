import zipfile
from pathlib import Path

import pandas as pd
import pytest

from painel_vendas_ecommerce.extract import (
    RAW_FILES,
    download_raw_data,
    missing_raw_files,
    read_raw_table,
)


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


def make_dataset_zip(path: Path, filenames: list[str]) -> Path:
    """Cria um zip falso com CSVs mínimos, imitando o arquivo do Kaggle."""
    with zipfile.ZipFile(path, "w") as archive:
        for filename in filenames:
            archive.writestr(filename, "col\n1\n")
        archive.writestr("README.txt", "não é csv")
    return path


def test_missing_raw_files_lists_absent_csvs(tmp_path: Path) -> None:
    write_csv(tmp_path / RAW_FILES["orders"], "col\n1\n")

    missing = missing_raw_files(tmp_path)

    assert RAW_FILES["orders"] not in missing
    assert RAW_FILES["products"] in missing


def test_download_raw_data_downloads_and_extracts_csvs(tmp_path: Path) -> None:
    zip_path = make_dataset_zip(tmp_path / "dataset.zip", list(RAW_FILES.values()))
    raw_dir = tmp_path / "raw"

    downloaded = download_raw_data(raw_dir, url=zip_path.as_uri())

    assert downloaded is True
    assert missing_raw_files(raw_dir) == []
    assert not (raw_dir / "README.txt").exists()


def test_download_raw_data_skips_when_files_exist(tmp_path: Path) -> None:
    for filename in RAW_FILES.values():
        write_csv(tmp_path / filename, "col\n1\n")

    downloaded = download_raw_data(tmp_path, url="file:///nao/existe.zip")

    assert downloaded is False


def test_download_raw_data_fails_when_zip_is_incomplete(tmp_path: Path) -> None:
    zip_path = make_dataset_zip(tmp_path / "dataset.zip", [RAW_FILES["orders"]])

    with pytest.raises(RuntimeError, match="não trouxe os arquivos esperados"):
        download_raw_data(tmp_path / "raw", url=zip_path.as_uri())
