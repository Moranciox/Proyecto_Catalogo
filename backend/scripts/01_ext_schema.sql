-- Ejecutar en la BD externa (EXT), por ejemplo: aromo_catalog_ext

CREATE SCHEMA IF NOT EXISTS catalog;

CREATE TABLE IF NOT EXISTS catalog.product_extra (
  cod_producto      integer PRIMARY KEY,
  image_filename    text,
  is_featured       boolean NOT NULL DEFAULT false,
  sort_order        integer,
  notes             text,
  updated_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_extra_featured
  ON catalog.product_extra (is_featured);

CREATE INDEX IF NOT EXISTS idx_product_extra_sort
  ON catalog.product_extra (sort_order);
