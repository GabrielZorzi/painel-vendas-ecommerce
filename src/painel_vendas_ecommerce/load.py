"""Carga: envio das tabelas para o Postgres (Supabase)."""

import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg import sql

PASSWORD_PLACEHOLDER = "[YOUR-PASSWORD]"
DB_SCHEMA = "painel"
SCHEMA_SQL_PATH = Path(__file__).with_name("schema.sql")


def get_database_url() -> str:
    """Lê a connection string da variável de ambiente DATABASE_URL."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL não definida. Copie .env.example para .env e preencha.")
    if PASSWORD_PLACEHOLDER in url:
        raise RuntimeError("DATABASE_URL ainda contém [YOUR-PASSWORD]: troque pela senha do banco.")
    return url


def build_truncate_statement(table_names: list[str]) -> sql.Composed:
    """Monta um único TRUNCATE para todas as tabelas (respeita as chaves estrangeiras)."""
    tables = sql.SQL(", ").join(sql.Identifier(DB_SCHEMA, name) for name in table_names)
    return sql.SQL("TRUNCATE {}").format(tables)


def build_copy_statement(table_name: str, columns: list[str]) -> sql.Composed:
    """Monta o COPY ... FROM STDIN em CSV, com as colunas na ordem do DataFrame."""
    column_list = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
    return sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv)").format(
        sql.Identifier(DB_SCHEMA, table_name), column_list
    )


def to_copy_payload(df: pd.DataFrame) -> str:
    """Converte o DataFrame no texto CSV (sem cabeçalho) que o COPY recebe."""
    return df.to_csv(index=False, header=False, date_format="%Y-%m-%d", lineterminator="\n")


def load_tables(tables: dict[str, pd.DataFrame], database_url: str) -> None:
    """Substitui o conteúdo das tabelas do banco numa única transação.

    Se qualquer passo falhar, o psycopg desfaz tudo (rollback) e o banco
    continua com os dados da carga anterior.
    """
    with psycopg.connect(database_url) as conn, conn.cursor() as cursor:
        cursor.execute(SCHEMA_SQL_PATH.read_text(encoding="utf-8"))
        cursor.execute(build_truncate_statement(list(tables)))
        for table_name, df in tables.items():
            statement = build_copy_statement(table_name, list(df.columns))
            with cursor.copy(statement) as copy:
                copy.write(to_copy_payload(df))
