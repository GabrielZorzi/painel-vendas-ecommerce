-- Estrutura das tabelas do painel. Idempotente: pode rodar a cada carga.

CREATE SCHEMA IF NOT EXISTS painel;

CREATE TABLE IF NOT EXISTS painel.fact_orders (
    order_id            text PRIMARY KEY,
    purchase_date       date NOT NULL,
    order_status        text NOT NULL,
    is_canceled         boolean NOT NULL,
    customer_state      char(2) NOT NULL,
    customer_unique_id  text NOT NULL,
    products_value      numeric(12, 2) NOT NULL,
    freight_value       numeric(12, 2) NOT NULL,
    revenue             numeric(12, 2) NOT NULL,
    items_count         integer NOT NULL
);

CREATE TABLE IF NOT EXISTS painel.fact_order_items (
    order_id        text NOT NULL REFERENCES painel.fact_orders (order_id),
    order_item_id   integer NOT NULL,
    purchase_date   date NOT NULL,
    order_status    text NOT NULL,
    is_canceled     boolean NOT NULL,
    customer_state  char(2) NOT NULL,
    category        text NOT NULL,
    price           numeric(12, 2) NOT NULL,
    freight_value   numeric(12, 2) NOT NULL,
    revenue         numeric(12, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);
